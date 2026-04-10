"""
Skill: Test Case I18N - Python Implementation

多语言 JSON 校验与生成
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any


STANDARD_LANGUAGES = ["en-us", "id-id", "pt-pt", "es-es", "bn-bn", "tr-tr", "fp-fp"]


def validate_and_generate_json(input_content: str) -> dict[str, Any]:
    """
    校验多语言数据并生成 JSON

    参数:
        input_content: 包含多语言文案的内容

    返回:
        {
            "success": bool,
            "i18n_json": dict | None,
            "missing_languages": list,
            "file_path": str | None
        }
    """
    # 提取多语言数据
    i18n_data = extract_i18n_data(input_content)

    if not i18n_data:
        return {
            "success": False,
            "error": "No i18n data found",
            "i18n_json": None,
            "missing_languages": [],
            "file_path": None
        }

    # 校验语言完整性
    validation = validate_languages(i18n_data, STANDARD_LANGUAGES)

    if not validation["is_complete"]:
        return {
            "success": False,
            "error": "Incomplete languages",
            "i18n_json": None,
            "missing_languages": validation["missing_languages"],
            "file_path": None
        }

    # 生成 JSON 文件
    file_path = save_i18n_json(i18n_data)

    return {
        "success": True,
        "i18n_json": i18n_data,
        "missing_languages": [],
        "file_path": file_path
    }


def extract_i18n_data(input_content: str) -> dict | None:
    """从输入内容中提取多语言数据"""
    # 尝试解析 JSON
    try:
        json_pattern = r'\{[^{}]*"?(?:en-us|id-id|pt-pt)"?[^{}]*\}'
        json_matches = re.findall(json_pattern, input_content, re.IGNORECASE)

        for match in json_matches:
            try:
                data = json.loads(match)
                if any(lang in data for lang in STANDARD_LANGUAGES):
                    return {"entries": [data], "source": "input_json"}
            except json.JSONDecodeError:
                continue
    except:
        pass

    return None


def validate_languages(i18n_data: dict, languages: list[str]) -> dict:
    """校验语言完整性"""
    entries = i18n_data.get("entries", [])
    missing = []

    for entry in entries:
        for lang in languages:
            if lang not in entry and lang not in missing:
                missing.append(lang)

    return {
        "is_complete": len(missing) == 0,
        "missing_languages": missing,
        "total_entries": len(entries),
        "complete_entries": sum(1 for e in entries if all(lang in e for lang in languages))
    }


def save_i18n_json(i18n_data: dict) -> str | None:
    """保存多语言 JSON 文件"""
    try:
        output_dir = Path(__file__).parent.parent.parent / "testcases" / "i18n"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"i18n_{timestamp}.json"

        output_data = {
            "created_at": datetime.now().isoformat(),
            "source": i18n_data.get("source", "unknown"),
            "entries": i18n_data.get("entries", [])
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return str(output_file)
    except Exception:
        return None


def detect_i18n(input_content: str) -> bool:
    """检测是否包含多语言数据"""
    keywords = ["多语言", "国际化", "i18n", "en-us", "id-id", "pt-pt", "es-es", "bn-bn", "tr-tr", "fp-fp"]
    return any(kw.lower() in input_content.lower() for kw in keywords)
