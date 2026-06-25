"""
Product task selector — scans real repo state to find safe bounded product-source tasks.

Sprint: FORMAT-FACTORY-AUTONOMOUS-FILE-FORMAT-ACQUISITION-MEGA-TRAIN-001
(originally: FORMAT-FACTORY-H6-QUEUE-DRIVEN-PRODUCT-SOURCE-PILOT-001)

Rules for task selection:
- Task must be AGENT_OWNED (no external gate, no human credential)
- Task must be BOUNDED: single function or small addition, not a structural rewrite
- Task must be REVERSIBLE: can be rolled back by reverting the diff
- Task must introduce NO new external dependencies
- Task must NOT mutate poc-targets.yaml or registry files
- Task must target FOSS Python source only (no src/net/)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

_repo_root = Path(__file__).resolve().parent.parent.parent

# ============================================================
# Authority gate — prevents blocked formats from emitting tasks
# ============================================================

_BLOCKED_AUTHORITY_STATES: frozenset[str] = frozenset({
    "BLOCKED_MISSING_SPEC",
    "BLOCKED_METADATA_ONLY_SPEC",
    "BLOCKED_NO_VERIFIED_FACTS",
    "BLOCKED_SYNTHETIC_REQUIREMENTS",
    "BLOCKED_AI_ONLY_AUTHORITY",
    "BLOCKED_UNKNOWN_AUTHORITY",
    "BLOCKED_INSUFFICIENT_AUTHORITY",  # SAL-HEAL-A004: P<4 without valid exception
})


def _get_format_authority_status(format_name: str) -> str:
    """Return the authority gate status for a format.

    SAL-HEAL-A004 (2026-06-25): Now calls authority_gate_validation.py to get the
    real P-level instead of using poc-targets.yaml binary membership check.
    Formats with exception_classification (Tier 2) are ALLOWED_WITH_EXCEPTION.
    Formats at P4+ are ALLOWED. Formats below P4 without exception are BLOCKED.

    Falls back to poc-targets.yaml membership if authority_gate_validation.py fails.
    """
    import subprocess

    fmt_lower = format_name.lower()
    # Try authority_gate_validation.py for the real P-level
    try:
        result = subprocess.run(
            [sys.executable, str(_repo_root / "tools" / "supervisor" / "authority_gate_validation.py"),
             "--format-id", fmt_lower, "--json"],
            capture_output=True, text=True, timeout=15
        )
        # Parse JSON even on non-zero exit (authority_gate returns 1 for P<4 formats with valid JSON)
        if result.stdout.strip():
            gate = json.loads(result.stdout)
            product_expansion = gate.get("product_expansion_allowed", False)
            exception_class = gate.get("exception_allowed")
            if product_expansion:
                return "ALLOWED"
            if exception_class:
                # Tier 2 format with valid exception — ALLOWED with recorded exception
                return f"ALLOWED_WITH_EXCEPTION:{exception_class}"
            return "BLOCKED_INSUFFICIENT_AUTHORITY"
    except Exception:
        pass  # Fall through to poc-targets fallback

    # Fallback: poc-targets.yaml membership (legacy — kept as safety net per SAL-HEAL-A004)
    poc_targets_path = _repo_root / "product-capability-matrix" / "poc-targets.yaml"
    if not poc_targets_path.exists():
        return "BLOCKED_MISSING_SPEC"
    try:
        with open(poc_targets_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return "BLOCKED_MISSING_SPEC"
    registered: set[str] = set()
    for section_key, section_val in data.items():
        if isinstance(section_val, list):
            for item in section_val:
                if isinstance(item, dict) and "format" in item:
                    registered.add(item["format"].upper())
    if format_name.upper() in registered:
        return "ALLOWED"
    return "BLOCKED_UNKNOWN_AUTHORITY"

# Known safe bounded task catalog — curated from real repo state
_CANDIDATE_CATALOG: list[dict[str, Any]] = [
    {
        "task_id": "h8-probe-abw-001",
        "format": "ABW",
        "action": "add_function",
        "target_file": "src/python/abw/abw_codec.py",
        "also_modifies": ["src/python/abw/__init__.py"],
        "function_name": "probe_abw",
        "description": "Add probe_abw(source) format-detection function: returns True if source appears to be a valid ABW/AbiWord XML document",
        "capability_added": "FORMAT_DETECTION",
        "bounded": True,
        "reversible": True,
        "new_external_deps": False,
        "gate_required": None,
        "classification": "AGENT_OWNED_SAFE",
        "rationale": (
            "ABW codec (Sprint 7 pilot) has load/create/write but no probe/detect. "
            "probe_abw() reads the first bytes and checks for '<abiword' root element. "
            "Pure stdlib, ~20 lines, non-structural addition."
        ),
    },
    {
        "task_id": "h8-probe-gnumeric-001",
        "format": "Gnumeric",
        "action": "add_function",
        "target_file": "src/python/gnumeric/gnumeric_codec.py",
        "also_modifies": ["src/python/gnumeric/__init__.py"],
        "function_name": "probe_gnumeric",
        "description": "Add probe_gnumeric(source) format-detection function: returns True if source appears to be a valid gzip-compressed Gnumeric XML document",
        "capability_added": "FORMAT_DETECTION",
        "bounded": True,
        "reversible": True,
        "new_external_deps": False,
        "gate_required": None,
        "classification": "AGENT_OWNED_SAFE",
        "rationale": (
            "Gnumeric codec has load/export_to_csv but no probe/detect. "
            "probe_gnumeric() checks gzip magic bytes + decompresses header to check for Gnumeric namespace. "
            "Pure stdlib, ~15 lines."
        ),
    },
    {
        "task_id": "h9-gnumeric-create-001",
        "format": "Gnumeric",
        "action": "add_function",
        "target_file": "src/python/gnumeric/gnumeric_codec.py",
        "also_modifies": ["src/python/gnumeric/__init__.py"],
        "function_name": "create_gnumeric",
        "description": "Add create_gnumeric(sheets) document-builder: builds a Gnumeric workbook model from a list of sheet dicts",
        "capability_added": "DOCUMENT_CREATION",
        "bounded": True,
        "reversible": True,
        "new_external_deps": False,
        "gate_required": None,
        "classification": "AGENT_OWNED_SAFE",
        "rationale": (
            "Gnumeric codec has load/export_to_csv but no create/write. "
            "create_gnumeric() builds an in-memory model dict from row-major sheet data. "
            "Pure stdlib, ~25 lines, non-structural addition."
        ),
    },
    {
        "task_id": "h9-gnumeric-write-001",
        "format": "Gnumeric",
        "action": "add_function",
        "target_file": "src/python/gnumeric/gnumeric_codec.py",
        "also_modifies": ["src/python/gnumeric/__init__.py"],
        "function_name": "write_gnumeric",
        "description": "Add write_gnumeric(model, dest) serializer: writes a gzip-compressed Gnumeric XML file from a model dict",
        "capability_added": "DOCUMENT_WRITE",
        "bounded": True,
        "reversible": True,
        "new_external_deps": False,
        "gate_required": None,
        "classification": "AGENT_OWNED_SAFE",
        "rationale": (
            "Gnumeric codec has no write path. "
            "write_gnumeric() serializes the model dict to gzip-compressed Gnumeric XML. "
            "Pure stdlib (gzip + ET), ~35 lines."
        ),
    },
    {
        "task_id": "h9-abw-txt-export-001",
        "format": "ABW",
        "action": "add_function",
        "target_file": "src/python/abw/abw_codec.py",
        "also_modifies": ["src/python/abw/__init__.py"],
        "function_name": "export_to_txt",
        "description": "Add export_to_txt(source) text-export: extracts all paragraph text from an ABW document as a plain-text string",
        "capability_added": "PLAIN_TEXT_EXPORT",
        "bounded": True,
        "reversible": True,
        "new_external_deps": False,
        "gate_required": None,
        "classification": "AGENT_OWNED_SAFE",
        "rationale": (
            "ABW codec has load/create/write/probe but no plain-text export. "
            "export_to_txt() calls load() and joins paragraphs with newlines. "
            "Pure stdlib, ~10 lines."
        ),
    },
]


def _check_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Verify a candidate task is actionable in the current repo state."""
    result = dict(candidate)

    # Authority gate — must pass before any other check (SAL-HEAL-A004: calls authority_gate_validation.py)
    authority_status = _get_format_authority_status(candidate.get("format", ""))
    result["authority_status"] = authority_status
    # ALLOWED_WITH_EXCEPTION:* statuses are allowed (Tier 2 formats with valid exception)
    is_blocked = authority_status in _BLOCKED_AUTHORITY_STATES and not authority_status.startswith("ALLOWED")
    if is_blocked:
        result["target_exists"] = False
        result["already_implemented"] = False
        result["actionable"] = False
        result["blocker"] = f"authority_gate_blocked: {authority_status}"
        return result

    target = _repo_root / candidate["target_file"]
    result["target_exists"] = target.exists()

    # Check function not already present
    if target.exists():
        content = target.read_text(encoding="utf-8")
        fn = candidate["function_name"]
        result["already_implemented"] = f"def {fn}" in content or f"def {fn}(" in content
    else:
        result["already_implemented"] = False

    # Check also_modifies files exist
    for mod in candidate.get("also_modifies", []):
        if not (_repo_root / mod).exists():
            result["already_implemented"] = True  # can't add to missing file
            result["blocker"] = f"missing file: {mod}"
            break

    result["actionable"] = (
        result["target_exists"]
        and not result.get("already_implemented", False)
        and "blocker" not in result
    )
    return result


