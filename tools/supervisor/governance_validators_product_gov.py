"""governance_validators_product_gov.py — V150-V151, V154-V157: Product governance chain validators.

Added 2026-07-14 (CT-GOV-002, memoized-frolicking-donut TC-GOV-015).

These validators enforce the governed change lifecycle:
  Change Proposal (CP-*) → Impact Analysis (CI-*) → Release Candidate (RC-*) → GA artifact

All six validators return WARN (blocks_sprint=False) when the governed infrastructure
(registry/change-proposals/, registry/impact-analyses/, etc.) does not yet exist.
They return FAIL (blocks_sprint=True) only when the infrastructure is present but
a declaration violates its rules.

V150 (validate_governed_artifact_pre_flight): PROMOTED_STABLE files in changed_files
    must have a matching accepted CP-* in registry/change-proposals/. WARN when
    directory absent (infrastructure not yet set up). FAIL when present + violated.

V151 (validate_change_proposal_coverage): PRODUCT_SOURCE items must declare a
    cp_ref field when modifying PROMOTED artifacts. WARN-only (advisory).

V154 (validate_impact_analysis_on_accepted_proposals): For each ACCEPTED CP-*
    in registry/change-proposals/, a matching CI-* must exist in
    registry/impact-analyses/. WARN when directory absent.

V155 (validate_release_candidate_decision_chain): Release candidate files (RC-*.yaml)
    in registry/release-candidates/ must have final_decision: ACCEPT and must list
    only CP-* that are ACCEPTED. WARN when directory absent.

V156 (validate_governance_counter_report_fresh): reports/product-governance/
    governance-counter-report.yaml must exist and be < 14 days old when a
    PRODUCT_SOURCE item is in the declaration. WARN-only.

V157 (validate_governance_binding_paths): registry/governance-binding.yaml must
    exist and all listed governance_files paths must resolve on disk. FAIL when
    governance-binding.yaml is present but lists missing paths (blocks_sprint=True).
    WARN when governance-binding.yaml is absent.
"""

from __future__ import annotations

from governance_validators_contract import validator  # noqa: F401

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_CP_DIR = _REPO_ROOT / "registry" / "change-proposals"
_CI_DIR = _REPO_ROOT / "registry" / "impact-analyses"
_RC_DIR = _REPO_ROOT / "registry" / "release-candidates"
_GOVERNANCE_BINDING = _REPO_ROOT / "registry" / "governance-binding.yaml"
_COUNTER_REPORT = _REPO_ROOT / "reports" / "product-governance" / "governance-counter-report.yaml"
_PROMOTED_STABLE_REGISTRY = _REPO_ROOT / "registry" / "promoted-stable-registry.yaml"


def _result(vid: str, name: str, passed: bool, items: list, blocks: bool) -> dict:
    label = "PASS" if passed else ("FAIL" if blocks else "WARN")
    return {
        "validator": name,
        "result": label,
        "blocks_sprint": (not passed) and blocks,
        "items": items,
        "summary": f"{vid}: {'OK' if passed else str(len(items)) + ' issue(s)'}",
    }


