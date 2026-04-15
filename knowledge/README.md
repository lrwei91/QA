# 知识库管理 (Knowledge Management)

基于 llm-wiki 框架的个人知识库构建系统，用于持续积累 QA 测试用例相关的领域知识。

## 前置要求

使用前请确保已安装以下依赖：

- **bun** - 运行网页提取工具
- **Google Chrome** - 用于网页渲染和内容提取

详见 [requirements.md](requirements.md) 安装指南。

## 快速开始

### 安装依赖

```bash
# macOS
curl -fsSL https://bun.sh/install | bash
brew install --cask google-chrome

# 启动 Chrome 调试模式
open -na "Google Chrome" --args --remote-debugging-port=9222
```

### 使用方式

通过 `/qa` 命令进入知识库管理：

```
/qa → 选择「3. 知识库管理」→ 选择具体操作
```

### 可用操作

| 操作 | 说明 |
|------|------|
| 消化素材 (ingest) | 将链接/文件/文本整理成 wiki 页面 |
| 查询知识 (query) | 基于已有知识库回答问题 |
| 深度综合 (digest) | 跨素材深度分析，生成综述/对比表/时间线 |
| 健康检查 (lint) | 检测孤立页面、断链、矛盾信息 |
| 知识结晶 (crystallize) | 将有价值的对话沉淀为知识库页面 |
| 查看状态 (status) | 查看知识库当前状态和统计 |

## 支持的素材类型

| 类型 | 状态 | 说明 |
|------|------|------|
| 网页文章 | ✅ 支持 | 需要 Chrome 调试模式 |
| PDF 文件 | ✅ 支持 | 本地文件直接读取 |
| Markdown/文本 | ✅ 支持 | 本地文件直接读取 |
| 纯文本粘贴 | ✅ 支持 | 手动粘贴进入主线 |

## 目录结构

```
knowledge/
├── scripts/              # 处理脚本
│   ├── adapter-state.sh      # 外挂状态检测
│   ├── cache.sh              # 素材缓存管理
│   ├── init-wiki.sh          # 初始化知识库
│   ├── lint-runner.sh        # 健康检查
│   └── ...
├── templates/            # wiki 模板
│   ├── entity-template.md    # 实体页模板
│   ├── topic-template.md     # 主题页模板
│   ├── source-template.md    # 素材摘要模板
│   └── ...
├── deps/                 # 依赖工具
│   └── baoyu-url-to-markdown/  # 网页提取工具
├── raw/                  # 原始素材
│   └── articles/             # 网页文章
├── wiki/                 # 知识库内容
│   ├── entities/             # 实体页
│   ├── topics/               # 主题页
│   └── sources/              # 素材摘要
├── index.md              # 知识库索引
├── log.md                # 操作日志
├── purpose.md            # 研究方向
├── requirements.md       # 前置依赖说明
└── SKILL.md              # 能力定义
```

## 核心能力

### 1. 素材消化 (Ingest)

将碎片化的信息变成结构化的 wiki 页面：

1. 隐私自查确认
2. 提取素材内容
3. 保存到 `raw/` 目录
4. 缓存检查（跳过未变化的素材）
5. Step 1：结构化分析（JSON 格式）
6. Step 2：生成 wiki 页面
7. 更新 index.md 和 log.md

### 2. 知识查询 (Query)

基于已有知识库回答问题：

1. 搜索相关 wiki 页面
2. 综合回答用户问题
3. 引用来源（`[[页面名]]` 格式）
4. 如引用≥3 个来源，提示是否保存为持久化页面

### 3. 深度综合 (Digest)

跨素材深度分析，生成持久化报告：

- 深度报告格式
- 对比表格式
- 时间线格式

### 4. 健康检查 (Lint)

检测知识库健康问题：

- 机械检查：孤立页面、断链、索引一致性
- AI 判断：矛盾信息、交叉引用缺失、置信度报告

### 5. 知识结晶 (Crystallize)

将有价值的对话沉淀为知识库页面：

1. 提取核心洞见（3-5 条）
2. 提取关键决策和原因
3. 生成结晶页面
4. 更新 log.md

## 核心原则

- **知识被编译一次，持续维护** - 不是每次查询都从原始文档重新推导
- **置信度标注** - 每个知识点标注来源可信度
- **智能去重** - SHA256 缓存跳过未变化的素材
- **Obsidian 兼容** - 所有内容都是本地 markdown 文件

## 相关文档

- [requirements.md](requirements.md) - 前置依赖安装指南
- [SKILL.md](SKILL.md) - 核心能力与工作流详细说明
- [.wiki-schema.md](.wiki-schema.md) - 知识库配置
