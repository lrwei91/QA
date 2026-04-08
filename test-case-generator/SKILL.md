---
name: test-case-generator
description: 面向需求文档、PRD、网页正文、接口说明、现有用例和固定模板，生成结构化、可执行、可导出的专业测试用例；支持主模块识别、客户端/账服拆分、增量补充、模板保真、Excel 导出，以及在需求包含完整多语言文案时额外生成多语言校验 JSON，并分别纳入测试用例索引与多语言索引。
---

# Test Case Generator

## Overview

将零散需求资料转成结构化、可执行、可校验、可直接交付的测试用例。若需求中包含完整的多语言文案，还要额外产出可校验的多语言 JSON。输出必须专业、全面、去重、贴近真实测试执行，不生成空泛散文，不堆砌无关场景。

## Default workflow

按下面顺序执行：

1. 获取输入正文，清洗噪音并识别需求主体。
2. 判断需求类型：功能/业务需求、接口说明、页面交互说明、性能或 SLA 要求、混合型需求。
3. 提取模块、子模块、角色、流程、字段、参数、约束、状态流转、权限、异常条件、已有用例、模板信息。
4. 若当前工作区存在 `testcases/testcase-index.json` 或 `testcases/i18n-index.json`，且用户要求补充已有用例、查历史用例、保存、导出或处理多语言 JSON，先读取 `references/testcase-store.md`，用工作区索引定位候选产物文件。
5. 先应用通用测试设计与质量规则，再判断项目索引是否能显著提升主模块识别和关联回归范围判断。
6. 若项目索引有价值，先读取 `references/module-index.json`，再按需读取命中的领域文件和 `references/system-map.md`。
7. 按 `references/platform-rules.md` 判定 `平台` 字段，必要时把同一需求拆成 `客户端` 与 `账服` 两侧用例。
8. 按 `references/testcase-taxonomy.md` 设计核心用例与关联补充用例，优先覆盖核心主流程、高风险校验、状态流转、异常和边界。
9. 按 `references/output-template.md` 的列结构和格式输出；若用户指定模板，优先跟随用户模板，不为生成方便而重排模板。
10. 若提供已有用例并要求补充，只做增量去重补充。若工作区存在对应 Excel 文件，将新增用例追加到原文件末尾（不新建文件），新增行标黄标识，序号连续递增，并更新索引条目的 `updated_at`。
11. **自动检测多语言**：生成测试用例后，检查需求内容中是否包含多语言文案（关键词、语言代码、对照表格式），如有则自动提取并生成多语言校验 JSON。
12. 若需求或对话中包含多语言文案，检查是否覆盖固定语言集合；仅在语言值完整时生成多语言 JSON，不完整时输出缺失语言清单。
13. 若用户要求导出或落盘，按模板保真、默认留空、Excel 展示规则和工作区索引规则写出结果。
14. 只有在用户明确要求”更新 skill / 更新索引 / 修改模块文件”时，才进入维护模式并修改资源文件。

## Core principles

### 1) 结果导向

- 只输出结构化测试用例，不输出大段解释性文字。
- 每条用例都要可执行、可验证、可复现。
- 预期结果必须明确，不得写成“提示正确”“功能正常”这类空话。

### 2) 风险优先

- 先覆盖核心主流程，再覆盖关键校验、状态流转、异常和边界。
- 高风险功能优先补足 `P0 / P1` 场景。
- 对信息稀缺的需求，优先保核心路径和关键异常，不机械堆砌低价值组合。

### 3) 去重与控量

- 一条用例只验证一个核心目标，避免一条塞入多个不相干验证点。
- 使用等价类和代表值减少重复。
- 对仅文案不同、路径相同、校验逻辑相同的场景，合并表达，不重复生成。

### 4) 不臆造

- 不凭空补充不存在的业务规则。
- 用户未明确给出的文档信息字段，不自动推断填写。
- 若存在必要假设，可在结果外单独说明，不混入用例表体。

### 5) 范围收敛

除非需求明确提到，或业务风险足够高，不默认扩展以下内容：

- 性能压测
- 安全渗透
- 浏览器兼容矩阵
- 自动化脚本实现
- 与当前需求无直接关系的环境类检查

## Input understanding

### 1) 获取并清洗输入

优先从以下来源获取需求内容：

- 用户直接粘贴文本
- 文件正文
- 网页正文
- 现有测试用例
- Excel / Word 模板

