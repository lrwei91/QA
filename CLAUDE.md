# QA 测试用例生成器项目

## 🎯 项目目标
本仓库用于将需求文档（PRD / 页面 / 接口 / 描述）自动转换为结构化测试用例，支持：
- Excel 测试用例生成与追加
- 功能点查询与索引复用
- 测试用例快照与主题页同步
- Figma/Axure 设计稿读取
- 知识库管理与领域知识沉淀

该项目本质是一个 **测试用例生产流水线**，而不是自动化测试执行框架。

---

## 🚪 主入口
- 使用 `/qa` 命令作为统一入口
- 所有测试用例生成、补充、分析、导出均通过该入口触发

---

## 📦 仓库结构说明

```
QA/
├── README.md                        # 快速开始指南
├── CLAUDE.md                        # 项目行为约束（本文件）
├── requirements.txt                 # Python 依赖
├── .claude/commands/qa.md           # /qa 命令入口定义
├── engine/                          # 核心引擎
│   ├── workflows/                   # LangGraph 流程编排
│   │   ├── qa_state.py              # 工作流状态定义
│   │   ├── qa_nodes.py              # 流程节点定义
│   │   ├── qa_workflow.py           # 工作流构建
│   │   └── utils.py                 # 工具函数
│   ├── skills_python/               # Python 技能模块
│   │   ├── testcase_generate.py     # 测试用例生成
│   │   ├── testcase_format.py       # 测试用例格式化
│   │   ├── figma_reader.py          # Figma 读取器
│   │   └── README.md                # 技能说明
│   ├── scripts/                     # 确定性处理脚本
│   │   # 索引管理
│   │   ├── upsert_testcase_index.py     # 新增/更新测试用例索引
│   │   ├── validate_testcase_index.py   # 校验测试用例索引
│   │   ├── validate_index.py            # 校验模块索引
│   │   ├── cleanup_testcase_store.py    # 清理过期用例
│   │   ├── diff_testcase_indexes.py     # 比较索引差异
│   │   # Excel 处理
│   │   ├── xlsx_fill_testcase_template.py   # Excel 模板填充
│   │   ├── xlsx_append_and_highlight.py     # 追加用例并标黄
│   │   # 快照与同步
│   │   ├── snapshot_testcase.py         # 从 Excel 生成快照
│   │   ├── sync_testcase_snapshot.py    # 同步快照到主题页
│   │   ├── view_snapshot_history.py     # 查看快照历史
│   │   # 报告与导出
│   │   ├── export_testcase_report.py    # 生成覆盖率报告
│   │   # Axure/Figma 解析
│   │   ├── parse_axure_html.py          # 解析 Axure HTML
│   │   ├── save_axure_to_wiki.py        # 保存 Axure 到 wiki
│   │   ├── save_figma_to_wiki.py        # 保存 Figma 到 wiki
│   │   └── generate_testcase_md.py      # 生成 MD 测试用例
│   └── skills/                      # AI 技能定义
│       ├── testcase-generate/       # 生成测试用例（需求 → 用例）
│       ├── testcase-augment/        # 补充已有用例（缺口分析 → 追加）
│       ├── testcase-analyze/        # 分析需求
│       ├── testcase-format/         # Excel 导出与索引更新
│       ├── figma-reader/            # Figma 设计稿读取
│       └── axure-parser/            # Axure HTML 解析
├── knowledge/                       # 知识库（基于 llm-wiki）
│   ├── SKILL.md                     # 知识库能力定义
│   ├── README.md                    # 知识库使用指南
│   ├── requirements.md              # 前置依赖安装说明
│   ├── index.md                     # 知识库索引
│   ├── wiki/                        # 知识库内容
│   │   ├── domain/                  # 领域知识（24 个领域）
│   │   │   ├── 运营活动.md          # 任务/锦标赛/充值活动/洗码
│   │   │   ├── 财务系统.md          # 充值/提现/支付/账目
│   │   │   ├── 账号访问.md          # 认证/账号/权限/组织/KYC
│   │   │   ├── 代理管理.md          # 代理/佣金/团队/ROI
│   │   │   └── ...
│   │   ├── topics/                  # 测试主题页
│   │   ├── testcases/               # MD 测试用例文档
│   │   └── sources/                 # 素材摘要
│   ├── rules/                       # 规则与索引
│   │   ├── module-index.json        # 模块索引（51+ 业务模块）
│   │   ├── platform-rules.md        # 客户端/账服划分规则
│   │   ├── system-map.md            # 跨模块联动规则
│   │   ├── testcase-taxonomy.md     # 测试覆盖分类
│   │   ├── output-template.md       # 输出模板
│   │   ├── testcase-store.md        # 存储规则
│   │   ├── update-governance.md     # 更新治理
│   │   └── domain-template.md       # 领域文档模板
│   ├── scripts/                     # 知识库处理脚本
│   ├── templates/                   # wiki 模板
│   ├── deps/                        # 依赖工具
│   │   └── baoyu-url-to-markdown/   # 网页提取工具（需 bun + Chrome）
│   └── raw/                         # 原始素材
├── docs/                            # 用户文档
│   ├── user-guide.md                # 用户指南
│   ├── contributing.md              # 贡献指南
│   ├── troubleshooting.md           # 故障排查与避坑指南
│   ├── glossary.md                  # 术语词典
│   ├── changelog.md                 # 变更日志
│   ├── workflow-guide.md            # LangGraph 工作流指南
│   ├── figma-guide.md               # Figma 配置指南
│   ├── axure-export-guide.md        # Axure 导出指南
│   └── testcase-sync.md             # 测试用例自动同步机制
├── outputs/                         # 产物仓库
│   ├── generated/                   # 测试用例 Excel
│   ├── snapshots/                   # 快照文件
│   └── testcase-index.json          # 用例索引（11+ 用例）
└── templates/                       # Excel 模板
    └── testcase_template.xlsx       # 标准测试用例模板
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
- 优先使用 testcase-index.json 判断模块
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
- 创建新的领域知识文档

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

**重要说明：** 以下"Skills"是内部能力模块文档（SKILL.md），不是独立的命令行技能。
用户**只能通过 `/qa` 统一入口**进行操作，不能直接调用 `/testcase-generate` 等命令。

| 能力模块 | 职责 | 触发场景 |
|----------|------|----------|
| `testcase-generate` | 从需求生成测试用例 | 用户提供 PRD/页面/描述，需要生成用例 |
| `testcase-augment` | 补充已有用例 | 用户提供已有用例，需要补充遗漏 |
| `testcase-format` | Excel 导出与索引更新 | 需要导出 Excel 或更新索引 |
| `testcase-analyze` | 分析需求 | 需要分析需求结构、识别测试点 |
| `figma-reader` | Figma 设计稿读取 | 用户提供 Figma 链接，需要提取 UI 数据 |
| `axure-parser` | Axure HTML 解析 | 用户提供 Axure HTML，需要提取 UI 结构 |
| `knowledge` | 知识库管理 | 消化素材/查询知识/深度综合/健康检查 |

**唯一用户入口：** `/qa`

---

## 📋 快速开始

```bash
# 生成测试用例
/qa → 选择「生成测试用例」→ 选择冒烟/完整用例 → 提供需求内容 → (可选) 提供 Figma/Axure 链接

