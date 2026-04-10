---
name: qa
description: QA 测试用例生成器入口 - 分析需求文档、PRD、接口说明、现有用例和模板，自动生成结构化测试用例；支持 Figma 设计稿读取、Axure HTML 解析补充 UI 细节
---

# QA Test Case Generator

**完整技能定义：**
- [`testcase-generate`](../engine/skills/testcase-generate/SKILL.md) - 生成测试用例
- [`testcase-augment`](../engine/skills/testcase-augment/SKILL.md) - 补充已有用例
- [`testcase-analyze`](../engine/skills/testcase-analyze/SKILL.md) - 仅分析需求
- [`testcase-i18n`](../engine/skills/testcase-i18n/SKILL.md) - 多语言 JSON 校验
- [`testcase-format`](../engine/skills/testcase-format/SKILL.md) - Excel 导出与索引更新
- [`figma-reader`](../engine/skills/figma-reader/SKILL.md) - Figma 设计稿读取
- [`axure-parser`](../engine/skills/axure-parser/SKILL.md) - Axure HTML 解析

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
▎ 2. 提供文件路径，我来读取 (.rp 导出 HTML/.md/.txt)
▎ 3. 提供 URL，我来抓取网页内容
▎ 4. 提供 Axure 导出 HTML 目录

说明：
- 选项 2：支持 Axure 导出的单个 HTML 文件
- 选项 4：支持 Axure 导出的完整目录（推荐）
```

**第 3 步：收到需求后，输出：**

```
▎ 需求已接收

[如检测到 Axure HTML 数据]
▎ 检测到 Axure HTML 数据，已提取:
  - 页面：XX 个
  - 元件：XX 个
  - 注释：XX 条

是否需要提供 Figma 设计稿链接以补充 UI 细节？

Figma 设计稿可以帮助识别:
- 页面文案和按钮文本
- 组件层级和布局关系
- 视觉状态和交互反馈

▎ 1. 提供 Figma 文件 URL 和 Frame 名称
▎ 2. 跳过，仅用需求文档生成
```

**第 3.5 步：模块确认（必须）**

```
▎ 需求已解析，检测到以下关键词：[xxx, xxx, xxx]

最匹配的模块可能是（请选择或自定义）：

▎ 1. {模块 1 名称} ({module_id}) - 匹配度 XX%
   - 触发词：xxx, xxx
   - 领域：{domain}
   - 参考文档：engine/references/domain-knowledge/{domain}.md

▎ 2. {模块 2 名称} ({module_id}) - 匹配度 XX%
   ...

▎ 3. {模块 3 名称} ({module_id}) - 匹配度 XX%
   ...

▎ 4. 自定义输入模块名称

注意：
- 模块归属将决定测试用例的组织结构和复用策略
- 如现有模块都不匹配，请选择「自定义输入」
- 新活动类型将补充到领域知识文档中
```

**用户确认模块后，检查领域知识文件：**

1. 读取对应 `domain-knowledge/{domain}.md` 文件
2. 检查是否已存在该活动/功能类型的说明
3. 如不存在 → 新增模块说明到文件
4. 如已存在 → 判断是增量更新还是功能修改

**领域知识补充规则：**

```markdown
新增模块说明格式（以充值活动为例）：

### 2.X 充值活动
- 活动类型：首充活动、每日充值、累计充值、阶梯返利、复充返利
- 充值档位：单笔满额、累计满额、多档位选择
- 返利类型：即时返利、手动领取、定时发放
- 返利形式：金币、优惠券、抽奖机会、道具
- 限制条件：每日次数限制、总参与次数、玩家资格限制
- 叠加规则：可与其他活动叠加、互斥规则

高风险测试点：
- 返利资格判定（首充/每日/累计）
- 返利发放、次数限制校验
- 活动配置（时间/档位/奖励）
- 与其他活动互斥逻辑
- 叠加规则验证
```

**第 4 步（可选）：用户提供 Figma 链接后**

调用 `figma-reader` 技能读取设计稿：
- 使用 Figma REST API `/v1/files/{file_id}/nodes?ids={node_id}` 读取指定节点
- 提取文案数据
- 提取组件结构
- 提取交互说明

**注意：** 必须使用带 `node-id` 参数的链接，例如：
```
https://www.figma.com/design/TTCIlEUeIyxXWG9pMIkOp9/web5?node-id=25246:54081
```

**第 5 步：生成测试用例**

根据用户选择的用例类型生成：
- **冒烟用例**：仅覆盖核心主流程、P0 级高风险场景，用例数量精简
- **完整用例**：覆盖主流程、异常、边界、状态流转、权限等全部场景

如提供 Axure HTML，生成 UI 验证用例：
- 页面元素展示验证
- 元件状态验证
- 交互跳转验证
- 约束条件验证

如提供 Figma 设计稿，额外生成：
- 视觉状态验证
- 设计稿一致性验证

**输出要求：**
- 简洁提示即可，不得在命令行逐条输出所有用例详情
- 仅展示：用例总数、客户端用例数、账服用例数、覆盖的功能点清单

**第 6 步：生成测试用例后，输出导出选项：**

```
测试用例已生成，请选择导出方式：

