#!/usr/bin/env python3
"""Validate module-index.json for the QA skill set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = {
    'id',
    'name',
    'domain',
    'aliases',
    'trigger_words',
    'core_functions',
    'depends_on',
    'impacted_modules',
    'always_check',
    'platform_scope',
    'client_signals',
    'server_signals',
    'reference_file',
}
VALID_DOMAINS = {'account-access', 'finance-system', 'marketing-activities', 'affiliate-management'}
VALID_PLATFORMS = {'客户端', '账服'}


def fail(msg: str) -> int:
    print(f'ERROR: {msg}')
    return 1


def ensure_string_list(value, key: str, entry_id: str):
    if not isinstance(value, list) or not all(isinstance(i, str) and i.strip() for i in value):
        raise ValueError(f"entry '{entry_id}' field '{key}' must be a non-empty string list")


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate module-index.json structure and references.'
    )
    parser.add_argument(
        'index_path',
        help='Path to module index file (index-rules/module-index.json)'
    )
    args = parser.parse_args()

    index_path = Path(args.index_path).resolve()
    if not index_path.exists():
        return fail(f'file not found: {index_path}')

    try:
        data = json.loads(index_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return fail(f'invalid json: {exc}')

    if not isinstance(data, list) or not data:
        return fail('module-index.json must be a non-empty list')

    ids = []
    entry_map = {}
    for idx, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            return fail(f'entry #{idx} must be an object')
        missing = REQUIRED_KEYS - set(entry.keys())
        if missing:
            return fail(f"entry #{idx} missing keys: {', '.join(sorted(missing))}")
        extra = set(entry.keys()) - REQUIRED_KEYS
        if extra:
            return fail(f"entry #{idx} has unexpected keys: {', '.join(sorted(extra))}")

        entry_id = entry['id']
        if not isinstance(entry_id, str) or not entry_id.strip():
            return fail(f"entry #{idx} field 'id' must be a non-empty string")
        if entry_id in entry_map:
            return fail(f"duplicate id: {entry_id}")
        ids.append(entry_id)
        entry_map[entry_id] = entry

        if entry['domain'] not in VALID_DOMAINS:
            return fail(f"entry '{entry_id}' has invalid domain: {entry['domain']}")

        for key in ['aliases', 'trigger_words', 'core_functions', 'depends_on', 'impacted_modules', 'always_check', 'platform_scope', 'client_signals', 'server_signals']:
            try:
                ensure_string_list(entry[key], key, entry_id)
            except ValueError as exc:
                return fail(str(exc))

        bad_platforms = set(entry['platform_scope']) - VALID_PLATFORMS
        if bad_platforms:
            return fail(f"entry '{entry_id}' has invalid platform_scope value(s): {', '.join(sorted(bad_platforms))}")

        ref = Path(index_path.parent / entry['reference_file'])
        if not ref.exists():
            return fail(f"entry '{entry_id}' points to missing reference file: {entry['reference_file']}")

    valid_ids = set(ids)
    for entry_id, entry in entry_map.items():
        for rel_key in ['depends_on', 'impacted_modules']:
            unknown = set(entry[rel_key]) - valid_ids
            if unknown:
                return fail(f"entry '{entry_id}' has unknown {rel_key}: {', '.join(sorted(unknown))}")

    print(f'OK: validated {len(data)} module entries')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
