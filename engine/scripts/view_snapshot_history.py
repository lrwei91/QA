#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
view_snapshot_history.py — View testcase snapshot history and compare versions.

Usage:
    python3 view_snapshot_history.py outputs/generated/运营活动/复充返利活动.xlsx
    python3 view_snapshot_history.py --module 运营活动
    python3 view_snapshot_history.py --all  # List all snapshots

This script:
1. Lists all snapshots for a given testcase or module
2. Shows snapshot timeline with metadata
3. Compares two snapshots if specified
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List


SNAPSHOTS_ROOT = Path('outputs/snapshots')


def find_snapshots_for_file(xlsx_path: Path) -> List[Path]:
    """Find all snapshots for a given Excel file.

    Args:
        xlsx_path: Path to Excel file

    Returns:
        List of snapshot JSON file paths, sorted by timestamp
    """
    # Extract module and title from path
    # e.g., outputs/generated/运营活动/复充返利活动.xlsx
    if not xlsx_path.exists():
        return []

    module = xlsx_path.parent.name
    title = xlsx_path.stem

    snapshot_dir = SNAPSHOTS_ROOT / module / title
    if not snapshot_dir.exists():
        return []

    snapshots = sorted(snapshot_dir.glob('*.json'))
    return snapshots


def find_snapshots_by_module(module: str) -> dict:
    """Find all snapshots for a given module.

    Args:
        module: Module name

    Returns:
        Dict of {title: [snapshot_paths]}
    """
    module_dir = SNAPSHOTS_ROOT / module
    if not module_dir.exists():
        return {}

    result = {}
    for title_dir in module_dir.iterdir():
        if title_dir.is_dir():
            snapshots = sorted(title_dir.glob('*.json'))
            if snapshots:
                result[title_dir.name] = snapshots

    return result


def load_snapshot(snapshot_path: Path) -> dict:
    """Load snapshot data from JSON file."""
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_snapshot_info(snapshot: dict, snapshot_path: Path) -> str:
    """Format snapshot metadata for display."""
    metadata = snapshot.get('metadata', {})
    snapshot_at = snapshot.get('snapshot_at', 'Unknown')

    # Parse and format timestamp
    try:
        # Handle ISO format with timezone
        ts = snapshot_at.replace('T', ' ').replace('+08:00', '').replace('+0800', '')
        ts = ts[:19]  # Trim microseconds
        dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        formatted_time = dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        formatted_time = snapshot_at[:19]

    lines = [
        f"  📄 {snapshot_path.name}",
        f"     时间：{formatted_time}",
        f"     用例数：{metadata.get('total_cases', 'N/A')} 条",
        f"     平台：{', '.join(metadata.get('platform_scope', []))}",
    ]

    # Add test point summary preview
    summary = snapshot.get('test_point_summary', {})
    server_count = len(summary.get('server_side', []))
    client_count = len(summary.get('client_side', []))
    lines.append(f"     测试点：账服{server_count}项，客户端{client_count}项")

    return '\n'.join(lines)


def compare_snapshots(snapshot1_path: Path, snapshot2_path: Path) -> str:
    """Compare two snapshots and return diff summary.

    Args:
        snapshot1_path: Path to first snapshot
        snapshot2_path: Path to second snapshot

    Returns:
        Formatted comparison result
    """
    s1 = load_snapshot(snapshot1_path)
    s2 = load_snapshot(snapshot2_path)

    m1 = s1.get('metadata', {})
    m2 = s2.get('metadata', {})

    lines = [
        "\n📊 快照对比结果",
        f"  快照 1: {snapshot1_path.name}",
        f"  快照 2: {snapshot2_path.name}",
        "",
        "  【元数据对比】",
        f"    用例数变化：{m1.get('total_cases', 0)} → {m2.get('total_cases', 0)}",
    ]

    # Compare test point summary
    sum1 = s1.get('test_point_summary', {})
    sum2 = s2.get('test_point_summary', {})

    server1 = set(sum1.get('server_side', []))
    server2 = set(sum2.get('server_side', []))
    client1 = set(sum1.get('client_side', []))
    client2 = set(sum2.get('client_side', []))

    server_added = server2 - server1
    server_removed = server1 - server2
    client_added = client2 - client1
    client_removed = client1 - client2

    lines.append("  【账服测试点变化】")
    if server_added:
        lines.append(f"    + 新增：{len(server_added)} 项")
        for p in sorted(server_added)[:5]:  # Show first 5
            lines.append(f"      • {p}")
        if len(server_added) > 5:
            lines.append(f"      ... 还有 {len(server_added) - 5} 项")
    if server_removed:
        lines.append(f"    - 删除：{len(server_removed)} 项")
        for p in sorted(server_removed)[:5]:
            lines.append(f"      • {p}")
        if len(server_removed) > 5:
            lines.append(f"      ... 还有 {len(server_removed) - 5} 项")
    if not server_added and not server_removed:
        lines.append("    无变化")

    lines.append("  【客户端测试点变化】")
    if client_added:
        lines.append(f"    + 新增：{len(client_added)} 项")
        for p in sorted(client_added)[:5]:
            lines.append(f"      • {p}")
        if len(client_added) > 5:
            lines.append(f"      ... 还有 {len(client_added) - 5} 项")
    if client_removed:
        lines.append(f"    - 删除：{len(client_removed)} 项")
        for p in sorted(client_removed)[:5]:
            lines.append(f"      • {p}")
        if len(client_removed) > 5:
            lines.append(f"      ... 还有 {len(client_removed) - 5} 项")
    if not client_added and not client_removed:
        lines.append("    无变化")

    return '\n'.join(lines)


