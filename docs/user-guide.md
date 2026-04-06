# 用户指南

详细的 QA 测试用例生成器使用说明。

---

## 目录

- [工作流程](#工作流程)
- [用例生成模式](#用例生成模式)
- [平台拆分规则](#平台拆分规则)
- [导出与保存](#导出与保存)
- [增量补充](#增量补充)
- [多语言 JSON](#多语言-json)
- [脚本工具](#脚本工具)
- [模块索引](#模块索引)

---

## 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  输入需求   │ →  │  分析识别   │ →  │  设计用例   │
│  文档/PRD   │    │  模块/平台  │    │  正向/异常  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  更新索引   │ ←  │  导出保存   │ ←  │  质量检查   │
│  testcase/  │    │  Excel/JSON │    │  去重/控量  │
│  i18n       │    └─────────────┘    └─────────────┘
└─────────────┘
```

### 第 1 步：获取并清洗输入

支持以下输入来源：
- 用户直接粘贴文本
- 文件正文（.md, .docx, .txt）
- 网页正文（提供 URL）
- 现有测试用例
- Excel / Word 模板

如果输入包含明显噪音（导航、页眉页脚、历史记录），应保留需求主体，忽略无关内容。

### 第 2 步：识别需求类型

判断输入主体属于哪一类：
- **功能/业务需求** - 最常见的类型
- **接口说明** - API 文档、接口定义
- **页面交互说明** - UI 原型、交互流程
- **性能或 SLA 要求** - 性能指标、响应时间
- **混合型需求** - 包含以上多种类型

### 第 3 步：提取关键要素

至少提取以下信息：
- 功能模块和子模块
- 关键流程与业务场景
- 输入项、参数、字段及其约束
- 输出项、返回结果、错误码或页面反馈
- 业务规则、状态流转、角色权限
- 边界条件、异常条件
- 是否存在已有测试用例需要避重补充
- 是否存在指定模板、固定区、表头行或导出要求
- 当前工作区是否存在索引可复用历史产物库
- 是否存在多语言相关内容，以及是否已给齐固定语言集合

### 第 4 步：应用模块索引

读取 `references/module-index.json`，使用以下字段做匹配：
- `aliases` - 模块别名
- `trigger_words` - 触发关键词
- `core_functions` - 核心功能
- `client_signals` - 客户端信号
- `server_signals` - 服务端信号

优先给出 1 个主模块；如果存在明显歧义，可以保留 2 到 3 个候选模块并说明理由。

### 第 5 步：平台拆分

按以下规则判定 `平台` 字段：

| 平台值 | 说明 |
|--------|------|
| `客户端` | 前端展示、交互、UI、跳转、渲染、表单输入、按钮点击、弹窗、列表、禁用态、前端校验 |
| `账服` | 接口入参/出参、服务端校验、业务处理、状态变更、写库/查库、缓存、消息、异步任务、错误码、幂等、权限、风控、限流 |

同一需求同时涉及前后端时，不要强行合并成一个平台：
- 页面交互与展示 → `客户端`
- 接口校验、处理逻辑、返回结果和数据落库 → `账服`

### 第 6 步：设计测试用例

按 `references/testcase-taxonomy.md` 设计核心用例与关联补充用例，优先覆盖：
1. 核心主流程
2. 高风险校验
3. 状态流转
4. 异常和边界

### 第 7 步：输出生成

按 `references/output-template.md` 的列结构和格式输出。若用户指定模板，优先跟随用户模板。

### 第 8 步：导出与索引

若用户要求落盘：
1. 写入 `testcases/generated/<模块>/<主题>_<日期>.xlsx`
2. 调用 `upsert_testcase_index.py` 更新索引
3. 调用 `validate_testcase_index.py` 校验索引

---

## 用例生成模式

### 冒烟用例模式

适用于快速回归、版本冒烟：
- 仅生成正向主流程用例
- 仅覆盖 P0 级高风险校验
- 不生成边界值、异常、权限等扩展场景
- 用例数量控制在完整用例的 20%-30%

### 完整用例模式

适用于正式测试、全量回归：
- 生成全部类型用例：主流程、异常、边界、状态流转、权限
- 覆盖 P0/P1/P2 全优先级
- 按正常测试设计策略全面覆盖

---

## 平台拆分规则

### 客户端（前端）

**关注点：**
- 页面展示、控件交互、文案提示
- 跳转、渲染、表单输入
- 按钮点击、弹窗、列表
- 禁用态、前端校验、交互反馈
- 视觉状态、动画效果

**示例场景：**
- 用户在页面输入手机号
- 点击按钮后弹窗提示
- 倒计时显示与归零
- 列表筛选与排序

### 账服（后端）

**关注点：**
- 接口入参/出参
- 服务端校验、业务处理
- 状态变更、写库/查库
- 缓存、消息、异步任务
- 错误码、幂等、权限
- 风控、限流

**示例场景：**
- 登录接口校验密码
- 订单状态流转
- 优惠券核销写库
- 消息推送异步任务

---

## 导出与保存

### 默认行为

默认在对话中直接输出结构化测试用例，不自动落盘。

### 导出选项

只有在用户明确要求保存、导出或写入某路径时，才执行落盘：

| 用户指令 | 行为 |
|----------|------|
| "导出 Excel" | 写入 `testcases/generated/<模块>/<主题>_<yyyymmdd>.xlsx` |
| "保存到桌面" | 写入用户指定路径 |
| "更新索引" | 调用 `upsert_testcase_index.py` 更新索引 |

### 导出流程

使用 minimax-xlsx 模板导出：

```bash
python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx \
    --template templates/testcase_template.xlsx
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
    "备注": "【功能测试】【P0】"
  }
]
```

### 索引更新

导出后自动调用：
```bash
python3 test-case-generator/scripts/upsert_testcase_index.py \
    testcases/generated/<模块>/<主题>_<yyyymmdd>.xlsx
```

---

## 增量补充

当用户提供已有用例并要求"继续补充""只补新增""避免重复"时：

1. **只输出新增测试用例**，不改写已有用例
2. **不重排已有用例内容**
3. **旧用例仅用于判断覆盖范围和避重**
4. **优先结合索引命中的历史文件一起判断覆盖缺口和重复**
5. **优先补齐遗漏的功能、异常、边界、状态和权限场景**
6. **如果没有真正新增的场景，返回空结果**

### 合并到原文件

当工作区存在对应 Excel 文件时：
1. 不要新建文件，将新增用例追加到原文件末尾
2. 新增用例行使用黄色背景（#FFFF00）填充，便于区分
3. 新增用例序号从原最后序号 +1 开始连续递增
4. `前置条件（测试点） `、`操作步骤`、`预期结果` 多行字段开启自动换行
5. 使用 `upsert_testcase_index.py` 更新索引，复用原条目 id，仅更新 `updated_at`

```bash
python3 test-case-generator/scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx \
    --highlight --highlight-color "FFFF00"
```

---

## 多语言 JSON

### 何时生成

当需求、附件或对话中明确出现多语言文案，并且固定语言集合都已提供时，额外输出一份多语言校验 JSON。

### 固定语言集合

| 代码 | 语言 |
|------|------|
| `en-us` | 英语 |
| `id-id` | 印尼语 |
| `pt-pt` | 葡萄牙语 |
| `es-es` | 西班牙语 |
| `bn-bn` | 孟加拉语 |
| `tr-tr` | 土耳其语 |
| `fp-fp` | 菲律宾语 |

### JSON 结构

```json
{
  "name": "页面/功能名称",
  "url": "页面 URL",
  "preScriptPath": "前置脚本路径",
  "languages": {
    "en-us": { "title": "...", ... },
    "id-id": { "title": "...", ... },
    ...
  },
  "options": {
    "matchRule": "normalized-exact",
    "captureRegion": {
      "x": 0, "y": 0, "width": 0, "height": 0
    }
  }
}
```

### 生成规则

- 只在全部语言值完整时生成 JSON
- 若缺语言，不自动补翻译，只输出缺失语言清单
- 若语言完整但验证配置缺失，生成草稿 JSON：
  - `url=""`
  - `preScriptPath=""`
  - `matchRule="normalized-exact"`
  - `captureRegion={x:0,y:0,width:0,height:0}`
  - 对应索引条目使用 `status=draft`

---

## 脚本工具

| 脚本 | 用途 | 示例 |
|------|------|------|
| `upsert_testcase_index.py` | 新增/更新索引条目 | `python3 upsert_testcase_index.py --all` |
| `validate_testcase_index.py` | 校验测试用例索引 | `python3 validate_testcase_index.py testcases/testcase-index.json` |
| `validate_i18n_index.py` | 校验多语言索引 | `python3 validate_i18n_index.py testcases/i18n-index.json` |
| `validate_i18n_json.py` | 校验单个多语言 JSON | `python3 validate_i18n_json.py testcases/i18n/模块/文件.json` |
| `validate_index.py` | 校验模块索引 | `python3 validate_index.py test-case-generator/references/module-index.json` |
| `cleanup_testcase_store.py` | 清理过期/孤立文件 | `python3 cleanup_testcase_store.py --dry-run` |
| `diff_testcase_indexes.py` | 比较索引差异 | `python3 diff_testcase_indexes.py old.json new.json` |
| `export_testcase_report.py` | 生成覆盖率报告 | `python3 export_testcase_report.py --output report.html` |
| `generate_testcase_from_template.py` | 从模板生成用例 | `python3 generate_testcase_from_template.py template.xlsx data.json output.xlsx` |
| `xlsx_append_and_highlight.py` | Excel 追加标黄 | `python3 xlsx_append_and_highlight.py existing.xlsx new.json output.xlsx --highlight` |

---

## 模块索引

### 已定义模块（30+）

| 模块 ID | 名称 | 领域 |
|--------|------|------|
| `auth-center` | 认证中心 | account-access |
| `admin-user` | 后台账号管理 | account-access |
| `role-permission` | 角色权限 | account-access |
| `organization` | 组织架构 | account-access |
| `personal-center` | 个人中心 | account-access |
| `kyc-certification` | 认证内容 | account-access |
| `product-catalog` | 商品中心 | commerce-ops |
| `marketing-banner` | banner 投放 | commerce-ops |
| `order-management` | 订单管理 | commerce-ops |
| `refund-approval` | 退款审批 | commerce-ops |
| `finance-system` | 财务系统 | commerce-ops |
| `player-management` | 玩家管理 | commerce-ops |
| `game-golden-flow` | 游戏及金流记录 | operation-management |
| `vendor-activities` | 厂商活动记录 | operation-management |
| `affiliate-management` | 全民代管理 | operation-management |
| `partner-agent` | 合伙人与代理 | operation-management |
| `channel-management` | 渠道管理 | operation-management |
| `frontend-management` | 前端管理 | operation-management |
| `game-management` | 游戏管理 | operation-management |
| `operation-management` | 运营管理 | operation-management |
| `dashboard` | 运营看板 | platform-ops |
| `operation-log` | 操作日志 | platform-ops |
| `notification-center` | 消息中心 | platform-ops |
| `report-system` | 报表系统 | platform-ops |
| `risk-management` | 风险管理 | platform-ops |
| `config-management` | 配置管理 | platform-ops |
| `customer-service` | 客服后台 | platform-ops |
| `sms-marketing` | 短信营销中心 | platform-ops |
| `email-management` | 邮件管理 | platform-ops |
| `system-settings` | 系统设置 | platform-ops |

### 模块匹配

每个模块定义包含：
- `id` - 唯一标识
- `name` - 中文名称
- `domain` - 所属领域
- `aliases` - 别名列表
- `trigger_words` - 触发关键词
- `core_functions` - 核心功能列表
- `depends_on` - 依赖模块
- `impacted_modules` - 受影响模块
- `client_signals` - 客户端信号
- `server_signals` - 服务端信号

---

## 输出模板

### 默认列结构

| 列号 | 列名 | 说明 |
|------|------|------|
| A | 序号 | 连续递增数字 |
| B | 平台 | `客户端` 或 `账服` |
| C | 模块 | 功能所属模块 |
| D | 功能点 | 被验证的具体点 |
| E | 前置条件（测试点） | 执行前必须满足的状态 |
| F | 操作步骤 | 操作顺序，多行用 `1、2、3、` |
| G | 预期结果 | 与步骤对应，多行用 `1、2、3、` |
| H | 测试结果 | 默认留空 |
| I | 备注 | 至少标记用例类型，推荐带优先级 |

### Excel 模板画像

- 工作表名称：`测试用例`
- 固定区：第 1 至 7 行（标题区 + 文档信息区 + 统计区）
- 表头行：第 7 行
- 数据区：第 8 行起
- 冻结窗格：A8

---

## 质量检查清单

输出前自动检查：
- [ ] 每个核心功能点是否至少有 1 条正向用例
- [ ] 关键校验是否有异常用例
- [ ] 有边界约束的字段是否覆盖边界值
- [ ] 状态流转是否覆盖合法与非法路径
- [ ] 是否遗漏角色/权限差异
- [ ] 是否存在空模块、空功能点或空预期结果
- [ ] 是否把前后端混成一条
- [ ] 是否存在明显重复或低价值重复
- [ ] 备注是否标记了用例类型
- [ ] 若导出 Excel，多行字段是否已开启自动换行
- [ ] 若需求含多语言内容，是否检查了固定语言集合是否完整
