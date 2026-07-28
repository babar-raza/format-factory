"""Compatibility-gated supervisor dogfood lane construction.

generated_by: codex
"""


def available_dogfood_pairs() -> tuple[list[str], str]:
    """Return allowed converter pairs and an explicit gate status."""
    try:
        from tools.governance.skill_gates import converter_compat
    except ImportError:
        return [], "gate_unavailable"
    try:
        matrix = converter_compat.load_matrix()
    except converter_compat.MatrixError:
        return [], "matrix_absent"
    except Exception:
        return [], "matrix_absent"
    return converter_compat.allowed_pairs(matrix), "ok"


def build_dogfood_task(task_seq: int, selected_product_gaps_path: str) -> dict | None:
    """Build a governed dogfood task, a visible gate failure, or no task."""
    pairs, status = available_dogfood_pairs()
    if status == "gate_unavailable":
        return {
            "task_id": f"TASK-{task_seq:03d}",
            "title": "BLOCKED: converter compatibility gate unavailable",
            "description": (
                "tools.governance.skill_gates.converter_compat could not be imported, "
                "so no source-target pair can be assessed and the dogfood export lane "
                "was skipped. Repair the gate import before scheduling dogfood work. "
                "See docs/governance/skill-gate-validator-seam.md."
            ),
            "status": "blocked",
            "ff_doc_ref": "docs/governance/skill-gate-validator-seam.md",
            "supervisor_task_ref": "TC-PA-009",
            "acceptance_evidence": (
                "python -m tools.governance.skill_gates.dogfood_export_gate "
                "--source-format dif --target-format csv exits 0/1/2 (not ImportError)"
            ),
            "validation_command": (
                "python -c \"from tools.governance.skill_gates import converter_compat\""
            ),
            "non_authoritative": False,
            "lane": "C4",
        }
    if not pairs:
        return None
    pair_hint = ", ".join(pairs[:5])
    return {
        "task_id": f"TASK-{task_seq:03d}",
        "title": "Advance one dogfood export path using a Format Factory library",
        "description": (
            f"Product objective: close or verify a selected dogfood export from "
            f"{selected_product_gaps_path}. Use a Format Factory-produced library and "
            f"record truthful status. Only these pairs are registered as COMPATIBLE or "
            f"PROJECTION and may be generated: {pair_hint}. Invoke /add-dogfood-export; "
            f"do not generate a converter for an unlisted pair."
        ),
        "status": "pending",
        "ff_doc_ref": "docs/export/dogfood-export-strategy.md",
        "supervisor_task_ref": "R90-DOGFOOD-LANE",
        "acceptance_evidence": (
            "Dogfood test proves the Format Factory library path and matrix status is truthful"
        ),
        "validation_command": "pytest tests/ -x -q",
        "non_authoritative": True,
        "lane": "C4",
    }
