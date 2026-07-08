"""
TC-SAL-ENFORCE-001: Regression tests for V13/V47 enforcement.

Plan: shiny-kindling-cocoa v2.0 / Lane E
Ensures V13 and V47 correctly block invalid inputs after schema normalization.
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUP = str(_REPO / "tools" / "supervisor")
if _SUP not in sys.path:
    sys.path.insert(0, _SUP)

from validate_spec_fact_refs import reset_fact_registry_cache
from governance_validators import validate_spec_fact_refs_wired, validate_spec_fact_refs_in_sal_output


@pytest.fixture(autouse=True)
def reset_cache():
    reset_fact_registry_cache()
    yield
    reset_fact_registry_cache()


class TestV13V47Enforcement:
    def test_v47_blocks_fake_fact_release_gate(self):
        """V47 must block RELEASE_GATE items with non-existent fact IDs."""
        sal_output = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_output.exists():
            pytest.skip("sal-facts-latest.json not present — V47 returns bootstrap tolerance PASS without it")
        decl = {"planned_work_items": [{"item_id": "NEG-001", "item_type": "RELEASE_GATE",
                                 "spec_fact_refs": ["FACT-FAKE-DOES-NOT-EXIST-99999"]}]}
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=_REPO)
        assert result.get("result") not in ("PASS", None), (
            f"V47 must not PASS fake fact ID, got: {result}"
        )
        assert result.get("blocks_sprint", False), "V47 must set blocks_sprint=True for fake fact"

    def test_v13_blocks_empty_refs_no_exception(self):
        """V13 must block PRODUCT_SOURCE with no refs and no exception."""
        decl = {"planned_work_items": [{"item_id": "NEG-002", "item_type": "PRODUCT_SOURCE",
                                 "spec_fact_refs": []}]}
        result = validate_spec_fact_refs_wired(decl, repo_root=_REPO)
        assert result.get("result") in ("BLOCK", "FAIL"), (
            f"V13 must block empty spec_fact_refs without exception, got: {result}"
        )

    def test_v47_passes_product_source_with_bootstrap_fact(self):
        """V47 must pass PRODUCT_SOURCE with a valid bootstrap-quality fact.

        PRODUCT_SOURCE requires quality >= 0 (any level accepted).
        """
        sal_output = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_output.exists():
            pytest.skip("sal-facts-latest.json not present (CI)")
        decl = {"planned_work_items": [{"item_id": "POS-001", "item_type": "PRODUCT_SOURCE",
                                 "spec_fact_refs": ["FACT-FODS-001"]}]}
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=_REPO)
        assert result.get("result") == "PASS", (
            f"V47 must pass valid FACT-FODS-001 for PRODUCT_SOURCE, got: {result}"
        )

    def test_v47_blocks_release_gate_with_fake_fact(self):
        """V47 blocks RELEASE_GATE with non-existent fact ID."""
        sal_output = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_output.exists():
            pytest.skip("sal-facts-latest.json not present (CI)")
        decl = {"planned_work_items": [{"item_id": "NEG-003", "item_type": "RELEASE_GATE",
                                 "spec_fact_refs": ["FACT-NONEXISTENT-99999"]}]}
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=_REPO)
        assert result.get("result") not in ("PASS", None), (
            f"V47 must not PASS nonexistent fact for RELEASE_GATE, got: {result}"
        )

    def test_v13_passes_product_source_with_exception(self):
        """V13 must not block PRODUCT_SOURCE with valid debt exception classification.

        Debt exceptions (no_public_spec_available) return WARN (not blocking),
        not PASS (no debt) — this is correct behavior.
        """
        decl = {"planned_work_items": [{"item_id": "POS-002", "item_type": "PRODUCT_SOURCE",
                                 "spec_fact_refs": [],
                                 "exception_classification": "no_public_spec_available"}]}
        result = validate_spec_fact_refs_wired(decl, repo_root=_REPO)
        # Debt exceptions return WARN (not blocking) — accepted
        assert result.get("result") in ("PASS", "WARN"), (
            f"V13 must not FAIL/BLOCK with valid exception_classification, got: {result}"
        )
        assert not result.get("blocks_sprint", False), (
            "Debt exception must not block sprint"
        )

    def test_wrong_dict_key_does_not_cause_false_pass(self):
        """Using 'work_items' instead of 'planned_work_items' results in empty check, not enforcement.

        This documents the GATE-0 test bug from plan v2.0 analysis:
        The plan used 'work_items' key which caused false PASS results.
        Real declarations use 'planned_work_items'.
        """
        # This test documents that 'work_items' key is silently ignored
        decl_wrong_key = {"work_items": [{"item_id": "WRONG-KEY-001", "item_type": "PRODUCT_SOURCE",
                                           "spec_fact_refs": []}]}
        result = validate_spec_fact_refs_wired(decl_wrong_key, repo_root=_REPO)
        # With wrong key, no items are checked → PASS (0 items)
        # This is expected behavior — real declarations use planned_work_items
        assert result.get("result") == "PASS", (
            "Wrong key 'work_items' skips all items and returns PASS — document this behavior"
        )

    def test_v13_fails_closed_when_module_unavailable(self):
        """V13 must FAIL with blocks_sprint=True when validate_spec_fact_refs is unimportable.

        RC-003 fix: the enforcement gate must fail closed, not degrade silently to WARN.
        Simulates a broken installation where the enforcement module cannot be loaded.
        """
        mod_name = "validate_spec_fact_refs"
        original_mod = sys.modules.get(mod_name)
        # Setting sys.modules[name] = None causes ImportError on 'from name import ...'
        sys.modules[mod_name] = None  # type: ignore[assignment]
        try:
            decl = {"planned_work_items": [{"item_id": "IMPORT-ERR-001",
                                             "item_type": "PRODUCT_SOURCE",
                                             "spec_fact_refs": []}]}
            result = validate_spec_fact_refs_wired(decl, repo_root=_REPO)
            assert result.get("blocks_sprint") is True, (
                f"V13 must set blocks_sprint=True when enforcement module missing, got: {result}"
            )
            assert result.get("result") in ("FAIL", "BLOCK"), (
                f"V13 must return FAIL or BLOCK when module unavailable, got: {result}"
            )
        finally:
            if original_mod is not None:
                sys.modules[mod_name] = original_mod
            else:
                sys.modules.pop(mod_name, None)
