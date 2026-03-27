# Testcase Store

## 1. Purpose

当用户要求保存、导出、继续补充已有测试用例、按模块查历史用例时，优先使用当前工作区的测试用例仓位，而不是只依赖用户临时提供的单个文件。

标准仓位：

- `testcases/`：工作区测试用例根目录
- `testcases/generated/`：默认输出目录
- `testcases/index.json`：机器可读索引

## 2. Lookup rules

出现以下任一意图时，优先读取 `testcases/index.json`：

- 继续补充已有用例
- 避免重复生成
- 查询某模块历史测试用例
- 保存到默认位置
- 导出后纳入可复用库

读取顺序：

1. 读取 `testcases/index.json`
2. 根据 `module`、`module_ids`、`topic`、`tags`、`platform_scope` 筛候选条目
3. 再打开命中的实际文件做去重、补充或更新

## 3. Index schema

根对象使用以下结构：

```json
{
  "version": 1,
  "store_name": "QA Test Case Store",
  "root_dir": "testcases",
  "cases_dir": "generated",
  "updated_at": "2026-03-27T00:00:00+08:00",
  "entries": []
}
```

每个条目至少包含：

- `id`：稳定唯一标识，优先由 `scripts/upsert_testcase_index.py` 自动生成
- `title`：文件标题或需求标题
- `module`：主模块名称
- `module_ids`：关联的模块索引 id 列表
- `topic`：当前主题或需求摘要
- `platform_scope`：平台检索标签列表。新生成文件优先使用 `客户端` / `账服`；导入历史文件时允许保留原始标签，如 `平台`、`后端`、`大厅`、`运营活动`
- `format`：如 `md`、`xlsx`
- `rel_path`：相对 `testcases/` 根目录的文件路径
- `template`：模板文件名或路径，无则留空字符串
- `source_refs`：需求来源、PRD、链接、原文件等引用列表
- `tags`：精简后的业务检索标签，优先来自模块名和标题关键词；不要把 `xlsx` 这类格式值、也不要把低价值噪音默认塞进去
- `status`：`draft`、`active`、`archived`
- `created_at`
- `updated_at`

## 4. Save rules

若用户未指定落盘路径，默认写入：

- Markdown：`testcases/generated/测试用例_<模块或主题>_<yyyymmdd>.md`
- Excel：`testcases/generated/测试用例_<模块或主题>_<yyyymmdd>.xlsx`

保存到工作区仓位时：

1. 若 `testcases/` 不存在，先创建
2. 若 `testcases/index.json` 不存在，先创建骨架
3. 文件写入成功后，再新增或更新索引条目
4. `rel_path` 必须使用相对路径，不能写绝对路径

默认优先调用脚本自动维护索引：

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/运营活动/任务系统前后端优化.xlsx
```

若要批量把仓位中的现有文件补进索引，可运行：

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py --all
```

## 5. Update rules

当保存的是同一份测试用例的后续版本时：

- 复用原条目的 `id`
- 更新 `updated_at`
- 视情况更新 `topic`、`platform_scope`、`template`、`tags`
- 不要为同一文件路径重复新增多条记录

当保存的是新文件时：

- 新增条目
- 保持 `id` 唯一
- `module_ids` 尽量与 `references/module-index.json` 命中的模块 id 对齐

## 6. Validation

修改 `testcases/index.json` 后，可运行：

```bash
python3 test-case-generator/scripts/validate_testcase_index.py testcases/index.json
```

校验项包括：

- 根结构完整
- 条目字段齐全
- `id` 不重复
- `format`、`status` 合法
- `rel_path` 为相对路径
- 条目指向的文件存在