如果输入包含明显噪音，应保留需求主体，忽略导航、页眉页脚、历史记录、无关说明。

### 2) 识别需求类型

先判断输入主体属于哪一类：

- 功能/业务需求
- 接口说明
- 页面交互说明
- 性能或 SLA 要求
- 混合型需求

### 3) 提取关键要素

至少提取以下信息：

- 功能模块和子模块
- 关键流程与业务场景
- 输入项、参数、字段及其约束
- 输出项、返回结果、错误码或页面反馈
- 业务规则、状态流转、角色权限
- 边界条件、异常条件
- 是否存在已有测试用例需要避重补充
- 是否存在指定模板、固定区、表头行或导出要求
- 当前工作区是否存在 `testcases/testcase-index.json` 或 `testcases/i18n-index.json` 可复用历史产物库
- 是否存在多语言相关内容，以及是否已给齐固定语言集合

## Use project index only when it adds value

### 1) 匹配主模块

先读取 `references/module-index.json`，使用以下字段做匹配：

- `aliases`
- `trigger_words`
- `core_functions`
- `client_signals`
- `server_signals`

优先给出 1 个主模块；如果存在明显歧义，可以保留 2 到 3 个候选模块并说明理由。

### 2) 扩展关联模块

使用以下信息扩展受影响范围：

- `depends_on`
- `impacted_modules`
- `always_check`
- `references/system-map.md` 中的联动规则

只读取命中的领域文件：

- `references/module-account-access.md`
- `references/module-commerce-ops.md`
- `references/module-platform-ops.md`

### 3) 什么时候必须补关联用例

出现以下任一信号时，必须补充关联用例：

- 权限、角色、可见范围、数据范围
- 登录、会话、账号状态、组织归属
- 新增、编辑、删除、审批、发布、配置变更
- 状态流转、审批结果、异步通知
- 商品、订单、退款、营销状态变化
- 统计口径、看板、日志、审计、消息触达

## Platform split rules

`平台` 字段只使用以下业务统一名称：

- `客户端`
- `账服`

必须遵循以下规则：

1. 页面展示、控件交互、文案提示、跳转、渲染、表单输入、按钮点击、弹窗、列表、禁用态、前端校验、交互反馈、视觉状态等前端关注点，归为 `客户端`。
2. 接口入参/出参、服务端校验、业务处理、状态变更、写库、查库、缓存、消息、异步任务、错误码、幂等、权限、风控、限流等服务端关注点，归为 `账服`。
3. 同一需求同时涉及前后端时，不要强行合并成一个平台；页面交互与展示拆为 `客户端`，接口校验、处理逻辑、返回结果和数据落库拆为 `账服`。
4. 判断模糊时，优先看本条用例验证的核心结果：
   - 关注页面表现，归 `客户端`
   - 关注接口返回或数据结果，归 `账服`
5. 需要更详细的判定时，读取 `references/platform-rules.md`。

## Test design baseline

始终先应用通用测试设计策略，再按项目模块补关联场景。具体分类和优先级规则见 `references/testcase-taxonomy.md`。

### 0) 用例类型选择

根据用户选择的用例类型调整覆盖策略：

**冒烟用例模式**：
- 仅生成正向主流程用例
- 仅覆盖 P0 级高风险校验
- 不生成边界值、异常、权限等扩展场景
- 用例数量控制在完整用例的 20%-30%

**完整用例模式**：
- 生成全部类型用例：主流程、异常、边界、状态流转、权限
- 覆盖 P0/P1/P2 全优先级
- 按正常测试设计策略全面覆盖

### 1) 基础覆盖面

每个核心功能点至少从以下维度判断是否需要覆盖：

- 正向主流程
- 必填 / 合法性校验
- 异常输入或非法操作
- 边界值
- 状态流转
- 权限或角色差异
- 数据结果或页面反馈一致性
- 前后端联动拆分

对后台管理系统还要额外检查：

- 日志
- 通知
- 统计口径
- 数据一致性
- 导出导入
- 查询筛选
- 幂等性

### 2) 典型设计方法

默认综合使用以下方法：

- 场景法：按真实用户路径组织主流程。
- 等价类：减少同质化冗余。
- 边界值：覆盖上下限、临界点、空值、未传。
- 状态迁移：覆盖合法流转和非法流转。
- 异常分析：覆盖参数非法、越权、重复操作、中断、失败回退。

### 3) 预期结果写法

预期结果应尽可能具体到：