def _load_yaml_safe(path: Path) -> dict | list | None:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ── V150 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V150", domain="governance", description=(
    "PROMOTED_STABLE files in changed_files must have an accepted CP-* "
    "in registry/change-proposals/ (WARN when infra absent, FAIL when violated)"
))
def validate_governed_artifact_pre_flight(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V150 (CT-GOV-002): PROMOTED_STABLE changed_files must have accepted CP-*.

    Returns WARN when registry/change-proposals/ is absent (not yet set up).
    Returns FAIL (blocks_sprint=True) when changed_files touch a PROMOTED_STABLE
    path and no accepted CP-* covers that change.
    """
    name = "validate_governed_artifact_pre_flight"
    _root = repo_root or _REPO_ROOT

    if not (_root / "registry" / "change-proposals").exists():
        return _result("V150", name, True, [], False) | {
            "result": "WARN",
            "summary": "V150: registry/change-proposals/ absent — infrastructure not set up yet",
        }

    promoted_registry = _root / "registry" / "promoted-stable-registry.yaml"
    if not promoted_registry.exists():
        return _result("V150", name, True, [], False) | {
            "result": "WARN",
            "summary": "V150: registry/promoted-stable-registry.yaml absent — skipped",
        }

    promoted_data = _load_yaml_safe(promoted_registry) or {}
    promoted_paths: set[str] = set(promoted_data.get("promoted_paths", []))
    if not promoted_paths:
        return _result("V150", name, True, [], False) | {
            "result": "WARN",
            "summary": "V150: no PROMOTED_STABLE paths registered — nothing to check",
        }

    changed_files: list[str] = declaration.get("changed_files", [])
    promoted_changed = [f for f in changed_files if f in promoted_paths]
    if not promoted_changed:
        return _result("V150", name, True, [], False) | {
            "summary": "V150: no PROMOTED_STABLE files in changed_files",
        }

    # Load accepted CPs
    cp_dir = _root / "registry" / "change-proposals"
    accepted_paths: set[str] = set()
    for cp_file in cp_dir.glob("*.yaml"):
        cp_data = _load_yaml_safe(cp_file) or {}
        if cp_data.get("status") == "ACCEPTED":
            for p in cp_data.get("affected_paths", []):
                accepted_paths.add(p)

    violations = [p for p in promoted_changed if p not in accepted_paths]
    if violations:
        return _result("V150", name, False, violations, True) | {
            "summary": (
                f"V150: {len(violations)} PROMOTED_STABLE file(s) modified without "
                "accepted CP-*. Create a Change Proposal in registry/change-proposals/."
            ),
        }
    return _result("V150", name, True, [], False) | {
        "summary": f"V150: all {len(promoted_changed)} PROMOTED_STABLE change(s) covered by accepted CP-*",
    }


# ── V151 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V151", domain="governance", description=(
    "PRODUCT_SOURCE items should declare cp_ref when modifying PROMOTED artifacts (WARN-only)"
))
def validate_change_proposal_coverage(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V151 (CT-GOV-002): PRODUCT_SOURCE items should declare cp_ref for PROMOTED artifact changes.

    Advisory-only (blocks_sprint=False). Checks that PRODUCT_SOURCE planned_work_items
    include a cp_ref field when the item's evidence_paths include promoted paths.
    """
    name = "validate_change_proposal_coverage"
    _root = repo_root or _REPO_ROOT

    promoted_registry = _root / "registry" / "promoted-stable-registry.yaml"
    if not promoted_registry.exists():
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V151: registry/promoted-stable-registry.yaml absent — skipped",
        }

    promoted_data = _load_yaml_safe(promoted_registry) or {}
    promoted_paths: set[str] = set(promoted_data.get("promoted_paths", []))

    items = declaration.get("planned_work_items", [])
    missing_cp_ref = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if "cp_ref" in item:
            continue
        evidence = item.get("evidence_paths", [])
        if any(e in promoted_paths for e in evidence):
            missing_cp_ref.append(item.get("item_id", "unknown"))

    if missing_cp_ref:
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": missing_cp_ref,
            "summary": (
                f"V151: {len(missing_cp_ref)} PRODUCT_SOURCE item(s) modify PROMOTED "
                "paths without cp_ref field (advisory)"
            ),
        }
    return {
        "validator": name,
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V151: all PRODUCT_SOURCE items referencing PROMOTED paths have cp_ref",
    }


# ── V154 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V154", domain="governance", description=(
    "For each ACCEPTED CP-* in registry/change-proposals/, a matching CI-* must "
    "exist in registry/impact-analyses/ (WARN when infra absent)"
))
def validate_impact_analysis_on_accepted_proposals(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V154 (CT-GOV-002): ACCEPTED CP-* must have a CI-* in registry/impact-analyses/.

    Returns WARN when either directory is absent.
    Returns FAIL when an ACCEPTED CP-* has no matching impact analysis.
    """
    name = "validate_impact_analysis_on_accepted_proposals"
    _root = repo_root or _REPO_ROOT
    cp_dir = _root / "registry" / "change-proposals"
    ci_dir = _root / "registry" / "impact-analyses"

    if not cp_dir.exists() or not ci_dir.exists():
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V154: registry/change-proposals/ or registry/impact-analyses/ absent — skipped",
        }

    accepted_cps = []
    for cp_file in cp_dir.glob("*.yaml"):
        cp_data = _load_yaml_safe(cp_file) or {}
        if cp_data.get("status") == "ACCEPTED":
            accepted_cps.append(cp_file.stem)

    if not accepted_cps:
        return {
            "validator": name,
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V154: no ACCEPTED CP-* found — nothing to check",
        }

    ci_ids = {f.stem for f in ci_dir.glob("*.yaml")}
    missing_ci = []
    for cp_stem in accepted_cps:
        expected_ci = cp_stem.replace("CP-", "CI-", 1)
        if expected_ci not in ci_ids:
            missing_ci.append(f"{cp_stem} → expected {expected_ci}")

    if missing_ci:
        return {
            "validator": name,
            "result": "FAIL",
            "blocks_sprint": True,
            "items": missing_ci,
            "summary": (
                f"V154: {len(missing_ci)} ACCEPTED CP-* have no matching CI-* "
                "in registry/impact-analyses/"
            ),
        }
    return {
        "validator": name,
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V154: all {len(accepted_cps)} ACCEPTED CP-* have matching CI-*",
    }


# ── V155 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V155", domain="governance", description=(
    "RC files in registry/release-candidates/ must have final_decision=ACCEPT "
    "and only reference ACCEPTED CP-* (WARN when directory absent)"
))
def validate_release_candidate_decision_chain(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V155 (CT-GOV-002): Release candidate files must have final_decision=ACCEPT
    and included_changes must all reference ACCEPTED CP-*.

    Returns WARN when directory absent.
    Returns FAIL when a RC has final_decision != ACCEPT or references non-ACCEPTED CP-*.
    """
    name = "validate_release_candidate_decision_chain"
    _root = repo_root or _REPO_ROOT
    rc_dir = _root / "registry" / "release-candidates"
    cp_dir = _root / "registry" / "change-proposals"

    if not rc_dir.exists():
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V155: registry/release-candidates/ absent — skipped",
        }

    cp_statuses: dict[str, str] = {}
    if cp_dir.exists():
        for cp_file in cp_dir.glob("*.yaml"):
            cp_data = _load_yaml_safe(cp_file) or {}
            cp_statuses[cp_file.stem] = cp_data.get("status", "UNKNOWN")

    violations = []
    for rc_file in rc_dir.glob("*.yaml"):
        rc_data = _load_yaml_safe(rc_file) or {}
        decision = rc_data.get("final_decision")
        if decision and decision != "ACCEPT":
            violations.append(f"{rc_file.stem}: final_decision={decision!r} (must be ACCEPT)")
            continue
        for cp_ref in rc_data.get("included_changes", []):
            status = cp_statuses.get(cp_ref)
            if status is None:
                violations.append(f"{rc_file.stem}: references {cp_ref!r} not found in registry")
            elif status != "ACCEPTED":
                violations.append(
                    f"{rc_file.stem}: references {cp_ref!r} which has status={status!r} (must be ACCEPTED)"
                )

    if violations:
        return {
            "validator": name,
            "result": "FAIL",
            "blocks_sprint": True,
            "items": violations,
            "summary": f"V155: {len(violations)} RC decision-chain violation(s)",
        }
    return {
        "validator": name,
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": "V155: all RC files have valid decision chains",
    }


