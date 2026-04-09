---
name: axure-parser
description: 解析 Axure RP 导出的 HTML - 提取页面结构、元件、注释和交互说明，供测试用例生成使用
---

# Skill: Axure Parser

## 触发场景

- 用户提供 Axure RP 导出的 HTML 文件
- 用户提供 Axure 导出 HTML 的目录
- 需要从 Axure 原型提取需求信息
- 补充需求文档中的 UI 细节

## 职责

1. **解析 HTML 文件** - 使用 `parse_axure_html.py` 脚本解析
2. **提取页面结构** - 页面名称、层级关系
3. **提取元件信息** - 按钮、输入框、表格等组件
4. **提取注释说明** - Axure 元件注释、说明文字
5. **输出结构化数据** - 供 `testcase-generate` 使用

## 输入格式

### 1. 单个 HTML 文件

```
输入：testcases/axure_export/login_page.html
输出：单个页面的结构化数据
```

### 2. HTML 目录

```
输入：testcases/axure_export/
输出：所有 HTML 文件的聚合数据
```

### 3. 递归目录

```
输入：testcases/axure_export/ --recursive
输出：包括子目录所有 HTML 文件的聚合数据
```

## 输出格式

### 1. 原始解析数据

```json
{
  "source": "axure",
  "file": "path/to/file.html",
  "pages": [
    {
      "name": "登录页",
      "id": "page_001",
      "components": [],
      "annotations": []
    }
  ],
  "components": [
    {
      "id": "comp_001",
      "name": "手机号输入框",
      "type": "input",
      "parent": "page_001",
      "page": "登录页"
    }
  ],
  "annotations": [
    {
      "page": "登录页",
      "content": "手机号必须是 11 位数字",
      "element_id": "comp_001"
    }
  ],
  "summary": {
    "page_count": 1,
    "component_count": 5,
    "annotation_count": 3
  }
}
```

### 2. 测试用例格式

```json
{
  "source": "axure",
  "modules": [
    {
      "name": "登录页",
      "source": "axure_page"
    }
  ],
  "function_points": [
    {
      "module": "登录页",
      "name": "手机号输入框",
      "type": "input"
    }
  ],
  "ui_elements": [
    {
      "module": "登录页",
      "element_name": "手机号输入框",
      "element_type": "input"
    }
  ],
  "interactions": [],
  "constraints": [
    {
      "module": "登录页",
      "description": "手机号必须是 11 位数字",
      "source": "axure_annotation"
    }
  ]
}
```

## 工作流程

### 第 1 步：接收输入

```
用户提供:
- HTML 文件路径，或
- HTML 目录路径
```

### 第 2 步：调用解析脚本

```bash
python3 test-case-generator/scripts/parse_axure_html.py \
    <input_path> \
    --format testcase \
    --output /tmp/axure_data.json
```

### 第 3 步：解析结果

```
▎ Axure HTML 解析完成

文件：testcases/axure_export/login_page.html

【页面结构】
- 已识别 XX 个页面
- 页面列表：登录页、首页、个人中心...

【元件信息】
- 已提取 XX 个元件
- 按钮：XX 个
- 输入框：XX 个
- 表格：XX 个

【注释说明】
- 已提取 XX 条注释
- 约束条件：XX 条
- 交互说明：XX 条

【可用于测试用例的信息】
- 模块：XX 个
- 功能点：XX 个
- UI 元素：XX 项
- 约束条件：XX 条
```

### 第 4 步：传递给 testcase-generate

将解析结果传递给 `testcase-generate` 技能：

```json
{
  "source": "axure",
  "axure_data": { ... },
  "testcase_hints": {
    "modules": ["模块 1", "模块 2"],
    "ui_elements": ["元素 1", "元素 2"],
    "constraints": ["约束 1", "约束 2"]
  }
}
```

## 与 testcase-generate 集成

### 在 /qa 流程中的位置

