---
name: qa
description: QA 工作流编排入口 - 分析需求文档、PRD、接口说明、现有用例和模板，按场景分发到测试用例生成、补充、知识库管理、同步快照、禅道集成等子能力
---

# QA Workflow Entry

**子能力编排入口：**
- [`testcase-generate`](../engine/skills/testcase-generate/SKILL.md) - 生成测试用例
- [`testcase-augment`](../engine/skills/testcase-augment/SKILL.md) - 补充已有用例
- [`testcase-format`](../engine/skills/testcase-format/SKILL.md) - Excel 导出与索引更新
- [`figma-reader`](../engine/skills/figma-reader/SKILL.md) - Figma 设计稿读取
- [`axure-parser`](../engine/skills/axure-parser/SKILL.md) - Axure HTML 解析
- [`knowledge`](../knowledge/SKILL.md) - 知识库管理（消化/查询/结晶）
- [`zentao`](~/.agents/skills/zentao/SKILL.md) - 禅道集成（bug/任务/需求/测试用例）

---

## 欢迎语

每次执行 `/qa` 时，首先输出：

```
欢迎使用🐟鲤鱼用例管理生成系统

请告诉我您的需求内容，或从以下选项中选择操作：

▎ 1. 生成测试用例
▎ 2. 补充已有用例
▎ 3. 知识库管理
▎ 4. 同步已生成用例
▎ 5. 禅道集成
```

---

## 选项 5：禅道集成响应流程

**用户选择「禅道集成」时，输出：**

```
请选择禅道操作：

▎ 1. 登录禅道
▎ 2. 查看当前账号 (whoami)
▎ 3. 连接测试 (self-test)
▎ 4. 查看产品列表
▎ 5. 查看 Bug 列表
▎ 6. 查看我的 Bug
▎ 7. Bug 统计报表
▎ 8. 查看测试用例
▎ 9. 查看任务/执行
▎ 10. 自定义命令

禅道配置：
- URL: $ZENTAO_URL
- 账号：$ZENTAO_ACCOUNT
```

**子选项 1：登录禅道**

```bash
# 方式 1：使用 .env 文件配置（推荐）
# 在项目根目录创建 .env 文件，配置以下变量：
# - ZENTAO_URL
# - ZENTAO_ACCOUNT
# - ZENTAO_PASSWORD
source .env && zentao login --zentao-url="$ZENTAO_URL" --zentao-account="$ZENTAO_ACCOUNT" --zentao-password="$ZENTAO_PASSWORD"

# 方式 2：直接命令行参数
zentao login --zentao-url="..." --zentao-account="..." --zentao-password="..."
```

**子选项 2-3：验证连接**

```bash
zentao whoami    # 查看当前账号
zentao self-test # 测试连接是否正常
```

**子选项 4：查看产品列表**

```bash
zentao products list [--page N] [--limit N] [--json]
```

**子选项 5：查看 Bug 列表**

```
请选择查看方式：

▎ 1. 按产品查看 Bug
   zentao bugs list --product <id> [--page N] [--limit N]

▎ 2. 查看我的 Bug
   zentao bugs mine [--scope ...] [--status ...]

▎ 3. 查看指定状态的 Bug
   zentao bugs list --product <id> --status active|resolved|closed
```

**子选项 6：查看我的 Bug**

```bash
zentao bugs mine --status active --include-details [--json]
```

**子选项 7：Bug 统计报表**

```
请选择统计维度：

▎ 1. 按产品统计
   zentao bugs stats --product-ids 1,2 --group-by product

▎ 2. 按人员统计
   zentao bugs stats --product-ids 1,2 --group-by person

▎ 3. 指定时间范围
   zentao bugs stats --product-ids 1,2 --from 2026-01-01 --to 2026-04-15
```

**子选项 8：查看测试用例**

```bash
# 查看测试用例
zentao testcases list --product <id> [--json]

# 查看测试任务
zentao testtasks list [--json]

# 查看测试套件
zentao testsuites list --product <id> [--json]
```

**子选项 9：查看任务/执行**

```bash
# 查看任务列表
zentao tasks list --execution <id> [--json]

# 查看执行列表
zentao executions list [--json]

# 查看项目列表
zentao projects list [--json]
```

**子选项 10：自定义命令**

支持所有 zentao CLI 命令，用户可以直接指定命令执行。

---

## 禅道与测试用例生成集成

**从禅道需求生成测试用例：**

1. 从禅道获取需求/故事
   ```bash
   zentao stories list --product <id> [--json]
   zentao story get <id>
   ```

2. 将需求内容传递给 testcase-generate 生成测试用例

3. 生成的测试用例可导出为 Excel 或同步回禅道（通过 testcases create）

