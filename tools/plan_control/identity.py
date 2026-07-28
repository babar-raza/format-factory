from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable


_VOLATILE = re.compile(
    r"(?im)^\s*(?:\*\*)?(?:status|last updated|updated|generated_at|heartbeat)"
    r"(?:\*\*)?\s*:\s*.*$"
)


def normalize_alias(value: str) -> str:
    return re.sub(r"[^a-z0-9:._/-]+", "-", value.strip().lower()).strip("-")


def stable_plan_id(
    *,
    repository_id: str,
    aliases: Iterable[str],
    title: str,
    task_ids: Iterable[str],
    content: str,
) -> str:
    normalized_aliases = sorted({normalize_alias(item) for item in aliases if item})
    normalized_tasks = sorted({normalize_alias(item) for item in task_ids if item})
    if normalized_aliases:
        seed = f"alias:{normalized_aliases[0]}"
    elif normalized_tasks:
        seed = f"title-tasks:{normalize_alias(title)}:{'|'.join(normalized_tasks)}"
    else:
        stable_content = _VOLATILE.sub("", content)
        fingerprint = hashlib.sha256(stable_content.encode("utf-8")).hexdigest()
        seed = f"title-content:{normalize_alias(title)}:{fingerprint}"
    digest = hashlib.sha256(f"{repository_id}:{seed}".encode("utf-8")).hexdigest()
    return f"plan-v2-{digest[:24]}"


def stable_task_id(plan_id: str, external_id: str, title: str) -> str:
    seed = normalize_alias(external_id) or normalize_alias(title)
    digest = hashlib.sha256(f"{plan_id}:{seed}".encode("utf-8")).hexdigest()
    return f"task-v2-{digest[:24]}"
