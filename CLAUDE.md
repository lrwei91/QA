# QA Test Case Generation Project

## 🎯 项目目标
本仓库用于将需求文档（PRD / 页面 / 接口 / 描述）转换为结构化测试用例，并支持：
- Excel 测试用例生成与追加
- 多语言 JSON 校验与导出
- 测试用例索引与复用

该项目本质是一个 **测试用例生产流水线**，而不是自动化测试执行框架。

---

## 🚪 主入口
- 使用 `/qa` 命令作为统一入口
- 所有测试用例生成、补充、分析、导出均通过该入口触发

---

## 📦 仓库结构说明

```
QA/
├── .claude/commands/qa.md              # 用户交互入口
├── engine/
│   ├── skills/                         # 测试用例相关技能
│   │   ├── testcase-generate/          # 核心生成：需求 → 测试用例
│   │   ├── testcase-augment/           # 增量补充：分析缺口 → 追加用例
│   │   ├── testcase-analyze/           # 需求分析：模块拆分 → 测试点清单
│   │   ├── testcase-i18n/              # 多语言处理：JSON 校验 → 一致性检查
│   │   └── testcase-format/            # 工程化处理：Excel 导出 → 索引更新
│   ├── references/                     # 规则库
│   │   ├── index-rules/                # 索引与规则
│   │   │   ├── module-index.json       # 模块索引
│   │   │   ├── platform-rules.md       # 客户端/账服划分规则
│   │   │   └── system-map.md           # 跨模块联动规则
│   │   ├── test-design/                # 测试设计
│   │   │   ├── testcase-taxonomy.md    # 测试覆盖分类
│   │   │   └── output-template.md      # 输出模板
│   │   ├── domain-knowledge/           # 领域知识
│   │   ├── module-account-access.md    # 账号访问领域：认证/账号/权限/组织/KYC
│   │   ├── finance-system.md           # 充值提现领域：充值/提现/支付/账目
│   │   ├── marketing-activities.md     # 运营活动领域：任务/锦标赛/充值活动/洗码
│   │   └── affiliate-management.md     # 全民代领域：代理/佣金/团队/ROI
│   │   └── engineering/                # 工程规范
│   │       ├── testcase-store.md       # 工作区索引约定
│   │       ├── update-governance.md    # 更新治理
│   │       └── domain-template.md      # 领域文档模板
│   └── scripts/                        # 确定性处理脚本
│       ├── xlsx_fill_testcase_template.py  # Excel 模板填充
│       ├── xlsx_append_and_highlight.py    # 追加用例并标黄
│       ├── upsert_testcase_index.py        # 新增/更新索引
│       ├── validate_index.py               # 模块索引校验
│       ├── validate_testcase_index.py      # 测试用例索引校验
│       ├── validate_i18n_json.py           # 多语言 JSON 校验
│       └── ...
├── outputs/
│   ├── generated/                      # 生成的测试用例 Excel
│   ├── i18n/                           # 多语言 JSON
│   ├── testcase-index.json             # 测试用例索引
│   └── i18n-index.json                 # 多语言索引
└── templates/
    └── testcase_template.xlsx          # Excel 模板
```

---

## 🧠 核心原则（全局约束）

### 1. 平台划分必须严格
仅允许：
- `客户端`（UI/交互/提示/展示）
- `账服`（接口/状态/权限/后台/落库）

禁止：
- "后台"、"管理后台"等非标准名称

---

### 2. 测试用例必须结构化
必须包含：
- 模块
- 功能点
- 前置条件
- 操作步骤
- 预期结果

禁止：
- 模糊描述（如"正常显示"）
- 缺少断言

---

### 3. 输出必须遵循模板
- 严格按 Excel 模板字段输出
- 不得随意新增/删除列
- 不得改变列顺序

---

### 4. 增量优先（避免覆盖）
- 补充用例时必须追加
- 不覆盖已有测试用例
- 新增行需可标识（高亮/标记）

---

### 5. 优先复用历史数据
- 优先使用 testcase index 判断模块
- 避免重复造轮子
- 保持命名一致性

---

### 6. 生成 ≠ 执行
该项目不负责：
- UI 自动化执行
- Playwright 脚本运行
- 测试结果验证

只负责：
👉 **高质量测试用例生成**

---

## ⚙️ 行为准则

Claude 在本仓库中应：

- 优先调用已有 skill，而不是自由发挥
- 优先结构化输出，而不是自然语言描述
- 优先遵循 references，而不是重新定义规则
- 保持输出稳定、可重复、可维护

---

## 🚫 修改策略

允许：
- 增加测试用例
- 更新索引
- 扩展 references

谨慎：
- 修改 SKILL.md
- 修改模板

禁止：
- 破坏已有数据结构
- 改变核心字段定义

---

## 📌 一句话总结
这是一个 **"AI 驱动的测试用例生成系统"**，  
所有行为都应围绕 **结构化、稳定、可复用** 展开。

---

## 🛠️ Skills 索引

| Skill | 职责 | 触发场景 |
|-------|------|----------|
| [`testcase-generate`](engine/skills/testcase-generate/SKILL.md) | 从需求生成测试用例 | 用户提供 PRD/页面/描述，需要生成用例 |
| [`testcase-augment`](engine/skills/testcase-augment/SKILL.md) | 补充已有用例 | 用户提供已有用例，需要补充遗漏 |
| [`testcase-analyze`](engine/skills/testcase-analyze/SKILL.md) | 仅分析需求 | 用户只想评估需求质量，不生成用例 |
| [`testcase-i18n`](engine/skills/testcase-i18n/SKILL.md) | 多语言 JSON 校验 | 需要校验多语言文案完整性 |
| [`testcase-format`](engine/skills/testcase-format/SKILL.md) | Excel 导出与索引更新 | 需要导出 Excel 或更新索引 |
| [`figma-reader`](engine/skills/figma-reader/SKILL.md) | Figma 设计稿读取 | 用户提供 Figma 链接，需要提取 UI 数据 |

---

## 📋 快速开始

```bash
# 生成测试用例
/qa → 选择「生成测试用例」→ 选择冒烟/完整用例 → 提供需求内容 → (可选) 提供 Figma 链接

# 补充已有用例
/qa → 选择「补充已有用例」→ 选择模块和用例 → 提供补充内容

# 分析需求
/qa → 选择「仅分析需求」→ 提供需求内容

# 多语言校验
/qa → 选择「生成多语言校验 JSON」→ 提供多语言文案

# Figma 设计稿读取
/qa → 生成测试用例 → 提供 Figma 链接 (可选)
```

**Figma MCP 配置：** 使用前需完成 Figma MCP 配置，详见 [docs/figma-mcp-guide.md](docs/figma-mcp-guide.md)
