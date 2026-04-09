# 测试用例生成器 - 脚本使用说明

本目录包含 10 个 Python 脚本，用于测试用例和索引的管理。

## 依赖安装

```bash
pip3 install -r ../requirements.txt
```

---

## 脚本清单

| 脚本 | 用途 | 示例 |
|------|------|------|
| `upsert_testcase_index.py` | 新增/更新测试用例索引 | 见下方 |
| `validate_testcase_index.py` | 校验测试用例索引 | 见下方 |
| `validate_i18n_index.py` | 校验多语言索引 | 见下方 |
| `validate_i18n_json.py` | 校验多语言 JSON | 见下方 |
| `validate_index.py` | 校验模块索引 | 见下方 |
| `cleanup_testcase_store.py` | 清理过期用例 | 见下方 |
| `diff_testcase_indexes.py` | 比较索引差异 | 见下方 |
| `export_testcase_report.py` | 生成覆盖率报告 | 见下方 |
| `generate_testcase_from_template.py` | 从模板生成用例 | 见下方 |
| `xlsx_append_and_highlight.py` | Excel 追加标黄 | 见下方 |
| `parse_axure_html.py` | 解析 Axure HTML | 见下方 |

---

## 详细使用说明

### 1. upsert_testcase_index.py

**用途**：将测试用例或多语言 JSON 纳入索引管理

```bash
# 全量重建所有索引
python3 upsert_testcase_index.py --all

# 纳入单个测试用例
python3 upsert_testcase_index.py testcases/generated/运营活动/任务系统前后端优化.xlsx

# 纳入单个多语言 JSON
python3 upsert_testcase_index.py testcases/i18n/个人中心/个人中心 - 免费旋转记录.json
```

**参数说明：**
- `--all`：扫描整个 testcases 目录，重建索引
- 无参数：需要指定具体文件路径

---

### 2. validate_testcase_index.py

**用途**：校验测试用例索引结构的合法性

```bash
python3 validate_testcase_index.py testcases/testcase-index.json
```

**检查项：**
- 索引 JSON 格式是否合法
- 必填字段是否存在
- rel_path 指向的文件是否存在
- platform_scope 值是否规范

---

### 3. validate_i18n_index.py

**用途**：校验多语言索引结构的合法性

```bash
python3 validate_i18n_index.py testcases/i18n-index.json
```

**检查项：**
- 索引 JSON 格式是否合法
- language_codes 是否包含 7 种语言
- rel_path 指向的文件是否存在

---

### 4. validate_i18n_json.py

**用途**：校验多语言 JSON 是否符合固定 schema

```bash
python3 validate_i18n_json.py testcases/i18n/个人中心/个人中心 - 免费旋转记录.json
```

**检查项：**
- 必填字段：name, url, languages
- 语言集合是否完整（en-us, id-id, pt-pt, es-es, bn-bn, tr-tr, fp-fp）
- options 配置是否合法

---

### 5. validate_index.py

**用途**：校验业务模块索引的合法性

```bash
python3 validate_index.py index-rules/module-index.json
```

**检查项：**
- 模块 ID 唯一性
- 必填字段完整性
- platform_scope 值规范性（客户端/账服）
- depends_on 引用的模块是否存在

---

### 6. cleanup_testcase_store.py

**用途**：清理过期的测试用例和孤立索引条目

```bash
# 预览将要删除的文件
python3 cleanup_testcase_store.py --dry-run

# 执行清理
python3 cleanup_testcase_store.py
```

**清理规则：**
- status="deprecated" 的索引条目对应的文件
- 索引中不存在的孤立文件

---

### 7. diff_testcase_indexes.py

**用途**：比较两个索引文件的差异

```bash
python3 diff_testcase_indexes.py \
    testcases/testcase-index.json \
    testcases/testcase-index-backup.json
```

**输出：**
- 新增的条目
- 删除的条目
- 修改的条目

---

### 8. export_testcase_report.py

