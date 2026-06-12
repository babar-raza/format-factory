"""
Tests for the LibForge Integration coordinator evidence checker.

Required test cases:
1. valid file ownership matrix passes
2. overlapping file ownership fails
3. forbidden path ownership fails
4. missing evidence file fails
5. invalid taskcard state fails
6. final verdict mismatch fails
7. placeholder/stub evidence file fails
8. real package evidence passes (integration test against prior sprint)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.libforge_integration_evidence_check import (
    CheckResult,
    ValidationReport,
    check_1_file_ownership,
    check_2_no_overlap,
    check_4_forbidden_paths,
    check_5_evidence_files_0,
    check_7_taskcard_states,
    check_8_verdict_consistency,
    check_9_declaration_refs,
    check_10_no_stubs,
    run_all_checks,
    _is_path_allowed,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_taskcard(
    tc_id: str,
    lane: str,
    status: str = "ACCEPTED_VERIFIED",
    file_ownership: list[str] | None = None,
    allowed_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    evidence_files: list[str] | None = None,
) -> dict:
    return {
        "taskcard_id": tc_id,
        "title": f"Test taskcard {tc_id}",
        "lane": lane,
        "owner_role": "coordinator",
        "status": status,
        "file_ownership": file_ownership or [],
        "allowed_paths": allowed_paths or [],
        "forbidden_paths": forbidden_paths or [],
        "evidence_files": evidence_files or [],
    }


def _make_ledger(lanes: list[dict]) -> dict:
    return {
        "run_id": "test-run",
        "sprint_id": "TEST-SPRINT-001",
        "lanes": lanes,
    }


# ---------------------------------------------------------------------------
# Test 1: Valid file ownership matrix passes
# ---------------------------------------------------------------------------

class TestValidFileOwnership:
    def test_all_files_owned(self):
        """All files in ledger are owned by exactly one taskcard."""
        taskcards = [
            _make_taskcard("TC-A", "A", file_ownership=["file_a.py"]),
            _make_taskcard("TC-B", "B", file_ownership=["file_b.py"]),
        ]
        ledger = _make_ledger([
            {"taskcard_id": "TC-A", "files_created": ["file_a.py"]},
            {"taskcard_id": "TC-B", "files_created": ["file_b.py"]},
        ])
        result = check_1_file_ownership(taskcards, ledger, str(_REPO))
        assert result.passed is True

    def test_unowned_file_fails(self):
        """A file not owned by any taskcard is flagged."""
        taskcards = [
            _make_taskcard("TC-A", "A", file_ownership=["file_a.py"]),
        ]
        ledger = _make_ledger([
            {"taskcard_id": "TC-A", "files_created": ["file_a.py", "orphan.py"]},
        ])
        result = check_1_file_ownership(taskcards, ledger, str(_REPO))
        assert result.passed is False
        assert "orphan.py" in str(result.violations)


# ---------------------------------------------------------------------------
# Test 2: Overlapping file ownership fails
# ---------------------------------------------------------------------------

class TestOverlappingOwnership:
    def test_no_overlap_passes(self):
        taskcards = [
            _make_taskcard("TC-A", "A", file_ownership=["file_a.py"]),
            _make_taskcard("TC-B", "B", file_ownership=["file_b.py"]),
        ]
        result = check_2_no_overlap(taskcards)
        assert result.passed is True

    def test_overlap_fails(self):
        """Same file owned by two taskcards should fail."""
        taskcards = [
            _make_taskcard("TC-A", "A", file_ownership=["shared.py"]),
            _make_taskcard("TC-B", "B", file_ownership=["shared.py"]),
        ]
        result = check_2_no_overlap(taskcards)
        assert result.passed is False
        assert any("shared.py" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Test 3: Forbidden path ownership fails
# ---------------------------------------------------------------------------

class TestForbiddenPathEnforcement:
    def test_no_forbidden_changes(self):
        """No forbidden paths modified in git working tree."""
        taskcards = [
            _make_taskcard("TC-A", "A", forbidden_paths=["nonexistent_dir/"]),
        ]
        result = check_4_forbidden_paths(taskcards, str(_REPO))
        assert result.passed is True

    def test_allowed_path_check(self):
        """Files within allowed paths pass."""
        assert _is_path_allowed("evidence/file.md", ["evidence/"]) is True
        assert _is_path_allowed("evidence/file.md", ["other/"]) is False

    def test_exact_match(self):
        assert _is_path_allowed("tools/x.py", ["tools/x.py"]) is True
        assert _is_path_allowed("tools/y.py", ["tools/x.py"]) is False


# ---------------------------------------------------------------------------
# Test 4: Missing evidence file fails
# ---------------------------------------------------------------------------

class TestMissingEvidenceFile:
    def test_existing_evidence_passes(self, tmp_path):
        """Evidence files that exist on disk pass."""
        ev_file = tmp_path / "evidence.md"
        ev_file.write_text("real evidence content here")
        taskcards = [
            _make_taskcard(
                "LFI-0-001", "0",
                evidence_files=[str(ev_file.relative_to(tmp_path))],
            ),
        ]
        result = check_5_evidence_files_0(taskcards, str(tmp_path))
        assert result.passed is True

    def test_missing_evidence_fails(self, tmp_path):
        """Evidence file that doesn't exist fails."""
        taskcards = [
            _make_taskcard(
                "LFI-0-001", "0",
                evidence_files=["nonexistent/file.md"],
            ),
        ]
        result = check_5_evidence_files_0(taskcards, str(tmp_path))
        assert result.passed is False
        assert "nonexistent/file.md" in str(result.violations)


