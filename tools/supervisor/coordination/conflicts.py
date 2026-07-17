"""Structured conflict records (TC-COORD-005).

A conflict is actionable evidence, not a log line: resource, both parties,
fingerprints, the attempted operation and the safe next action. Conflicts
must reach ACKNOWLEDGED/RESOLVED -- `status` exits non-zero while any are
OPEN, and validator V195 fails a sprint carrying unexplained open conflicts.

TC-STRUCT-003 (2026-07-17, FOUND-ISSUE-OWNERSHIP-ENFORCEMENT-2026-07-17):
`resolve(state="RESOLVED", ...)` used to accept a free-text note with zero
verification that remediation actually happened -- the note "I fixed it" and
the note "asserting this closes it with nothing behind that claim" were
equally accepted. This session used `resolve --state RESOLVED` correctly and
safely ~6 times for genuine own-session baseline mismatches, but the
*mechanism itself* could not distinguish that legitimate case from someone
typing a justification for a genuinely unaddressed problem -- the path of
least resistance was always available and never technically contradicted.
`RESOLVED` now requires `--evidence` pointing at one of: a real git commit
(verified against this repo's object store, not merely well-formatted), a
`found-issue-register.yaml` entry with an allowlisted disposition (reuses
governance_validators_found_issue.OWNERSHIP_VALID_DISPOSITIONS -- the same
allowlist TC-STRUCT-002 fixed), or the literal `same-session-rebaseline`
class -- itself verified against the write_journal (the resolving agent must
actually be the resource's own most recent writer), not merely asserted.
`ACKNOWLEDGED`/`WONT_FIX` remain lower-friction but must carry a real,
non-generic reason (reuses the forbidden-reason pattern shipped this session
in .hooks/pre-commit-skill-guard for the same underlying problem: a note
that carries no actual information should not count as a note).
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .db import NowFn, connect, default_now, emit_event, immediate
from .ids import new_conflict_id
from .root import resolve_coordination_root

_FORBIDDEN_GENERIC_REASONS = frozenset({
    "resolved", "done", "fixed", "ok", "okay", "n/a", "na", "handled",
    "sorted", "fine", "no issue", "no_issue", "closed", "complete", "yes",
})
_FI_ID_RE = re.compile(r"^FI-\d+$")
_GIT_HASH_RE = re.compile(r"^[0-9a-f]{7,40}$")


class ConflictLog:
    def __init__(self, root: Path | None = None, now_fn: NowFn = default_now):
        self.root = root or resolve_coordination_root()
        self.now_fn = now_fn

    def record(self, conn: sqlite3.Connection, *, resource_key: str,
               resource_display: str, detected_by: str, conflict_type: str,
               safe_action: str, apparent_owner: str | None = None,
               related_tasks: list[str] | None = None,
               baseline_sha256: str | None = None,
               current_sha256: str | None = None,
               attempted_op: str | None = None,
               classification: str | None = None) -> str:
        """Insert a conflict row (caller holds the transaction). Dedupes on an
        identical OPEN conflict for the same resource/type/detector."""
        existing = conn.execute(
            "SELECT conflict_id FROM conflicts WHERE resource_key=? AND"
            " conflict_type=? AND detected_by=? AND resolution_state='OPEN'",
            (resource_key, conflict_type, detected_by)).fetchone()
        if existing is not None:
            return existing["conflict_id"]
        cid = new_conflict_id()
        conn.execute(
            "INSERT INTO conflicts(conflict_id, resource_key,"
            " resource_display, detected_by, apparent_owner, related_tasks,"
            " conflict_type, baseline_sha256, current_sha256, attempted_op,"
            " classification, safe_action, detected_at)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cid, resource_key, resource_display, detected_by, apparent_owner,
             json.dumps(related_tasks or []), conflict_type, baseline_sha256,
             current_sha256, attempted_op, classification, safe_action,
             self.now_fn()))
        emit_event(conn, "conflict", cid, "CONFLICT_RECORDED",
                   to_status="OPEN", actor=detected_by,
                   detail={"resource": resource_key, "type": conflict_type},
                   now_fn=self.now_fn)
        return cid

    def list_conflicts(self, open_only: bool = True) -> list[dict]:
        conn = connect(self.root)
        try:
            sql = "SELECT * FROM conflicts"
            if open_only:
                sql += " WHERE resolution_state='OPEN'"
            sql += " ORDER BY detected_at"
            return [dict(r) for r in conn.execute(sql).fetchall()]
        finally:
            conn.close()

    def open_count(self, conn: sqlite3.Connection | None = None) -> int:
        own = conn is None
        if own:
            conn = connect(self.root)
        try:
            return conn.execute(
                "SELECT COUNT(*) AS n FROM conflicts WHERE"
                " resolution_state='OPEN'").fetchone()["n"]
        finally:
            if own:
                conn.close()

    def _verify_evidence(self, conn: sqlite3.Connection, evidence: str,
                          resolved_by: str, resource_key: str) -> str | None:
        """Return None if `evidence` is verified valid for a RESOLVED
        transition; otherwise a human-readable reason it was rejected."""
        evidence = (evidence or "").strip()
        if not evidence:
            return ("RESOLVED requires --evidence: a git commit hash, a "
                    "found-issue-register FI-NNN id, or "
                    "'same-session-rebaseline'")

        if evidence == "same-session-rebaseline":
            row = conn.execute(
                "SELECT agent_id FROM write_journal WHERE file_key=?"
                " ORDER BY entry_id DESC LIMIT 1", (resource_key,)).fetchone()
            if row is None:
                return ("'same-session-rebaseline' claimed but no "
                        f"write_journal entry exists for {resource_key!r} "
                        "to verify against")
            if row["agent_id"] != resolved_by:
                return ("'same-session-rebaseline' claimed but the resource's "
                        f"most recent writer ({row['agent_id']!r}) does not "
                        f"match the resolving agent ({resolved_by!r})")
            return None

        if _FI_ID_RE.match(evidence):
            try:
                import yaml  # noqa: PLC0415
                reg_path = self.root_repo_path() / "registry" / "found-issue-register.yaml"
                data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
                issues = {i.get("issue_id"): i for i in (data or {}).get("issues", [])}
            except Exception as exc:
                return f"could not read found-issue-register.yaml to verify {evidence}: {exc}"
            issue = issues.get(evidence)
            if issue is None:
                return f"found-issue-register.yaml has no entry {evidence}"
            try:
                import sys as _sys_gvfi  # noqa: PLC0415
                _sup_dir = Path(__file__).resolve().parent.parent
                if str(_sup_dir) not in _sys_gvfi.path:
                    _sys_gvfi.path.insert(0, str(_sup_dir))
                from governance_validators_found_issue import OWNERSHIP_VALID_DISPOSITIONS  # noqa: PLC0415
            except Exception:
                OWNERSHIP_VALID_DISPOSITIONS = frozenset()  # noqa: N806
            disp = str(issue.get("disposition") or "").lower()
            if disp not in {d.lower() for d in OWNERSHIP_VALID_DISPOSITIONS}:
                return (f"{evidence} exists but its disposition {issue.get('disposition')!r} "
                        "is not one of the 6 allowlisted ownership dispositions")
            return None

        if _GIT_HASH_RE.match(evidence):
            import subprocess  # noqa: PLC0415
            try:
                result = subprocess.run(
                    ["git", "cat-file", "-e", evidence + "^{commit}"],
                    cwd=str(self.root_repo_path()), capture_output=True, timeout=10)
            except Exception as exc:
                return f"could not verify git commit {evidence}: {exc}"
            if result.returncode != 0:
                return f"{evidence} does not resolve to a real commit in this repo"
            return None

        return (f"evidence {evidence!r} is not a recognized commit hash, "
                "FI-NNN id, or 'same-session-rebaseline'")

    def root_repo_path(self) -> Path:
        """The actual git repo root -- distinct from self.root (the
        coordination state directory, which may live under AppData)."""
        try:
            from .root import find_git_entry
            git_dir = find_git_entry(Path.cwd())
            if git_dir is not None:
                return git_dir.parent
        except Exception:
            pass
        return Path.cwd()

    def resolve(self, conflict_id: str, resolved_by: str, state: str,
                note: str, evidence: str | None = None) -> None:
        if state not in ("ACKNOWLEDGED", "RESOLVED", "WONT_FIX"):
            raise ValueError(f"invalid resolution state: {state}")
        if not note or not note.strip():
            raise ValueError("a non-empty resolution note is required")
        if state != "RESOLVED" and note.strip().lower() in _FORBIDDEN_GENERIC_REASONS:
            raise ValueError(
                f"note {note!r} is too generic for {state} -- give a real, "
                "specific reason (what was checked, why this is safe to "
                "leave as-is)")
        conn = connect(self.root)
        try:
            with immediate(conn):
                row = conn.execute(
                    "SELECT resolution_state, resource_key FROM conflicts"
                    " WHERE conflict_id=?", (conflict_id,)).fetchone()
                if row is None:
                    raise ValueError(f"no such conflict: {conflict_id}")
                if state == "RESOLVED":
                    rejection = self._verify_evidence(
                        conn, evidence or "", resolved_by, row["resource_key"])
                    if rejection is not None:
                        raise ValueError(f"evidence verification failed: {rejection}")
                conn.execute(
                    "UPDATE conflicts SET resolution_state=?, resolved_by=?,"
                    " resolution_note=?, resolved_at=? WHERE conflict_id=?",
                    (state, resolved_by, note.strip(), self.now_fn(),
                     conflict_id))
                detail = {"note": note.strip()}
                if evidence:
                    detail["evidence"] = evidence
                emit_event(conn, "conflict", conflict_id, "CONFLICT_" + state,
                           from_status=row["resolution_state"], to_status=state,
                           actor=resolved_by, detail=detail,
                           now_fn=self.now_fn)
        finally:
            conn.close()
