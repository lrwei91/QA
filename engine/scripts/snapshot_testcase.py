#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
snapshot_testcase.py — Extract testcase data from xlsx and save as snapshot.

Usage:
    python3 snapshot_testcase.py outputs/generated/运营活动/复充返利活动.xlsx
    python3 snapshot_testcase.py outputs/generated/运营活动/复充返利活动.xlsx --output-dir outputs/snapshots/复充返利活动/

This script reads testcase data from an Excel file and saves it as a JSON snapshot.
The snapshot can be used for:
- Theme page test point summary generation
- Version tracking and diff comparison
- Knowledge base query enrichment
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook

# Column mapping for testcase template (starting from row 8)
# 序号 | 平台 | 模块 | 功能点 | 前置条件 | 操作步骤 | 预期结果 | 测试结果 | 备注
COLUMN_MAP = {
    'id': 1,      # A: 序号
    'platform': 2,  # B: 平台
    'module': 3,    # C: 模块
    'function': 4,  # D: 功能点
    'precondition': 5,  # E: 前置条件（测试点）
    'steps': 6,         # F: 操作步骤
    'expected': 7,      # G: 预期结果
    'result': 8,        # H: 测试结果
    'remark': 9,        # I: 备注
}

HEADER_ROW = 7  # Data starts from row 8 (1-indexed)
METADATA_ROW = 2  # Metadata starts from row 2


def extract_metadata(ws, max_row: int = 7) -> dict:
    """Extract metadata from the top section of the worksheet.

    Metadata cells:
    - B2: 测试平台
    - F2: 测试日期
    - B3: 系统&版本
    - F3: 最后更新
    - B4: 文档编写人
    - F4: 文档测试人
    - B5: 策划负责人
    - F5: 审阅人员
    - B6: 参考档
    """
    metadata_map = {
        '测试平台': (2, 2),  # B2
        '测试日期': (2, 6),  # F2
        '系统&版本': (3, 2),  # B3
        '最后更新': (3, 6),  # F3
        '文档编写人': (4, 2),  # B4
        '文档测试人': (4, 6),  # F4
        '策划负责人': (5, 2),  # B5
        '审阅人员': (5, 6),  # F5
        '参考档': (6, 2),    # B6
    }

    metadata = {}
    for key, (row, col) in metadata_map.items():
        if row <= max_row:
            cell = ws.cell(row=row, column=col)
            value = cell.value
            if value:
                metadata[key] = str(value).strip()

    return metadata