- 页面展示什么
- 接口返回什么
- 是否提示错误
- 状态是否变更
- 是否写库 / 不写库
- 是否触发后续动作

不要只写：

- 功能正常
- 提示正确
- 返回成功

最低覆盖要求：

- 每个核心功能点或接口至少 1 条正常路径用例。
- 每个关键校验条件至少 1 类异常/无效输入用例。
- 有边界限制的字段必须覆盖边界值。
- 涉及状态流转、审批流、多角色权限时必须覆盖合法与非法迁移。

## Output contract

若用户未指定模板，严格使用 `references/output-template.md` 中的默认列结构：

1. 序号
2. 平台
3. 模块
4. 功能点
5. 前置条件（测试点）
6. 操作步骤
7. 预期结果
8. 测试结果
9. 备注

必须满足：

- `序号` 连续递增。
- `平台` 仅使用 `账服` 或 `客户端`。
- `模块` 写功能所属模块，不要过于笼统。
- `功能点` 写被验证的具体点，不要只写“功能测试”。
- `前置条件（测试点）`、`操作步骤`、`预期结果` 必须可执行、可验证。
- 多行内容使用 `1、2、3、` 的编号格式。
- `测试结果` 保持空值。
- `备注` 至少标记用例类型，推荐同时带优先级，例如 `【功能测试】【P0】`。
- 不要把说明性文字混进结果体；如需解释思路，放在结果外。

### 字段写法规范

- `模块`：写明确模块，不写过于笼统的“功能测试”“流程测试”。
- `功能点`：一条用例只对应一个清晰的验证目标。
- `前置条件（测试点）`：写执行前必须满足的状态、角色、数据、配置，与步骤不要重复。
- `操作步骤`：写清操作顺序，多行时使用 `1、2、3、` 编号换行。
- `预期结果`：与步骤对应，多行时使用 `1、2、3、` 编号换行。
- `测试结果`：默认留空，不自动填 `Pass` / `Fail` / `N/A`。
- `备注`：至少标记用例类型，常用 `【功能测试】`、`【异常测试】`、`【边界测试】`、`【状态流转测试】`、`【权限测试】`。

## Template handling and export

### 1) 用户指定模板时

- 优先遵循用户模板的列名、列顺序、表头位置、固定区和样式结构。
- 不得因为方便生成而重排模板。
- 若模板字段不足以表达关键测试信息，在不破坏模板结构前提下尽量补齐。
- 若用户提供的是 Word 模板，保留标题区、章节顺序、表格表头、固定说明文本和占位字段。

### 2) 模板固定区识别

若模板在正式表头上方存在标题区、统计区、文档信息区等内容，这些都属于模板的一部分，必须保留。

处理时先识别：

- 固定区在哪几行
- 真正表头行是哪一行
- 数据区从哪一行开始
- 是否存在统计公式
- 是否存在合并单元格

### 3) 当前项目常见 Excel 模板约定

对类似“前 6 行为固定区，第 7 行为表头，第 8 行起为数据区”的模板，默认按以下方式处理：

- 第 1 行可为标题区
- 第 1 至 4 行右侧可为统计区
- 第 2 至 6 行可为文档信息区
- 第 7 行为数据表头
- 第 8 行起写测试用例

固定区中的标签、合并单元格、边框、底色、公式位置应保持不变。

### 4) 默认留空字段

对于以下文档信息字段，若用户未明确提供内容，默认必须保留为空，不自动推断填写：

- `测试平台`
- `系统&版本`
- `文档编写人`
- `参考档`
- `测试日期`
- `最后更新`

规则是：

- 保留字段
- 不自动填值
- 只有用户明确提供，或明确要求代填时才写入

### 5) Excel 导出要求

**统一使用 minimax-xlsx 模板导出**

必须使用 `templates/testcase_template.xlsx` 模板和 `test-case-generator/scripts/xlsx_fill_testcase_template.py` 脚本导出 Excel，不得使用 openpyxl 直接创建。

```bash
# 使用 minimax-xlsx 脚本
python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx --template templates/testcase_template.xlsx
```

**rows.json 格式：**
```json
[
  {
    "平台": "客户端",
    "模块": "功能入口",
    "功能点": "侧边栏入口",
    "前置条件（测试点）": "1、已启用活动",
    "操作步骤": "1、进入页面",
    "预期结果": "入口展示正常",
    "测试结果": "",
    "备注": "【功能测试】"
  }
]
```

