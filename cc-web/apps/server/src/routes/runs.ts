import type { FastifyInstance } from "fastify";

export async function registerRunRoutes(app: FastifyInstance) {
  app.post("/api/runs/:runId/cancel", { preHandler: [app.authenticate] }, async (request, reply) => {
    const { runId } = request.params as { runId: string };
    const run = app.sessionService.getRun(runId, request.currentUser.id);
    if (!run) {
      return reply.code(404).send({ message: "Run not found" });
    }
    if (run.status !== "running") {
      return reply.code(409).send({ message: "Run is not active" });
    }
    const cancelled = app.claudeAdapter.cancel(runId);
    if (!cancelled) {
      return reply.code(409).send({ message: "Run is not cancellable" });
    }
    app.sessionService.updateRun(runId, {
      status: "cancelled",
      error_code: "cancelled",
      error_message: "Run cancelled by user",
      completed_at: new Date().toISOString(),
    });
    app.eventBroker.publish(run.session_id, {
      id: `evt_${Date.now()}`,
      type: "run.cancelled",
      runId,
      payload: { message: "Run cancelled by user" },
      createdAt: new Date().toISOString(),
    });
    return { ok: true };
  });
}
