"""Helpers to execute the CrewAI workflow from the Django backend."""

from __future__ import annotations

import json
import os
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
CREW_SRC_PATH = REPO_ROOT / "crewai_project" / "src"
REPORT_PATH = CREW_SRC_PATH / "latest_ai_development" / "report.md"
CREW_ENV_PATHS = [
    REPO_ROOT / ".env",
    REPO_ROOT / "crewai_project" / ".env",
]

_crew_module_error: Optional[str] = None

if str(CREW_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(CREW_SRC_PATH))


def _load_env_file(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to read env file %s: %s", path, exc)
        return

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


for env_path in CREW_ENV_PATHS:
    _load_env_file(env_path)

try:
    from latest_ai_development.crew import LatestAiDevelopment
except Exception as exc:  # pragma: no cover
    _crew_module_error = f"Failed to import CrewAI project: {exc}"
    LatestAiDevelopment = None  # type: ignore


@dataclass
class CrewAIProgress:
    """Progress information for CrewAI execution."""
    stage: str
    progress: float
    message: str
    task_name: Optional[str] = None
    task_status: Optional[str] = None

@dataclass
class CrewAIResult:
    """Structured result returned by CrewAI analysis."""
    summary: Optional[str]
    report_markdown: Optional[str]
    report_path: Optional[str]
    task_outputs: Optional[Dict[str, Any]]
    progress_history: Optional[List[CrewAIProgress]] = None


class CrewAIExecutionError(RuntimeError):
    """Raised when CrewAI cannot be executed successfully."""


def run_crewai_analysis(data_path: Path, progress_callback=None) -> CrewAIResult:
    """
    Trigger the CrewAI workflow using the JSON payload stored at `data_path`.

    Args:
        data_path: Path to the JSON file containing survey data
        progress_callback: Optional callback function to report progress
    
    Returns:
        A structured `CrewAIResult` containing the main summary, optional
        markdown report content, and per-task outputs when available.
    """
    if _crew_module_error:
        logger.error(_crew_module_error)
        raise CrewAIExecutionError(_crew_module_error)

    if LatestAiDevelopment is None:  # pragma: no cover
        raise CrewAIExecutionError("CrewAI project is unavailable.")

    # 进度历史记录
    progress_history = []
    
    def report_progress(stage, progress, message, task_name=None, task_status=None):
        progress_info = CrewAIProgress(
            stage=stage,
            progress=progress,
            message=message,
            task_name=task_name,
            task_status=task_status
        )
        progress_history.append(progress_info)
        if progress_callback:
            try:
                progress_callback(progress_info)
            except Exception as exc:
                logger.warning(f"Failed to call progress callback: {exc}")
        logger.info(f"Progress: {progress*100:.1f}% - {message}")

    report_progress("initialization", 0.0, "开始初始化CrewAI工作流")

    try:
        with data_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as exc:
        raise CrewAIExecutionError(f"Unable to load survey data: {exc}") from exc

    report_progress("initialization", 0.1, "成功加载用户数据")
    inputs = {"data": payload}

    try:
        report_progress("initialization", 0.2, "正在创建CrewAI团队")
        crew = LatestAiDevelopment().crew()
        report_progress("initialization", 0.3, "团队创建完成，开始执行工作流")
        
        # 直接执行工作流，不再尝试替换方法
        report_progress("execution", 0.4, "开始执行数据合规审查任务")
        
        # 尝试不同的执行方法，适配不同版本的CrewAI
        try:
            # 尝试直接调用crew对象（较新版本的CrewAI）
            result = crew(inputs=inputs)
        except (TypeError, AttributeError):
            # 如果失败，尝试查找其他可能的执行方法
            try:
                # 尝试使用kickoff方法
                if hasattr(crew, "kickoff"):
                    result = crew.kickoff(inputs=inputs)
                # 尝试使用其他可能的执行方法
                elif hasattr(crew, "execute"):
                    result = crew.execute(inputs=inputs)
                else:
                    raise AttributeError("Crew对象没有可用的执行方法")
            except Exception as inner_exc:
                logger.error(f"无法执行CrewAI工作流: {inner_exc}")
                raise CrewAIExecutionError(f"无法执行CrewAI工作流: {inner_exc}") from inner_exc
        
        # 检查是否有任务输出可以用来报告进度
        if hasattr(result, "tasks_output") and result.tasks_output:
            total_tasks = len(result.tasks_output)
            for i, task_output in enumerate(result.tasks_output):
                task_progress = 0.4 + 0.5 * (i + 1) / total_tasks
                task_name = getattr(task_output, "task_name", "未知任务")
                task_status = getattr(task_output, "status", "未知状态")
                report_progress(
                    "execution", 
                    task_progress, 
                    f"任务 {i+1}/{total_tasks} 完成",
                    task_name=task_name,
                    task_status=task_status
                )
        
        report_progress("execution", 0.9, "所有任务执行完成，开始生成最终报告")
        
        report_progress("execution", 1.0, "CrewAI工作流执行完成")
        
    except Exception as exc:
        logger.exception("CrewAI execution failed")
        report_progress("error", 1.0, f"执行失败: {str(exc)}", task_status="error")
        raise CrewAIExecutionError(f"CrewAI execution failed: {exc}") from exc

    summary: Optional[str] = None
    task_outputs: list[Dict[str, Any]] | None = None

    if hasattr(result, "final_output"):
        summary = getattr(result, "final_output")
    elif hasattr(result, "raw"):
        summary = getattr(result, "raw")

    if summary is not None and not isinstance(summary, str):
        summary = str(summary)

    # Collect task outputs when available to aid debugging/show richer detail.
    raw_tasks = getattr(result, "tasks_output", None)
    if raw_tasks:
        serialized: list[Dict[str, Any]] = []
        for item in raw_tasks:
            if isinstance(item, dict):
                serialized.append(item)
                continue

            item_dict: Dict[str, Any] = {}
            for attr in ("task_name", "agent", "description", "output", "status"):
                if hasattr(item, attr):
                    value = getattr(item, attr)
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        item_dict[attr] = value
                    else:
                        item_dict[attr] = str(value)
            if item_dict:
                serialized.append(item_dict)
        if serialized:
            task_outputs = serialized

    report_markdown: Optional[str] = None
    report_path: Optional[str] = None

    if REPORT_PATH.exists():
        report_path = str(REPORT_PATH)
        try:
            report_markdown = REPORT_PATH.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to read CrewAI report markdown: %s", exc)

    return CrewAIResult(
        summary=summary,
        report_markdown=report_markdown,
        report_path=report_path,
        task_outputs=task_outputs,
        progress_history=progress_history
    )
