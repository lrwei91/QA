---
name: qa
description: 分析需求文档、PRD、网页正文、接口说明、现有用例和固定模板，自动生成从环境检查到生成报告的全流程测试用例
---

# Test Case Generator

## 固定欢迎语

每次执行 `/qa` 时，首先输出以下内容：

```
▎请选择要执行的操作：
▎ 1. 生成测试用例
▎ 2. 补充已有用例
▎ 3. 生成多语言校验 JSON
▎ 4. 仅分析需求，不生成用例
```

用户选择后，根据选项继续引导。

---

## 固定流程

### 步骤 1：环境检查（自动执行，无需输出）

```bash
# 检查 Python 环境
which python3 >/dev/null 2>&1 || echo "PYTHON_NOT_FOUND"

# 检查必要依赖
python3 -c "import json, openpyxl, pandas" 2>/dev/null \
  && echo "DEPS_OK" \
  || pip install openpyxl pandas
```

---

### 选项 1：生成测试用例

**第一步：选择用例类型**

```
▎请选择用例类型：
▎ 1. 生成冒烟用例（P0 主流程，10%-20%）
▎ 2. 生成完整测试用例
```

**第二步：提供需求材料**

```
▎请选择提供需求材料的方式：
▎ 1. 需求文档/PRD 文本（直接粘贴）
▎ 2. 提供文件/图片路径（我来读取）
▎ 3. 提供禅道 URL（我来抓取）
```

**第三步：提取关键要素**

至少提取：
- 功能模块和子模块
- 关键流程与业务场景
- 输入项、参数、字段及其约束
- 输出项、返回结果、错误码或页面反馈
- 业务规则、状态流转、角色权限
- 边界条件、异常条件

**第四步：确认需求要素**

使用 AskUserQuestion 确认：

```
▎ 请确认需求要素：
▎ • 主模块：[识别结果]
▎ • 涉及平台：客户端 / 账服 / 两者
▎ • 核心功能点：[列表]

▎ 确认无误后，我将开始设计测试用例
```

**第五步：检查历史用例库**

```bash
if [ -f "testcases/testcase-index.json" ]; then
  echo "INDEX_EXISTS"
else
  echo "INDEX_NOT_FOUND"
fi
```

**第六步：匹配主模块**

读取 `test-case-generator/references/module-index.json`，使用以下字段匹配：
- `aliases`
- `trigger_words`
- `core_functions`
- `client_signals`
- `server_signals`

**第七步：读取关联规则**

根据命中模块读取：
- `references/platform-rules.md`（必选）
- `references/testcase-taxonomy.md`（必选）
- `references/output-template.md`（必选）
- 其他命中的领域文件

**第八步：设计测试用例**

按以下维度设计：
- 正向主流程
- 必填/合法性校验
- 异常输入或非法操作
- 边界值
- 状态流转
- 权限或角色差异

若用户选择**冒烟用例**，在完整用例基础上筛选：
- 只保留 P0 优先级用例
- 正向主流程 + 关键校验
- 总量控制在 10%-20%

**第九步：输出用例**

使用默认列结构：
| 序号 | 平台 | 模块 | 功能点 | 前置条件（测试点） | 操作步骤 | 预期结果 | 测试结果 | 备注 |

**第十步：导出与保存**

若用户要求保存：
- 默认目录：`testcases/generated/`
- 命名格式：
  - 冒烟用例：`测试用例_<模块或主题>_smoke_<yyyymmdd>.xlsx`
  - 完整用例：`测试用例_<模块或主题>_<yyyymmdd>.xlsx`
- 索引更新：`python3 test-case-generator/scripts/upsert_testcase_index.py <文件路径>`

---

### 选项 2：补充已有用例

**第一步：读取历史索引**

```bash
if [ -f "testcases/testcase-index.json" ]; then
  echo "INDEX_EXISTS"
else
  echo "INDEX_NOT_FOUND"
fi
```

**第二步：确认补充范围和方式（并行展示）**

使用 **单个 AskUserQuestion 调用，包含多个问题**，实现并行展示（分段控制器形式）：

