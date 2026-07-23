from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .identity import stable_plan_id, stable_task_id
from .models import AuthorityMode, ExecutionState, parse_execution_state


_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TITLE = re.compile(r"(?m)^#\s+(.+?)\s*$")
_TASK_HEADING = re.compile(
    r"(?m)^#{2,6}\s+(?P<id>TC-[A-Z0-9][A-Z0-9._-]*"
    r"(?:\s*(?:\.\.|â€”|â€“|to)\s*TC-[A-Z0-9][A-Z0-9._-]*)?)"
    r"(?:\s*[—–:-]\s*|\s+)(?P<title>.+?)\s*$",
    re.IGNORECASE,
)
_STATUS = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?status\s*:\s*(?:\*\*)?\s*([A-Z0-9 _-]+)"
)
_CHECKLIST = re.compile(r"(?m)^\s*[-*]\s+\[(?P<mark>[ xX])\]\s+(?P<title>.+?)\s*$")


@dataclass(slots=True)
class ParsedTask:
    external_id: str
    title: str
    state: ExecutionState
    warnings: list[str] = field(default_factory=list)
    created_at: str = "9999-12-31T23:59:59Z"


@dataclass(slots=True)
class ParsedPlan:
    plan_id: str
    title: str
    aliases: list[str]
    execution_state: ExecutionState
    authority_mode: AuthorityMode
    tasks: list[ParsedTask]
    metadata: dict[str, Any]
    warnings: list[str]
    content_sha256: str


def _metadata(text: str) -> dict[str, Any]:
    match = _FRONTMATTER.search(text)
    if not match:
        return {}
    value = yaml.safe_load(match.group(1)) or {}
    return value if isinstance(value, dict) else {}


def _status_in_block(block: str) -> tuple[ExecutionState, list[str]]:
    match = _STATUS.search(block)
    state, warning = parse_execution_state(match.group(1) if match else None)
    return state, [warning] if warning else []


def _expand_external_id(value: str) -> tuple[list[str], str | None]:
    cleaned = value.strip("`* ")
    match = re.fullmatch(
        r"(TC-[A-Z0-9][A-Z0-9._-]*?)(\d+)\s*(?:\.\.|â€”|â€“|to)\s*"
        r"(TC-[A-Z0-9][A-Z0-9._-]*?)(\d+)",
        cleaned,
        re.IGNORECASE,
    )
    if not match:
        return [cleaned.upper()], None
    left_prefix, left_number, right_prefix, right_number = match.groups()
    if left_prefix.upper() != right_prefix.upper():
        return [], f"PARSER_GAP:AMBIGUOUS_TASK_RANGE:{cleaned}"
    start, end = int(left_number), int(right_number)
    if end < start or end - start > 1000:
        return [], f"PARSER_GAP:INVALID_TASK_RANGE:{cleaned}"
    width = max(len(left_number), len(right_number))
    return [
        f"{left_prefix.upper()}{number:0{width}d}" for number in range(start, end + 1)
    ], None


def _table_tasks(text: str) -> tuple[list[ParsedTask], list[str]]:
    lines = text.splitlines()
    tasks: list[ParsedTask] = []
    warnings: list[str] = []
    for index in range(len(lines) - 1):
        header = [cell.strip().lower() for cell in lines[index].strip().strip("|").split("|")]
        divider = lines[index + 1].strip()
        looks_like_status_table = (
            "|" in lines[index]
            and any(cell in {"id", "task", "task id", "taskcard"} for cell in header)
            and any("status" in cell or cell == "state" for cell in header)
        )
        if not looks_like_status_table:
            continue
        if not re.fullmatch(r"\|?[\s:|-]+\|?", divider):
            warnings.append(f"PARSER_GAP:MALFORMED_STATUS_TABLE:line={index + 1}")
            continue
        id_index = next((i for i, cell in enumerate(header) if cell in {"id", "task", "task id", "taskcard"}), None)
        status_index = next((i for i, cell in enumerate(header) if "status" in cell or cell == "state"), None)
        if id_index is None or status_index is None:
            continue
        title_index = next((i for i, cell in enumerate(header) if cell in {"title", "description", "task"} and i != id_index), None)
        row = index + 2
        while row < len(lines) and "|" in lines[row] and lines[row].strip():
            cells = [cell.strip() for cell in lines[row].strip().strip("|").split("|")]
            if len(cells) > max(id_index, status_index):
                external_id = cells[id_index].strip("`* ")
                if external_id:
                    state, warning = parse_execution_state(cells[status_index].strip("`* "))
                    title = cells[title_index] if title_index is not None and title_index < len(cells) else external_id
                    expanded, range_warning = _expand_external_id(external_id)
                    if range_warning:
                        warnings.append(range_warning)
                    for expanded_id in expanded:
                        tasks.append(ParsedTask(expanded_id, title, state, [warning] if warning else []))
                else:
                    warnings.append(f"PARSER_GAP:MISSING_TASK_ID:line={row + 1}")
            else:
                warnings.append(f"PARSER_GAP:MALFORMED_STATUS_ROW:line={row + 1}")
            row += 1
    return tasks, warnings


