# 故障排查与避坑指南

本文档汇总了 QA 测试用例生成器使用过程中的常见问题及解决方案。

---

## 目录

- [核心原则](#核心原则)
- [环境安装问题](#环境安装问题)
- [索引校验失败](#索引校验失败)
- [Excel 导出问题](#excel-导出问题)
- [多语言 JSON 问题](#多语言-json-问题)
- [模块匹配问题](#模块匹配问题)
- [脚本执行错误](#脚本执行错误)
- [Git 相关问题](#git-相关问题)
- [诊断工具](#诊断工具)
- [获取帮助](#获取帮助)

---

## 核心原则

**三条黄金法则**，违反任何一条都会导致索引校验失败：

1. **路径格式**：索引中的 `rel_path` 始终相对于 `testcases/` 目录
   - 正确：`generated/文件名.xlsx`
   - 错误：`testcases/generated/文件名.xlsx`

2. **文件名规范**：
   - 避免使用空格（使用下划线或连字符）
   - 中文文件名格式：`<模块名>_<YYYYMMDD>.xlsx`

3. **索引更新前验证**：
   - 先用 `os.listdir()` 确认文件实际名称
   - 再用脚本更新索引

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

### 问题 8：macOS Unicode 规范化导致文件路径校验失败（高频）

**错误信息：**
```
ERROR: entry 'tc-xxx' points to missing file: generated/无 CPF 用户限制功能_20260408.xlsx
```
但 `ls` 显示文件确实存在。

**原因：**
- macOS 文件系统使用 NFD（规范化分解）存储 Unicode 文件名
- Python 的 `Path.exists()` 在某些情况下使用 NFC（规范化组合）进行检查
- 中文字符在 NFD 和 NFC 之间可能有不同的字节表示

**验证问题：**
```bash
# 检查文件实际存在
ls -la testcases/generated/ | grep "无 CPF"

# 但 Python 检查失败
python3 -c "from pathlib import Path; print(Path('testcases/generated/无 CPF 用户限制功能_20260408.xlsx').exists())"
```

**解决方案：**

#### 方案 1：手动创建索引条目（推荐）

```bash
python3 -c "
import json, hashlib
from pathlib import Path
from datetime import datetime

index_path = Path('testcases/testcase-index.json')
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 用 os.listdir 获取实际文件名（绕过 Unicode 问题）
import os
files = os.listdir('testcases/generated/')
target = [f for f in files if '你的关键词' in f][0]
rel_path = 'generated/' + target

now = datetime.now().astimezone().replace(microsecond=0).isoformat()
digest = hashlib.sha1(rel_path.encode('utf-8')).hexdigest()[:8]

entry = {
    'id': f'tc-{rel_path.replace(\"/\", \"-\")}-{digest}',
    'group_key': f'group-模块名 - 主题名-{hashlib.sha1(\"模块名::主题名\".encode()).hexdigest()[:8]}',
    'title': '你的主题',
    'module': '你的模块',
    'module_ids': ['module-你的模块'],
    'topic': '你的主题',
    'platform_scope': ['账服', '客户端'],
    'format': 'xlsx',
    'rel_path': rel_path,
    'template': '',
    'source_refs': [],
    'tags': ['你的模块', '你的主题'],
    'status': 'active',
    'created_at': now,
    'updated_at': now
}

data['entries'].append(entry)
data['updated_at'] = now

with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('Index updated')
"
```

#### 方案 2：修复已有索引路径

```bash
python3 -c "
import os
import json
from pathlib import Path

# 获取实际文件名（使用 os.listdir 绕过 Unicode 问题）
files = os.listdir('testcases/generated/')
target_file = [f for f in files if 'CPF' in f][0]
rel_path = 'generated/' + target_file

# 修复索引
index_path = Path('testcases/testcase-index.json')
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for entry in data.get('entries', []):
    if 'CPF' in entry.get('rel_path', ''):
        entry['rel_path'] = rel_path  # 使用实际文件名
        break

with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
```

#### 方案 3：使用 NFC 规范化统一路径

```python
import unicodedata
path = unicodedata.normalize('NFC', 'testcases/generated/无 CPF 用户限制功能_20260408.xlsx')
# 然后使用规范化后的路径
```

**最佳实践：**
1. 索引中的 `rel_path` 应始终相对于 `testcases/` 目录（如 `generated/xxx.xlsx`）
2. 避免在文件名中使用空格，使用下划线或连字符替代
3. 在创建索引条目前，先用 `os.listdir()` 获取实际文件名

---

### 问题 9：Excel 导出后索引路径格式错误（高频）

**现象：**
- Excel 文件成功导出到 `testcases/generated/`
- 但索引校验失败，提示文件不存在

**原因：**
- `rel_path` 被错误地设置为 `testcases/generated/xxx.xlsx`
- 校验脚本会在 `testcases/` 目录下再次拼接 `testcases/generated/`
- 正确格式应该是 `generated/xxx.xlsx`

**解决方案：**

修复已有索引：
```bash
python3 -c "
import json
from pathlib import Path

index_path = Path('testcases/testcase-index.json')
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 修复所有以 testcases/ 开头的 rel_path
fixed = 0
for entry in data.get('entries', []):
    rel_path = entry['rel_path']
    if rel_path.startswith('testcases/'):
        new_path = rel_path[len('testcases/'):]
        print(f'Fixing: {rel_path} -> {new_path}')
        entry['rel_path'] = new_path
        fixed += 1

# 保存
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'Fixed {fixed} entries')
"
```

验证修复：
```bash
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
```

---

## Excel 导出问题

### 问题 10：Excel 缺少"备注"列

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

### 问题 11：Excel 样式丢失

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

### 问题 12：无法打开 Excel 文件

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

### 问题 13：语言集合不完整

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

### 问题 14：JSON Schema 校验失败

**错误信息：**
```
ValidationError: 'url' is a required property
```

**原因：**
- 缺少必填字段（name, url, languages）
- options 配置错误

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

### 问题 15：多语言检测逻辑无法识别中文语言名称

**症状：**
- 多语言 JSON 只提取到少量条目，但网页原型中实际有大量多语言对照内容
- 验证通过但覆盖不全

**原因：**
- 原检测逻辑只搜索语言代码（如 `en-us`、`id-id`）
- 但 Axure 导出的 HTML 中使用的是中文语言名称（如 `英文`、`印尼语`、`巴西葡语`）

**修复方案：**
```python
# 新增语言名称映射表
LANG_MAP = {
    'en-us': ['英文', '英语', 'en', 'en-us', 'English'],
    'id-id': ['印尼语', '印度尼西亚语', 'id', 'Indonesian', 'Bahasa'],
    'pt-pt': ['葡萄牙语', '葡语', '巴西葡语', 'pt', 'Portuguese'],
    'es-es': ['西班牙语', '西语', 'es', 'Spanish'],
    'bn-bn': ['孟加拉语', '孟加拉', 'bn', 'Bengali'],
    'tr-tr': ['土耳其语', '土语', 'tr', 'Turkish'],
    'fp-fp': ['法语', '法文', 'fr', 'French'],
}

def detect_language(text):
    text_lower = text.lower()
    for lang_code, names in LANG_MAP.items():
        for name in names:
            if name.lower() in text_lower:
                return lang_code
    return None
```

**改进提取逻辑：**
- 按 div 区块分组，确保同一区块内的 7 种语言被归为一个完整条目
- 去重：使用英文内容作为去重依据
- `key` 字段改为可选，需求未提供时留空

---

### 问题 16：validate_i18n_json.py 验证脚本不支持 entries 格式

**错误信息：**
```
ERROR: missing root keys: languages
```

**原因：**
- 验证脚本期望根级别有 `languages` 字段
- 但 SKILL.md 规范使用 `entries` 数组格式

**解决方案：**

更新 `validate_i18n_json.py`：
1. 修改 `REQUIRED_ROOT_KEYS` 从 `languages` 改为 `entries`
2. 验证逻辑从检查根级 `languages` 改为遍历 `entries[]` 数组
3. `key` 字段改为可选（`if 'key' in entry and ...`）

**经验教训：**
1. 对于 Axure 导出的 HTML 原型文件，优先使用 Python 提取文本，不要直接用 Read 工具
2. 对于包含特殊字符的文件名，先用 `ls` 确认，再操作
3. 对于大的 `data.js` 文件，直接解析 HTML 更高效
4. 多语言检测需要同时支持语言代码和中文语言名称
5. 多语言 JSON 的 `key` 字段是可选的，需求未提供时留空

---

## 模块匹配问题

### 问题 17：无法识别主模块

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

### 问题 18：脚本权限不足

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

### 问题 19：路径包含空格导致失败

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

### 问题 20：upsert_testcase_index.py 无法找到含中文的文件名

**错误信息：**
```
ERROR: file not found: /path/to/testcases/generated/无 CPF 用户限制功能_20260408.xlsx
```
但文件实际存在于该路径。

**原因：**
- shell 对中文字符的处理问题
- 参数传递过程中文件名被截断或转义错误

**解决方案：**

#### 方法 1：在 Python 中直接调用（推荐）
```bash
python3 -c "
import sys
sys.path.insert(0, 'test-case-generator/scripts')
from pathlib import Path
from upsert_testcase_index import main
import sys as sys_module
sys_module.argv = [
    'upsert_testcase_index.py',
    'testcases/generated/你的文件.xlsx',
    '--topic', '你的主题',
    '--module', '你的模块',
    '--status', 'auto'
]
main()
"
```

#### 方法 2：确保路径正确引用
```bash
# 使用双引号包裹完整路径
python3 test-case-generator/scripts/upsert_testcase_index.py "testcases/generated/无 CPF 用户限制功能_20260408.xlsx" --topic "xxx" --module "xxx"
```

#### 方法 3：使用相对路径而非绝对路径
```bash
# 在项目目录下执行
cd /path/to/QA
python3 test-case-generator/scripts/upsert_testcase_index.py testcases/generated/你的文件.xlsx
```

---

### 问题 21：脚本输出乱码

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

### 问题 22：索引文件冲突

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

### 问题 23：大文件提交失败

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

生成/导出测试用例后，依次检查：

- [ ] Excel 文件存在于 `testcases/generated/` 目录
- [ ] 文件名格式：`<模块名>_<YYYYMMDD>.xlsx`
- [ ] 索引中 `rel_path` 格式：`generated/文件名.xlsx`
- [ ] 索引校验通过：`validate_testcase_index.py` 返回 OK
- [ ] 模块索引校验通过：`validate_index.py` 返回 OK

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

### 常用命令

```bash
# 验证测试用例索引
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json

# 验证模块索引
python3 test-case-generator/scripts/validate_index.py test-case-generator/references/module-index.json

# 验证多语言 JSON
python3 test-case-generator/scripts/validate_i18n_json.py testcases/i18n/模块/文件.json

# 清理过期文件（先预览）
python3 test-case-generator/scripts/cleanup_testcase_store.py --dry-run

# 查看索引内容
python3 -c "import json; print(json.dumps(json.load(open('testcases/testcase-index.json')), ensure_ascii=False, indent=2))"
```

---

### 标准操作流程

#### 生成测试用例并导出

```bash
# 1. 在 Claude Code 中运行
/qa 生成测试用例
# 粘贴需求 -> 选择完整用例 -> 选择导出 Excel 并更新索引

# 2. 验证导出结果
ls -la testcases/generated/模块名_*.xlsx

# 3. 验证索引
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json

# 4. 如索引失败，手动修复（见问题 8/9）
```

#### 补充已有用例

```bash
# 1. 读取索引
python3 -c "
import json
with open('testcases/testcase-index.json') as f:
    data = json.load(f)
for e in data.get('entries', []):
    print(f\"{e['module']} - {e['title']} [{e['format']}] - {e.get('updated_at', '')[:10]}\")
"

# 2. 选择要补充的用例文件
# 3. 生成补充内容并追加
python3 test-case-generator/scripts/xlsx_append_and_highlight.py \
    existing.xlsx new_rows.json output.xlsx --highlight
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
| 2026-04-08 | 1.2 | 整合 troubleshooting.md 和 lessons-learned.md，合并重复问题，添加核心原则章节 |
| 2026-04-08 | 1.1 | 添加 macOS Unicode 规范化问题、upsert 脚本路径问题、索引路径格式问题 |
| 2026-04-01 | 1.0 | 初始版本 |
