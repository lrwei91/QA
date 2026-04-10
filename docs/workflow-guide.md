# QA Workflows 工作流指南

## 概述

QA Workflows 是基于 LangGraph 的流程编排层，用于 orchestrate QA 测试用例生成工作流。它位于用户交互层（`/qa` 命令）和 Skill 层之间。

### 架构图

```
用户输入 (/qa)
       ↓
LangGraph Workflow ← 本模块
       ↓
Skill 层 (testcase-generate, figma-reader, etc.)
       ↓
Python Scripts (xlsx_fill, upsert_index, etc.)
```

---

## 快速开始

### 导入

```python
from workflows import QAWorkflowState, build_qa_workflow
```

### 基本用法

```python
# 构建工作流
workflow = build_qa_workflow()

# 定义初始状态
initial_state: QAWorkflowState = {
    "workflow_type": "generate",
    "case_type": "smoke",  # 或 "full"
    "input_content": "你的需求内容",
    "input_source": "text",  # 或 "file", "axure_dir"
    "errors": [],
    "retry_count": 0,
}

# 运行工作流
result = workflow.invoke(initial_state)

# 访问结果
test_cases = result.get("test_cases", [])
excel_path = result.get("excel_path")
errors = result.get("errors", [])
```

---

## 状态字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `workflow_type` | `"generate"/"augment"/"analyze"/"i18n"` | 工作流类型 |
| `case_type` | `"smoke"/"full"` | 用例类型（仅 generate 模式） |
| `input_content` | `str` | 输入内容 |
| `input_source` | `"text"/"file"/"url"/"axure_dir"` | 输入来源 |
| `figma_url` | `str` | Figma URL |
| `axure_data` | `dict` | Axure 解析结果 |
| `figma_data` | `dict` | Figma 读取结果 |
| `test_cases` | `list[dict]` | 测试用例 |
| `i18n_json` | `dict` | 多语言 JSON |
| `excel_path` | `str` | Excel 路径 |
| `errors` | `list` | 错误列表 |

---

## 工作流图

### Generate Workflow

```
parse_input
    ↓
[has figma_url?] ──Yes──→ read_figma ──┐
    │                                   ↓
    No                           generate_test_cases
    └───────────────────────────────────┘
                                      ↓
                              [has i18n?] ──Yes──→ check_i18n
                                      │                 ↓
                                      No                │
                                      └────────→ export_excel → END
```

### Augment Workflow (补充已有用例)

```
load_existing_cases → analyze_gaps → generate_augment_cases → append_to_excel → END
```

### Analyze Workflow (需求分析)

```
parse_input → analyze_requirements → output_analysis → END
```

---

## 节点函数

| 节点 | 函数 | 职责 |
|------|------|------|
| 解析输入 | `parse_input()` | 读取文件、解析 Axure HTML、处理文本 |
| 读取 Figma | `read_figma()` | 调用 Figma REST API，提取文案/组件/状态 |
| 生成用例 | `generate_test_cases()` | 准备 prompt，由 Claude 生成测试用例 |
| 多语言校验 | `check_i18n()` | 多语言数据提取、校验、JSON 生成 |
| 导出 Excel | `export_excel()` | 导出 Excel 文件，更新索引 |

---

## 条件分支

| 函数 | 判断 |
|------|------|
| `should_read_figma()` | 是否有 Figma URL |
| `has_i18n()` | 是否检测到多语言 |
| `has_test_cases()` | 是否生成了用例 |

---

## 在 Claude Code 中使用

### 重要说明

**本工作流运行在 Claude Code 环境中，不需要配置 `ANTHROPIC_API_KEY`。**

- **LangGraph 工作流**：负责流程编排、状态流转、条件分支、脚本调用
- **Claude（当前对话）**：负责需要智能的任务（生成测试用例、分析需求等）
- **节点函数**：只负责数据处理、脚本调用、文件操作

### 为什么不需要 ANTHROPIC_API_KEY？

