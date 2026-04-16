---
name: testcase-format
description: 测试用例工程化处理 - 负责转换为模板结构、调用脚本生成 Excel、更新索引，与 Python scripts 对接
---

# Skill: Format & Export

## 触发场景

- 需要导出测试用例为 Excel
- 需要追加用例到已有文件
- 需要更新测试用例索引
- 需要清理过期文件

**触发时机：**

必须在用户明确选择导出方式后才能执行：
- 用户选择「导出为 Excel 文件并更新索引文件」→ 执行导出 + 更新索引
- 用户选择「仅导出为 Excel 文件」→ 仅执行导出，不更新索引

**约束：**
- 不得在用户未选择的情况下自动执行导出
- 不得在用户选择「仅导出」时更新索引

## 职责

1. **转换为模板结构** - 将结构化用例转换为目标模板格式
2. **调用脚本生成 Excel** - 使用 Python 脚本导出 Excel 文件
3. **更新索引** - 新增或更新测试用例索引条目
4. **创建/更新主题页** - 在 `knowledge/wiki/topics/` 创建或更新功能主题页，关联领域知识和已生成用例
5. **保存快照** - 调用 `snapshot_testcase.py` 保存用例内容快照到 `outputs/snapshots/`
6. **工程化处理** - 文件清理、索引差异比较、覆盖率报告

## 不负责

- 不生成测试点（由 `testcase-generate` 负责）
- 不分析需求（由 `testcase-analyze` 负责）
- 不补充用例（由 `testcase-augment` 负责）
## Excel 导出

### 标准模板导出

使用 `templates/testcase_template.xlsx` 模板和 `xlsx_fill_testcase_template.py` 脚本：

```bash
python3 engine/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx --template templates/testcase_template.xlsx
```

**rows.json 格式：**

```json
[
  {
    "平台": "客户端",
    "模块": "功能入口",
    "功能点": "侧边栏入口",
    "前置条件（测试点）": "1、已启用活动",
    "操作步骤": "1、进入页面",
    "预期结果": "入口展示正常",
    "测试结果": "",
    "备注": "【功能测试】"
  }
]
```

**meta.json 格式（可选）：**

```json
{
  "测试平台": "账服、客户端",
  "参考档": "需求文档 v2"
}
```

### 导出要求

| 要求 | 说明 |
|------|------|
| 列顺序 | 与目标模板保持一致 |
| 多行字段 | 必须写入真实换行符 |
| 自动换行 | `前置条件 `、`操作步骤 `、`预期结果` 必须开启 wrap text |
| 固定区 | 不得被覆盖、删除或上移 |
| 表头行 | 位置不得改变 |
| 数据区 | 从模板指定起始行连续写入 |
| 默认留空字段 | 若无用户输入，必须保持为空 |

### 默认留空字段

以下字段若用户未明确提供内容，默认必须保留为空：

- `测试平台`
- `系统&版本`
- `文档编写人`
- `参考档`
- `测试日期`
- `最后更新`

## 增量追加用例

当用户要求"补充已有用例"时，使用 `xlsx_append_and_highlight.py` 脚本：

```bash
python3 engine/scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx --highlight
```

**规则：**

1. 新增用例追加到原文件末尾
2. 新增用例行使用黄色背景（#FFFF00）填充
3. 序号从原最后序号 +1 开始连续递增
4. 索引条目复用原 `id`，仅更新 `updated_at`

## 索引更新

使用 `upsert_testcase_index.py` 自动生成或更新索引条目：

```bash
python3 engine/scripts/upsert_testcase_index.py \
    outputs/generated/module.xlsx
```

**索引条目字段：**

| 字段 | 说明 |
|------|------|
| `id` | 唯一标识 |
| `group_key` | 分组键 |
| `title` | 标题 |
| `module` | 模块 |
| `module_ids` | 模块 ID 列表 |
| `topic` | 主题 |
| `platform_scope` | 平台范围 |
| `format` | 文件格式 |
| `rel_path` | 相对路径 |
| `template` | 使用的模板 |
| `source_refs` | 来源引用 |
| `tags` | 标签 |
| `status` | 状态 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## 工具脚本

