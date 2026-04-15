#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
sync_testcase_snapshot.py — Sync testcase snapshot to theme page.

Usage:
    python3 sync_testcase_snapshot.py outputs/generated/运营活动/复充返利活动.xlsx
    python3 sync_testcase_snapshot.py --all  # Sync all excel files
    python3 sync_testcase_snapshot.py --config submodule-config.json  # Use submodule config

This script:
1. Reads testcase data from Excel file
2. Saves/updates snapshot
3. Updates theme page with latest test point summary

Submodule Support:
    Theme pages can be organized in subfolders:
    knowledge/wiki/topics/运营活动/充值优惠/复充返利活动.md

    Configure submodules via:
    - --submodule argument
    - submodule-config.json file
    - Module index file
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add script directory to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from snapshot_testcase import (
    extract_testcases_from_xlsx,
    build_test_point_summary,
    save_snapshot,
    get_latest_snapshot,
)


# Submodule configuration file path
SUBMODULE_CONFIG_FILE = Path('knowledge/wiki/topics/submodule-config.json')


def update_theme_page(theme_path: Path, snapshot: dict, snapshot_file: Path) -> None:
    """Update theme page with snapshot data.

    Args:
        theme_path: Path to theme page markdown file
        snapshot: Snapshot data dict
        snapshot_file: Path to snapshot JSON file
    """
    # Build test point summary section
    summary_lines = ["## 测试点摘要", ""]

    # Add snapshot reference - use a fixed relative path pattern
    # Snapshot is at: outputs/snapshots/<module>/<title>/<timestamp>.json
    # Theme page is at: knowledge/wiki/topics/<title>.md
    # Relative path from theme page: ../../../outputs/snapshots/<module>/<title>/<timestamp>.json
    module = snapshot['metadata']['module']
    title = snapshot['metadata']['title']
    snapshot_name = snapshot_file.name
    rel_path = f"../../../outputs/snapshots/{module}/{title}/{snapshot_name}"

    timestamp = snapshot['snapshot_at'][:19].replace('T', ' ')
    summary_lines.append(f"> 数据来源：快照文件 `{rel_path}`")
    summary_lines.append(f"> 最后同步时间：{timestamp}")
    summary_lines.append("")

    # Server side test points
    server_points = snapshot['test_point_summary'].get('server_side', [])
    if server_points:
        summary_lines.append("**账服用例**：")
        for point in server_points:
            summary_lines.append(f"- {point}")
        summary_lines.append("")

    # Client side test points
    client_points = snapshot['test_point_summary'].get('client_side', [])
    if client_points:
        summary_lines.append("**客户端用例**：")
        for point in client_points:
            summary_lines.append(f"- {point}")
        summary_lines.append("")

    summary_content = "\n".join(summary_lines)

    # Read existing theme page
    if not theme_path.exists():
        # Create new theme page
        module = snapshot['metadata']['module']
        title = snapshot['metadata']['title']

        theme_content = f"""# {title}

## 领域知识
参考：[[{module}]]

## 已生成测试用例

| 文件名 | 模块 | 用例数 | 平台 | 生成时间 |
|--------|------|--------|------|----------|
| {title}.xlsx | {module} | {snapshot['metadata']['total_cases']} 条 | {', '.join(snapshot['metadata']['platform_scope'])} | {datetime.now().strftime('%Y-%m-%d')} |

{summary_content}
## 相关文件

- 领域知识：[[{module}]]
- 测试用例：`outputs/generated/{module}/{title}.xlsx`
- 快照文件：`{rel_path}`
- 模块索引：`engine/references/index-rules/module-index.json`

---

**页面信息**：
- 创建时间：{datetime.now().strftime('%Y-%m-%d')}
- 最后更新：{datetime.now().strftime('%Y-%m-%d')}
- 状态：active
"""
    else:
        # Update existing theme page
        content = theme_path.read_text(encoding='utf-8')

        # Find and replace test point summary section
        import re

        # Pattern to match "## 测试点摘要" section until next "##" or end
        pattern = r'## 测试点摘要\n+.*?(?=\n## |\Z)'
        replacement = summary_content

        # If section exists, replace it
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # If section doesn't exist, add it before "## 相关文件" or at end
            if "## 相关文件" in content:
                content = content.replace("## 相关文件", f"{summary_content}\n## 相关文件")
            else:
                content = content.rstrip() + "\n\n" + summary_content

        theme_content = content

    # Write theme page
    theme_path.parent.mkdir(parents=True, exist_ok=True)
    theme_path.write_text(theme_content, encoding='utf-8')


def check_submodule_config_and提示 (title: str, module: str) -> Optional[str]:
    """Check if submodule config exists and return hint if not configured.

    Args:
        title: Test case title
        module: Module name

    Returns:
        Hint message if not configured, None otherwise
    """
    config = load_submodule_config()
    module_config = config.get(module, {})

    if title in module_config:
        # Already configured
        return None

    # Not configured - return hint
    return f"提示：'{module}/{title}' 未配置子文件夹分类，建议添加到 submodule-config.json"


