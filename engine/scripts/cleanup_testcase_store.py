#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
cleanup_testcase_store.py - Clean up orphaned testcase files and expired indexes.

Usage:
    python3 cleanup_testcase_store.py [--dry-run] [--expired-days 90]

This script removes:
- Testcase files referenced in index but missing from disk
- Index entries pointing to non-existent files
- Old generated files (configurable, default 90 days)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_index(index_path: str) -> tuple:
    """Load index JSON file."""
    if not os.path.exists(index_path):
        return None, None

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {index_path}: {e}"
    except Exception as e:
        return None, f"Error reading {index_path}: {e}"


def save_index(index_path: str, data: dict) -> tuple:
    """Save index JSON file."""
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, None
    except Exception as e:
        return False, f"Error writing {index_path}: {e}"


def get_file_mtime(file_path: str) -> datetime:
    """Get file modification time."""
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime)
    except OSError:
        return None


def cleanup_orphaned_entries(index_data: dict, base_dir: str, dry_run: bool = False) -> tuple:
    """Remove index entries for files that no longer exist."""
    testcases = index_data.get("testcases", [])
    original_count = len(testcases)
    removed = []

    valid_testcases = []
    for entry in testcases:
        rel_path = entry.get("rel_path", "")
        if not rel_path:
            removed.append({"reason": "missing rel_path", "entry": entry})
            continue

        # Try both absolute and relative paths
        abs_path = os.path.join(base_dir, rel_path) if not os.path.isabs(rel_path) else rel_path

        if os.path.exists(abs_path):
            valid_testcases.append(entry)
        else:
            removed.append({
                "reason": "file not found",
                "path": rel_path,
                "title": entry.get("title", "Unknown")
            })

    index_data["testcases"] = valid_testcases
    count = original_count - len(valid_testcases)

    return count, removed


def cleanup_old_files(generated_dir: str, expired_days: int, dry_run: bool = False) -> tuple:
    """Remove files older than expired_days."""
    if not os.path.exists(generated_dir):
        return 0, []

    cutoff = datetime.now() - timedelta(days=expired_days)
    removed = []
    count = 0

    for root, dirs, files in os.walk(generated_dir):
        for file in files:
            if not file.endswith(('.xlsx', '.md', '.json')):
                continue

            file_path = os.path.join(root, file)
            mtime = get_file_mtime(file_path)

            if mtime and mtime < cutoff:
                if not dry_run:
                    try:
                        os.remove(file_path)
                        count += 1
                        removed.append({"path": file_path, "age_days": (datetime.now() - mtime).days})
                    except OSError as e:
                        removed.append({"path": file_path, "error": str(e)})
                else:
                    count += 1
                    removed.append({
                        "path": file_path,
                        "age_days": (datetime.now() - mtime).days,
                        "dry_run": True
                    })

    return count, removed


def main():
    parser = argparse.ArgumentParser(
        description="Clean up orphaned testcase files and expired indexes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing"
    )
    parser.add_argument(
        "--expired-days",
        type=int,
        default=90,
        help="Remove files older than N days (default: 90)"
    )
    parser.add_argument(
        "--base-dir",
        default="testcases",
        help="Base directory for testcases (default: testcases)"
    )

    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    generated_dir = os.path.join(base_dir, "generated")
    index_path = os.path.join(base_dir, "testcase-index.json")
    i18n_index_path = os.path.join(base_dir, "i18n-index.json")

    print(f"Base directory: {base_dir}")
    print(f"Generated directory: {generated_dir}")
    print(f"Expired threshold: {args.expired_days} days")
    print(f"Dry run: {args.dry_run}")
    print("-" * 50)

    # Cleanup orphaned index entries
    total_removed = 0
    all_removed = []

    for index_file in [index_path, i18n_index_path]:
        if not os.path.exists(index_file):
            print(f"Index not found: {index_file}")
            continue

        index_data, error = load_index(index_file)
        if error:
            print(f"ERROR: {error}")
            continue

        count, removed = cleanup_orphaned_entries(index_data, base_dir, args.dry_run)

        if count > 0:
            if not args.dry_run:
                success, save_error = save_index(index_file, index_data)
                if not save_error:
                    print(f"Cleaned {count} orphaned entries from {os.path.basename(index_file)}")
                else:
                    print(f"ERROR: {save_error}")
            else:
                print(f"Would clean {count} orphaned entries from {os.path.basename(index_file)}")

            total_removed += count
            all_removed.extend(removed)

    # Cleanup old files
    old_count, old_removed = cleanup_old_files(generated_dir, args.expired_days, args.dry_run)

    if old_count > 0:
        action = "Would remove" if args.dry_run else "Removed"
        print(f"{action} {old_count} files older than {args.expired_days} days")
        all_removed.extend(old_removed)

    total_removed += old_count

    print("-" * 50)
    print(f"Total cleanup: {total_removed} items")

    if args.dry_run:
        print("\nDry run complete. Re-run without --dry-run to apply changes.")
    else:
        print("\nCleanup complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