| 脚本 | 用途 |
|------|------|
| `xlsx_fill_testcase_template.py` | 填充 Excel 模板 |
| `xlsx_append_and_highlight.py` | 追加用例并标黄 |
| `upsert_testcase_index.py` | 新增/更新索引 |
| `validate_testcase_index.py` | 校验测试用例索引 |
| `cleanup_testcase_store.py` | 清理过期文件 |
| `diff_testcase_indexes.py` | 比较索引差异 |
| `export_testcase_report.py` | 生成覆盖率报告 |

### 使用示例

```bash
# 索引校验
python3 engine/scripts/validate_testcase_index.py \
    outputs/testcase-index.json

# 清理过期文件（先 dry-run）
python3 engine/scripts/cleanup_testcase_store.py --dry-run

# 索引差异比较
python3 engine/scripts/diff_testcase_indexes.py \
    old-index.json new-index.json

# 覆盖率报告
python3 engine/scripts/export_testcase_report.py \
    outputs/testcase-index.json --output report.md
```

## 文件命名规范

### 测试用例文件

```
outputs/generated/<模块>/<用例名称>.xlsx
例：outputs/generated/认证中心/用户登录功能优化.xlsx
```

## 输出格式

### 导出成功

```
测试用例已导出：

文件路径：outputs/generated/<模块>/<用例名称>.xlsx
用例数量：XX 条
- 账服：XX 条
- 客户端：XX 条

索引已更新：outputs/testcase-index.json
主题页已创建/更新：knowledge/wiki/topics/<功能名称>.md
快照已保存：outputs/snapshots/<模块>/<用例名称>/<timestamp>.json
```

### 主题页创建/更新规则

**触发条件**：
- 用户选择「导出为 Excel 文件并更新索引文件」
- Excel 导出成功且索引更新成功

**主题页格式**：

```markdown
# <功能名称>

## 领域知识
参考：[[<模块名称>]]

## 已生成测试用例
| 文件名 | 模块 | 用例数 | 平台 | 生成时间 |
|--------|------|--------|------|----------|
| <文件名>.xlsx | <模块> | XX 条 | 客户端、账服 | YYYY-MM-DD |

## 测试点摘要
- <测试点 1>
- <测试点 2>
- ...
```

**更新规则**：
- 如主题页不存在 → 创建新页面
- 如主题页已存在 → 在用例表格中追加新条目，不覆盖已有内容
- 同一功能的多次导出 → 累积在同一主题页中

### 快照保存规则

**触发条件**：
- Excel 导出成功后
- 索引更新成功后
- 主题页创建/更新成功后

**快照生成命令**：
```bash
python3 engine/scripts/snapshot_testcase.py \
    outputs/generated/<模块>/<用例名称>.xlsx \
    --output-dir outputs/snapshots/<模块>/<用例名称>/
```

**快照用途**：
- 主题页测试点摘要的数据源
- 版本追踪和差异比较
- 知识库查询增强

**主题页中的快照引用**：
```markdown
## 测试点摘要

> 数据来源：快照文件 `outputs/snapshots/<模块>/<用例名称>/<timestamp>.json`
> 最后同步时间：2026-04-14 19:17
```

### 主题页子文件夹支持

主题页支持按子文件夹组织，便于管理和查找。

**子文件夹配置**：
- 配置文件：`knowledge/wiki/topics/submodule-config.json`
- 格式：`{ "模块名": { "用例名称": "子文件夹名", ... }, ... }`

**示例配置**：
```json
{
  "运营活动": {
    "复充返利活动": "充值优惠",
    "幸运卡片": "游戏优惠",
    "锦标赛": "锦标赛"
  }
}
```

**主题页路径**：
- 无子文件夹：`knowledge/wiki/topics/<用例名称>.md`
- 有子文件夹：`knowledge/wiki/topics/<模块>/<子文件夹>/<用例名称>.md`

**同步命令**：
```bash
# 使用配置文件
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx

# 手动指定子文件夹
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx \
    --submodule 充值优惠
```

### 追加成功

```
用例已追加：

原文件：outputs/generated/<模块>/<用例名称>.xlsx
新增用例：XX 条
- 新增行已标黄标识
- 索引已更新 updated_at
```

## 资源文件

- `../../../knowledge/rules/output-template.md` - 输出模板
- `../../../knowledge/rules/testcase-store.md` - 工作区索引约定

## 相关 Skills

- [`testcase-generate`](../testcase-generate/SKILL.md) - 从需求生成测试用例
- [`testcase-augment`](../testcase-augment/SKILL.md) - 补充已有用例
