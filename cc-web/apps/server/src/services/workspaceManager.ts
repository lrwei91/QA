import fs from "node:fs";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { AppConfig } from "../config/env.js";

const execFileAsync = promisify(execFile);

export interface SessionWorkspace {
  workspacePath: string;
  artifactsPath: string;
  sessionRoot: string;
  uploadsPath: string;
  logsPath: string;
  workspaceMode: "git-worktree" | "snapshot-copy";
}

export class WorkspaceManager {
  constructor(private readonly config: AppConfig) {}

  async ensureSessionWorkspace(sessionId: string): Promise<SessionWorkspace> {
    const sessionRoot = path.join(this.config.dataDir, "sessions", sessionId);
    const workspacePath = path.join(sessionRoot, "workspace");
    const artifactsPath = path.join(sessionRoot, "artifacts");
    const uploadsPath = path.join(workspacePath, "uploads");
    const logsPath = path.join(sessionRoot, "logs");

    if (!fs.existsSync(workspacePath)) {
      fs.mkdirSync(sessionRoot, { recursive: true });
      const gitMode = await this.isGitRepository(this.config.sourceRepo);
      if (gitMode) {
        await execFileAsync("git", ["-C", this.config.sourceRepo, "worktree", "add", "--detach", workspacePath, "HEAD"]);
      } else {
        await fs.promises.cp(this.config.sourceRepo, workspacePath, {
          recursive: true,
          force: true,
          filter: (src) => {
            const normalized = path.resolve(src);
            if (normalized === path.resolve(this.config.dataDir)) {
              return false;
            }
            const basename = path.basename(normalized);
            return basename !== ".git" && basename !== "node_modules";
          },
        });
      }
    }

    fs.mkdirSync(artifactsPath, { recursive: true });
    fs.mkdirSync(uploadsPath, { recursive: true });
    fs.mkdirSync(logsPath, { recursive: true });

    return {
      sessionRoot,
      workspacePath,
      artifactsPath,
      uploadsPath,
      logsPath,
      workspaceMode: (await this.isGitRepository(this.config.sourceRepo)) ? "git-worktree" : "snapshot-copy",
    };
  }

  async deleteSessionWorkspace(
    workspacePath: string,
    sessionRoot: string,
    workspaceMode: "git-worktree" | "snapshot-copy",
  ): Promise<void> {
    if (workspaceMode === "git-worktree" && fs.existsSync(workspacePath)) {
      await execFileAsync("git", ["-C", this.config.sourceRepo, "worktree", "remove", "--force", workspacePath]);
    }

    if (fs.existsSync(sessionRoot)) {
      await fs.promises.rm(sessionRoot, { recursive: true, force: true });
    }
  }

  private async isGitRepository(targetPath: string): Promise<boolean> {
    try {
      const { stdout } = await execFileAsync("git", ["-C", targetPath, "rev-parse", "--is-inside-work-tree"]);
      return stdout.trim() === "true";
    } catch {
      return false;
    }
  }
}
