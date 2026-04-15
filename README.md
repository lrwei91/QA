# QA Test Case Generator - 测试用例生成器

> 将需求文档/PRD/接口说明自动转换为结构化测试用例，支持 Excel 导出和多语言校验

---

## 快速开始

### 步骤概览

1. 安装 Node.js（运行环境）
2. 安装 Claude Code（AI 工具）
3. 安装 Python 依赖
4. 配置 API（使用 cc-switch）
5. 开始生成测试用例

**可选配置：**
- 配置 Figma Reader（基于 Figma REST API 读取设计稿）
- 配置 Axure RP 导出（从原型生成用例）

---

### 1. 安装 Node.js

Node.js 是运行 Claude Code 的必要环境。

**检查是否已安装:**
```bash
node --version
```
如果显示版本号（如 v20.x.x），说明已安装，可跳过此步骤。

**macOS 用户（推荐）:**
```bash
# 使用 Homebrew 安装
brew install node@20
```

**Windows 用户:**
1. 访问 https://nodejs.org/
2. 下载并安装 LTS 版本（推荐）

**验证安装:**
```bash
node --version
npm --version
```
两个命令都显示版本号即表示安装成功。

---

### 2. 安装 Claude Code

Claude Code 是基于命令行的 AI 编程工具。

**全局安装:**
```bash
npm install -g @anthropic/claude-code / sudo npm install -g @anthropic-ai/claude-code
```
```或者
curl -fsSL https://claude.ai/install.sh | bash
```或者
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com

**验证安装:**
```bash
claude --version
```
显示版本号即表示安装成功。

---

### 3. 安装 Python 依赖

QA 技能包需要 Python 依赖来处理 Excel 文件。

**进入项目目录:**
```bash
cd /path/to/QA
```
> 提示：将 `/path/to/QA` 替换为你实际的项目路径

**安装依赖:**
```bash
pip3 install -r requirements.txt
```

> 注意：依赖文件位于项目根目录的 `requirements.txt`

**验证安装:**
```bash
python3 -c "import openpyxl, pandas; print('✓ 依赖安装成功')"
```
显示"依赖安装成功"即表示安装完成。

---

### 4. 配置 API（使用 cc-switch）

Claude Code 需要配置 API 才能使用。

