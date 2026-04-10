---
name: figma-reader
description: 读取 Figma 设计稿数据 - 提取文案、组件结构、设计标注和交互说明，供测试用例生成使用
---

# Skill: Figma Reader

## 触发场景

- 用户提供 Figma 设计稿链接
- 需要从 UI 设计稿提取测试相关信息
- 补充需求文档中缺失的 UI 细节

## 职责

1. **调用 Figma REST API** - 使用 Figma REST API 读取设计稿（不依赖 MCP）
2. **提取文案数据** - 所有文本图层的文字内容
3. **提取组件结构** - Frame/Component 层级关系
4. **提取设计标注** - 尺寸、颜色、状态等
5. **输出结构化数据** - 供 `testcase-generate` 使用

## Figma API 调用方式

**使用直接 API 调用，不依赖 MCP 配置：**

```bash
curl -s \
  -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
  "https://api.figma.com/v1/files/{file_id}/nodes?ids={node_id}"
```

**关键点：**
- 使用 `/nodes` 端点 + `ids` 参数，只读取指定节点
- 避免读取整个文件（大文件会导致超时）
- Token 从环境变量 `FIGMA_ACCESS_TOKEN` 获取

## 输入格式

用户提供 Figma 链接的格式：

```
https://www.figma.com/file/{file_id}/{file_name}
https://www.figma.com/file/{file_id}/{file_name}?node-id={frame_id}
```

**必需信息：**
- `file_id` - Figma 文件 ID
- `frame_id` (可选) - 指定 Frame，不指定则读取首页

## 输出格式

### 1. 文案数据

```json
{
  "file_name": "个人中心 - 免费旋转记录",
  "frame_name": "主界面",
  "texts": [
    {
      "id": "text_001",
      "content": "免费旋转记录",
      "layer_name": "标题文本",
      "parent": "页面容器"
    },
    {
      "id": "text_002",
      "content": "旋转时间",
      "layer_name": "表格列头 - 时间",
      "parent": "记录表格"
    }
  ]
}
```

### 2. 组件结构

```json
{
  "components": [
    {
      "id": "comp_001",
      "name": "页面容器",
      "type": "Frame",
      "children": ["标题文本", "记录表格", "刷新按钮"]
    },
    {
      "id": "comp_002",
      "name": "记录表格",
      "type": "Table",
      "columns": ["旋转时间", "游戏名称", "旋转次数", "赢得金币"]
    }
  ]
}
```

### 3. 组件状态

```json
{
  "states": [
    {
      "component": "刷新按钮",
      "variants": ["Default", "Hover", "Pressed", "Disabled"]
    },
    {
      "component": "记录表格",
      "variants": ["空状态", "有数据", "加载中"]
    }
  ]
}
```

### 4. 交互说明

```json
{
  "interactions": [
    {
      "source": "刷新按钮",
      "event": "onClick",
      "target": "记录表格",
      "action": "刷新数据"
    },
    {
      "source": "返回按钮",
      "event": "onClick",
      "target": "个人中心首页",
      "action": "页面跳转"
    }
  ]
}
```

## 工作流程

### 第 1 步：解析 Figma 链接

```
输入：https://www.figma.com/file/ABC123/个人中心设计稿?node-id=101-201
输出：
  - file_id: ABC123
  - file_name: 个人中心设计稿
  - frame_id: 101-201 (可选)
```

### 第 2 步：调用 Figma REST API

使用 `curl` 或 `Bash` 调用 Figma REST API：

```bash
# 提取 file_id 和 node_id
file_id="TTCIlEUeIyxXWG9pMIkOp9"
node_id="25246:54081"

# 调用 API
curl -s \
  -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
  "https://api.figma.com/v1/files/${file_id}/nodes?ids=${node_id}"
```

**API 端点说明：**
- `/v1/files/{file_id}/nodes` - 获取指定节点数据
- `ids` 参数 - 指定要读取的节点 ID（格式：`{page_id}:{node_id}`）
- 响应包含节点名称、子节点树、文本内容等

