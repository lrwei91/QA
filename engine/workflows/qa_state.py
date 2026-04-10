"""
QA Workflow - 状态定义

定义 QA 测试用例生成工作流的状态结构。
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal


class QAWorkflowState(TypedDict, total=False):
    """测试用例生成工作流状态"""

    # 输入阶段
    workflow_type: Literal["generate", "augment", "analyze", "i18n"]
    case_type: Literal["smoke", "full"]
    input_content: str
    input_source: Literal["text", "file", "url", "axure_dir"]
    figma_url: Optional[str]

    # 解析阶段
    axure_data: Optional[Dict[str, Any]]
    figma_data: Optional[Dict[str, Any]]

    # 生成阶段
    test_cases: Optional[List[Dict[str, Any]]]
    i18n_json: Optional[Dict[str, Any]]

    # 输出阶段
    excel_path: Optional[str]
    update_index: bool
    export_option: Literal["with_index", "excel_only"]

    # 错误处理
    errors: List[str]
    retry_count: int

    # 补充用例专用
    existing_file_path: Optional[str]
    existing_cases: Optional[List[Dict[str, Any]]]
    identified_gaps: Optional[List[str]]
    new_cases: Optional[List[Dict[str, Any]]]

    # 内部字段
    _i18n_detected: bool
    _prompt_for_claude: str
    _i18n_missing: List[str]
    _analysis_mode: bool
    _augment_mode: bool
    _analysis_result: Dict[str, Any]
    _gap_analysis: Dict[str, Any]
