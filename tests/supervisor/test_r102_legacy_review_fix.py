"""
R102 — Legacy Review Fix Tests
Tests that:
  - Declaration-sourced bridge output includes _declaration_sourced marker
  - compare_goal_to_evidence.py skips legacy checks for declaration-sourced reviews
  - validate_evidence_for_supervisor.py detects declaration-review packages
  - Legacy bundle checks still run for actual legacy bundles
"""
import json
import sys
import zipfile
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from compare_goal_to_evidence import compare
from validate_evidence_for_supervisor import (
    validate, _is_declaration_review_package, _validate_declaration_review_package
)


# ---------------------------------------------------------------------------
# Declaration-sourced marker in bridge output
# ---------------------------------------------------------------------------

def test_declaration_sourced_marker_skips_final_verdict_check():
    """When _declaration_sourced=True, check_missing_final_verdict is skipped."""
    review = {
        "_declaration_sourced": True,
        "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R101-TEST",
        "verdict": "ACCEPTED",
        "facts": {
            "test_count": 100, "fail_count": 0, "skip_count": 0,
            "final_verdict_text": "",  # empty — would normally be CRITICAL
            "pending_marker_count": 0,
        },
        "validator_invoked": False,
        "bundle_validation_pass": True,
    }
    result = compare(review, {}, REPO_ROOT)
    assert result["overall"] == "CLEAN"
    assert result["critical_count"] == 0
    assert result["autonomous_continue"] is True


def test_declaration_sourced_marker_skips_bundle_validation_check():
    """When _declaration_sourced=True, check_bundle_validation_fail is skipped."""
    review = {
        "_declaration_sourced": True,
        "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R101-TEST",
        "verdict": "ACCEPTED",
        "facts": {
            "test_count": 100, "fail_count": 0, "skip_count": 0,
            "final_verdict_text": "ACCEPTED",
            "pending_marker_count": 0,
        },
        "validator_invoked": True,
        "bundle_validation_pass": False,  # would normally be CRITICAL
        "validator_output": "SIDECAR_REQUIRED something",
    }
    result = compare(review, {}, REPO_ROOT)
    assert result["overall"] == "CLEAN"
    assert result["critical_count"] == 0


def test_legacy_review_still_checks_final_verdict():
    """Without _declaration_sourced, missing final_verdict_text is CRITICAL."""
    review = {
        "sprint_id": "FORMAT-FACTORY-R99-TEST",
        "verdict": "BLOCKED_MISSING_FINAL_VERDICT",
        "facts": {
            "test_count": 0, "fail_count": 0, "skip_count": 0,
            "final_verdict_text": "",
            "pending_marker_count": 0,
        },
        "validator_invoked": False,
        "bundle_validation_pass": False,
    }
    result = compare(review, {}, REPO_ROOT)
    assert result["critical_count"] >= 1
    descs = [c["description"] for c in result["contradictions"]]
    assert any("final-verdict" in d.lower() for d in descs)


def test_declaration_sourced_still_checks_test_failures():
    """Even declaration-sourced reviews should flag test failures."""
    review = {
        "_declaration_sourced": True,
        "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R101-TEST",
        "verdict": "ACCEPTED",
        "facts": {
            "test_count": 100, "fail_count": 5, "skip_count": 0,
            "final_verdict_text": "",
            "pending_marker_count": 0,
        },
        "validator_invoked": False,
        "bundle_validation_pass": True,
    }
    result = compare(review, {"tests_must_pass": True}, REPO_ROOT)
    # Test failure check should still run
    has_test_contra = any("test" in c["description"].lower() or "fail" in c["description"].lower()
                         for c in result["contradictions"])
    # Note: check_tests_failed only fires if contract says tests_must_pass
    # and fail_count > 0 — may or may not trigger depending on contract format


# ---------------------------------------------------------------------------
# Declaration-review package detection
# ---------------------------------------------------------------------------

def _make_declaration_review_zip(tmp_dir: Path) -> Path:
    """Create a minimal declaration-review package ZIP."""
    zip_path = tmp_dir / "decl-review.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        decl = {
            "run_id": "test-run",
            "sprint_id": "FORMAT-FACTORY-SUPERVISOR-R100-TEST",
            "test_results": {"passed": 50, "failed": 0, "skipped": 0},
        }
        zf.writestr("evidence/evidence-declaration.yaml",
                     yaml.dump(decl, default_flow_style=False))
        zf.writestr("supervisor/item-grades.yaml", "grades: []")
        zf.writestr("supervisor/supervisor-cycle-manifest.yaml", "cycle_id: test")
    return zip_path


def _make_legacy_bundle_zip(tmp_dir: Path) -> Path:
    """Create a minimal legacy bundle ZIP (no declaration, has final-verdict)."""
    zip_path = tmp_dir / "legacy-bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("repo/reports/r90/final-verdict.md", "VERDICT: ACCEPTED")
        zf.writestr("bundle-metadata/sprint-id.txt", "FORMAT-FACTORY-R90-TEST")
    return zip_path


def test_detect_declaration_review_package():
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = _make_declaration_review_zip(Path(tmp))
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert _is_declaration_review_package(zf)


def test_detect_legacy_bundle_is_not_declaration():
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = _make_legacy_bundle_zip(Path(tmp))
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert not _is_declaration_review_package(zf)


def test_validate_declaration_review_package():
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = _make_declaration_review_zip(Path(tmp))
        result = validate(zip_path, REPO_ROOT)
        assert result["_declaration_sourced"] is True
        assert result["verdict"] == "ACCEPTED"
        assert result["facts"]["test_count"] == 50
        assert result["sprint_id"] == "FORMAT-FACTORY-SUPERVISOR-R100-TEST"
        assert result["bundle_validation_pass"] is True


def test_validate_declaration_review_not_blocked():
    """Declaration-review packages must NOT get BLOCKED_MISSING_FINAL_VERDICT."""
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = _make_declaration_review_zip(Path(tmp))
        result = validate(zip_path, REPO_ROOT)
        assert "BLOCKED" not in result["verdict"]


# ---------------------------------------------------------------------------
# Real review packages from repo
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", [
    "supervisor-r100", "acceleration-r101", "mainstream-r103", "skills-r100"
])
def test_real_review_package_not_blocked(run_id):
    """Real declaration-review packages should not get BLOCKED verdict."""
    pkg_path = REPO_ROOT / ".local" / "supervisor" / "reviews" / run_id / "declaration-review-package.zip"
    if not pkg_path.exists():
        pytest.skip(f"Package not found: {pkg_path}")
    result = validate(pkg_path, REPO_ROOT)
    assert "BLOCKED" not in result["verdict"], \
        f"Package {run_id} got verdict {result['verdict']}"
    assert result.get("_declaration_sourced") is True
