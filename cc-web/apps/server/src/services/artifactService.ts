import fs from "node:fs";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import mime from "mime-types";
import type { ArtifactRecord, PublishConflict, PublishPreview } from "@cc-web/shared";
import type { AppConfig } from "../config/env.js";
import type { DatabaseClient, DbArtifactRow } from "../db/client.js";
import { mapArtifact } from "../db/client.js";
import { checksumBuffer, newId, nowIso } from "../lib/utils.js";

const execFileAsync = promisify(execFile);

type FileSnapshot = Map<string, { mtimeMs: number; size: number }>;

export class ArtifactService {
  private readonly publishLocks = new Set<string>();

  constructor(private readonly db: DatabaseClient, private readonly config: AppConfig) {}

  scanWorkspaceArtifacts(workspacePath: string): FileSnapshot {
    const snapshot: FileSnapshot = new Map();
    const targets = ["testcases/generated", "testcases/i18n", "testcases/testcase-index.json", "testcases/i18n-index.json"];

    for (const target of targets) {
      const absolute = path.join(workspacePath, target);
      if (!fs.existsSync(absolute)) {
        continue;
      }
      const stat = fs.statSync(absolute);
      if (stat.isDirectory()) {
        for (const filePath of walkFiles(absolute)) {
          const relPath = path.relative(workspacePath, filePath);
          const fileStat = fs.statSync(filePath);
          snapshot.set(relPath, { mtimeMs: fileStat.mtimeMs, size: fileStat.size });
        }
      } else {
        snapshot.set(target, { mtimeMs: stat.mtimeMs, size: stat.size });
      }
    }

    return snapshot;
  }

  async captureChangedArtifacts(sessionId: string, runId: string, workspacePath: string, artifactsPath: string, before: FileSnapshot): Promise<ArtifactRecord[]> {
    const after = this.scanWorkspaceArtifacts(workspacePath);
    const changed = [...after.entries()].filter(([relPath, stat]) => {
      const previous = before.get(relPath);
      return !previous || previous.mtimeMs !== stat.mtimeMs || previous.size !== stat.size;
    });

    const records: ArtifactRecord[] = [];
    for (const [relativePath] of changed) {
      if (!/\.(xlsx|json|md|txt|csv|docx)$/i.test(relativePath)) {
        continue;
      }
      const sourcePath = path.join(workspacePath, relativePath);
      if (!fs.existsSync(sourcePath) || fs.statSync(sourcePath).isDirectory()) {
        continue;
      }
      const artifactPath = path.join(artifactsPath, relativePath);
      await fs.promises.mkdir(path.dirname(artifactPath), { recursive: true });
      await fs.promises.copyFile(sourcePath, artifactPath);
      const buffer = await fs.promises.readFile(artifactPath);
      const now = nowIso();
      const existing = this.db.sqlite
        .prepare("SELECT * FROM artifacts WHERE session_id = ? AND relative_path = ?")
        .get(sessionId, relativePath) as DbArtifactRow | undefined;

      const row: DbArtifactRow = {
        id: existing?.id ?? newId("art"),
        session_id: sessionId,
        run_id: runId,
        relative_path: relativePath,
        workspace_path: sourcePath,
        artifact_path: artifactPath,
        publish_target_path: path.join(this.config.sourceRepo, relativePath),
        status: existing?.status ?? "ready",
        size_bytes: buffer.byteLength,
        mime_type: mime.lookup(artifactPath) || "application/octet-stream",
        checksum: checksumBuffer(buffer),
        created_at: existing?.created_at ?? now,
        updated_at: now,
        published_at: existing?.published_at ?? null,
        published_by: existing?.published_by ?? null,
      };

      this.db.sqlite
        .prepare(`
          INSERT INTO artifacts (
            id, session_id, run_id, relative_path, workspace_path, artifact_path, publish_target_path,
            status, size_bytes, mime_type, checksum, created_at, updated_at, published_at, published_by
          ) VALUES (
            @id, @session_id, @run_id, @relative_path, @workspace_path, @artifact_path, @publish_target_path,
            @status, @size_bytes, @mime_type, @checksum, @created_at, @updated_at, @published_at, @published_by
          )
          ON CONFLICT(session_id, relative_path) DO UPDATE SET
            run_id = excluded.run_id,
            workspace_path = excluded.workspace_path,
            artifact_path = excluded.artifact_path,
            publish_target_path = excluded.publish_target_path,
            status = excluded.status,
            size_bytes = excluded.size_bytes,
            mime_type = excluded.mime_type,
            checksum = excluded.checksum,
            updated_at = excluded.updated_at
        `)
        .run(row);
      records.push(mapArtifact(row));
    }

    return records;
  }

