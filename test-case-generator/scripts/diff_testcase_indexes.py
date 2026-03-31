#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
diff_testcase_indexes.py - Compare testcase indexes and show differences.

Usage:
    python3 diff_testcase_indexes.py index1.json index2.json [--format json|text]

This script helps identify:
- New test cases added between versions
- Removed test cases
- Modified test cases (based on title, module, or content hash)
"""

import argparse
import json
import os
import sys
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


def entry_key(entry: dict) -> str:
    """Generate a unique key for a testcase entry."""
    # Use combination of title and module as key
    title = entry.get("title", "")
    module = entry.get("module", "")
    return f"{module}:{title}"


def entries_by_key(entries: list) -> dict:
    """Index entries by their key."""
    return {entry_key(e): e for e in entries}


def compute_diff(index1: dict, index2: dict) -> dict:
    """Compute differences between two indexes."""
    testcases1 = index1.get("testcases", [])
    testcases2 = index2.get("testcases", [])

    map1 = entries_by_key(testcases1)
    map2 = entries_by_key(testcases2)

    keys1 = set(map1.keys())
    keys2 = set(map2.keys())

    # Find differences
    added_keys = keys2 - keys1
    removed_keys = keys1 - keys2
    common_keys = keys1 & keys2

    added = [map2[k] for k in sorted(added_keys)]
    removed = [map1[k] for k in sorted(removed_keys)]

    # Check for modifications in common entries
    modified = []
    for key in sorted(common_keys):
        entry1 = map1[key]
        entry2 = map2[key]

        # Compare relevant fields
        changes = []

        if entry1.get("status") != entry2.get("status"):
            changes.append({
                "field": "status",
                "old": entry1.get("status"),
                "new": entry2.get("status")
            })

        if entry1.get("updated_at") != entry2.get("updated_at"):
            changes.append({
                "field": "updated_at",
                "old": entry1.get("updated_at"),
                "new": entry2.get("updated_at")
            })

        # Compare tags
        tags1 = set(entry1.get("tags", []))
        tags2 = set(entry2.get("tags", []))
        if tags1 != tags2:
            changes.append({
                "field": "tags",
                "removed": list(tags1 - tags2),
                "added": list(tags2 - tags1)
            })

        if changes:
            modified.append({
                "key": key,
                "title": entry1.get("title"),
                "module": entry1.get("module"),
                "changes": changes
            })

    return {
        "summary": {
            "index1_count": len(testcases1),
            "index2_count": len(testcases2),
            "added": len(added),
            "removed": len(removed),
            "modified": len(modified),
            "unchanged": len(common_keys) - len(modified)
        },
        "added": added,
        "removed": removed,
        "modified": modified
    }


def format_text(diff: dict, index1_name: str, index2_name: str) -> str:
    """Format diff as human-readable text."""
    lines = []
    summary = diff["summary"]

    lines.append("=" * 60)
    lines.append("Testcase Index Diff Report")
    lines.append("=" * 60)
    lines.append(f"Comparing: {index1_name} -> {index2_name}")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"  {index1_name}: {summary['index1_count']} test cases")
    lines.append(f"  {index2_name}: {summary['index2_count']} test cases")
    lines.append(f"  Added:     {summary['added']}")
    lines.append(f"  Removed:   {summary['removed']}")
    lines.append(f"  Modified:  {summary['modified']}")
    lines.append(f"  Unchanged: {summary['unchanged']}")
    lines.append("")

    if diff["added"]:
        lines.append("-" * 60)
        lines.append("ADDED Test Cases:")
        lines.append("-" * 60)
        for entry in diff["added"]:
            lines.append(f"  + [{entry.get('module', 'N/A')}] {entry.get('title', 'N/A')}")
        lines.append("")

    if diff["removed"]:
        lines.append("-" * 60)
        lines.append("REMOVED Test Cases:")
        lines.append("-" * 60)
        for entry in diff["removed"]:
            lines.append(f"  - [{entry.get('module', 'N/A')}] {entry.get('title', 'N/A')}")
        lines.append("")

    if diff["modified"]:
        lines.append("-" * 60)
        lines.append("MODIFIED Test Cases:")
        lines.append("-" * 60)
        for entry in diff["modified"]:
            lines.append(f"  ~ [{entry.get('module', 'N/A')}] {entry.get('title', 'N/A')}")
            for change in entry.get("changes", []):
                field = change.get("field")
                if field in ["status", "updated_at"]:
                    lines.append(f"      {field}: {change.get('old')} -> {change.get('new')}")
                elif field == "tags":
                    lines.append(f"      tags: -{change.get('removed')} +{change.get('added')}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare testcase indexes and show differences"
    )
    parser.add_argument("index1", help="Path to first index file (baseline)")
    parser.add_argument("index2", help="Path to second index file (comparison)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    index1, error1 = load_index(args.index1)
    if error1:
        print(f"ERROR: {error1}", file=sys.stderr)
        sys.exit(1)

    index2, error2 = load_index(args.index2)
    if error2:
        print(f"ERROR: {error2}", file=sys.stderr)
        sys.exit(1)

    diff = compute_diff(index1, index2)

    if args.format == "json":
        print(json.dumps(diff, indent=2, ensure_ascii=False))
    else:
        print(format_text(diff, args.index1, args.index2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
