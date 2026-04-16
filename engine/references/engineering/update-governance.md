---
# 用途：更新治理规则 - 定义生成模式与维护模式的边界，以及何时更新索引、模块文件和 skill 资源
---

# 更新治理规则

## 1. 两种运行模式

### 1.1 生成模式（默认）

默认只做下面四件事：

- 生成结构化测试用例
- 输出关联补充用例
- 给出 `索引增量建议`
- 给出 `模块文档增量建议`
- 若用户明确要求保存或导出，可写入工作区 `outputs/` 并更新 `outputs/testcase-index.json`

生成模式下不要直接改写 skill 文件。
工作区 `outputs/`、`outputs/testcase-index.json` 属于项目产物仓位，不属于 skill 资源文件。

### 1.2 维护模式（显式触发）

只有当用户明确说出以下意图时，才进入维护模式：

- 更新 skill
- 更新索引
- 修改模块文件
- 把新需求沉淀进 skill
- 重新打包 skill

## 2. 什么时候应该更新索引

出现以下情况时，应更新 `index-rules/module-index.json`：

1. 新需求暴露出新的模块或子模块
2. 现有模块缺少常用别名、触发词或核心功能
3. 缺少新的 `depends_on` 或 `impacted_modules`
4. 缺少前端/后端平台信号：`client_signals` 或 `server_signals`
5. 现有 `always_check` 无法覆盖新暴露的高风险维度

## 3. 什么时候应该更新领域文件

出现以下情况时，应更新对应领域文件：

1. 新需求带来新的业务规则、状态机或审批约束
2. 模块之间出现新的联动关系或回归清单
3. 平台表现（客户端或账服）新增明确规则
4. 旧说明过于笼统，已经无法支持高质量测试设计

## 4. 推荐更新顺序

1. 先更新 `index-rules/module-index.json`
2. 再更新对应领域文件
3. 必要时更新 `index-rules/system-map.md`
4. 若平台规则变化，再更新 `index-rules/platform-rules.md`
5. 若默认输出结构变化，再更新 `test-design/output-template.md`
6. 运行 `scripts/validate_index.py index-rules/module-index.json`
7. 打包 skill

## 5. 推荐变更清单输出格式

进入维护模式前，先给出变更清单：

- 要新增或修改的模块 id
- 要补充的别名 / 触发词 / 平台信号
- 要新增的联动关系
- 要更新的领域文件
- 预期影响的测试覆盖范围

## 6. 不要自动做的事情

- 不要在普通生成任务里偷偷修改资源文件
- 不要在用户没有要求保存、导出或纳入历史库时修改 `outputs/testcase-index.json`
- 不要为了追求完整而复制整套客户端/账服双份索引
- 不要把一次性需求细节直接写进索引，除非它已经具备可复用价值