**meta.json 格式（可选）：**
```json
{
  "测试平台": "账服、客户端",
  "参考档": "需求文档 v2"
}
```

**导出要求：**
- 列顺序与目标模板保持一致。
- 多行字段必须写入真实换行符。
- `前置条件（测试点）`、`操作步骤`、`预期结果` 等多行单元格必须开启 Excel 的自动换行（wrap text）。
- 固定区不得被覆盖、删除或上移。
- 表头行位置不得改变。
- 数据区从模板指定起始行连续写入。
- 合并单元格按模板原样保留，数据区如需新增合并应谨慎且有明确依据。
- 统计公式应覆盖当前数据区。
- 默认留空字段若无用户输入，必须保持为空。

## Incremental supplement rules

当用户提供已有用例并要求“继续补充”“只补新增”“避免重复”时：

- 只输出新增测试用例。
- 不改写已有用例。
- 不重排已有用例内容。
- 旧用例仅用于判断覆盖范围和避重。
- 若当前工作区存在 `testcases/testcase-index.json` 或 `testcases/i18n-index.json`，优先结合索引命中的历史文件一起判断覆盖缺口和重复。
- 优先补齐遗漏的功能、异常、边界、状态和权限场景。
- 如果没有真正新增的场景，返回空结果，不要重复旧用例。

## Multilingual validation JSON

当需求、附件或对话中明确出现多语言文案，并且固定语言集合都已提供时，额外输出一份多语言校验 JSON。

### Auto-Detection Rules

在生成测试用例后，自动检查需求内容是否包含多语言文案：

**1. 关键词检测**
- 包含 `多语言 `、`国际化 `、`i18n`、` 翻译`、`Translation`、`Localization`
- 包含语言代码：`en-us`、`id-id`、`pt-pt`、`es-es`、`bn-bn`、`tr-tr`、`fp-fp`、`hi-in`、`th-th`、`zh-cn`、`zh-hk`、`vi-vn`
- 包含文案 key 格式：`UI_`、`Key_`、`STR_` 等前缀

**2. 表格格式检测**
- 多列表格，表头包含语言名称或语言代码
- key-value 对照格式（第一列为 key，后续列为各语言翻译）

**3. 提取策略**
- 自动识别 key 列和语言列
- 提取标准 7 种语言：`en-us`、`id-id`、`pt-pt`、`es-es`、`bn-bn`、`tr-tr`、`fp-fp`
- 如果包含额外语言（如 `hi-in`、`th-th` 等），仅提取标准 7 种

**4. 语言完整性检查**
- 检查每个 key 是否都包含完整 7 种语言
- 如果所有 key 语言完整 → 生成 JSON
- 如果有缺失 → 输出缺失清单，不生成 JSON

固定语言集合：

- `en-us`
- `id-id`
- `pt-pt`
- `es-es`
- `bn-bn`
- `tr-tr`
- `fp-fp`

JSON 固定结构：

- `name`
- `url`
- `preScriptPath`
- `options.matchRule`
- `options.captureRegion.x/y/width/height`
- `entries` (数组，每个元素包含 `key` 和 `languages`)
  - `key` (可选)：文案 key，仅在需求文档明确提供时写入，否则留空字符串
  - `languages` (必填)：包含 7 种标准语言的翻译文案

生成规则：

- 只在全部语言值完整时生成 JSON。
- 若缺语言，不自动补翻译，不生成 JSON，只输出缺失语言清单。
- 若语言完整但验证配置缺失，生成草稿 JSON：
  - `url=""`
  - `preScriptPath=""`
  - `matchRule="normalized-exact"`
  - `captureRegion={x:0,y:0,width:0,height:0}`
  - 对应索引条目使用 `status=draft`
- 若用户后续通过对话补齐全部语言，或手动新增合法 JSON 文件，使用多语言索引纳入历史库。

### Output Format

**检测到多语言内容时的输出：**
```
▎ 检测到需求中包含多语言文案
  - 已提取 XX 个多语言条目
  - 语言集合：en-us, id-id, pt-pt, es-es, bn-bn, tr-tr, fp-fp
  - ✓ 所有条目语言完整，已生成多语言校验 JSON
  - 文件路径：testcases/i18n/<模块>/<模块>-<功能>.json
  - 已更新多语言索引 testcases/i18n-index.json
```

