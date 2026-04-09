import fs from "node:fs";
import path from "node:path";
import Database from "better-sqlite3";
import type { ArtifactRecord, AuthUser, QuickAction, RunSummary, WebSessionSummary } from "@cc-web/shared";
import { nowIso, normalizeName } from "../lib/utils.js";

export interface DbUserRow {
  id: string;
  username: string;
  password_hash: string;
  role: "admin" | "member";
  created_at: string;
}

export interface DbSessionRow {
  id: string;
  user_id: string;
  name: string;
  claude_session_id: string | null;
  workspace_path: string;
  artifacts_path: string;
  source_repo_path: string;
  workspace_mode: "git-worktree" | "snapshot-copy";
  status: "idle" | "running";
  created_at: string;
  updated_at: string;
  last_run_id: string | null;
}

export interface DbRunRow {
  id: string;
  session_id: string;
  user_id: string;
  action: QuickAction;
  prompt: string;
  prompt_preview: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  claude_session_id: string | null;
  result_text: string | null;
  error_code: string | null;
  error_message: string | null;
  raw_log_path: string;
  started_at: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DbArtifactRow {
  id: string;
  session_id: string;
  run_id: string;
  relative_path: string;
  workspace_path: string;
  artifact_path: string;
  publish_target_path: string;
  status: "ready" | "published";
  size_bytes: number;
  mime_type: string;
  checksum: string;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  published_by: string | null;
}

export interface DatabaseClient {
  sqlite: Database.Database;
  close(): void;
  bootstrap(): void;
}

export function createDatabase(dbPath: string): DatabaseClient {
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  const sqlite = new Database(dbPath);
  sqlite.pragma("journal_mode = WAL");
  sqlite.pragma("foreign_keys = ON");

  const client: DatabaseClient = {
    sqlite,
    close() {
      sqlite.close();
    },
    bootstrap() {
      sqlite.exec(`
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          username TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS web_sessions (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          name TEXT NOT NULL,
          claude_session_id TEXT,
          workspace_path TEXT NOT NULL,
          artifacts_path TEXT NOT NULL,
          source_repo_path TEXT NOT NULL,
          workspace_mode TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          last_run_id TEXT,
          FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS claude_runs (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          user_id TEXT NOT NULL,
          action TEXT NOT NULL,
          prompt TEXT NOT NULL,
          prompt_preview TEXT NOT NULL,
          status TEXT NOT NULL,
          claude_session_id TEXT,
          result_text TEXT,
          error_code TEXT,
          error_message TEXT,
          raw_log_path TEXT NOT NULL,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY (session_id) REFERENCES web_sessions(id),
          FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS artifacts (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          relative_path TEXT NOT NULL,
          workspace_path TEXT NOT NULL,
          artifact_path TEXT NOT NULL,
          publish_target_path TEXT NOT NULL,
          status TEXT NOT NULL,
          size_bytes INTEGER NOT NULL,
          mime_type TEXT NOT NULL,
          checksum TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          published_at TEXT,
          published_by TEXT,
          UNIQUE (session_id, relative_path),
          FOREIGN KEY (session_id) REFERENCES web_sessions(id),
          FOREIGN KEY (run_id) REFERENCES claude_runs(id)
        );

        CREATE TABLE IF NOT EXISTS publish_jobs (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          artifact_ids_json TEXT NOT NULL,
          status TEXT NOT NULL,
          conflict_summary_json TEXT NOT NULL,
          result_json TEXT,
          created_by TEXT NOT NULL,
          created_at TEXT NOT NULL,
          completed_at TEXT,
          FOREIGN KEY (session_id) REFERENCES web_sessions(id),
          FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          session_id TEXT,
          entity_type TEXT NOT NULL,
          entity_id TEXT NOT NULL,
          action TEXT NOT NULL,
          detail_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users(id)
        );
      `);

      sqlite
        .prepare("UPDATE claude_runs SET status = 'failed', error_code = 'server_restart', error_message = 'Run interrupted by server restart', updated_at = ?, completed_at = COALESCE(completed_at, ?) WHERE status = 'running'")
        .run(nowIso(), nowIso());
      sqlite
        .prepare("UPDATE web_sessions SET status = 'idle', updated_at = ? WHERE status = 'running'")
        .run(nowIso());
    },
  };

  client.bootstrap();
  return client;
}

export function mapUser(row: DbUserRow): AuthUser {
  return {
    id: row.id,
    username: row.username,
    role: row.role,
    createdAt: row.created_at,
  };
}

export function mapSession(row: DbSessionRow): WebSessionSummary {
  return {
    id: row.id,
    name: row.name,
    claudeSessionId: row.claude_session_id,
    workspaceMode: row.workspace_mode,
    status: row.status,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    lastRunId: row.last_run_id,
  };
}

export function mapRun(row: DbRunRow): RunSummary {
  return {
    id: row.id,
    sessionId: row.session_id,
    action: row.action,
    promptPreview: row.prompt_preview,
    status: row.status,
    claudeSessionId: row.claude_session_id,
    resultText: row.result_text,
    errorCode: row.error_code,
    errorMessage: row.error_message,
    startedAt: row.started_at,
    completedAt: row.completed_at,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

export function mapArtifact(row: DbArtifactRow): ArtifactRecord {
  return {
    id: row.id,
    sessionId: row.session_id,
    runId: row.run_id,
    relativePath: row.relative_path,
    artifactPath: row.artifact_path,
    publishTargetPath: row.publish_target_path,
    status: row.status,
    sizeBytes: row.size_bytes,
    mimeType: row.mime_type,
    checksum: row.checksum,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    publishedAt: row.published_at,
  };
}

export function previewText(prompt: string): string {
  return normalizeName(prompt).slice(0, 160);
}