```
/qa 生成测试用例
  ↓
选择用例类型（冒烟/完整）
  ↓
提供需求文档 ← Axure HTML 作为输入之一
  ↓
(如为 Axure HTML) 调用 axure-parser
  ↓
(可选) 提供 Figma 链接
  ↓
合并 Axure + Figma + 其他需求数据
  ↓
生成测试用例
```

### 数据合并策略

```
优先级：
1. 需求文档（PRD/Word）- 主需求来源
2. Axure HTML - UI 结构和注释
3. Figma 设计稿 - 视觉细节和状态

合并规则：
- 模块识别：以需求文档为准，Axure 补充
- 功能点：合并三方数据，去重
- 约束条件：Axure 注释优先（最详细）
- UI 元素：Axure + Figma 合并
```

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 处理 |
|------|------|------|
| 文件不存在 | 路径错误或文件被移动 | 提示用户确认路径 |
| 解析失败 | HTML 格式不符合预期 | 尝试备用解析策略 |
| 无有效数据 | HTML 中无页面/元件信息 | 提示用户检查导出设置 |
| 编码问题 | 非 UTF-8 编码 | 自动尝试 GBK 等编码 |

### 错误输出格式

```
❌ Axure HTML 解析失败

错误类型：无有效数据

可能原因：
1. Axure 导出时未勾选"生成元件注释"
2. HTML 文件不完整
3. 导出格式不兼容

解决方案：
1. 在 Axure 中重新导出，确保勾选:
   - 生成 HTML 说明
   - 包含元件注释
   - 包含交互说明
2. 提供完整的导出目录
3. 尝试提供 Axure .rp 源文件

如需帮助，请查看：docs/axure-export-guide.md
```

## Axure 导出最佳实践

### 推荐导出设置

```
1. 发布 → 生成 HTML 文件
2. 选项设置:
   ✓ 生成原型说明
   ✓ 包含元件注释
   ✓ 包含交互说明
   ✓ 按页面生成（推荐）
   ✓ 包含母版说明
3. 输出目录：testcases/axure_export/
```

### 元件注释规范

```
在 Axure 中为元件添加注释:
1. 选中元件
2. 右键 → 添加注释
3. 填写内容:
   - 功能说明
   - 输入约束
   - 交互效果
   - 边界条件
```

### 交互说明规范

```
在 Axure 中设置交互:
1. 选中元件
2. 交互面板 → 新建交互
3. 设置:
   - 触发事件（onClick、onChange 等）
   - 目标动作（跳转、显示、隐藏等）
   - 动画效果
```

## 使用脚本

### 基本用法

```bash
# 解析单个文件
python3 test-case-generator/scripts/parse_axure_html.py \
    testcases/axure_export/login_page.html

# 解析目录
python3 test-case-generator/scripts/parse_axure_html.py \
    testcases/axure_export/

# 递归解析
python3 test-case-generator/scripts/parse_axure_html.py \
    testcases/axure_export/ --recursive

# 输出到文件
python3 test-case-generator/scripts/parse_axure_html.py \
    testcases/axure_export/ \
    --output axure_data.json

# 详细模式
python3 test-case-generator/scripts/parse_axure_html.py \
    testcases/axure_export/ \
    --verbose
```

### 脚本选项

| 选项 | 说明 |
|------|------|
| `input_path` | 输入 HTML 文件或目录路径 |
| `--output, -o` | 输出 JSON 文件路径 |
| `--recursive, -r` | 递归搜索子目录 |
| `--format` | 输出格式：`raw`（原始）或 `testcase`（测试用例） |
| `--verbose, -v` | 详细输出模式 |

## 资源文件

- [`parse_axure_html.py`](../../test-case-generator/scripts/parse_axure_html.py) - Axure 解析脚本
- [`testcase-generate/SKILL.md`](../testcase-generate/SKILL.md) - 测试用例生成技能
- [`figma-reader/SKILL.md`](../figma-reader/SKILL.md) - Figma 设计稿读取技能

## 相关 Skills

- [`testcase-generate`](../testcase-generate/SKILL.md) - 从需求生成测试用例
- [`figma-reader`](../figma-reader/SKILL.md) - Figma 设计稿读取