在 Claude Code 环境中：
1. 你已经在使用 Claude（当前对话的 AI）
2. LangGraph 工作流是 Python 代码，由 Claude Code 执行
3. 当需要 AI 能力时，直接让当前对话的 Claude 处理即可
4. 不需要再通过 API 调用另一个 Claude

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │              你（用户）对话的 Claude                │  │
│  │              ↑                                    │  │
│  │              │ 需要 AI 处理                         │  │
│  │              ↓                                    │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │        LangGraph Workflows (Python)         │ │  │
│  │  │  - parse_input (读取文件/解析 Axure)         │ │  │
│  │  │  - read_figma (调用 Figma API)              │ │  │
│  │  │  - generate_test_cases (准备 prompt)        │ │  │
│  │  │  - check_i18n (多语言校验)                   │ │  │
│  │  │  - export_excel (导出 Excel)                │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 使用方式

#### 方式 1：通过 `/qa` 命令（推荐）

`/qa` 命令已经集成了工作流调用逻辑，你只需要：
1. 选择操作类型
2. 提供需求内容
3. Claude 会自动使用工作流处理

#### 方式 2：手动调用工作流

```python
from workflows import QAWorkflowState, build_qa_workflow

# 构建工作流
workflow = build_qa_workflow()

# 定义初始状态
initial_state: QAWorkflowState = {
    "workflow_type": "generate",
    "case_type": "smoke",
    "input_content": "你的需求内容",
    "input_source": "text",
    "errors": [],
    "retry_count": 0,
}

# 运行工作流（到 generate_test_cases 节点）
result = workflow.invoke(initial_state)

# 获取 prompt，让 Claude 生成测试用例
prompt = result.get("_prompt_for_claude", "")

# 将 prompt 发送给 Claude（当前对话）
# Claude 会返回测试用例 JSON

# 解析 Claude 返回的 JSON，更新 state
import json
test_cases = json.loads(claude_response)
result["test_cases"] = test_cases

# 继续运行工作流到 export_excel
final_result = workflow.invoke(result)
```

---

## 环境变量

| 变量 | 用途 | 必需 |
|------|------|------|
| `FIGMA_ACCESS_TOKEN` | 调用 Figma REST API | 读取 Figma 时需要 |

**注意：** `ANTHROPIC_API_KEY` **不需要** 配置！

---

## 测试

```bash
cd test-case-generator
python3 -c "from workflows import build_qa_workflow; print('OK')"
```

---

## 完整示例

### 示例 1：生成测试用例

```python
#!/usr/bin/env python3
"""
在 Claude Code 中使用 QA Workflows 的完整示例
"""

from workflows import QAWorkflowState, build_qa_workflow
from workflows.qa_nodes import generate_test_cases, export_excel
import json

def main():
    # 1. 构建工作流
    workflow = build_qa_workflow()

    # 2. 初始状态
    state: QAWorkflowState = {
        "workflow_type": "generate",
        "case_type": "full",
        "input_content": """
        需求：用户登录功能
        1. 用户可以通过手机号和密码登录
        2. 手机号必须是 11 位中国手机号
        3. 密码长度 6-20 位，必须包含字母和数字
        4. 登录成功后跳转到首页
        """,
        "input_source": "text",
        "errors": [],
    }

    # 3. 运行到 parse_input
    state = workflow.get_node("parse_input")(state)

    # 4. 运行到 generate_test_cases（准备 prompt）
    state = workflow.get_node("generate_test_cases")(state)

    # 5. 获取 prompt，让 Claude 生成测试用例
    prompt = state["_prompt_for_claude"]
    print("Prompt for Claude:", prompt)

    # 【在 Claude Code 中】
    # 这里应该将 prompt 发送给当前对话的 Claude
    # Claude 会返回测试用例 JSON

    # 6. 假设 Claude 返回了测试用例
    claude_response = """
    [
        {
            "平台": "账服",
            "模块": "认证中心",
            "功能点": "手机号登录",
            "前置条件（测试点）": "用户已注册",
            "操作步骤": "1.输入手机号 2.输入密码 3.点击登录",
            "预期结果": "登录成功，返回 token",
            "备注": "【功能测试】【P0】"
        }
    ]
    """

    test_cases = json.loads(claude_response)
    state["test_cases"] = test_cases

    # 7. 继续运行工作流，导出 Excel
    state = workflow.get_node("export_excel")(state)

    print("Excel path:", state.get("excel_path"))

if __name__ == "__main__":
    main()
```

### 示例 2：补充已有用例

```python
from workflows import build_augment_workflow

workflow = build_augment_workflow()

state: QAWorkflowState = {
    "workflow_type": "augment",
    "_target_module": "认证中心",
    "input_content": "新增手机验证码登录...",
    "errors": [],
}

result = workflow.invoke(state)
# result 包含补充的用例
```