_GAP_LEDGER_PATH = _repo_root / "reports" / "capability-layer" / "gap-ledger.json"


def _load_gap_candidates() -> list[dict[str, Any]]:
    """Load gap candidates from the capability gap ledger.

    Returns a list of gap candidate dicts (may be empty if all gaps are closed).
    Each candidate has: task_id, format, action, target_file, function_name,
    classification, gap_source, gap_priority.
    """
    if not _GAP_LEDGER_PATH.exists():
        return []
    try:
        data = json.loads(_GAP_LEDGER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    candidates: list[dict[str, Any]] = []
    for gap in data.get("gaps", []):
        fmt = gap.get("format", "")
        fn = gap.get("function_name", gap.get("capability", ""))
        gap_id = gap.get("gap_id", f"GAP-{fmt}-{fn}")
        target = gap.get("target_file", f"src/python/{fmt.lower()}/{fmt.lower()}_codec.py")
        candidates.append({
            "task_id": gap_id,
            "format": fmt,
            "action": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "target_file": target,
            "function_name": fn,
            "classification": "AGENT_OWNED_SAFE",
            "gap_source": gap_id,
            "gap_priority": gap.get("priority", "P2"),
        })
    return candidates


def select_product_task() -> dict[str, Any]:
    """Select the best safe bounded product-source task from the current repo state.

    Returns a dict with:
        candidates: list of all evaluated candidates
        selected: the chosen task (or None if none actionable)
        selection_rationale: explanation
        no_safe_task_found: bool
        gap_candidates_loaded: int count of gap candidates loaded
    """
    gap_candidates = _load_gap_candidates()
    evaluated_gaps = [
        {**c, "actionable": True, "rationale": f"Gap-derived: {c['gap_priority']}"}
        for c in gap_candidates
    ]
    evaluated_catalog = [_check_candidate(c) for c in _CANDIDATE_CATALOG]
    # Gap candidates appear before catalog candidates
    evaluated = evaluated_gaps + evaluated_catalog

    actionable = [c for c in evaluated if c.get("actionable")]

    if not actionable:
        return {
            "candidates": evaluated,
            "selected": None,
            "selection_rationale": "No actionable safe bounded tasks found in current repo state",
            "no_safe_task_found": True,
            "gap_candidates_loaded": len(gap_candidates),
        }

    # Prefer the first actionable candidate (gap candidates take priority)
    selected = actionable[0]
    return {
        "candidates": evaluated,
        "selected": selected,
        "selection_rationale": (
            f"Selected {selected['task_id']}: {selected.get('description', selected.get('function_name', ''))}. "
            f"Reason: {selected.get('rationale', '')}"
        ),
        "no_safe_task_found": False,
        "gap_candidates_loaded": len(gap_candidates),
    }


def write_selection_report(output_dir: Path | None = None) -> dict[str, Any]:
    """Run selection and write reports to output_dir."""
    if output_dir is None:
        output_dir = _repo_root / "reports" / "h6-product-source-pilot" / "product-task"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = select_product_task()

    candidates_path = output_dir / "product-task-candidates.json"
    candidates_path.write_text(
        json.dumps(result["candidates"], indent=2, default=str), encoding="utf-8"
    )

    selected_path = output_dir / "selected-product-task.json"
    selected_path.write_text(
        json.dumps(
            {
                "selected": result["selected"],
                "selection_rationale": result["selection_rationale"],
                "no_safe_task_found": result["no_safe_task_found"],
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"Candidates: {len(result['candidates'])}")
    print(f"Actionable: {sum(1 for c in result['candidates'] if c.get('actionable'))}")
    print(f"Selected: {result['selected']['task_id'] if result['selected'] else 'NONE'}")
    print(f"No safe task found: {result['no_safe_task_found']}")
    return result


if __name__ == "__main__":
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    result = write_selection_report(out_dir)
    sys.exit(0 if not result["no_safe_task_found"] else 1)
