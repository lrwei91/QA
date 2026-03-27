# QA 项目说明

## 项目概览

这个项目围绕 `test-case-generator` 技能包，沉淀了一套可复用的 QA 产物生成与管理方案，当前已经支持两类核心产物：

- 结构化测试用例
- 多语言校验 JSON

项目的目标不是只“生成一份文件”，而是把生成结果纳入可检索索引，方便后续继续补充、避免重复、按模块查历史，并把同一需求下的不同产物通过 `group_key` 关联起来。

## 当前能力

### 1. 测试用例生成

基于需求文档、PRD、网页正文、接口说明、现有用例和模板，生成结构化测试用例，支持：

- 主模块识别
- 客户端 / 账服拆分
- 增量补充
- 模板保真输出
- Excel 导出
- 历史用例索引复用

对应 skill 文件：

- [test-case-generator/SKILL.md](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/SKILL.md)

### 2. 多语言校验 JSON

当需求中包含完整多语言文案时，额外生成一份多语言校验 JSON，用于文案验证。

固定语言集合：

- `en-us`
- `id-id`
- `pt-pt`
- `es-es`
- `bn-bn`
- `tr-tr`
- `fp-fp`

固定 JSON 结构：

- `name`
- `url`
- `preScriptPath`
- `languages`
- `options.matchRule`
- `options.captureRegion`

如果语言值完整但验证配置缺失，当前实现允许生成草稿 JSON：

- `url=""`
- `preScriptPath=""`
- `options.matchRule="normalized-exact"`
- `options.captureRegion={x:0,y:0,width:0,height:0}`
- 索引条目状态记为 `draft`

参考样例：

- [个人中心-免费旋转记录.json](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/文档/json/个人中心-免费旋转记录.json)

## 目录结构

```text
QA/
├── README.md
├── test-case-generator/
│   ├── SKILL.md
│   ├── references/
│   │   ├── testcase-store.md
│   │   ├── output-template.md
│   │   ├── update-governance.md
│   │   ├── module-index.json
│   │   └── ...
│   └── scripts/
│       ├── upsert_testcase_index.py
│       ├── validate_testcase_index.py
│       ├── validate_i18n_json.py
│       └── validate_index.py
├── testcases/
│   ├── generated/
│   │   └── <模块>/<测试用例文件>
│   ├── i18n/
│   │   └── <模块>/<多语言校验 JSON>
│   ├── testcase-index.json
│   └── i18n-index.json
└── Office-Skills/
```

说明：

- `test-case-generator/` 是技能包本体
- `testcases/generated/` 存放测试用例产物
- `testcases/i18n/` 存放多语言校验 JSON
- `testcases/testcase-index.json` 只管理测试用例
- `testcases/i18n-index.json` 只管理多语言校验 JSON
- `Office-Skills/` 是外部技能集，不是当前这套 QA 产物管理逻辑的主实现目录

## 索引结构

当前索引文件：

- [testcases/testcase-index.json](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/testcases/testcase-index.json)
- [testcases/i18n-index.json](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/testcases/i18n-index.json)

测试用例索引根结构：

-- `version`
-- `store_name`
-- `root_dir`
-- `cases_dir`
-- `updated_at`
-- `entries`

测试用例条目至少包含：

- `id`
- `group_key`
- `title`
- `module`
- `module_ids`
- `topic`
- `platform_scope`
- `format`
- `rel_path`
- `template`
- `source_refs`
- `tags`
- `status`
- `created_at`
- `updated_at`

i18n 索引根结构：

- `version`
- `store_name`
- `root_dir`
- `i18n_dir`
- `updated_at`
- `entries`

i18n 条目至少包含：

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

关键约定：

- 同一需求下的 testcase 和 i18n JSON 通过 `group_key` 关联
- `testcase-index.json` 只收录测试用例
- `i18n-index.json` 只收录多语言 JSON
- `tags` 只保留高价值业务词，不把 `xlsx/json` 这类格式值塞进去

## 当前实现文件

### Skill 与规则

- [test-case-generator/SKILL.md](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/SKILL.md)
- [test-case-generator/references/testcase-store.md](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/references/testcase-store.md)
- [test-case-generator/references/output-template.md](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/references/output-template.md)
- [test-case-generator/references/update-governance.md](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/references/update-governance.md)

### 脚本

- [upsert_testcase_index.py](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/scripts/upsert_testcase_index.py)
  负责把 testcase / i18n JSON 分流新增或更新到两份索引
- [validate_testcase_index.py](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/scripts/validate_testcase_index.py)
  校验测试用例索引结构和目标文件
- [validate_i18n_index.py](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/scripts/validate_i18n_index.py)
  校验多语言索引结构和目标文件
- [validate_i18n_json.py](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/scripts/validate_i18n_json.py)
  校验多语言 JSON 是否符合固定 schema
- [validate_index.py](/Users/lrwei91/Library/CloudStorage/OneDrive-个人/Project/QA/test-case-generator/scripts/validate_index.py)
  校验业务模块索引 `references/module-index.json`

## 常用命令

### 1. 全量重建两份索引

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py --all
```

### 2. 纳入单个测试用例文件

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/运营活动/任务系统前后端优化.xlsx
```

### 3. 纳入单个多语言 JSON

```bash
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/i18n/运营活动/任务系统前后端优化.json
```

### 4. 校验测试用例索引

```bash
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
```

### 5. 校验多语言索引

```bash
python3 test-case-generator/scripts/validate_i18n_index.py testcases/i18n-index.json
```

### 6. 校验单个多语言 JSON

```bash
python3 test-case-generator/scripts/validate_i18n_json.py testcases/i18n/运营活动/任务系统前后端优化.json
```

### 7. 校验模块索引

```bash
python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json
```

## 当前行为约定

### 1. 什么时候生成多语言 JSON

- 需求或对话中明确存在多语言内容
- 固定语言集合已经给齐

否则：

- 不自动生成 JSON
- 应输出缺失语言清单

### 2. 什么时候更新索引

- 用户明确要求保存
- 用户明确要求导出
- 用户手动新增合法 testcase / i18n JSON 后，需要纳入历史库

默认不应在普通“仅对话输出”场景中偷偷修改索引。

### 3. 什么时候是草稿 JSON

语言值完整，但以下配置缺失时：

- `url`
- `preScriptPath`
- `captureRegion`

此时可以生成 JSON，但应：

- 使用默认占位配置
- 在索引中标记为 `draft`

## 已验证状态

当前实现已经完成并验证：

- 双索引结构已迁移
- 多语言 JSON 校验脚本可正常工作
- `upsert_testcase_index.py` 可同时处理 testcase 和 i18n JSON，并自动分流到对应索引
- 两份索引和多语言 JSON 的端到端验证已通过

## 后续建议

如果继续扩展当前项目，优先做这几件事：

- 把 `module_ids` 从目录级占位，进一步对齐到真实业务模块索引
- 增加“从需求文本直接生成 i18n JSON”的执行脚本
- 为常见模块补一批真实的 `testcases/i18n/<模块>/<主题>.json`
- 如果后续存在更多 JSON 变体，再考虑把多语言 schema 抽成单独 reference