# 补充已有用例
/qa → 选择「补充已有用例」→ 选择模块和用例 → 提供补充内容

# 知识库管理
/qa → 选择「知识库管理」→ 选择消化素材/查询知识/深度综合/健康检查/知识结晶/查看状态

# 同步已生成用例
/qa → 选择「同步已生成用例」→ 选择同步单个/全部文件

# Figma 设计稿读取
/qa → 生成测试用例 → 提供 Figma 链接 (可选)

# Axure 设计稿读取
/qa → 生成测试用例 → 提供 Axure HTML 目录 (可选)
```

**前置依赖安装：** 知识库管理功能需要安装 `bun` 和 `Google Chrome`，详见 [knowledge/requirements.md](knowledge/requirements.md)

**Figma MCP 配置：** 使用前需完成 Figma MCP 配置，详见 [docs/figma-mcp-guide.md](docs/figma-mcp-guide.md)

---

## 🔧 常用命令速查

| 用途 | 命令 |
|------|------|
| 生成测试用例 | `/qa 生成测试用例` |
| 补充已有用例 | `/qa 补充已有用例` |
| 仅分析需求 | `/qa 仅分析需求，不生成用例` |
| 同步已生成用例 | `/qa 同步已生成用例` |
| 重建索引 | `python3 engine/scripts/upsert_testcase_index.py --all` |
| 校验测试用例索引 | `python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json` |
| 校验模块索引 | `python3 engine/scripts/validate_index.py knowledge/rules/module-index.json` |
| 生成覆盖率报告 | `python3 engine/scripts/export_testcase_report.py --output outputs/coverage_report.md` |
| 查看快照历史 | `python3 engine/scripts/view_snapshot_history.py outputs/snapshots/<模块>/<用例>/` |

---

## 📊 当前状态

| 类型 | 数量 | 最新更新时间 |
|------|------|-------------|
| 业务模块 | 51+ | 2026-04-16 |
| 领域知识 | 24 | 2026-04-16 |
| 已生成用例 | 11+ | 2026-04-16 |
| 测试主题页 | 7+ | 2026-04-16 |

**索引文件：** `outputs/testcase-index.json`
**知识库索引：** `knowledge/index.md`
**模块索引：** `knowledge/rules/module-index.json`
