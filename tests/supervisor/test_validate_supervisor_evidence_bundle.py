"""
Tests for tools/supervisor/validate_supervisor_evidence_bundle.py

Covers recurrence-prevention for defects found in dual-orchestration sprint:
  D-SUP-01: Contract not in ZIP
  D-SUP-02: reports/supervisor/ not in ZIP when claimed
  D-SUP-03: Stale/wrong SHA in final verdict
  D-SUP-04: No replay fixture when replay claimed

Tests:
  test_good_bundle_passes
  test_missing_contract_fails
  test_stale_sha_warns
  test_missing_supervisor_reports_fails
  test_missing_replay_fixture_fails
  test_false_bundle_validation_claim_warns
  test_delegation_label_passes_sha_check
  test_pending_in_verdict_fails
"""

import sys
import zipfile
from pathlib import Path


# Allow import from tools/supervisor
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from tools.supervisor.validate_supervisor_evidence_bundle import validate_bundle


def make_zip(files: dict, path: str):
    """Create a ZIP file with given filename->content dict."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            if isinstance(content, str):
                zf.writestr(name, content)
            else:
                zf.writestr(name, content)


def test_good_bundle_passes(tmp_path):
    """A well-formed bundle with all required elements passes all checks."""
    bundle = str(tmp_path / "good.zip")
    contract_path = str(tmp_path / "contract.yaml")

    # Write a dummy contract file
    with open(contract_path, "w") as f:
        f.write("sprint_id: test\n")

    make_zip({
        "repo/tools/evidence/contracts/contract.yaml": "sprint_id: test\n",
        "repo/reports/test/final-verdict.md": (
            "# Final Verdict\n\n"
            "BUNDLE_SHA256: delegated_to_sidecar_proof\n\n"
            "## Accepted Limitations\n"
            "1. Test limitation — deferred to MODE 4\n"
        ),
        "repo/reports/supervisor/evidence-review.json": '{"sprint_id": "test"}',
        "repo/reports/supervisor/approval-gates.md": "# Approval Gates",
    }, bundle)

    result = validate_bundle(bundle, contract_path)
    # Contract check should pass
    assert not any(c["id"] == "SUP-V-003" and c["result"] == "FAIL" for c in result.checks)
    # Supervisor reports — no run-on-latest claimed, so no fail
    assert not any(c["id"] == "SUP-V-004" and c["result"] == "FAIL" for c in result.checks)
    # SHA delegation label — should pass
    assert any(c["id"] == "SUP-V-005" and c["result"] == "PASS" for c in result.checks)
    # No PENDING markers
    assert any(c["id"] == "SUP-V-008" and c["result"] == "PASS" for c in result.checks)


def test_missing_contract_fails(tmp_path):
    """Bundle without the contract file fails SUP-V-003 when contract arg is provided."""
    bundle = str(tmp_path / "no_contract.zip")
    contract_path = str(tmp_path / "my-contract.yaml")
    with open(contract_path, "w") as f:
        f.write("sprint_id: test\n")

    make_zip({
        "repo/reports/test/final-verdict.md": "# Verdict\n",
    }, bundle)

    result = validate_bundle(bundle, contract_path)
    assert any(c["id"] == "SUP-V-003" and c["result"] == "FAIL" for c in result.checks), \
        "Missing contract should fail SUP-V-003"
    assert not result.passed


def test_stale_sha_warns(tmp_path):
    """Bundle where final verdict has a SHA that doesn't match actual ZIP gets a warning."""
    bundle = str(tmp_path / "stale_sha.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "## BUNDLE_SHA256\n"
            "0000000000000000000000000000000000000000000000000000000000000000\n"
        ),
    }, bundle)

    result = validate_bundle(bundle)
    sha_check = next((c for c in result.checks if c["id"] == "SUP-V-005"), None)
    assert sha_check is not None
    # Should warn (not fail) — one-generation-behind pattern
    assert sha_check["result"] == "WARN", f"Expected WARN, got {sha_check['result']}"


def test_delegation_label_passes_sha_check(tmp_path):
    """Final verdict using delegation label passes SHA check."""
    bundle = str(tmp_path / "delegation.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "BUNDLE_SHA256: delegated_to_sidecar_proof\n"
        ),
    }, bundle)

    result = validate_bundle(bundle)
    sha_check = next((c for c in result.checks if c["id"] == "SUP-V-005"), None)
    assert sha_check is not None
    assert sha_check["result"] == "PASS", f"Expected PASS for delegation label, got {sha_check['result']}"


def test_missing_supervisor_reports_fails(tmp_path):
    """Bundle claiming supervisor run but missing reports/supervisor/ fails SUP-V-004."""
    bundle = str(tmp_path / "no_supervisor_reports.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "| supervisor_loop.py run-on-latest | EXIT 0 |\n"
            "BUNDLE_SHA256: delegated_to_sidecar_proof\n"
        ),
        # No reports/supervisor/ files
    }, bundle)

    result = validate_bundle(bundle)
    assert any(c["id"] == "SUP-V-004" and c["result"] == "FAIL" for c in result.checks), \
        "Missing supervisor reports when claimed should fail SUP-V-004"
    assert not result.passed


def test_missing_replay_fixture_fails(tmp_path):
    """Bundle claiming replay EXIT 0 but missing fixture fails SUP-V-007."""
    bundle = str(tmp_path / "no_replay_fixture.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "| supervisor_loop.py run-on-latest | EXIT 0 |\n"
            "| Idempotence replay | SEMANTIC PASS |\n"
            "run-on-latest EXIT 0 confirmed\n"
        ),
        "repo/reports/supervisor/evidence-review.json": '{"sprint_id": "test"}',
        "repo/reports/supervisor/approval-gates.md": "# Gates",
    }, bundle)

    result = validate_bundle(bundle)
    assert any(c["id"] == "SUP-V-007" and c["result"] == "FAIL" for c in result.checks), \
        "Missing replay fixture should fail SUP-V-007"
    assert not result.passed


def test_false_bundle_validation_claim_warns(tmp_path):
    """Bundle claiming BUNDLE_VALIDATION: PASS without raw log gets a warning."""
    bundle = str(tmp_path / "false_validation.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "## BUNDLE_VALIDATION: PASS\n"
            "SIDECAR_PROOF_VALIDATION: PASS\n"
        ),
    }, bundle)

    result = validate_bundle(bundle)
    v006 = next((c for c in result.checks if c["id"] == "SUP-V-006"), None)
    assert v006 is not None
    assert v006["result"] == "WARN", f"Expected WARN for missing raw log, got {v006['result']}"


def test_pending_in_verdict_fails(tmp_path):
    """Final verdict with PENDING marker fails SUP-V-008."""
    bundle = str(tmp_path / "pending_verdict.zip")

    make_zip({
        "repo/reports/test/final-verdict.md": (
            "# Verdict\n\n"
            "BUNDLE_SHA256: PENDING\n"
            "SIDECAR_SHA: PENDING\n"
        ),
    }, bundle)

    result = validate_bundle(bundle)
    assert any(c["id"] == "SUP-V-008" and c["result"] == "FAIL" for c in result.checks), \
        "PENDING markers should fail SUP-V-008"
    assert not result.passed


def test_bundle_not_found():
    """Non-existent bundle fails immediately."""
    result = validate_bundle("/nonexistent/path/to/bundle.zip")
    assert not result.passed
    assert any(c["id"] == "SUP-V-001" and c["result"] == "FAIL" for c in result.checks)
