"""Tests for governance_validators_product_gov.py (V150-V151, V154-V157).

CT-GOV-002 (memoized-frolicking-donut TC-GOV-015, 2026-07-14).

Coverage:
  V150 — validate_governed_artifact_pre_flight
  V151 — validate_change_proposal_coverage
  V154 — validate_impact_analysis_on_accepted_proposals
  V155 — validate_release_candidate_decision_chain
  V156 — validate_governance_counter_report_fresh
  V157 — validate_governance_binding_paths
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators_product_gov import (
    validate_change_proposal_coverage,
    validate_governance_binding_paths,
    validate_governance_counter_report_fresh,
    validate_governed_artifact_pre_flight,
    validate_impact_analysis_on_accepted_proposals,
    validate_release_candidate_decision_chain,
)

_EMPTY_DECL: dict = {}


# ────────────────────────────────────────────────────────────────────────────
# V150 — validate_governed_artifact_pre_flight
# ────────────────────────────────────────────────────────────────────────────


class TestV150GovernedArtifactPreFlight:

    def test_warn_when_cp_dir_absent(self, tmp_path):
        """WARN when registry/change-proposals/ does not exist."""
        result = validate_governed_artifact_pre_flight(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert "absent" in result["summary"]

    def test_warn_when_promoted_registry_absent(self, tmp_path):
        """WARN when promoted-stable-registry.yaml is missing."""
        (tmp_path / "registry" / "change-proposals").mkdir(parents=True)
        result = validate_governed_artifact_pre_flight(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert "promoted-stable-registry.yaml" in result["summary"]

    def test_pass_when_no_promoted_files_changed(self, tmp_path):
        """PASS when changed_files has no PROMOTED_STABLE entries."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        cp_dir.mkdir(parents=True)
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        preg.write_text(yaml.dump({"promoted_paths": ["src/python/csv/csv_codec.py"]}))

        decl = {"changed_files": ["src/python/tsv/tsv_codec.py"]}
        result = validate_governed_artifact_pre_flight(decl, tmp_path)
        assert result["result"] in ("PASS", "WARN")
        assert result["blocks_sprint"] is False

    def test_pass_when_promoted_file_covered_by_accepted_cp(self, tmp_path):
        """PASS when a PROMOTED_STABLE file is covered by an ACCEPTED CP."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        cp_dir.mkdir(parents=True)
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        promoted_path = "src/python/csv/csv_codec.py"
        preg.write_text(yaml.dump({"promoted_paths": [promoted_path]}))

        cp_data = {"status": "ACCEPTED", "affected_paths": [promoted_path]}
        (cp_dir / "CP-001.yaml").write_text(yaml.dump(cp_data))

        decl = {"changed_files": [promoted_path]}
        result = validate_governed_artifact_pre_flight(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_fail_when_promoted_file_uncovered(self, tmp_path):
        """FAIL (blocks_sprint=True) when promoted file changed without accepted CP."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        cp_dir.mkdir(parents=True)
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        promoted_path = "src/python/csv/csv_codec.py"
        preg.write_text(yaml.dump({"promoted_paths": [promoted_path]}))

        # No CP or only DRAFT CP
        cp_data = {"status": "DRAFT", "affected_paths": [promoted_path]}
        (cp_dir / "CP-001.yaml").write_text(yaml.dump(cp_data))

        decl = {"changed_files": [promoted_path]}
        result = validate_governed_artifact_pre_flight(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert promoted_path in result["items"]


# ────────────────────────────────────────────────────────────────────────────
# V151 — validate_change_proposal_coverage
# ────────────────────────────────────────────────────────────────────────────


class TestV151ChangeProposalCoverage:

    def test_warn_when_promoted_registry_absent(self, tmp_path):
        """WARN (advisory) when promoted-stable-registry.yaml is absent."""
        result = validate_change_proposal_coverage(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_when_no_promoted_paths_in_evidence(self, tmp_path):
        """PASS when no planned_work_items reference promoted paths."""
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        preg.parent.mkdir(parents=True, exist_ok=True)
        preg.write_text(yaml.dump({"promoted_paths": ["src/python/csv/csv_codec.py"]}))

        decl = {
            "planned_work_items": [
                {
                    "item_id": "ITEM-001",
                    "evidence_paths": ["src/python/tsv/tsv_codec.py"],
                }
            ]
        }
        result = validate_change_proposal_coverage(decl, tmp_path)
        assert result["result"] == "PASS"

    def test_warn_when_promoted_path_missing_cp_ref(self, tmp_path):
        """WARN when a work item references a promoted path but lacks cp_ref."""
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        preg.parent.mkdir(parents=True, exist_ok=True)
        promoted_path = "src/python/csv/csv_codec.py"
        preg.write_text(yaml.dump({"promoted_paths": [promoted_path]}))

        decl = {
            "planned_work_items": [
                {
                    "item_id": "ITEM-001",
                    "evidence_paths": [promoted_path],
                    # no cp_ref field
                }
            ]
        }
        result = validate_change_proposal_coverage(decl, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert "ITEM-001" in result["items"]

    def test_pass_when_cp_ref_present(self, tmp_path):
        """PASS when promoted-path work item declares cp_ref."""
        preg = tmp_path / "registry" / "promoted-stable-registry.yaml"
        preg.parent.mkdir(parents=True, exist_ok=True)
        promoted_path = "src/python/csv/csv_codec.py"
        preg.write_text(yaml.dump({"promoted_paths": [promoted_path]}))

        decl = {
            "planned_work_items": [
                {
                    "item_id": "ITEM-001",
                    "evidence_paths": [promoted_path],
                    "cp_ref": "CP-001",
                }
            ]
        }
        result = validate_change_proposal_coverage(decl, tmp_path)
        assert result["result"] == "PASS"


# ────────────────────────────────────────────────────────────────────────────
# V154 — validate_impact_analysis_on_accepted_proposals
# ────────────────────────────────────────────────────────────────────────────


class TestV154ImpactAnalysis:

    def test_warn_when_directories_absent(self, tmp_path):
        """WARN when change-proposals or impact-analyses directories absent."""
        result = validate_impact_analysis_on_accepted_proposals(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_when_no_accepted_cps(self, tmp_path):
        """PASS when directories exist but no ACCEPTED CP-* present."""
        (tmp_path / "registry" / "change-proposals").mkdir(parents=True)
        (tmp_path / "registry" / "impact-analyses").mkdir(parents=True)
        (tmp_path / "registry" / "change-proposals" / "CP-001.yaml").write_text(
            yaml.dump({"status": "DRAFT"})
        )
        result = validate_impact_analysis_on_accepted_proposals(_EMPTY_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_accepted_cp_has_ci(self, tmp_path):
        """PASS when each ACCEPTED CP-* has a matching CI-*."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        ci_dir = tmp_path / "registry" / "impact-analyses"
        cp_dir.mkdir(parents=True)
        ci_dir.mkdir(parents=True)
        (cp_dir / "CP-001.yaml").write_text(yaml.dump({"status": "ACCEPTED"}))
        (ci_dir / "CI-001.yaml").write_text(yaml.dump({"status": "COMPLETE"}))

        result = validate_impact_analysis_on_accepted_proposals(_EMPTY_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_fail_when_accepted_cp_missing_ci(self, tmp_path):
        """FAIL (blocks_sprint=True) when ACCEPTED CP-* has no matching CI-*."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        ci_dir = tmp_path / "registry" / "impact-analyses"
        cp_dir.mkdir(parents=True)
        ci_dir.mkdir(parents=True)
        (cp_dir / "CP-001.yaml").write_text(yaml.dump({"status": "ACCEPTED"}))
        # CI-001.yaml intentionally absent

        result = validate_impact_analysis_on_accepted_proposals(_EMPTY_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("CP-001" in item for item in result["items"])


# ────────────────────────────────────────────────────────────────────────────
# V155 — validate_release_candidate_decision_chain
# ────────────────────────────────────────────────────────────────────────────


class TestV155ReleaseCandidate:

    def test_warn_when_rc_dir_absent(self, tmp_path):
        """WARN when registry/release-candidates/ is absent."""
        result = validate_release_candidate_decision_chain(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_when_rc_has_accept_decision(self, tmp_path):
        """PASS when RC file has final_decision=ACCEPT."""
        rc_dir = tmp_path / "registry" / "release-candidates"
        rc_dir.mkdir(parents=True)
        (rc_dir / "RC-001.yaml").write_text(
            yaml.dump({"final_decision": "ACCEPT", "included_changes": []})
        )
        result = validate_release_candidate_decision_chain(_EMPTY_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_fail_when_rc_has_reject_decision(self, tmp_path):
        """FAIL when RC file has final_decision != ACCEPT."""
        rc_dir = tmp_path / "registry" / "release-candidates"
        rc_dir.mkdir(parents=True)
        (rc_dir / "RC-001.yaml").write_text(
            yaml.dump({"final_decision": "REJECT", "included_changes": []})
        )
        result = validate_release_candidate_decision_chain(_EMPTY_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("RC-001" in item for item in result["items"])

    def test_fail_when_rc_references_non_accepted_cp(self, tmp_path):
        """FAIL when RC includes_changes references a CP that is not ACCEPTED."""
        cp_dir = tmp_path / "registry" / "change-proposals"
        rc_dir = tmp_path / "registry" / "release-candidates"
        cp_dir.mkdir(parents=True)
        rc_dir.mkdir(parents=True)
        (cp_dir / "CP-001.yaml").write_text(yaml.dump({"status": "DRAFT"}))
        (rc_dir / "RC-001.yaml").write_text(
            yaml.dump({"final_decision": "ACCEPT", "included_changes": ["CP-001"]})
        )
        result = validate_release_candidate_decision_chain(_EMPTY_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert any("CP-001" in item for item in result["items"])


# ────────────────────────────────────────────────────────────────────────────
# V156 — validate_governance_counter_report_fresh
# ────────────────────────────────────────────────────────────────────────────


class TestV156CounterReportFresh:

    def _product_source_decl(self) -> dict:
        return {
            "planned_work_items": [{"item_id": "X", "item_type": "PRODUCT_SOURCE"}]
        }

    def test_pass_when_no_product_source_items(self, tmp_path):
        """PASS when no PRODUCT_SOURCE work items present."""
        result = validate_governance_counter_report_fresh(_EMPTY_DECL, tmp_path)
        assert result["result"] == "PASS"

    def test_warn_when_report_missing_but_product_source_present(self, tmp_path):
        """WARN when PRODUCT_SOURCE present but counter-report file absent."""
        decl = self._product_source_decl()
        result = validate_governance_counter_report_fresh(decl, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_when_report_is_fresh(self, tmp_path):
        """PASS when governance-counter-report.yaml was modified recently."""
        report_dir = tmp_path / "reports" / "product-governance"
        report_dir.mkdir(parents=True)
        report = report_dir / "governance-counter-report.yaml"
        report.write_text("generated_at: today")
        # file mtime defaults to now — should be fresh

        decl = self._product_source_decl()
        result = validate_governance_counter_report_fresh(decl, tmp_path)
        assert result["result"] == "PASS"

    def test_warn_when_report_is_stale(self, tmp_path, monkeypatch):
        """WARN when governance-counter-report.yaml is older than 14 days."""
        report_dir = tmp_path / "reports" / "product-governance"
        report_dir.mkdir(parents=True)
        report = report_dir / "governance-counter-report.yaml"
        report.write_text("generated_at: old")

        # Mock datetime.now() to return 15 days in the future
        import governance_validators_product_gov as mod
        real_datetime = mod.datetime

        class _FutureDatetime(real_datetime):
            @classmethod
            def now(cls, tz=None):
                return real_datetime.now(tz=tz) + timedelta(days=15)

        monkeypatch.setattr(mod, "datetime", _FutureDatetime)

        decl = self._product_source_decl()
        result = validate_governance_counter_report_fresh(decl, tmp_path)
        assert result["result"] == "WARN"
        assert "15" in result["summary"] or "15" in str(result["items"])


# ────────────────────────────────────────────────────────────────────────────
# V157 — validate_governance_binding_paths
# ────────────────────────────────────────────────────────────────────────────


class TestV157GovernanceBindingPaths:

    def test_warn_when_binding_file_absent(self, tmp_path):
        """WARN when registry/governance-binding.yaml is absent."""
        result = validate_governance_binding_paths(_EMPTY_DECL, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_pass_when_all_binding_paths_exist(self, tmp_path):
        """PASS when all governance_files paths in binding file resolve on disk."""
        (tmp_path / "registry").mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("agents")
        (tmp_path / "CLAUDE.md").write_text("claude")

        binding = {
            "governance_files": [
                {"path": "AGENTS.md", "role": "policy"},
                {"path": "CLAUDE.md", "role": "instructions"},
            ]
        }
        (tmp_path / "registry" / "governance-binding.yaml").write_text(yaml.dump(binding))

        result = validate_governance_binding_paths(_EMPTY_DECL, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_fail_when_binding_path_missing(self, tmp_path):
        """FAIL (blocks_sprint=True) when a governance_files path is missing on disk."""
        (tmp_path / "registry").mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("agents")

        binding = {
            "governance_files": [
                {"path": "AGENTS.md", "role": "policy"},
                {"path": "MISSING_FILE.md", "role": "orphaned"},
            ]
        }
        (tmp_path / "registry" / "governance-binding.yaml").write_text(yaml.dump(binding))

        result = validate_governance_binding_paths(_EMPTY_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert "MISSING_FILE.md" in result["items"]

    def test_fail_when_binding_yaml_malformed(self, tmp_path):
        """FAIL when governance-binding.yaml is not a valid mapping."""
        (tmp_path / "registry").mkdir(parents=True)
        (tmp_path / "registry" / "governance-binding.yaml").write_text("- item1\n- item2\n")

        result = validate_governance_binding_paths(_EMPTY_DECL, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_pass_against_real_repo_binding(self):
        """PASS when run against the actual repository's governance-binding.yaml."""
        result = validate_governance_binding_paths(_EMPTY_DECL, REPO_ROOT)
        assert result["result"] == "PASS", (
            f"Real governance-binding.yaml has missing paths: {result['items']}"
        )


# ────────────────────────────────────────────────────────────────────────────
# Runner integration: count check
# ────────────────────────────────────────────────────────────────────────────


class TestRunnerIntegration:

    def test_expected_validator_count_is_221(self):
        """_EXPECTED_VALIDATOR_COUNT must be 221 (216 base + V172-V175 TC-VWR-007 + V224 TC-GOV-V224-001, 2026-07-15)."""
        from governance_validator_runner import _EXPECTED_VALIDATOR_COUNT
        assert _EXPECTED_VALIDATOR_COUNT == 221, (
            f"Expected 221, got {_EXPECTED_VALIDATOR_COUNT}. "
            "Update governance_validator_runner.py after adding/removing validators."
        )

    def test_product_gov_validators_registered(self):
        """All 6 product-gov validators are registered in _VALIDATOR_REGISTRY."""
        from governance_validators_contract import _VALIDATOR_REGISTRY
        # Import triggers registration
        import governance_validators_product_gov  # noqa: F401

        registered_ids = {e.get("rule_id") for e in _VALIDATOR_REGISTRY}
        for vid in ("V150", "V151", "V154", "V155", "V156", "V157"):
            assert vid in registered_ids, f"{vid} not found in _VALIDATOR_REGISTRY"

    def test_runner_includes_product_gov_validators(self):
        """governance_validator_runner.run_all_governance_validators includes all 6 new validators."""
        from governance_validator_runner import run_all_governance_validators
        decl = {"changed_files": [], "planned_work_items": [], "declared_scope": "test"}
        summary = run_all_governance_validators(decl, repo_root=REPO_ROOT)
        all_validators = {r.get("validator", "") for r in summary.get("validators", [])}
        expected = {
            "validate_governed_artifact_pre_flight",
            "validate_change_proposal_coverage",
            "validate_impact_analysis_on_accepted_proposals",
            "validate_release_candidate_decision_chain",
            "validate_governance_counter_report_fresh",
            "validate_governance_binding_paths",
        }
        missing = expected - all_validators
        assert not missing, f"Missing validators in runner output: {missing}"
