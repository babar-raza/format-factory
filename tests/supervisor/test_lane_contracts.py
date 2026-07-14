"""Tests for V171 lane contract existence validator (TC-GFB-021, FF-MR-2026-001)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add tools/supervisor to path for direct import
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _validator(declaration: dict, repo_root: Path | None = None) -> dict:
    from governance_validators_ext4 import validate_lane_contract_exists  # noqa: PLC0415
    return validate_lane_contract_exists(declaration, repo_root)


class TestLaneContractsYaml:
    """Tests for the lane-contracts.yaml registry file."""

    def test_lane_contracts_file_exists(self):
        """lane-contracts.yaml must exist after TC-GFB-021."""
        path = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"
        assert path.exists(), f"lane-contracts.yaml not found at {path}"

    def test_lane_contracts_has_13_lanes(self):
        """lane-contracts.yaml must define exactly 13 lanes."""
        import yaml
        path = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        lanes = data.get("lanes", [])
        assert len(lanes) == 13, f"Expected 13 lanes, found {len(lanes)}"

    def test_all_lanes_have_required_fields(self):
        """Every lane entry must have lane_id, allowed_paths, concurrency."""
        import yaml
        path = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        required_fields = {"lane_id", "allowed_paths", "concurrency"}
        for lane in data.get("lanes", []):
            missing = required_fields - set(lane.keys())
            assert not missing, f"Lane {lane.get('lane_id', '?')} missing fields: {missing}"

    def test_all_lanes_have_non_empty_allowed_paths(self):
        """Every lane must declare at least one allowed_paths entry."""
        import yaml
        path = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for lane in data.get("lanes", []):
            paths = lane.get("allowed_paths", [])
            assert len(paths) >= 1, f"Lane {lane['lane_id']} has empty allowed_paths"


class TestV171ValidatorBehavior:
    """Tests for V171 validate_lane_contract_exists function."""

    def test_valid_lane_id_passes(self):
        """A valid lane_id from lane-contracts.yaml must PASS."""
        result = _validator({"lane_id": "coordinator"}, REPO_ROOT)
        assert result["result"] == "PASS", f"Expected PASS, got: {result}"
        assert result["blocks_sprint"] is False

    def test_invalid_lane_id_fails(self):
        """An unregistered lane_id must FAIL and block the sprint."""
        result = _validator({"lane_id": "L99_nonexistent"}, REPO_ROOT)
        assert result["result"] == "FAIL", f"Expected FAIL, got: {result}"
        assert result["blocks_sprint"] is True
        assert "L99_nonexistent" in result["summary"]

    def test_missing_lane_id_passes(self):
        """A declaration without lane_id must PASS (lane_id is optional)."""
        result = _validator({}, REPO_ROOT)
        assert result["result"] == "PASS", f"Expected PASS, got: {result}"
        assert result["blocks_sprint"] is False

    def test_missing_lane_contracts_yaml_warns(self, tmp_path: Path):
        """If lane-contracts.yaml is absent, result must be WARN (non-blocking)."""
        fake_repo = tmp_path
        (fake_repo / ".governance").mkdir()
        # Note: we do NOT create lanes/ subdir to simulate missing file
        result = _validator({"lane_id": "coordinator"}, fake_repo)
        assert result["result"] == "WARN", f"Expected WARN, got: {result}"
        assert result["blocks_sprint"] is False

    def test_all_13_lanes_are_valid(self):
        """All 13 registered lane IDs must pass V171."""
        import yaml
        path = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for lane in data.get("lanes", []):
            lane_id = lane["lane_id"]
            result = _validator({"lane_id": lane_id}, REPO_ROOT)
            assert result["result"] == "PASS", (
                f"Lane {lane_id!r} unexpectedly failed V171: {result}"
            )
