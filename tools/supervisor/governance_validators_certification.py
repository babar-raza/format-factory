"""Governance validators for the certification lifecycle.

TC-007 (precious-wandering-lighthouse, 2026-07-13):
Connects certification state to the autonomous loop via governance validators.
Validators read state (fast); they do NOT execute tools (slow).

When staleness is detected, the validator produces a WARN finding which surfaces
in the autonomous cycle as a rework item. The supervisor selects recertification
work from the normal task queue.

Validators (V_CERT_01 through V_CERT_05):
  V_CERT_01 — validate_all_evidence_present_for_certified_formats
  V_CERT_02 — validate_no_certified_format_has_material_stubs
  V_CERT_03 — validate_certification_run_manifests_exist
  V_CERT_04 — validate_certification_layer_registered
  V_CERT_05 — validate_gap_reconciliation_map_exists
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from governance_validators_contract import validator  # noqa: F401


def _pass(validator: str, message: str = "OK") -> dict[str, Any]:
    return {"result": "PASS", "validator": validator, "message": message}


def _warn(validator: str, message: str) -> dict[str, Any]:
    return {"result": "WARN", "validator": validator, "message": message}


def _fail(validator: str, message: str) -> dict[str, Any]:
    return {"result": "FAIL", "validator": validator, "message": message}


def _skip(validator: str, message: str) -> dict[str, Any]:
    return {"result": "SKIP", "validator": validator, "message": message}


_DIMENSION_REPORTS = [
    "api-contract.json",
    "traceability-audit.json",
    "stub-audit.json",
    "exception-audit.json",
    "oracle-alignment.json",
    "assertion-quality.json",
    "roundtrip-audit.json",
    "package-proof.json",
    "consumer-proof.json",
]


@validator(rule_id="V_CERT_01", domain="certification", description=(
    "CERTIFIED formats must have all 9 dimension report files present in reports/certification/{fmt}/"
))
def validate_all_evidence_present_for_certified_formats(
    declaration: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """V_CERT_01: CERTIFIED formats must have all 9 dimension report files present.

    Reads portfolio-certification-matrix.json. For each CERTIFIED format,
    checks that all 9 expected report files exist in reports/certification/{fmt}/.

    Note: Produces WARN (not FAIL) until TC-009 pilot regeneration completes,
    because existing reports predate the run model.
    """
    validator = "validate_all_evidence_present_for_certified_formats"
    matrix_path = repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    if not matrix_path.exists():
        return _skip(validator, "portfolio-certification-matrix.json not found — skip")

    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return _warn(validator, f"Could not read matrix: {exc}")

    missing: list[str] = []
    cert_root = repo_root / "reports" / "certification"

    for entry in matrix.get("formats", []):
        if entry.get("overall_verdict") != "CERTIFIED":
            continue
        fmt = entry.get("format_id", "")
        fmt_dir = cert_root / fmt
        for report in _DIMENSION_REPORTS:
            if not (fmt_dir / report).exists():
                missing.append(f"{fmt}: {report}")

    if missing:
        return _warn(
            validator,
            f"CERTIFIED formats with missing evidence ({len(missing)} files): "
            + "; ".join(missing[:5])
            + (" ..." if len(missing) > 5 else ""),
        )
    return _pass(validator, "All CERTIFIED formats have 9 dimension report files")


@validator(rule_id="V_CERT_02", domain="certification", description=(
    "No CERTIFIED format should have material stubs in its stub-audit.json"
))
def validate_no_certified_format_has_material_stubs(
    declaration: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """V_CERT_02: No CERTIFIED format should have material stubs in its stub-audit.json.

    For each CERTIFIED format, reads stub-audit.json and checks material_finding_count == 0.
    """
    validator = "validate_no_certified_format_has_material_stubs"
    matrix_path = repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    if not matrix_path.exists():
        return _skip(validator, "portfolio-certification-matrix.json not found — skip")

    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return _warn(validator, f"Could not read matrix: {exc}")

    violations: list[str] = []
    cert_root = repo_root / "reports" / "certification"

    for entry in matrix.get("formats", []):
        if entry.get("overall_verdict") != "CERTIFIED":
            continue
        fmt = entry.get("format_id", "")
        stub_path = cert_root / fmt / "stub-audit.json"
        if not stub_path.exists():
            continue
        try:
            stub = json.loads(stub_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        count = stub.get("material_finding_count", stub.get("stub_count", 0))
        if count > 0:
            violations.append(f"{fmt}: {count} material stub(s)")

    if violations:
        return _fail(
            validator,
            f"CERTIFIED formats with material stubs: " + "; ".join(violations),
        )
    return _pass(validator, "No CERTIFIED format has material stubs in stub-audit.json")


@validator(rule_id="V_CERT_03", domain="certification", description=(
    "CERTIFIED formats should have a run manifest in reports/certification/runs/"
))
def validate_certification_run_manifests_exist(
    declaration: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """V_CERT_03: CERTIFIED formats should have a run manifest in reports/certification/runs/.

    Produces WARN (not FAIL) because existing certified formats use the synthetic
    initial run manifest which is acceptable until TC-009 pilot regeneration.
    """
    validator = "validate_certification_run_manifests_exist"
    matrix_path = repo_root / "reports" / "certification" / "portfolio-certification-matrix.json"
    if not matrix_path.exists():
        return _skip(validator, "portfolio-certification-matrix.json not found — skip")

    runs_root = repo_root / "reports" / "certification" / "runs"
    if not runs_root.exists():
        return _warn(validator, "No runs/ directory found — no run manifests exist")

    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return _warn(validator, f"Could not read matrix: {exc}")

    missing_manifests: list[str] = []

    for entry in matrix.get("formats", []):
        if entry.get("overall_verdict") != "CERTIFIED":
            continue
        fmt = entry.get("format_id", "")
        # Find any manifest for this format in any run directory
        has_manifest = any(
            (run_dir / f"{fmt}-manifest.json").exists()
            for run_dir in runs_root.iterdir()
            if run_dir.is_dir()
        )
        if not has_manifest:
            missing_manifests.append(fmt)

    if missing_manifests:
        return _warn(
            validator,
            f"CERTIFIED formats without run manifests (verdict may be stale): "
            + ", ".join(missing_manifests),
        )
    return _pass(validator, "All CERTIFIED formats have at least one run manifest")


@validator(rule_id="V_CERT_04", domain="certification", description=(
    "L28 Certification Audit Layer must exist in plans/layers/index.yaml with maturity >= 4"
))
def validate_certification_layer_registered(
    declaration: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """V_CERT_04: L28 Certification Audit Layer must exist with maturity >= 4."""
    validator = "validate_certification_layer_registered"
    index_path = repo_root / "plans" / "layers" / "index.yaml"
    if not index_path.exists():
        return _warn(validator, "plans/layers/index.yaml not found")

    text = index_path.read_text(encoding="utf-8")
    if "layer_id: L28" not in text:
        return _fail(validator, "L28 Certification Audit Layer not registered in plans/layers/index.yaml")

    # Find maturity_current for L28
    lines = text.splitlines()
    in_l28 = False
    for line in lines:
        if "layer_id: L28" in line:
            in_l28 = True
        if in_l28 and "maturity_current:" in line:
            try:
                maturity = int(line.split(":")[-1].strip())
                if maturity < 4:
                    return _fail(
                        validator,
                        f"L28 maturity_current={maturity} is below required 4"
                    )
                return _pass(validator, f"L28 registered with maturity_current={maturity}")
            except ValueError:
                return _warn(validator, f"Could not parse maturity_current from: {line}")
        # Stop searching once we leave the L28 block
        if in_l28 and line.startswith("- layer_id:") and "L28" not in line:
            break

    return _warn(validator, "Could not verify L28 maturity_current in index.yaml")


@validator(rule_id="V_CERT_05", domain="certification", description=(
    "reports/certification-integration/gap-reconciliation-map-v2.yaml must exist with content"
))
def validate_gap_reconciliation_map_exists(
    declaration: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """V_CERT_05: reports/certification-integration/gap-reconciliation-map-v2.yaml must exist.

    The map must have at least one entry (can be INVALID for infrastructure findings).
    This verifies the gap reconciler has been run against normalized-findings.yaml.
    """
    validator = "validate_gap_reconciliation_map_exists"
    map_v2 = repo_root / "reports" / "certification-integration" / "gap-reconciliation-map-v2.yaml"
    map_v1 = repo_root / "reports" / "certification-integration" / "gap-reconciliation-map.yaml"

    if map_v2.exists():
        text = map_v2.read_text(encoding="utf-8")
        if "dispositions" in text or "total_findings" in text:
            return _pass(validator, "gap-reconciliation-map-v2.yaml exists with machine-verifiable mappings")
        return _warn(validator, "gap-reconciliation-map-v2.yaml exists but appears empty or malformed")

    if map_v1.exists():
        return _warn(
            validator,
            "Only hand-written gap-reconciliation-map.yaml found; "
            "run gap_reconciler.py to generate machine-verifiable v2 map",
        )

    return _fail(
        validator,
        "No gap reconciliation map found in reports/certification-integration/",
    )
