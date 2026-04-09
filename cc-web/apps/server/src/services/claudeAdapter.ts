import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import type { QuickAction, SseEvent } from "@cc-web/shared";
import type { AppConfig } from "../config/env.js";
import { newId, nowIso, toErrorMessage } from "../lib/utils.js";
import { buildAllowedTools } from "./claudePermissions.js";

export type ClaudeRunContext = {
  runId: string;
  sessionId: string;
  workspacePath: string;
  logPath: string;
  prompt: string;
  claudeSessionId?: string | null;
};

export type ClaudeRunResult = {
  claudeSessionId: string | null;
  resultText: string;
};

export type ClaudeEventCallbacks = {
  onEvent(event: SseEvent): void;
  onClaudeSessionId(sessionId: string): void;
};

export class ClaudeAdapter {
  private readonly activeProcesses = new Map<string, ReturnType<typeof spawn>>();

  constructor(private readonly config: AppConfig) {}

  async run(context: ClaudeRunContext, callbacks: ClaudeEventCallbacks): Promise<ClaudeRunResult> {
    const allowedTools = buildAllowedTools();
    const args = [
      "-p",
      "--verbose",
      "--output-format",
      "stream-json",
      "--include-partial-messages",
      "--permission-mode",
      "dontAsk",
      "--allowedTools",
      ...allowedTools,
      "--append-system-prompt",
      buildSystemPrompt(),
    ];

    if (this.config.defaultModel) {
      args.push("--model", this.config.defaultModel);
    }
    if (context.claudeSessionId) {
      args.push("--resume", context.claudeSessionId);
    }
    args.push("--", context.prompt);

    await fs.promises.mkdir(path.dirname(context.logPath), { recursive: true });
    const logStream = fs.createWriteStream(context.logPath, { flags: "a" });
    const child = spawn("claude", args, {
      cwd: context.workspacePath,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    this.activeProcesses.set(context.runId, child);

    let buffer = "";
    let stderr = "";
    let assistantText = "";
    let claudeSessionId = context.claudeSessionId ?? null;
    let pendingToolInputs = new Map<number, { toolId?: string; name?: string; partialJson: string }>();

    callbacks.onEvent({
      id: newId("evt"),
      type: "run.started",
      runId: context.runId,
      payload: { sessionId: context.sessionId, prompt: context.prompt },
      createdAt: nowIso(),
    });

    const handleLine = (line: string) => {
      logStream.write(`${line}\n`);
      let parsed: any;
      try {
        parsed = JSON.parse(line);
      } catch {
        return;
      }

      if (parsed.session_id && !claudeSessionId) {
        claudeSessionId = parsed.session_id as string;
        callbacks.onClaudeSessionId(claudeSessionId);
      }

      if (parsed.type === "stream_event") {
        const event = parsed.event;
        if (event.type === "content_block_start" && event.content_block?.type === "tool_use") {
          const entry = {
            toolId: event.content_block.id as string,
            name: event.content_block.name as string,
            partialJson: "",
          };
          pendingToolInputs.set(event.index as number, entry);
          callbacks.onEvent({
            id: newId("evt"),
            type: "tool.started",
            runId: context.runId,
            payload: { toolId: entry.toolId, name: entry.name },
            createdAt: nowIso(),
          });
          return;
        }

        if (event.type === "content_block_delta" && event.delta?.type === "input_json_delta") {
          const current = pendingToolInputs.get(event.index as number);
          if (!current) {
            return;
          }
          current.partialJson += event.delta.partial_json as string;
          callbacks.onEvent({
            id: newId("evt"),
            type: "tool.output",
            runId: context.runId,
            payload: { toolId: current.toolId, stage: "input", text: current.partialJson },
            createdAt: nowIso(),
          });
          return;
        }

        if (event.type === "content_block_delta" && event.delta?.type === "text_delta") {
          const text = event.delta.text as string;
          assistantText += text;
          callbacks.onEvent({
            id: newId("evt"),
            type: "assistant.delta",
            runId: context.runId,
            payload: { text },
            createdAt: nowIso(),
          });
        }
        return;
      }

      if (parsed.type === "user" && parsed.message?.content?.[0]?.type === "tool_result") {
        const content = parsed.message.content[0];
        callbacks.onEvent({
          id: newId("evt"),
          type: "tool.output",
          runId: context.runId,
          payload: {
            toolId: content.tool_use_id,
            stage: "result",
            text: parsed.tool_use_result?.stdout || content.content || "",
            stderr: parsed.tool_use_result?.stderr || "",
          },
          createdAt: nowIso(),
        });
        callbacks.onEvent({
          id: newId("evt"),
          type: "tool.completed",
          runId: context.runId,
          payload: {
            toolId: content.tool_use_id,
            interrupted: Boolean(parsed.tool_use_result?.interrupted),
            isError: Boolean(content.is_error),
          },
          createdAt: nowIso(),
        });
        return;
      }

      if (parsed.type === "result") {
        if (parsed.subtype === "success" && !parsed.is_error) {
          const resultText = typeof parsed.result === "string" ? parsed.result : assistantText;
          callbacks.onEvent({
            id: newId("evt"),
            type: "assistant.completed",
            runId: context.runId,
            payload: { text: resultText, usage: parsed.usage ?? null },
            createdAt: nowIso(),
          });
          return;
        }
        callbacks.onEvent({
          id: newId("evt"),
          type: "run.failed",
          runId: context.runId,
          payload: {
            errorCode: parsed.subtype ?? "claude_error",
            errorMessage: parsed.result || "Claude execution failed",
          },
          createdAt: nowIso(),
        });
      }
    };

    child.stdout.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      buffer += text;
      let newlineIndex = buffer.indexOf("\n");
      while (newlineIndex >= 0) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);
        if (line) {
          handleLine(line);
        }
        newlineIndex = buffer.indexOf("\n");
      }
    });

    child.stderr.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      stderr += text;
      logStream.write(text);
    });

    return await new Promise<ClaudeRunResult>((resolve, reject) => {
      child.on("error", (error) => {
        this.activeProcesses.delete(context.runId);
        logStream.end();
        reject(error);
      });
      child.on("close", (code) => {
        this.activeProcesses.delete(context.runId);
        logStream.end();
        if (buffer.trim()) {
          handleLine(buffer.trim());
        }
        if (code === 0) {
          resolve({
            claudeSessionId,
            resultText: assistantText,
          });
          return;
        }
        reject(new Error(stderr.trim() || `claude exited with code ${code}`));
      });
    });
  }

  cancel(runId: string): boolean {
    const child = this.activeProcesses.get(runId);
    if (!child) {
      return false;
    }
    child.kill("SIGTERM");
    this.activeProcesses.delete(runId);
    return true;
  }
}

