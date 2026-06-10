"""Integration tests for governance validators against real Sprint 1 evidence.

GRH-TC-015 (Lane G): Verify 4 sidecar attribution files exist and pass validator,
run all 10 validators against real governance sprint declaration, confirm no
FAIL results for governance items.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

SPRINT1_DECL = (
    REPO_ROOT / ".local/evidences/governance-repeatability-contracts-001"
    / "evidence-declaration.yaml"
)

SIDECAR_PATHS = {
    "gnumeric": REPO_ROOT / ".local/attribution/gnumeric/gnumeric_codec.py.attribution.yaml",
    "tsv": REPO_ROOT / ".local/attribution/tsv/tsv_parser.py.attribution.yaml",
    "abw": REPO_ROOT / ".local/attribution/abw/abw_codec.py.attribution.yaml",
    "ndjson": REPO_ROOT / ".local/attribution/ndjson/ndjson_codec.py.attribution.yaml",
}

EXPECTED_IDEMPOTENCY_KEYS = {
    "gnumeric": hashlib.sha256(
        b"gnumeric|set_cell_value|set_cell_value|MANUAL|src/python/gnumeric/gnumeric_codec.py"
    ).hexdigest(),
    "tsv": hashlib.sha256(
        b"tsv|get_headers|get_headers|MANUAL|src/python/tsv/tsv_parser.py"
    ).hexdigest(),
    "abw": hashlib.sha256(
        b"abw|get_paragraph|get_paragraph|MANUAL|src/python/abw/abw_codec.py"
    ).hexdigest(),
    "ndjson": hashlib.sha256(
        b"ndjson|export_to_csv|export_to_csv|MANUAL|src/python/ndjson/ndjson_codec.py"
    ).hexdigest(),
}


# ---------------------------------------------------------------------------
# Sidecar file verification tests
# ---------------------------------------------------------------------------

class TestSidecarAttributionFiles:
    """Lane G: Verify all 4 sidecar attribution files exist and are valid."""

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_file_exists(self, format_id):
        path = SIDECAR_PATHS[format_id]
        assert path.exists(), f"Sidecar file missing: {path}"

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_yaml_valid(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), "Sidecar must be a YAML mapping"

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_has_symbols(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "symbols" in data, "Sidecar must have 'symbols' list"
        assert len(data["symbols"]) >= 1

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_execution_method_is_backfilled(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for sym in data.get("symbols", []):
            assert sym.get("execution_method") == "BACKFILLED_LEGACY_EXECUTION", (
                f"{format_id} sidecar symbol {sym.get('name')} has wrong execution_method"
            )

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_claim_classification_is_legacy_backfilled(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for sym in data.get("symbols", []):
            assert sym.get("claim_classification") == "LEGACY_BACKFILLED", (
                f"{format_id} sidecar symbol {sym.get('name')} has wrong claim_classification"
            )

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_idempotency_key_matches_formula(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        expected_key = EXPECTED_IDEMPOTENCY_KEYS[format_id]
        for sym in data.get("symbols", []):
            actual_key = sym.get("idempotency_key", "")
            assert actual_key == expected_key, (
                f"{format_id}/{sym.get('name')}: idempotency_key mismatch\n"
                f"  expected: {expected_key}\n"
                f"  actual:   {actual_key}"
            )

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_idempotency_key_is_64_hex_chars(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for sym in data.get("symbols", []):
            key = sym.get("idempotency_key", "")
            assert len(key) == 64, f"idempotency_key must be 64 hex chars, got {len(key)}"
            assert all(c in "0123456789abcdef" for c in key.lower()), (
                f"idempotency_key must be hex, got: {key[:20]}..."
            )

    @pytest.mark.parametrize("format_id", ["gnumeric", "tsv", "abw", "ndjson"])
    def test_sidecar_may_not_claim_repeatable(self, format_id):
        path = SIDECAR_PATHS[format_id]
        if not path.exists():
            pytest.skip(f"Sidecar not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for sym in data.get("symbols", []):
            assert sym.get("may_claim_repeatable") is False, (
                f"{format_id}/{sym.get('name')} must have may_claim_repeatable=false"
            )
            assert sym.get("may_claim_autonomous") is False, (
                f"{format_id}/{sym.get('name')} must have may_claim_autonomous=false"
            )


# ---------------------------------------------------------------------------
# Replay upgrade taskcards
# ---------------------------------------------------------------------------

class TestReplayUpgradeTaskcards:
    """Verify GR-REPLAY-001..004 exist and reference correct data."""

    @pytest.mark.parametrize("tc_id,format_id,function_name", [
        ("GR-REPLAY-001", "gnumeric", "set_cell_value"),
        ("GR-REPLAY-002", "tsv", "get_headers"),
        ("GR-REPLAY-003", "abw", "get_paragraph"),
        ("GR-REPLAY-004", "ndjson", "export_to_csv"),
    ])
    def test_replay_taskcard_exists(self, tc_id, format_id, function_name):
        path = REPO_ROOT / f"taskcards/governance-repeatability/{tc_id}.yaml"
        assert path.exists(), f"Replay taskcard missing: {path}"

    @pytest.mark.parametrize("tc_id,format_id,function_name", [
        ("GR-REPLAY-001", "gnumeric", "set_cell_value"),
        ("GR-REPLAY-002", "tsv", "get_headers"),
        ("GR-REPLAY-003", "abw", "get_paragraph"),
        ("GR-REPLAY-004", "ndjson", "export_to_csv"),
    ])
    def test_replay_taskcard_yaml_valid(self, tc_id, format_id, function_name):
        path = REPO_ROOT / f"taskcards/governance-repeatability/{tc_id}.yaml"
        if not path.exists():
            pytest.skip(f"Taskcard not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert data.get("id") == tc_id
        assert data.get("format_id") == format_id
        assert data.get("function_name") == function_name

    @pytest.mark.parametrize("tc_id,format_id,function_name", [
        ("GR-REPLAY-001", "gnumeric", "set_cell_value"),
        ("GR-REPLAY-002", "tsv", "get_headers"),
        ("GR-REPLAY-003", "abw", "get_paragraph"),
        ("GR-REPLAY-004", "ndjson", "export_to_csv"),
    ])
    def test_replay_taskcard_target_state(self, tc_id, format_id, function_name):
        path = REPO_ROOT / f"taskcards/governance-repeatability/{tc_id}.yaml"
        if not path.exists():
            pytest.skip(f"Taskcard not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data.get("target_state") == "REPLAY_RECIPE_RECORDED"
        assert data.get("target_claim") == "REPLAYABLE_NOT_YET_REPLAYED"
        assert data.get("current_state") == "BACKFILLED_LEGACY_ACCEPTED"

    @pytest.mark.parametrize("tc_id,format_id,function_name", [
        ("GR-REPLAY-001", "gnumeric", "set_cell_value"),
        ("GR-REPLAY-002", "tsv", "get_headers"),
        ("GR-REPLAY-003", "abw", "get_paragraph"),
        ("GR-REPLAY-004", "ndjson", "export_to_csv"),
    ])
    def test_replay_taskcard_idempotency_key_matches_sidecar(self, tc_id, format_id, function_name):
        """Idempotency key in replay taskcard must match the sidecar attribution."""
        tc_path = REPO_ROOT / f"taskcards/governance-repeatability/{tc_id}.yaml"
        sidecar_path = SIDECAR_PATHS[format_id]
        if not tc_path.exists() or not sidecar_path.exists():
            pytest.skip("File(s) missing")
        with open(tc_path, encoding="utf-8") as f:
            tc = yaml.safe_load(f)
        with open(sidecar_path, encoding="utf-8") as f:
            sidecar = yaml.safe_load(f)
        tc_key = tc.get("idempotency_key", "")
        sidecar_keys = [sym.get("idempotency_key", "") for sym in sidecar.get("symbols", [])]
        assert tc_key in sidecar_keys, (
            f"{tc_id}: idempotency_key {tc_key!r} not found in sidecar keys {sidecar_keys}"
        )


# ---------------------------------------------------------------------------
# Integration: run all 10 validators against Sprint 1 governance declaration
# ---------------------------------------------------------------------------

class TestValidatorsAgainstSprint1Declaration:
    """Run all 10 governance validators against the real Sprint 1 declaration."""

    def _load_declaration(self):
        if not SPRINT1_DECL.exists():
            pytest.skip("Sprint 1 evidence-declaration.yaml not found")
        with open(SPRINT1_DECL, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_sprint1_declaration_loadable(self):
        decl = self._load_declaration()
        assert isinstance(decl, dict)
        assert "planned_work_items" in decl

    def test_all_sprint1_items_are_governance_types(self):
        from governance_validators import GOVERNANCE_ITEM_TYPES
        decl = self._load_declaration()
        items = decl.get("planned_work_items", [])
        assert items, "No planned_work_items in Sprint 1 declaration"
        for item in items:
            item_type = item.get("item_type", "")
            exc_class = item.get("exception_classification", "")
            is_governance = (
                item_type in GOVERNANCE_ITEM_TYPES
                or exc_class in {"investigation_only", "legacy_backfill"}
            )
            assert is_governance, (
                f"Item {item.get('item_id')} has unexpected type {item_type!r}"
            )

    def test_execution_method_validator_no_fail(self):
        from governance_validators import validate_execution_method_required
        decl = self._load_declaration()
        result = validate_execution_method_required(decl)
        assert result["result"] != "FAIL", (
            f"execution_method_required_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_source_diff_validator_no_fail(self):
        from governance_validators import validate_source_diff_required
        decl = self._load_declaration()
        result = validate_source_diff_required(decl)
        assert result["result"] != "FAIL", (
            f"source_diff_required_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_idempotency_key_validator_no_fail(self):
        from governance_validators import validate_idempotency_key_required
        decl = self._load_declaration()
        result = validate_idempotency_key_required(decl)
        assert result["result"] != "FAIL", (
            f"idempotency_key_required_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_replay_recipe_validator_no_fail(self):
        from governance_validators import validate_replay_recipe_required
        decl = self._load_declaration()
        result = validate_replay_recipe_required(decl)
        assert result["result"] != "FAIL", (
            f"replay_recipe_required_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_claim_classification_validator_no_fail(self):
        from governance_validators import validate_claim_classification
        decl = self._load_declaration()
        result = validate_claim_classification(decl)
        assert result["result"] != "FAIL", (
            f"claim_classification_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_manual_ungoverned_validator_no_fail(self):
        from governance_validators import validate_manual_ungoverned_rejection
        decl = self._load_declaration()
        result = validate_manual_ungoverned_rejection(decl)
        assert result["result"] != "FAIL", (
            f"manual_ungoverned_rejection_validator FAIL for Sprint 1: {result['items']}"
        )

    def test_taskcard_state_validator_no_fail(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = self._load_declaration()
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] != "FAIL", (
            f"taskcard_state_transitions_validator FAIL for Sprint 1: {result}"
        )

    def test_run_all_validators_no_blocking_fail(self):
        """No validator should produce blocks_sprint=True for governance sprint."""
        from governance_validators import run_all_governance_validators
        decl = self._load_declaration()
        summary = run_all_governance_validators(decl, REPO_ROOT)
        blocking = [
            v for v in summary.get("validators", [])
            if v.get("blocks_sprint") and v.get("result") == "FAIL"
        ]
        assert not blocking, (
            f"Blocking FAIL validators for Sprint 1: "
            f"{[v['validator'] for v in blocking]}"
        )

    def test_run_all_validators_returns_summary(self):
        from governance_validators import run_all_governance_validators
        decl = self._load_declaration()
        summary = run_all_governance_validators(decl, REPO_ROOT)
        assert "validators" in summary
        assert len(summary["validators"]) == 10
        assert "all_pass" in summary or "overall_result" in summary or "fail_count" in summary