### 第 3 步：数据清洗

- 过滤隐藏图层
- 合并重复文案
- 识别有效组件
- 提取可读的交互说明

### 第 4 步：输出结果

```
▎ Figma 设计稿读取完成

文件：个人中心 - 免费旋转记录
Frame: 主界面

【文案数据】
- 已提取 XX 条文案

【组件结构】
- 主要组件：XX 个
- 表格/列表：XX 个
- 按钮/入口：XX 个

【组件状态】
- 有变体的组件：XX 个
- 状态列表：Default, Hover, Disabled...

【交互说明】
- 页面跳转：XX 处
- 数据刷新：XX 处
- 弹窗/抽屉：XX 个

【可用于测试用例的信息】
- 页面展示元素：XX 项
- 可操作组件：XX 项
- 状态变化场景：XX 项
- 页面跳转场景：XX 项
```

## 与 testcase-generate 集成

### 在 /qa 流程中的位置

```
/qa 生成测试用例
  ↓
选择用例类型（冒烟/完整）
  ↓
提供需求文档（Axure/PRD）
  ↓
提供 Figma 链接（可选）  ← 此处调用 figma-reader
  ↓
合并需求 + Figma 数据
  ↓
生成测试用例
```

### 数据传递格式

```json
{
  "source": "figma_api",
  "file_url": "https://www.figma.com/file/xxx",
  "api_endpoint": "/v1/files/{file_id}/nodes?ids={node_id}",
  "extracted_data": {
    "texts": [...],
    "components": [...],
    "states": [...],
    "interactions": [...]
  },
  "testcase_hints": {
    "ui_elements": ["元素 1", "元素 2"],
    "actions": ["操作 1", "操作 2"],
    "states_to_test": ["状态 1", "状态 2"],
    "navigation": ["跳转 1", "跳转 2"]
  }
}
```

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 处理 |
|------|------|------|
| Token 无效 | Figma Access Token 过期 | 提示用户重新获取 Token |
| 文件无权限 | Token 对应账号无权访问 | 提示用户申请文件权限 |
| Frame 不存在 | 指定的 node-id 无效 | 尝试读取首页或提示确认 |
| 网络超时 | 网络问题导致读取失败 | 建议重试或检查网络 |
| 响应过大 | 未使用 node-id 参数 | 必须使用 `ids` 参数读取指定节点 |

### 错误输出格式

```
❌ Figma 设计稿读取失败

错误类型：Token 无效

可能原因：
1. Figma Access Token 已过期
2. Token 配置不正确

解决方案：
1. 访问 https://figma.com/settings → Personal access tokens
2. 重新生成 Token
3. 更新环境变量：export FIGMA_ACCESS_TOKEN="新 token"
4. 重试

如需帮助，请查看：docs/figma-api-guide.md
```

## 最佳实践

### 1. 提供具体 Frame

```
✅ 推荐：https://www.figma.com/file/xxx?node-id=101-201
❌ 不推荐：https://www.figma.com/file/xxx（可能读取到错误的页面）
```

### 2. 设计稿命名规范

```
✅ 推荐：个人中心 - 免费旋转记录
❌ 不推荐：Untitled、Page 1、Frame 123
```

### 3. 使用组件变体

```
✅ 推荐：为按钮创建 Default/Hover/Disabled 变体
❌ 不推荐：所有状态画在同一 Frame 中
```

### 4. 添加交互标注

```
✅ 推荐：使用 Figma 原型功能连接页面
❌ 不推荐：只用文字说明跳转关系
```

## 资源文件

- [engine/skills/testcase-generate/SKILL.md](../testcase-generate/SKILL.md) - 测试用例生成技能

## 相关 Skills

- [`testcase-generate`](../testcase-generate/SKILL.md) - 从需求生成测试用例
- [`testcase-i18n`](../testcase-i18n/SKILL.md) - 多语言 JSON 校验（可从 Figma 提取多语言文案）
