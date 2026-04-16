#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
save_axure_to_wiki.py — Save Axure HTML parse data to knowledge base.

Usage:
    python3 save_axure_to_wiki.py <axure_json> --type sources --output knowledge/wiki/sources/
    python3 save_axure_to_wiki.py <axure_json> --type sources --output knowledge/wiki/sources/

This script:
1. Reads Axure HTML parser JSON output
2. Extracts pages, components, annotations, interactions
3. Generates wiki markdown page
4. Saves to knowledge base
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def extract_page_name(axure_data: dict) -> str:
    """Extract main page name from Axure data."""
    pages = axure_data.get('pages', [])
    if pages:
        return pages[0].get('name', 'axure-page').replace('/', '-').strip()
    return 'axure-export'


def generate_sources_page(axure_data: dict, page_name: str) -> str:
    """Generate wiki page for sources category."""
    pages = axure_data.get('pages', [])
    components = axure_data.get('components', [])
    annotations = axure_data.get('annotations', [])
    summary = axure_data.get('summary', {})

    lines = [
        f"# {page_name} - Axure 原型",
        "",
        "## 来源信息",
        f"- 来源类型：Axure RP 导出 HTML",
        f"- 提取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 页面结构",
        "",
    ]

    if pages:
        lines.append("| 页面名称 | ID |")
        lines.append("|----------|-----|")
        for page in pages[:20]:  # Limit to 20 pages
            lines.append(f"| {page.get('name', 'Unknown')} | {page.get('id', '-')} |")
        if len(pages) > 20:
            lines.append(f"\n*还有 {len(pages) - 20} 个页面...*")
    else:
        lines.append("暂无页面数据")

    lines.extend([
        "",
        "## 元件列表",
        "",
    ])

    if components:
        lines.append("| 元件名称 | 类型 | 所属页面 |")
        lines.append("|----------|------|----------|")
        for comp in components[:50]:  # Limit to 50 components
            lines.append(f"| {comp.get('name', '-')} | {comp.get('type', '-')} | {comp.get('parent', '-')} |")
        if len(components) > 50:
            lines.append(f"\n*还有 {len(components) - 50} 个元件...*")
    else:
        lines.append("暂无元件数据")

    lines.extend([
        "",
        "## 注释说明",
        "",
    ])

    if annotations:
        for ann in annotations[:30]:  # Limit to 30 annotations
            page = ann.get('page', 'Unknown')
            content = ann.get('content', 'No content')
            lines.append(f"- **{page}**: {content}")
        if len(annotations) > 30:
            lines.append(f"\n*还有 {len(annotations) - 30} 条注释...*")
    else:
        lines.append("暂无注释数据")

    lines.extend([
        "",
        "## 交互说明",
        "",
    ])
    lines.append("暂无交互数据（需要从 Axure HTML 中提取）")

    lines.extend([
        "",
        "## 统计信息",
        "",
        f"- 页面数量：{summary.get('page_count', 0)}",
        f"- 元件数量：{summary.get('component_count', 0)}",
        f"- 注释数量：{summary.get('annotation_count', 0)}",
        "",
        "---",
        "",
        "**相关文件**：",
        f"- 原始文件：`{axure_data.get('file', 'unknown')}`",
        "",
        f"**创建时间**：{datetime.now().strftime('%Y-%m-%d')}",
    ])

    return '\n'.join(lines)


def generate_entities_page(axure_data: dict, page_name: str) -> str:
    """Generate wiki page for entities category (UI component spec)."""
    components = axure_data.get('components', [])

    # Group components by type
    by_type = {}
    for comp in components:
        t = comp.get('type', 'Unknown')
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(comp.get('name', 'Unknown'))

    lines = [
        f"# UI 组件规范 - {page_name}",
        "",
        "## 来源信息",
        f"- 来源类型：Axure RP 导出 HTML",
        f"- 提取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 组件分类",
        "",
    ]

    if by_type:
        for comp_type, names in sorted(by_type.items()):
            lines.append(f"### {comp_type}")
            lines.append("")
            for name in names[:20]:  # Limit per category
                lines.append(f"- {name}")
            if len(names) > 20:
                lines.append(f"\n*还有 {len(names) - 20} 个...*")
            lines.append("")
    else:
        lines.append("暂无组件数据")

    lines.extend([
        "",
        "---",
        "",
        "**相关页面**：",
        f"- 原型来源：[[{page_name}-Axure 原型]]",
        "",
        f"**创建时间**：{datetime.now().strftime('%Y-%m-%d')}",
    ])

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Save Axure data to knowledge base')
    parser.add_argument('input', type=Path, help='Input Axure JSON file')
    parser.add_argument('--type', '-t', choices=['sources', 'entities'], required=True,
                        help='Output type: sources or entities')
    parser.add_argument('--output', '-o', type=Path, required=True,
                        help='Output directory')
    parser.add_argument('--name', '-n', type=str,
                        help='Page name (default: extract from Axure data)')

    args = parser.parse_args()

    # Load Axure data
    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        return 1

    try:
        axure_data = json.loads(args.input.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        return 1

    # Determine page name
    page_name = args.name or extract_page_name(axure_data)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Generate content based on type
    if args.type == 'sources':
        content = generate_sources_page(axure_data, page_name)
        output_file = args.output / f"{page_name}-Axure 原型.md"
    else:  # entities
        content = generate_entities_page(axure_data, page_name)
        output_file = args.output / f"UI 组件规范-{page_name}.md"

    # Write output
    output_file.write_text(content, encoding='utf-8')

    print(f"Saved: {output_file}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
