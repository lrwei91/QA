#!/usr/bin/env python3
"""Validate multilingual verification JSON files for the QA skill set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_LANGUAGE_CODES = [
    'en-us',
    'id-id',
    'pt-pt',
    'es-es',
    'bn-bn',
    'tr-tr',
    'fp-fp',
]

REQUIRED_ROOT_KEYS = {'name', 'url', 'preScriptPath', 'options', 'entries'}
REQUIRED_OPTION_KEYS = {'matchRule', 'captureRegion'}
REQUIRED_CAPTURE_KEYS = {'x', 'y', 'width', 'height'}


def fail(message: str) -> int:
    print(f'ERROR: {message}')
    return 1


def ensure_string(value: object, field: str, allow_empty: bool = True) -> None:
    if not isinstance(value, str):
        raise ValueError(f"field '{field}' must be a string")
    if not allow_empty and not value.strip():
        raise ValueError(f"field '{field}' must be a non-empty string")


def ensure_number(value: object, field: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValueError(f"field '{field}' must be a number")


def analyze_i18n_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ValueError(f'invalid json: {exc}') from exc

    if not isinstance(data, dict):
        raise ValueError('root must be an object')

    missing_root = REQUIRED_ROOT_KEYS - set(data.keys())
    if missing_root:
        raise ValueError(f"missing root keys: {', '.join(sorted(missing_root))}")

    extra_root = set(data.keys()) - REQUIRED_ROOT_KEYS
    if extra_root:
        raise ValueError(f"unexpected root keys: {', '.join(sorted(extra_root))}")

    ensure_string(data['name'], 'name', allow_empty=False)
    ensure_string(data['url'], 'url')
    ensure_string(data['preScriptPath'], 'preScriptPath')

    # Validate entries array
    entries = data.get('entries', [])
    if not isinstance(entries, list):
        raise ValueError("field 'entries' must be an array")

    if len(entries) == 0:
        raise ValueError("field 'entries' must contain at least one entry")

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entries[{i}] must be an object")
        # 'key' is optional - only validate if present
        if 'key' in entry and not isinstance(entry['key'], str):
            raise ValueError(f"entries[{i}].key must be a string")
        if 'languages' not in entry:
            raise ValueError(f"entries[{i}] missing 'languages'")
        if not isinstance(entry['languages'], dict):
            raise ValueError(f"entries[{i}].languages must be an object")

        # Check required languages in each entry
        entry_langs = entry['languages']
        missing_langs = [code for code in REQUIRED_LANGUAGE_CODES if code not in entry_langs]
        if missing_langs:
            raise ValueError(f"entries[{i}] missing language codes: {', '.join(missing_langs)}")

        for code in REQUIRED_LANGUAGE_CODES:
            ensure_string(entry_langs[code], f'entries[{i}].languages.{code}')

    options = data['options']
    if not isinstance(options, dict):
        raise ValueError("field 'options' must be an object")

    missing_options = REQUIRED_OPTION_KEYS - set(options.keys())
    extra_options = set(options.keys()) - REQUIRED_OPTION_KEYS
    if missing_options:
        raise ValueError(f"missing options keys: {', '.join(sorted(missing_options))}")
    if extra_options:
        raise ValueError(f"unexpected options keys: {', '.join(sorted(extra_options))}")

    ensure_string(options['matchRule'], 'options.matchRule', allow_empty=False)

    capture_region = options['captureRegion']
    if not isinstance(capture_region, dict):
        raise ValueError("field 'options.captureRegion' must be an object")

    missing_capture = REQUIRED_CAPTURE_KEYS - set(capture_region.keys())
    extra_capture = set(capture_region.keys()) - REQUIRED_CAPTURE_KEYS
    if missing_capture:
        raise ValueError(f"missing captureRegion keys: {', '.join(sorted(missing_capture))}")
    if extra_capture:
        raise ValueError(f"unexpected captureRegion keys: {', '.join(sorted(extra_capture))}")

    for key in ['x', 'y', 'width', 'height']:
        ensure_number(capture_region[key], f'options.captureRegion.{key}')

    is_draft = (
        capture_region['x'] == 0
        and capture_region['y'] == 0
        and capture_region['width'] == 0
        and capture_region['height'] == 0
    )

    return {
        'name': data['name'].strip(),
        'language_codes': list(REQUIRED_LANGUAGE_CODES),
        'is_draft': is_draft,
        'data': data,
        'entry_count': len(entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate a single i18n JSON file against the schema.'
    )
    parser.add_argument(
        'file_path',
        help='Path to i18n JSON file'
    )
    args = parser.parse_args()

    path = Path(args.file_path).resolve()
    if not path.exists():
        return fail(f'file not found: {path}')

    try:
        result = analyze_i18n_json(path)
    except ValueError as exc:
        return fail(str(exc))

    state = 'draft' if result['is_draft'] else 'active'
    print(f"OK: validated i18n json ({state}) with {result['entry_count']} entries and {len(result['language_codes'])} languages")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
