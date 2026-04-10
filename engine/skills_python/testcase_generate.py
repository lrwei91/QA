"""
Skill: Generate Test Cases - Python Implementation

从需求文档/PRD/页面/接口说明生成结构化测试用例
"""

import json
from pathlib import Path
from typing import Any


def generate_test_cases(
    requirement: str,
    axure_data: dict | None = None,
    figma_data: dict | None = None,
    case_type: str = "full"
) -> list[dict]:
    """
    生成测试用例

    参数:
        requirement: 需求内容
        axure_data: Axure 解析数据（可选）
        figma_data: Figma 读取数据（可选）
        case_type: "smoke" 或 "full"

    返回:
        测试用例列表
    """
    # 合并输入数据
    combined_input = {
        "requirement": requirement,
        "axure": axure_data,
        "figma": figma_data,
        "case_type": case_type
    }

    # 构建 prompt
    prompt = _build_prompt(combined_input)

    # 返回 prompt，由 Claude Code 的 Claude 生成用例
    # 注意：此函数不直接调用 AI，而是准备数据
    return _prompt_to_testcases(prompt)


def _build_prompt(combined_input: dict) -> str:
    """构建测试用例生成 prompt"""
    requirement = combined_input.get("requirement", "")
    axure = combined_input.get("axure")
    figma = combined_input.get("figma")
    case_type = combined_input.get("case_type", "full")

    return f"""你是一个专业的测试工程师。请根据以下需求内容生成结构化测试用例。

## 需求内容
{requirement}

## Axure 设计数据
{json.dumps(axure, ensure_ascii=False) if axure else "无"}

## Figma 设计数据
{json.dumps(figma, ensure_ascii=False) if figma else "无"}

## 用例类型
{"冒烟用例" if case_type == "smoke" else "完整用例"}

## 输出格式要求

请以 JSON 数组格式输出测试用例列表，每条用例包含以下字段：
- 平台：只能使用 "客户端" 或 "账服"
- 模块：功能所属模块
- 功能点：具体验证目标
- 前置条件（测试点）：执行前必须满足的状态
- 操作步骤：可执行的操作序列
- 预期结果：明确可验证的结果
- 备注：用例类型标记，如 "【功能测试】【P0】"

## 平台划分规则

- 客户端：页面展示、控件交互、文案提示、跳转、渲染、表单输入、按钮点击、弹窗、列表、禁用态、前端校验
- 账服：接口入参/出参、服务端校验、业务处理、状态变更、写库、查库、缓存、消息、异步任务、错误码、幂等、权限、风控、限流

## 用例设计策略

{"冒烟用例模式：仅覆盖核心主流程、P0 级高风险场景，用例数量精简" if case_type == "smoke" else "完整用例模式：覆盖主流程、异常、边界、状态流转、权限等全部场景"}

请直接返回 JSON 数组，不要包含其他解释文字。"""


def _prompt_to_testcases(prompt: str) -> list[dict]:
    """
    将 prompt 转换为测试用例

    在 Claude Code 环境中，这一步由当前对话的 Claude 完成
    这里返回空列表，实际实现在 Claude Code 中
    """
    # 注意：此函数不直接调用 AI
    # 在 Claude Code 中，prompt 会发送给当前对话的 Claude
    # Claude 返回的 JSON 会被解析为测试用例列表

    # 占位返回
    return []


# 平台划分规则
PLATFORM_RULES = {
    "客户端": [
        "页面展示", "控件交互", "文案提示", "跳转", "渲染",
        "表单输入", "按钮点击", "弹窗", "列表", "禁用态", "前端校验"
    ],
    "账服": [
        "接口入参", "接口出参", "服务端校验", "业务处理", "状态变更",
        "写库", "查库", "缓存", "消息", "异步任务", "错误码",
        "幂等", "权限", "风控", "限流"
    ]
}


def determine_platform(feature_description: str) -> str:
    """
    根据功能描述判断平台类型

    参数:
        feature_description: 功能描述

    返回:
        "客户端" 或 "账服"
    """
    desc_lower = feature_description.lower()

    # 客户端关键词
    client_keywords = ["页面", "展示", "交互", "提示", "跳转", "渲染", "按钮", "弹窗", "列表"]
    for keyword in client_keywords:
        if keyword in desc_lower:
            return "客户端"

    # 账服关键词
    server_keywords = ["接口", "服务端", "业务处理", "状态", "写库", "缓存", "消息", "权限"]
    for keyword in server_keywords:
        if keyword in desc_lower:
            return "账服"

    # 默认返回账服（保守策略）
    return "账服"
