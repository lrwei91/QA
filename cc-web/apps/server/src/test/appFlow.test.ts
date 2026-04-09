import fs from "node:fs";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { buildApp } from "../app.js";
import { createTestConfig } from "./helpers.js";

class MockClaudeAdapter {
  async run(context: { workspacePath: string }, callbacks: { onClaudeSessionId(sessionId: string): void; onEvent(event: any): void }) {
    callbacks.onClaudeSessionId("mock-claude-session");
    callbacks.onEvent({
      id: "evt_run_started",
      type: "run.started",
      runId: "mock-run",
      payload: { prompt: "mock" },
      createdAt: new Date().toISOString(),
    });
    callbacks.onEvent({
      id: "evt_delta",
      type: "assistant.delta",
      runId: "mock-run",
      payload: { text: "done" },
      createdAt: new Date().toISOString(),
    });
    await fs.promises.mkdir(path.join(context.workspacePath, "testcases/generated/module"), { recursive: true });
    await fs.promises.writeFile(path.join(context.workspacePath, "testcases/generated/module/demo.xlsx"), "artifact", "utf8");
    return {
      claudeSessionId: "mock-claude-session",
      resultText: "done",
    };
  }

  cancel() {
    return true;
  }
}

const cleanups: Array<() => Promise<void>> = [];

afterEach(async () => {
  while (cleanups.length > 0) {
    const cleanup = cleanups.pop();
    if (cleanup) {
      await cleanup();
    }
  }
});

describe("app flow", () => {
  it("supports login, session creation, message run, artifact listing, logout, and session deletion", async () => {
    const fixture = await createTestConfig();
    cleanups.push(fixture.cleanup);
    const app = await buildApp({
      config: fixture.config,
      claudeAdapter: new MockClaudeAdapter() as any,
    });
    cleanups.push(() => app.close());

    const login = await app.inject({
      method: "POST",
      url: "/api/auth/login",
      payload: {
        username: "admin",
        password: "secret123",
      },
    });
    expect(login.statusCode).toBe(200);
    const cookie = login.cookies[0]?.value;
    expect(cookie).toBeTruthy();

    const created = await app.inject({
      method: "POST",
      url: "/api/sessions",
      headers: {
        cookie: `cc_web_token=${cookie}`,
      },
      payload: {
        name: "集成测试",
      },
    });
    expect(created.statusCode).toBe(200);
    const sessionId = (created.json() as { session: { id: string } }).session.id;

    const sent = await app.inject({
      method: "POST",
      url: `/api/sessions/${sessionId}/messages`,
      headers: {
        cookie: `cc_web_token=${cookie}`,
      },
      payload: {
        action: "generate",
        text: "请生成测试用例",
        uploadPaths: [],
      },
    });
    expect(sent.statusCode).toBe(200);

    await waitFor(async () => {
      const artifacts = await app.inject({
        method: "GET",
        url: `/api/sessions/${sessionId}/artifacts`,
        headers: {
          cookie: `cc_web_token=${cookie}`,
        },
      });
      const body = artifacts.json() as { artifacts: Array<{ relativePath: string }> };
      expect(body.artifacts[0]?.relativePath).toBe("testcases/generated/module/demo.xlsx");
    });

    const deleted = await app.inject({
      method: "DELETE",
      url: `/api/sessions/${sessionId}`,
      headers: {
        cookie: `cc_web_token=${cookie}`,
      },
    });
    expect(deleted.statusCode).toBe(200);

    const logout = await app.inject({
      method: "POST",
      url: "/api/auth/logout",
      headers: {
        cookie: `cc_web_token=${cookie}`,
      },
    });
    expect(logout.statusCode).toBe(200);
  });
});

async function waitFor(assertion: () => Promise<void>, timeoutMs = 1000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    try {
      await assertion();
      return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 30));
    }
  }
  await assertion();
}
