"""
QA Workflow - LangGraph 状态图

构建 QA 测试用例生成工作流的状态图。
支持：generate（生成）、augment（补充）、analyze（分析）工作流。
"""

from langgraph.graph import StateGraph, END

from .qa_state import QAWorkflowState


def build_qa_workflow() -> StateGraph:
    """
    构建 QA 测试用例生成工作流

    流程：
    1. parse_input: 解析输入内容
    2. [条件分支] 是否需要读取 Figma?
    3. [条件分支] 是否包含多语言？
    4. export_excel → END
    """
    from .qa_nodes import (
        parse_input, read_figma, generate_test_cases,
        check_i18n, export_excel, should_read_figma, has_i18n,
    )

    workflow = StateGraph(QAWorkflowState)

    workflow.add_node("parse_input", parse_input)
    workflow.add_node("read_figma", read_figma)
    workflow.add_node("generate_test_cases", generate_test_cases)
    workflow.add_node("check_i18n", check_i18n)
    workflow.add_node("export_excel", export_excel)

    workflow.set_entry_point("parse_input")

    workflow.add_conditional_edges(
        "parse_input",
        should_read_figma,
        {True: "read_figma", False: "generate_test_cases"}
    )

    workflow.add_edge("read_figma", "generate_test_cases")

    workflow.add_conditional_edges(
        "generate_test_cases",
        has_i18n,
        {True: "check_i18n", False: "export_excel"}
    )

    workflow.add_edge("check_i18n", "export_excel")
    workflow.add_edge("export_excel", END)

    return workflow.compile()


def build_augment_workflow() -> StateGraph:
    """
    构建补充已有用例工作流

    流程：
    1. load_existing_cases → 2. analyze_gaps → 3. generate_augment_cases → 4. append_to_excel → END
    """
    from .qa_nodes import (
        load_existing_cases, analyze_gaps,
        generate_augment_cases, append_to_excel
    )

    workflow = StateGraph(QAWorkflowState)

    workflow.add_node("load_existing_cases", load_existing_cases)
    workflow.add_node("analyze_gaps", analyze_gaps)
    workflow.add_node("generate_augment_cases", generate_augment_cases)
    workflow.add_node("append_to_excel", append_to_excel)

    workflow.set_entry_point("load_existing_cases")
    workflow.add_edge("load_existing_cases", "analyze_gaps")
    workflow.add_edge("analyze_gaps", "generate_augment_cases")
    workflow.add_edge("generate_augment_cases", "append_to_excel")
    workflow.add_edge("append_to_excel", END)

    return workflow.compile()


def build_analyze_workflow() -> StateGraph:
    """
    构建仅分析需求工作流

    流程：
    1. parse_input → 2. analyze_requirements → 3. output_analysis → END
    """
    from .qa_nodes import parse_input, analyze_requirements, output_analysis

    workflow = StateGraph(QAWorkflowState)

    workflow.add_node("parse_input", parse_input)
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("output_analysis", output_analysis)

    workflow.set_entry_point("parse_input")
    workflow.add_edge("parse_input", "analyze_requirements")
    workflow.add_edge("analyze_requirements", "output_analysis")
    workflow.add_edge("output_analysis", END)

    return workflow.compile()
