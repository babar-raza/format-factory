"""Composite view functions for the control index.

TC-OCRD-C5-02: Provides multi-table join views that combine control layer,
trust registry, sprint, and gap data into action-oriented context dicts.
All views check trust_registry for trust_warnings.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def _trust_warnings(conn: sqlite3.Connection, *paths: str) -> list[str]:
    """Return trust warnings for the given artifact paths."""
    warnings: list[str] = []
    for path in paths:
        row = conn.execute(
            "SELECT authority_level, trusted, reason FROM trust_registry WHERE artifact_path = ?",
            (path,),
        ).fetchone()
        if row and not row["trusted"]:
            warnings.append(
                f"UNTRUSTED: {path} (authority={row['authority_level']}, reason={row['reason']})"
            )
    return warnings


def get_task_context(conn: sqlite3.Connection, task_id: str) -> dict:
    """Return context for a specific task ID: plan, layer, gaps, evidence, trust warnings.

    Args:
        conn: Open SQLite connection.
        task_id: TC-* identifier to look up.

    Returns:
        Dict with plan, sprint_evidence, linked_gaps, and trust_warnings.
    """
    # Find plan containing the task_id
    plan_row = conn.execute(
        "SELECT plan_id, plan_path, plan_type, status FROM plans WHERE plan_id LIKE ?",
        (f"%{task_id}%",),
    ).fetchone()

    # Find sprint work items referencing this task
    work_items = conn.execute(
        "SELECT swi.item_id, swi.title, swi.status, s.sprint_id, s.verdict "
        "FROM sprint_work_items swi "
        "LEFT JOIN sprints s ON swi.sprint_id = s.sprint_id "
        "WHERE swi.item_id = ? OR swi.title LIKE ? "
        "ORDER BY s.start_time DESC LIMIT 5",
        (task_id, f"%{task_id}%"),
    ).fetchall()

    # Find linked gaps
    gaps = conn.execute(
        "SELECT gap_id, format, capability_name, status FROM gaps "
        "WHERE gap_id LIKE ? LIMIT 10",
        (f"%{task_id}%",),
    ).fetchall()

    artifact_paths = []
    if plan_row:
        artifact_paths.append(plan_row["plan_path"])

    return {
        "task_id": task_id,
        "plan": dict(plan_row) if plan_row else None,
        "sprint_evidence": [dict(r) for r in work_items],
        "linked_gaps": [dict(r) for r in gaps],
        "trust_warnings": _trust_warnings(conn, *artifact_paths),
    }


def get_resume_context(conn: sqlite3.Connection, repo_root: Path | None = None) -> dict:
    """Return the current sprint resume context.

    Combines: latest sprint, continuation signal state, active plan lock,
    trust warnings for key state files.

    Args:
        conn: Open SQLite connection.
        repo_root: Optional repo root for reading signal files directly.

    Returns:
        Dict with latest_sprint, active_plan, contradiction_events, trust_warnings.
    """
    # Latest sprint
    latest_sprint = conn.execute(
        "SELECT sprint_id, verdict, test_count, fail_count, start_time "
        "FROM sprints ORDER BY start_time DESC LIMIT 1"
    ).fetchone()

    # Active plan lock
    active_plan = conn.execute(
        "SELECT lock_file, plan_path, status, session_id FROM plan_locks "
        "WHERE status = 'IN_PROGRESS' ORDER BY updated_at DESC LIMIT 1"
    ).fetchone()

    # Recent contradiction events
    contradictions = conn.execute(
        "SELECT timestamp, detail FROM events "
        "WHERE event_type = 'contradiction_detected' "
        "ORDER BY timestamp DESC LIMIT 5"
    ).fetchall()

    # Trust warnings for key artifacts
    key_paths = [
        "reports/supervisor/next-sprint.md",
        "reports/supervisor/session-resume.md",
        ".local/supervisor/continuation-signal.json",
    ]
    trust_warnings = _trust_warnings(conn, *key_paths)

    return {
        "latest_sprint": dict(latest_sprint) if latest_sprint else None,
        "active_plan": dict(active_plan) if active_plan else None,
        "contradiction_events": [dict(r) for r in contradictions],
        "trust_warnings": trust_warnings,
    }


def get_product_context(conn: sqlite3.Connection, format_id: str) -> dict:
    """Return product context for a format: format info, gaps, oracle evidence.

    Args:
        conn: Open SQLite connection.
        format_id: Format identifier (e.g., 'fods').

    Returns:
        Dict with format, open_gaps, recent_sprints, trust_warnings.
    """
    fmt_upper = format_id.upper()

    fmt_row = conn.execute(
        "SELECT format_id, display_name, family, spec_body FROM formats "
        "WHERE UPPER(format_id) = ?",
        (fmt_upper,),
    ).fetchone()

    open_gaps = conn.execute(
        "SELECT gap_id, capability_name, status, priority FROM gaps "
        "WHERE UPPER(format) = ? AND LOWER(status) = 'open' "
        "ORDER BY gap_id LIMIT 20",
        (fmt_upper,),
    ).fetchall()

    recent_sprints = conn.execute(
        "SELECT s.sprint_id, s.verdict, swi.item_id, swi.title, swi.status "
        "FROM sprint_work_items swi "
        "JOIN sprints s ON swi.sprint_id = s.sprint_id "
        "WHERE LOWER(swi.title) LIKE ? "
        "ORDER BY s.start_time DESC LIMIT 10",
        (f"%{format_id.lower()}%",),
    ).fetchall()

    artifact_paths = []
    if fmt_row:
        artifact_paths.append(f"src/python/{format_id}/{format_id}_file_analytics.py")

    return {
        "format_id": format_id,
        "format": dict(fmt_row) if fmt_row else None,
        "open_gaps": [dict(r) for r in open_gaps],
        "recent_sprints": [dict(r) for r in recent_sprints],
        "trust_warnings": _trust_warnings(conn, *artifact_paths),
    }


def get_control_feature_context(conn: sqlite3.Connection, feature_id: str) -> dict:
    """Return context for a specific control feature.

    Args:
        conn: Open SQLite connection.
        feature_id: Feature identifier (e.g., 'cif-001').

    Returns:
        Dict with feature, layer, consumers, parity_result, trust_warnings.
    """
    feature = conn.execute(
        "SELECT * FROM control_features WHERE feature_id = ?",
        (feature_id,),
    ).fetchone()

    layer = None
    if feature:
        layer = conn.execute(
            "SELECT layer_key, name, status FROM control_layers WHERE layer_key = ?",
            (feature["control_layer_key"],),
        ).fetchone()

    consumers = conn.execute(
        "SELECT consumer_id, consumer_type, consumer_path FROM control_feature_consumers "
        "WHERE feature_id = ?",
        (feature_id,),
    ).fetchall()

    parity = conn.execute(
        "SELECT reuse_strategy, parity_status, intentional_changes FROM feature_parity_results "
        "WHERE feature_id = ?",
        (feature_id,),
    ).fetchone()

    artifact_paths = [c["consumer_path"] for c in consumers if c["consumer_path"]]
    trust_warnings = _trust_warnings(conn, *artifact_paths)

    return {
        "feature_id": feature_id,
        "feature": dict(feature) if feature else None,
        "layer": dict(layer) if layer else None,
        "consumers": [dict(c) for c in consumers],
        "parity_result": dict(parity) if parity else None,
        "trust_warnings": trust_warnings,
    }
