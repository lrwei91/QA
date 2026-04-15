# 前置依赖安装要求

## 必需依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| `bun` | 运行 baoyu-url-to-markdown（网页提取） | `curl -fsSL https://bun.sh/install \| bash` |
| `Google Chrome` | Chrome 浏览器，用于网页渲染 | 从 [chrome.com](https://www.google.com/chrome/) 下载 |

## 可选依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| `uv` | YouTube 字幕提取、微信公众号提取 | `brew install uv` |

---

## 快速安装

### macOS

```bash
# 1. 安装 bun
curl -fsSL https://bun.sh/install | bash

# 2. 安装 Chrome（如使用 Homebrew）
brew install --cask google-chrome

# 3. 启动 Chrome 调试模式（使用网页提取功能前）
open -na "Google Chrome" --args --remote-debugging-port=9222
```

### Linux

```bash
# 1. 安装 bun
curl -fsSL https://bun.sh/install | bash

# 2. 安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# 3. 启动 Chrome 调试模式
google-chrome --remote-debugging-port=9222
```

### Windows (PowerShell)

```powershell
# 1. 安装 bun
powershell -c "iwr https://bun.sh/install -o install.ps1; .\install.ps1"

# 2. 安装 Chrome
winget install Google.Chrome
```

---

## 验证安装

```bash
# 检查 bun
which bun && bun --version

# 检查 Chrome 调试端口
lsof -i :9222 -sTCP:LISTEN
```

---

## 依赖说明

### baoyu-url-to-markdown

- **位置**：`knowledge/deps/baoyu-url-to-markdown/`
- **用途**：网页文章、X/Twitter、知乎等内容提取
- **运行方式**：通过 `bun` 执行 TypeScript 脚本
- **Chrome 要求**：需要以调试模式启动（`--remote-debugging-port=9222`）

### youtube-transcript（可选）

- **位置**：`knowledge/deps/youtube-transcript/`
- **用途**：YouTube 视频字幕提取
- **运行方式**：通过 `uv` 执行 Python 脚本

### wechat-article-to-markdown（可选）

- **用途**：微信公众号文章提取
- **运行方式**：通过 `uv` 执行

---

## 故障排除

### Chrome 找不到

```bash
# macOS
open -na "Google Chrome" --args --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"chrome.exe" --remote-debugging-port=9222
```

### bun 找不到

确保 bun 已添加到 PATH：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

### 网页提取失败

1. 确认 Chrome 调试端口已启动
2. 检查 bun 版本是否最新
3. 尝试使用 `--wait` 模式（针对登录页面）
