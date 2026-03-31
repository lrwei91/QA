---
name: qa
description: QA 测试用例生成器入口 - 分析需求文档、PRD、接口说明、现有用例和模板，自动生成结构化测试用例
---

# QA Test Case Generator

**完整技能定义：** [`test-case-generator/SKILL.md`](test-case-generator/SKILL.md)

本文件是 `/qa` 命令的快速入口，详细规则请阅读 SKILL.md。

---

## 欢迎语

每次执行 `/qa` 时，首先输出：

```
请提供需求内容

您可以通过以下方式提供需求：
1. 直接粘贴 需求文档/PRD 文本
2. 提供文件路径，我来读取
3. 提供 URL，我来抓取网页内容
4. 提供现有用例，要求补充或分析

收到需求后，我会：
1. 分析需求类型和关键要素
2. 匹配主模块
3. 生成结构化测试用例
4. 支持导出 Excel 或多语言 JSON

请告诉我您的需求内容，或从以下选项中选择操作：

▎ 请选择要执行的操作：
▎ 1. 生成测试用例
▎ 2. 补充已有用例
▎ 3. 生成多语言校验 JSON
▎ 4. 仅分析需求，不生成用例
```

---

## 快速参考

### 选项说明

| 选项 | 功能 | 详细说明 |
|------|------|---------|
| 1 | 生成测试用例 | SKILL.md "选项 1：生成测试用例" |
| 2 | 补充已有用例 | SKILL.md "选项 2：补充已有用例" |
| 3 | 生成多语言 JSON | SKILL.md "选项 3：生成多语言校验 JSON" |
| 4 | 仅分析需求 | SKILL.md "选项 4：仅分析需求" |

### 核心规则

- **平台拆分**：SKILL.md "Platform split rules"
- **测试设计**：SKILL.md "Test design baseline"
- **输出模板**：SKILL.md "Output contract"
- **Excel 导出**：SKILL.md "Template handling and export"
- **质量检查**：SKILL.md "Quality checks"

### 工具脚本

| 用途 | 命令 |
|------|------|
| 索引校验 | `python3 test-case-generator/scripts/validate_index.py` |
| 用例索引 | `python3 test-case-generator/scripts/validate_testcase_index.py` |
| 多语言 JSON 校验 | `python3 test-case-generator/scripts/validate_i18n_json.py` |
| 模板生成 | `python3 test-case-generator/scripts/generate_testcase_from_template.py` |
| 清理过期文件 | `python3 test-case-generator/scripts/cleanup_testcase_store.py --dry-run` |
| 索引差异比较 | `python3 test-case-generator/scripts/diff_testcase_indexes.py` |
| 覆盖率报告 | `python3 test-case-generator/scripts/export_testcase_report.py` |

---

## 环境检查（自动执行）

```bash
if ! which python3 >/dev/null 2>&1; then
  echo "ERROR: Python3 not found. Please install Python 3."
  return 1
fi

python3 -c "import json, openpyxl, pandas" 2>/dev/null \
  && echo "DEPS_OK" \
  || pip install openpyxl pandas
```

---

## 错误速查

| 错误 | 处理 |
|------|------|
| 模块匹配歧义 | 展示候选模块列表，用 AskUserQuestion 确认 |
| 需求类型不明确 | 基于现有内容做最合理匹配 |
| 多语言不完整 | 输出缺失语言清单 |
| 历史用例索引不存在 | 自动创建仓位和索引骨架 |
| Excel 导出依赖缺失 | 自动 `pip install openpyxl pandas` |
| 索引文件校验失败 | 见上方工具脚本 |

---

**详细流程、测试设计规则、输出规范、质量检查清单等，请阅读 [`test-case-generator/SKILL.md`](test-case-generator/SKILL.md)**
