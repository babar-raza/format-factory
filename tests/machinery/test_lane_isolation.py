"""Tests for lane contract isolation (TC-GFB-024-02, FF-MR-2026-001).

Requirements: REQ-TEST-001 — Lane contracts valid; no overlapping owned paths.

Tests:
1. lane-contracts.yaml is valid (13 lanes, required fields)
2. No two lanes have the exact same path in allowed_paths (owned path isolation)
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LANE_CONTRACTS_PATH = REPO_ROOT / ".governance" / "lanes" / "lane-contracts.yaml"


class TestLaneContractsValid:
    """Lane contracts YAML must be valid and complete."""

    def test_lane_contracts_yaml_exists(self) -> None:
        """lane-contracts.yaml must exist."""
        assert LANE_CONTRACTS_PATH.exists(), (
            f"lane-contracts.yaml not found at {LANE_CONTRACTS_PATH}"
        )

    def test_lane_contracts_has_13_lanes(self) -> None:
        """lane-contracts.yaml must define exactly 13 lanes."""
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        lanes = data.get("lanes", [])
        assert len(lanes) == 13, f"Expected 13 lanes, found {len(lanes)}: {[l['lane_id'] for l in lanes]}"

    def test_all_lanes_have_required_fields(self) -> None:
        """Every lane must have lane_id, allowed_paths, and concurrency."""
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        required = {"lane_id", "allowed_paths", "concurrency"}
        for lane in data.get("lanes", []):
            missing = required - set(lane.keys())
            assert not missing, (
                f"Lane {lane.get('lane_id', '?')} is missing required fields: {missing}"
            )

    def test_all_lanes_have_non_empty_allowed_paths(self) -> None:
        """Every lane must have at least one entry in allowed_paths."""
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        for lane in data.get("lanes", []):
            paths = lane.get("allowed_paths", [])
            assert len(paths) >= 1, (
                f"Lane {lane['lane_id']} has empty allowed_paths"
            )

    def test_all_lane_ids_are_unique(self) -> None:
        """All lane_id values must be unique."""
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        ids = [lane["lane_id"] for lane in data.get("lanes", [])]
        assert len(ids) == len(set(ids)), (
            f"Duplicate lane_ids found: {[x for x in ids if ids.count(x) > 1]}"
        )


class TestLanePathIsolation:
    """No two lanes may claim the exact same primary path (owned path isolation)."""

    def test_primary_source_paths_not_duplicated_across_lanes(self) -> None:
        """Primary source paths (src/python/, src/net/) must each belong to only one lane.

        Shared infrastructure paths (.local/evidences/, oracle/, reports/) are legitimately
        claimed by multiple lanes — they are collaboration zones.
        Only primary product source directories must be exclusively owned.
        """
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        lanes = data.get("lanes", [])

        # These are the exclusively-owned source paths that must not be shared
        exclusive_source_prefixes = ("src/python/", "src/net/", "src/python", "src/net")

        path_to_lanes: dict[str, list[str]] = {}
        for lane in lanes:
            lane_id = lane["lane_id"]
            for path in lane.get("allowed_paths", []):
                if any(path.startswith(p) for p in exclusive_source_prefixes):
                    path_to_lanes.setdefault(path, []).append(lane_id)

        conflicts = {
            path: lane_ids
            for path, lane_ids in path_to_lanes.items()
            if len(lane_ids) > 1
        }

        assert not conflicts, (
            f"Primary source paths owned by multiple lanes (isolation violation):\n"
            + "\n".join(f"  {p}: {ls}" for p, ls in sorted(conflicts.items()))
        )

    def test_coordinator_lane_is_serial(self) -> None:
        """The coordinator lane must be SERIAL (not parallel) to prevent plan lock conflicts."""
        data = yaml.safe_load(LANE_CONTRACTS_PATH.read_text(encoding="utf-8"))
        coordinator = next(
            (l for l in data.get("lanes", []) if l["lane_id"] == "coordinator"), None
        )
        assert coordinator is not None, "coordinator lane must exist"
        concurrency = coordinator.get("concurrency", "")
        assert str(concurrency).upper() == "SERIAL", (
            f"coordinator lane must be SERIAL, got: {concurrency}"
        )
