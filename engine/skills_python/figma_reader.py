"""
Skill: Figma Reader - Python Implementation

读取 Figma 设计稿数据，提取文案、组件结构、设计标注和交互说明
"""

import json
import os
import subprocess
import re
from pathlib import Path
from typing import Any


def read_figma(figma_url: str) -> dict[str, Any]:
    """
    读取 Figma 设计稿

    参数:
        figma_url: Figma 设计稿 URL

    返回:
        包含 texts, components, states, interactions 的字典
    """
    # 解析 URL
    parsed = parse_figma_url(figma_url)
    if not parsed:
        return {"error": "Invalid Figma URL", "file_id": None, "node_id": None}

    file_id = parsed["file_id"]
    node_id = parsed["node_id"]

    # 获取 Token
    token = os.environ.get("FIGMA_ACCESS_TOKEN")
    if not token:
        return {"error": "FIGMA_ACCESS_TOKEN not set", "file_id": file_id, "node_id": node_id}

    # 调用 API
    api_endpoint = f"https://api.figma.com/v1/files/{file_id}/nodes?ids={node_id}" if node_id else f"https://api.figma.com/v1/files/{file_id}"

    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"X-Figma-Token: {token}", api_endpoint],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            return {"error": f"API call failed: {result.stderr}", "file_id": file_id}

        api_response = json.loads(result.stdout)

        if "err" in api_response:
            return {"error": f"Figma API error: {api_response.get('status')}", "file_id": file_id}

        # 提取数据
        return extract_figma_data(api_response, file_id, node_id)

    except subprocess.TimeoutExpired:
        return {"error": "API call timed out", "file_id": file_id}
    except Exception as e:
        return {"error": str(e), "file_id": file_id}


def parse_figma_url(figma_url: str) -> dict | None:
    """解析 Figma URL"""
    file_id_match = re.search(r'/file/([a-zA-Z0-9]+)/', figma_url)
    node_id_match = re.search(r'node-id=(\d+[:\-]\d+)', figma_url)

    if not file_id_match:
        return None

    return {
        "file_id": file_id_match.group(1),
        "node_id": node_id_match.group(1) if node_id_match else None
    }


def extract_figma_data(api_response: dict, file_id: str, node_id: str) -> dict[str, Any]:
    """从 Figma API 响应中提取数据"""
    result = {
        "source": "figma_api",
        "file_id": file_id,
        "node_id": node_id,
        "file_name": api_response.get("name", "Unknown"),
        "texts": [],
        "components": [],
        "states": [],
        "interactions": [],
        "testcase_hints": {
            "ui_elements": [],
            "actions": [],
            "states_to_test": [],
            "navigation": []
        }
    }

    nodes = api_response.get("nodes", {})
    for node_key, node_data in nodes.items():
        if not node_data or "document" not in node_data:
            continue

        document = node_data["document"]
        _extract_node_tree(document, result)

    return result


def _extract_node_tree(node: dict, result: dict, parent: str = None):
    """递归遍历节点树"""
    node_name = node.get("name", "Unnamed")
    node_type = node.get("type", "UNKNOWN")

    # 提取文本
    if node_type == "TEXT" and node.get("characters"):
        result["texts"].append({
            "id": f"text_{len(result['texts'])}",
            "content": node["characters"],
            "layer_name": node_name,
            "parent": parent
        })

    # 提取组件
    if node_type in ["FRAME", "COMPONENT", "COMPONENT_SET", "GROUP"]:
        result["components"].append({
            "id": f"comp_{len(result['components'])}",
            "name": node_name,
            "type": node_type,
            "parent": parent
        })

        # 组件状态
        if node_type == "COMPONENT_SET":
            variants = node.get("children", [])
            result["states"].append({
                "component": node_name,
                "variants": [v.get("name", "") for v in variants]
            })

    # 递归子节点
    for child in node.get("children", []):
        _extract_node_tree(child, result, parent=node_name)