**从禅道 Bug 补充测试用例：**

1. 从禅道获取 Bug 详情
   ```bash
   zentao bug get <id>
   zentao bugs mine --status resolved
   ```

2. 分析 Bug 根因，补充相关测试用例到 testcase-augment

3. 更新到 Excel 并同步回禅道

---

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

**第 7 步：用户选择导出方式后，调用 `testcase-format` 子能力执行 Excel 导出**

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

**用户选择「知识库管理」时，输出：**

```
请选择知识库管理操作：

▎ 1. 消化素材 (ingest) - 将链接/文件/文本整理成 wiki 页面
▎ 2. 查询知识 (query) - 基于已有知识库回答问题
▎ 3. 深度综合 (digest) - 跨素材深度分析，生成综述/对比表/时间线
▎ 4. 健康检查 (lint) - 检测孤立页面、断链、矛盾信息
▎ 5. 知识结晶 (crystallize) - 将有价值的对话沉淀为知识库页面
▎ 6. 查看状态 (status) - 查看知识库当前状态和统计

知识库位置：knowledge/
```

**子选项 1：消化素材**

```
请提供要消化的素材，支持以下方式：

▎ 1. 直接粘贴 链接/文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来提取网页内容

支持的素材类型：
- 网页文章、微信公众号、YouTube 视频
- X/Twitter、知乎、小红书（手动粘贴）
- PDF、Markdown、纯文本文件

注意：在开始分析前，请确认素材中不包含敏感信息
（手机号、身份证号、API 密钥、明文密码等）
```

处理流程：
1. 隐私自查确认
2. 提取素材内容
3. 保存到 `knowledge/raw/` 对应目录
4. 缓存检查（跳过未变化的素材）
5. Step 1：结构化分析（JSON 格式）
6. Step 2：生成 wiki 页面（entities/topics/sources）
7. 更新 index.md 和 log.md

**子选项 2：查询知识**

```
请输入要查询的关键词或问题：

例如：
- "英雄技能升级的相关测试点"
- "充值活动的返利规则"
- "什么是 [[实体名]]"
```

处理流程：
1. 在 knowledge/wiki/ 下搜索相关页面
2. 综合回答用户问题
3. 引用来源（[[页面名]] 格式）
4. 如引用≥3 个来源，提示是否保存为持久化页面

**子选项 3：深度综合**

```
请选择深度分析类型：

▎ 1. 深度报告 - 全面总结某个主题
▎ 2. 对比表 - 对比多个对象/概念
▎ 3. 时间线 - 按时间顺序梳理事件

请输入主题和分析类型，例如：
- "给我讲讲充值活动"
- "对比一下首充活动和每日充值"
- "整理一下运营活动的时间线"
```

处理流程：
1. 搜索相关 wiki 页面
2. 深度阅读所有相关材料
3. 生成结构化报告（保存到 knowledge/wiki/synthesis/）
4. 更新 index.md 和 log.md

**子选项 4：健康检查**

```
开始知识库健康检查...

检查范围：
- 机械检查：孤立页面、断链、索引一致性
- AI 判断：矛盾信息、交叉引用缺失、置信度报告

检查完成后将输出修复建议。
```

处理流程：
1. 运行 `bash knowledge/scripts/lint-runner.sh <wiki_root>`
2. AI 判断矛盾信息、置信度
3. 输出报告并询问是否自动修复

**子选项 5：知识结晶**

```
请提供要结晶化的对话内容或主题：

可以：
- 直接粘贴文字
- 引用当前对话的某段内容
- 描述要记录的核心观点

结晶化后将保存到：knowledge/wiki/synthesis/sessions/
```

处理流程：
1. 提取核心洞见（3-5 条）
2. 提取关键决策和原因
3. 生成结晶页面（参考 synthesis-template.md）
4. 更新 log.md

**子选项 6：查看状态**

统计知识库状态，输出：
- 各分类页面数量（entities/topics/sources/synthesis）
- 最近活动（log.md 最后 5 条）
- 外挂状态（adapter-state.sh summary-human）

---

## 选项 4 响应流程

**用户选择「同步已生成用例」时，输出：****

```
请选择同步方式：

▎ 1. 同步单个用例文件
   - 选择要同步的 Excel 文件
   - 读取最新内容，更新快照和主题页

▎ 2. 同步全部用例文件
   - 扫描所有 Excel 文件
   - 批量更新快照和主题页

▎ 3. 查看快照历史
   - 查看指定用例的快照历史记录
   - 比较不同版本的差异
```

**第 2 步：用户选择同步方式后**

