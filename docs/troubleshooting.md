# 故障排查指南

本文档汇总了 QA 测试用例生成器使用过程中的常见问题及解决方案。

---

## 目录

- [环境安装问题](#环境安装问题)
- [索引校验失败](#索引校验失败)
- [Excel 导出问题](#excel-导出问题)
- [多语言 JSON 问题](#多语言-json-问题)
- [模块匹配问题](#模块匹配问题)
- [脚本执行错误](#脚本执行错误)
- [Git 相关问题](#git-相关问题)

---

## 环境安装问题

### 问题 1：Python3 未找到

**错误信息：**
```
/bin/sh: python3: command not found
```

**解决方案：**

macOS:
```bash
# 使用 Homebrew 安装
brew install python3
```

Windows:
```powershell
# 从官网下载安装
# https://www.python.org/downloads/
```

验证安装：
```bash
python3 --version
```

---

### 问题 2：依赖包安装失败

**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement openpyxl>=3.1.0
```

**原因：**
- pip 版本过旧
- Python 版本不兼容（需要 3.8+）
- 网络连接问题

**解决方案：**

```bash
# 1. 升级 pip
pip3 install --upgrade pip

# 2. 指定国内镜像（如在国内）
pip3 install -r test-case-generator/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 验证安装
python3 -c "import openpyxl, pandas; print('OK')"
```

---

### 问题 3：jsonschema 模块缺失

**错误信息：**
```
ModuleNotFoundError: No module named 'jsonschema'
```

**解决方案：**
```bash
# 单独安装 jsonschema
pip3 install jsonschema>=4.17.0

# 或重新安装所有依赖
pip3 install -r test-case-generator/requirements.txt
```

---

## 索引校验失败

### 问题 4：testcase-index.json 格式错误

**错误信息：**
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**原因：**
- JSON 文件包含注释
- 使用了单引号而非双引号
- 末尾逗号

**解决方案：**

1. 使用 JSON 校验工具检查：
```bash
python3 -m json.tool testcases/testcase-index.json > /dev/null
```

2. 使用 VS Code 或 IDE 的 JSON 插件格式化

3. 确保不使用注释（JSON 不支持注释）

---

### 问题 5：rel_path 指向的文件不存在

**错误信息：**
```
ERROR: File not found: testcases/generated/模块/用例.xlsx
```

**原因：**
- 文件被手动删除
- 路径拼写错误
- 文件移动到其他位置

**解决方案：**

```bash
# 1. 检查文件是否真的存在
ls -la testcases/generated/模块/

# 2. 运行清理脚本（预览模式）
python3 test-case-generator/scripts/cleanup_testcase_store.py --dry-run

# 3. 确认需要清理后执行
python3 test-case-generator/scripts/cleanup_testcase_store.py
```

---

### 问题 6：platform_scope 值不规范

**错误信息：**
```
WARNING: Non-standard platform_scope value: 平台
```

**原因：**
- 使用了旧版值（平台、后端、大厅等）

**解决方案：**

自动转换：
```bash
# 运行 upsert 脚本会自动标准化
python3 test-case-generator/scripts/upsert_testcase_index.py --all
```

手动修正（如需要）：
```python
PLATFORM_MAPPING = {
    '平台': '账服',
    '后端': '账服',
    '大厅': '客户端',
    '运营活动': '账服'
}
```

---

### 问题 7：module-index.json 模块 ID 重复

**错误信息：**
```
ERROR: Duplicate module ID: personal-center
```

**原因：**
- 手动编辑时复制了条目
- 合并分支时产生冲突

**解决方案：**

1. 打开 `test-case-generator/references/module-index.json`
2. 搜索重复的 `id` 字段
3. 删除重复条目，保留一份正确的
4. 重新运行校验：
```bash
python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json
```

---

## Excel 导出问题

### 问题 8：Excel 缺少"备注"列

**现象：**
- 导出的 Excel 表格没有"备注"列
- 优先级标签缺失

**原因：**
- 没有使用正确的模板脚本
- rows.json 数据缺少 remark 字段

**解决方案：**

确保使用 `minimax-xlsx` 模板：

```python
# 在生成数据中包含 remark
{
    "序号": 1,
    "平台": "客户端",
    "模块": "个人中心",
    "功能点": "头像上传",
    "前置条件": "已登录",
    "操作步骤": "1. 点击头像...",
    "预期结果": "1. 弹出选择框...",
    "测试结果": "",
    "备注": "【功能测试】【P0】"
}
```

使用正确的脚本导出：
```bash
python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx \
    --template templates/testcase_template.xlsx
```

---

### 问题 9：Excel 样式丢失

**现象：**
- 导出的 Excel 没有表头颜色
- 字体格式不一致

**原因：**
- 直接使用 openpyxl 创建而非模板填充

**解决方案：**

必须使用模板填充脚本：
```bash
# 正确方式
python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx \
    --template templates/testcase_template.xlsx
```

模板脚本会：
1. 读取模板的 styles.xml
2. 保留原有样式
3. 填充数据到指定位置

---

### 问题 10：无法打开 Excel 文件

**错误信息：**
```
Excel 发现 unreadable content
```

**原因：**
- Excel 文件损坏
- XML 结构不完整
- 使用了不支持的 Excel 版本

**解决方案：**

1. 检查 openpyxl 版本：
```bash
pip3 show openpyxl
# 需要 >= 3.1.0
```

2. 重新生成文件

3. 尝试使用 WPS 或 LibreOffice 打开

---

## 多语言 JSON 问题

### 问题 11：语言集合不完整

**错误信息：**
```
ERROR: Missing language: fp-fp
```

**原因：**
- 只提供了部分语言的翻译
- 漏掉了某个语言

**解决方案：**

必须包含全部 7 种语言：
```json
{
  "languages": {
    "en-us": { ... },
    "id-id": { ... },
    "pt-pt": { ... },
    "es-es": { ... },
    "bn-bn": { ... },
    "tr-tr": { ... },
    "fp-fp": { ... }
  }
}
```

如果某些语言确实没有文案，可以：
1. 使用空字符串占位
2. 标记为 `draft` 状态

---

### 问题 12：JSON Schema 校验失败

**错误信息：**
```
ValidationError: 'url' is a required property
```

**原因：**
- 缺少必填字段（name, url, languages）
- options 配置格式错误

**解决方案：**

完整结构：
```json
{
  "name": "个人中心 - 免费旋转记录",
  "url": "https://example.com/free-spin-record",
  "preScriptPath": "",
  "languages": { ... },
  "options": {
    "matchRule": "normalized-exact",
    "captureRegion": { "x": 0, "y": 0, "width": 0, "height": 0 }
  }
}
```

运行校验：
```bash
python3 test-case-generator/scripts/validate_i18n_json.py \
    testcases/i18n/模块/文件.json
```

---

## 模块匹配问题

### 问题 13：无法识别主模块

**现象：**
- 生成的用例模块字段为空
- 匹配到错误的模块

**原因：**
- 需求文档中没有明确的模块关键词
- module-index.json 中缺少该模块定义

**解决方案：**

1. 在需求文档开头明确模块名称：
```markdown
# 模块：个人中心
# 功能：用户资料编辑
```

2. 如需新增模块，编辑 `module-index.json`：
```json
{
  "id": "new-module",
  "name": "新模块",
  "aliases": ["模块别名"],
  "trigger_words": ["关键词 1", "关键词 2"]
}
```

3. 重新运行索引校验：
```bash
python3 test-case-generator/scripts/validate_index.py \
    test-case-generator/references/module-index.json
```

---

## 脚本执行错误

### 问题 14：脚本权限不足

**错误信息：**
```
Permission denied: ./script_name.py
```

**解决方案：**

```bash
# 添加执行权限
chmod +x test-case-generator/scripts/*.py

# 或使用 python3 显式调用
python3 test-case-generator/scripts/script_name.py
```

---

### 问题 15：路径包含空格导致失败

**错误信息：**
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/with space/file.xlsx'
```

**解决方案：**

1. 使用引号包裹路径：
```bash
python3 script.py "/path/with space/file.xlsx"
```

2. 或转义空格：
```bash
python3 script.py /path/with\ space/file.xlsx
```

3. 最佳实践：避免在文件路径中使用空格

---

### 问题 16：脚本输出乱码

**现象：**
- 控制台显示中文乱码
- 日志文件乱码

**解决方案：**

1. 设置终端编码为 UTF-8：
```bash
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

2. 在脚本开头添加：
```python
# -*- coding: utf-8 -*-
```

3. Windows PowerShell：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## Git 相关问题

### 问题 17：索引文件冲突

**错误信息：**
```
CONFLICT (content): Merge conflict in testcases/testcase-index.json
```

**解决方案：**

1. 打开冲突文件，找到冲突标记：
```
<<<<<<< HEAD
"entries": [...]
=======
"entries": [...]
>>>>>>> branch-name
```

2. 手动合并两个分支的 entries 数组

3. 或者接受一方：
```bash
# 接受当前分支
git checkout --ours testcases/testcase-index.json

# 接受对方分支
git checkout --theirs testcases/testcase-index.json
```

4. 重新运行 upsert 脚本重建索引：
```bash
python3 test-case-generator/scripts/upsert_testcase_index.py --all
```

---

### 问题 18：大文件提交失败

**错误信息：**
```
File too large: testcases/generated/xxx.xlsx (50MB)
```

**原因：**
- Git 仓库对大文件有限制
- 测试用例 Excel 文件过大

**解决方案：**

1. 使用 Git LFS：
```bash
git lfs install
git lfs track "*.xlsx"
git lfs track "*.json"
```

2. 或在 `.gitignore` 中排除大文件目录：
```
testcases/generated/*.xlsx
```

3. 或使用外部存储（推荐）：
- 对象存储（S3、OSS）
- 内部文件服务器

---

## 诊断工具

### 检查清单

遇到问题时，依次运行以下命令：

```bash
# 1. 检查 Python 环境
python3 --version
python3 -c "import openpyxl, pandas, jsonschema; print('OK')"

# 2. 检查依赖
pip3 list | grep -E "openpyxl|pandas|jsonschema"

# 3. 检查索引格式
python3 -m json.tool testcases/testcase-index.json > /dev/null && echo "testcase-index.json: OK"
python3 -m json.tool testcases/i18n-index.json > /dev/null && echo "i18n-index.json: OK"
python3 -m json.tool test-case-generator/references/module-index.json > /dev/null && echo "module-index.json: OK"

# 4. 运行校验脚本
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
python3 test-case-generator/scripts/validate_i18n_index.py testcases/i18n-index.json
python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json

# 5. 检查孤立文件
python3 test-case-generator/scripts/cleanup_testcase_store.py --dry-run
```

---

## 获取帮助

如果以上方案无法解决问题：

1. **查看日志**：检查脚本输出的完整错误信息
2. **搜索 Issue**：在 GitHub Issues 中搜索类似问题
3. **创建 Issue**：提供以下信息：
   - 错误信息全文
   - 执行的命令
   - 环境信息（Python 版本、操作系统）
   - 相关索引片段（脱敏后）

---

## 版本兼容性

| 版本 | Python | openpyxl | pandas | jsonschema |
|------|--------|----------|--------|------------|
| v1.0.0 | 3.8+ | 3.1.0+ | 2.0.0+ | 4.17.0+ |

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-01 | 1.0 | 初始版本 |
