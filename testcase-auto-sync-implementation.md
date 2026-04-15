# 测试用例自动同步机制实现总结

## 完成时间
2026-04-14

## 问题描述

用户生成测试用例后，可能会在 Excel 文件中自行修改内容（如修改预期结果、补充操作步骤等）。这些修改之前无法同步回知识库和主题页，导致：

1. 主题页中的测试点摘要与 Excel 实际内容不一致
2. 查询知识库时展示的测试点可能已过时
3. 无法追踪用户修改历史

## 解决方案

采用**快照机制** + **按需同步**的混合方案：

### 核心组件

1. **快照生成脚本** (`snapshot_testcase.py`)
   - 从 Excel 文件提取测试用例数据
   - 保存为 JSON 格式的快照
   - 生成测试点摘要

2. **同步脚本** (`sync_testcase_snapshot.py`)
   - 读取最新 Excel 内容
   - 保存/更新快照
   - 更新主题页的测试点摘要

3. **Skill 修改**
   - `testcase-format`：导出 Excel 后自动保存快照
   - `qa`：添加同步选项

## 新增文件

### 1. `engine/scripts/snapshot_testcase.py`
从 Excel 文件提取测试用例数据并保存为快照。

**功能**：
- 读取 Excel 文件的测试用例数据（从第 8 行开始）
- 提取元数据（测试平台、日期等）
- 生成测试点摘要（按账服/客户端分组）
- 保存 JSON 格式快照

**使用方法**：
```bash
# 显示模式（预览将提取的内容）
python3 engine/scripts/snapshot_testcase.py --show outputs/generated/运营活动/复充返利活动.xlsx

# 保存快照
python3 engine/scripts/snapshot_testcase.py outputs/generated/运营活动/复充返利活动.xlsx

# 指定输出目录
python3 engine/scripts/snapshot_testcase.py outputs/generated/运营活动/复充返利活动.xlsx \
    --output-dir outputs/snapshots/复充返利活动/
```

**快照 JSON 格式**：
```json
{
  "version": 1,
  "snapshot_at": "2026-04-14T20:05:54.691802+08:00",
  "source_file": "outputs/generated/运营活动/复充返利活动.xlsx",
  "metadata": {
    "title": "复充返利活动",
    "module": "运营活动",
    "platform_scope": ["账服", "客户端"],
    "total_cases": 22
  },
  "testcases": [...],
  "test_point_summary": {
    "server_side": ["复充返利活动配置", ...],
    "client_side": ["复充返利弹框 - 触发条件 - 登录检测", ...],
    "all_points": [...]
  },
  "statistics": {
    "server_side_count": 12,
    "client_side_count": 10
  }
}
```

### 2. `engine/scripts/sync_testcase_snapshot.py`
同步 Excel 内容到快照和主题页。

**功能**：
- 读取最新 Excel 内容
- 保存/更新快照
- 更新主题页的测试点摘要部分
- 支持批量同步（`--all` 选项）

**使用方法**：
```bash
# 同步单个文件
python3 engine/scripts/sync_testcase_snapshot.py \
    outputs/generated/运营活动/复充返利活动.xlsx

# 同步所有 Excel 文件
python3 engine/scripts/sync_testcase_snapshot.py --all

# 预览模式（显示将要执行的操作）
python3 engine/scripts/sync_testcase_snapshot.py --dry-run --all
```

## 修改文件

### 1. `engine/skills/testcase-format/SKILL.md`
**修改点**：
- 添加职责：保存快照（第 5 项）
- 添加快照生成规则章节
- 更新导出成功输出格式（包含快照路径）

### 2. `.claude/commands/qa.md`
**修改点**：
- 欢迎语添加选项 5：同步已生成用例
- 添加选项 5 响应流程（同步单个/全部/查看历史）
- 更新选项说明表格

