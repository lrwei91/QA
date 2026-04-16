#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
save_figma_to_wiki.py — Save Figma design data to knowledge base.

Usage:
    python3 save_figma_to_wiki.py <figma_json> --type sources --output knowledge/wiki/sources/
    python3 save_figma_to_wiki.py <figma_json> --type sources --output knowledge/wiki/sources/

This script:
1. Reads Figma API response JSON
2. Extracts page structure, components, states, interactions
3. Generates wiki markdown page
4. Saves to knowledge base
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def extract_page_name(figma_data: dict) -> str:
    """Extract page/frame name from Figma data."""
    nodes = figma_data.get('nodes', {})
    if nodes:
        for node_id, node_data in nodes.items():
            if 'name' in node_data:
                return node_data['name'].replace('/', '-').strip()
    return 'figma-design'


def extract_components(figma_data: dict) -> list:
    """Extract component list from Figma data."""
    components = []
    nodes = figma_data.get('nodes', {})

    for node_id, node_data in nodes.items():
        document = node_data.get('document', {})
        if document:
            # Traverse document tree to find components
            def traverse(node, parent=None):
                if isinstance(node, dict):
                    name = node.get('name', '')
                    node_type = node.get('type', '')
                    if name and node_type:
                        components.append({
                            'name': name,
                            'type': node_type,
                            'parent': parent
                        })
                    for child in node.get('children', []):
                        traverse(child, name)

            traverse(document)

    return components


def extract_states(figma_data: dict) -> list:
    """Extract component states/variants from Figma data."""
    states = []
    # This is a simplified extraction
    # Real implementation would need more detailed Figma API parsing
    return states


def extract_interactions(figma_data: dict) -> list:
    """Extract interaction descriptions from Figma data."""
    interactions = []
    # This is a simplified extraction
    # Real implementation would parse prototype connections
    return interactions


def generate_sources_page(figma_data: dict, page_name: str) -> str:
    """Generate wiki page for sources category."""
    components = extract_components(figma_data)
    states = extract_states(figma_data)
    interactions = extract_interactions(figma_data)

    lines = [
        f"# {page_name} - 设计稿",
        "",
        "## 来源信息",
        f"- 来源类型：Figma 设计稿",
        f"- 提取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 页面结构",
        "",
        "页面名称：" + page_name,
        "",
        "## 组件列表",
        "",
    ]

    if components:
        lines.append("| 组件名称 | 类型 | 父级 |")
        lines.append("|----------|------|------|")
        for comp in components[:50]:  # Limit to 50 components
            lines.append(f"| {comp['name']} | {comp['type']} | {comp['parent'] or '-'} |")
        if len(components) > 50:
            lines.append(f"\n*还有 {len(components) - 50} 个组件...*")
    else:
        lines.append("暂无组件数据")

    lines.extend([
        "",
        "## 组件状态",
        "",
    ])

    if states:
        for state in states:
            lines.append(f"- **{state['component']}**: {', '.join(state['variants'])}")
    else:
        lines.append("暂无状态数据")

    lines.extend([
        "",
        "## 交互说明",
        "",
    ])

    if interactions:
        for interaction in interactions:
            lines.append(f"- **{interaction['source']}** {interaction['event']} → {interaction['action']}")
    else:
        lines.append("暂无交互数据")

    lines.extend([
        "",
        "---",
        "",
        "**相关文件**：",
        f"- 设计稿页面：`{page_name}`",
        "",
        f"**创建时间**：{datetime.now().strftime('%Y-%m-%d')}",
    ])

    return '\n'.join(lines)


def generate_entities_page(figma_data: dict, page_name: str) -> str:
    """Generate wiki page for entities category (UI component spec)."""
    components = extract_components(figma_data)

    # Group components by type
    by_type = {}
    for comp in components:
        t = comp['type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(comp['name'])

    lines = [
        f"# UI 组件规范 - {page_name}",
        "",
        "## 来源信息",
        f"- 来源类型：Figma 设计稿",
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
        f"- 设计稿来源：[[{page_name}-设计稿]]",
        "",
        f"**创建时间**：{datetime.now().strftime('%Y-%m-%d')}",
    ])

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Save Figma data to knowledge base')
    parser.add_argument('input', type=Path, help='Input Figma JSON file')
    parser.add_argument('--type', '-t', choices=['sources', 'entities'], required=True,
                        help='Output type: sources or entities')
    parser.add_argument('--output', '-o', type=Path, required=True,
                        help='Output directory')
    parser.add_argument('--name', '-n', type=str,
                        help='Page name (default: extract from Figma data)')

    args = parser.parse_args()

    # Load Figma data
    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        return 1

    try:
        figma_data = json.loads(args.input.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        return 1

    # Determine page name
    page_name = args.name or extract_page_name(figma_data)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Generate content based on type
    if args.type == 'sources':
        content = generate_sources_page(figma_data, page_name)
        output_file = args.output / f"{page_name}-设计稿.md"
    else:  # entities
        content = generate_entities_page(figma_data, page_name)
        output_file = args.output / f"UI 组件规范-{page_name}.md"

    # Write output
    output_file.write_text(content, encoding='utf-8')

    print(f"Saved: {output_file}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
