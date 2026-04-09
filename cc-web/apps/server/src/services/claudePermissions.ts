export function buildAllowedTools(): string[] {
  return [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Skill",
    "WebFetch",
    "Bash(pwd:*)",
    "Bash(ls:*)",
    "Bash(find:*)",
    "Bash(rg:*)",
    "Bash(cat:*)",
    "Bash(head:*)",
    "Bash(tail:*)",
    "Bash(sed:*)",
    "Bash(wc:*)",
    "Bash(python3 test-case-generator/scripts/upsert_testcase_index.py:*)",
    "Bash(python3 test-case-generator/scripts/validate_testcase_index.py:*)",
    "Bash(python3 test-case-generator/scripts/validate_i18n_index.py:*)",
    "Bash(python3 test-case-generator/scripts/validate_i18n_json.py:*)",
    "Bash(python3 test-case-generator/scripts/validate_index.py:*)",
    "Bash(python3 test-case-generator/scripts/xlsx_fill_testcase_template.py:*)",
    "Bash(python3 test-case-generator/scripts/xlsx_append_and_highlight.py:*)",
    "Bash(python3 test-case-generator/scripts/export_testcase_report.py:*)",
    "Bash(python3 test-case-generator/scripts/generate_testcase_from_template.py:*)",
  ];
}

export function isAllowedBashCommand(command: string): boolean {
  const normalized = command.trim();
  if (/^(pwd|ls|find|rg|cat|head|tail|sed|wc)(\s|$)/.test(normalized)) {
    return true;
  }
  return /^python3\s+test-case-generator\/scripts\/(upsert_testcase_index|validate_testcase_index|validate_i18n_index|validate_i18n_json|validate_index|xlsx_fill_testcase_template|xlsx_append_and_highlight|export_testcase_report|generate_testcase_from_template)\.py(\s|$)/.test(
    normalized,
  );
}
