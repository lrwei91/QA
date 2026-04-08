# QA Test Case Generator - 测试用例生成器

> 将需求文档/PRD/接口说明自动转换为结构化测试用例，支持 Excel 导出和多语言校验

---

## 快速开始

### 步骤概览

1. 安装 Node.js（运行环境）
2. 安装 Claude Code（AI 工具）
3. 配置 API（使用 cc-switch）
4. 安装 Python 依赖
5. 开始生成测试用例

**可选**：安装 AionUi 图形化界面

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
npm install -g @anthropic/claude-code
```

**验证安装:**
```bash
claude --version
```
显示版本号即表示安装成功。

---

### 3. 配置 API（使用 cc-switch）

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

### 4. 安装 Python 依赖

QA 技能包需要 Python 依赖来处理 Excel 文件。

**进入项目目录:**
```bash
cd /path/to/QA/test-case-generator
```
> 提示：将 `/path/to/QA` 替换为你实际的项目路径

**安装依赖:**
```bash
pip3 install -r requirements.txt
```

**验证安装:**
```bash
python3 -c "import openpyxl, pandas; print('✓ 依赖安装成功')"
```
显示"依赖安装成功"即表示安装完成。

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
   /qa 生成测试用例
   ```
4. 粘贴你的需求文档内容
5. 选择「生成测试用例」选项

**导出 Excel:**
```
/qa 导出 Excel
```

生成的用例将保存到：
```
testcases/generated/认证中心/用户登录功能优化_YYYYMMDD.xlsx
```

---

## 可选：安装 AionUi 图形化界面

AionUi 是 Claude Code 的技能管理平台，提供图形化界面。

**下载安装:**
1. 访问 [AionUi GitHub 仓库](https://github.com/iOfficeAI/AionUi)
2. 下载并安装 AionUi 应用
3. 启动 AionUi 并加载 QA 技能包

---

## 目录结构

```
QA/
├── README.md                    # 本文档
├── docs/
│   ├── user-guide.md            # 用户指南
│   ├── contributing.md          # 贡献指南
│   ├── troubleshooting.md       # 故障排查指南
│   ├── lessons-learned.md       # 避坑指南（新增）
│   ├── glossary.md              # 术语词典
│   └── changelog.md             # 变更日志
├── test-case-generator/         # 技能包核心
│   ├── SKILL.md                 # 技能包规则
│   ├── references/              # 参考文档
│   │   ├── module-index.json    # 模块索引 (30+ 业务模块)
│   │   ├── testcase-store.md    # 存储规则
│   │   ├── output-template.md   # 输出模板
│   │   └── ...
│   └── scripts/                 # 脚本工具
│       ├── upsert_testcase_index.py
│       ├── validate_testcase_index.py
│       └── ...
├── testcases/                   # 产物仓库
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

---

## 常用命令速查

| 用途 | 命令 |
|------|------|
| 生成测试用例 | `/qa 生成测试用例` |
| 补充已有用例 | `/qa 补充已有用例` |
| 生成多语言 JSON | `/qa 生成多语言校验 JSON` |
| 仅分析需求 | `/qa 仅分析需求，不生成用例` |
| 重建索引 | `python3 test-case-generator/scripts/upsert_testcase_index.py --all` |
| 校验测试用例索引 | `python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json` |
| 校验模块索引 | `python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json` |

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
4. **Python 依赖缺失**: 重新执行步骤 4 安装依赖

**更多帮助:**

1. 查看 [故障排查指南](docs/troubleshooting.md)
2. 查看 [避坑指南](docs/lessons-learned.md) - 典型问题和最佳实践
3. 运行诊断工具:
   ```bash
   python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
   ```
4. 在 GitHub Issues 中搜索或提问

---

## 下一步学习

- [用户指南](docs/user-guide.md) - 详细使用说明
- [贡献指南](docs/contributing.md) - 代码规范与提交流程
- [故障排查](docs/troubleshooting.md) - 常见问题解决方案
- [术语词典](docs/glossary.md) - 核心术语定义
- [变更日志](docs/changelog.md) - 版本历史记录

---

## 版本

当前版本：v1.0.0 | [变更日志](docs/changelog.md)
