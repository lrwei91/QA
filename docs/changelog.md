# 变更日志 (CHANGELOG)

本文档记录 QA 测试用例生成器项目的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.2.0] - 2026-04-08

### 变更

#### 文档整合
- **troubleshooting.md**：整合原 `lessons-learned.md` 内容，合并为《故障排查与避坑指南》
  - 新增「核心原则」章节，强调三条黄金法则
  - 合并重复的 Unicode 规范化问题（原问题 19/20 与 Q1/Q2）
  - 合并重复的索引路径格式问题（原问题 21 与 Q2）
  - 统一问题编号（从 21 个扩展到 23 个）
- **lessons-learned.md**：已删除，内容全部迁移至 troubleshooting.md

### 优化

#### 文档结构
- 将高频问题（Unicode 规范化、路径格式错误）标记为「高频」
- 添加「标准操作流程」章节
- 整合检查清单和常用命令到诊断工具章节

---

## [1.0.2] - 2026-04-08

### 新增

#### 多语言识别增强
- 支持中文语言名称识别（如 `英文`、` 印尼语`、` 巴西葡语`）
- 新增语言名称映射表 `LANG_MAP`，同时支持中文和英文/代码
- 改进提取逻辑：按 div 区块分组，确保同一区块内的 7 种语言被归为一个条目

### 修复

#### validate_i18n_json.py
- 支持 `entries` 数组格式（符合 SKILL.md 规范）
- `key` 字段改为可选，需求未提供时留空

### 文档

#### troubleshooting.md（整合原 lessons-learned.md）
- 整合避坑指南内容到故障排查文档
- 新增核心原则章节
- 合并重复的 Unicode 规范化、路径格式问题

#### SKILL.md
- 明确多语言 JSON 中 `key` 字段为可选
- 删除与 qa.md 重复的章节（Welcome message、Test case type selection、Excel Export Options、Supplement Existing Testcases、Error Handling）

---

## [1.0.1] - 2026-04-08

### 新增

#### 文档
- **troubleshooting.md**：故障排查与避坑指南（整合原 lessons-learned.md 内容）
  - 路径格式规范
  - Unicode 规范化问题（NFD/NFC）
  - 索引手动修复方法
  - 标准操作流程
  - 检查清单

#### 故障排查 (troubleshooting.md)
- **问题 19**：upsert_testcase_index.py 无法找到含中文的文件名
- **问题 20**：macOS Unicode 规范化导致文件路径校验失败
- **问题 21**：Excel 导出后索引路径格式错误

### 修复

#### 索引路径格式
- 修正 `rel_path` 格式应为 `generated/xxx.xlsx` 而非 `testcases/generated/xxx.xlsx`
- 添加手动修复脚本用于快速修正路径格式

### 优化

#### 工作流程
- 推荐使用 `os.listdir()` 获取实际文件名后再更新索引
- 避免在文件名中使用空格，推荐使用下划线

---

## [1.0.0] - 2026-04-07

### 新增

#### 核心功能
- **测试用例生成**：支持从需求文档/PRD/接口说明自动生成结构化测试用例
  - 主模块自动识别
  - 客户端/账服平台自动拆分
  - 增量补充支持
  - Excel 模板保真导出

- **多语言校验 JSON**：支持 7 种语言的文案校验 JSON 生成
  - 固定语言集合：en-us, id-id, pt-pt, es-es, bn-bn, tr-tr, fp-fp
  - Schema 校验
  - 草稿状态支持

- **双索引结构**
  - `testcases/testcase-index.json`：测试用例索引
  - `testcases/i18n-index.json`：多语言 JSON 索引
  - 通过 `group_key` 关联同一需求下的不同产物

- **模块索引**
  - `test-case-generator/references/module-index.json`
  - 定义 27+ 业务模块及其依赖关系
  - 支持模块别名和触发词匹配

#### 脚本工具 (10 个)
| 脚本 | 用途 |
|------|------|
| `upsert_testcase_index.py` | 新增/更新索引条目 |
| `validate_testcase_index.py` | 校验测试用例索引 |
| `validate_i18n_index.py` | 校验多语言索引 |
| `validate_i18n_json.py` | 校验单个多语言 JSON |
| `validate_index.py` | 校验模块索引 |
| `cleanup_testcase_store.py` | 清理过期/孤立文件 |
| `diff_testcase_indexes.py` | 比较索引差异 |
| `export_testcase_report.py` | 生成覆盖率报告 |
| `generate_testcase_from_template.py` | 从模板生成用例 |
| `xlsx_append_and_highlight.py` | Excel 追加标黄 |

