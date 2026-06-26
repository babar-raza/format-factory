"""Tests for V74 (validate_ledger_continuation_gate) — TC-PDL-005.

Extracted from test_governance_validators.py to keep that file under LOC cap.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestV74LedgerContinuationGate:
    """V74 (TC-PDL-005): Block PRODUCT_SOURCE/PRODUCT_TEST items for blocked formats."""

    @staticmethod
    def _get_validator():
        from governance_validators_ledger import validate_ledger_continuation_gate
        return validate_ledger_continuation_gate

    def _make_ledger(self, tmp_path, entries):
        """Create a minimal product-deepening-ledger.yaml."""
        import yaml
        reg_dir = tmp_path / "registry"
        reg_dir.mkdir(parents=True, exist_ok=True)
        (reg_dir / "product-deepening-ledger.yaml").write_text(
            yaml.dump(entries), encoding="utf-8"
        )

    def test_v74_pass_for_allowed_format(self, tmp_path):
        """PASS when PRODUCT_SOURCE targets a format with continuation_allowed=true."""
        validator = self._get_validator()
        self._make_ledger(tmp_path, [
            {"format": "abw", "continuation_allowed": True, "continuation_reason": "Green"},
            {"format": "ods", "continuation_allowed": False, "continuation_reason": "Gen3"},
        ])
        decl = {"planned_work_items": [{
            "item_id": "PROD-ABW-001", "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/abw/models.py"],
        }]}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v74_fail_for_blocked_format(self, tmp_path):
        """FAIL when PRODUCT_SOURCE targets a format with continuation_allowed=false."""
        validator = self._get_validator()
        self._make_ledger(tmp_path, [
            {"format": "ods", "continuation_allowed": False,
             "continuation_reason": "ODS is Gen3 -- no typed domain model class."},
        ])
        decl = {"planned_work_items": [{
            "item_id": "PROD-ODS-001", "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/ods/codec.py"],
        }]}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("ods" in v["format"] for v in result["items"])

    def test_v74_pass_for_non_product_item_type(self, tmp_path):
        """PASS when a blocked format appears in GOVERNANCE_TASKCARD (not PRODUCT_SOURCE)."""
        validator = self._get_validator()
        self._make_ledger(tmp_path, [
            {"format": "ods", "continuation_allowed": False, "continuation_reason": "Gen3"},
        ])
        decl = {"planned_work_items": [{
            "item_id": "GOV-ODS-001", "item_type": "GOVERNANCE_TASKCARD",
            "evidence_paths": ["src/python/ods/codec.py"],
        }]}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_v74_skip_when_ledger_missing(self, tmp_path):
        """SKIP when product-deepening-ledger.yaml does not exist."""
        validator = self._get_validator()
        decl = {"planned_work_items": []}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "SKIP"
        assert result["blocks_sprint"] is False

    def test_v74_pass_csv_after_correction(self, tmp_path):
        """PASS for CSV after TC-R01 correction (continuation_allowed=true)."""
        validator = self._get_validator()
        self._make_ledger(tmp_path, [
            {"format": "csv", "continuation_allowed": True,
             "continuation_reason": "Gen4 library verified. Ready for product deepening."},
        ])
        decl = {"planned_work_items": [{
            "item_id": "PROD-CSV-001", "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/csv/models.py"],
        }]}
        result = validator(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