# ── V156 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V156", domain="governance", description=(
    "governance-counter-report.yaml must be < 14 days old when PRODUCT_SOURCE items "
    "are present (WARN-only)"
))
def validate_governance_counter_report_fresh(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V156 (CT-GOV-002): reports/product-governance/governance-counter-report.yaml
    freshness check. Returns WARN when report is stale or missing with PRODUCT_SOURCE items.

    blocks_sprint=False (advisory).
    """
    name = "validate_governance_counter_report_fresh"
    _root = repo_root or _REPO_ROOT

    items = declaration.get("planned_work_items", [])
    has_product_source = any(
        isinstance(i, dict) and i.get("item_type", "").upper() == "PRODUCT_SOURCE"
        for i in items
    )
    if not has_product_source:
        return {
            "validator": name,
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": "V156: no PRODUCT_SOURCE items — counter-report freshness skipped",
        }

    report_path = _root / "reports" / "product-governance" / "governance-counter-report.yaml"
    if not report_path.exists():
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V156: governance-counter-report.yaml not found — create before product deepening",
        }

    try:
        mtime = datetime.fromtimestamp(report_path.stat().st_mtime, tz=timezone.utc)
        age = datetime.now(timezone.utc) - mtime
        if age > timedelta(days=14):
            return {
                "validator": name,
                "result": "WARN",
                "blocks_sprint": False,
                "items": [f"age={age.days}d (threshold: 14d)"],
                "summary": f"V156: governance-counter-report.yaml is {age.days} days old (>14d threshold)",
            }
        return {
            "validator": name,
            "result": "PASS",
            "blocks_sprint": False,
            "items": [],
            "summary": f"V156: governance-counter-report.yaml is {age.days}d old — fresh",
        }
    except Exception as exc:
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [str(exc)],
            "summary": "V156: could not check governance-counter-report.yaml age",
        }


# ── V157 ─────────────────────────────────────────────────────────────────────


@validator(rule_id="V157", domain="governance", description=(
    "registry/governance-binding.yaml must exist and all listed paths must resolve "
    "(WARN when absent, FAIL when present but paths missing)"
))
def validate_governance_binding_paths(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V157 (CT-GOV-002): registry/governance-binding.yaml path resolution check.

    Returns WARN when governance-binding.yaml is absent (governance not yet set up).
    Returns FAIL (blocks_sprint=True) when governance-binding.yaml exists but one or
    more listed governance_files paths do not exist on disk.
    """
    name = "validate_governance_binding_paths"
    _root = repo_root or _REPO_ROOT
    binding_path = _root / "registry" / "governance-binding.yaml"

    if not binding_path.exists():
        return {
            "validator": name,
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V157: registry/governance-binding.yaml not found — governance binding not set up",
        }

    binding_data = _load_yaml_safe(binding_path)
    if not isinstance(binding_data, dict):
        return {
            "validator": name,
            "result": "FAIL",
            "blocks_sprint": True,
            "items": ["governance-binding.yaml is not a valid YAML mapping"],
            "summary": "V157: governance-binding.yaml malformed (not a mapping)",
        }

    governance_files = binding_data.get("governance_files", [])
    missing = []
    for entry in governance_files:
        if not isinstance(entry, dict):
            continue
        path_str = entry.get("path", "")
        if path_str and not (_root / path_str).exists():
            missing.append(path_str)

    if missing:
        return {
            "validator": name,
            "result": "FAIL",
            "blocks_sprint": True,
            "items": missing,
            "summary": (
                f"V157: {len(missing)} governance_files path(s) in governance-binding.yaml "
                "do not exist on disk"
            ),
        }
    return {
        "validator": name,
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V157: all {len(governance_files)} governance_files paths resolve correctly",
    }
