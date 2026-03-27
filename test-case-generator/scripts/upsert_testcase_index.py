#!/usr/bin/env python3
"""Create or update testcase index entries for files in the workspace store."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

VALID_EXTENSIONS = {
    '.md': 'md',
    '.xlsx': 'xlsx',
    '.docx': 'docx',
    '.csv': 'csv',
    '.txt': 'txt',
}
VALID_STATUSES = {'draft', 'active', 'archived'}
GENERIC_TAG_STOPWORDS = {'测试', '测试用例', '测试案例', '用例'}
GENERIC_SUFFIXES = ['汇总', '优化', '改造', '功能', '前后端']


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def fail(message: str) -> int:
    print(f'ERROR: {message}')
    return 1


def stable_slug(text: str, prefix: str) -> str:
    cleaned = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    digest = hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]
    if cleaned:
        return f'{prefix}-{cleaned}-{digest}'
    return f'{prefix}-{digest}'


def default_index_data(index_path: Path) -> dict:
    return {
        'version': 1,
        'store_name': 'QA Test Case Store',
        'root_dir': index_path.parent.name,
        'cases_dir': 'generated',
        'updated_at': now_iso(),
        'entries': [],
    }


def load_index(index_path: Path) -> dict:
    if not index_path.exists():
        return default_index_data(index_path)
    return json.loads(index_path.read_text(encoding='utf-8'))


def dump_index(index_path: Path, data: dict) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def first_non_empty_string(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ''
    return str(value).strip()


def infer_xlsx_metadata(path: Path) -> dict:
    workbook = load_workbook(path, read_only=True, data_only=False)
    worksheet = workbook[workbook.sheetnames[0]]
    title = first_non_empty_string(worksheet['A1'].value) or path.stem

    platform_scope: list[str] = []
    seen_platforms: set[str] = set()
    max_row = min(worksheet.max_row, 5000)
    for row in range(8, max_row + 1):
        label = first_non_empty_string(worksheet.cell(row, 2).value)
        if label and label not in seen_platforms:
            seen_platforms.add(label)
            platform_scope.append(label)

    return {
        'title': title,
        'topic': title,
        'sheet_name': workbook.sheetnames[0],
        'platform_scope': platform_scope,
    }


def infer_text_metadata(path: Path) -> dict:
    return {
        'title': path.stem,
        'topic': path.stem,
        'sheet_name': '',
        'platform_scope': [],
    }


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def split_title_chunks(title: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r'[\-_/|｜]+', title) if chunk.strip()]


def strip_generic_suffixes(text: str) -> str:
    cleaned = text.strip().strip('()（）[]【】')
    previous = None
    while cleaned and cleaned != previous:
        previous = cleaned
        for suffix in GENERIC_SUFFIXES:
            if cleaned.endswith(suffix) and len(cleaned) > len(suffix):
                cleaned = cleaned[: -len(suffix)].rstrip().rstrip('-_/|｜').strip().strip('()（）[]【】')
                break
    return cleaned


def derive_tags(module: str, title: str, extra_tags: list[str]) -> list[str]:
    candidates = [module]
    for chunk in split_title_chunks(title):
        cleaned = strip_generic_suffixes(chunk)
        if not cleaned:
            continue
        if cleaned in GENERIC_TAG_STOPWORDS:
            continue
        if len(cleaned) < 2:
            continue
        candidates.append(cleaned)
    candidates.extend(extra_tags)
    return dedupe_keep_order(candidates)


def infer_module(rel_path: Path, cases_dir: str) -> str:
    parts = rel_path.parts
    if len(parts) >= 2 and parts[0] == cases_dir:
        return parts[1]
    if len(parts) >= 2:
        return parts[-2]
    return rel_path.stem


def infer_entry(path: Path, store_root: Path, index_data: dict, args: argparse.Namespace) -> dict:
    rel_path = path.relative_to(store_root)
    file_format = VALID_EXTENSIONS[path.suffix.lower()]
    module = args.module or infer_module(rel_path, index_data['cases_dir'])

    if file_format == 'xlsx':
        inferred = infer_xlsx_metadata(path)
    else:
        inferred = infer_text_metadata(path)

    title = args.title or inferred['title']
    topic = args.topic or inferred['topic']
    platform_scope = args.platform_scope or inferred['platform_scope']
    module_ids = args.module_ids or [stable_slug(module, 'module')]

    tags = derive_tags(module, title, args.tags)

    entry_id = stable_slug(rel_path.as_posix(), 'tc')
    return {
        'id': entry_id,
        'title': title,
        'module': module,
        'module_ids': dedupe_keep_order(module_ids),
        'topic': topic,
        'platform_scope': dedupe_keep_order(platform_scope),
        'format': file_format,
        'rel_path': rel_path.as_posix(),
        'template': args.template or '',
        'source_refs': dedupe_keep_order(args.source_refs),
        'tags': tags,
        'status': args.status,
        'created_at': now_iso(),
        'updated_at': now_iso(),
    }


def merge_entry(existing: dict, new_entry: dict) -> dict:
    created_at = existing.get('created_at') or new_entry['created_at']
    merged = dict(new_entry)
    merged['id'] = existing.get('id', new_entry['id'])
    merged['created_at'] = created_at
    merged['source_refs'] = dedupe_keep_order(existing.get('source_refs', []) + new_entry['source_refs'])
    merged['tags'] = dedupe_keep_order(new_entry['tags'])
    merged['module_ids'] = dedupe_keep_order(existing.get('module_ids', []) + new_entry['module_ids'])
    merged['platform_scope'] = dedupe_keep_order(existing.get('platform_scope', []) + new_entry['platform_scope'])
    return merged


def collect_files(store_root: Path, index_data: dict, args: argparse.Namespace) -> list[Path]:
    if args.all:
        cases_dir = store_root / index_data['cases_dir']
        if not cases_dir.exists():
            return []
        files = []
        for path in sorted(cases_dir.rglob('*')):
            if not path.is_file():
                continue
            if path.name.startswith('.'):
                continue
            if path.suffix.lower() in VALID_EXTENSIONS:
                files.append(path.resolve())
        return files

    files = [Path(item).resolve() for item in args.files]
    return files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Create or update entries in testcases/index.json for testcase files.'
    )
    parser.add_argument('files', nargs='*', help='Testcase files to upsert into the index')
    parser.add_argument('--all', action='store_true', help='Scan the whole cases_dir and upsert all supported files')
    parser.add_argument(
        '--index',
        default='testcases/index.json',
        help='Path to testcase index file. Defaults to testcases/index.json',
    )
    parser.add_argument('--title', help='Override entry title')
    parser.add_argument('--topic', help='Override entry topic')
    parser.add_argument('--module', help='Override entry module')
    parser.add_argument('--module-id', action='append', dest='module_ids', default=[], help='Append module id')
    parser.add_argument('--platform', action='append', dest='platform_scope', default=[], help='Append platform label')
    parser.add_argument('--tag', action='append', dest='tags', default=[], help='Append tag')
    parser.add_argument('--source-ref', action='append', dest='source_refs', default=[], help='Append source ref')
    parser.add_argument('--template', default='', help='Set template name or path')
    parser.add_argument('--status', default='active', help='Entry status: draft, active, archived')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.status not in VALID_STATUSES:
        return fail(f"invalid status: {args.status}")

    if not args.all and not args.files:
        return fail('provide at least one testcase file or use --all')

    index_path = Path(args.index).resolve()
    index_data = load_index(index_path)
    store_root = index_path.parent.resolve()
    files = collect_files(store_root, index_data, args)

    if not files:
        print('No testcase files found to index')
        return 0

    for path in files:
        if not path.exists():
            return fail(f'file not found: {path}')
        if path.suffix.lower() not in VALID_EXTENSIONS:
            return fail(f'unsupported file format: {path}')
        try:
            path.relative_to(store_root)
        except ValueError:
            return fail(f'file is outside testcase store root: {path}')

    entries_by_path = {entry['rel_path']: entry for entry in index_data.get('entries', [])}
    updated_entries: dict[str, dict] = {}

    for path in files:
        new_entry = infer_entry(path, store_root, index_data, args)
        existing = entries_by_path.get(new_entry['rel_path'])
        updated_entries[new_entry['rel_path']] = merge_entry(existing, new_entry) if existing else new_entry

    for rel_path, entry in entries_by_path.items():
        if rel_path not in updated_entries:
            updated_entries[rel_path] = entry

    index_data['entries'] = [updated_entries[key] for key in sorted(updated_entries)]
    index_data['updated_at'] = now_iso()
    dump_index(index_path, index_data)

    print(f'Updated {len(files)} testcase entry(s) in {index_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