def parse_plan(path: Path, *, repository_id: str = "format-factory") -> ParsedPlan:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata = _metadata(text)
    title_match = _TITLE.search(text)
    title = str(metadata.get("title") or (title_match.group(1) if title_match else path.stem))
    aliases = [
        str(value)
        for key in ("plan_identity", "artifact_id", "mission_id", "plan_id")
        if (value := metadata.get(key))
    ]
    tasks: list[ParsedTask] = []
    matches = list(_TASK_HEADING.finditer(text))
    created_at = str(
        metadata.get("created_at")
        or metadata.get("generated_at")
        or metadata.get("created")
        or "9999-12-31T23:59:59Z"
    )
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        state, task_warnings = _status_in_block(text[match.end():end])
        expanded, range_warning = _expand_external_id(match.group("id"))
        if range_warning:
            task_warnings.append(range_warning)
        tasks.extend(
            ParsedTask(
                external_id,
                match.group("title").strip(),
                state,
                task_warnings.copy(),
                created_at,
            )
            for external_id in expanded
        )
    table_tasks, table_warnings = _table_tasks(text)
    tasks.extend(table_tasks)
    for match in _CHECKLIST.finditer(text):
        title_value = match.group("title").strip()
        explicit = re.match(r"(TC-[A-Z0-9][A-Z0-9._-]*)\b", title_value, re.IGNORECASE)
        external_id = explicit.group(1).upper() if explicit else "CHK-" + hashlib.sha256(title_value.encode()).hexdigest()[:12].upper()
        state = ExecutionState.COMPLETE if match.group("mark").lower() == "x" else ExecutionState.READY
        tasks.append(ParsedTask(external_id, title_value, state))
    deduplicated: dict[str, ParsedTask] = {}
    warnings: list[str] = list(table_warnings)
    for task in tasks:
        if task.external_id in deduplicated:
            existing = deduplicated[task.external_id]
            if existing.state != task.state:
                existing.warnings.append(f"CONTRADICTORY_TASK_STATE:{task.state.value}")
                existing.state = ExecutionState.BLOCKED
            continue
        deduplicated[task.external_id] = task
        warnings.extend(task.warnings)
    plan_state, warning = parse_execution_state(str(metadata.get("status") or ""))
    if warning:
        warnings.append(warning)
    mode_raw = str(metadata.get("authority_mode") or ("CANONICAL" if path.name == "master-plan.md" else "CHILD")).upper()
    try:
        authority = AuthorityMode(mode_raw)
    except ValueError:
        authority = AuthorityMode.CHILD
        warnings.append(f"UNKNOWN_AUTHORITY_MODE:{mode_raw}")
    plan_id = stable_plan_id(
        repository_id=repository_id,
        aliases=aliases,
        title=title,
        task_ids=deduplicated,
        content=text,
    )
    return ParsedPlan(
        plan_id=plan_id,
        title=title,
        aliases=sorted(set(aliases)),
        execution_state=plan_state,
        authority_mode=authority,
        tasks=list(deduplicated.values()),
        metadata=metadata,
        warnings=sorted(set(warnings)),
        content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def materialize_task(plan_id: str, parsed: ParsedTask, source_path: str) -> dict[str, Any]:
    return {
        "task_id": stable_task_id(plan_id, parsed.external_id, parsed.title),
        "plan_id": plan_id,
        "external_id": parsed.external_id,
        "title": parsed.title,
        "state": parsed.state.value,
        "dependencies": [],
        "severity": "MEDIUM",
        "created_at": parsed.created_at,
        "retry_count": 0,
        "retry_history": [],
        "retry_not_before": None,
        "external_blocker": False,
        "evidence": [],
        "source_kind": "plan",
        "source_path": source_path,
        "disposition": None,
        "warnings": parsed.warnings,
    }