### 示例 3：需求分析

```python
from workflows import build_analyze_workflow

workflow = build_analyze_workflow()

state: QAWorkflowState = {
    "workflow_type": "analyze",
    "input_content": "PRD 文档内容...",
    "errors": [],
}

result = workflow.invoke(state)
# result 包含分析结果
```

---

## 重试机制

### 使用方式

```python
from workflows.utils import with_retry

@with_retry(max_retries=3, delay=1.0)
def my_node(state):
    # 可能失败的操作
    pass
```

### 已应用重试的节点

| 节点 | 重试次数 | 延迟 |
|------|----------|------|
| `parse_input_with_retry` | 3 | 1s |
| `read_figma_with_retry` | 3 | 2s |
| `export_excel_with_retry` | 2 | 1s |

---

## 并行执行

### 使用方式

```python
from workflows.utils import ParallelExecutor

executor = ParallelExecutor()
executor.add_task(parse_input, state)
executor.add_task(read_figma, state)  # 并行执行

result = executor.run(state)
```

### 并行节点

`parse_input_parallel` - 同时解析输入和读取 Figma

---

## 核心设计原则

### Skill = 能力说明书 ✅

- SKILL.md 文档定义了每个技能的职责、输入输出、行为规则
- 人类可以阅读 SKILL.md 理解系统能力
- AI（当前对话的 Claude）可以参照 SKILL.md 执行任务

### LangGraph = 流程编排器 ✅

- `QAWorkflowState` 定义了统一的状态结构
- 节点函数定义了每个步骤的执行逻辑（**纯 Python**）
- `StateGraph` 定义了流程走向和条件分支
- 支持重试、并行、复杂条件判断

### 分层协作 ✅

```
用户交互层 (/qa 命令)
       ↓
Claude（当前对话）← AI 能力提供者
       ↑
LangGraph 编排层 ← Python 流程控制
       ↓
Python 脚本层 ← 确定性任务执行
```

---

## 节点函数职责

| 节点 | 职责 | 需要 AI 吗 |
|------|------|----------|
| `parse_input` | 读取文件、解析 Axure HTML | ❌ |
| `read_figma` | 调用 Figma REST API | ❌ |
| `generate_test_cases` | **准备 prompt**（给 Claude 用） | ❌ |
| `check_i18n` | 多语言数据提取、校验 | ❌ |
| `export_excel` | 导出 Excel 文件 | ❌ |

### `generate_test_cases` 的真正实现

```python
def generate_test_cases(state: QAWorkflowState) -> QAWorkflowState:
    """
    生成测试用例 - 准备阶段

    【重要】此节点不调用 AI，而是：
    1. 合并输入数据（需求 + Axure + Figma）
    2. 构建结构化的 prompt
    3. 将 prompt 存储在 state 中
    4. 由 Claude Code 的 Claude 生成用例
    """
    # 合并数据
    combined_input = {...}

    # 构建 prompt
    prompt = build_testcase_generation_prompt(combined_input)

    # 存储到 state，供 Claude 使用
    return {
        **state,
        "_prompt_for_claude": prompt,
        "_i18n_detected": detect_i18n(...)
    }
```

### 在 Claude Code 中的使用流程

```
1. 运行工作流 → parse_input → generate_test_cases
                      ↓
              state["_prompt_for_claude"]
                      ↓
2. Claude 读取 prompt，生成测试用例 JSON
                      ↓
3. 解析 JSON，更新 state["test_cases"]
                      ↓
4. 继续运行工作流 → check_i18n → export_excel
```

---

## 总结

| 组件 | 职责 | 运行环境 |
|------|------|----------|
| LangGraph 工作流 | 流程编排、状态管理 | Python |
| 节点函数 | 数据处理、脚本调用 | Python |
| Claude | 测试用例生成、需求分析 | 当前对话 |

**核心原则：**
- Python 负责确定性的、可编程的任务
- Claude 负责需要智能的、创造性的任务
- 两者协作，发挥各自优势

---

## 文件结构

```
engine/
└── workflows/
    ├── __init__.py              # 包导出
    ├── qa_state.py              # 状态定义
    ├── qa_nodes.py              # 节点函数
    ├── qa_workflow.py           # 工作流构建
    └── utils.py                 # 工具函数（重试、并行）
```
