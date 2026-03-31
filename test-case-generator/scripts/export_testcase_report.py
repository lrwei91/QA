#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
export_testcase_report.py - Generate testcase coverage and statistics report.

Usage:
    python3 export_testcase_report.py [--format json|html|markdown] [--output report.json]

This script generates:
- Test case count by module
- Coverage statistics
- Status breakdown (draft/active/archived)
- Platform distribution (客户端/账服)
- Tag analysis
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


def load_index(index_path: str) -> tuple:
    """Load index JSON file."""
    if not os.path.exists(index_path):
        return None, f"File not found: {index_path}"

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except Exception as e:
        return None, f"Error reading: {e}"


def generate_report(index_data: dict, i18n_index_data: dict = None) -> dict:
    """Generate comprehensive report from index data."""
    testcases = index_data.get("testcases", [])

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_testcases": len(testcases),
            "by_status": defaultdict(int),
            "by_format": defaultdict(int),
            "by_platform": defaultdict(int)
        },
        "modules": defaultdict(lambda: {
            "count": 0,
            "testcases": [],
            "statuses": defaultdict(int)
        }),
        "tags": defaultdict(int),
        "i18n": None
    }

    # Process testcases
    for entry in testcases:
        status = entry.get("status", "unknown")
        format_type = entry.get("format", "unknown")
        module = entry.get("module", "Unknown")
        platforms = entry.get("platform_scope", [])
        tags = entry.get("tags", [])

        report["summary"]["by_status"][status] += 1
        report["summary"]["by_format"][format_type] += 1

        # Platform distribution
        if isinstance(platforms, list):
            for p in platforms:
                report["summary"]["by_platform"][p] += 1
        elif isinstance(platforms, str):
            report["summary"]["by_platform"][platforms] += 1

        # Module breakdown
        report["modules"][module]["count"] += 1
        report["modules"][module]["statuses"][status] += 1
        report["modules"][module]["testcases"].append({
            "title": entry.get("title"),
            "status": status,
            "format": format_type,
            "rel_path": entry.get("rel_path")
        })

        # Tag analysis
        if isinstance(tags, list):
            for tag in tags:
                report["tags"][tag] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    report["summary"]["by_status"] = dict(report["summary"]["by_status"])
    report["summary"]["by_format"] = dict(report["summary"]["by_format"])
    report["summary"]["by_platform"] = dict(report["summary"]["by_platform"])

    # Process modules
    modules_dict = {}
    for module, data in report["modules"].items():
        modules_dict[module] = {
            "count": data["count"],
            "statuses": dict(data["statuses"]),
            "testcases": data["testcases"]
        }
    report["modules"] = modules_dict

    # Process i18n index if provided
    if i18n_index_data:
        i18n_entries = i18n_index_data.get("entries", [])
        report["i18n"] = {
            "total": len(i18n_entries),
            "by_status": defaultdict(int),
            "by_language_count": defaultdict(int)
        }

        for entry in i18n_entries:
            status = entry.get("status", "unknown")
            lang_codes = entry.get("language_codes", [])

            report["i18n"]["by_status"][status] += 1
            report["i18n"]["by_language_count"][len(lang_codes)] += 1

        report["i18n"]["by_status"] = dict(report["i18n"]["by_status"])
        report["i18n"]["by_language_count"] = dict(report["i18n"]["by_language_count"])

    return report