def load_submodule_config() -> dict:
    """Load submodule configuration from JSON file.

    Config format:
    {
        "运营活动": {
            "复充返利活动": "充值优惠",
            "幸运卡片": "游戏优惠",
            "锦标赛": "锦标赛"
        }
    }

    Returns:
        dict: {module: {title: submodule_path}}
    """
    if not SUBMODULE_CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(SUBMODULE_CONFIG_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def get_theme_path_with_submodule(title: str, module: str, submodule_overrides: dict = None) -> Path:
    """Determine theme page path with optional submodule support.

    Args:
        title: Test case title (e.g., "复充返利活动")
        module: Module name (e.g., "运营活动")
        submodule_overrides: Optional dict {title: submodule_path}

    Returns:
        Path: Theme page path (e.g., knowledge/wiki/topics/运营活动/充值优惠/复充返利活动.md)
    """
    # Load config and merge with overrides
    config = load_submodule_config()
    if submodule_overrides:
        if module not in config:
            config[module] = {}
        config[module].update(submodule_overrides)

    # Check if title has a configured submodule
    module_config = config.get(module, {})
    submodule = module_config.get(title)

    if submodule:
        # Theme page in subfolder
        return Path('knowledge/wiki/topics') / module / submodule / f"{title}.md"
    else:
        # Theme page in root topics folder
        return Path('knowledge/wiki/topics') / f"{title}.md"


def sync_excel_to_snapshot(
    xlsx_path: Path,
    snapshot_dir: Path = None,
    submodule: str = None
) -> tuple[Path, Path]:
    """Sync Excel file to snapshot and theme page.

    Args:
        xlsx_path: Path to Excel file
        snapshot_dir: Optional snapshot directory override
        submodule: Optional submodule path (e.g., "充值优惠")

    Returns:
        tuple: (snapshot_file, theme_page)
    """
    # Determine snapshot directory
    if snapshot_dir is None:
        module = xlsx_path.parent.name
        snapshot_dir = Path('outputs/snapshots') / module / xlsx_path.stem

    # Save snapshot
    snapshot_file = save_snapshot(xlsx_path, snapshot_dir)

    # Load snapshot data
    snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))

    # Determine theme page path with submodule support
    title = snapshot['metadata']['title']
    module = snapshot['metadata']['module']

    # Build submodule overrides if provided
    submodule_overrides = {}
    if submodule:
        submodule_overrides[title] = submodule

    theme_path = get_theme_path_with_submodule(title, module, submodule_overrides)

    # Update theme page
    update_theme_page(theme_path, snapshot, snapshot_file)

    return snapshot_file, theme_path


def main() -> int:
    parser = argparse.ArgumentParser(description='Sync testcase snapshot to theme page')
    parser.add_argument('xlsx_file', type=Path, nargs='?', help='Path to the Excel file')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Sync all Excel files in outputs/generated/')
    parser.add_argument('--output-dir', '-o', type=Path,
                        help='Override snapshot output directory')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Show what would be done without actually writing')
    parser.add_argument('--submodule', '-s', type=str,
                        help='Submodule path for theme page (e.g., "充值优惠")')
    parser.add_argument('--config', '-c', type=Path,
                        help='Path to submodule config JSON file')

    args = parser.parse_args()

    # Update config file path if provided
    if args.config:
        global SUBMODULE_CONFIG_FILE
        SUBMODULE_CONFIG_FILE = args.config

    # Collect files to sync
    if args.all:
        # Find all xlsx files in outputs/generated/
        generated_dir = Path('outputs/generated')
        if not generated_dir.exists():
            print("ERROR: outputs/generated/ directory not found", file=sys.stderr)
            return 1

        xlsx_files = list(generated_dir.rglob('*.xlsx'))
        if not xlsx_files:
            print("No Excel files found in outputs/generated/")
            return 0
    elif args.xlsx_file:
        if not args.xlsx_file.exists():
            print(f"ERROR: File not found: {args.xlsx_file}", file=sys.stderr)
            return 1
        xlsx_files = [args.xlsx_file]
    else:
        print("ERROR: Provide an Excel file path or use --all", file=sys.stderr)
        return 1

    # Sync files
    synced = []
    for xlsx_path in xlsx_files:
        if args.dry_run:
            module = xlsx_path.parent.name
            title = xlsx_path.stem

            # Determine theme path with submodule
            theme_path = get_theme_path_with_submodule(
                title, module, {title: args.submodule} if args.submodule else None
            )

            snapshot_dir = Path('outputs/snapshots') / module / title
            print(f"Would sync: {xlsx_path}")
            print(f"  Snapshot: {snapshot_dir}/<timestamp>.json")
            print(f"  Theme page: {theme_path}")
            print()
        else:
            try:
                snapshot_file, theme_page = sync_excel_to_snapshot(
                    xlsx_path, args.output_dir, args.submodule
                )
                synced.append((xlsx_path, snapshot_file, theme_page))
                print(f"Synced: {xlsx_path.name}")
                print(f"  Snapshot: {snapshot_file}")
                print(f"  Theme page: {theme_page}")
                print()
            except Exception as e:
                print(f"ERROR syncing {xlsx_path}: {e}", file=sys.stderr)
                continue

    if synced:
        print(f"Successfully synced {len(synced)} file(s)")

        # Check for submodule config hints
        print("\n子文件夹配置检查：")
        config_hints = []
        for xlsx_path, _, _ in synced:
            module = xlsx_path.parent.name
            title = xlsx_path.stem
            hint = check_submodule_config_and提示 (title, module)
            if hint:
                config_hints.append(hint)

        if config_hints:
            print("⚠️  以下用例未配置子文件夹分类：")
            for hint in config_hints:
                print(f"  - {hint}")
            print("\n建议编辑 knowledge/wiki/topics/submodule-config.json 添加分类配置")
        else:
            print("✓ 所有用例已配置子文件夹分类")
    else:
        print("No files synced")

    return 0


if __name__ == '__main__':
    sys.exit(main())
