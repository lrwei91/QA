"""
QA Workflows - 工具函数

提供：
- 节点重试机制
- 并行执行辅助函数
"""

import asyncio
from functools import wraps
from typing import Callable, Any

from .qa_state import QAWorkflowState


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """
    重试机制装饰器

    用法:
        @with_retry(max_retries=3, delay=1.0)
        def my_node(state: QAWorkflowState) -> QAWorkflowState:
            ...

    参数:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    """
    def decorator(node_func: Callable) -> Callable:
        @wraps(node_func)
        def wrapper(state: QAWorkflowState) -> QAWorkflowState:
            errors = state.get("errors", [])
            retry_count = state.get("retry_count", 0)

            for attempt in range(max_retries):
                try:
                    result = node_func(state)
                    # 成功，清除重试相关状态
                    if "_last_error" in result:
                        del result["_last_error"]
                    return result

                except Exception as e:
                    if attempt == max_retries - 1:
                        # 最后一次尝试失败
                        errors.append(f"{node_func.__name__} failed after {max_retries} attempts: {str(e)}")
                        return {**state, "errors": errors, "retry_count": retry_count}
                    else:
                        # 等待后重试
                        import time
                        time.sleep(delay)
                        retry_count += 1
                        state = {**state, "retry_count": retry_count, "_last_error": str(e)}

            return {**state, "errors": errors, "retry_count": retry_count}

        return wrapper
    return decorator


async def run_nodes_parallel(
    state: QAWorkflowState,
    *node_funcs: Callable[[QAWorkflowState], QAWorkflowState]
) -> QAWorkflowState:
    """
    并行执行多个节点函数

    用法:
        result = await run_nodes_parallel(state, parse_axure, read_figma)

    注意: 节点函数必须是异步的或可以快速同步执行
    对于 IO 密集型任务（API 调用），建议使用 asyncio.create_task
    """
    async def run_node(node_func: Callable) -> tuple[str, QAWorkflowState]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: node_func(state))
        return (node_func.__name__, result)

    tasks = [run_node(func) for func in node_funcs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 合并结果
    merged_state = {**state}
    for result in results:
        if isinstance(result, Exception):
            merged_state.setdefault("errors", []).append(str(result))
        elif isinstance(result, tuple):
            _, node_result = result
            for key, value in node_result.items():
                if key == "errors":
                    merged_state.setdefault("errors", []).extend(value)
                elif key not in merged_state:
                    merged_state[key] = value

    return merged_state


def run_async(func: Callable, *args, **kwargs) -> Any:
    """
    在同步代码中运行异步函数

    用法:
        result = run_async(run_nodes_parallel, state, func1, func2)
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 在已有事件循环中运行
            future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop)
            return future.result()
        else:
            return loop.run_until_complete(func(*args, **kwargs))
    except RuntimeError:
        # 没有事件循环，创建新的
        return asyncio.run(func(*args, **kwargs))


class ParallelExecutor:
    """
    并行执行器

    用法:
        executor = ParallelExecutor()
        executor.add_task(parse_axure, axure_dir)
        executor.add_task(read_figma, figma_url)
        results = executor.run()
    """

    def __init__(self):
        self.tasks = []

    def add_task(self, func: Callable, *args, **kwargs) -> 'ParallelExecutor':
        """添加任务"""
        self.tasks.append((func, args, kwargs))
        return self

    def run(self, initial_state: QAWorkflowState) -> QAWorkflowState:
        """执行所有任务并合并结果"""
        async def _run():
            async def run_single(func: Callable, args: tuple, kwargs: dict) -> tuple:
                loop = asyncio.get_event_loop()
                func_with_args = lambda: func(initial_state, *args, **kwargs)
                result = await loop.run_in_executor(None, func_with_args)
                return (func.__name__, result)

            tasks = [run_single(func, args, kwargs) for func, args, kwargs in self.tasks]
            return await asyncio.gather(*tasks, return_exceptions=True)

        results = run_async(_run)

        # 合并结果
        merged_state = {**initial_state}
        for result in results:
            if isinstance(result, Exception):
                merged_state.setdefault("errors", []).append(str(result))
            elif isinstance(result, tuple):
                _, node_result = result
                for key, value in node_result.items():
                    if key == "errors":
                        merged_state.setdefault("errors", []).extend(value)
                    elif key not in merged_state:
                        merged_state[key] = value

        return merged_state
