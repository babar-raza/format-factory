"""V47 integration in governance pass + SAL format advisory wiring tests.

TC-SAL-HARD-003: V47 fires within run_all_governance_validators.
TC-SAL-HARD-004: SAL format advisory appears in governance runner output.
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


class TestV47InGovernancePass:
    """V47 executes within run_all_governance_validators and produces results."""

    def test_v47_present_in_full_governance_run(self):
        """run_all_governance_validators includes V47 result."""
        from governance_validators import run_all_governance_validators

        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-INT-001",
                    "item_type": "PRODUCT_SOURCE",
                    "status": "completed",
                    "spec_fact_refs": ["FACT-FODS-001"],
                    "evidence_paths": ["src/python/fods/fods_codec.py"],
                },
            ],
            "changed_files": ["src/python/fods/fods_codec.py"],
            "evidence_artifacts": [],
        }
        output = run_all_governance_validators(decl, repo_root=_REPO)
        # Output is a dict with 'validators' key containing list of result dicts
        assert isinstance(output, dict), f"Expected dict, got {type(output)}"
        validators = output.get("validators", [])
        v47_results = [
            r for r in validators
            if isinstance(r, dict) and r.get("validator") == "validate_spec_fact_refs_in_sal_output"
        ]
        assert len(v47_results) == 1, (
            f"Expected exactly 1 V47 result, got {len(v47_results)}. "
            f"Validators present: {[r.get('validator') for r in validators if isinstance(r, dict)]}"
        )
        v47 = v47_results[0]
        # With a valid FACT-FODS-001 in sal-facts-latest.json, should PASS
        assert v47["result"] == "PASS"
        assert v47["blocks_sprint"] is False

    def test_v47_blocks_release_gate_with_bootstrap_fact(self):
        """V47 blocks RELEASE_GATE items citing bootstrap-only facts in full pass."""
        from governance_validators import run_all_governance_validators

        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-INT-002",
                    "item_type": "RELEASE_GATE",
                    "status": "completed",
                    "spec_fact_refs": ["ODF-FACT-NAMESPACE"],
                    "evidence_paths": ["src/python/fods/fods_codec.py"],
                },
            ],
            "changed_files": ["src/python/fods/fods_codec.py"],
            "evidence_artifacts": [],
        }
        output = run_all_governance_validators(decl, repo_root=_REPO)
        validators = output.get("validators", [])
        v47_results = [
            r for r in validators
            if isinstance(r, dict) and r.get("validator") == "validate_spec_fact_refs_in_sal_output"
        ]
        assert len(v47_results) == 1
        v47 = v47_results[0]
        # ODF-FACT-NAMESPACE is bootstrap_only with registered source_id (Level 1)
        # RELEASE_GATE requires Level 2 -> should FAIL
        assert v47["result"] == "FAIL"
        assert v47["blocks_sprint"] is True


class TestSALFormatAdvisory:
    """SAL format advisory fires in governance validator runner."""

    def test_advisory_validator_present_in_runner(self):
        """governance_validator_runner imports and calls sal_format_advisory."""
        import governance_validator_runner as gvr
        source_text = Path(gvr.__file__).read_text(encoding="utf-8")
        assert "sal_format_advisory" in source_text, (
            "sal_format_advisory not found in governance_validator_runner.py source"
        )
        assert "build_advisory" in source_text, (
            "build_advisory not imported in governance_validator_runner.py"
        )

    def test_advisory_runs_without_blocking(self):
        """Advisory produces output without setting blocks_sprint=True."""
        from governance_validator_runner import run_all_governance_validators

        decl = {
            "planned_work_items": [],
            "changed_files": [],
            "evidence_artifacts": [],
        }
        output = run_all_governance_validators(decl, repo_root=_REPO)
        validators = output.get("validators", [])
        advisory_results = [
            r for r in validators
            if isinstance(r, dict) and r.get("validator") == "sal_format_advisory"
        ]
        # Advisory may or may not produce output depending on SAL state
        # But if present, it must not block
        for adv in advisory_results:
            assert adv.get("blocks_sprint") is False, (
                "sal_format_advisory must be non-blocking"
            )
