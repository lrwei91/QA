---
# 用途：测试用例仓位约定 - 定义工作区测试用例的存储位置、索引结构和查找规则
---

# 测试用例仓位约定

## 1. 用途

当用户要求保存、导出、继续补充已有测试用例、按模块查历史用例时，优先使用当前工作区的验证产物仓位，而不是只依赖用户临时提供的单个文件。

标准仓位：

- `outputs/`：工作区共享验证产物根目录
- `outputs/generated/`：默认测试用例输出目录
- `outputs/testcase-index.json`：机器可读测试用例索引

## 2. 查找规则

出现以下任一意图时，优先读取对应索引：

- 继续补充已有用例
- 避免重复生成
- 查询某模块历史测试用例
- 保存到默认位置
- 导出后纳入可复用库

读取顺序：

1. 测试用例读取 `outputs/testcase-index.json`
2. 根据 `module`、`module_ids`、`topic`、`group_key`、`tags`，再结合 `platform_scope` 筛候选条目
3. 再打开命中的实际文件做去重、补充或更新

## 3. 索引结构

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
- `format`：如 `md`、`xlsx`
- `rel_path`：相对 `outputs/` 根目录的文件路径
- `template`：模板文件名或路径，无则留空字符串
- `source_refs`：需求来源、PRD、链接、原文件等引用列表
- `tags`：精简后的业务检索标签，优先来自模块名和标题关键词；不要把 `json/xlsx` 这类格式值默认塞进去
- `status`：`draft`、`active`、`archived`
- `created_at`
- `updated_at`

## 4. 保存规则

若用户未指定落盘路径，默认写入：

- Markdown：`outputs/generated/测试用例_<模块或主题>.md`
- Excel：`outputs/generated/测试用例_<模块或主题>.xlsx`

保存到工作区仓位时：

1. 若 `outputs/` 不存在，先创建
2. 若 `outputs/testcase-index.json` 不存在，先创建对应骨架
3. 文件写入成功后，再新增或更新对应索引条目
4. `rel_path` 必须使用相对路径，不能写绝对路径

默认优先调用脚本自动维护索引：

```bash
python3 engine/scripts/upsert_testcase_index.py outputs/generated/运营活动/任务系统前后端优化.xlsx
```

若要批量把仓位中的现有文件补进索引，可运行：

```bash
python3 engine/scripts/upsert_testcase_index.py --all
```

## 5. 更新规则

当保存的是同一份测试用例的后续版本时：

- 复用原条目的 `id`
- 更新 `updated_at`
- 视情况更新 `topic`、`platform_scope`、`template`、`tags`
- 不要为同一文件路径重复新增多条记录

当保存的是同一需求下的新产物时：

- 为新文件新增条目
- 通过 `group_key` 与同主题 testcase 关联
- `module_ids` 尽量与 `index-rules/module-index.json` 命中的模块 id 对齐

### 增量补充用例规则

当用户要求补充已有用例且工作区存在对应 Excel 文件时：

1. **合并到原文件**：不要新建文件，将新增用例追加到原文件末尾
2. **标黄标识**：新增用例行使用黄色背景（#FFFF00）填充，便于区分
3. **序号连续**：新增用例序号从原最后序号 +1 开始连续递增
4. **索引更新**：复用原条目 `id`，仅更新 `updated_at`

使用脚本：
```bash
python3 scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx --highlight --highlight-color "FFFF00"
```

```bash
python3 scripts/upsert_testcase_index.py outputs/generated/运营活动/锦标赛.xlsx
```

## 6. 校验

修改索引后，可运行：

```bash
python3 engine/scripts/validate_testcase_index.py outputs/testcase-index.json
```

校验项包括：

- 根结构完整
- 条目字段齐全
- `id` 不重复
- `group_key` 合法
- `format`、`status` 合法
- `rel_path` 为相对路径
- 条目指向的文件存在