**用途**：生成测试用例覆盖率统计报告

```bash
python3 export_testcase_report.py --output report.md
```

**输出内容：**
- 总用例数统计
- 按模块分布
- 按平台分布
- 按标签统计

---

### 9. generate_testcase_from_template.py

**用途**：从 Excel 模板生成测试用例

```bash
python3 generate_testcase_from_template.py \
    --template templates/testcase_template.xlsx \
    --output testcases/generated/模块/用例名称.xlsx \
    --data rows.json
```

**参数说明：**
- `--template`：Excel 模板路径
- `--output`：输出文件路径
- `--data`：测试数据 JSON 文件

---

### 10. xlsx_append_and_highlight.py

**用途**：向已有 Excel 追加用例并标黄标识

```bash
python3 xlsx_append_and_highlight.py \
    existing.xlsx \
    new_rows.json \
    output.xlsx \
    --highlight \
    --highlight-color "FFFF00"
```

**参数说明：**
- `--highlight`：启用标黄功能
- `--highlight-color`：高亮颜色（默认黄色）

---

### 11. parse_axure_html.py

**用途**：解析 Axure RP 导出的 HTML 文件，提取页面结构、元件、注释和交互说明

```bash
# 解析单个 HTML 文件
python3 parse_axure_html.py testcases/axure_export/login_page.html

# 解析目录下的所有 HTML 文件
python3 parse_axure_html.py testcases/axure_export/

# 递归解析子目录
python3 parse_axure_html.py testcases/axure_export/ --recursive

# 输出到文件
python3 parse_axure_html.py testcases/axure_export/ \
    --output axure_data.json

# 使用详细模式
python3 parse_axure_html.py testcases/axure_export/ \
    --recursive --verbose
```

**参数说明：**
- `input_path`：输入 HTML 文件或目录路径
- `--output, -o`：输出 JSON 文件路径
- `--recursive, -r`：递归搜索子目录
- `--format`：输出格式：`raw`（原始解析）或 `testcase`（测试用例格式）
- `--verbose, -v`：详细输出模式

**输出格式：**
- `raw` 格式：包含完整的页面、元件、注释原始数据
- `testcase` 格式：转换为测试用例生成所需的结构（modules, function_points, ui_elements, constraints）

**使用场景：**
- 从 Axure 原型提取 UI 结构和交互说明
- 补充需求文档中缺失的 UI 细节
- 为 testcase-generate 技能提供 UI 输入数据

---

## 组合使用示例

### 场景 1：完成一次完整的需求测试用例生成

```bash
# 1. 生成测试用例（通过/qa 命令）
# 2. 纳入索引
python3 upsert_testcase_index.py testcases/generated/模块/用例.xlsx
# 3. 验证索引
python3 validate_testcase_index.py testcases/testcase-index.json
```

### 场景 2：定期维护

```bash
# 1. 清理过期用例
python3 cleanup_testcase_store.py
# 2. 重建索引
python3 upsert_testcase_index.py --all
# 3. 验证
python3 validate_testcase_index.py testcases/testcase-index.json
python3 validate_i18n_index.py testcases/i18n-index.json
```

### 场景 3：生成报告

```bash
# 导出覆盖率报告
python3 export_testcase_report.py --output testcases/coverage_report.md
```

---

## 故障排查

### 问题 1：脚本报 "ModuleNotFoundError"

**解决**：
```bash
pip3 install -r ../requirements.txt
```

### 问题 2：索引校验失败

**解决**：
1. 检查 JSON 格式是否合法
2. 检查 rel_path 路径是否正确
3. 运行 `cleanup_testcase_store.py --dry-run` 查看问题条目

### 问题 3：Excel 导出失败

**解决**：
1. 确认模板文件存在
2. 检查 openpyxl 版本是否 >= 3.1.0
3. 确认 rows.json 格式正确

---

## 返回主文档

- [返回 README.md](../README.md)
- [查看 QUICKSTART.md](../QUICKSTART.md)
