"""design_artifact_validator.py — V153 (TC-SPW-004): Design artifact gate.

Blocks sprints that modify src/net/ files without a pre-execution design artifact at
.local/design-artifacts/{taskcard_id}.yaml.

Rules:
  FAIL + blocks_sprint=True  when:
    - .cs files in changed_files but no artifact file found
    - artifact.primary_class.is_partial_class == True  (new domain types may not use partial)
    - artifact.primary_class.estimated_loc not in (10, 800) range
    - artifact.no_dictionary_state == False
    - artifact.no_constant_returns == False
  WARN + blocks_sprint=False when:
    - spec_fact in public_api[*].spec_fact not found in sal-facts-latest.json
  PASS when:
    - No .cs changes in sprint (fast path)
    - Artifact valid, constraints satisfied, all spec_facts present
"""
from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from governance_validators_contract import validator  # noqa: F401
except ImportError:
    def validator(rule_id, domain=None):  # type: ignore[misc]
        def _dec(fn):
            return fn
        return _dec

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_ARTIFACTS_DIR = _REPO_ROOT / ".local" / "design-artifacts"
_SAL_LATEST = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
_SCHEMA_PATH = _REPO_ROOT / ".supervisor" / "schemas" / "design-artifact.schema.json"

_SRC_NET_CS = re.compile(r"src[/\\]net[/\\].+\.cs$", re.IGNORECASE)


def _cs_files_in_changed(declaration: dict) -> list[str]:
    """Return changed_files entries that are .cs files under src/net/."""
    changed = declaration.get("changed_files", [])
    return [f for f in changed if _SRC_NET_CS.search(str(f).replace("\\", "/"))]


def _artifact_path(declaration: dict) -> Path | None:
    """Return the expected design artifact path from declaration's taskcard_id."""
    tc_id = (
        declaration.get("taskcard_id")
        or declaration.get("sprint_id")
        or declaration.get("run_id")
        or ""
    )
    if not tc_id:
        return None
    return _ARTIFACTS_DIR / f"{tc_id}.yaml"


def _load_sal_fact_ids() -> set[str]:
    """Return set of fact IDs from sal-facts-latest.json. Empty set on error."""
    try:
        data = json.loads(_SAL_LATEST.read_text(encoding="utf-8"))
        facts = data if isinstance(data, list) else data.get("facts", [])
        return {
            str(f.get("fact_id") or f.get("id") or "")
            for f in facts
            if isinstance(f, dict)
        }
    except Exception:
        return set()


def _validate_artifact_content(artifact: dict, sal_ids: set[str]) -> tuple[list[dict], list[dict]]:
    """Validate artifact fields. Returns (fail_items, warn_items)."""
    fails: list[dict] = []
    warns: list[dict] = []

    pc = artifact.get("primary_class", {})
    if not isinstance(pc, dict):
        fails.append({"issue": "INVALID_PRIMARY_CLASS", "detail": "primary_class must be a dict"})
        return fails, warns

    if pc.get("is_partial_class") is True:
        fails.append({
            "issue": "PARTIAL_CLASS_FORBIDDEN",
            "detail": f"primary_class.is_partial_class=true for '{pc.get('name', '?')}' — new domain types may not use partial classes",
        })

    est_loc = pc.get("estimated_loc")
    if est_loc is not None:
        if not isinstance(est_loc, int) or est_loc <= 10:
            fails.append({"issue": "LOC_TOO_LOW", "detail": f"estimated_loc={est_loc} must be > 10"})
        elif est_loc >= 800:
            fails.append({"issue": "LOC_EXCEEDS_CAP", "detail": f"estimated_loc={est_loc} must be < 800 (V78 cap)"})

    spec_qname = pc.get("spec_qname", "")
    if not spec_qname or not str(spec_qname).strip():
        fails.append({"issue": "MISSING_SPEC_QNAME", "detail": "primary_class.spec_qname must be non-empty"})

    if artifact.get("no_dictionary_state") is False:
        fails.append({"issue": "DICTIONARY_STATE_FORBIDDEN", "detail": "no_dictionary_state=false — commit denies using Dictionary fields"})

    if artifact.get("no_constant_returns") is False:
        fails.append({"issue": "CONSTANT_RETURNS_FORBIDDEN", "detail": "no_constant_returns=false — commit denies constant-return getters"})

    # SAL cross-reference (WARN-only)
    if sal_ids:
        for api in artifact.get("public_api", []):
            if not isinstance(api, dict):
                continue
            fact_id = api.get("spec_fact", "")
            if fact_id and fact_id not in sal_ids:
                warns.append({
                    "issue": "SPEC_FACT_NOT_IN_SAL",
                    "detail": f"spec_fact '{fact_id}' for api '{api.get('name', '?')}' not found in sal-facts-latest.json",
                    "fact_id": fact_id,
                })

    return fails, warns


