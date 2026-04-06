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
欢迎使用🐟鲤鱼用例管理生成系统

请告诉我您的需求内容，或从以下选项中选择操作：

▎ 1. 生成测试用例
▎ 2. 补充已有用例
▎ 3. 生成多语言校验 JSON
▎ 4. 仅分析需求，不生成用例
```

---

## 选项 1 响应流程

**第 1 步：用户选择「生成测试用例」时，输出：**

```
请告诉我您想生成的用例类型：

▎ 1. 生成冒烟用例
▎ 2. 生成完整用例
```

**第 2 步：用户选择冒烟/完整用例后，输出：**

```
请提供您的需求内容，可以通过以下方式：

▎ 1. 直接粘贴 需求文档/PRD 文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来抓取网页内容
▎ 4. 提供现有用例，要求补充或分析
```

**第 3 步：收到需求后，根据用户选择的用例类型生成：**

- **冒烟用例**：仅覆盖核心主流程、P0 级高风险场景，用例数量精简
- **完整用例**：覆盖主流程、异常、边界、状态流转、权限等全部场景

**第 4 步：生成测试用例后，输出导出选项：**

```
测试用例已生成，请选择导出方式：

▎ 1. 导出为 Excel 文件并更新索引文件
▎ 2. 仅导出为 Excel 文件

导出后将保存到：testcases/generated/<模块>_<日期>.xlsx
```

## 选项 2 响应流程

**第 1 步：用户选择「补充已有用例」时，读取索引并列出用例：**

```bash
# 读取 testcases/testcase-index.json，按模块分组展示
python3 -c "
import json
with open('testcases/testcase-index.json', 'r') as f:
    data = json.load(f)
entries = data.get('entries', [])
# 按 module 分组
modules = {}
for e in entries:
    m = e.get('module', '其他')
    if m not in modules:
        modules[m] = []
    modules[m].append(e)
# 输出
for m, es in sorted(modules.items()):
    print(f'【{m}】({len(es)}个)')
    for i, e in enumerate(es, 1):
        print(f'  {i}. {e.get(\"title\", \"\")} [{e.get(\"format\", \"\")}]')
"
```

**输出格式：**

```
请选择要补充的模块：

【英雄技能】(3 个)
  1. 英雄技能升级功能 [xlsx] - 2026-04-06
  2. 英雄技能解锁条件 [xlsx] - 2026-04-01
  3. 英雄技能特效展示 [md] - 2026-03-28

【装备系统】(2 个)
  1. 装备合成规则 [xlsx] - 2026-04-05
  2. 装备强化功能 [xlsx] - 2026-04-02

请输入模块编号和用例编号（如：1-2 表示英雄技能 - 第 2 个）：
```

**第 2 步：用户选择用例后，输出：**

```
已选择：英雄技能 - 英雄技能升级功能

请提供您需要补充的内容，可以通过以下方式：

▎ 1. 直接粘贴 新增需求/变更内容 文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来抓取网页内容
▎ 4. 描述需要补充的测试场景

补充后将：
- 追加到原 Excel 文件末尾
- 新增用例行标黄标识
- 更新索引条目的 updated_at
```

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
