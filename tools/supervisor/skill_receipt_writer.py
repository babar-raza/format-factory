"""TC-SGOV-W2-005: Skill execution receipt auto-write (EP-004).

Writes receipts to .local/skill-execution-receipts/ for each declared skill ID
in a processed evidence declaration. Called by autonomous_cycle.run_cycle() after
write_outputs(). Best-effort, non-blocking. Receipts are consumed by V-SGF-002.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def write_skill_receipts(
    decl: dict,
    run_id: str,
    declaration_path: Path,
    verdict: str,
    repo_root: Path,
) -> set[str]:
    """Write one receipt file per declared skill ID.

    Returns the set of skill_ids for which receipts were written.
    """
    receipts_dir = repo_root / ".local" / "skill-execution-receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    written: set[str] = set()
    ts = datetime.now(timezone.utc).isoformat()
    for wi in decl.get("planned_work_items", []):
        sids: list[str] = []
        sid_val = wi.get("skill_id") or wi.get("fallback_skill_id")
        if sid_val:
            sids.append(str(sid_val))
        dsids = wi.get("declared_skill_ids")
        if isinstance(dsids, list):
            sids.extend(str(s) for s in dsids if s)
        elif isinstance(dsids, str) and dsids:
            sids.append(dsids)
        for sid in sids:
            if sid in written:
                continue
            written.add(sid)
            rp = receipts_dir / f"{sid}-{run_id}.yaml"
            rp.write_text(
                f"skill_id: {sid}\n"
                f"run_id: {run_id}\n"
                f"declaration_path: {str(declaration_path)}\n"
                f"verdict: {verdict}\n"
                f"written_at: {ts}\n",
                encoding="utf-8",
            )
    return written