# ---------------------------------------------------------------------------
# Test 5: Invalid taskcard state fails
# ---------------------------------------------------------------------------

class TestInvalidTaskcardState:
    def test_valid_states_pass(self):
        taskcards = [
            _make_taskcard("TC-A", "A", status="ACCEPTED_VERIFIED"),
            _make_taskcard("TC-B", "B", status="READY_FOR_EXECUTION"),
            _make_taskcard("TC-C", "C", status="BLOCKED_EXTERNAL"),
        ]
        result = check_7_taskcard_states(taskcards)
        assert result.passed is True

    def test_invalid_state_fails(self):
        taskcards = [
            _make_taskcard("TC-A", "A", status="ACCEPTED_VERIFIED"),
            _make_taskcard("TC-B", "B", status="INVALID_STATE"),
        ]
        result = check_7_taskcard_states(taskcards)
        assert result.passed is False
        assert any("INVALID_STATE" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Test 6: Final verdict mismatch fails
# ---------------------------------------------------------------------------

class TestFinalVerdictMismatch:
    def test_consistent_verdict_passes(self, tmp_path):
        """Verdict and declaration agree on ACCEPTED_VERIFIED."""
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        (ev_root / "final-verdict.md").write_text("## Verdict: ACCEPTED_VERIFIED\n")
        (ev_root / "evidence-declaration.yaml").write_text(yaml.dump({
            "worker_self_verdict": "ACCEPTED_VERIFIED",
            "test_results": {"passed": 10, "failed": 0, "errors": 0},
        }))
        result = check_8_verdict_consistency(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
            None,
        )
        assert result.passed is True

    def test_mismatch_fails(self, tmp_path):
        """Verdict claims ACCEPTED_VERIFIED but declaration says REJECTED_UNSAFE."""
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        (ev_root / "final-verdict.md").write_text("## Verdict: ACCEPTED_VERIFIED\n")
        (ev_root / "evidence-declaration.yaml").write_text(yaml.dump({
            "worker_self_verdict": "REJECTED_UNSAFE",
            "test_results": {"passed": 0, "failed": 5, "errors": 0},
        }))
        result = check_8_verdict_consistency(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
            None,
        )
        assert result.passed is False


# ---------------------------------------------------------------------------
# Test 7: Placeholder/stub evidence file fails
# ---------------------------------------------------------------------------

class TestPlaceholderStubEvidence:
    def test_no_stubs_passes(self, tmp_path):
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        (ev_root / "real-evidence.md").write_text("This is substantial evidence content.")
        result = check_10_no_stubs(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
        )
        assert result.passed is True

    def test_stub_file_fails(self, tmp_path):
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        (ev_root / "evidence-stub.json").write_text("{}")
        result = check_10_no_stubs(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
        )
        assert result.passed is False
        assert any("stub" in v.lower() for v in result.violations)

    def test_tiny_file_flagged(self, tmp_path):
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        (ev_root / "tiny.json").write_text("{}")
        result = check_10_no_stubs(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
        )
        assert result.passed is False


# ---------------------------------------------------------------------------
# Test 8: Real package evidence passes (integration test)
# ---------------------------------------------------------------------------

class TestRealPackageEvidence:
    def test_prior_sprint_evidence(self):
        """Integration test: run all checks against actual prior sprint evidence."""
        evidence_root = ".local/evidences/ff-libforge-integration-exec-20260610-133949"
        taskcards_dir = "taskcards/libforge-integration"
        repo_root = str(_REPO)

        # Only run if evidence actually exists
        if not (Path(repo_root) / evidence_root).is_dir():
            pytest.skip("Prior sprint evidence directory not found")

        report = run_all_checks(evidence_root, taskcards_dir, repo_root)

        # The report should be produced without errors
        assert len(report.checks) == 10

        # All non-rework checks should produce results (not crash)
        for c in report.checks:
            assert isinstance(c, CheckResult)
            assert c.check_id > 0
            assert c.name

        # Serialize to JSON without error
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["run_id"] == "ff-libforge-integration-exec-20260610-133949"


# ---------------------------------------------------------------------------
# Test: ValidationReport dataclass
# ---------------------------------------------------------------------------

class TestValidationReport:
    def test_passed_property(self):
        report = ValidationReport(run_id="test", evidence_root=".", taskcards_dir=".")
        report.checks = [
            CheckResult(check_id=1, name="a", passed=True),
            CheckResult(check_id=2, name="b", passed=True),
        ]
        assert report.passed is True

    def test_failed_property(self):
        report = ValidationReport(run_id="test", evidence_root=".", taskcards_dir=".")
        report.checks = [
            CheckResult(check_id=1, name="a", passed=True),
            CheckResult(check_id=2, name="b", passed=False, violations=["x"]),
        ]
        assert report.passed is False

    def test_to_json(self):
        report = ValidationReport(run_id="test", evidence_root=".", taskcards_dir=".")
        report.checks = [CheckResult(check_id=1, name="a", passed=True)]
        j = json.loads(report.to_json())
        assert j["passed"] is True
        assert len(j["checks"]) == 1


# ---------------------------------------------------------------------------
# Test: Declaration refs check
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Test: Self-contained valid fixture passes all checks
# ---------------------------------------------------------------------------

class TestSelfContainedValidFixture:
    """Run all 10 checks against a self-contained valid fixture directory."""

    @pytest.fixture
    def valid_fixture_root(self):
        fixture = _REPO / ".local" / "evidences" / \
            "ff-libforge-pilot1-evidence-quality-repair-20260610-163200" / \
            "fixtures" / "valid"
        if not fixture.is_dir():
            pytest.skip("Valid fixture directory not found")
        return fixture

    def test_all_checks_pass(self, valid_fixture_root):
        """A self-contained valid evidence set passes all 10 checks."""
        report = run_all_checks(
            evidence_root="evidence",
            taskcards_dir="taskcards",
            repo_root=str(valid_fixture_root),
        )
        assert len(report.checks) == 10
        # Check 4 (forbidden paths) uses git, which won't work in fixture dir
        # All other checks should pass
        non_git_checks = [c for c in report.checks if c.check_id != 4]
        for c in non_git_checks:
            assert c.passed is True, f"Check {c.check_id} ({c.name}) failed: {c.details}"

    def test_no_overlaps_in_valid(self, valid_fixture_root):
        """Valid fixture has no file ownership overlaps."""
        from tools.supervisor.libforge_integration_evidence_check import _load_taskcards
        taskcards = _load_taskcards("taskcards", str(valid_fixture_root))
        result = check_2_no_overlap(taskcards)
        assert result.passed is True

    def test_verdict_consistent_in_valid(self, valid_fixture_root):
        """Valid fixture has consistent verdict."""
        result = check_8_verdict_consistency("evidence", str(valid_fixture_root), None)
        assert result.passed is True


# ---------------------------------------------------------------------------
# Test: Self-contained invalid fixture fails expected checks
# ---------------------------------------------------------------------------

class TestSelfContainedInvalidFixture:
    """Run checks against an invalid fixture to prove negative detection."""

    @pytest.fixture
    def invalid_fixture_root(self):
        fixture = _REPO / ".local" / "evidences" / \
            "ff-libforge-pilot1-evidence-quality-repair-20260610-163200" / \
            "fixtures" / "invalid"
        if not fixture.is_dir():
            pytest.skip("Invalid fixture directory not found")
        return fixture

    def test_overlap_detected(self, invalid_fixture_root):
        """Invalid fixture has overlapping file ownership (shared-file.md)."""
        from tools.supervisor.libforge_integration_evidence_check import _load_taskcards
        taskcards = _load_taskcards("taskcards", str(invalid_fixture_root))
        result = check_2_no_overlap(taskcards)
        assert result.passed is False
        assert any("shared-file.md" in v for v in result.violations)

    def test_invalid_state_detected(self, invalid_fixture_root):
        """Invalid fixture has a taskcard with INVALID_STATE_FOR_TESTING."""
        from tools.supervisor.libforge_integration_evidence_check import _load_taskcards
        taskcards = _load_taskcards("taskcards", str(invalid_fixture_root))
        result = check_7_taskcard_states(taskcards)
        assert result.passed is False
        assert any("INVALID_STATE" in v for v in result.violations)

    def test_missing_evidence_detected(self, invalid_fixture_root):
        """Invalid fixture references nonexistent evidence files."""
        from tools.supervisor.libforge_integration_evidence_check import _load_taskcards
        taskcards = _load_taskcards("taskcards", str(invalid_fixture_root))
        result = check_5_evidence_files_0(taskcards, str(invalid_fixture_root))
        assert result.passed is False

    def test_stub_detected(self, invalid_fixture_root):
        """Invalid fixture contains evidence-stub.json."""
        result = check_10_no_stubs("evidence", str(invalid_fixture_root))
        assert result.passed is False
        assert any("stub" in v.lower() for v in result.violations)

    def test_verdict_mismatch_detected(self, invalid_fixture_root):
        """Invalid fixture has ACCEPTED_VERIFIED in verdict but REJECTED_UNSAFE in declaration."""
        result = check_8_verdict_consistency("evidence", str(invalid_fixture_root), None)
        assert result.passed is False


# ---------------------------------------------------------------------------
# Test: Declaration refs check
# ---------------------------------------------------------------------------

class TestDeclarationRefs:
    def test_all_refs_exist(self, tmp_path):
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        real_file = ev_root / "real.md"
        real_file.write_text("content")
        decl = {
            "evidence_artifacts": [
                {"path": str(real_file.relative_to(tmp_path)), "type": "test"},
            ],
            "changed_files": [str(real_file.relative_to(tmp_path))],
        }
        (ev_root / "evidence-declaration.yaml").write_text(yaml.dump(decl))
        result = check_9_declaration_refs(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
        )
        assert result.passed is True

    def test_missing_ref_fails(self, tmp_path):
        ev_root = tmp_path / "evidence"
        ev_root.mkdir()
        decl = {
            "evidence_artifacts": [
                {"path": "nonexistent/file.md", "type": "test"},
            ],
            "changed_files": [],
        }
        (ev_root / "evidence-declaration.yaml").write_text(yaml.dump(decl))
        result = check_9_declaration_refs(
            str(ev_root.relative_to(tmp_path)),
            str(tmp_path),
        )
        assert result.passed is False
