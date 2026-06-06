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

_repo_root = Path(__file__).resolve().parent.parent.parent

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


def select_product_task() -> dict[str, Any]:
    """Select the best safe bounded product-source task from the current repo state.

    Returns a dict with:
        candidates: list of all evaluated candidates
        selected: the chosen task (or None if none actionable)
        selection_rationale: explanation
        no_safe_task_found: bool
    """
    evaluated = [_check_candidate(c) for c in _CANDIDATE_CATALOG]

    actionable = [c for c in evaluated if c.get("actionable")]

    if not actionable:
        return {
            "candidates": evaluated,
            "selected": None,
            "selection_rationale": "No actionable safe bounded tasks found in current repo state",
            "no_safe_task_found": True,
        }

    # Prefer the first actionable candidate (ABW probe_abw takes priority)
    selected = actionable[0]
    return {
        "candidates": evaluated,
        "selected": selected,
        "selection_rationale": (
            f"Selected {selected['task_id']}: {selected['description']}. "
            f"Reason: {selected['rationale']}"
        ),
        "no_safe_task_found": False,
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