**下载 cc-switch:**
1. 访问 [cc-switch GitHub 仓库](https://github.com/farion1231/cc-switch)
2. 下载并安装 cc-switch 应用
3. 在 cc-switch 中加载你的 API 密钥
4. 启动 Claude Code

**启动 Claude Code:**
```bash
claude
```

---

### 5. 生成第一个测试用例

**准备需求文档**

创建一个新文件 `demo_requirement.md`，内容示例：

```markdown
# 需求：用户登录功能优化

## 功能描述
用户在登录页输入手机号和验证码，点击登录按钮完成登录。

## 规则
1. 手机号格式校验：必须是 11 位数字
2. 验证码有效期：5 分钟
3. 登录失败锁定：连续失败 5 次后锁定 30 分钟
4. 支持单端登录：新设备登录会踢掉旧设备
```

**在 Claude Code 中运行:**

1. 打开终端，进入 QA 项目目录
2. 启动 Claude Code:
   ```bash
   claude
   ```
3. 输入命令:
   ```
   /qa 
   ```
4. 选择「生成测试用例」选项
5. 粘贴你的需求文档内容

**导出 Excel:**
生成完成后，选择「导出为 Excel 文件」选项即可。

生成的用例将保存到：
```
outputs/generated/认证中心/用户登录功能优化.xlsx
```

---

## 可选：配置 Figma Reader

Figma Reader 使用 **Figma REST API** 直接读取 UI 设计稿中的文案、组件和状态信息，用于生成测试用例。

**快速配置:**

```bash
# 1. 获取 Figma Token (https://figma.com/settings → Personal access tokens)
# 2. 添加到环境变量
export FIGMA_ACCESS_TOKEN="figd_xxxxxxxxxxxxxx"

# 3. 配置环境变量后即可使用
# Figma Reader 直接调用 REST API，无需额外配置 MCP 服务器
```

**详细配置指南:** [docs/figma-guide.md](docs/figma-guide.md)

**使用方式:**
```
/qa 生成测试用例 → 提供需求文档 → 提供 Figma 链接 (可选)
```

---

## 可选：配置 Axure RP 导出

Axure RP 导出的 HTML 文件可以提取 UI 结构、元件信息和交互说明，用于生成测试用例。

**快速导出:**

1. 在 Axure 中：发布 → 生成 HTML 文件
2. 勾选选项：
   - 生成原型说明
   - 包含元件注释
   - 包含交互说明
3. 输出目录：`outputs/axure_export/`

**使用方式:**
```
/qa 生成测试用例 → 提供需求文档 → 提供 Axure HTML 目录
```

**详细指南:** [docs/axure-export-guide.md](docs/axure-export-guide.md)

---

## 目录结构

```
QA/
├── README.md                    # 本文档
├── docs/
│   ├── user-guide.md            # 用户指南
│   ├── contributing.md          # 贡献指南
│   ├── troubleshooting.md       # 故障排查与避坑指南
│   ├── glossary.md              # 术语词典
│   ├── changelog.md             # 变更日志
│   ├── workflow-guide.md        # LangGraph 工作流指南
│   ├── figma-guide.md       # Figma Reader / REST API 配置指南
│   └── axure-export-guide.md    # Axure RP 导出指南
├── engine/         # 技能包核心
│   ├── SKILL.md                 # 技能包规则
│   ├── references/              # 参考文档
│   │   ├── module-index.json    # 模块索引 (30+ 业务模块)
│   │   ├── testcase-store.md    # 存储规则
│   │   ├── output-template.md   # 输出模板
│   │   └── ...
│   ├── workflows/               # LangGraph 流程编排
│   │   ├── qa_state.py          # 状态定义
│   │   ├── qa_nodes.py          # 节点函数
│   │   ├── qa_workflow.py       # 工作流构建
│   │   └── utils.py             # 工具函数
│   ├── scripts/                 # 脚本工具
│   │   ├── upsert_testcase_index.py
│   │   ├── validate_testcase_index.py
│   │   └── ...
│   └── skills/                  # 技能定义（SKILL.md 文档）
│       ├── testcase-generate/   # 生成测试用例
│       ├── testcase-augment/    # 补充已有用例
│       ├── testcase-format/     # Excel 导出与索引更新
│       ├── figma-reader/        # Figma 设计稿读取
│       └── axure-parser/        # Axure HTML 解析
├── requirements.txt             # Python 依赖
├── outputs/                   # 产物仓库
│   ├── generated/               # 测试用例 Excel
│   ├── i18n/                    # 多语言校验 JSON
│   ├── testcase-index.json      # 用例索引
│   └── i18n-index.json          # 多语言索引
└── templates/                   # Excel/JSON 模板
```

---

## 核心能力

| 能力 | 说明 |
|------|------|
| 需求 → 用例 | 从需求文档/PRD/接口说明自动生成结构化测试用例 |
| 平台拆分 | 自动识别并拆分为「客户端」和「账服」两侧用例 |
| Excel 导出 | 使用 minimax-xlsx 模板保真导出，支持标黄追加 |
| 多语言校验 | 7 种语言文案校验 JSON 生成（en/id/pt/es/bn/tr/fp） |
| 增量补充 | 基于已有用例做增量去重补充，避免重复生成 |
| 索引管理 | 双索引结构管理用例和多语言 JSON，支持关联检索 |
| LangGraph 编排 | 基于 LangGraph 的流程编排，支持重试、并行、复杂条件判断 |

---

## 架构概览

```
用户交互层 (`/qa` 编排入口)
       ↓
Claude（当前对话）← AI 能力提供者
       ↑
LangGraph 编排层 ← Python 流程控制 / 子能力分发
       ↓
Python 脚本层 ← 确定性任务执行
```

**核心原则：**
- Python 负责确定性的、可编程的任务（数据处理、脚本调用、文件操作）
- Claude 负责需要智能的、创造性的任务（测试用例生成、需求分析）
- 两者协作，发挥各自优势

**详细说明：** [docs/workflow-guide.md](docs/workflow-guide.md)

---

## 常用命令速查

| 用途 | 命令 |
|------|------|
| 生成测试用例 | `/qa 生成测试用例` |
| 补充已有用例 | `/qa 补充已有用例` |
| 生成多语言 JSON | `/qa 生成多语言校验 JSON` |
| 仅分析需求 | `/qa 仅分析需求，不生成用例` |
| 重建索引 | `python3 engine/scripts/upsert_testcase_index.py --all` |
| 校验测试用例索引 | `python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json` |
| 校验模块索引 | `python3 engine/scripts/validate_index.py engine/references/module-index.json` |

---

## 脚本工具说明

脚本集中放在 `engine/scripts/`，用于索引维护、Excel 导出、Axure 解析和报告生成。

| 脚本 | 用途 |
|------|------|
| `upsert_testcase_index.py` | 新增/更新测试用例索引 |
| `validate_testcase_index.py` | 校验测试用例索引 |
| `validate_i18n_index.py` | 校验多语言索引 |
| `validate_i18n_json.py` | 校验多语言 JSON |
| `validate_index.py` | 校验模块索引 |
| `cleanup_testcase_store.py` | 清理过期用例 |
| `diff_testcase_indexes.py` | 比较索引差异 |
| `export_testcase_report.py` | 生成覆盖率报告 |
| `generate_testcase_from_template.py` | 从模板生成用例 |
| `xlsx_append_and_highlight.py` | Excel 追加标黄 |
| `parse_axure_html.py` | 解析 Axure HTML |

### 常见脚本示例

```bash
# 全量重建索引
python3 engine/scripts/upsert_testcase_index.py --all

# 校验测试用例索引
python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json

# 校验多语言索引
python3 engine/scripts/validate_i18n_index.py outputs/i18n-index.json

# 校验模块索引
python3 engine/scripts/validate_index.py engine/references/module-index.json

# 预览清理过期用例
python3 engine/scripts/cleanup_testcase_store.py --dry-run

# 生成覆盖率报告
python3 engine/scripts/export_testcase_report.py --output outputs/coverage_report.md

# 解析 Axure HTML
python3 engine/scripts/parse_axure_html.py outputs/axure_export/ --recursive
```

---

## LangGraph 工作流

项目使用 LangGraph 作为流程编排层，提供以下能力：

### 工作流类型

| 工作流 | 用途 | 流程图 |
|--------|------|--------|
| Generate | 生成测试用例 | `parse_input → [read_figma] → generate_test_cases → [check_i18n] → export_excel` |
| Augment | 补充已有用例 | `load_existing_cases → analyze_gaps → generate_augment_cases → append_to_excel` |
| Analyze | 需求分析 | `parse_input → analyze_requirements → output_analysis` |

### 环境变量

| 变量 | 用途 | 必需 |
|------|------|------|
| `FIGMA_ACCESS_TOKEN` | Figma REST API | 读取 Figma 时需要 |
| `ANTHROPIC_API_KEY` | **不需要配置** | ❌ |

**注意：** 在 Claude Code 环境中运行时，不需要配置 `ANTHROPIC_API_KEY`，AI 能力由当前对话的 Claude 提供。

### 基本用法

```python
from workflows import QAWorkflowState, build_qa_workflow

workflow = build_qa_workflow()

state: QAWorkflowState = {
    "workflow_type": "generate",
    "case_type": "full",
    "input_content": "你的需求内容",
    "input_source": "text",
    "errors": [],
}

result = workflow.invoke(state)
```

**详细文档：** [docs/workflow-guide.md](docs/workflow-guide.md)

---

## 输出示例

### 测试用例 Excel 结构

| 序号 | 平台 | 模块 | 功能点 | 前置条件 | 操作步骤 | 预期结果 | 测试结果 | 备注 |
|------|------|------|--------|----------|----------|----------|----------|------|
| 1 | 客户端 | 认证中心 | 手机号格式校验 | 已进入登录页 | 1、输入非 11 位手机号<br>2、点击获取验证码 | 1、提示"手机号格式错误"<br>2、不发送验证码 | | 【功能测试】【P0】 |
| 2 | 账服 | 认证中心 | 验证码校验 | 1、手机号已发送验证码<br>2、验证码在有效期内 | 1、输入正确验证码<br>2、点击登录 | 1、登录成功<br>2、返回 token | | 【功能测试】【P0】 |

### 多语言 JSON 结构

```json
{
  "name": "个人中心 - 免费旋转记录",
  "url": "https://example.com/free-spin-record",
  "preScriptPath": "",
  "languages": {
    "en-us": { "title": "Free Spin Record", ... },
    "id-id": { "title": "Catatan Putaran Gratis", ... },
    "pt-pt": { "title": "Registo de Rodadas Grátis", ... },
    "es-es": { "title": "Registro de Tiradas Gratis", ... },
    "bn-bn": { "title": "ফ্রি স্পিন রেকর্ড", ... },
    "tr-tr": { "title": "Ücretsiz Dönüş Kaydı", ... },
    "fp-fp": { "title": "Tala ng Libreng Spin", ... }
  },
  "options": {
    "matchRule": "normalized-exact",
    "captureRegion": { "x": 0, "y": 0, "width": 0, "height": 0 }
  }
}
```

---

## 遇到问题？

**常见问题排查:**

1. **Node.js 未安装**: 执行 `node --version` 检查，未安装请参考步骤 1
2. **Claude Code 无法启动**: 执行 `claude --version` 检查，未安装请参考步骤 2
3. **API 配置问题**: 确认 cc-switch 已正确配置 API 密钥
4. **Python 依赖缺失**: 重新执行步骤 3 安装依赖
5. **Figma Reader 读取失败**: 检查 Token 是否有效，参考 [Figma 配置指南](docs/figma-guide.md)

**更多帮助:**

1. 查看 [故障排查与避坑指南](docs/troubleshooting.md) - 常见问题和最佳实践
2. 运行诊断工具:
   ```bash
   python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json
   ```
4. 在 GitHub Issues 中搜索或提问

---

## 下一步学习

- [用户指南](docs/user-guide.md) - 详细使用说明
- [贡献指南](docs/contributing.md) - 代码规范与提交流程
- [故障排查](docs/troubleshooting.md) - 常见问题解决方案
- [术语词典](docs/glossary.md) - 核心术语定义
- [变更日志](docs/changelog.md) - 版本历史记录
- [工作流指南](docs/workflow-guide.md) - LangGraph 工作流架构与使用

---

## 版本

当前版本：v2.0.0 | [变更日志](docs/changelog.md)
