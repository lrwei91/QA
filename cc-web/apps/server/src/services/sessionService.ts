import path from "node:path";
import type { CreateSessionRequest } from "@cc-web/shared";
import type { DatabaseClient, DbRunRow, DbSessionRow } from "../db/client.js";
import { mapRun, mapSession, previewText } from "../db/client.js";
import { newId, nowIso, normalizeName } from "../lib/utils.js";
import type { SessionWorkspace, WorkspaceManager } from "./workspaceManager.js";

export class SessionService {
  constructor(
    private readonly db: DatabaseClient,
    private readonly workspaceManager: WorkspaceManager,
    private readonly sourceRepoPath: string,
  ) {}

  async createSession(userId: string, request: CreateSessionRequest) {
    const id = newId("ses");
    const now = nowIso();
    const workspace = await this.workspaceManager.ensureSessionWorkspace(id);
    const row: DbSessionRow = {
      id,
      user_id: userId,
      name: normalizeName(request.name),
      claude_session_id: null,
      workspace_path: workspace.workspacePath,
      artifacts_path: workspace.artifactsPath,
      source_repo_path: this.sourceRepoPath,
      workspace_mode: workspace.workspaceMode,
      status: "idle",
      created_at: now,
      updated_at: now,
      last_run_id: null,
    };
    this.db.sqlite
      .prepare(`
        INSERT INTO web_sessions (
          id, user_id, name, claude_session_id, workspace_path, artifacts_path, source_repo_path,
          workspace_mode, status, created_at, updated_at, last_run_id
        ) VALUES (
          @id, @user_id, @name, @claude_session_id, @workspace_path, @artifacts_path, @source_repo_path,
          @workspace_mode, @status, @created_at, @updated_at, @last_run_id
        )
      `)
      .run(row);
    return { session: mapSession(row), workspace };
  }

  listSessions(userId: string) {
    const rows = this.db.sqlite
      .prepare("SELECT * FROM web_sessions WHERE user_id = ? ORDER BY updated_at DESC")
      .all(userId) as DbSessionRow[];
    return rows.map(mapSession);
  }

  getSession(sessionId: string, userId: string): DbSessionRow | undefined {
    return this.db.sqlite
      .prepare("SELECT * FROM web_sessions WHERE id = ? AND user_id = ?")
      .get(sessionId, userId) as DbSessionRow | undefined;
  }

  setSessionStatus(sessionId: string, status: "idle" | "running", lastRunId?: string | null, claudeSessionId?: string | null) {
    this.db.sqlite
      .prepare(
        `
          UPDATE web_sessions
          SET status = ?, updated_at = ?, last_run_id = COALESCE(?, last_run_id), claude_session_id = COALESCE(?, claude_session_id)
          WHERE id = ?
        `,
      )
      .run(status, nowIso(), lastRunId ?? null, claudeSessionId ?? null, sessionId);
  }

  createRun(sessionId: string, userId: string, action: DbRunRow["action"], prompt: string, rawLogPath: string): DbRunRow {
    const now = nowIso();
    const row: DbRunRow = {
      id: newId("run"),
      session_id: sessionId,
      user_id: userId,
      action,
      prompt,
      prompt_preview: previewText(prompt),
      status: "running",
      claude_session_id: null,
      result_text: null,
      error_code: null,
      error_message: null,
      raw_log_path: rawLogPath,
      started_at: now,
      completed_at: null,
      created_at: now,
      updated_at: now,
    };
    this.db.sqlite
      .prepare(`
        INSERT INTO claude_runs (
          id, session_id, user_id, action, prompt, prompt_preview, status, claude_session_id,
          result_text, error_code, error_message, raw_log_path, started_at, completed_at, created_at, updated_at
        ) VALUES (
          @id, @session_id, @user_id, @action, @prompt, @prompt_preview, @status, @claude_session_id,
          @result_text, @error_code, @error_message, @raw_log_path, @started_at, @completed_at, @created_at, @updated_at
        )
      `)
      .run(row);
    this.setSessionStatus(sessionId, "running", row.id);
    return row;
  }

  updateRun(runId: string, patch: Partial<Pick<DbRunRow, "status" | "claude_session_id" | "result_text" | "error_code" | "error_message" | "completed_at">>) {
    const current = this.db.sqlite.prepare("SELECT * FROM claude_runs WHERE id = ?").get(runId) as DbRunRow | undefined;
    if (!current) {
      return;
    }
    const next: DbRunRow = {
      ...current,
      ...patch,
      updated_at: nowIso(),
    };
    this.db.sqlite
      .prepare(`
        UPDATE claude_runs
        SET status = @status,
            claude_session_id = @claude_session_id,
            result_text = @result_text,
            error_code = @error_code,
            error_message = @error_message,
            completed_at = @completed_at,
            updated_at = @updated_at
        WHERE id = @id
      `)
      .run(next);
    if (patch.status && patch.status !== "running") {
      this.setSessionStatus(current.session_id, "idle", runId, patch.claude_session_id ?? current.claude_session_id);
    } else if (patch.claude_session_id) {
      this.setSessionStatus(current.session_id, "running", runId, patch.claude_session_id);
    }
  }

  getRun(runId: string, userId: string): DbRunRow | undefined {
    return this.db.sqlite
      .prepare("SELECT * FROM claude_runs WHERE id = ? AND user_id = ?")
      .get(runId, userId) as DbRunRow | undefined;
  }

  listRuns(sessionId: string) {
    const rows = this.db.sqlite
      .prepare("SELECT * FROM claude_runs WHERE session_id = ? ORDER BY created_at ASC")
      .all(sessionId) as DbRunRow[];
    return rows.map(mapRun);
  }

  activeRunExists(sessionId: string): boolean {
    const row = this.db.sqlite
      .prepare("SELECT id FROM claude_runs WHERE session_id = ? AND status = 'running' LIMIT 1")
      .get(sessionId) as { id: string } | undefined;
    return Boolean(row);
  }

  ensureWorkspace(row: DbSessionRow): Promise<SessionWorkspace> {
    return this.workspaceManager.ensureSessionWorkspace(row.id);
  }

  async deleteSession(sessionId: string, userId: string): Promise<"deleted" | "running" | "missing"> {
    const row = this.getSession(sessionId, userId);
    if (!row) {
      return "missing";
    }
    if (this.activeRunExists(sessionId)) {
      return "running";
    }

    const sessionRoot = path.dirname(row.workspace_path);
    await this.workspaceManager.deleteSessionWorkspace(row.workspace_path, sessionRoot, row.workspace_mode);

    const transaction = this.db.sqlite.transaction(() => {
      this.db.sqlite.prepare("DELETE FROM artifacts WHERE session_id = ?").run(sessionId);
      this.db.sqlite.prepare("DELETE FROM claude_runs WHERE session_id = ?").run(sessionId);
      this.db.sqlite.prepare("DELETE FROM publish_jobs WHERE session_id = ?").run(sessionId);
      this.db.sqlite.prepare("DELETE FROM audit_logs WHERE session_id = ?").run(sessionId);
      this.db.sqlite.prepare("DELETE FROM web_sessions WHERE id = ? AND user_id = ?").run(sessionId, userId);
    });
    transaction();
    return "deleted";
  }
}
