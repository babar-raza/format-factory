"""closeout_skip_ledger.py — Machine-readable skip records for closeout failures.

TC-MA2-SKIP-001 (bubbly-dancing-pony, 2026-07-12)
Mission: BUBBLY-DANCING-PONY-MA2-001

When a closeout step in autonomous_cycle.py fails silently (best-effort),
call record_closeout_skip() to append a machine-readable record to the skip
ledger. The next sprint can read outstanding skips via load_outstanding_skips().

Ledger: .local/supervisor/closeout-skip-ledger.json
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SKIP_LEDGER_REL = ".local/supervisor/closeout-skip-ledger.json"
_SKIP_LEDGER_PATH = _REPO_ROOT / _SKIP_LEDGER_REL


def _load_ledger(ledger_path: Path) -> list[dict]:
    if not ledger_path.exists():
        return []
    try:
        return json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_ledger(ledger_path: Path, entries: list[dict]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(ledger_path) + ".tmp")
    tmp.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(ledger_path))


def record_closeout_skip(
    step_name: str,
    error: str,
    sprint_id: str = "",
    ledger_path: Path | None = None,
) -> None:
    """Append a skip record to the closeout skip ledger.

    Args:
        step_name: Identifier for the failed closeout step (e.g. "copy_cycle_summaries").
        error: The exception or error description.
        sprint_id: The sprint that was closing out when the failure occurred.
        ledger_path: Override ledger path (default: canonical).
    """
    lp = ledger_path or _SKIP_LEDGER_PATH
    entries = _load_ledger(lp)
    entries.append(
        {
            "step_name": step_name,
            "error": str(error)[:500],
            "sprint_id": sprint_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "resolved": False,
        }
    )
    _save_ledger(lp, entries)


def load_outstanding_skips(ledger_path: Path | None = None) -> list[dict]:
    """Return all unresolved skip records from the ledger.

    Args:
        ledger_path: Override ledger path (default: canonical).

    Returns:
        List of unresolved skip entries.
    """
    lp = ledger_path or _SKIP_LEDGER_PATH
    return [e for e in _load_ledger(lp) if not e.get("resolved", False)]


def resolve_skip(
    step_name: str,
    sprint_id: str = "",
    ledger_path: Path | None = None,
) -> int:
    """Mark skip records for step_name (and optionally sprint_id) as resolved.

    Args:
        step_name: The closeout step whose skip should be resolved.
        sprint_id: If given, only resolve skips for this sprint.
        ledger_path: Override ledger path (default: canonical).

    Returns:
        Number of entries marked resolved.
    """
    lp = ledger_path or _SKIP_LEDGER_PATH
    entries = _load_ledger(lp)
    resolved_count = 0
    for entry in entries:
        if entry.get("step_name") == step_name and not entry.get("resolved", False):
            if sprint_id and entry.get("sprint_id") != sprint_id:
                continue
            entry["resolved"] = True
            resolved_count += 1
    if resolved_count:
        _save_ledger(lp, entries)
    return resolved_count


def format_skips_for_session_resume(ledger_path: Path | None = None) -> str:
    """Return a markdown block summarizing outstanding skips for session-resume.md.

    Args:
        ledger_path: Override ledger path (default: canonical).

    Returns:
        Markdown string (empty if no outstanding skips).
    """
    outstanding = load_outstanding_skips(ledger_path)
    if not outstanding:
        return ""
    lines = [
        "## Outstanding Closeout Skips\n",
        f"**{len(outstanding)} unresolved closeout step failure(s):**\n",
    ]
    for skip in outstanding[-5:]:  # show at most 5 most recent
        lines.append(
            f"- `{skip['step_name']}` (sprint={skip.get('sprint_id', '?')}, "
            f"recorded={skip.get('recorded_at', '?')[:19]}): {skip.get('error', '')[:120]}\n"
        )
    return "".join(lines)
