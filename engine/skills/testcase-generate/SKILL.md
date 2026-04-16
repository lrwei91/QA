---
name: testcase-generate
description: 从需求文档/PRD/页面/接口说明生成结构化测试用例 - 负责需求解析、模块识别、平台拆分、测试点设计、输出结构化用例
---

# Skill: Generate Test Cases

## 触发场景

- 用户提供 PRD / 页面 / 描述
- 需要生成测试用例（冒烟用例或完整用例）

## 职责

1. **需求解析** - 获取并清洗输入正文，识别需求类型
2. **模块识别** - 读取 `../../references/index-rules/module-index.json` 匹配候选模块，**必须让用户确认**
3. **模块确认** - 输出候选模块列表，用户确认或自定义输入后方可继续
4. **领域知识读取** - 读取 `../../references/domain-knowledge/<中文名>.md`
5. **平台拆分** - 按 `../../references/index-rules/platform-rules.md` 判定客户端/账服
6. **测试点设计** - 按 `../../references/test-design/testcase-taxonomy.md` 设计用例
7. **输出结构化用例** - 按 `../../references/test-design/output-template.md` 格式输出

## 领域知识路径说明

**单一知识源**：`engine/references/domain-knowledge/<中文名>.md`

例：`engine/references/domain-knowledge/运营活动.md`

路径对应规则：模块中文名 → 同名 .md 文件。文件内部使用 module-index.json 中的 module ID（如 `marketing-activities`）标识模块。

## 输入来源

- 用户直接粘贴文本
- 文件正文
- 网页正文
- Excel / Word 模板

## 输出

标准测试用例结构，包含：

| 字段 | 说明 |
|------|------|
| 序号 | 连续递增 |
| 平台 | `客户端` 或 `账服` |
| 模块 | 功能所属模块 |
| 功能点 | 具体验证目标 |
| 前置条件（测试点） | 执行前必须满足的状态 |
| 操作步骤 | 可执行的操作序列 |
| 预期结果 | 明确可验证的结果 |
| 测试结果 | 留空 |
| 备注 | 用例类型标记，如 `【功能测试】【P0】` |

## 用例类型策略

### 冒烟用例模式

- 仅生成正向主流程用例
- 仅覆盖 P0 级高风险校验
- 不生成边界值、异常、权限等扩展场景
- 用例数量控制在完整用例的 20%-30%

### 完整用例模式

- 生成全部类型用例：主流程、异常、边界、状态流转、权限
- 覆盖 P0/P1/P2 全优先级
- 按正常测试设计策略全面覆盖

## 核心原则

### 0. 模块确认优先

**在生成测试用例之前，必须先确认模块归属：**

1. **输出候选模块** - 基于需求关键词匹配 Top 3 模块
2. **等待用户确认** - 用户选择或自定义输入前不得继续
3. **领域知识补充** - 如新活动类型，需补充到 domain-knowledge 对应文件

**模块确认流程：**

```
▎ 需求已解析，检测到以下关键词：[复充返利、充值活动、返利比例]

最匹配的模块可能是（请选择或自定义）：

▎ 1. 运营管理 (marketing-activity) - 匹配度 90%
   - 触发词：运营活动、充值活动、返利活动
   - 领域：marketing-activities
   - 知识库：engine/references/domain-knowledge/运营活动.md
   - 参考文档：engine/references/domain-knowledge/运营活动.md

▎ 2. 财务系统 (finance-system) - 匹配度 70%
   - 触发词：充值、返利、资金账目
   - 领域：finance-system
   - 知识库：engine/references/domain-knowledge/财务系统.md
   - 参考文档：engine/references/domain-knowledge/财务系统.md

▎ 3. 厂商活动记录 (vendor-activities) - 匹配度 50%
   - 触发词：FC 活动、FG 活动、锦标赛
   - 领域：marketing-activities
   - 知识库：engine/references/domain-knowledge/运营活动.md
   - 参考文档：engine/references/domain-knowledge/运营活动.md

▎ 4. 自定义输入模块名称
```

**用户确认后，检查领域知识文件：**

读取 `engine/references/domain-knowledge/<模块中文名>.md`，如不存在则新增该文件。

**领域知识补充规则：**

- 如领域知识文件中不存在该活动类型 → 新增模块说明
- 如已存在但功能有增量 → 增量更新
- 如已存在但描述不一致 → 功能修改

---

### 1. 结果导向

- 只输出结构化测试用例，不输出大段解释性文字
- 每条用例都要可执行、可验证、可复现
- 预期结果必须明确，不得写成"提示正确""功能正常"这类空话

### 2. 风险优先

- 先覆盖核心主流程，再覆盖关键校验、状态流转、异常和边界
- 高风险功能优先补足 `P0 / P1` 场景

### 3. 去重与控量

- 一条用例只验证一个核心目标
- 使用等价类和代表值减少重复
- 对仅文案不同、路径相同、校验逻辑相同的场景，合并表达

### 4. 不臆造

- 不凭空补充不存在的业务规则
- 用户未明确给出的文档信息字段，不自动推断填写

### 5. 范围收敛

除非需求明确提到，或业务风险足够高，不默认扩展：

- 性能压测
- 安全渗透
- 浏览器兼容矩阵
- 自动化脚本实现
- 与当前需求无直接关系的环境类检查

## 平台划分规则

`平台` 字段仅允许使用：

- `客户端` - 页面展示、控件交互、文案提示、跳转、渲染、表单输入、按钮点击、弹窗、列表、禁用态、前端校验
- `账服` - 接口入参/出参、服务端校验、业务处理、状态变更、写库、查库、缓存、消息、异步任务、错误码、幂等、权限、风控、限流

**重要说明**：
- "管理后台"、"后台"、"后台管理系统"等都统一标记为 `账服`
- 不得在 `平台` 字段出现"管理后台"、"后台"等非标准名称

## 排序规则

- 生成用例时必须按平台排序：**先 `账服` 后 `客户端`**
- 同一平台内的用例按功能模块逻辑顺序排列（配置→展示→操作→结果）
- 序号按排序后的顺序连续递增

## 导出选项

生成测试用例后，输出导出选项：

```
测试用例已生成，请选择导出方式：

▎ 1. 导出为 Excel 文件并更新索引文件
▎ 2. 仅导出为 Excel 文件

导出后将保存到：outputs/generated/<模块>/<用例名称>.xlsx
```

**用户选择后，必须调用 `testcase-format` skill 执行 Excel 导出**：

- 不得手动创建 Excel 文件
- 必须使用 `xlsx_fill_testcase_template.py` 脚本
- 确保样式与 `templates/testcase_template.xlsx` 模板一致

## 资源文件

- `../../references/index-rules/module-index.json` - 模块索引
- `../../references/index-rules/platform-rules.md` - 平台划分规则
- `../../references/test-design/testcase-taxonomy.md` - 测试覆盖分类
- `../../references/test-design/output-template.md` - 输出模板

## 相关 Skills

- [`testcase-augment`](../testcase-augment/SKILL.md) - 补充已有用例
- [`testcase-analyze`](../testcase-analyze/SKILL.md) - 仅分析需求
- [`testcase-format`](../testcase-format/SKILL.md) - 导出 Excel 与索引更新