export function buildSystemPrompt(): string {
  return [
    "You are operating inside a QA-only web wrapper for Claude Code.",
    "You must stay within the current workspace and use the /qa workflow when the user asks to generate, supplement, analyze, export, or build i18n validation output.",
    "Prefer Read, Glob, Grep, Edit, and Write tools for repo inspection and file edits.",
    "Only use the Bash tool for read-only shell commands and the approved Python scripts already available in this repository.",
    "Never attempt to access files outside the current workspace.",
    "If uploaded files are referenced, read them from the workspace uploads directory.",
  ].join(" ");
}

export function buildPrompt(action: QuickAction, text: string, uploadPaths: string[]): string {
  const uploadSection =
    uploadPaths.length > 0
      ? `\n\n可用上传文件：\n${uploadPaths.map((item) => `- ${item}`).join("\n")}\n请在需要时主动读取这些文件。`
      : "";

  const body = text.trim();
  switch (action) {
    case "generate":
      return `/qa 生成测试用例\n\n${body || "请根据当前输入生成完整测试用例。"}${uploadSection}`;
    case "supplement":
      return `/qa 补充已有用例\n\n${body || "请在避免重复的前提下补充新增测试用例。"}${uploadSection}`;
    case "analyze":
      return `/qa 仅分析需求，不生成用例\n\n${body || "请分析当前需求并输出结构化分析结果。"}${uploadSection}`;
    case "export":
      return `/qa 导出 Excel\n\n${body || "请将当前结果导出为 Excel 并落到工作区。"}${uploadSection}`;
    case "i18n":
      return `/qa 生成多语言校验 JSON\n\n${body || "请生成多语言校验 JSON。"}${uploadSection}`;
    case "custom":
      return `${body}${uploadSection}`;
  }
}

export function classifyClaudeFailure(error: unknown): { errorCode: string; errorMessage: string } {
  const message = toErrorMessage(error);
  if (/Could not find/i.test(message) || /spawn claude ENOENT/i.test(message)) {
    return { errorCode: "claude_missing", errorMessage: "claude CLI 未安装或不在 PATH 中" };
  }
  if (/Invalid API key|authentication|subscription|login|token/i.test(message)) {
    return { errorCode: "claude_auth", errorMessage: "Claude Code 未登录或 token 无效" };
  }
  if (/permission/i.test(message)) {
    return { errorCode: "permission_denied", errorMessage: message };
  }
  return { errorCode: "claude_run_failed", errorMessage: message };
}
