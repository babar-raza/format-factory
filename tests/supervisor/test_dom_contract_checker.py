"""Tests for dom_contract_checker.py — TC-DL2-002."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from dom_contract_checker import check_contract

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "reports" / "dual-lane-deepening" / "dom-contracts"


class TestDomContractChecker:

    def test_fods_passes_d2(self):
        """FODS passes D2 contract (has FodsDocument, FodsSheet, FodsCell with spec_qname)."""
        result = check_contract("fods", "D2")
        assert result["passed"] is True
        assert result["level"] == "D2"

    def test_fods_passes_d3(self):
        """FODS passes D3 contract (has iterator, traversal)."""
        result = check_contract("fods", "D3")
        assert result["passed"] is True

    def test_nonexistent_fails_d2(self):
        """Nonexistent format fails D2 contract."""
        result = check_contract("nonexistent_xyz_format", "D2")
        assert result["passed"] is False

    def test_contract_yaml_files_parse(self):
        """Contract YAML files parse correctly."""
        for level in ("d2", "d3", "d4", "d5"):
            path = CONTRACTS_DIR / f"{level}-contract.yaml"
            assert path.exists(), f"Missing contract file: {path}"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert "level" in data
            assert "criteria" in data
            assert len(data["criteria"]) > 0

    def test_d2_criteria_individually_testable(self):
        """Each D2 criterion individually testable against FODS."""
        result = check_contract("fods", "D2")
        for criterion in result["criteria"]:
            assert "id" in criterion
            assert "name" in criterion
            assert "found" in criterion
            assert "evidence" in criterion

    def test_missing_format_handled(self):
        """Missing format handled gracefully."""
        result = check_contract("nonexistent_format_xyz", "D2")
        assert result["passed"] is False
        assert "error" in result

    def test_invalid_level_handled(self):
        """Invalid level handled gracefully."""
        result = check_contract("fods", "D99")
        assert result["passed"] is False
        assert "error" in result

    def test_d5_includes_roundtrip_requirement(self):
        """D5 contract includes roundtrip requirement."""
        result = check_contract("fods", "D5")
        roundtrip = [c for c in result["criteria"] if c["id"] == "D5-C2"]
        assert len(roundtrip) == 1
        assert roundtrip[0]["name"] == "roundtrip_proof"