@validator(rule_id="V153", domain="dotnet")
def validate_design_artifact_present(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V153 (TC-SPW-004): Sprints touching src/net/ must have a pre-execution design artifact.

    A design artifact is a YAML file at .local/design-artifacts/{taskcard_id}.yaml that:
    - Declares the target class, estimated LOC, and spec QName
    - Commits to no partial classes, no Dictionary state, no constant returns
    - Lists public API members with spec_fact cross-references

    Returns FAIL+blocks_sprint=True when artifact is absent or violates constraints.
    Returns WARN+blocks_sprint=False when spec_facts are unverifiable against SAL.
    Returns PASS when no .cs files changed or artifact is valid.
    """
    _r = (repo_root or _REPO_ROOT).resolve()

    cs_files = _cs_files_in_changed(declaration)
    if not cs_files:
        return {
            "validator": "validate_design_artifact_present",
            "rule_id": "V153",
            "result": "PASS",
            "items": [],
            "summary": "V153: No src/net/ .cs files in changed_files — skip",
            "blocks_sprint": False,
        }

    # Locate artifact
    artifacts_dir = _r / ".local" / "design-artifacts"
    tc_id = (
        declaration.get("taskcard_id")
        or declaration.get("sprint_id")
        or declaration.get("run_id")
        or ""
    )
    artifact_path = artifacts_dir / f"{tc_id}.yaml" if tc_id else None

    if not artifact_path or not artifact_path.exists():
        return {
            "validator": "validate_design_artifact_present",
            "rule_id": "V153",
            "result": "FAIL",
            "items": [{
                "issue": "ARTIFACT_MISSING",
                "detail": (
                    f"Design artifact not found at '.local/design-artifacts/{tc_id}.yaml'. "
                    f"Changed .cs files: {cs_files[:3]}"
                ),
                "artifact_path": str(artifact_path) if artifact_path else "unknown",
            }],
            "summary": (
                f"V153: Design artifact missing for taskcard '{tc_id}' — "
                f"{len(cs_files)} .cs file(s) changed without pre-execution commitment"
            ),
            "blocks_sprint": True,
        }

    # Load artifact YAML
    try:
        import yaml as _yaml
        artifact = _yaml.safe_load(artifact_path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {
            "validator": "validate_design_artifact_present",
            "rule_id": "V153",
            "result": "FAIL",
            "items": [{"issue": "ARTIFACT_UNREADABLE", "detail": str(e)}],
            "summary": f"V153: Design artifact at '{artifact_path}' could not be parsed: {e}",
            "blocks_sprint": True,
        }

    # Load SAL facts (non-blocking if unavailable)
    sal_ids = _load_sal_fact_ids()

    fail_items, warn_items = _validate_artifact_content(artifact, sal_ids)

    if fail_items:
        all_items = fail_items + [dict(w, result="WARN") for w in warn_items]
        return {
            "validator": "validate_design_artifact_present",
            "rule_id": "V153",
            "result": "FAIL",
            "items": all_items,
            "summary": f"V153: {len(fail_items)} design artifact constraint(s) violated for '{tc_id}'",
            "blocks_sprint": True,
        }

    if warn_items:
        return {
            "validator": "validate_design_artifact_present",
            "rule_id": "V153",
            "result": "WARN",
            "items": [dict(w, result="WARN") for w in warn_items],
            "summary": (
                f"V153: Artifact valid but {len(warn_items)} spec_fact(s) not verified in SAL — "
                "advisory only"
            ),
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_design_artifact_present",
        "rule_id": "V153",
        "result": "PASS",
        "items": [],
        "summary": f"V153: Design artifact for '{tc_id}' is valid — {len(cs_files)} .cs file(s) covered",
        "blocks_sprint": False,
    }
