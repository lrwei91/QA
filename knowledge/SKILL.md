---
name: knowledge
description: |
  QA 项目内置知识库管理能力（基于 llm-wiki 框架）。
  触发条件：用户明确提到"知识库"、"wiki"、"消化素材"、"查询知识"、"知识结晶"等，
  或通过 `/qa` 命令选择「知识库管理」选项。
---

# 知识库管理 (Knowledge Management)

基于 llm-wiki 框架的个人知识库构建系统，用于持续积累 QA 测试用例相关的领域知识。

## 核心能力

- **素材消化 (ingest)**：将链接、文件、文本整理成结构化的 wiki 页面
- **知识查询 (query)**：基于已有知识库回答问题
- **深度综合 (digest)**：跨素材深度分析，生成综述/对比表/时间线
- **健康检查 (lint)**：检测孤立页面、断链、矛盾信息
- **结晶化 (crystallize)**：将有价值的对话沉淀为知识库页面

## 工作流路由

| 用户意图 | 工作流 |
|----------|--------|
| "消化"、"添加素材"、给链接/文件 | → **ingest** |
| "查询"、"XX 是什么" | → **query** |
| "深度分析"、"对比"、"时间线" | → **digest** |
| "检查知识库"、"健康检查" | → **lint** |
| "结晶化"、"记进知识库" | → **crystallize** |

## 前置检查

1. 知识库根路径：`/Users/lanye/Documents/QA/knowledge/`
2. 配置文件：`knowledge/.wiki-schema.md`
3. 脚本目录：`knowledge/scripts/`
4. 模板目录：`knowledge/templates/`

## 脚本调用约定

所有脚本通过 `knowledge/scripts/` 调用：

```bash
# 来源注册表
bash knowledge/scripts/source-registry.sh list

# 适配器状态检查
bash knowledge/scripts/adapter-state.sh check <source_id>

# 缓存检查
bash knowledge/scripts/cache.sh check "<文件路径>"

# 健康检查
bash knowledge/scripts/lint-runner.sh <wiki_root>
```

## 输出语言

根据 `.wiki-schema.md` 中的「语言」字段：
- `语言：中文` → 所有输出使用中文
- `语言：English` → 所有输出使用英文

当前配置：**中文**

---

## 外挂状态模型

当前仅支持一个可选外挂：**网页文章**（baoyu-url-to-markdown）。

**适配器状态检查**：

```bash
bash knowledge/scripts/adapter-state.sh check web_article
```

返回状态：
- `not_installed`：未找到 baoyu-url-to-markdown
- `env_unavailable`：Chrome 调试端口 9222 未监听
- `runtime_failed`：自动提取执行失败
- `available`：外挂已可用

**网页文章外挂说明**：
- 依赖：`baoyu-url-to-markdown`（bundled，已内置到 `knowledge/deps/`）
- 环境要求：Chrome 需要以调试模式启动（`--remote-debugging-port=9222`）
- 安装提示：`bash knowledge/install.sh --platform claude`
- 环境提示：`open -na "Google Chrome" --args --remote-debugging-port=9222`
- 回退方式：自动提取失败时，改为复制全文或保存为本地文件后继续

**核心主线不因外挂失败而中断**——外挂失败时改走手动入口即可。

---

## 工作流程详细说明

### 工作流 1：ingest (消化素材)

**隐私自查提示**（首次执行时必须显示）：

> 在开始分析这份素材前，请先确认里面**不**包含这些敏感内容：
> - 手机号码、身份证号、API 密钥、明文密码等
>
> 确认无上述内容请回复 `y`，要中止请回复 `n`。

**处理流程**：
1. 提取素材内容（URL/文件/文本）
2. 保存到 `knowledge/raw/` 对应目录
3. 缓存检查（跳过未变化的素材）
4. Step 1：结构化分析（JSON 格式）
5. Step 2：生成 wiki 页面
6. 更新 index.md 和 log.md

### 工作流 2：query (查询)

1. 搜索相关 wiki 页面
2. 综合回答用户问题
3. 引用来源（`[[页面名]]` 格式）
4. 如引用≥3 个来源，提示是否保存为持久化页面

### 工作流 3：digest (深度综合)

**输出格式**（根据触发词选择）：
- 默认 → 深度报告格式
- "对比"/"比较" → 对比表格式
- "时间线"/"按时间" → 时间线格式

### 工作流 4：lint (健康检查)

1. 脚本检查：孤立页面、断链、索引一致性
2. AI 判断：矛盾信息、交叉引用缺失、置信度报告
3. 输出修复建议

### 工作流 5：crystallize (结晶化)

将有价值的对话内容沉淀为 `knowledge/wiki/synthesis/sessions/{主题}-{日期}.md`

---

## 与 QA 项目的集成

本知识库是 QA 测试用例生成系统的组成部分：

1. **领域知识来源**：`knowledge/wiki/entities/` 和 `knowledge/wiki/topics/` 为测试用例生成提供领域知识
2. **需求文档沉淀**：PRD、Axure、Figma 等需求文档可通过 ingest 工作流转化为知识库
3. **测试用例复用**：知识库中的实体和主题可用于测试用例的模块归属判断

**触发边界**：
- 用户通过 `/qa` → 「知识库管理」选项触发
- 用户直接使用 "消化"、"查询"、"知识库" 等关键词触发
- 单纯 "总结这篇文章" 不触发，需明确 "消化到知识库"

---

## 相关文档

- [README.md](README.md) - 快速开始指南
- [requirements.md](requirements.md) - 前置依赖安装说明
- [.wiki-schema.md](.wiki-schema.md) - 知识库配置
