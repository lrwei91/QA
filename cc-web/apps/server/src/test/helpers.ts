import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type { AppConfig } from "../config/env.js";

export async function createTempRepo(): Promise<{ root: string; cleanup(): Promise<void> }> {
  const root = await fs.promises.mkdtemp(path.join(os.tmpdir(), "cc-web-repo-"));
  await fs.promises.mkdir(path.join(root, "testcases/generated"), { recursive: true });
  await fs.promises.mkdir(path.join(root, "testcases/i18n"), { recursive: true });
  await fs.promises.mkdir(path.join(root, "test-case-generator/scripts"), { recursive: true });
  await fs.promises.writeFile(path.join(root, "README.md"), "# temp repo\n", "utf8");
  await fs.promises.writeFile(path.join(root, "testcases/testcase-index.json"), '{"version":1,"entries":[]}\n', "utf8");
  await fs.promises.writeFile(path.join(root, "testcases/i18n-index.json"), '{"version":1,"entries":[]}\n', "utf8");
  return {
    root,
    async cleanup() {
      await fs.promises.rm(root, { recursive: true, force: true });
    },
  };
}

export async function createTestConfig(): Promise<{ config: AppConfig; cleanup(): Promise<void> }> {
  const repo = await createTempRepo();
  const dataDir = await fs.promises.mkdtemp(path.join(os.tmpdir(), "cc-web-data-"));
  return {
    config: {
      nodeEnv: "test",
      host: "127.0.0.1",
      port: 0,
      allowedOrigins: ["http://localhost:5173"],
      jwtSecret: "test-secret-key",
      sourceRepo: repo.root,
      dataDir,
      bootstrapAdminUsername: "admin",
      bootstrapAdminPassword: "secret123",
      defaultModel: undefined,
      clientDistDir: path.join(dataDir, "client-dist"),
    },
    async cleanup() {
      await repo.cleanup();
      await fs.promises.rm(dataDir, { recursive: true, force: true });
    },
  };
}