**语言不完整时的输出：**
```
▎ 检测到需求中包含多语言文案
  - 已提取 XX 个多语言条目
  - 语言不完整，缺少：hi-in, th-th (非标准语言已忽略)
  - 标准 7 种语言检查：
    - 有 YY 个条目缺少 zz 语言
  - 暂不生成 JSON，请补充缺失语言后重试
```

## Export and save rules

默认行为是在对话中直接输出结构化测试用例；若语言完整，也可同时输出多语言 JSON 内容。

只有在用户明确要求保存、导出或写入某路径时，才执行落盘：

- 如果用户指定完整路径，直接写入指定文件。
- 如果用户只指定目录，默认文件名可使用 `测试用例_<模块或主题>_<yyyymmdd>.md`。
- 如果用户希望落盘但未指定路径，可默认写入当前工作区下的 `testcases/generated/` 目录。
- 如果 `testcases/`、`testcases/testcase-index.json` 或 `testcases/i18n-index.json` 不存在，先按 `references/testcase-store.md` 创建仓位与索引骨架。
- 多语言 JSON 默认写入当前工作区下的 `testcases/i18n/<模块>/` 目录。
- 若输出写入工作区产物仓位，写完后同步新增或更新对应索引条目。
- 优先使用 `test-case-generator/scripts/upsert_testcase_index.py` 自动生成或更新索引条目，而不是手工拼接 JSON。
- 多语言 JSON 合法性优先使用 `test-case-generator/scripts/validate_i18n_json.py` 校验。
- 测试用例索引条目至少维护：`id`、`group_key`、`title`、`module`、`module_ids`、`topic`、`platform_scope`、`format`、`rel_path`、`template`、`source_refs`、`tags`、`status`、`created_at`、`updated_at`。
- 多语言索引条目至少维护：`id`、`group_key`、`title`、`module`、`module_ids`、`topic`、`language_codes`、`format`、`rel_path`、`template`、`source_refs`、`tags`、`status`、`created_at`、`updated_at`。
- 若用户要求导出 Excel，保持默认列顺序并输出为 `.xlsx`。

### 增量补充用例规则

当用户要求"补充已有用例"且工作区存在对应 Excel 文件时：

1. **合并到原文件**：不要新建文件，将新增用例追加到原文件末尾
2. **标黄标识**：新增用例行使用黄色背景（#FFFF00）填充，便于区分
3. **序号连续**：新增用例序号从原最后序号 +1 开始连续递增
4. **自动换行**：`前置条件（测试点） `、`操作步骤`、`预期结果` 多行字段开启 wrap text
5. **索引更新**：使用 `upsert_testcase_index.py` 更新索引，复用原条目 `id`，仅更新 `updated_at`

使用脚本：
```bash
python3 test-case-generator/scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx --highlight
```

## Maintenance mode

默认只输出：

- 测试用例结果
- 索引增量建议
- 模块文档增量建议

只有在用户明确要求更新 skill 时，才执行以下动作：

1. 先根据 `references/update-governance.md` 判断要改哪些资源。
2. 修改 `references/module-index.json` 与对应领域文件。
3. 必要时同步更新 `references/system-map.md`、`references/platform-rules.md` 或 `references/output-template.md`。
4. 运行 `test-case-generator/scripts/validate_index.py references/module-index.json` 校验索引。
5. 若用户要求交付安装包，再重新打包整个 skill。

如果用户要求的是“修改测试用例生成能力”，优先修改以下内容：

- 生成策略
- 覆盖规则
- 去重规则
- 模板识别与导出规则
- 字段约束与质量自检

## Quality checks

输出前至少检查以下问题：

- 每个核心功能点是否至少有 1 条正向用例。
- 关键校验是否有异常用例。
- 有边界约束的字段是否覆盖边界值。
- 状态流转是否覆盖合法与非法路径。
- 是否遗漏角色 / 权限差异。
- 是否存在空模块、空功能点或空预期结果。
- 是否把前后端混成一条。
- 是否存在明显重复或低价值重复。
- 备注是否标记了用例类型。
- 是否把说明性文字混入了结果体。
- 若导出 Excel，多行字段是否已开启自动换行。
- 若使用模板，固定区、表头行、统计区、默认留空字段是否都符合要求。
- 若需求含多语言内容，是否检查了固定语言集合是否完整。
- 若生成多语言 JSON，是否符合固定 schema，并已同步写入多语言索引。

## Resources