def format_markdown(report: dict) -> str:
    """Format report as markdown."""
    lines = []

    lines.append("# 测试用例覆盖率报告")
    lines.append(f"\n生成时间：{report['generated_at']}")
    lines.append("")

    # Summary
    summary = report["summary"]
    lines.append("## 总览")
    lines.append("")
    lines.append(f"- **总用例数**: {summary['total_testcases']}")
    lines.append("")

    # By status
    lines.append("### 按状态分布")
    lines.append("")
    lines.append("| 状态 | 数量 |")
    lines.append("|------|------|")
    for status, count in sorted(summary["by_status"].items()):
        lines.append(f"| {status} | {count} |")
    lines.append("")

    # By format
    lines.append("### 按格式分布")
    lines.append("")
    lines.append("| 格式 | 数量 |")
    lines.append("|------|------|")
    for format_type, count in sorted(summary["by_format"].items()):
        lines.append(f"| {format_type} | {count} |")
    lines.append("")

    # By platform
    lines.append("### 按平台分布")
    lines.append("")
    lines.append("| 平台 | 数量 |")
    lines.append("|------|------|")
    for platform, count in sorted(summary["by_platform"].items()):
        lines.append(f"| {platform} | {count} |")
    lines.append("")

    # By module
    lines.append("## 模块覆盖")
    lines.append("")
    lines.append("| 模块 | 用例数 | 状态分布 |")
    lines.append("|------|--------|----------|")
    for module, data in sorted(report["modules"].items()):
        status_str = ", ".join(f"{k}:{v}" for k, v in data["statuses"].items())
        lines.append(f"| {module} | {data['count']} | {status_str} |")
    lines.append("")

    # Tags
    if report["tags"]:
        lines.append("## 标签分布")
        lines.append("")
        lines.append("| 标签 | 使用次数 |")
        lines.append("|------|----------|")
        for tag, count in sorted(report["tags"].items(), key=lambda x: -x[1])[:20]:
            lines.append(f"| {tag} | {count} |")
        lines.append("")

    # i18n
    if report["i18n"]:
        i18n = report["i18n"]
        lines.append("## 多语言覆盖")
        lines.append("")
        lines.append(f"- **总条目数**: {i18n['total']}")
        lines.append("")
        lines.append("### 按状态分布")
        lines.append("")
        lines.append("| 状态 | 数量 |")
        lines.append("|------|------|")
        for status, count in sorted(i18n["by_status"].items()):
            lines.append(f"| {status} | {count} |")
        lines.append("")

    return "\n".join(lines)


def format_html(report: dict) -> str:
    """Format report as HTML."""
    html_lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>测试用例报告</title>",
        "<style>",
        "body { font-family: -apple-system, sans-serif; padding: 20px; }",
        "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background: #f5f5f5; }",
        "h1, h2 { color: #333; }",
        "</style>",
        "</head><body>"
    ]

    summary = report["summary"]
    html_lines.append(f"<h1>测试用例覆盖率报告</h1>")
    html_lines.append(f"<p>生成时间：{report['generated_at']}</p>")

    html_lines.append(f"<h2>总览</h2>")
    html_lines.append(f"<p><strong>总用例数</strong>: {summary['total_testcases']}</p>")

    # By status table
    html_lines.append("<h2>按状态分布</h2>")
    html_lines.append("<table><tr><th>状态</th><th>数量</th></tr>")
    for status, count in sorted(summary["by_status"].items()):
        html_lines.append(f"<tr><td>{status}</td><td>{count}</td></tr>")
    html_lines.append("</table>")

    # By module table
    html_lines.append("<h2>模块覆盖</h2>")
    html_lines.append("<table><tr><th>模块</th><th>用例数</th><th>状态分布</th></tr>")
    for module, data in sorted(report["modules"].items()):
        status_str = ", ".join(f"{k}:{v}" for k, v in data["statuses"].items())
        html_lines.append(f"<tr><td>{module}</td><td>{data['count']}</td><td>{status_str}</td></tr>")
    html_lines.append("</table>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate testcase coverage and statistics report"
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--index",
        default="testcases/testcase-index.json",
        help="Path to testcase index (default: testcases/testcase-index.json)"
    )
    parser.add_argument(
        "--i18n-index",
        default="testcases/i18n-index.json",
        help="Path to i18n index (default: testcases/i18n-index.json)"
    )

    args = parser.parse_args()

    index_data, error = load_index(args.index)
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)

    i18n_index_data, _ = load_index(args.i18n_index)

    report = generate_report(index_data, i18n_index_data)

    if args.format == "json":
        output = json.dumps(report, indent=2, ensure_ascii=False)
    elif args.format == "html":
        output = format_html(report)
    else:
        output = format_markdown(report)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report written to {args.output}")
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
