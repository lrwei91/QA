# Testcase Template Workbook

Use this path when the user wants a testcase workbook with the standard columns:

`序号 / 平台 / 模块 / 功能点 / 前置条件（测试点） / 操作步骤 / 预期结果 / 测试结果 / 备注`

and the output must preserve a fixed team template, colored summary rows, frozen panes,
dropdown validation, or wrapped multi-line cells.

## Rule Set

1. Do not use `templates/minimal_xlsx/` for testcase sheets.
2. Use `templates/testcase_template.xlsx` as the base workbook.
3. Keep the template structure exactly:
   - rows `1-6`: summary/meta area from the template
   - row `7`: header row from the template
   - row `8+`: testcase data rows
4. Do not add extra summary blocks such as "来源基线", "整合策略", or other invented rows unless the template already contains them.
5. Do not add columns not present in the template. In particular, do not append a `图片` column if the template does not include it.
6. Multi-line values such as `1、2、3、...` must use the template's wrapped styles so Excel shows line breaks immediately without re-editing the cell.
7. When serializing the worksheet XML, preserve the template's worksheet-level namespace declarations (for example `xmlns:r`, `xmlns:x14ac`, `xmlns:xr2`, `xmlns:xr3`). Do not emit `mc:Ignorable` prefixes without matching declarations.
8. Do not carry a stale `calcChain.xml` into generated testcase workbooks. Let Excel rebuild the calculation chain from the formulas.

## Metadata

The template includes these fields:

- `测试平台`
- `测试日期`
- `系统&版本`
- `最后更新`
- `文档编写人`
- `文档测试人`
- `策划负责人`
- `审阅人员`
- `参考档`

Only fill these when the user provided the values or they are directly derivable and clearly useful. Otherwise leave them blank. Do not invent extra metadata rows.

## Generator Script

```bash
python3 SKILL_DIR/scripts/xlsx_fill_testcase_template.py rows.json output.xlsx
python3 SKILL_DIR/scripts/xlsx_fill_testcase_template.py rows.json output.xlsx --meta meta.json
```

`rows.json` may be either:

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

or:

```json
{
  "meta": {
    "测试平台": "账服、客户端",
    "测试日期": "2026-03-28",
    "参考档": "需求文档 v2"
  },
  "rows": [
    {
      "平台": "账服",
      "模块": "活动配置",
      "功能点": "默认状态验证",
      "前置条件（测试点）": "1、进入页面",
      "操作步骤": "1、查看默认值",
      "预期结果": "默认值正确",
      "测试结果": "",
      "备注": "【功能测试】"
    }
  ]
}
```

## Validation Checklist

After generating the workbook:

1. Read the output with `pandas.read_excel(path, header=6)` and confirm the columns are exactly the template columns.
2. Confirm the sheet still has the template's summary rows and colored header row.
3. Confirm the `测试结果` column still has the dropdown validation.
4. Confirm multi-line content is visible with wrapping when the file is opened, without double-clicking cells.
5. Confirm the workbook opens in Excel without a repair prompt.