- `references/module-index.json`：项目模块索引，第一层检索入口。
- `references/system-map.md`：跨模块联动规则与回归扩展逻辑。
- `references/platform-rules.md`：客户端与账服的详细区分规则。
- `references/testcase-taxonomy.md`：测试覆盖分类、优先级和后台系统高风险维度。
- `references/output-template.md`：默认列结构、输出格式和 Excel 导出约定。
- `references/testcase-store.md`：工作区测试用例仓位与双索引约定。
- `references/update-governance.md`：生成模式与维护模式边界。
- `references/module-account-access.md`：账号、登录、权限、组织领域说明。
- `references/module-commerce-ops.md`：商品、营销、订单、退款领域说明。
- `references/module-platform-ops.md`：看板、日志、通知领域说明。
- `scripts/validate_index.py`：索引结构校验脚本。
- `scripts/upsert_testcase_index.py`：工作区测试用例索引与多语言索引新增/更新脚本。
- `scripts/validate_i18n_json.py`：多语言校验 JSON 结构校验脚本。
- `scripts/validate_testcase_index.py`：测试用例索引校验脚本。
- `scripts/validate_i18n_index.py`：多语言索引校验脚本。
- `scripts/generate_testcase_from_template.py`：测试用例模板生成脚本（减少跨技能依赖）。
- `scripts/cleanup_testcase_store.py`：清理过期用例和孤立索引条目。
- `scripts/diff_testcase_indexes.py`：比较两个索引文件的差异。
- `scripts/export_testcase_report.py`：生成测试用例覆盖率统计报告。
- `references/domain-template.md`：领域文档编写模板。

## Failure handling

遇到信息不足时：

1. 先基于现有内容和索引做最合理匹配，不要停在”无法判断”。
2. 明确标出假设项。
3. 对不确定联动关系使用”建议补查”，不要伪装成确定事实。
4. 继续输出可执行的基础用例和高风险关联用例。

## Welcome message

每次启动 skill 时，首先输出以下固定引导内容：

```
欢迎使用🐟鲤鱼用例管理生成系统

请告诉我您的需求内容，或从以下选项中选择操作：

▎ 请选择要执行的操作：
▎ 1. 生成测试用例
▎ 2. 补充已有用例
▎ 3. 生成多语言校验 JSON
▎ 4. 仅分析需求，不生成用例
```

## Test case type selection

当用户选择「生成测试用例」后，进一步确认用例类型：

### 冒烟用例 vs 完整用例

**冒烟用例（Smoke Test）**：
- 仅覆盖核心主流程
- 仅覆盖 P0 级高风险场景
- 用例数量精简，快速验证功能可用性
- 适用于快速回归、版本冒烟

**完整用例（Full Test）**：
- 覆盖主流程、异常、边界、状态流转、权限等全部场景
- 覆盖 P0/P1/P2 全优先级
- 用例数量全面，深度验证功能
- 适用于正式测试、全量回归

## Multilingual Auto-Detection

在生成测试用例后，自动检查需求内容中是否包含多语言相关的文案：

### 检查规则

1. **关键词检测**：检查需求中是否包含以下关键词
   - `多语言`、`国际化`、`i18n`、`翻译`、`Translation`
   - 语言代码：`en-us`、`id-id`、`pt-pt`、`es-es`、`bn-bn`、`tr-tr`、`fp-fp`、`hi-in`、`th-th`、`zh-cn`、`zh-hk`、`vi-vn`
   - 文案 key 格式：`UI_`、`key`、`文案`、`文本`

2. **表格检测**：检查是否包含多语言对照表格式
   - 多列表格包含语言代码或语言名称
   - key-value 对照格式

3. **自动提取**：如果检测到多语言内容，自动提取并整理

### 执行流程

```
检测到多语言内容 → 检查语言完整性 → 生成多语言校验 JSON → 更新多语言索引
```

**输出提示：**
```
▎ 检测到需求中包含多语言文案
  - 已提取 XX 个多语言条目
  - 语言集合：en-us, id-id, pt-pt, es-es, bn-bn, tr-tr, fp-fp
  - 已生成多语言校验 JSON：testcases/i18n/<模块>/<模块>-<功能>.json
  - 已更新多语言索引
```

## Excel Export Options

生成测试用例后，提供导出选项：

```
测试用例已生成，请选择导出方式：

▎ 1. 导出为 Excel 文件并更新索引文件
▎ 2. 仅导出为 Excel 文件

导出后将保存到：testcases/generated/<模块>_<日期>.xlsx
```

