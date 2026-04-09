import fs from "node:fs";
import path from "node:path";
import Fastify from "fastify";
import fastifyCookie from "@fastify/cookie";
import fastifyCors from "@fastify/cors";
import fastifyJwt from "@fastify/jwt";
import fastifyMultipart from "@fastify/multipart";
import type { FastifyInstance } from "fastify";
import mime from "mime-types";
import { loadConfig, type AppConfig } from "./config/env.js";
import { createDatabase, mapUser, type DatabaseClient } from "./db/client.js";
import { registerAuthRoutes } from "./routes/auth.js";
import { registerHealthRoutes } from "./routes/health.js";
import { registerRunRoutes } from "./routes/runs.js";
import { registerSessionRoutes } from "./routes/sessions.js";
import { ArtifactService } from "./services/artifactService.js";
import { ClaudeAdapter } from "./services/claudeAdapter.js";
import { EventBroker } from "./services/eventBroker.js";
import { SessionService } from "./services/sessionService.js";
import { UserService } from "./services/userService.js";
import { WorkspaceManager } from "./services/workspaceManager.js";

declare module "fastify" {
  interface FastifyInstance {
    config: AppConfig;
    db: DatabaseClient;
    userService: UserService;
    sessionService: SessionService;
    artifactService: ArtifactService;
    eventBroker: EventBroker;
    claudeAdapter: ClaudeAdapter;
    authenticate: (request: any, reply: any) => Promise<void>;
  }

  interface FastifyRequest {
    currentUser: ReturnType<typeof mapUser>;
  }
}

export type BuildAppOptions = {
  config?: AppConfig;
  db?: DatabaseClient;
  claudeAdapter?: ClaudeAdapter;
};

export async function buildApp(options: BuildAppOptions = {}): Promise<FastifyInstance> {
  const config = options.config ?? loadConfig();
  const db = options.db ?? createDatabase(path.join(config.dataDir, "meta.sqlite"));
  const app = Fastify({
    logger: {
      level: config.nodeEnv === "production" ? "info" : "debug",
    },
  });

  const workspaceManager = new WorkspaceManager(config);
  const userService = new UserService(db, config);
  const sessionService = new SessionService(db, workspaceManager, config.sourceRepo);
  const artifactService = new ArtifactService(db, config);
  const eventBroker = new EventBroker();
  const claudeAdapter = options.claudeAdapter ?? new ClaudeAdapter(config);

  userService.bootstrapAdmin();

  await app.register(fastifyCors, {
    origin: config.allowedOrigins,
    credentials: true,
  });
  await app.register(fastifyCookie);
  await app.register(fastifyJwt, {
    secret: config.jwtSecret,
    cookie: {
      cookieName: "cc_web_token",
      signed: false,
    },
  });
  await app.register(fastifyMultipart);

  app.decorate("config", config);
  app.decorate("db", db);
  app.decorate("userService", userService);
  app.decorate("sessionService", sessionService);
  app.decorate("artifactService", artifactService);
  app.decorate("eventBroker", eventBroker);
  app.decorate("claudeAdapter", claudeAdapter);
  app.decorate("authenticate", async function authenticate(request, reply) {
    try {
      await request.jwtVerify();
      const userId = typeof request.user.sub === "string" ? request.user.sub : "";
      const current = userService.findById(userId);
      if (!current) {
        return reply.code(401).send({ message: "Invalid user" });
      }
      request.currentUser = mapUser(current);
    } catch {
      return reply.code(401).send({ message: "Unauthorized" });
    }
  });

  await registerHealthRoutes(app);
  await registerAuthRoutes(app);
  await registerSessionRoutes(app);
  await registerRunRoutes(app);

  if (fs.existsSync(config.clientDistDir)) {
    const assetRoot = path.join(config.clientDistDir, "assets");
    app.setNotFoundHandler(async (request, reply) => {
      const url = request.raw.url || "";
      if (url.startsWith("/api/")) {
        return reply.code(404).send({ message: "Not found" });
      }
      if (url.startsWith("/assets/") && fs.existsSync(assetRoot)) {
        const relativeAssetPath = url.replace(/^\/assets\//, "").split("?")[0] ?? "";
        const assetPath = path.resolve(assetRoot, relativeAssetPath);
        if (!assetPath.startsWith(assetRoot) || !fs.existsSync(assetPath)) {
          return reply.code(404).send({ message: "Asset not found" });
        }
        const contentType = mime.lookup(assetPath);
        if (contentType) {
          reply.type(contentType);
        } else {
          reply.type("application/octet-stream");
        }
        return reply.send(fs.createReadStream(assetPath));
      }
      reply.type("text/html; charset=utf-8");
      return reply.send(fs.createReadStream(path.join(config.clientDistDir, "index.html")));
    });
  }

  app.addHook("onClose", async () => {
    db.close();
  });

  return app;
}