### 3. 主题页格式（示例：`knowledge/wiki/topics/复充返利活动.md`）
**新增内容**：
```markdown
## 测试点摘要

> 数据来源：快照文件 `../../../outputs/snapshots/运营活动/复充返利活动/2026-04-14T20-05-54.691802+08:00.json`
> 最后同步时间：2026-04-14 20:05:54

**账服用例**：
- 复充返利活动配置
- 复充返利资格判定 - 余额条件
- ...

**客户端用例**：
- 复充返利弹框 - 触发条件 - 登录检测
- ...
```

## 目录结构

```
QA/
├── engine/
│   └── scripts/
│       ├── snapshot_testcase.py          ← 新增
│       └── sync_testcase_snapshot.py     ← 新增
├── outputs/
│   ├── generated/                        # Excel 文件
│   └── snapshots/                        ← 新增
│       └── <模块>/
│           └── <用例名称>/
│               └── <timestamp>.json      # 快照文件
└── knowledge/
    └── wiki/
        └── topics/                       # 主题页（已更新）
            └── <功能名称>.md
```

## 使用流程

### 场景 1：生成新用例后
```
用户：/qa → 生成测试用例 → 导出 Excel
系统：
1. 生成 Excel 文件（xlsx_fill_testcase_template.py）
2. 更新索引（upsert_testcase_index.py）
3. 创建/更新主题页
4. 自动保存快照（snapshot_testcase.py）← 新增
```

### 场景 2：用户修改 Excel 后
```
用户：在 Excel 中修改了用例内容
用户：/qa → 选择「同步已生成用例」→ 选择文件
系统：
1. 读取最新 Excel 内容
2. 保存新快照
3. 更新主题页测试点摘要
4. 显示同步结果
```

### 场景 3：批量同步
```
用户：/qa → 选择「同步已生成用例」→ 选择「同步全部」
系统：
1. 扫描 outputs/generated/ 所有 Excel 文件
2. 批量保存快照
3. 批量更新主题页
4. 显示同步报告
```

## 验证结果

### 快照生成验证
```bash
$ python3 engine/scripts/snapshot_testcase.py --show outputs/generated/运营活动/复充返利活动.xlsx
=== 复充返利活动.xlsx ===
Module: 运营活动
Total testcases: 22
Server side: 12
Client side: 10
```

### 同步验证
```bash
$ python3 engine/scripts/sync_testcase_snapshot.py outputs/generated/运营活动/复充返利活动.xlsx
Synced: 复充返利活动.xlsx
  Snapshot: outputs/snapshots/运营活动/复充返利活动/2026-04-14T20-05-54.691802+08-00.json
  Theme page: knowledge/wiki/topics/复充返利活动.md

Successfully synced 1 file(s)
```

### 主题页验证
```markdown
## 测试点摘要

> 数据来源：快照文件 `../../../outputs/snapshots/运营活动/复充返利活动/2026-04-14T20-05-54.691802+08-00.json`
> 最后同步时间：2026-04-14 20:05:54

**账服用例**：
- 复充返利活动配置
- 复充返利资格判定 - 余额条件
...
```

## 优势

1. **可追溯**：每次修改都有快照记录
2. **可比较**：快照之间可以比较差异
3. **低开销**：不需要每次启动都扫描，只在需要时同步
4. **用户友好**：提供多种同步方式（单个/批量/预览）

## 扩展功能（可选）

1. **差异报告**：
   - 比较新旧快照
   - 高亮显示变化的测试点
   - 生成变更日志

2. **版本历史**：
   - 主题页显示历史版本列表
   - 可回溯查看旧版本测试点

3. **自动触发器**：
   - 文件监听（inotify / fswatch）
   - 当 Excel 文件变化时自动同步

## 相关文件

- 快照脚本：`engine/scripts/snapshot_testcase.py`
- 同步脚本：`engine/scripts/sync_testcase_snapshot.py`
- testcase-format skill: `engine/skills/testcase-format/SKILL.md`
- QA 入口：`.claude/commands/qa.md`
- 示例主题页：`knowledge/wiki/topics/复充返利活动.md`
