# 主题页子文件夹支持方案

## 完成时间
2026-04-15

## 需求背景

随着测试用例数量增长，主题页文件全部放在 `knowledge/wiki/topics/` 目录下变得难以管理。用户希望能够：

1. 在主题页文件夹内创建子文件夹
2. 按模块和活动类型组织主题页
3. 框架自动支持子文件夹路径
4. 索引文件同步更新

例如，将运营活动相关的主题页按类型分组：
```
knowledge/wiki/topics/运营活动/
├── 充值优惠/
│   ├── 复充返利活动.md
│   ├── 首充活动.md
│   └── 每日充值.md
├── 游戏优惠/
│   ├── 幸运卡片.md
│   ├── 免费旋转.md
│   └── 幸运转盘.md
├── 锦标赛/
│   └── 锦标赛.md
└── 任务系统/
    ├── 任务系统前后端优化.md
    └── 活动周期规则优化.md
```

## 解决方案

### 1. 子文件夹配置文件

**文件路径**：`knowledge/wiki/topics/submodule-config.json`

**配置格式**：
```json
{
  "模块名": {
    "用例名称": "子文件夹路径",
    ...
  },
  ...
}
```

**示例配置**：
```json
{
  "运营活动": {
    "复充返利活动": "充值优惠",
    "首充活动": "充值优惠",
    "每日充值": "充值优惠",
    "累计充值": "充值优惠",
    "阶梯返利": "充值优惠",
    "幸运卡片": "游戏优惠",
    "集福活动": "游戏优惠",
    "五福合成": "游戏优惠",
    "免费旋转": "游戏优惠",
    "幸运转盘": "游戏优惠",
    "锦标赛": "锦标赛",
    "任务系统": "任务系统",
    "活动周期规则": "任务系统",
    "洗码活动": "其他活动",
    "世界杯竞猜": "其他活动"
  }
}
```

### 2. 修改同步脚本

**文件**：`engine/scripts/sync_testcase_snapshot.py`

**新增功能**：

1. **配置加载函数**：
```python
def load_submodule_config() -> dict:
    """从 JSON 文件加载子文件夹配置。"""
```

2. **主题页路径计算函数**：
```python
def get_theme_path_with_submodule(
    title: str,
    module: str,
    submodule_overrides: dict = None
) -> Path:
    """根据配置计算主题页路径（支持子文件夹）。"""
```

3. **命令行参数**：
```bash
# 使用配置文件自动匹配子文件夹
python3 sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx

# 手动指定子文件夹
python3 sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx \
    --submodule 充值优惠

# 使用自定义配置文件
python3 sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx \
    --config custom-submodule-config.json
```

### 3. 目录结构

**执行前**：
```
knowledge/wiki/topics/
├── 复充返利活动.md
├── 幸运卡片（集福活动）.md
├── 锦标赛.md
└── ...
```

**执行后**：
```
knowledge/wiki/topics/
├── 运营活动/
│   ├── 充值优惠/
│   │   └── 复充返利活动.md
│   ├── 游戏优惠/
│   │   ├── 幸运卡片（集福活动）.md
│   │   └── 免费旋转功能优化汇总.md
│   ├── 锦标赛/
│   │   └── 锦标赛.md
│   ├── 任务系统/
│   └── 其他活动/
├── 洗码活动改造.md  (待移动)
├── 任务系统前后端优化.md  (待移动)
└── 分享好礼优化.md  (待移动)
```

### 4. 索引文件更新

**文件**：`knowledge/index.md`

**更新内容**：
```markdown
## 测试主题 (topics)

> **说明**：主题页按模块和子模块组织，便于管理和查找。
> 格式：`knowledge/wiki/topics/<模块>/<子模块>/<功能名称>.md`

### 运营活动

#### 充值优惠
- [[复充返利活动]] - 复充返利活动的测试用例和历史记录

#### 游戏优惠
- [[幸运卡片（集福活动）]] - 幸运卡片/集福活动的测试用例和历史记录
- [[免费旋转功能优化汇总]] - 免费旋转功能的测试用例和历史记录

#### 锦标赛
- [[锦标赛]] - 锦标赛活动的测试用例和历史记录

#### 任务系统
- [[任务系统前后端优化]] - 任务系统优化的测试用例和历史记录
```

### 5. 主题页内容更新

移动到子文件夹后，主题页中的相对路径需要更新：

**原路径**（在 `topics/复充返利活动.md`）：
```markdown
## 已生成测试用例

| 文件名 | ... |
|--------|-----|
| [复充返利活动.xlsx](../../outputs/generated/运营活动/复充返利活动.xlsx) | ... |
```

