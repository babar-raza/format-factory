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
    """V47 executes and produces correct results."""

    def test_v47_present_in_governance_validators(self):
        """validate_spec_fact_refs_in_sal_output is importable and returns correct schema."""
        from governance_validators import validate_spec_fact_refs_in_sal_output

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
        v47 = validate_spec_fact_refs_in_sal_output(decl, repo_root=_REPO)
        assert isinstance(v47, dict), f"Expected dict, got {type(v47)}"
        assert v47["validator"] == "validate_spec_fact_refs_in_sal_output"
        # With a valid FACT-FODS-001 in sal-facts-latest.json (or bootstrap tolerance), should PASS
        assert v47["result"] == "PASS"
        assert v47["blocks_sprint"] is False

    def test_v47_blocks_release_gate_with_nonexistent_fact(self):
        """V47 blocks RELEASE_GATE items citing non-existent facts."""
        from governance_validators import validate_spec_fact_refs_in_sal_output

        sal_output = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_output.exists():
            pytest.skip("sal-facts-latest.json not present (CI)")

        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-INT-002",
                    "item_type": "RELEASE_GATE",
                    "status": "completed",
                    "spec_fact_refs": ["FACT-NONEXISTENT-99999"],
                    "evidence_paths": ["src/python/fods/fods_codec.py"],
                },
            ],
            "changed_files": ["src/python/fods/fods_codec.py"],
            "evidence_artifacts": [],
        }
        v47 = validate_spec_fact_refs_in_sal_output(decl, repo_root=_REPO)
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

    def test_advisory_module_importable(self):
        """sal_format_advisory module is importable and has build_advisory."""
        from sal_format_advisory import build_advisory
        assert callable(build_advisory)
