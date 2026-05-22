"""
R47 Lane B: Cross-layer physical invariant tests.

Tests:
1. All physical invariants pass in the current committed repo.
2. Each invariant correctly detects its specific violation condition.

These tests are sprint-agnostic — they test PROJECT-LEVEL invariants, not
sprint-specific conditions. They should pass in perpetuity unless a governance
decision explicitly changes the invariants.
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from check_repo_invariants import (
    check_all_invariants,
    check_inv001_acquisition_pack_coverage,
    check_inv002_state_files_present,
    check_inv003_latest_contract_satisfied,
    check_inv004_no_stale_pending_verdict,
    check_inv005_no_compiled_artifacts_tracked,
)


# ---------------------------------------------------------------------------
# TestCurrentRepoPhysicalConsistency — live repo must pass all invariants
# ---------------------------------------------------------------------------

class TestCurrentRepoPhysicalConsistency:
    """All physical invariants must pass in the currently committed repo."""

    def test_all_invariants_pass(self):
        results = check_all_invariants(REPO_ROOT)
        failed = [r for r in results if not r["passed"]]
        if failed:
            lines = []
            for r in failed:
                lines.append(f"  {r['id']}: {r['name']}")
                for d in r.get("details", []):
                    lines.append(f"    - {d}")
            pytest.fail("Physical invariants FAILED:\n" + "\n".join(lines))

    def test_inv001_passes_in_current_repo(self):
        r = check_inv001_acquisition_pack_coverage(REPO_ROOT)
        assert r["passed"], f"INV-001 failed: {r['details']}"

    def test_inv002_passes_in_current_repo(self):
        r = check_inv002_state_files_present(REPO_ROOT)
        assert r["passed"], f"INV-002 failed: {r['details']}"

    def test_inv003_passes_in_current_repo(self):
        r = check_inv003_latest_contract_satisfied(REPO_ROOT)
        assert r["passed"], f"INV-003 failed: {r['details']}"

    def test_inv004_passes_in_current_repo(self):
        r = check_inv004_no_stale_pending_verdict(REPO_ROOT)
        assert r["passed"], f"INV-004 failed: {r['details']}"

    def test_inv005_passes_in_current_repo(self):
        r = check_inv005_no_compiled_artifacts_tracked(REPO_ROOT)
        assert r["passed"], f"INV-005 failed: {r['details']}"


# ---------------------------------------------------------------------------
# TestInvariantDetection — each invariant must catch its violation
# ---------------------------------------------------------------------------

class TestInvariantDetection:
    """Each invariant must detect its specific failure condition."""

    # --- INV-001 ---

    def test_inv001_detects_missing_pack_yaml(self, tmp_path):
        """Format claiming acquisition_pack_created=true with no pack.yaml triggers INV-001."""
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            "formats:\n  - format_id: fods\n    acquisition_pack_created: true\n",
            encoding="utf-8",
        )
        (tmp_path / "acquisition-packs" / "fods").mkdir(parents=True)
        # Do NOT create pack.yaml
        r = check_inv001_acquisition_pack_coverage(tmp_path)
        assert not r["passed"]
        assert any("MISSING" in d and "fods" in d for d in r["details"])

    def test_inv001_passes_when_pack_yaml_present(self, tmp_path):
        """INV-001 passes when pack.yaml exists for all formats claiming packs."""
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            "formats:\n  - format_id: fods\n    acquisition_pack_created: true\n",
            encoding="utf-8",
        )
        (tmp_path / "acquisition-packs" / "fods").mkdir(parents=True)
        (tmp_path / "acquisition-packs" / "fods" / "pack.yaml").write_text("gate_1: {}\n", encoding="utf-8")
        r = check_inv001_acquisition_pack_coverage(tmp_path)
        assert r["passed"], f"Unexpected failure: {r['details']}"

    def test_inv001_skips_formats_without_acquisition_pack(self, tmp_path):
        """Formats without acquisition_pack_created=true are not checked."""
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            "formats:\n  - format_id: ora\n    acquisition_pack_created: false\n",
            encoding="utf-8",
        )
        r = check_inv001_acquisition_pack_coverage(tmp_path)
        assert r["passed"]

    def test_inv001_fails_when_registry_missing(self, tmp_path):
        """Missing registry file fails INV-001 with a clear message."""
        r = check_inv001_acquisition_pack_coverage(tmp_path)
        assert not r["passed"]
        assert any("format-registry.yaml" in d for d in r["details"])

    # --- INV-002 ---

    def test_inv002_detects_missing_state_md(self, tmp_path):
        """Missing state/current-state.md triggers INV-002."""
        (tmp_path / "state").mkdir()
        (tmp_path / "state" / "current-state.json").write_text("{}", encoding="utf-8")
        r = check_inv002_state_files_present(tmp_path)
        assert not r["passed"]
        assert any("current-state.md" in d for d in r["details"])

    def test_inv002_detects_missing_state_json(self, tmp_path):
        """Missing state/current-state.json triggers INV-002."""
        (tmp_path / "state").mkdir()
        (tmp_path / "state" / "current-state.md").write_text("# ok\n", encoding="utf-8")
        r = check_inv002_state_files_present(tmp_path)
        assert not r["passed"]
        assert any("current-state.json" in d for d in r["details"])

    def test_inv002_detects_empty_state_file(self, tmp_path):
        """Empty state file (0 bytes) triggers INV-002."""
        (tmp_path / "state").mkdir()
        (tmp_path / "state" / "current-state.md").write_text("", encoding="utf-8")
        (tmp_path / "state" / "current-state.json").write_text("{}", encoding="utf-8")
        r = check_inv002_state_files_present(tmp_path)
        assert not r["passed"]
        assert any("EMPTY" in d for d in r["details"])

    def test_inv002_passes_when_both_present_and_nonempty(self, tmp_path):
        (tmp_path / "state").mkdir()
        (tmp_path / "state" / "current-state.md").write_text("# ok\n", encoding="utf-8")
        (tmp_path / "state" / "current-state.json").write_text("{}", encoding="utf-8")
        r = check_inv002_state_files_present(tmp_path)
        assert r["passed"]

    # --- INV-003 ---

    def test_inv003_detects_missing_required_file(self, tmp_path):
        """Missing required_repo_files entry in latest contract triggers INV-003."""
        (tmp_path / "tools" / "evidence" / "contracts").mkdir(parents=True)
        contract = (tmp_path / "tools" / "evidence" / "contracts" / "r47-test.yaml")
        contract.write_text(
            "run_number: R47\nrequired_repo_files:\n  - reports/r47/final-verdict.md\n",
            encoding="utf-8",
        )
        # Do NOT create reports/r47/final-verdict.md
        r = check_inv003_latest_contract_satisfied(tmp_path)
        assert not r["passed"]
        assert any("final-verdict.md" in d for d in r["details"])

    def test_inv003_passes_when_all_required_files_exist(self, tmp_path):
        """INV-003 passes when all required_repo_files exist."""
        (tmp_path / "tools" / "evidence" / "contracts").mkdir(parents=True)
        (tmp_path / "reports" / "r47").mkdir(parents=True)
        (tmp_path / "reports" / "r47" / "final-verdict.md").write_text("ok", encoding="utf-8")
        contract = (tmp_path / "tools" / "evidence" / "contracts" / "r47-test.yaml")
        contract.write_text(
            "run_number: R47\nrequired_repo_files:\n  - reports/r47/final-verdict.md\n",
            encoding="utf-8",
        )
        r = check_inv003_latest_contract_satisfied(tmp_path)
        assert r["passed"], f"Unexpected failure: {r['details']}"

    def test_inv003_detects_duplicate_latest_contracts(self, tmp_path):
        """Two contracts sharing the same highest run_number fail as AMBIGUOUS."""
        cd = tmp_path / "tools" / "evidence" / "contracts"
        cd.mkdir(parents=True)
        (cd / "r47-a.yaml").write_text("run_number: R47\n", encoding="utf-8")
        (cd / "r47-b.yaml").write_text("run_number: R47\n", encoding="utf-8")
        r = check_inv003_latest_contract_satisfied(tmp_path)
        assert not r["passed"]
        assert any("AMBIGUOUS" in d for d in r["details"])

    def test_inv003_skips_non_sprint_contracts(self, tmp_path):
        """Contracts without run_number are ignored by INV-003."""
        cd = tmp_path / "tools" / "evidence" / "contracts"
        cd.mkdir(parents=True)
        # A non-sprint contract (no run_number) with a sprint contract that's satisfied
        (cd / "tc0001-gate1.yaml").write_text("purpose: Gate 1 test contract\n", encoding="utf-8")
        (cd / "r46-sprint.yaml").write_text(
            "run_number: R46\nrequired_repo_files: []\n",
            encoding="utf-8",
        )
        r = check_inv003_latest_contract_satisfied(tmp_path)
        assert r["passed"]

    # --- INV-004 ---

    def test_inv004_detects_standalone_pending_on_complete_verdict(self, tmp_path):
        """Standalone BUNDLE_VALIDATION: PENDING in a COMPLETE verdict fails INV-004."""
        (tmp_path / "reports" / "r40").mkdir(parents=True)
        (tmp_path / "reports" / "r40" / "final-verdict.md").write_text(
            "**VERDICT:** R40_COMPLETE\n\nBUNDLE_VALIDATION: PENDING\n",
            encoding="utf-8",
        )
        r = check_inv004_no_stale_pending_verdict(tmp_path)
        assert not r["passed"]
        assert any("r40" in d for d in r["details"])

    def test_inv004_does_not_flag_historical_prose(self, tmp_path):
        """Historical prose mentioning BUNDLE_VALIDATION: PENDING is not flagged."""
        (tmp_path / "reports" / "r40").mkdir(parents=True)
        (tmp_path / "reports" / "r40" / "final-verdict.md").write_text(
            "**VERDICT:** R40_COMPLETE\n\n"
            "D02 fix: BUNDLE_VALIDATION: PENDING forward-documented in R32 was resolved.\n"
            "Previously had BUNDLE_VALIDATION: PENDING as a description.\n"
            "\nBUNDLE_VALIDATION: PASS\n",
            encoding="utf-8",
        )
        r = check_inv004_no_stale_pending_verdict(tmp_path)
        assert r["passed"], f"False positive detected: {r['details']}"

    def test_inv004_does_not_flag_non_complete_verdicts(self, tmp_path):
        """Verdicts that are not COMPLETE are not scanned (non-complete sprint)."""
        (tmp_path / "reports" / "r41").mkdir(parents=True)
        (tmp_path / "reports" / "r41" / "final-verdict.md").write_text(
            "VERDICT: R41_PROGRESS_ACCEPTED_CLOSEOUT_SUPERSEDED\n\n"
            "BUNDLE_VALIDATION: PENDING\n",
            encoding="utf-8",
        )
        r = check_inv004_no_stale_pending_verdict(tmp_path)
        assert r["passed"], f"Non-COMPLETE verdict should not be scanned: {r['details']}"

    def test_inv004_passes_when_pending_inline_in_list_item(self, tmp_path):
        """List item referencing PENDING (e.g. '- BUNDLE_VALIDATION: PENDING ref') is prose."""
        (tmp_path / "reports" / "r40").mkdir(parents=True)
        (tmp_path / "reports" / "r40" / "final-verdict.md").write_text(
            "VERDICT: R40_COMPLETE\n\n"
            "- BUNDLE_VALIDATION: PENDING was a defect in R39\n"
            "\nBUNDLE_VALIDATION: PASS\n",
            encoding="utf-8",
        )
        r = check_inv004_no_stale_pending_verdict(tmp_path)
        assert r["passed"], f"List item should not trigger: {r['details']}"

    # --- INV-005 ---

    def test_inv005_skips_gracefully_without_git(self, tmp_path):
        """INV-005 returns passed=True with NO_GIT_REPO when .git is absent."""
        # tmp_path has no .git directory
        r = check_inv005_no_compiled_artifacts_tracked(tmp_path)
        assert r["passed"]
        assert any("NO_GIT_REPO" in d for d in r["details"])


# ---------------------------------------------------------------------------
# TestProductionBlockerIntegration — state_snapshot delegates to invariants
# ---------------------------------------------------------------------------

class TestProductionBlockerIntegration:
    """state_snapshot.get_production_blockers() must surface physical failures."""

    def test_production_blockers_no_physical_failures_in_current_repo(self):
        """Current repo must not have physical-invariant blockers."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "state"))
        from state_snapshot import get_production_blockers
        blockers = get_production_blockers()
        # Filter to only physical invariant blockers (INV-00x prefix)
        physical = [b for b in blockers if b.startswith("INV-")]
        assert not physical, (
            f"Physical invariant blockers detected in current repo: {physical}\n"
            "This means required filesystem artifacts are missing."
        )

    def test_production_blockers_detects_missing_pack_yaml(self, tmp_path, monkeypatch):
        """get_production_blockers() returns INV-001 blocker when pack.yaml is missing."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "state"))
        import state_snapshot as ss
        monkeypatch.setattr(ss, "ROOT", tmp_path)

        # Minimal repo structure: registry claims pack, but pack.yaml absent
        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            "formats:\n  - format_id: fods\n    acquisition_pack_created: true\n",
            encoding="utf-8",
        )
        (tmp_path / "acquisition-packs" / "fods").mkdir(parents=True)
        (tmp_path / "state").mkdir()
        (tmp_path / "state" / "current-state.md").write_text("# ok\n", encoding="utf-8")
        (tmp_path / "state" / "current-state.json").write_text("{}", encoding="utf-8")
        (tmp_path / "generated-requirements").mkdir()
        (tmp_path / "tools" / "evidence" / "contracts").mkdir(parents=True)
        (tmp_path / "reports").mkdir()

        blockers = ss.get_production_blockers()
        assert any("INV-001" in b for b in blockers), (
            f"Expected INV-001 blocker for missing pack.yaml, got: {blockers}"
        )

    def test_production_blockers_detects_missing_state_files(self, tmp_path, monkeypatch):
        """get_production_blockers() returns INV-002 blocker when state files missing."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "state"))
        import state_snapshot as ss
        monkeypatch.setattr(ss, "ROOT", tmp_path)

        (tmp_path / "registry").mkdir()
        (tmp_path / "registry" / "format-registry.yaml").write_text(
            "formats: []\n", encoding="utf-8",
        )
        (tmp_path / "generated-requirements").mkdir()
        (tmp_path / "tools" / "evidence" / "contracts").mkdir(parents=True)
        (tmp_path / "reports").mkdir()
        # Do NOT create state/ directory

        blockers = ss.get_production_blockers()
        assert any("INV-002" in b for b in blockers), (
            f"Expected INV-002 blocker for missing state files, got: {blockers}"
        )
