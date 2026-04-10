# QA 项目术语词典

本文档定义了 QA 测试用例生成器项目中使用的核心术语和概念。

---

## 核心概念

### 测试用例 (Test Case)

结构化测试执行文档，包含：
- 序号、平台、模块、功能点
- 前置条件、操作步骤、预期结果
- 测试结果、备注（优先级标签）

存储格式：Excel (.xlsx)
存储位置：`outputs/generated/<模块>/`

---

### 多语言校验 JSON (I18N Validation JSON)

用于验证界面多语言文案完整性的 JSON 文件。

**固定语言集合**（7 种）：
- `en-us` - 英语
- `id-id` - 印尼语
- `pt-pt` - 葡萄牙语
- `es-es` - 西班牙语
- `bn-bn` - 孟加拉语
- `tr-tr` - 土耳其语
- `fp-fp` - 菲律宾语

**JSON 结构**：
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
    "captureRegion": { "x": 0, "y": 0, "width": 0, "height": 0 }
  }
}
```

存储位置：`outputs/i18n/<模块>/`

---

### group_key

**用途**：关联同一需求/主题下的多个产物

**命名规则**：`<模块>-<主题>`

**示例**：
- `personal-center-free-spin`
- `task-system-optimization`

**关联关系**：
```
group_key: task-system-optimization
├── testcase-index.json 中的条目 (测试用例)
└── i18n-index.json 中的条目 (多语言 JSON)
```

---

### module_ids

**定义**：业务模块的唯一标识符列表

**来源**：`engine/references/module-index.json`

**当前已定义模块**（27+）：
- `personal-center` - 个人中心
- `task-system` - 任务系统
- `auth-center` - 认证中心
- `user-profile` - 用户资料
- `wallet` - 钱包
- `payment` - 支付
- `bonus` - 红利
- `activity` - 活动管理
- `agency` - 代理管理
- `risk-control` - 风控管理
- `customer-service` - 客服管理
- `report` - 报表中心
- `system-config` - 系统配置
- `content-management` - 内容管理
- `game-management` - 游戏管理
- `marketing` - 营销工具
- `affiliate` - 联盟管理
- `notification` - 通知中心
- `search` - 搜索中心
- `recommendation` - 推荐中心
- `analytics` - 分析中心
- `security` - 安全管理
- `compliance` - 合规管理
- `audit` - 审计中心
- `monitoring` - 监控中心
- `dev-tools` - 开发工具
- `ops-tools` - 运营工具

**使用场景**：
- 测试用例索引中的模块定位
- 多语言 JSON 的模块分类
- 依赖关系分析

---

### platform_scope

**定义**：测试用例或模块所属的平台范围

**合法值**：
- `客户端` - 前端客户端（Web/App/H5）
- `账服` - 后端账务/服务层

**历史兼容值**（需标准化）：
- `平台` → `账服`
- `后端` → `账服`
- `大厅` → `客户端`
- `运营活动` → `账服`

**自动转换规则**：
```python
PLATFORM_MAPPING = {
    '平台': '账服',
    '后端': '账服',
    '大厅': '客户端',
    '运营活动': '账服'
}
```

---

### 账服 (Server/Backend)

**定义**：后端服务层，处理核心业务逻辑、数据存储、API 接口

**典型功能**：
- 用户认证与授权
- 账务计算与结算
- 数据持久化
- 第三方服务集成
- 风控规则执行

**测试关注点**：
- API 接口正确性
- 数据一致性
- 事务完整性
- 并发安全性

---

### 客户端 (Client)

**定义**：前端展示层，包括 Web、App、H5 等用户界面

**典型功能**：
- 页面渲染
- 用户交互
- 数据展示
- 表单校验
- 路由导航

**测试关注点**：
- UI 一致性
- 交互流畅性
- 响应式布局
- 浏览器兼容性
- 性能指标（首屏时间、卡顿率）

---

## 索引相关

### testcase-index.json

**用途**：测试用例的中心化索引

**位置**：`outputs/testcase-index.json`

**结构**：
```json
{
  "version": "1.0",
  "store_name": "QA-Test-Case-Store",
  "root_dir": ".",
  "cases_dir": "outputs/generated",
  "updated_at": "2026-04-01T00:00:00Z",
  "entries": [
    {
      "id": "<UUID>",
      "group_key": "<group_key>",
      "title": "<用例标题>",
      "module": "<模块名>",
      "module_ids": ["<module_id>"],
      "topic": "<主题>",
      "platform_scope": "客户端 | 账服",
      "format": "xlsx",
      "rel_path": "outputs/generated/模块/文件.xlsx",
      "template": "minimax-xlsx",
      "source_refs": [],
      "tags": ["功能测试", "P0"],
      "status": "active|deprecated|draft",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### i18n-index.json

**用途**：多语言校验 JSON 的中心化索引

**位置**：`outputs/i18n-index.json`

**结构**：
```json
{
  "version": "1.0",
  "store_name": "QA-I18N-Store",
  "root_dir": ".",
  "i18n_dir": "outputs/i18n",
  "updated_at": "2026-04-01T00:00:00Z",
  "entries": [
    {
      "id": "<UUID>",
      "group_key": "<group_key>",
      "title": "<主题>",
      "module": "<模块名>",
      "module_ids": ["<module_id>"],
      "topic": "<主题>",
      "language_codes": ["en-us", "id-id", ...],
      "format": "json",
      "rel_path": "outputs/i18n/模块/文件.json",
      "template": "i18n-schema-v1",
      "source_refs": [],
      "tags": ["多语言", "文案校验"],
      "status": "active|deprecated|draft",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### module-index.json

**用途**：业务模块定义与依赖关系索引

**位置**：`engine/references/module-index.json`

**结构**：
```json
{
  "version": "1.0",
  "updated_at": "2026-04-01T00:00:00Z",
  "modules": [
    {
      "id": "personal-center",
      "name": "个人中心",
      "aliases": ["用户中心", "UC"],
      "trigger_words": ["个人中心", "用户资料", "账户设置"],
      "core_functions": ["资料编辑", "头像上传", "密码修改"],
      "depends_on": ["auth-center"],
      "impacted_modules": ["user-profile"],
      "platform_scope": "客户端，账服",
      "client_signals": ["页面加载", "按钮点击"],
      "server_signals": ["API 响应", "数据库操作"],
      "reference_file": "modules/personal-center.md"
    }
  ]
}
```

---

## 状态枚举

### status 字段

| 值 | 含义 | 使用场景 |
|------|------|---------|
| `active` | 活跃 | 当前有效、正在使用的用例/JSON |
| `deprecated` | 已废弃 | 需求变更导致不再适用 |
| `draft` | 草稿 | 配置不完整（如 i18n JSON 缺少 URL） |

---

## 脚本工具

| 脚本 | 用途 |
|------|------|
| `upsert_testcase_index.py` | 新增/更新索引条目 |
| `validate_testcase_index.py` | 校验测试用例索引 |
| `validate_i18n_index.py` | 校验多语言索引 |
| `validate_i18n_json.py` | 校验单个多语言 JSON |
| `validate_index.py` | 校验模块索引 |
| `cleanup_testcase_store.py` | 清理过期/孤立文件 |
| `diff_testcase_indexes.py` | 比较索引差异 |
| `export_testcase_report.py` | 生成覆盖率报告 |
| `generate_testcase_from_template.py` | 从模板生成用例 |
| `xlsx_append_and_highlight.py` | Excel 追加标黄 |

---

## 其他术语

### Template (模板)

预定义的 Excel 或 JSON 骨架，用于保证输出格式一致性。

**当前模板**：
- `minimax-xlsx` - 测试用例 Excel 模板
- `i18n-schema-v1` - 多语言 JSON Schema

### Source References (源引用)

生成用例时所依据的需求来源，如：
- 需求文档路径
- PRD 文件
- 接口说明
- Axure 原型路径

### Tags (标签)

高价值业务标签，用于分类检索。

**推荐标签**：
- `功能测试`
- `P0` / `P1` / `P2` (优先级)
- `多语言`
- `文案校验`
- `回归测试`
- `冒烟测试`

**不推荐**：
- `xlsx` / `json` (格式信息已由 `format` 字段表达)

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-04-01 | 初始版本 |