  listSessionArtifacts(sessionId: string): ArtifactRecord[] {
    const rows = this.db.sqlite
      .prepare("SELECT * FROM artifacts WHERE session_id = ? ORDER BY updated_at DESC")
      .all(sessionId) as DbArtifactRow[];
    return rows.map(mapArtifact);
  }

  getArtifactsByIds(sessionId: string, artifactIds: string[]): ArtifactRecord[] {
    const statement = this.db.sqlite.prepare(
      `SELECT * FROM artifacts WHERE session_id = ? AND id IN (${artifactIds.map(() => "?").join(",")})`,
    );
    const rows = statement.all(sessionId, ...artifactIds) as DbArtifactRow[];
    return rows.map(mapArtifact);
  }

  previewPublish(artifacts: ArtifactRecord[]): PublishPreview {
    const conflicts: PublishConflict[] = artifacts.map((artifact) => {
      const exists = fs.existsSync(artifact.publishTargetPath);
      let changed = false;
      if (exists) {
        const currentChecksum = checksumBuffer(fs.readFileSync(artifact.publishTargetPath));
        changed = currentChecksum !== artifact.checksum;
      }
      return {
        artifactId: artifact.id,
        relativePath: artifact.relativePath,
        targetPath: artifact.publishTargetPath,
        exists,
        changed,
      };
    });

    return { conflicts, selected: artifacts };
  }

  async publishArtifacts(userId: string, sessionId: string, artifacts: ArtifactRecord[], force: boolean): Promise<PublishPreview> {
    const preview = this.previewPublish(artifacts);
    const blocking = preview.conflicts.filter((item) => item.exists && item.changed);
    if (blocking.length > 0 && !force) {
      return preview;
    }

    const targets = preview.conflicts.map((item) => item.targetPath).sort();
    for (const target of targets) {
      if (this.publishLocks.has(target)) {
        throw new Error(`Publish lock already held for ${target}`);
      }
      this.publishLocks.add(target);
    }

    const backupRoot = path.join(this.config.dataDir, "publish-backups", newId("job"));
    await fs.promises.mkdir(backupRoot, { recursive: true });

    try {
      for (const artifact of artifacts) {
        const backupPath = path.join(backupRoot, artifact.relativePath);
        await fs.promises.mkdir(path.dirname(backupPath), { recursive: true });
        if (fs.existsSync(artifact.publishTargetPath)) {
          await fs.promises.copyFile(artifact.publishTargetPath, backupPath);
        }
        await fs.promises.mkdir(path.dirname(artifact.publishTargetPath), { recursive: true });
        await fs.promises.copyFile(artifact.artifactPath, artifact.publishTargetPath);
      }

      for (const artifact of artifacts) {
        const relative = path.relative(this.config.sourceRepo, artifact.publishTargetPath);
        if (!relative.startsWith("testcases/")) {
          continue;
        }
        await execFileAsync("python3", ["test-case-generator/scripts/upsert_testcase_index.py", relative], {
          cwd: this.config.sourceRepo,
        });
      }

      if (fs.existsSync(path.join(this.config.sourceRepo, "testcases/testcase-index.json"))) {
        await execFileAsync("python3", ["test-case-generator/scripts/validate_testcase_index.py", "testcases/testcase-index.json"], {
          cwd: this.config.sourceRepo,
        });
      }
      if (fs.existsSync(path.join(this.config.sourceRepo, "testcases/i18n-index.json"))) {
        await execFileAsync("python3", ["test-case-generator/scripts/validate_i18n_index.py", "testcases/i18n-index.json"], {
          cwd: this.config.sourceRepo,
        });
      }

      const now = nowIso();
      const statement = this.db.sqlite.prepare(
        "UPDATE artifacts SET status = 'published', published_at = ?, published_by = ?, updated_at = ? WHERE id = ? AND session_id = ?",
      );
      const transaction = this.db.sqlite.transaction(() => {
        for (const artifact of artifacts) {
          statement.run(now, userId, now, artifact.id, sessionId);
        }
      });
      transaction();
      return this.previewPublish(this.getArtifactsByIds(sessionId, artifacts.map((artifact) => artifact.id)));
    } catch (error) {
      for (const artifact of artifacts) {
        const backupPath = path.join(backupRoot, artifact.relativePath);
        if (fs.existsSync(backupPath)) {
          await fs.promises.copyFile(backupPath, artifact.publishTargetPath);
        } else if (fs.existsSync(artifact.publishTargetPath)) {
          await fs.promises.rm(artifact.publishTargetPath);
        }
      }
      throw error;
    } finally {
      for (const target of targets) {
        this.publishLocks.delete(target);
      }
    }
  }
}

function* walkFiles(root: string): Generator<string> {
  const entries = fs.readdirSync(root, { withFileTypes: true });
  for (const entry of entries) {
    const absolute = path.join(root, entry.name);
    if (entry.isDirectory()) {
      yield* walkFiles(absolute);
    } else {
      yield absolute;
    }
  }
}
