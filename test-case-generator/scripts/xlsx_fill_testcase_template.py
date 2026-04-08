#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

"""
xlsx_fill_testcase_template.py — Fill the bundled testcase workbook template.

This script preserves the template's summary rows, colors, frozen panes,
dropdown validation, and wrapping styles. Testcase data starts at row 8.

Usage:
    python3 xlsx_fill_testcase_template.py rows.json output.xlsx
    python3 xlsx_fill_testcase_template.py rows.json output.xlsx --meta meta.json
    python3 xlsx_fill_testcase_template.py rows.json output.xlsx --template other.xlsx

Input JSON formats:
1. A list of testcase row objects
2. An object with {"rows": [...], "meta": {...}}

Supported row keys:
    序号, 平台, 模块, 功能点, 前置条件（测试点）, 操作步骤, 预期结果, 测试结果, 备注

Supported meta keys:
    测试平台, 测试日期, 系统&版本, 最后更新, 文档编写人, 文档测试人, 策划负责人, 审阅人员, 参考档
"""

import argparse
import json
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


NS_SS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_X14AC = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac"
NS_XR2 = "http://schemas.microsoft.com/office/spreadsheetml/2015/revision2"
NS_XR3 = "http://schemas.microsoft.com/office/spreadsheetml/2016/revision3"

ET.register_namespace("", NS_SS)
ET.register_namespace("r", NS_REL)
ET.register_namespace("mc", "http://schemas.openxmlformats.org/markup-compatibility/2006")
ET.register_namespace("x14ac", NS_X14AC)
ET.register_namespace("xr", "http://schemas.microsoft.com/office/spreadsheetml/2014/revision")
ET.register_namespace("xr2", NS_XR2)
ET.register_namespace("xr3", NS_XR3)


HEADER_ROW = 7
DATA_START_ROW = 8

DATA_STYLE_MAP = {
    "A": "3",
    "B": "4",
    "C": "3",
    "D": "3",
    "E": "5",
    "F": "5",
    "G": "5",
    "H": "23",
    "I": "3",
}

META_CELL_MAP = {
    "测试平台": "B2",
    "测试日期": "F2",
    "系统&版本": "B3",
    "最后更新": "F3",
    "文档编写人": "B4",
    "文档测试人": "F4",
    "策划负责人": "B5",
    "审阅人员": "F5",
    "参考档": "B6",
}

WORKSHEET_REQUIRED_NAMESPACE_DECLS = {
    "xmlns:r": NS_REL,
    "xmlns:x14ac": NS_X14AC,
    "xmlns:xr2": NS_XR2,
    "xmlns:xr3": NS_XR3,
}


def _tag(local: str) -> str:
    return f"{{{NS_SS}}}{local}"