#### 文档体系
- `README.md`：项目说明
- `docs/user-guide.md`：5 分钟快速入门
- `test-case-generator/SKILL.md`：技能包完整规则
- `test-case-generator/scripts/README.md`：脚本使用手册
- `test-case-generator/references/`：
  - `testcase-store.md`：用例存储规则
  - `output-template.md`：输出模板规范
  - `update-governance.md`：更新治理规则
  - `module-index.json`：模块索引
- `docs/glossary.md`：术语词典（20+ 术语）
- `docs/contributing.md`：贡献指南
- `docs/troubleshooting.md`：故障排查指南

#### 配置与依赖
- `test-case-generator/requirements.txt`：Python 依赖定义
  - openpyxl >= 3.1.0
  - pandas >= 2.0.0
  - jsonschema >= 4.17.0

---

### 修复

- 修复 README.md 中的绝对路径（从 `/Users/lrwei91/...` 改为相对路径）
- 修复 platform_scope 值标准化逻辑
  - 统一映射：平台→账服，后端→账服，大厅→客户端，运营活动→账服
- 修复测试用例 Excel 导出格式
  - 改用 `minimax-xlsx` 模板脚本
  - 确保包含"备注"列和优先级标签
- 修复 module-index.json 缺失"个人中心"模块定义

---

### 变更

- 索引结构从单索引拆分为双索引（testcase + i18n）
- 脚本路径统一为 `test-case-generator/scripts/`
- 产物目录结构标准化：
  - `testcases/generated/`：测试用例
  - `testcases/i18n/`：多语言 JSON

---

### 已验证

- [x] 双索引结构迁移完成
- [x] 多语言 JSON 校验脚本可正常工作
- [x] `upsert_testcase_index.py` 可同时处理 testcase 和 i18n JSON
- [x] 两份索引和多语言 JSON 的端到端验证通过
- [x] 10 个脚本的 README 文档完成
- [x] 快速入门文档完成

### v1.0.0 后续更新 (2026-04-07)

#### 文档优化
- 文档整合：合并分散的文档内容，提升可读性
- Office-Skills 移除：将相关脚本内化到主项目
- 补充世界杯竞猜活动冒烟测试用例
- QA 技能包优化：
  - 领域文档覆盖完善
  - 新增工具脚本支持
  - 文档去重整理

#### 版本发布
- 1.0.0 正式版本发布
- 文档持续更新与完善

---

## [计划中]

### v1.1.0

#### 新增
- CLI `--help` 支持：所有 10 个脚本使用 argparse 添加帮助信息
- `templates/` 目录：统一管理 Excel 和 JSON 模板
- `CHANGELOG.md`：版本变更日志（本文档）

#### 改进
- 单元测试覆盖：使用 pytest 为核心脚本编写测试（目标 60%+ 覆盖率）
- 模块 ID 对齐：将 `module_ids` 从目录级占位对齐到真实业务模块索引
- 增量生成脚本：从需求文本直接生成 i18n JSON 的执行脚本

#### 文档
- 补充 TROUBLESHOOTING.md 至 10+ 常见问题
- 为常见模块补一批真实的 `testcases/i18n/<模块>/<主题>.json`

---

## 版本说明

### 版本号规则

```
MAJOR.MINOR.PATCH
```

- **MAJOR** (1.x.x)：不兼容的变更
- **MINOR** (x.1.x)：向后兼容的功能新增
- **PATCH** (x.x.1)：向后兼容的问题修复

### 发布周期

- PATCH 版本：按需发布
- MINOR 版本：累积 3+ 个 PATCH 后发布
- MAJOR 版本：架构级变更时发布

---

## 贡献者

- Initial work: QA Team

---

## 链接

- [GitHub Repository](https://github.com/...)
- [技能包文档](test-case-generator/SKILL.md)
- [快速入门](user-guide.md)
- [贡献指南](contributing.md)
- [故障排查](troubleshooting.md)
