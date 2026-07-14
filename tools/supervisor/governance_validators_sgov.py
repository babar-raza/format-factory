"""governance_validators_sgov.py — Skill governance validators.

Extracted from governance_validators_ext.py (at LOC cap 1413/1413) to accommodate
additional skill-governance validators without violating the baseline_loc_cap ceiling.

TC-SGOV-W3-001: V-SGF-002 validate_skill_receipt_presence
  — Check that PRODUCT_SOURCE work items have a skill execution receipt on disk.
  — WARN-only: receipt writing is still being established as of 2026-07-11.
  — Receipts live in .local/skill-execution-receipts/<skill_id>-<run_id>.yaml.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Directory where skill execution receipts are stored (per skill-only-policy.yaml §5)
_RECEIPTS_DIR = ".local/skill-execution-receipts"


def validate_skill_receipt_presence(
    declaration: dict, repo_root: Path | None = None
) -> dict:
    """V-SGF-002: Verify that PRODUCT_SOURCE work items have a skill execution receipt.

    For each PRODUCT_SOURCE (or PRODUCT_TEST) item that declares skill IDs, check
    that at least one receipt file exists in .local/skill-execution-receipts/ that
    references that skill_id.

    Receipt filename pattern:
      .local/skill-execution-receipts/<skill_id>-<run_id>.yaml
      OR any .yaml file in that directory whose skill_id field matches.

    Enforcement level:
      - WARN-only (blocks_sprint=False) — receipt writing is still being established.
      - If the receipts directory does not exist at all → WARN (advisory only).
      - If a declared skill has no matching receipt → WARN per item.

    Reference: docs/governance/skill-only-policy.yaml §5 (registration_required,
    execution_receipt_required) and EP-004 (PROMPT_ONLY enforcement gap).
    """
    repo = repo_root or _REPO_ROOT
    receipts_dir = repo / _RECEIPTS_DIR

    # Gather PRODUCT_SOURCE / PRODUCT_TEST items with declared skills
    all_items = (
        declaration.get("completed_work_items", []) or []
    ) + (
        declaration.get("planned_work_items", []) or []
    )

    product_items = [
        item for item in all_items
        if isinstance(item, dict)
        and item.get("item_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST")
        and item.get("declared_skill_ids")
        and isinstance(item.get("declared_skill_ids"), list)
        and len(item["declared_skill_ids"]) > 0
    ]

    if not product_items:
        return {
            "validator": "validate_skill_receipt_presence",
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": (
                "V-SGF-002: No PRODUCT_SOURCE items with declared_skill_ids — "
                "receipt check skipped"
            ),
        }

    if not receipts_dir.exists():
        # Receipts directory doesn't exist — all items lack receipts
        warnings = [
            {
                "item_id": item.get("item_id", item.get("id", "UNKNOWN")),
                "declared_skill_ids": item["declared_skill_ids"],
                "reason": "receipts_directory_absent",
            }
            for item in product_items
        ]
        return {
            "validator": "validate_skill_receipt_presence",
            "result": "WARN",
            "blocks_sprint": False,
            "items": warnings,
            "summary": (
                f"V-SGF-002: .local/skill-execution-receipts/ does not exist — "
                f"{len(warnings)} PRODUCT_SOURCE item(s) lack execution receipts (WARN-only)"
            ),
        }

    # Build index of skill_ids covered by existing receipts
    # Receipts may use filename prefix OR internal skill_id field
    covered_skill_ids: set[str] = set()
    try:
        for receipt_file in receipts_dir.glob("*.yaml"):
            # Extract skill_id from filename (pattern: <skill_id>-<run_id>.yaml)
            stem = receipt_file.stem  # e.g. "add-python-api-run-001"
            # Try reading internal skill_id field too
            try:
                import yaml as _yaml
                data = _yaml.safe_load(receipt_file.read_text(encoding="utf-8")) or {}
                if isinstance(data, dict) and data.get("skill_id"):
                    covered_skill_ids.add(str(data["skill_id"]))
            except Exception:
                pass
            # Also try matching filename prefixes against known patterns
            # Any skill whose id appears as a prefix of the stem is considered covered
            covered_skill_ids.add(stem)  # broad match — refine per-item below
    except Exception:
        pass

    def _receipt_exists_for_skill(skill_id: str) -> bool:
        """Return True if any receipt in the dir is attributable to skill_id."""
        if skill_id in covered_skill_ids:
            return True
        # Check if any receipt filename starts with skill_id
        for receipt_file in receipts_dir.glob(f"{skill_id}*.yaml"):
            return True
        return False

    missing_receipts: list[dict] = []
    for item in product_items:
        item_id = item.get("item_id", item.get("id", "UNKNOWN"))
        declared = item["declared_skill_ids"]
        uncovered = [sid for sid in declared if not _receipt_exists_for_skill(sid)]
        if uncovered:
            missing_receipts.append({
                "item_id": item_id,
                "declared_skill_ids": declared,
                "skills_without_receipts": uncovered,
                "reason": "skill_execution_receipt_absent",
            })

    if missing_receipts:
        return {
            "validator": "validate_skill_receipt_presence",
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing_receipts,
            "summary": (
                f"V-SGF-002: {len(missing_receipts)} PRODUCT_SOURCE item(s) have skills "
                f"without execution receipts in {_RECEIPTS_DIR} (WARN-only, EP-004)"
            ),
        }

    return {
        "validator": "validate_skill_receipt_presence",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": (
            f"V-SGF-002: All {len(product_items)} PRODUCT_SOURCE item(s) with declared "
            f"skills have execution receipts"
        ),
    }