### 选项 1：导出 Excel 并更新索引

**执行步骤：**

1. **生成 rows.json**：将测试用例转为 minimax-xlsx 模板所需的 JSON 格式
2. **导出 Excel**：
   ```bash
   python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
       rows.json output.xlsx --template templates/testcase_template.xlsx
   ```
3. **保存到仓位**：将 Excel 文件移动到 `testcases/generated/<模块>_<yyyymmdd>.xlsx`
4. **更新索引**：
   ```bash
   python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/<模块>_<yyyymmdd>.xlsx
   ```
5. **验证索引**：
   ```bash
   python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
   ```

### 选项 2：仅导出 Excel

**执行步骤：**

1. **生成 rows.json**：将测试用例转为 minimax-xlsx 模板所需的 JSON 格式
2. **导出 Excel**：
   ```bash
   python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
       rows.json output.xlsx --template templates/testcase_template.xlsx
   ```
3. **保存到仓位**：将 Excel 文件移动到 `testcases/generated/<模块>_<yyyymmdd>.xlsx`

## Supplement Existing Testcases

当用户选择「补充已有用例」时，按以下流程执行：

### 第 1 步：读取索引并按模块列出用例

```bash
python3 << 'EOF'
import json
from pathlib import Path

index_path = Path('testcases/testcase-index.json')
if not index_path.exists():
    print("索引文件不存在，先创建仓位")
    # 创建仓位和索引骨架

with open(index_path, 'r') as f:
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
print("请选择要补充的模块：\n")
for i, (m, es) in enumerate(sorted(modules.items()), 1):
    print(f"{i}. 【{m}】({len(es)}个)")
    for j, e in enumerate(es, 1):
        updated = e.get('updated_at', '')[:10] if e.get('updated_at') else ''
        fmt = e.get('format', '')
        title = e.get('title', '')
        print(f"   {j}. {title} [{fmt}] - {updated}")
EOF
```

### 第 2 步：用户选择用例后

用户输入模块编号和用例编号（如：`1-2` 表示第 1 个模块的第 2 个用例）后：

```
已选择：英雄技能 - 英雄技能升级功能
文件路径：testcases/generated/英雄技能/英雄技能升级功能.xlsx

请提供您需要补充的内容，可以通过以下方式：

▎ 1. 直接粘贴 新增需求/变更内容 文本
▎ 2. 提供文件路径，我来读取
▎ 3. 提供 URL，我来抓取网页内容
▎ 4. 描述需要补充的测试场景
```

### 第 3 步：生成补充用例并追加

**执行步骤：**

1. **生成新增用例**：根据用户提供的内容，生成增量测试用例（去重）
2. **读取原文件最后序号**：
   ```bash
   python3 << 'EOF'
   from openpyxl import load_workbook
   wb = load_workbook('existing.xlsx', read_only=True)
   ws = wb.active
   # 从数据区第 8 行开始读取
   last_row = 7  # 表头在第 7 行
   for row in range(8, ws.max_row + 1):
       if ws.cell(row, 1).value:  # 序号列
           last_row = row
   print(f"last序号={ws.cell(last_row, 1).value if last_row > 7 else 0}")
   EOF
   ```
3. **追加用例并标黄**：
   ```bash
   python3 test-case-generator/scripts/xlsx_append_and_highlight.py \
       existing.xlsx new_rows.json output.xlsx --highlight
   ```
4. **更新索引**（复用原 id，仅更新 updated_at）：
   ```bash
   python3 test-case-generator/scripts/upsert_testcase_index.py \
       testcases/generated/英雄技能/英雄技能升级功能.xlsx \
       --topic "英雄技能升级功能" --module "英雄技能" --status auto
   ```

### rows.json 格式

```json
[
  {
    "平台": "客户端",
    "模块": "技能升级",
    "功能点": "升级按钮点击 - 材料不足",
    "前置条件（测试点）": "1、背包材料不足",
    "操作步骤": "1、点击升级按钮",
    "预期结果": "1、飘字提示【材料不足】\n2、技能等级不变",
    "测试结果": "",
    "备注": "【异常测试】【P0】"
  }
]
```

### meta.json 格式（可选）

用于填充 Excel 模板的文档信息区：

```json
{
  "测试平台": "账服、客户端",
  "参考档": "Y-001-002-养成 - 英雄技能升级功能.docx",
  "系统&版本": "",
  "文档编写人": "",
  "测试日期": "",
  "最后更新": ""
}
```

