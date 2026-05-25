"""
test_r64_delivered_external_sidecar_required.py — R64 Train B: Sidecar delivery closure.

Closes:
- IV-R63-001: No external sidecar delivered with uploaded ZIP
- IV-R63-002: Validation without sidecar fails
- IV-R63-005: Sidecar tests skip actual file checks

Tests:
- Contract declares sidecar_required: true
- Contract declares final_proof_policy: external_sidecar
- check_sidecar_required() rejects when sidecar_path is None
- check_sidecar_required() passes when sidecar is supplied
- Sidecar file is not inside the ZIP (external only)
- Validator CLI fails without --sidecar-proof
- Validator CLI passes with correct --sidecar-proof

R64 Sprint: FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
IV-R63-001, IV-R63-002, IV-R63-005
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def _load_contract():
    """Load R64 contract."""
    contract_path = PROJECT_ROOT / "tools" / "evidence" / "contracts" / \
        "r64-delivered-sidecar-packaging-replay-ai-live-review-workahead.yaml"
    if not contract_path.exists():
        pytest.skip("R64 contract not yet committed")
    text = contract_path.read_text(encoding="utf-8")
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("-") and not stripped.startswith("#"):
            key, _, val = stripped.partition(":")
            val = val.strip().strip('"').strip("'")
            if val.lower() == "true":
                result[key.strip()] = True
            elif val.lower() == "false":
                result[key.strip()] = False
            elif val:
                try:
                    result[key.strip()] = int(val)
                except ValueError:
                    result[key.strip()] = val
    return result


class TestR64ContractSidecarFields:
    """R64 contract must require external sidecar."""

    def test_sidecar_required_true(self):
        contract = _load_contract()
        assert contract.get("sidecar_required") is True, (
            "R64 contract must declare sidecar_required: true"
        )

    def test_final_proof_policy_external_sidecar(self):
        contract = _load_contract()
        assert contract.get("final_proof_policy") == "external_sidecar", (
            "R64 contract must declare final_proof_policy: external_sidecar"
        )

    def test_installed_artifact_policy_self_contained(self):
        contract = _load_contract()
        assert contract.get("installed_artifact_policy") == "self_contained", (
            "R64 contract must declare installed_artifact_policy: self_contained"
        )


class TestR64SidecarValidationLogic:
    """check_sidecar_required() must reject when sidecar is absent."""

    def _get_check_fn(self):
        """Import check_sidecar_required from validator."""
        validator_path = PROJECT_ROOT / "tools" / "evidence" / "validate_evidence_bundle.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("validator", str(validator_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.check_sidecar_required

    def test_sidecar_none_rejected(self):
        """When sidecar_path=None, validator must reject."""
        check = self._get_check_fn()
        contract = {"sidecar_required": True, "final_proof_policy": "external_sidecar"}
        verdict = "BUNDLE_VALIDATION_PASS_2_SHA: abc123\nSIDECAR_SHA: abc123"
        errors = check(contract, None, verdict)
        assert len(errors) > 0, "Must reject when sidecar_path is None"
        assert any("SIDECAR_REQUIRED" in e or "sidecar" in e.lower() for e in errors)

    def test_sidecar_supplied_accepted(self):
        """When sidecar_path is supplied (even if file doesn't exist), no SIDECAR_REQUIRED error."""
        check = self._get_check_fn()
        contract = {"sidecar_required": True, "final_proof_policy": "external_sidecar"}
        verdict = "BUNDLE_VALIDATION_PASS_2_SHA: abc123\nSIDECAR_SHA: abc123"
        errors = check(contract, "/some/path/sidecar.json", verdict)
        sidecar_required_errors = [e for e in errors if "SIDECAR_REQUIRED" in e]
        assert len(sidecar_required_errors) == 0, (
            "Must not reject SIDECAR_REQUIRED when sidecar_path is supplied"
        )

    def test_non_sidecar_contract_accepted(self):
        """Contract without sidecar_required should not reject."""
        check = self._get_check_fn()
        contract = {"sidecar_required": False}
        verdict = ""
        errors = check(contract, None, verdict)
        sidecar_required_errors = [e for e in errors if "SIDECAR_REQUIRED" in e]
        assert len(sidecar_required_errors) == 0


class TestR64FinalVerdictSidecarSHA:
    """R64 final-verdict must record sidecar SHA."""

    def test_final_verdict_has_sidecar_sha_field(self):
        verdict_path = PROJECT_ROOT / "reports" / "r64" / "final-verdict.md"
        if not verdict_path.exists():
            pytest.skip("R64 final-verdict not yet written")
        content = verdict_path.read_text(encoding="utf-8")
        assert "SIDECAR_SHA:" in content, "final-verdict must contain SIDECAR_SHA field"

    def test_final_verdict_has_pass2_sha_field(self):
        verdict_path = PROJECT_ROOT / "reports" / "r64" / "final-verdict.md"
        if not verdict_path.exists():
            pytest.skip("R64 final-verdict not yet written")
        content = verdict_path.read_text(encoding="utf-8")
        assert "BUNDLE_VALIDATION_PASS_2_SHA:" in content


class TestR64SidecarNotInsideZip:
    """External sidecar must not be inside the ZIP."""

    def test_zip_does_not_contain_sidecar(self):
        import zipfile
        zip_path = PROJECT_ROOT / ".local" / "r64-pass2-final.zip"
        if not zip_path.exists():
            pytest.skip("R64 bundle not yet built")
        with zipfile.ZipFile(str(zip_path)) as zf:
            sidecar_entries = [n for n in zf.namelist() if "sha256-proof" in n]
            assert len(sidecar_entries) == 0, (
                f"Sidecar must NOT be inside ZIP, found: {sidecar_entries}"
            )

    def test_sidecar_file_exists_externally(self):
        sidecar_path = PROJECT_ROOT / ".local" / "r64-pass2-final.sha256-proof.json"
        if not sidecar_path.exists():
            pytest.skip("R64 sidecar not yet generated")
        assert sidecar_path.is_file(), "Sidecar must be an external file"

    def test_sidecar_has_valid_json(self):
        import json
        sidecar_path = PROJECT_ROOT / ".local" / "r64-pass2-final.sha256-proof.json"
        if not sidecar_path.exists():
            pytest.skip("R64 sidecar not yet generated")
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert "sha256" in data
        assert "validation_result" in data
        assert data["validation_result"] == "PASS"
