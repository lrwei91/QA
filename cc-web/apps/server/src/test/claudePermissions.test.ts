import { describe, expect, it } from "vitest";
import { isAllowedBashCommand } from "../services/claudePermissions.js";
import { buildPrompt } from "../services/claudeAdapter.js";

describe("claude permissions", () => {
  it("allows read-only and approved python script commands", () => {
    expect(isAllowedBashCommand("pwd")).toBe(true);
    expect(isAllowedBashCommand("rg --files")).toBe(true);
    expect(isAllowedBashCommand("python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/demo.xlsx")).toBe(true);
  });

  it("blocks arbitrary shell commands", () => {
    expect(isAllowedBashCommand("rm -rf /tmp/demo")).toBe(false);
    expect(isAllowedBashCommand("python3 -c 'print(1)'")).toBe(false);
    expect(isAllowedBashCommand("git status")).toBe(false);
  });

  it("builds slash-command prompts with uploaded files", () => {
    const prompt = buildPrompt("generate", "请生成完整用例", ["uploads/demo.md"]);
    expect(prompt).toContain("/qa 生成测试用例");
    expect(prompt).toContain("uploads/demo.md");
  });
});
