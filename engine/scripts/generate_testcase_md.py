#!/usr/bin/env python3
"""
generate_testcase_md.py — Generate Markdown test case document from JSON.

Usage:
    python3 generate_testcase_md.py rows.json output.md
    python3 generate_testcase_md.py rows.json output.md --template custom_template.md

Input JSON format:
    [
      {
        "平台": "客户端",
        "模块": "认证中心",
        "功能点": "登录",
        "前置条件（测试点）": "已打开登录页",
        "操作步骤": "1、输入账号\n2、输入密码\n3、点击登录",
        "预期结果": "1、登录成功\n2、跳转首页",
        "测试结果": "",
        "备注": "【功能测试】【P0】"
      }
    ]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_template(template_path: str) -> str:
    """Load MD template file."""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def load_rows(rows_json: str) -> list[dict]:
    """Load test case rows from JSON."""
    with open(rows_json, "r", encoding="utf-8") as f:
        return json.load(f)


def format_steps(text: str) -> str:
    """Convert step separators to numbered list format."""
    if not text:
        return ""
    # Convert semicolons to newlines for numbered steps
    text = text.replace("；", "\n").replace(";", "\n")
    lines = text.split("\n")
    formatted = []
    for line in lines:
        line = line.strip()
        if line:
            formatted.append(line)
    return "\n".join(formatted)


def rows_to_table_rows(rows: list[dict]) -> str:
    """Convert rows to Markdown table format."""
    lines = []
    for row in rows:
        precondition = format_steps(row.get("前置条件（测试点）", ""))
        steps = format_steps(row.get("操作步骤", ""))
        expected = format_steps(row.get("预期结果", ""))

        line = f"| {row.get('序号', '')} | {row.get('功能点', '')} | {precondition} | {steps} | {expected} | {row.get('备注', '')} |"
        lines.append(line)
    return "\n".join(lines) if lines else "| | | | | | |"


def generate_md(
    rows: list[dict],
    template: str,
    output_path: str,
    module: str = "",
    title: str = "",
    excel_path: str = "",
    snapshot_path: str = "",
) -> None:
    """Generate MD file from rows and template."""

    # Separate server and client cases
    server_rows = [r for r in rows if r.get("平台") == "账服"]
    client_rows = [r for r in rows if r.get("平台") == "客户端"]

    # Generate table rows
    server_table = rows_to_table_rows(server_rows)
    client_table = rows_to_table_rows(client_rows)

    # Get unique platforms
    platforms = list(set(r.get("平台", "") for r in rows))
    platform_str = "、".join(sorted(platforms))

    # Format template
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = template.format(
        title=title or module,
        module=module,
        platform=platform_str,
        generated_at=now,
        total_count=len(rows),
        server_cases=server_table,
        client_cases=client_table,
        excel_path=excel_path or "",
        snapshot_path=snapshot_path or "",
    )

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

    print(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MD test case document")
    parser.add_argument("rows_json", help="JSON rows file")
    parser.add_argument("output_md", help="Output MD path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent.parent.parent / "templates" / "testcase_template.md"),
        help="Template MD path",
    )
    parser.add_argument("--module", default="", help="Module name")
    parser.add_argument("--title", default="", help="Document title")
    parser.add_argument("--excel", default="", help="Excel file path")
    parser.add_argument("--snapshot", default="", help="Snapshot path")

    args = parser.parse_args()

    rows = load_rows(args.rows_json)
    template = load_template(args.template)

    generate_md(
        rows=rows,
        template=template,
        output_path=args.output_md,
        module=args.module,
        title=args.title,
        excel_path=args.excel,
        snapshot_path=args.snapshot,
    )


if __name__ == "__main__":
    main()