def extract_testcases_from_xlsx(xlsx_path: Path) -> tuple[list[dict], dict]:
    """读取 Excel 文件，提取测试用例数据和元数据。

    Returns:
        tuple: (testcases list, metadata dict)
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=False)
    ws = wb.active

    # Extract metadata from top section
    metadata = extract_metadata(ws, max_row=HEADER_ROW)

    # Extract testcase data starting from row 8
    testcases = []
    for row in range(HEADER_ROW + 1, ws.max_row + 1):
        # Skip empty rows
        first_cell = ws.cell(row, COLUMN_MAP['id'])
        if not first_cell.value:
            continue

        testcase = {
            'id': int(first_cell.value) if first_cell.value else len(testcases) + 1,
            'platform': str(ws.cell(row, COLUMN_MAP['platform']).value or '').strip(),
            'module': str(ws.cell(row, COLUMN_MAP['module']).value or '').strip(),
            'function': str(ws.cell(row, COLUMN_MAP['function']).value or '').strip(),
            'precondition': str(ws.cell(row, COLUMN_MAP['precondition']).value or '').strip(),
            'steps': str(ws.cell(row, COLUMN_MAP['steps']).value or '').strip(),
            'expected': str(ws.cell(row, COLUMN_MAP['expected']).value or '').strip(),
            'result': str(ws.cell(row, COLUMN_MAP['result']).value or '').strip(),
            'remark': str(ws.cell(row, COLUMN_MAP['remark']).value or '').strip(),
        }
        testcases.append(testcase)

    wb.close()
    return testcases, metadata


def build_test_point_summary(testcases: list[dict]) -> dict:
    """从测试用例生成测试点摘要。

    Groups test points by platform (server/client) and function.
    """
    summary = {
        'server_side': [],
        'client_side': [],
        'all_points': []
    }

    seen_points = set()

    for tc in testcases:
        # Use function point or module as the test point
        point = tc['function'] or tc['module'] or f"用例 #{tc['id']}"

        # Skip duplicates
        point_key = f"{tc['platform']}:{point}"
        if point_key in seen_points:
            continue
        seen_points.add(point_key)

        # Build test point entry
        point_entry = {
            'id': tc['id'],
            'point': point,
            'module': tc['module'],
        }

        if tc['platform'] == '账服':
            summary['server_side'].append(point)
        elif tc['platform'] == '客户端':
            summary['client_side'].append(point)

        summary['all_points'].append(point_entry)

    return summary


def save_snapshot(xlsx_path: Path, output_dir: Path, dry_run: bool = False) -> Path:
    """保存快照文件。

    Args:
        xlsx_path: Path to the Excel file
        output_dir: Directory to save the snapshot
        dry_run: If True, only print info without writing

    Returns:
        Path to the saved snapshot file
    """
    # Extract data
    testcases, metadata = extract_testcases_from_xlsx(xlsx_path)

    # Build summary
    test_point_summary = build_test_point_summary(testcases)

    # Build snapshot structure
    timestamp = datetime.now().astimezone().isoformat()
    snapshot = {
        'version': 1,
        'snapshot_at': timestamp,
        'source_file': str(xlsx_path),
        'metadata': {
            'title': xlsx_path.stem,
            'module': xlsx_path.parent.name,
            'platform_scope': list(set(tc['platform'] for tc in testcases if tc['platform'])),
            'total_cases': len(testcases),
            'extra_metadata': metadata,
        },
        'testcases': testcases,
        'test_point_summary': test_point_summary,
        'statistics': {
            'server_side_count': len(test_point_summary['server_side']),
            'client_side_count': len(test_point_summary['client_side']),
        }
    }

    if dry_run:
        ts = timestamp.replace(':', '-')
        print(f"Would save snapshot to: {output_dir / f'{ts}.json'}")
        print(f"Total testcases: {len(testcases)}")
        print(f"Server side: {snapshot['statistics']['server_side_count']}")
        print(f"Client side: {snapshot['statistics']['client_side_count']}")
        return None

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save snapshot with timestamp filename
    snapshot_file = output_dir / f"{timestamp.replace(':', '-')}.json"
    snapshot_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')

    return snapshot_file


def get_latest_snapshot(snapshot_dir: Path) -> Optional[Path]:
    """Get the latest snapshot file from the snapshot directory.

    Returns:
        Path to the latest snapshot file, or None if no snapshots exist
    """
    if not snapshot_dir.exists():
        return None

    snapshot_files = sorted(snapshot_dir.glob('*.json'), reverse=True)
    return snapshot_files[0] if snapshot_files else None


def main() -> int:
    parser = argparse.ArgumentParser(description='Extract testcase data from xlsx and save as snapshot')
    parser.add_argument('xlsx_file', type=Path, help='Path to the Excel file')
    parser.add_argument('--output-dir', '-o', type=Path,
                        default=Path('outputs/snapshots'),
                        help='Directory to save snapshots (default: outputs/snapshots/<module>/)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Show what would be done without actually writing')
    parser.add_argument('--show', '-s', action='store_true',
                        help='Show snapshot content instead of saving')

    args = parser.parse_args()

    # Validate input file
    if not args.xlsx_file.exists():
        print(f"ERROR: File not found: {args.xlsx_file}", file=sys.stderr)
        return 1

    if not args.xlsx_file.suffix.lower() == '.xlsx':
        print(f"ERROR: Not an Excel file: {args.xlsx_file}", file=sys.stderr)
        return 1

    # Determine output directory
    if args.output_dir == Path('outputs/snapshots'):
        # Default: create subdirectory based on module and filename
        module = args.xlsx_file.parent.name
        snapshot_dir = args.output_dir / module / args.xlsx_file.stem
    else:
        snapshot_dir = args.output_dir

    # Show mode: display what would be extracted
    if args.show:
        testcases, metadata = extract_testcases_from_xlsx(args.xlsx_file)
        summary = build_test_point_summary(testcases)

        print(f"=== {args.xlsx_file.name} ===")
        print(f"Module: {args.xlsx_file.parent.name}")
        print(f"Total testcases: {len(testcases)}")
        print(f"Server side: {len(summary['server_side'])}")
        print(f"Client side: {len(summary['client_side'])}")
        print()
        print("Server side test points:")
        for point in summary['server_side'][:10]:
            print(f"  - {point}")
        if len(summary['server_side']) > 10:
            print(f"  ... and {len(summary['server_side']) - 10} more")
        print()
        print("Client side test points:")
        for point in summary['client_side'][:10]:
            print(f"  - {point}")
        if len(summary['client_side']) > 10:
            print(f"  ... and {len(summary['client_side']) - 10} more")
        return 0

    # Save snapshot
    snapshot_file = save_snapshot(args.xlsx_file, snapshot_dir, dry_run=args.dry_run)

    if snapshot_file:
        print(f"Snapshot saved: {snapshot_file}")
        print(f"Total testcases: {len(extract_testcases_from_xlsx(args.xlsx_file)[0])}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
