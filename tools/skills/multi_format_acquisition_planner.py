"""
multi_format_acquisition_planner.py -- Lane E (FORMAT-FACTORY-R10)

Deterministic multi-format acquisition planning POC.
Produces sequenced, governed acquisition plans for format groups.

SIMULATION ONLY — no source mutation, no Gate 11 approval, no real execution.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "no_internet_access": True,
    "plans_are_estimates_not_commitments": True,
    "unsupported_by_aspose_requires_audit": True,
}

# ---------------------------------------------------------------------------
# Group constants
# ---------------------------------------------------------------------------

GROUP_ACTIVE_FORMATS = "active_formats"
GROUP_KOREAN_WORD_PROCESSING = "korean_word_processing"
GROUP_ARCHIVE = "archive"
GROUP_DOCUMENT = "document"
GROUP_IMAGE = "image"

ALL_GROUP_NAMES = [
    GROUP_ACTIVE_FORMATS,
    GROUP_KOREAN_WORD_PROCESSING,
    GROUP_ARCHIVE,
    GROUP_DOCUMENT,
    GROUP_IMAGE,
]

# Predefined format groups (deterministic lists — order matters for sequencing)
FORMAT_GROUPS: dict[str, dict[str, Any]] = {
    GROUP_ACTIVE_FORMATS: {
        "description": "Currently active, evidence-ready formats (FODS + FODT)",
        "formats": ["fods", "fodt"],
        "lifecycle_state": "EVIDENCE_READY",
        "audit_state": "audited_supported",
        "spec_type": "full_public",
        "priority": 0,
        "parallelizable": True,
        "notes": "Both formats have Gates 1-10 PASSED; Gate 11 not approved.",
    },
    GROUP_KOREAN_WORD_PROCESSING: {
        "description": "Korean word-processing formats (HWP/HWPX/HWT)",
        "formats": ["hwpx", "hwp", "hwt"],
        "lifecycle_state": "CANDIDATE",
        "audit_state": "needs_audit",
        "spec_type": "mixed",  # hwpx=partial_public, hwp/hwt=reverse_engineering
        "priority": 1,
        "parallelizable": False,  # hwpx should be sequenced before hwp/hwt
        "notes": "hwpx has partial public spec; hwp and hwt require reverse-engineering.",
    },
    GROUP_ARCHIVE: {
        "description": "Archive format candidates (ALZ, EGG and others)",
        "formats": ["alz", "egg"],
        "lifecycle_state": "CANDIDATE",
        "audit_state": "needs_audit",
        "spec_type": "reverse_engineering",
        "priority": 2,
        "parallelizable": True,
        "notes": "Both proprietary archive formats; reverse engineering required.",
    },
    GROUP_DOCUMENT: {
        "description": "Open document format candidates (ABW, Gnumeric)",
        "formats": ["abw", "gnumeric"],
        "lifecycle_state": "CANDIDATE",
        "audit_state": "needs_audit",
        "spec_type": "full_public",
        "priority": 3,
        "parallelizable": True,
        "notes": "Both have full public specs; lower complexity than binary formats.",
    },
    GROUP_IMAGE: {
        "description": "Image/metafile format candidates (WMF, EMF)",
        "formats": ["wmf", "emf"],
        "lifecycle_state": "CANDIDATE",
        "audit_state": "needs_audit",
        "spec_type": "mixed",  # partial public
        "priority": 4,
        "parallelizable": True,
        "notes": "Windows metafile formats; partial public spec available.",
    },
}

# ---------------------------------------------------------------------------
# Sequencing rules per group
# ---------------------------------------------------------------------------

_SEQUENCING_RULES: dict[str, list[dict[str, str]]] = {
    GROUP_ACTIVE_FORMATS: [
        {"format": "fods", "rationale": "Primary spreadsheet active format; full evidence available."},
        {"format": "fodt", "rationale": "Primary document active format; mirrors fods pipeline."},
    ],
    GROUP_KOREAN_WORD_PROCESSING: [
        {"format": "hwpx", "rationale": "Partial public spec available; best entry point for audit."},
        {"format": "hwp", "rationale": "Requires reverse engineering; dependent on hwpx audit learnings."},
        {"format": "hwt", "rationale": "Template variant of hwp; benefits from hwp audit completion."},
    ],
    GROUP_ARCHIVE: [
        {"format": "alz", "rationale": "Korean archive format; predecessor to egg; simpler structure."},
        {"format": "egg", "rationale": "Successor to alz; shares structural similarities."},
    ],
    GROUP_DOCUMENT: [
        {"format": "gnumeric", "rationale": "Full public spec; well-documented XML spreadsheet format."},
        {"format": "abw", "rationale": "Full public spec; AbiWord XML document format."},
    ],
    GROUP_IMAGE: [
        {"format": "wmf", "rationale": "Older Windows Metafile format; better-documented partial spec."},
        {"format": "emf", "rationale": "Enhanced Metafile; extends WMF; sequence after WMF audit."},
    ],
}

# Gate stage estimates per lifecycle state
_GATES_REMAINING: dict[str, int] = {
    "EVIDENCE_READY": 1,           # Only Gate 11 remains
    "PLANNING_READY": 2,           # Gate 11 + implementation
    "IMPLEMENTATION_SIMULATION": 3,
    "DEC034_IV": 4,
    "VERIFIER_REVIEW": 5,
    "REQUIREMENTS_GENERATION": 6,
    "SPEC_NORMALIZATION": 7,
    "SPEC_DISCOVERY": 8,
    "SUPPORT_MATRIX_AUDIT": 9,
    "CANDIDATE": 10,
    "BLOCKED": -1,
    "DEFERRED": -1,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stable_hash(data: Any) -> str:
    """SHA-256 of canonical JSON, first 16 hex chars."""
    payload = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _governance_copy() -> dict[str, Any]:
    return dict(_GOVERNANCE_FLAGS)


def _estimated_sprint_count(lifecycle_state: str, spec_type: str, parallelizable: bool, fmt_count: int) -> int:
    """Estimate number of sprints to reach PLANNING_READY from current state."""
    gates = _GATES_REMAINING.get(lifecycle_state, 10)
    if gates < 0:
        return -1
    base = max(1, gates // 2)
    if spec_type == "reverse_engineering":
        base += 2
    elif spec_type == "mixed":
        base += 1
    if not parallelizable:
        base += fmt_count - 1  # sequential penalty
    return base


# ---------------------------------------------------------------------------
# Core planning functions
# ---------------------------------------------------------------------------

def plan_format_group(
    group_name: str,
    formats: list[str] | None = None,
    lifecycle_state: str | None = None,
    spec_type: str | None = None,
    parallelizable: bool | None = None,
    sequencing: list[dict[str, str]] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """
    Produce a deterministic acquisition plan for a format group.

    Parameters
    ----------
    group_name : str
        Logical group name.
    formats : list[str] | None
        Format IDs in this group. Defaults to group definition if group_name is known.
    lifecycle_state : str | None
        Current lifecycle state. Defaults to group definition value if None.
    spec_type : str | None
        Spec availability type. Defaults to group definition value if None.
    parallelizable : bool | None
        Whether formats can be worked in parallel. Defaults to group definition value if None.
    sequencing : list[dict] | None
        Ordered sequencing recommendations. Each entry: {"format": str, "rationale": str}.
    notes : str
        Additional planning notes.

    Returns
    -------
    dict  JSON-serializable plan result.
    """
    # Resolve from predefined group if available
    if group_name in FORMAT_GROUPS and formats is None:
        grp = FORMAT_GROUPS[group_name]
        formats = grp["formats"]
        if lifecycle_state is None:
            lifecycle_state = grp["lifecycle_state"]
        if spec_type is None:
            spec_type = grp["spec_type"]
        if parallelizable is None:
            parallelizable = grp["parallelizable"]
        notes = notes or grp.get("notes", "")

    # Apply defaults for custom groups
    if lifecycle_state is None:
        lifecycle_state = "CANDIDATE"
    if spec_type is None:
        spec_type = "full_public"
    if parallelizable is None:
        parallelizable = True

    formats = formats or []
    seq = sequencing or _SEQUENCING_RULES.get(group_name, [
        {"format": f, "rationale": "Ordered by format ID."} for f in sorted(formats)
    ])

    est_sprints = _estimated_sprint_count(lifecycle_state, spec_type, parallelizable, len(formats))
    gates_remaining = _GATES_REMAINING.get(lifecycle_state, 10)

    # Build blockers
    blockers: list[str] = []
    if lifecycle_state in ("BLOCKED", "DEFERRED"):
        blockers.append(f"group_in_{lifecycle_state.lower()}_state")
    if spec_type == "none":
        blockers.append("no_spec_available")
    if spec_type == "reverse_engineering":
        blockers.append("reverse_engineering_requires_legal_review")

    # Build recommendations
    recs: list[str] = []
    if spec_type in ("reverse_engineering", "none"):
        recs.append("[PLAN-REC] Conduct support-matrix audit before spec discovery.")
    if spec_type == "mixed":
        recs.append("[PLAN-REC] Segregate full-public formats from reverse-engineering formats.")
    if not parallelizable and len(formats) > 1:
        recs.append(f"[PLAN-REC] Process formats sequentially per sequencing_recommendation.")
    if lifecycle_state == "CANDIDATE":
        recs.append("[PLAN-REC] Begin with SUPPORT_MATRIX_AUDIT as first gate.")
    if gates_remaining <= 2 and lifecycle_state not in ("BLOCKED", "DEFERRED"):
        recs.append("[PLAN-REC] Formats near PLANNING_READY; prioritize DEC-034 IV.")

    plan_id = _stable_hash({
        "group_name": group_name,
        "formats": sorted(formats),
        "lifecycle_state": lifecycle_state,
        "spec_type": spec_type,
        "parallelizable": parallelizable,
    })

    return {
        "plan_id": plan_id,
        "group_name": group_name,
        "formats": list(formats),
        "format_count": len(formats),
        "lifecycle_state": lifecycle_state,
        "spec_type": spec_type,
        "parallelizable": parallelizable,
        "sequencing_recommendation": seq,
        "estimated_sprint_count": est_sprints,
        "gates_remaining": gates_remaining,
        "blockers": blockers,
        "recommendations": recs,
        "notes": notes,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "plan_note": "SIMULATION ESTIMATE — not a commitment or authorization to execute.",
    }


def plan_all_groups(
    custom_overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Produce plans for all predefined format groups.

    Parameters
    ----------
    custom_overrides : dict | None
        Per-group override kwargs passed to plan_format_group.

    Returns
    -------
    dict  Aggregate planning result with per-group plans, summary, and governance.
    """
    overrides = custom_overrides or {}
    per_group: dict[str, Any] = {}
    total_formats: set[str] = set()

    for group_name in ALL_GROUP_NAMES:
        kwargs = overrides.get(group_name, {})
        plan = plan_format_group(group_name, **kwargs)
        per_group[group_name] = plan
        total_formats.update(plan["formats"])

    # Aggregate summary
    groups_with_blockers = [g for g, p in per_group.items() if p["blockers"]]
    groups_near_ready = [
        g for g, p in per_group.items()
        if p["gates_remaining"] > 0 and p["gates_remaining"] <= 2
    ]
    all_ready = all(
        per_group[g]["lifecycle_state"] in ("EVIDENCE_READY", "PLANNING_READY")
        for g in ALL_GROUP_NAMES
    )

    aggregate_id = _stable_hash({
        "groups": sorted(ALL_GROUP_NAMES),
        "group_format_map": {g: sorted(per_group[g]["formats"]) for g in ALL_GROUP_NAMES},
    })

    return {
        "aggregate_plan_id": aggregate_id,
        "groups_planned": sorted(ALL_GROUP_NAMES),
        "per_group": per_group,
        "total_formats_covered": sorted(total_formats),
        "total_format_count": len(total_formats),
        "groups_with_blockers": groups_with_blockers,
        "groups_near_ready": groups_near_ready,
        "all_groups_ready": all_ready,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "plan_note": "SIMULATION ESTIMATE — aggregate multi-format plan. Not an execution authorization.",
    }


def plan_active_and_candidate_groups() -> dict[str, Any]:
    """
    Convenience function: plan active formats group + all candidate groups.
    Returns the same structure as plan_all_groups().
    """
    return plan_all_groups()


def get_group_definition(group_name: str) -> dict[str, Any] | None:
    """Return a copy of the predefined group definition, or None if not found."""
    if group_name not in FORMAT_GROUPS:
        return None
    return dict(FORMAT_GROUPS[group_name])