def list_snapshots(xlsx_path: Optional[Path] = None, module: Optional[str] = None) -> None:
    """List snapshots for a file or module.

    Args:
        xlsx_path: Path to Excel file (optional)
        module: Module name (optional)
    """
    if xlsx_path:
        snapshots = find_snapshots_for_file(xlsx_path)
        if not snapshots:
            print(f"未找到快照：{xlsx_path}")
            return

        print(f"\n📁 {xlsx_path.parent.name}/{xlsx_path.name} 的快照历史")
        print("=" * 60)

        for i, snapshot_path in enumerate(snapshots, 1):
            snapshot = load_snapshot(snapshot_path)
            print(f"\n[{i}/{len(snapshots)}]")
            print(format_snapshot_info(snapshot, snapshot_path))

    elif module:
        snapshots_by_title = find_snapshots_by_module(module)
        if not snapshots_by_title:
            print(f"未找到模块 '{module}' 的快照")
            return

        print(f"\n📁 模块 '{module}' 的快照历史")
        print("=" * 60)

        for title, snapshots in sorted(snapshots_by_title.items()):
            print(f"\n【{title}】({len(snapshots)} 个快照)")
            for snapshot_path in snapshots:
                snapshot = load_snapshot(snapshot_path)
                ts = snapshot.get('snapshot_at', '')[:19].replace('T', ' ')
                cases = snapshot.get('metadata', {}).get('total_cases', 0)
                print(f"  • {ts} - {cases} 条用例 ({snapshot_path.name})")
    else:
        # List all modules with snapshots
        if not SNAPSHOTS_ROOT.exists():
            print("快照目录不存在")
            return

        print(f"\n📁 所有模块的快照")
        print("=" * 60)

        total_snapshots = 0
        for module_dir in sorted(SNAPSHOTS_ROOT.iterdir()):
            if module_dir.is_dir():
                count = sum(1 for p in module_dir.rglob('*.json'))
                if count > 0:
                    print(f"\n【{module_dir.name}】({count} 个快照)")
                    for title_dir in sorted(module_dir.iterdir()):
                        if title_dir.is_dir():
                            title_snapshots = list(title_dir.glob('*.json'))
                            if title_snapshots:
                                print(f"  • {title_dir.name}: {len(title_snapshots)} 个")
                    total_snapshots += count

        print(f"\n总计：{total_snapshots} 个快照")


def main():
    parser = argparse.ArgumentParser(description='View testcase snapshot history')
    parser.add_argument('xlsx_path', nargs='?', type=Path,
                        help='Path to Excel file')
    parser.add_argument('--module', '-m', type=str,
                        help='Module name to list snapshots')
    parser.add_argument('--all', '-a', action='store_true',
                        help='List all snapshots')
    parser.add_argument('--compare', '-c', nargs=2, type=Path,
                        metavar=('SNAPSHOT1', 'SNAPSHOT2'),
                        help='Compare two snapshots')

    args = parser.parse_args()

    if args.compare:
        s1, s2 = args.compare
        if not s1.exists():
            print(f"快照不存在：{s1}")
            return
        if not s2.exists():
            print(f"快照不存在：{s2}")
            return
        print(compare_snapshots(s1, s2))
    elif args.all:
        list_snapshots()
    elif args.module:
        list_snapshots(module=args.module)
    elif args.xlsx_path:
        list_snapshots(xlsx_path=args.xlsx_path)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
