# QA 技能包 - 避坑指南

本文档记录使用 QA 测试用例生成技能包时遇到的典型问题和最佳实践。

---

## 核心原则

1. **路径格式**：索引中的 `rel_path` 始终相对于 `testcases/` 目录
   - 正确：`generated/文件名.xlsx`
   - 错误：`testcases/generated/文件名.xlsx`

2. **文件名规范**：
   - 避免使用空格
   - 中文文件名使用下划线分隔日期
   - 格式：`<模块名>_<YYYYMMDD>.xlsx`

3. **索引更新前验证**：
   - 先用 `os.listdir()` 确认文件实际名称
   - 再用脚本更新索引

---

## 高频问题速查

### Q1: upsert 脚本报 "file not found" 但文件确实存在

**症状**：
```
ERROR: file not found: /path/to/testcases/generated/无 CPF 用户限制功能_20260408.xlsx
```

**快速解决**：
```bash
# 方法：手动创建索引条目而非使用脚本
python3 -c "
import json, hashlib
from pathlib import Path
from datetime import datetime

index_path = Path('testcases/testcase-index.json')
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 用 os.listdir 获取实际文件名
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

---

### Q2: 索引校验失败 "points to missing file"

**症状**：
```
ERROR: entry 'tc-xxx' points to missing file: generated/xxx.xlsx
```

**原因**：macOS Unicode 规范化（NFD/NFC）问题

**快速解决**：
```bash
# 修复 rel_path 路径格式
python3 -c "
import json
from pathlib import Path

index_path = Path('testcases/testcase-index.json')
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for entry in data.get('entries', []):
    if entry['rel_path'].startswith('testcases/'):
        entry['rel_path'] = entry['rel_path'][len('testcases/'):]

with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print('Fixed')
"

# 验证
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json
```

---

### Q3: Excel 导出成功但索引损坏

**症状**：
- Excel 文件正常生成
- 索引文件包含错误的路径

**预防方案**：
```bash
# 标准流程
# 1. 导出 Excel
python3 test-case-generator/scripts/xlsx_fill_testcase_template.py \
    rows.json output.xlsx --template templates/testcase_template.xlsx

# 2. 移动到目标目录
mv output.xlsx "testcases/generated/模块名_$(date +%Y%m%d).xlsx"

# 3. 手动更新索引（避免脚本问题）
# 使用上面的 Q1 解决方案
```

---

## 标准操作流程

### 生成测试用例并导出

```bash
# 1. 在 Claude Code 中运行
/qa 生成测试用例
# 粘贴需求 -> 选择完整用例 -> 选择导出 Excel 并更新索引

# 2. 验证导出结果
ls -la testcases/generated/模块名_*.xlsx

# 3. 验证索引
python3 test-case-generator/scripts/validate_testcase_index.py testcases/testcase-index.json

# 4. 如索引失败，手动修复（见 Q1/Q2）
```

### 补充已有用例

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

## 检查清单

生成/导出测试用例后，依次检查：

- [ ] Excel 文件存在于 `testcases/generated/` 目录
- [ ] 文件名格式：`<模块名>_<YYYYMMDD>.xlsx`
- [ ] 索引中 `rel_path` 格式：`generated/文件名.xlsx`
- [ ] 索引校验通过：`validate_testcase_index.py` 返回 OK
- [ ] 模块索引校验通过：`validate_index.py` 返回 OK

---

## 常用命令

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

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-04-08 | 新增附录：多语言识别逻辑、验证脚本格式问题 |
| 2026-04-08 | 初始版本，记录 Unicode 规范化、路径格式、upsert 脚本问题 |

---

## 附录：典型问题案例

### 问题 4：多语言检测逻辑无法识别中文语言名称

**症状**：
- 多语言 JSON 只提取到少量条目，但网页原型中实际有大量多语言对照内容
- 验证通过但覆盖不全

**原因**：
- 原检测逻辑只搜索语言代码（如 `en-us`、`id-id`）
- 但 Axure 导出的 HTML 中使用的是中文语言名称（如 `英文`、`印尼语`、`巴西葡语`）

**修复方案**：
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

**改进提取逻辑**：
- 按 div 区块分组，确保同一区块内的 7 种语言被归为一个完整条目
- 去重：使用英文内容作为去重依据
- `key` 字段改为可选，需求未提供时留空

---

### 问题 5：validate_i18n_json.py 验证脚本不支持 entries 格式

**症状**：
```
ERROR: missing root keys: languages
```

**原因**：
- 验证脚本期望根级别有 `languages` 字段
- 但 SKILL.md 规范使用 `entries` 数组格式

**修复方案**：
更新 `validate_i18n_json.py`：
1. 修改 `REQUIRED_ROOT_KEYS` 从 `languages` 改为 `entries`
2. 验证逻辑从检查根级 `languages` 改为遍历 `entries[]` 数组
3. `key` 字段改为可选（`if 'key' in entry and ...`）

**经验教训**：
1. 对于 Axure 导出的 HTML 原型文件，优先使用 Python 提取文本，不要直接用 Read 工具
2. 对于包含特殊字符的文件名，先用 `ls` 确认，再操作
3. 对于大的 `data.js` 文件，直接解析 HTML 更高效
4. 多语言检测需要同时支持语言代码和中文语言名称
5. 多语言 JSON 的 `key` 字段是可选的，需求未提供时留空