def _set_text(elem: ET.Element, text: str) -> None:
    elem.text = text
    if text[:1].isspace() or text[-1:].isspace():
        elem.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _load_json(path: Path) -> object:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _normalize_rows(raw_rows: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for idx, raw in enumerate(raw_rows, start=1):
        rows.append(
            {
                "序号": idx,
                "平台": str(raw.get("平台", "") or "").strip(),
                "模块": str(raw.get("模块", "") or "").strip(),
                "功能点": str(raw.get("功能点", "") or "").strip(),
                "前置条件（测试点）": str(raw.get("前置条件（测试点）", "") or "").replace("\r\n", "\n").replace("\r", "\n").strip(),
                "操作步骤": str(raw.get("操作步骤", "") or "").replace("\r\n", "\n").replace("\r", "\n").strip(),
                "预期结果": str(raw.get("预期结果", "") or "").replace("\r\n", "\n").replace("\r", "\n").strip(),
                "测试结果": str(raw.get("测试结果", "") or "").strip(),
                "备注": str(raw.get("备注", "") or "").strip(),
            }
        )
    return rows


def _first_sheet_path(work_dir: Path) -> Path:
    wb_tree = ET.parse(work_dir / "xl/workbook.xml")
    wb_root = wb_tree.getroot()
    first_sheet = wb_root.find(_tag("sheets")).find(_tag("sheet"))
    rel_id = first_sheet.attrib[f"{{{NS_REL}}}id"]

    rels_tree = ET.parse(work_dir / "xl/_rels/workbook.xml.rels")
    rels_root = rels_tree.getroot()
    for rel in rels_root:
        if rel.attrib.get("Id") == rel_id:
            return work_dir / "xl" / rel.attrib["Target"]
    raise RuntimeError("Cannot resolve worksheet path from template workbook")


def _load_shared_strings(path: Path) -> tuple[ET.ElementTree, ET.Element, dict[str, int]]:
    tree = ET.parse(path)
    root = tree.getroot()
    index: dict[str, int] = {}
    for idx, si in enumerate(root.findall(_tag("si"))):
        texts = []
        for t in si.findall(".//" + _tag("t")):
            texts.append(t.text or "")
        value = "".join(texts)
        if value not in index:
            index[value] = idx
    return tree, root, index


def _shared_string_index(sst_root: ET.Element, sst_index: dict[str, int], value: str) -> int:
    existing = sst_index.get(value)
    if existing is not None:
        return existing

    idx = len(sst_index)
    si = ET.SubElement(sst_root, _tag("si"))
    t = ET.SubElement(si, _tag("t"))
    _set_text(t, value)
    sst_index[value] = idx
    sst_root.set("count", str(idx + 1))
    sst_root.set("uniqueCount", str(idx + 1))
    return idx


def _row_cells(row_elem: ET.Element) -> dict[str, ET.Element]:
    return {cell.attrib["r"]: cell for cell in row_elem.findall(_tag("c"))}


def _set_shared_string_cell(
    row_elem: ET.Element,
    ref: str,
    style: str,
    value: str,
    sst_root: ET.Element,
    sst_index: dict[str, int],
) -> None:
    cells = _row_cells(row_elem)
    cell = cells.get(ref)
    if cell is None:
        cell = ET.SubElement(row_elem, _tag("c"), {"r": ref})
    else:
        for child in list(cell):
            cell.remove(child)
    cell.set("s", style)
    cell.set("t", "s")
    idx = _shared_string_index(sst_root, sst_index, value)
    ET.SubElement(cell, _tag("v")).text = str(idx)


def _set_formula_cell(row_elem: ET.Element, ref: str, style: str, formula: str) -> None:
    cells = _row_cells(row_elem)
    cell = cells.get(ref)
    if cell is None:
        cell = ET.SubElement(row_elem, _tag("c"), {"r": ref})
    else:
        for child in list(cell):
            cell.remove(child)
    cell.set("s", style)
    cell.attrib.pop("t", None)
    ET.SubElement(cell, _tag("f")).text = formula
    ET.SubElement(cell, _tag("v")).text = ""


def _calc_row_height(data: dict) -> float:
    """Calculate row height based on content length in wrap columns.

    Excel's default row height is 15 points. With wrap text, we need to
    increase height for multi-line content. This is a heuristic calculation.
    """
    base_height = 15.0
    wrap_columns = ["前置条件（测试点）", "操作步骤", "预期结果"]
    # Column widths in points (from template)
    col_widths = {
        "前置条件（测试点）": 43.0,
        "操作步骤": 53.0,
        "预期结果": 60.0,
    }

    max_lines = 1
    for col_name in wrap_columns:
        value = data.get(col_name, "")
        if value:
            # Count newlines + estimate wrapped lines
            lines = value.count('\n') + 1
            # Estimate additional lines from content length
            width = col_widths.get(col_name, 50.0)
            # Rough estimate: 12 chars per line at default font
            estimated_lines = max(1, len(value) // int(width * 0.8))
            max_lines = max(max_lines, lines + estimated_lines - 1)

    # Cap at reasonable height (Excel max is 409)
    return min(base_height * max_lines, 200.0)


def _build_data_row(row_num: int, data: dict, sst_root: ET.Element, sst_index: dict[str, int]) -> ET.Element:
    # Calculate appropriate row height for wrapped content
    row_height = _calc_row_height(data)
    row_elem = ET.Element(_tag("row"), {
        "r": str(row_num),
        "ht": str(row_height),
        "customHeight": "1"
    })

    number_cell = ET.SubElement(row_elem, _tag("c"), {"r": f"A{row_num}", "s": DATA_STYLE_MAP["A"]})
    ET.SubElement(number_cell, _tag("v")).text = str(int(data["序号"]))

    col_to_value = {
        "B": data["平台"],
        "C": data["模块"],
        "D": data["功能点"],
        "E": data["前置条件（测试点）"],
        "F": data["操作步骤"],
        "G": data["预期结果"],
        "H": data["测试结果"],
        "I": data["备注"],
    }

    # Columns that need wrap text (multi-line fields)
    wrap_columns = ["E", "F", "G"]

    for col in ["B", "C", "D", "E", "F", "G", "H", "I"]:
        attrs = {"r": f"{col}{row_num}", "s": DATA_STYLE_MAP[col]}
        value = col_to_value[col]
        if value:
            cell = ET.SubElement(row_elem, _tag("c"), {**attrs, "t": "s"})
            idx = _shared_string_index(sst_root, sst_index, value)
            ET.SubElement(cell, _tag("v")).text = str(idx)
            # Add wrap text alignment for multi-line fields
            if col in wrap_columns:
                ET.SubElement(cell, _tag("alignment"), {"wrapText": "1"})
        else:
            cell = ET.SubElement(row_elem, _tag("c"), attrs)
            # Add wrap text alignment for multi-line fields even if empty
            if col in wrap_columns:
                ET.SubElement(cell, _tag("alignment"), {"wrapText": "1"})

    return row_elem


def _count_shared_string_refs(sheet_data: ET.Element) -> int:
    count = 0
    for cell in sheet_data.findall(".//" + _tag("c")):
        if cell.attrib.get("t") == "s":
            count += 1
    return count


def _inject_required_worksheet_namespaces(xml_bytes: bytes) -> bytes:
    text = xml_bytes.decode("utf-8")
    match = re.search(r"<worksheet\b[^>]*>", text)
    if not match:
        return xml_bytes

    root_tag = match.group(0)
    updated = root_tag
    for attr, value in WORKSHEET_REQUIRED_NAMESPACE_DECLS.items():
        if f'{attr}="' not in updated:
            updated = updated[:-1] + f' {attr}="{value}">'

    if updated == root_tag:
        return xml_bytes
    return (text[: match.start()] + updated + text[match.end() :]).encode("utf-8")


def _remove_calc_chain_parts(replacement_bytes: dict[str, bytes]) -> None:
    rels_name = "xl/_rels/workbook.xml.rels"
    content_types_name = "[Content_Types].xml"

    rels_text = replacement_bytes[rels_name].decode("utf-8")
    rels_text = re.sub(
        r'<Relationship\b[^>]*Type="http://schemas\.openxmlformats\.org/officeDocument/2006/relationships/calcChain"[^>]*/>',
        "",
        rels_text,
    )
    replacement_bytes[rels_name] = rels_text.encode("utf-8")

    content_types_text = replacement_bytes[content_types_name].decode("utf-8")
    content_types_text = re.sub(
        r'<Override\b[^>]*PartName="/xl/calcChain\.xml"[^>]*/>',
        "",
        content_types_text,
    )
    replacement_bytes[content_types_name] = content_types_text.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill testcase template workbook")
    parser.add_argument("rows_json", help="JSON rows file")
    parser.add_argument("output_xlsx", help="Output xlsx path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent.parent / "templates" / "testcase_template.xlsx"),
        help="Template xlsx path",
    )
    parser.add_argument("--meta", help="Optional metadata JSON path")
    args = parser.parse_args()

    template_xlsx = Path(args.template).resolve()
    output_xlsx = Path(args.output_xlsx).resolve()
    output_xlsx.parent.mkdir(parents=True, exist_ok=True)

    payload = _load_json(Path(args.rows_json))
    meta: dict[str, str] = {}
    if isinstance(payload, dict):
        rows_payload = payload.get("rows", [])
        meta.update(payload.get("meta", {}) or {})
    else:
        rows_payload = payload

    if args.meta:
        extra_meta = _load_json(Path(args.meta))
        if isinstance(extra_meta, dict):
            meta.update(extra_meta)

    rows = _normalize_rows(rows_payload)
    last_data_row = DATA_START_ROW + max(len(rows) - 1, 0)

    with tempfile.TemporaryDirectory(prefix="testcase_template_") as tmp:
        work_dir = Path(tmp)
        with zipfile.ZipFile(template_xlsx, "r") as zf:
            zf.extractall(work_dir)

        shared_strings_path = work_dir / "xl/sharedStrings.xml"
        sheet_path = _first_sheet_path(work_dir)

        sst_tree, sst_root, sst_index = _load_shared_strings(shared_strings_path)
        ws_tree = ET.parse(sheet_path)
        ws_root = ws_tree.getroot()
        sheet_data = ws_root.find(_tag("sheetData"))

        rows_by_number = {int(row.attrib["r"]): row for row in sheet_data.findall(_tag("row"))}

        for row_elem in list(sheet_data.findall(_tag("row"))):
            if int(row_elem.attrib["r"]) >= DATA_START_ROW:
                sheet_data.remove(row_elem)

        for key, ref in META_CELL_MAP.items():
            value = str(meta.get(key, "") or "").strip()
            if not value:
                continue
            row_num = int("".join(ch for ch in ref if ch.isdigit()))
            row_elem = rows_by_number[row_num]
            cell = _row_cells(row_elem).get(ref)
            style = cell.attrib.get("s", "3") if cell is not None else "3"
            _set_shared_string_cell(row_elem, ref, style, value, sst_root, sst_index)

        _set_formula_cell(rows_by_number[1], "H1", _row_cells(rows_by_number[1])["H1"].attrib["s"], "H2+H3+H4")
        _set_formula_cell(rows_by_number[2], "H2", _row_cells(rows_by_number[2])["H2"].attrib["s"], f"COUNTIF(H{DATA_START_ROW}:H{last_data_row},G2)")
        _set_formula_cell(rows_by_number[3], "H3", _row_cells(rows_by_number[3])["H3"].attrib["s"], f"COUNTIF(H{DATA_START_ROW}:H{last_data_row},G3)")
        _set_formula_cell(rows_by_number[4], "H4", _row_cells(rows_by_number[4])["H4"].attrib["s"], f"COUNTIF(H{DATA_START_ROW}:H{last_data_row},G4)")

        insert_index = list(sheet_data).index(rows_by_number[HEADER_ROW]) + 1
        for offset, row in enumerate(rows):
            row_num = DATA_START_ROW + offset
            sheet_data.insert(insert_index + offset, _build_data_row(row_num, row, sst_root, sst_index))

        sst_root.set("count", str(_count_shared_string_refs(sheet_data)))
        sst_root.set("uniqueCount", str(len(sst_index)))
        sst_tree.write(shared_strings_path, encoding="utf-8", xml_declaration=True)

        ws_root.find(_tag("dimension")).set("ref", f"A1:J{last_data_row}")

        cond = ws_root.find(_tag("conditionalFormatting"))
        if cond is not None:
            cond.set("sqref", f"H{DATA_START_ROW}:H{last_data_row}")

        dvals = ws_root.find(_tag("dataValidations"))
        if dvals is not None:
            for dval in dvals.findall(_tag("dataValidation")):
                dval.set("sqref", f"H{DATA_START_ROW}:H{last_data_row}")

        ignored = ws_root.find(_tag("ignoredErrors"))
        if ignored is not None:
            ws_root.remove(ignored)

        ws_tree.write(sheet_path, encoding="utf-8", xml_declaration=True)
        normalized_sheet_bytes = _inject_required_worksheet_namespaces(sheet_path.read_bytes())

        replacement_bytes = {
            "xl/sharedStrings.xml": shared_strings_path.read_bytes(),
            "xl/worksheets/sheet1.xml": normalized_sheet_bytes,
            "xl/_rels/workbook.xml.rels": (work_dir / "xl/_rels/workbook.xml.rels").read_bytes(),
            "[Content_Types].xml": (work_dir / "[Content_Types].xml").read_bytes(),
        }
        _remove_calc_chain_parts(replacement_bytes)

        with zipfile.ZipFile(template_xlsx, "r") as src_zip, zipfile.ZipFile(
            output_xlsx, "w", compression=zipfile.ZIP_DEFLATED
        ) as out_zip:
            for info in src_zip.infolist():
                if info.filename == "xl/calcChain.xml":
                    continue
                data = replacement_bytes.get(info.filename)
                if data is None:
                    data = src_zip.read(info.filename)
                out_zip.writestr(info.filename, data)

    print(output_xlsx)


if __name__ == "__main__":
    main()
