import fs from "node:fs";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { WorkspaceManager } from "../services/workspaceManager.js";
import { createTestConfig } from "./helpers.js";

const cleanups: Array<() => Promise<void>> = [];

afterEach(async () => {
  while (cleanups.length > 0) {
    const cleanup = cleanups.pop();
    if (cleanup) {
      await cleanup();
    }
  }
});

describe("workspace manager", () => {
  it("creates isolated snapshot workspaces per session", async () => {
    const fixture = await createTestConfig();
    cleanups.push(fixture.cleanup);
    const manager = new WorkspaceManager(fixture.config);

    const first = await manager.ensureSessionWorkspace("session-a");
    const second = await manager.ensureSessionWorkspace("session-b");

    expect(first.workspacePath).not.toBe(second.workspacePath);
    expect(fs.existsSync(path.join(first.workspacePath, "README.md"))).toBe(true);
    expect(fs.existsSync(first.uploadsPath)).toBe(true);
    expect(fs.existsSync(second.artifactsPath)).toBe(true);
  });
});
