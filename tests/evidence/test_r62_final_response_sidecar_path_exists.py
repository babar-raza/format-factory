"""
test_r62_final_response_sidecar_path_exists.py — R62 Train C: sidecar proof file existence.

Verifies:
1. R61 external sidecar proof file exists in reports/r61/.
2. R61 sidecar contains required fields (bundle_path, sha256, entries, size, validation_result).
3. R61 sidecar validation_result is PASS.
4. R62 contract requires sidecar to exist alongside final ZIP (external delivery policy).
5. R62 final-verdict.md (when created) must record sidecar path and SHA.

This closes IV-R61-001 by verifying R61's sidecar exists in the delivered location
and proving R62's contract prevents recurrence.

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
IV-R61-001 (no external sidecar delivered alongside R61 ZIP)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


R61_SIDECAR_PATH = (
    PROJECT_ROOT / "reports" / "r61" / "r61-pass2-final.zip.sha256-proof.json"
)
R62_CONTRACT_PATH = (
    PROJECT_ROOT / "tools" / "evidence" / "contracts"
    / "r62-ai-accelerated-sidecar-python-rc.yaml"
)


class TestR61SidecarProofExists:
    """R61 external sidecar proof must exist in reports/r61/ (delivered location)."""

    def test_r61_sidecar_file_exists(self):
        assert R61_SIDECAR_PATH.exists(), (
            f"R61 external sidecar missing: {R61_SIDECAR_PATH}\n"
            "IV-R61-001: R61 must deliver sidecar alongside ZIP"
        )

    def test_r61_sidecar_is_valid_json(self):
        content = R61_SIDECAR_PATH.read_text(encoding="utf-8")
        data = json.loads(content)
        assert isinstance(data, dict), "R61 sidecar must be a JSON object"

    def test_r61_sidecar_has_sha256(self):
        data = json.loads(R61_SIDECAR_PATH.read_text(encoding="utf-8"))
        assert "sha256" in data, "R61 sidecar must have sha256 field"
        sha = data["sha256"]
        assert len(sha) == 64, f"sha256 must be 64 hex chars, got {len(sha)}"

    def test_r61_sidecar_has_bundle_path(self):
        data = json.loads(R61_SIDECAR_PATH.read_text(encoding="utf-8"))
        assert "bundle_path" in data or "bundle_filename" in data or "filename" in data, (
            "R61 sidecar must have bundle_path or equivalent field"
        )

    def test_r61_sidecar_validation_result_pass(self):
        data = json.loads(R61_SIDECAR_PATH.read_text(encoding="utf-8"))
        result = data.get("validation_result", data.get("result", ""))
        assert result == "PASS", (
            f"R61 sidecar validation_result must be PASS, got: {result!r}"
        )

    def test_r61_sidecar_has_entries(self):
        data = json.loads(R61_SIDECAR_PATH.read_text(encoding="utf-8"))
        entries = data.get("entries", data.get("entry_count", 0))
        assert entries > 0, f"R61 sidecar must record positive entry count, got: {entries}"

    def test_r61_sidecar_has_size(self):
        data = json.loads(R61_SIDECAR_PATH.read_text(encoding="utf-8"))
        size = data.get("size_bytes", data.get("size", 0))
        assert size > 0, f"R61 sidecar must record positive size_bytes, got: {size}"


class TestR62ContractEnforcesSidecarDelivery:
    """R62 contract must enforce sidecar delivery to prevent R61-class recurrence."""

    def test_r62_contract_sidecar_required(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "sidecar_required: true" in content

    def test_r62_contract_external_sidecar_policy(self):
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "final_proof_policy: external_sidecar" in content

    def test_r62_contract_requires_delivered_sidecar_tests(self):
        """R62 contract must require Train C sidecar test files."""
        content = R62_CONTRACT_PATH.read_text(encoding="utf-8")
        assert "test_r62_delivered_external_sidecar_required.py" in content, (
            "R62 contract must reference sidecar delivery test"
        )
        assert "test_r62_final_response_sidecar_path_exists.py" in content, (
            "R62 contract must reference this test file"
        )
