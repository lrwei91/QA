# Figma MCP 配置指南

## 概述

Figma MCP (Model Context Protocol) 允许 Claude Code 直接读取 Figma 设计稿中的数据，包括：
- 文案和按钮文本
- 组件层级和布局
- 设计标注和状态
- 交互说明

这对于从 UI 设计稿生成测试用例非常有用。

---

## 前提条件

1. **Figma 账号** - 需要有 Figma 账号并能访问设计文件
2. **Node.js** - 已安装 Node.js (v18+)
3. **Claude Code** - 已安装 Claude Code

---

## 步骤一：获取 Figma Access Token

1. 登录 Figma: https://figma.com
2. 进入 **Settings** → **Personal access tokens**
3. 点击 **Create new token**
4. 复制生成的 Token（只显示一次，请妥善保存）

```
figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 步骤二：配置环境变量

将 Token 添加到 shell 配置文件：

```bash
# 编辑 ~/.zshrc 或 ~/.bashrc
export FIGMA_ACCESS_TOKEN="figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 使配置生效
source ~/.zshrc  # 或 source ~/.bashrc
```

**验证配置：**
```bash
echo $FIGMA_ACCESS_TOKEN
```
应显示你的 Token 值。

---

## 步骤三：配置 MCP 服务器

### 方式 A：全局配置（推荐）

编辑全局配置文件 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@figma/mcp-server@latest"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "${FIGMA_ACCESS_TOKEN}"
      }
    }
  }
}
```

### 方式 B：项目级配置

在项目 `.claude/` 目录下创建 `mcp.json`：

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@figma/mcp-server@latest"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "${FIGMA_ACCESS_TOKEN}"
      }
    }
  }
}
```

---

## 步骤四：验证连接

启动 Claude Code 并测试连接：

```bash
claude
```

然后输入：
```
读取 Figma 文件 https://www.figma.com/file/xxxxxx
```

如果配置正确，Claude 将能够访问 Figma 设计稿。

---

## 在 QA 项目中使用

### 基本用法

在 `/qa` 命令执行过程中，可以选择提供 Figma 设计稿链接：

```
/qa 生成测试用例

→ 选择：冒烟用例/完整用例
→ 提供需求文档
→ 提供 Figma 设计稿链接（可选）
```

### Figma 数据提取

Figma MCP 可以帮助提取：

| 数据类型 | 说明 | 测试用例用途 |
|----------|------|-------------|
| 文案内容 | 所有文本图层的文字 | 多语言校验、UI 文案测试 |
| 组件名称 | Frame/Component 名称 | 模块和功能点识别 |
| 组件状态 | Default/Hover/Disabled 等 | 状态测试用例 |
| 层级结构 | 组件父子关系 | 页面结构测试 |
| 设计标注 | 尺寸、颜色、间距 | UI 验收测试 |

---

## 常见问题

### Q: Token 失效了怎么办？
A: 在 Figma Settings 中重新生成 Token，并更新环境变量。

### Q: 提示"无法访问文件"？
A: 确保 Token 对应的账号有该 Figma 文件的访问权限。

### Q: 如何查看 MCP 日志？
A: 在 Claude Code 中运行 `/mcp status` 查看服务器状态。

### Q: 可以访问哪些 Figma 文件？
A: Token 持有者有权限访问的所有文件（包括团队文件）。

---

## 参考资源

- [Figma MCP 官方文档](https://help.figma.com/hc/en-us/articles/32132100833559)
- [Figma MCP GitHub](https://github.com/mcp/com.figma.mcp/mcp)
- [Figma MCP Catalog](https://www.figma.com/mcp-catalog/)

---

## 下一步

配置完成后，可以在生成测试用例时结合 Figma 设计稿：

1. 提供 Axure/PRD 需求文档
2. 提供 Figma 设计稿链接（可选）
3. 生成包含 UI 验证的测试用例
4. 导出 Excel 和多语言 JSON

详细用法请参考 [用户指南](docs/user-guide.md)。