### 导出要求

- **列顺序**：与 testcase_template.xlsx 保持一致
- **多行字段**：`前置条件（测试点） `、` 操作步骤`、`预期结果` 必须开启自动换行（wrap text）
- **默认留空字段**：`测试平台 `、` 系统&版本`、`文档编写人`、` 参考档`、` 测试日期`、` 最后更新` 若用户未提供则保持为空
- **索引更新**：使用 `upsert_testcase_index.py` 自动生成条目，包括 `id`、`group_key`、`module`、`platform_scope`、`rel_path` 等
- **增量补充**：追加到原文件末尾，新增行标黄（#FFFF00），序号连续递增，复用原索引 id

## Error Handling

### 常见错误与解决方案

| 错误现象 | 原因 | 解决方案 |
|----------|------|----------|
| `File content exceeds maximum allowed tokens` | HTML 文件过大，Read 工具无法一次性读取完整内容 | 使用 Python HTMLParser 提取文本，或用 `limit/offset` 参数分段读取 |
| `[Errno 2] No such file or directory` | 文件名包含空格或特殊字符（如 `帐服 - 运营管理新增活动.html` 实际不存在） | 先用 `ls` 确认文件名，处理文件名中的空格和特殊字符 |
| `xlsx_fill_testcase_template.py` 执行失败 | 模板文件路径错误或依赖缺失 | 确认 `templates/testcase_template.xlsx` 存在，检查 `openpyxl`、`pandas` 是否已安装 |
| 索引文件校验失败 | JSON 格式错误或必填字段缺失 | 使用 `python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json` 校验 |
| 模块匹配歧义 | 需求同时涉及多个模块 | 使用 `AskUserQuestion` 确认主模块，或输出多个候选模块说明 |
| 多语言不完整 | 需求中语言文案缺失部分语言 | 输出缺失语言清单，不生成 JSON，等待用户补充 |
| Excel 导出后索引未更新 | 忘记调用 `upsert_testcase_index.py` | 导出后必须执行索引更新脚本 |

### 错误处理流程

**1. 文件读取失败时：**

```bash
# 方案 1：使用 Python 提取 HTML 文本
python3 -c "
from html.parser import HTMLParser
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
    def handle_data(self, data):
        if data.strip():
            self.texts.append(data.strip())
with open('file.html', 'r') as f:
    parser = TextExtractor()
    parser.feed(f.read())
    print(parser.texts)
"

# 方案 2：分段读取大文件
# 使用 limit 和 offset 参数
```

**2. 文件名不存在时：**

```bash
# 先列出目录内容确认实际文件名
ls -la "path/to/dir/"

# 处理带空格的文件名，使用引号包裹
cp "file with spaces.html" target/
```

**3. Excel 导出依赖缺失：**

```bash
# 自动安装依赖
python3 -c "import openpyxl, pandas" 2>/dev/null \
  && echo "DEPS_OK" \
  || pip install openpyxl pandas
```

**4. 索引文件校验：**

```bash
# 校验测试用例索引
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json

# 校验多语言索引
python3 test-case-generator/scripts/validate_i18n_index.py testcases/i18n-index.json

# 校验模块索引
python3 test-case-generator/scripts/validate_index.py references/module-index.json
```

### 本次执行遇到的问题与修复

**问题 1：Read 工具读取大 HTML 文件失败**
- **错误**：`File content (290.8KB) exceeds maximum allowed size (256KB)`
- **修复**：改用 Python HTMLParser 提取文本内容，绕过 token 限制

**问题 2：文件名包含特殊字符导致读取失败**
- **错误**：`[Errno 2] No such file or directory: '帐服 - 运营管理新增活动.html'`
- **原因**：文件名实际为 `帐服 - 运营管理新增活动.html`（中间有多个空格）
- **修复**：先用 `ls` 确认实际文件名，使用引号包裹路径

**问题 3：Read 工具多次读取大文件失败**
- **错误**：连续 7 次读取 `data.js` 文件失败，token 超限
- **修复**：改用 `Bash + Python` 方式提取 HTML 中的文本内容

**经验教训：**
1. 对于 Axure 导出的 HTML 原型文件，优先使用 Python 提取文本，不要直接用 Read 工具
2. 对于包含特殊字符的文件名，先用 `ls` 确认，再操作
3. 对于大的 `data.js` 文件，直接解析 HTML 更高效