**新路径**（在 `topics/运营活动/充值优惠/复充返利活动.md`）：
```markdown
## 已生成测试用例

| 文件名 | ... |
|--------|-----|
| [复充返利活动.xlsx](../../../../outputs/generated/运营活动/复充返利活动.xlsx) | ... |
```

同步脚本会自动处理路径更新。

## 使用方法

### 方法 1：使用配置文件（推荐）

1. **编辑配置文件**：
```bash
# 编辑 knowledge/wiki/topics/submodule-config.json
# 添加用例名称到子文件夹的映射
```

2. **执行同步**：
```bash
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx
```

3. **验证结果**：
```bash
# 主题页会创建/移动到配置的子文件夹
ls knowledge/wiki/topics/运营活动/充值优惠/
```

### 方法 2：手动指定子文件夹

```bash
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx \
    --submodule 充值优惠
```

### 方法 3：批量同步

```bash
# 同步所有 Excel 文件，根据配置文件自动分配到子文件夹
python3 engine/scripts/sync_testcase_snapshot.py --all
```

## 文件清单

### 新增文件
- `knowledge/wiki/topics/submodule-config.json` - 子文件夹配置文件
- `knowledge/wiki/topics/运营活动/充值优惠/` - 子文件夹
- `knowledge/wiki/topics/运营活动/游戏优惠/` - 子文件夹
- `knowledge/wiki/topics/运营活动/锦标赛/` - 子文件夹
- `knowledge/wiki/topics/运营活动/任务系统/` - 子文件夹
- `knowledge/wiki/topics/运营活动/其他活动/` - 子文件夹

### 修改文件
- `engine/scripts/sync_testcase_snapshot.py` - 添加子文件夹支持
- `engine/skills/testcase-format/SKILL.md` - 添加子文件夹说明
- `knowledge/index.md` - 更新主题页索引结构

### 移动文件
- `复充返利活动.md` → `运营活动/充值优惠/复充返利活动.md`
- `幸运卡片（集福活动）.md` → `运营活动/游戏优惠/幸运卡片（集福活动）.md`
- `免费旋转功能优化汇总.md` → `运营活动/游戏优惠/免费旋转功能优化汇总.md`
- `锦标赛.md` → `运营活动/锦标赛/锦标赛.md`

## 验证结果

```bash
# 1. 验证目录结构
$ ls -la knowledge/wiki/topics/运营活动/
drwxr-xr-x  充值优惠/
drwxr-xr-x  游戏优惠/
drwxr-xr-x  锦标赛/
drwxr-xr-x  任务系统/
drwxr-xr-x  其他活动/

# 2. 验证同步命令
$ python3 engine/scripts/sync_testcase_snapshot.py --dry-run \
    outputs/generated/运营活动/复充返利活动.xlsx
Would sync: outputs/generated/运营活动/复充返利活动.xlsx
  Snapshot: outputs/snapshots/运营活动/复充返利活动/<timestamp>.json
  Theme page: knowledge/wiki/topics/运营活动/充值优惠/复充返利活动.md

# 3. 验证索引文件
$ grep -A 5 "充值优惠" knowledge/index.md
#### 充值优惠
- [[复充返利活动]] - 复充返利活动的测试用例和历史记录
```

## 扩展功能（可选）

1. **自动移动现有主题页**：
   ```bash
   python3 engine/scripts/sync_testcase_snapshot.py --move-existing
   ```

2. **子文件夹自动创建**：
   - 同步时如子文件夹不存在，自动创建

3. **路径验证**：
   - 验证主题页中的相对路径是否正确
   - 修复路径引用错误

4. **索引自动更新**：
   - 主题页移动后自动更新 `knowledge/index.md`

## 最佳实践

1. **命名规范**：
   - 子文件夹名称简洁明了（2-5 个汉字）
   - 使用中文命名，与模块名称保持一致

2. **分组原则**：
   - 按活动类型分组（充值优惠、游戏优惠、锦标赛等）
   - 每个子文件夹包含 3-10 个主题页为宜

3. **配置维护**：
   - 新增用例时同步更新配置文件
   - 定期检查和清理过期配置

4. **版本控制**：
   - 配置文件纳入 git 版本控制
   - 主题页移动时保留 git 历史记录

## 相关文件

- 配置文件：`knowledge/wiki/topics/submodule-config.json`
- 同步脚本：`engine/scripts/sync_testcase_snapshot.py`
- 技能文档：`engine/skills/testcase-format/SKILL.md`
- 索引文件：`knowledge/index.md`
