# Templates 目录说明

本目录存放统一的模板文件，供测试用例生成脚本使用。

## 模板清单

### 1. testcase_template.xlsx

**用途**：测试用例 Excel 模板

**特征**：
- 表头包含固定列：序号、平台、模块、功能点、前置条件、操作步骤、预期结果、测试结果、备注
- 表头样式：加粗、背景色填充
- 数据区域从第 8 行开始
- 支持自动换行的列：前置条件、操作步骤、预期结果

**使用脚本**：
```bash
python3 engine/scripts/generate_testcase_from_template.py \
    templates/testcase_template.xlsx \
    rows.json \
    output.xlsx

python3 engine/scripts/xlsx_append_and_highlight.py \
    existing.xlsx \
    new_rows.json \
    output.xlsx \
    --highlight
```

**样式说明**：
- 表头背景色：蓝色 (#4472C4)
- 表头字体：白色、加粗
- 数据字体：黑色、11pt
- 边框：细实线

---

### 2. i18n_schema.json (计划中)

**用途**：多语言 JSON Schema 模板

**状态**：v1.1.0 版本实现

---

## 模板版本

| 模板 | 版本 | 更新日期 |
|------|------|---------|
| testcase_template.xlsx | v1.0 | 2026-04-01 |

---

## 使用说明

1. **不要手动修改模板**：模板文件应保持稳定，修改需经过版本控制
2. **使用脚本填充**：始终使用 `generate_testcase_from_template.py` 或 `xlsx_fill_testcase_template.py` 脚本
3. **保持样式一致**：所有生成的 Excel 文件应使用同一模板，确保格式统一

---

## 维护

模板文件变更需在 CHANGELOG.md 中记录。
