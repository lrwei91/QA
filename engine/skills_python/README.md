# Skills Python - 实验性 Python 实现

## 目录定位

**Experimental Python implementations for future migration. Current production flow still relies on SKILL.md orchestration.**

本目录包含测试用例相关技能的 Python 函数实现，是**实验性代码**，用于探索将 SKILL.md 文档化的能力迁移到纯 Python 实现的可能性。

## 当前状态

| 文件 | 实现内容 | 状态 |
|------|----------|------|
| `__init__.py` | 包导出 | ✅ 完成 |
| `testcase_generate.py` | 测试用例生成函数 | 🧪 实验中 |
| `testcase_format.py` | Excel 导出与索引更新 | 🧪 实验中 |
| `figma_reader.py` | Figma 设计稿读取 | 🧪 实验中 |

## 与生产流程的关系

```
当前生产流程：
/qa → SKILL.md 文档 → Claude 执行 → Python 脚本

未来可能流程（实验方向）：
/qa → skills_python 函数 → Claude/本地执行 → Python 脚本
```

## 为什么需要这个目录？

1. **代码复用**：将分散在 `qa_nodes.py`、`scripts/` 中的逻辑统一组织
2. **可测试性**：Python 函数比 SKILL.md 文档更容易编写单元测试
3. **类型安全**：使用 TypedDict 等类型系统减少运行时错误
4. **未来迁移**：如果项目需要脱离 Claude Code 独立运行，这里是迁移目标

## 使用示例

```python
from skills_python import generate_test_cases

cases = generate_test_cases(
    requirement="用户登录功能...",
    case_type="smoke"
)
```

## 注意事项

⚠️ **当前生产流程仍使用 SKILL.md + Claude 执行**，本目录的代码仅供实验和参考。

如需修改核心逻辑，请优先修改：
- `engine/skills/*/SKILL.md` - 能力定义
- `engine/workflows/qa_nodes.py` - 工作流节点
