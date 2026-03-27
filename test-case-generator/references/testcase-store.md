# Testcase Store

## 1. Purpose

当用户要求保存、导出、继续补充已有测试用例、按模块查历史用例，或输出/补充多语言校验 JSON 时，优先使用当前工作区的验证产物仓位，而不是只依赖用户临时提供的单个文件。

标准仓位：

- `testcases/`：工作区共享验证产物根目录
- `testcases/generated/`：默认测试用例输出目录
- `testcases/i18n/`：多语言校验 JSON 目录
- `testcases/testcase-index.json`：机器可读测试用例索引
- `testcases/i18n-index.json`：机器可读多语言 JSON 索引

## 2. Lookup rules

出现以下任一意图时，优先读取对应索引：

- 继续补充已有用例
- 避免重复生成
- 查询某模块历史测试用例
- 查询某主题历史多语言校验 JSON
- 保存到默认位置
- 导出后纳入可复用库

读取顺序：

1. 测试用例读取 `testcases/testcase-index.json`；多语言 JSON 读取 `testcases/i18n-index.json`
2. 根据 `module`、`module_ids`、`topic`、`group_key`、`tags`，再结合 `platform_scope` 或 `language_codes` 筛候选条目
3. 再打开命中的实际文件做去重、补充或更新

## 3. Index schema

测试用例索引根对象使用以下结构：

```json
{
  "version": 1,
  "store_name": "QA Test Case Store",
  "root_dir": "testcases",
  "cases_dir": "generated",
  "updated_at": "2026-03-28T00:00:00+08:00",
  "entries": []
}
```

测试用例条目至少包含：

- `id`：稳定唯一标识，优先由 `scripts/upsert_testcase_index.py` 自动生成
- `group_key`：同一需求下不同产物的关联键
- `title`：文件标题或需求标题
- `module`：主模块名称
- `module_ids`：关联的模块索引 id 列表
- `topic`：当前主题或需求摘要
- `platform_scope`：平台检索标签列表。新生成测试用例优先使用 `客户端` / `账服`；导入历史文件时允许保留原始标签
- `format`：如 `md`、`xlsx`、`json`
- `rel_path`：相对 `testcases/` 根目录的文件路径
- `template`：模板文件名或路径，无则留空字符串
- `source_refs`：需求来源、PRD、链接、原文件等引用列表
- `tags`：精简后的业务检索标签，优先来自模块名和标题关键词；不要把 `json/xlsx` 这类格式值默认塞进去
- `status`：`draft`、`active`、`archived`
- `created_at`
- `updated_at`

多语言索引根对象使用以下结构：

```json
{
  "version": 1,
  "store_name": "QA I18N JSON Store",
  "root_dir": "testcases",
  "i18n_dir": "i18n",
  "updated_at": "2026-03-28T00:00:00+08:00",
  "entries": []
}
```

多语言条目至少包含：

- `id`
- `group_key`
- `title`
- `module`
- `module_ids`
- `topic`
- `language_codes`
- `format`
- `rel_path`
- `template`
- `source_refs`
- `tags`
- `status`
- `created_at`
- `updated_at`

## 4. Save rules

若用户未指定落盘路径，默认写入：

- Markdown：`testcases/generated/测试用例_<模块或主题>_<yyyymmdd>.md`
- Excel：`testcases/generated/测试用例_<模块或主题>_<yyyymmdd>.xlsx`
- 多语言 JSON：`testcases/i18n/<模块>/<主题>.json`

保存到工作区仓位时：

1. 若 `testcases/` 不存在，先创建
2. 若 `testcases/testcase-index.json` 或 `testcases/i18n-index.json` 不存在，先创建对应骨架
3. 文件写入成功后，再新增或更新对应索引条目
4. `rel_path` 必须使用相对路径，不能写绝对路径

多语言 JSON 固定格式沿用附件样式：

- `name`
- `url`
- `preScriptPath`
- `languages`
- `options.matchRule`
- `options.captureRegion`

固定语言集合必须完整包含：

- `en-us`
- `id-id`
- `pt-pt`
- `es-es`
- `bn-bn`
- `tr-tr`
- `fp-fp`

多语言 JSON 生成规则：

- 只有当需求或对话里已经给齐全部语言文案时，才自动生成 JSON
- 若没有多语言内容，或语言值不完整，不自动生成 JSON
- 若语言完整但 `captureRegion` 缺失，允许生成草稿 JSON：
  - `url=""`
  - `preScriptPath=""`
  - `matchRule="normalized-exact"`
  - `captureRegion={x:0,y:0,width:0,height:0}`
  - `i18n-index.json` 中 `status=draft`

默认优先调用脚本自动维护两份索引：

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/运营活动/任务系统前后端优化.xlsx
```

若要批量把仓位中的现有文件补进索引，可运行：

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py --all
```

手动新增多语言 JSON 后也使用同一脚本纳入多语言索引：

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/i18n/运营活动/任务系统前后端优化.json
```

## 5. Update rules

当保存的是同一份测试用例或同一份多语言 JSON 的后续版本时：

- 复用原条目的 `id`
- 更新 `updated_at`
- 视情况更新 `topic`、`platform_scope`、`language_codes`、`template`、`tags`
- 不要为同一文件路径重复新增多条记录

当保存的是同一需求下的新产物时：

- 为新文件新增条目
- 通过 `group_key` 与同主题 testcase / i18n JSON 关联
- `module_ids` 尽量与 `references/module-index.json` 命中的模块 id 对齐

## 6. Validation

修改索引后，可运行：

```bash
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
python3 test-case-generator/scripts/validate_i18n_index.py testcases/i18n-index.json
python3 test-case-generator/scripts/validate_i18n_json.py testcases/i18n/运营活动/任务系统前后端优化.json
```

校验项包括：

- 根结构完整
- 条目字段齐全
- `id` 不重复
- `group_key`、`language_codes` 合法
- `format`、`status` 合法
- `rel_path` 为相对路径
- 条目指向的文件存在
- 多语言 JSON 符合固定 schema 与语言集合
