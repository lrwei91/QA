---
name: testcase-i18n
description: 多语言 JSON 校验与处理 - 负责 key-value 校验、缺失检测、语言一致性检查、输出问题列表与修复建议
---

# Skill: I18N Testcase

## 触发场景

- 用户提供多语言 JSON 文件
- 需要校验多语言文案完整性
- 需要生成多语言校验 JSON
- 需要检查语言一致性

## 职责

1. **key-value 校验** - 检查每个 key 是否都有对应的翻译值
2. **缺失检测** - 识别缺少翻译的条目
3. **语言一致性检查** - 检查同一 key 在不同语言中的语义一致性
4. **格式校验** - 检查 JSON 结构是否符合标准 schema

## 标准语言集合

固定 7 种标准语言：

| 语言代码 | 语言名称 |
|----------|----------|
| `en-us` | 英语 |
| `id-id` | 印尼语 |
| `pt-pt` | 葡萄牙语 |
| `es-es` | 西班牙语 |
| `bn-bn` | 孟加拉语 |
| `tr-tr` | 土耳其语 |
| `fp-fp` | 菲律宾语 |

## JSON Schema

多语言校验 JSON 必须符合以下结构：

```json
{
  "name": "模块 - 功能名称",
  "url": "页面 URL（可选）",
  "preScriptPath": "前置脚本路径（可选）",
  "options": {
    "matchRule": "normalized-exact",
    "captureRegion": {
      "x": 0,
      "y": 0,
      "width": 0,
      "height": 0
    }
  },
  "entries": [
    {
      "key": "UI_BUTTON_SUBMIT",
      "languages": {
        "en-us": "Submit",
        "id-id": "Kirim",
        "pt-pt": "Enviar",
        "es-es": "Enviar",
        "bn-bn": "জমা দিন",
        "tr-tr": "Gönder",
        "fp-fp": "Ipasa"
      }
    }
  ]
}
```

## 校验规则

### 1. 结构校验

- `name` 字段必填
- `entries` 数组必填
- 每个 entry 必须包含 `languages` 对象
- `languages` 必须包含 7 种标准语言

### 2. 语言完整性检查

检查每个 key 是否都包含完整 7 种语言：

- 缺失语言 → 输出缺失清单
- 全部完整 → 校验通过

### 3. 空值检查

检查是否有语言值为空字符串：

```
警告：以下条目的语言值为空
- UI_BUTTON_SUBMIT: id-id 为空
- UI_LABEL_NAME: bn-bn 为空
```

### 4. 一致性检查

检查同一 key 在不同语言中的语义是否一致：

- 长度差异过大（超过 3 倍）→ 警告
- 包含占位符不一致 → 警告
- 包含变量名不一致 → 错误

## 输出格式

### 校验通过

```
▎ 多语言校验结果

文件：testcases/i18n/<模块>/<模块>-<功能>.json
条目数量：XX 个

✓ 所有条目语言完整
✓ 无空值
✓ 格式校验通过
```

### 发现问题

```
▎ 多语言校验结果

文件：testcases/i18n/<模块>/<模块>-<功能>.json
条目数量：XX 个

【问题清单】

1. 语言缺失（共 X 个）
   - UI_BUTTON_SUBMIT: 缺少 id-id, bn-bn
   - UI_LABEL_NAME: 缺少 tr-tr

2. 空值问题（共 X 个）
   - UI_HINT_PLACEHOLDER: fp-fp 为空字符串

3. 一致性警告（共 X 个）
   - UI_MESSAGE_LONG: en-us 长度为 50，bn-bn 长度为 150（差异过大）

【修复建议】
1. 补充缺失语言翻译
2. 填写空值字段
3. 检查过长翻译是否准确
```

## 自动检测规则

当需求、附件或对话中包含以下内容时，自动触发多语言处理：

### 关键词检测

- `多语言 `、`国际化 `、`i18n`、` 翻译`、`Translation`、`Localization`
- 语言代码：`en-us`、`id-id`、`pt-pt`、`es-es`、`bn-bn`、`tr-tr`、`fp-fp`
- 文案 key 格式：`UI_`、`Key_`、`STR_`、`文案 `、` 文本`

### 表格检测

- 多列表格，表头包含语言名称或语言代码
- key-value 对照格式

## 生成策略

### 语言完整时

生成多语言校验 JSON，并更新多语言索引。

### 语言不完整时

输出缺失清单，不生成 JSON：

```
▎ 检测到需求中包含多语言文案
  - 已提取 XX 个多语言条目
  - 语言不完整，缺少：hi-in, th-th (非标准语言已忽略)
  - 标准 7 种语言检查：
    - 有 YY 个条目缺少 zz 语言
  - 暂不生成 JSON，请补充缺失语言后重试
```

## 索引更新

多语言索引条目维护以下字段：

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识 |
| `group_key` | 分组键 |
| `title` | 标题 |
| `module` | 模块 |
| `module_ids` | 模块 ID 列表 |
| `topic` | 主题 |
| `language_codes` | 语言代码列表 |
| `format` | 文件格式 |
| `rel_path` | 相对路径 |
| `template` | 使用的模板 |
| `source_refs` | 来源引用 |
| `tags` | 标签 |
| `status` | 状态（draft/published） |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## 使用脚本

```bash
# 校验多语言 JSON
python3 test-case-generator/scripts/validate_i18n_json.py \
    testcases/i18n/<模块>/<模块>-<功能>.json

# 校验多语言索引
python3 test-case-generator/scripts/validate_i18n_index.py \
    testcases/i18n-index.json
```

## 资源文件

- `../../references/engineering/testcase-store.md` - 工作区索引约定

## 相关 Skills

- [`testcase-generate`](../testcase-generate/SKILL.md) - 从需求生成测试用例（含多语言自动检测）
- [`testcase-format`](../testcase-format/SKILL.md) - 导出 Excel 与索引更新
