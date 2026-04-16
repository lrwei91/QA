# 贡献指南

欢迎参与 QA 测试用例生成器项目的贡献！本文档定义了代码标准、提交流程和协作规范。

---

## 目录

- [代码标准](#代码标准)
- [提交规范](#提交规范)
- [PR 流程](#pr-流程)
- [测试要求](#测试要求)
- [文档规范](#文档规范)
- [版本发布](#版本发布)

---

## 代码标准

### Python 脚本规范

**1. 文件头注释**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称 - 简短描述

用途：详细说明脚本的功能
使用示例：python3 script_name.py --arg value
"""
```

**2. 参数解析**

所有脚本必须使用 `argparse` 支持 `--help`：

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='新增/更新测试用例索引',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python3 upsert_testcase_index.py --all
  python3 upsert_testcase_index.py outputs/generated/模块/用例.xlsx
  python3 upsert_testcase_index.py outputs/generated/模块/用例.xlsx
        '''
    )
    parser.add_argument(
        'file_path',
        nargs='?',
        help='测试用例文件路径'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='全量重建所有索引'
    )
    return parser.parse_args()
```

**3. 错误处理**

```python
import sys

def main():
    try:
        # 主逻辑
        pass
    except FileNotFoundError as e:
        print(f"ERROR: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**4. 路径处理**

```python
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parents[2]

# 使用相对路径
INDEX_FILE = ROOT_DIR / 'testcases' / 'testcase-index.json'
```

**5. 日志输出**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logging.info('处理成功：%(file)s', {'file': 'example.xlsx'})
logging.warning('跳过缺失文件：%(path)s', {'path': '...'})
logging.error('校验失败：%(reason)s', {'reason': '...'})
```

---

### JSON 格式规范

**1. 缩进与编码**

```json
{
  "key": "value"
}
```

- 缩进：2 个空格
- 编码：UTF-8
- 行尾：LF (Unix)

**2. 索引条目字段顺序**

```json
{
  "id": "...",
  "group_key": "...",
  "title": "...",
  "module": "...",
  "module_ids": [],
  "topic": "...",
  "platform_scope": "...",
  "format": "...",
  "rel_path": "...",
  "template": "...",
  "source_refs": [],
  "tags": [],
  "status": "...",
  "created_at": "...",
  "updated_at": "..."
}
```

**3. 时间格式**

```json
"created_at": "2026-04-01T12:00:00Z"
"updated_at": "2026-04-01T12:00:00Z"
```

使用 ISO 8601 格式，UTC 时间。

---

### Excel 模板规范

**1. 列顺序（固定）**

| 列号 | 列名 |
|------|------|
| A | 序号 |
| B | 平台 |
| C | 模块 |
| D | 功能点 |
| E | 前置条件 |
| F | 操作步骤 |
| G | 预期结果 |
| H | 测试结果 |
| I | 备注 |

**2. 样式要求**

- 表头：加粗、背景色填充
- 序号：从 1 开始连续编号
- 优先级：在备注列使用【P0】、【P1】、【P2】格式
- 测试类型：在备注列使用【功能测试】、【边界测试】等

---

## 提交规范

### Git Commit Message

遵循 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 格式调整（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

**Scope 范围：**
- `index`: 索引相关
- `script`: 脚本工具
- `template`: 模板
- `doc`: 文档
- `skill`: 技能包逻辑

**示例：**

```
feat(index): 添加测试用例索引支持

- 新增 testcase-index.json 索引文件
- 修改 upsert_testcase_index.py 支持索引更新
- 添加 validate_testcase_index.py 校验脚本

Fixes: #123
```

```
fix(script): 修复平台值标准化逻辑

- 修正 PLATFORM_MAPPING 字典的键匹配
- 添加未匹配值的警告日志

Closes: #145
```

---

## PR 流程

### 1. 创建分支

```bash
# 从 main 分支创建功能分支
git checkout -b feature/add-glossary
```

### 2. 开发与自测

```bash
# 运行索引校验
python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json

# 运行模块索引校验
python3 engine/scripts/validate_index.py engine/references/module-index.json

# 检查依赖
pip3 install -r engine/requirements.txt
```

### 3. 提交代码

```bash
# 添加变更
git add GLOSSARY.md

# 提交（遵循 commit message 规范）
git commit -m "docs: 添加术语词典 GLOSSARY.md"

# 推送
git push origin feature/add-glossary
```

### 4. 创建 Pull Request

PR 描述模板：

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 重构

## 变更描述
简要描述本次 PR 的目的和变更内容

## 测试
- [ ] 已运行索引校验
- [ ] 已验证脚本可正常执行
- [ ] 已检查依赖安装

## 相关链接
- Issue: #xxx
- 需求文档：[链接]
```

### 5. Code Review

审查要点：
- [ ] 代码符合本规范
- [ ] 索引格式正确
- [ ] 路径使用相对路径
- [ ] 无敏感信息泄露

---

## 测试要求

### 脚本测试

**1. 索引校验脚本**

```bash
# 测试测试用例索引
python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json

# 期望输出：
# ✓ 索引格式正确
# ✓ 所有 rel_path 指向的文件存在
# ✓ platform_scope 值规范
```

**2. 模块索引校验**

```bash
# 测试模块索引
python3 engine/scripts/validate_index.py engine/references/module-index.json

# 期望输出：
# ✓ 模块 ID 唯一
# ✓ 依赖关系有效
```

### 覆盖率目标

```bash
# 使用 pytest 运行测试（未来实现）
pytest --cov=engine/scripts test/

# 目标：60%+ 覆盖率
```

---

## 文档规范

### 文档结构

**1. README.md**
- 项目概览
- 核心能力
- 目录结构
- 常用命令
- 联系信息

**2. QUICKSTART.md**
- 环境准备
- 快速体验
- 常用命令速查
- 输出示例

**3. SKILL.md**
- 技能包详细规则
- 处理流程
- 质量检查清单

**4. GLOSSARY.md**
- 术语定义
- 概念说明
- 使用示例

### 文档写作风格

- 使用简体中文
- 代码块标注语言
- 表格对齐
- 链接使用相对路径

---

## 版本发布

### 版本号规则

遵循语义化版本（SemVer）：

```
MAJOR.MINOR.PATCH
```

- `MAJOR`: 不兼容的变更
- `MINOR`: 向后兼容的功能
- `PATCH`: 向后兼容的修复

### 发布清单

**v1.0.0（初始版本）**
- [x] 测试用例生成
- [x] 索引结构
- [x] 10 个管理脚本
- [x] 基础文档

**v1.1.0（计划）**
- [ ] CLI --help 支持
- [ ] 单元测试覆盖
- [ ] templates/ 目录

### 发布步骤

1. 更新 CHANGELOG.md
2. 更新版本号（如适用）
3. 创建 Git 标签
4. 发布说明

```bash
# 打标签
git tag -a v1.0.0 -m "v1.0.0 - 初始版本"

# 推送标签
git push origin v1.0.0
```

---

## 联系与支持

- Issue 追踪：[GitHub Issues](https://github.com/...)
- 技能包文档：`engine/SKILL.md`
- 脚本说明：已整合至根目录 `README.md` 的「脚本工具说明」章节
- 快速入门：`user-guide.md`

---

## 许可证

本项目遵循项目内部许可条款。