▎ 1. 导出为 Excel 文件并更新索引文件
   - 使用 xlsx_fill_testcase_template.py 填充模板
   - 使用 upsert_testcase_index.py 更新索引

▎ 2. 仅导出为 Excel 文件
   - 使用 xlsx_fill_testcase_template.py 填充模板
   - 不更新索引文件

导出后将保存到：outputs/generated/<模块>/<用例名称>.xlsx

注意：必须由用户选择后才能执行导出，不得自动执行。
```

**第 7 步：用户选择导出方式后，调用 `testcase-format` skill 执行 Excel 导出**

- 用户选择选项 1 → 调用 testcase-format，参数包含 `update_index=true`
- 用户选择选项 2 → 调用 testcase-format，参数包含 `update_index=false`
- 使用 `xlsx_fill_testcase_template.py` 脚本填充模板
- 如用户选择更新索引，使用 `upsert_testcase_index.py` 脚本更新索引
- 确保样式与 `templates/testcase_template.xlsx` 模板一致
- 不得手动创建 Excel 文件

---

## 选项 2 响应流程

**第 1 步：用户选择「补充已有用例」时，读取索引并列出用例：**

```bash
# 读取 outputs/testcase-index.json，按模块分组展示
python3 -c "
import json
with open('outputs/testcase-index.json', 'r') as f:
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
        print(f'  {i}. {e.get(\"title\", \"\")} [{e.get(\"format\", \"\")}] - {e.get(\"updated_at\", \"\")[:10]}')
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

---

## 选项 3 响应流程

**用户选择「生成多语言校验 JSON」时，输出：**

```
请提供多语言文案内容，可以通过以下方式：

▎ 1. 直接粘贴 多语言对照表/JSON 文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来抓取网页内容

标准语言集合：en-us, id-id, pt-pt, es-es, bn-bn, tr-tr, fp-fp
```

**收到内容后：**
- 检查语言完整性
- 生成多语言校验 JSON
- 更新多语言索引

---

## 选项 4 响应流程

**用户选择「仅分析需求」时，输出：**

```
请提供您的需求内容，可以通过以下方式：

▎ 1. 直接粘贴 需求文档/PRD 文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来抓取网页内容

分析后将输出：
- 模块拆分
- 风险等级评估
- 测试点清单（非完整用例）
- 关联影响模块
```

---

## 选项说明

| 选项 | 对应 Skill | 功能 |
|------|-----------|------|
| 1 | `testcase-generate` + `figma-reader` | 从需求生成测试用例（可选 Figma 补充） |
| 2 | `testcase-augment` | 补充已有用例 |
| 3 | `testcase-i18n` | 生成多语言校验 JSON |
| 4 | `testcase-analyze` | 仅分析需求 |

**工程化处理（所有选项都可能涉及）：**
- `testcase-format` - Excel 导出与索引更新

---

## 核心规则

- **平台拆分**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Platform split rules
- **测试设计**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Test design baseline
- **输出模板**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Output contract
- **增量补充**：[testcase-augment/SKILL.md](../engine/skills/testcase-augment/SKILL.md) 核心约束
- **多语言校验**：[testcase-i18n/SKILL.md](../engine/skills/testcase-i18n/SKILL.md) 校验规则
- **Figma 读取**：[figma-reader/SKILL.md](../engine/skills/figma-reader/SKILL.md) Figma 设计稿读取

---

## 工具脚本

| 用途 | 命令 |
|------|------|
| 索引校验 | `python3 engine/scripts/validate_index.py` |
| 用例索引 | `python3 engine/scripts/validate_testcase_index.py` |
| 多语言 JSON 校验 | `python3 engine/scripts/validate_i18n_json.py` |
| 模板生成 | `python3 engine/scripts/generate_testcase_from_template.py` |
| 清理过期文件 | `python3 engine/scripts/cleanup_testcase_store.py --dry-run` |
| 索引差异比较 | `python3 engine/scripts/diff_testcase_indexes.py` |
| 覆盖率报告 | `python3 engine/scripts/export_testcase_report.py` |
| Excel 填充 | `python3 engine/scripts/xlsx_fill_testcase_template.py` |
| 追加用例 | `python3 engine/scripts/xlsx_append_and_highlight.py` |
| 更新索引 | `python3 engine/scripts/upsert_testcase_index.py` |

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

## 项目文档

- [CLAUDE.md](../CLAUDE.md) - 项目总览与核心原则
- [engine/skills/](../engine/skills/) - Skills 目录

**详细流程、测试设计规则、输出规范、质量检查清单等，请阅读各 Skill 文档**
