#!/usr/bin/env python3
"""Validate i18n-index.json for the test-case-generator skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add script directory to path for sibling imports when running from workspace root
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_i18n_json import analyze_i18n_json

REQUIRED_ROOT_KEYS = {
    'version',
    'store_name',
    'root_dir',
    'i18n_dir',
    'updated_at',
    'entries',
}

REQUIRED_ENTRY_KEYS = {
    'id',
    'group_key',
    'title',
    'module',
    'module_ids',
    'topic',
    'language_codes',
    'format',
    'rel_path',
    'template',
    'source_refs',
    'tags',
    'status',
    'created_at',
    'updated_at',
}

VALID_STATUS = {'draft', 'active', 'archived'}


def fail(message: str) -> int:
    print(f'ERROR: {message}')
    return 1


def ensure_non_empty_string(value: object, key: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"field '{key}' must be a non-empty string")


def ensure_string_list(value: object, key: str, allow_empty: bool = False) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"field '{key}' must be a string list")
    if not allow_empty and not value:
        raise ValueError(f"field '{key}' must not be empty")


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate i18n-index.json structure and file references.'
    )
    parser.add_argument(
        'index_path',
        help='Path to i18n index file (testcases/i18n-index.json)'
    )
    args = parser.parse_args()

    index_path = Path(args.index_path).resolve()
    if not index_path.exists():
        return fail(f'file not found: {index_path}')

    try:
        data = json.loads(index_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return fail(f'invalid json: {exc}')

    if not isinstance(data, dict):
        return fail('i18n index must be a JSON object')

    missing_root = REQUIRED_ROOT_KEYS - set(data.keys())
    if missing_root:
        return fail(f"missing root keys: {', '.join(sorted(missing_root))}")

    extra_root = set(data.keys()) - REQUIRED_ROOT_KEYS
    if extra_root:
        return fail(f"unexpected root keys: {', '.join(sorted(extra_root))}")

    if data['version'] != 1:
        return fail("root field 'version' must equal 1")

    for key in ['store_name', 'root_dir', 'i18n_dir', 'updated_at']:
        try:
            ensure_non_empty_string(data[key], key)
        except ValueError as exc:
            return fail(str(exc))

    entries = data['entries']
    if not isinstance(entries, list):
        return fail("root field 'entries' must be a list")

    seen_ids: set[str] = set()
    root_dir = index_path.parent.resolve()
    i18n_prefix = f"{data['i18n_dir']}/"

    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            return fail(f'entry #{idx} must be an object')

        missing_entry = REQUIRED_ENTRY_KEYS - set(entry.keys())
        if missing_entry:
            return fail(f"entry #{idx} missing keys: {', '.join(sorted(missing_entry))}")

        extra_entry = set(entry.keys()) - REQUIRED_ENTRY_KEYS
        if extra_entry:
            return fail(f"entry #{idx} has unexpected keys: {', '.join(sorted(extra_entry))}")

        for key in [
            'id',
            'group_key',
            'title',
            'module',
            'topic',
            'format',
            'rel_path',
            'status',
            'created_at',
            'updated_at',
        ]:
            try:
                ensure_non_empty_string(entry[key], key)
            except ValueError as exc:
                return fail(f"entry #{idx} {exc}")

        try:
            ensure_string_list(entry['module_ids'], 'module_ids')
            ensure_string_list(entry['language_codes'], 'language_codes')
            ensure_string_list(entry['source_refs'], 'source_refs', allow_empty=True)
            ensure_string_list(entry['tags'], 'tags', allow_empty=True)
        except ValueError as exc:
            return fail(f'entry #{idx} {exc}')

        if not isinstance(entry['template'], str):
            return fail(f"entry #{idx} field 'template' must be a string")

        entry_id = entry['id']
        if entry_id in seen_ids:
            return fail(f'duplicate id: {entry_id}')
        seen_ids.add(entry_id)

        if entry['format'] != 'json':
            return fail(f"entry '{entry_id}' i18n rel_path must use json format")

        if entry['status'] not in VALID_STATUS:
            return fail(f"entry '{entry_id}' has invalid status: {entry['status']}")

        rel_path = Path(entry['rel_path'])
        if rel_path.is_absolute():
            return fail(f"entry '{entry_id}' rel_path must be relative")

        target = (root_dir / rel_path).resolve()
        try:
            target.relative_to(root_dir)
        except ValueError:
            return fail(f"entry '{entry_id}' rel_path escapes testcases root: {entry['rel_path']}")

        if not target.exists():
            return fail(f"entry '{entry_id}' points to missing file: {entry['rel_path']}")

        if not entry['rel_path'].startswith(i18n_prefix):
            return fail(f"entry '{entry_id}' i18n rel_path must be under {i18n_prefix}")

        try:
            analysis = analyze_i18n_json(target)
        except ValueError as exc:
            return fail(f"entry '{entry_id}' invalid i18n json: {exc}")

        if entry['language_codes'] != analysis['language_codes']:
            return fail(f"entry '{entry_id}' language_codes must match i18n json file")

        if analysis['is_draft'] and entry['status'] != 'draft':
            return fail(f"entry '{entry_id}' draft i18n json must use draft status")

    print(f'OK: validated i18n index with {len(entries)} entries')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