```json
{
  "questions": [
    {
      "question": "请选择要补充的模块：",
      "header": "模块",
      "options": [
        {"label": "全民代管理（1 个用例文件）", "description": "补充全民代管理模块的用例"},
        {"label": "帐服报表（1 个用例文件）", "description": "补充帐服报表模块的用例"},
        {"label": "运营活动（7 个用例文件）", "description": "补充运营活动模块的用例"},
        {"label": "自定义输入（输入用例文件名）", "description": "手动输入文件名进行模糊匹配"}
      ]
    },
    {
      "question": "请选择补充方式：",
      "header": "补充方式",
      "options": [
        {"label": "合并到原文件（推荐，新增行标黄）", "description": "将新增用例合并到原文件，新增行标黄"},
        {"label": "生成独立补充文件", "description": "生成新的独立补充文件"}
      ]
    }
  ]
}
```

若用户选择"自定义输入"，引导用户输入：
```
▎ 请输入用例文件名（支持模糊匹配）：
▎ 例如："锦标赛" 可匹配 "testcases/generated/运营活动/锦标赛.xlsx"
```

**第三步：提供需求材料**

```
▎ 请选择提供需求材料的方式：
▎ 1. 需求文档/PRD 文本（直接粘贴）
▎ 2. 提供文件/图片路径（我来读取）
▎ 3. 提供禅道 URL（我来抓取）
```

**第四步：增量合并规则**

若选择合并到原文件：
1. **合并到原文件**：将新增用例追加到原文件末尾
2. **标黄标识**：新增用例行使用黄色背景（#FFFF00）
3. **序号连续**：从原最后序号 +1 开始
4. **自动换行**：多行字段开启 wrap text
5. **索引更新**：复用原条目 `id`，仅更新 `updated_at`

使用脚本：
```bash
python3 test-case-generator/scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx \
    --highlight --highlight-color "FFFF00"
```

**第五步：输出新增用例**

只输出新增测试用例，不改写已有用例。

---

### 选项 3：生成多语言校验 JSON

**第一步：提供需求材料**

```
▎ 请选择提供需求材料的方式：
▎ 1. 需求文档/PRD 文本（直接粘贴）
▎ 2. 提供文件/图片路径（我来读取）
▎ 3. 提供禅道 URL（我来抓取）
```

**第二步：固定语言集合**

必须包含以下 7 种语言：
- `en-us`（English US）
- `id-id`（Bahasa Indonesia）
- `pt-pt`（Português PT）
- `es-es`（Español ES）
- `bn-bn`（বাংলা）
- `tr-tr`（Türkçe）
- `fp-fp`（Filipino）

**第三步：生成规则**

- 只在全部语言值完整时生成 JSON
- 若缺语言，输出缺失语言清单，不生成 JSON
- 若语言完整但配置缺失，生成草稿 JSON（`url=""`，`preScriptPath=""`）

**第四步：JSON 结构**

```json
{
  "name": "<功能名称>",
  "url": "<验证页面 URL>",
  "preScriptPath": "<前置脚本路径>",
  "languages": {
    "en-us": { "key": "value" },
    "id-id": { "key": "value" },
    ...
  },
  "options": {
    "matchRule": "normalized-exact",
    "captureRegion": { "x": 0, "y": 0, "width": 0, "height": 0 }
  }
}
```

**第五步：保存位置**

- 默认目录：`testcases/i18n/<模块>/`
- 索引更新：`python3 test-case-generator/scripts/upsert_testcase_index.py <文件路径>`

---

### 选项 4：仅分析需求

**第一步：提供需求材料**

```
▎ 请选择提供需求材料的方式：
▎ 1. 需求文档/PRD 文本（直接粘贴）
▎ 2. 提供文件/图片路径（我来读取）
▎ 3. 提供禅道 URL（我来抓取）
```

**第二步：输出分析结果**

- 需求类型判断
- 主模块识别
- 关键要素提取
- 建议的测试覆盖范围
- 不建议生成实际用例

---

## 平台拆分规则

`平台` 字段只使用：
- `客户端`：页面展示、控件交互、文案提示、跳转、渲染、表单输入、按钮点击、弹窗、列表、禁用态、前端校验
- `账服`：接口入参/出参、服务端校验、业务处理、状态变更、写库/查库、缓存、消息、异步任务、错误码、幂等、权限、风控、限流

同一需求同时涉及前后端时，拆分为两条用例。

---

## 错误速查

| 错误 | 处理 |
|------|------|
| 模块匹配歧义 | 展示候选模块列表，用 AskUserQuestion 确认 |
| 需求类型不明确 | 基于现有内容做最合理匹配 |
| 多语言不完整 | 输出缺失语言清单 |
| 历史用例索引不存在 | 自动创建仓位和索引骨架 |
| Excel 导出依赖缺失 | 自动 `pip install openpyxl pandas` |