**选项 1（同步单个文件）**：
```
请选择要同步的 Excel 文件：

▎ 1. [复充返利活动.xlsx](outputs/generated/运营活动/复充返利活动.xlsx) - 22 条
▎ 2. [幸运卡片（集福活动）- 完整用例.xlsx](outputs/generated/运营活动/幸运卡片/) - 多条
...

或提供文件路径：
```

**选项 2（同步全部文件）**：
```
开始同步所有 Excel 文件...

✓ 复充返利活动.xlsx - 快照已保存，主题页已更新
✓ 幸运卡片（集福活动）.xlsx - 快照已保存，主题页已更新
...

同步完成：共 X 个文件
```

**选项 3（查看快照历史）**：
```
请选择要查看的用例：

▎ 1. 复充返利活动 - 3 个快照
▎ 2. 幸运卡片（集福活动）- 2 个快照
...

或使用命令查看：
# 查看指定文件的快照历史
python3 engine/scripts/view_snapshot_history.py outputs/generated/运营活动/复充返利活动.xlsx

# 查看指定模块的所有快照
python3 engine/scripts/view_snapshot_history.py --module 运营活动

# 查看所有模块的快照
python3 engine/scripts/view_snapshot_history.py --all

# 比较两个快照的差异
python3 engine/scripts/view_snapshot_history.py --compare outputs/snapshots/运营活动/复充返利活动/2026-04-14T20-05-54.json outputs/snapshots/运营活动/复充返利活动/2026-04-15T10-00-00.json

选择后将显示：
- 快照时间线
- 版本差异比较
- 测试点变化
```

**第 3 步：执行同步**

调用 `sync_testcase_snapshot.py` 脚本：
```bash
# 同步单个文件
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/<模块>/<用例名称>.xlsx

# 同步全部文件
python3 engine/scripts/sync_testcase_snapshot.py --all
```

---

## 选项说明

| 选项 | 对应 Skill | 功能 |
|------|-----------|------|
| 1 | `testcase-generate` + `figma-reader` | 从需求生成测试用例（可选 Figma 补充） |
| 2 | `testcase-augment` | 补充已有用例 |
| 3 | `knowledge` | 知识库管理（消化/查询/结晶/健康检查） |
| 4 | `testcase-format` + `sync_testcase_snapshot` | 同步已生成用例到快照和主题页 |

**工程化处理（所有选项都可能涉及）：**
- `testcase-format` - Excel 导出与索引更新
- `snapshot_testcase` - 快照生成（选项 1、4）
- `sync_testcase_snapshot` - 快照同步到主题页（选项 4）

---

## 核心规则

- **平台拆分**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Platform split rules
- **测试设计**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Test design baseline
- **输出模板**：[testcase-generate/SKILL.md](../engine/skills/testcase-generate/SKILL.md) Output contract
- **增量补充**：[testcase-augment/SKILL.md](../engine/skills/testcase-augment/SKILL.md) 核心约束
- **Figma 读取**：[figma-reader/SKILL.md](../engine/skills/figma-reader/SKILL.md) Figma 设计稿读取
- **知识库管理**：[knowledge/SKILL.md](../knowledge/SKILL.md) 消化/查询/结晶/健康检查

---

## 工具脚本

| 用途 | 命令 |
|------|------|
| 索引校验 | `python3 engine/scripts/validate_index.py` |
| 用例索引 | `python3 engine/scripts/validate_testcase_index.py` |
| 模板生成 | `python3 engine/scripts/generate_testcase_from_template.py` |
| 清理过期文件 | `python3 engine/scripts/cleanup_testcase_store.py --dry-run` |
| 索引差异比较 | `python3 engine/scripts/diff_testcase_indexes.py` |
| 覆盖率报告 | `python3 engine/scripts/export_testcase_report.py` |
| Excel 填充 | `python3 engine/scripts/xlsx_fill_testcase_template.py` |
| 追加用例 | `python3 engine/scripts/xlsx_append_and_highlight.py` |
| 更新索引 | `python3 engine/scripts/upsert_testcase_index.py` |
| 同步快照 | `python3 engine/scripts/sync_testcase_snapshot.py` |

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
| 历史用例索引不存在 | 自动创建仓位和索引骨架 |
| Excel 导出依赖缺失 | 自动 `pip install openpyxl pandas` |
| 索引文件校验失败 | 见上方工具脚本 |
| 功能点数据缺失 | 从用例标题和步骤中提取关键词作为功能点 |

---

## 项目文档

- [CLAUDE.md](../CLAUDE.md) - 项目总览与核心原则
- [engine/skills/](../engine/skills/) - 子能力目录

**详细流程、测试设计规则、输出规范、质量检查清单等，请阅读各 Skill 文档**
