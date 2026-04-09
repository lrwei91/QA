import { buildApp } from "./app.js";

const app = await buildApp();

try {
  await app.listen({
    host: app.config.host,
    port: app.config.port,
  });
  app.log.info(`cc-web server listening on http://${app.config.host}:${app.config.port}`);
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
