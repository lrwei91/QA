import fs from "node:fs";
import path from "node:path";
import type { FastifyInstance } from "fastify";
import { z } from "zod";
import type { MessageRequest, PublishRequest, SessionSnapshot } from "@cc-web/shared";
import { buildPrompt, classifyClaudeFailure } from "../services/claudeAdapter.js";

const createSessionSchema = z.object({
  name: z.string().trim().min(1).max(80),
});

const messageSchema = z.object({
  action: z.enum(["generate", "supplement", "analyze", "export", "i18n", "custom"]),
  text: z.string().default(""),
  uploadPaths: z.array(z.string()).default([]),
});

const publishSchema = z.object({
  artifactIds: z.array(z.string()).min(1),
  confirm: z.boolean().optional(),
  force: z.boolean().optional(),
});

export async function registerSessionRoutes(app: FastifyInstance) {
  app.get("/api/sessions", { preHandler: [app.authenticate] }, async (request) => {
    return { sessions: app.sessionService.listSessions(request.currentUser.id) };
  });

  app.delete("/api/sessions/:sessionId", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const result = await app.sessionService.deleteSession(sessionId, request.currentUser.id);
    if (result === "missing") {
      return reply.code(404).send({ message: "Session not found" });
    }
    if (result === "running") {
      return reply.code(409).send({ message: "Cannot delete a running session" });
    }
    return { ok: true };
  });

  app.post("/api/sessions", { preHandler: [app.authenticate] }, async (request) => {
    const payload = createSessionSchema.parse(request.body);
    const created = await app.sessionService.createSession(request.currentUser.id, payload);
    return { session: created.session };
  });

  app.get("/api/sessions/:sessionId/events", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }

    reply.raw.setHeader("Content-Type", "text/event-stream");
    reply.raw.setHeader("Cache-Control", "no-cache");
    reply.raw.setHeader("Connection", "keep-alive");
    reply.raw.flushHeaders();

    const snapshot: SessionSnapshot = {
      session: app.sessionService.listSessions(request.currentUser.id).find((item) => item.id === sessionId)!,
      runs: app.sessionService.listRuns(sessionId),
      artifacts: app.artifactService.listSessionArtifacts(sessionId),
    };

    const initialEvent = {
      id: `evt_${Date.now()}`,
      type: "snapshot" as const,
      payload: snapshot,
      createdAt: new Date().toISOString(),
    };
    reply.raw.write(`event: snapshot\ndata: ${JSON.stringify(initialEvent)}\n\n`);

    const unsubscribe = app.eventBroker.subscribe(sessionId, reply);
    request.raw.on("close", unsubscribe);
    return reply;
  });

  app.post("/api/sessions/:sessionId/uploads", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }
    const workspace = await app.sessionService.ensureWorkspace(session);
    const file = await request.file();
    if (!file) {
      return reply.code(400).send({ message: "No file uploaded" });
    }
    const safeName = path.basename(file.filename);
    const target = path.join(workspace.uploadsPath, safeName);
    await fs.promises.mkdir(path.dirname(target), { recursive: true });
    await fs.promises.writeFile(target, await file.toBuffer());
    const relative = path.relative(workspace.workspacePath, target);
    return { uploaded: { name: safeName, relativePath: relative } };
  });

  app.get("/api/sessions/:sessionId/artifacts", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }
    return { artifacts: app.artifactService.listSessionArtifacts(sessionId) };
  });

  app.get("/api/sessions/:sessionId/artifacts/:artifactId/download", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId, artifactId } = request.params as { sessionId: string; artifactId: string };
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }
    const artifact = app.artifactService.getArtifactsByIds(sessionId, [artifactId])[0];
    if (!artifact || !fs.existsSync(artifact.artifactPath)) {
      return reply.code(404).send({ message: "Artifact not found" });
    }
    reply.header("Content-Disposition", `attachment; filename="${encodeURIComponent(path.basename(artifact.relativePath))}"`);
    reply.type(artifact.mimeType);
    return reply.send(fs.createReadStream(artifact.artifactPath));
  });

  app.post("/api/sessions/:sessionId/messages", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const payload = messageSchema.parse(request.body) as MessageRequest;
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }
    if (app.sessionService.activeRunExists(sessionId)) {
      return reply.code(409).send({ message: "This session already has an active run" });
    }

    const workspace = await app.sessionService.ensureWorkspace(session);
    const prompt = buildPrompt(payload.action, payload.text ?? "", payload.uploadPaths ?? []);
    const rawLogPath = path.join(workspace.logsPath, `${Date.now()}-${Math.random().toString(16).slice(2)}.jsonl`);
    const before = app.artifactService.scanWorkspaceArtifacts(workspace.workspacePath);
    const run = app.sessionService.createRun(sessionId, request.currentUser.id, payload.action, prompt, rawLogPath);

    void app.claudeAdapter
      .run(
        {
          runId: run.id,
          sessionId,
          workspacePath: workspace.workspacePath,
          logPath: rawLogPath,
          prompt,
          claudeSessionId: session.claude_session_id,
        },
        {
          onClaudeSessionId: (claudeSessionId) => {
            app.sessionService.updateRun(run.id, { claude_session_id: claudeSessionId });
          },
          onEvent: (event) => {
            app.eventBroker.publish(sessionId, event);
          },
        },
      )
      .then(async (result) => {
        app.sessionService.updateRun(run.id, {
          status: "completed",
          claude_session_id: result.claudeSessionId,
          result_text: result.resultText,
          completed_at: new Date().toISOString(),
        });
        const artifacts = await app.artifactService.captureChangedArtifacts(
          sessionId,
          run.id,
          workspace.workspacePath,
          workspace.artifactsPath,
          before,
        );
        for (const artifact of artifacts) {
          app.eventBroker.publish(sessionId, {
            id: `evt_${Date.now()}_${artifact.id}`,
            type: "artifact.created",
            runId: run.id,
            payload: artifact,
            createdAt: new Date().toISOString(),
          });
        }
      })
      .catch((error) => {
        const failure = classifyClaudeFailure(error);
        app.sessionService.updateRun(run.id, {
          status: "failed",
          error_code: failure.errorCode,
          error_message: failure.errorMessage,
          completed_at: new Date().toISOString(),
        });
        app.eventBroker.publish(sessionId, {
          id: `evt_${Date.now()}_${run.id}`,
          type: "run.failed",
          runId: run.id,
          payload: failure,
          createdAt: new Date().toISOString(),
        });
      });

    return {
      run: app.sessionService.listRuns(sessionId).find((item) => item.id === run.id),
    };
  });

  app.post("/api/sessions/:sessionId/publish", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { sessionId } = request.params as { sessionId: string };
    const payload = publishSchema.parse(request.body) as PublishRequest;
    const session = app.sessionService.getSession(sessionId, request.currentUser.id);
    if (!session) {
      return reply.code(404).send({ message: "Session not found" });
    }
    const artifacts = app.artifactService.getArtifactsByIds(sessionId, payload.artifactIds);
    if (artifacts.length !== payload.artifactIds.length) {
      return reply.code(404).send({ message: "Some artifacts were not found" });
    }
    const preview = app.artifactService.previewPublish(artifacts);
    if (!payload.confirm) {
      return { preview };
    }
    try {
      const result = await app.artifactService.publishArtifacts(request.currentUser.id, sessionId, artifacts, Boolean(payload.force));
      return { preview: result };
    } catch (error) {
      return reply.code(409).send({
        message: error instanceof Error ? error.message : String(error),
        preview,
      });
    }
  });
}
