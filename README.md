# QA Test Case Generator - 测试用例生成器

> 将需求文档/PRD/接口说明自动转换为结构化测试用例，支持 Excel 导出和多语言校验

---

## 快速开始

### 1. 安装 Claude Code

**macOS (Homebrew):**
```bash
brew install claude-code
```

**npm 全局安装:**
```bash
npm install -g @anthropic/claude-code
```

**验证安装:**
```bash
claude --version
```

**登录认证:**
```bash
claude login
```

详细文档：[Claude Code 官方文档](https://docs.anthropic.com/claude-code/)

---

### 2. 安装 AionUi Skills

AionUi 是 Claude Code 的技能管理平台，用于加载和管理 QA 测试用例生成器技能。

**方法一：通过 AionUi CLI（推荐）**
```bash
# 安装 AionUi CLI
npm install -g @aionui/cli

# 登录 AionUi
aionui login

# 安装 QA 技能包
aionui skill install test-case-generator
```

**方法二：手动配置**

1. 在 Claude Code 工作区创建 `.aionui/skills` 目录
2. 将本项目的 `test-case-generator` 目录复制或 symlink 到该目录
3. 重启 Claude Code

**方法三：使用内置 skill-creator**
```bash
# 在 Claude Code 中运行
/skill-creator
```

详细文档：[AionUi Skills 平台](https://aionui.com/docs)

---

### 3. 安装 Python 依赖

```bash
cd test-case-generator
pip3 install -r requirements.txt
```

**验证安装:**
```bash
python3 -c "import openpyxl, pandas; print('✓ 依赖安装成功')"
```

---

### 4. 生成第一个测试用例

**准备需求文档** `demo_requirement.md`:
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
```
/qa 生成测试用例
```

粘贴需求文档内容，选择「生成测试用例」选项。

**导出 Excel:**
```
/qa 导出 Excel
```

生成的用例会保存到：
```
testcases/generated/认证中心/用户登录功能优化_YYYYMMDD.xlsx
```

---

## 目录结构

```
QA/
├── README.md                    # 本文档
├── docs/
│   ├── user-guide.md            # 用户指南
│   ├── contributing.md          # 贡献指南
│   ├── troubleshooting.md       # 故障排查
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

## 下一步学习

- [用户指南](docs/user-guide.md) - 详细使用说明
- [贡献指南](docs/contributing.md) - 代码规范与提交流程
- [故障排查](docs/troubleshooting.md) - 常见问题解决方案
- [术语词典](docs/glossary.md) - 核心术语定义
- [变更日志](docs/changelog.md) - 版本历史记录

---

## 遇到问题？

1. 查看 [故障排查指南](docs/troubleshooting.md)
2. 运行诊断工具：
   ```bash
   python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
   python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json
   ```
3. 在 GitHub Issues 中搜索或提问

---

## 版本

当前版本：v1.0.0 | [变更日志](docs/changelog.md)
