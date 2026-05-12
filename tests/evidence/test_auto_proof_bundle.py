#!/usr/bin/env python3
"""
Tests for --auto-proof two-pass bundle build (ACCEL-003).

Verifies:
1. Auto-proof happy path: candidate -> proof -> final, both validate.
2. Candidate validation failure stops final output.
3. Proof file content: sprint_id, candidate name, sha256, entries, bytes, metadata count.
4. sprint_id in proof matches contract sprint_id.
5. Without --auto-proof, build_bundle behavior unchanged.
6. Final bundle validates with --check-no-pending.
7. Proof includes final bundle path/SHA-256/entries/bytes/metadata count (ACCEL-003 hardening).

Run from repo root:
    python -m pytest tests/evidence/test_auto_proof_bundle.py -v

Exits 0 if all tests pass, non-zero otherwise.
"""

import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from build_evidence_bundle import build_auto_proof_bundle, build_bundle  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SPRINT_ID = "test-auto-proof-sprint"


def _write_contract(tmp_dir: Path, min_meta: int = 5,
                    sprint_id: str = SPRINT_ID) -> Path:
    """Write a minimal contract for tests.

    Uses emergency_blocker_bundle: true so the builder can run with a dirty git
    tree during development/test. NOTE: require_clean_git: false only affects
    validation (git-status-file presence), NOT the build's git-clean check.
    The only builder-level bypass is emergency_blocker_bundle: true.
    """
    contract = tmp_dir / "test-contract.yaml"
    contract.write_text(
        f"""\
sprint_id: {sprint_id}
contract_id: {sprint_id}
emergency_blocker_bundle: true
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: {min_meta}
required_repo_files: []
required_metadata_files:
  - final-bundle-validation-proof.txt
forbidden_paths: []
""",
        encoding="utf-8",
    )
    return contract


def _write_metadata(metadata_dir: Path, count: int = 6,
                    sprint_id: str = SPRINT_ID) -> None:
    """Write enough metadata files to satisfy min_metadata_count."""
    metadata_dir.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        (metadata_dir / f"meta_{i:02d}.txt").write_text(
            f"sprint_id: {sprint_id}\ncontent: dummy {i}\n",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Test 1: Happy path
# ---------------------------------------------------------------------------

def test_auto_proof_happy_path(tmp_path):
    """--auto-proof builds candidate, validates, writes real proof, builds final, validates."""
    contract = _write_contract(tmp_path, min_meta=5)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6)

    output = tmp_path / "final.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok, "build_auto_proof_bundle should return True on success"
    assert output.exists(), "Final zip must exist"

    proof_file = meta_dir / "final-bundle-validation-proof.txt"
    assert proof_file.exists(), "Proof file must exist after auto-proof"
    proof_text = proof_file.read_text(encoding="utf-8")
    assert "BUNDLE_VALIDATION: PASS" in proof_text
    assert "PLACEHOLDER" not in proof_text, "Proof must not still be a placeholder"


# ---------------------------------------------------------------------------
# Test 2: Candidate validation failure stops final output
# ---------------------------------------------------------------------------

def test_auto_proof_candidate_fail_stops_final(tmp_path):
    """When candidate fails validation, final bundle must NOT be produced."""
    # Contract requires 50 metadata files — impossible with only 3 → candidate FAIL
    contract = _write_contract(tmp_path, min_meta=50)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=3)

    output = tmp_path / "final.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert not ok, "Should return False when candidate fails"
    assert not output.exists(), "Final zip must NOT exist when candidate fails"


# ---------------------------------------------------------------------------
# Test 3: Proof file content
# ---------------------------------------------------------------------------

def test_auto_proof_proof_file_content(tmp_path):
    """Proof file must contain candidate name, sha256, entries, bytes, metadata count."""
    contract = _write_contract(tmp_path, min_meta=5)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6)

    output = tmp_path / "final.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok

    proof_text = (meta_dir / "final-bundle-validation-proof.txt").read_text(encoding="utf-8")

    assert "-candidate.zip" in proof_text, "Proof must name the candidate zip"
    assert "SHA-256:" in proof_text, "Proof must include candidate SHA-256"
    assert "entries:" in proof_text, "Proof must include entry count"
    assert "bytes:" in proof_text, "Proof must include byte size"
    assert "metadata:" in proof_text, "Proof must include metadata count"
    assert "PLACEHOLDER" not in proof_text, "Proof must not be a placeholder"
    # ACCEL-003 hardening: final bundle metrics must also be present
    assert "Final SHA-256:" in proof_text, "Proof must include final bundle SHA-256"
    assert "Final entries:" in proof_text, "Proof must include final bundle entry count"
    assert "Final bytes:" in proof_text, "Proof must include final bundle byte size"
    assert "Final metadata:" in proof_text, "Proof must include final bundle metadata count"
    assert "Final validation: PASS" in proof_text, "Proof must record final validation PASS"


# ---------------------------------------------------------------------------
# Test 4: sprint_id in proof matches contract sprint_id
# ---------------------------------------------------------------------------

def test_auto_proof_sprint_id_in_proof(tmp_path):
    """Proof file sprint_id must match the contract sprint_id."""
    sprint_id = "my-test-sprint-001"
    contract = _write_contract(tmp_path, min_meta=5, sprint_id=sprint_id)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6, sprint_id=sprint_id)

    output = tmp_path / "final.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok

    proof_text = (meta_dir / "final-bundle-validation-proof.txt").read_text(encoding="utf-8")
    assert sprint_id in proof_text, f"sprint_id {sprint_id!r} must appear in proof"


# ---------------------------------------------------------------------------
# Test 5: Without --auto-proof, build_bundle behavior unchanged
# ---------------------------------------------------------------------------

def test_build_bundle_unchanged_without_auto_proof(tmp_path):
    """build_bundle (no auto-proof) still works correctly."""
    contract_text = """\
sprint_id: test-no-autoproof
contract_id: test-no-autoproof
emergency_blocker_bundle: true
require_clean_git: false
require_contract_in_bundle: false
require_manifest: false
min_metadata_count: 5
required_repo_files: []
required_metadata_files: []
forbidden_paths: []
"""
    contract = tmp_path / "contract.yaml"
    contract.write_text(contract_text, encoding="utf-8")

    meta_dir = tmp_path / "metadata"
    meta_dir.mkdir()
    for i in range(6):
        (meta_dir / f"meta_{i}.txt").write_text(f"content {i}")

    output = tmp_path / "out.zip"
    ok = build_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        dry_run=False,
        require_clean_git=False,
        allow_legacy_root_metadata=False,
    )
    assert ok, "build_bundle should succeed"
    assert output.exists(), "Output zip must exist"


# ---------------------------------------------------------------------------
# Test 6: Final bundle validates with --check-no-pending
# ---------------------------------------------------------------------------

def test_auto_proof_final_no_pending(tmp_path):
    """Final bundle from --auto-proof must pass --check-no-pending."""
    import subprocess

    contract = _write_contract(tmp_path, min_meta=5)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6)

    output = tmp_path / "final.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok

    validator = REPO_ROOT / "tools" / "evidence" / "validate_evidence_bundle.py"
    result = subprocess.run(
        [sys.executable, str(validator),
         "--bundle", str(output),
         "--contract", str(contract),
         "--check-no-pending"],
        capture_output=True, text=True,
    )
    combined = result.stdout + result.stderr
    assert "BUNDLE_VALIDATION: PASS" in combined, \
        f"Final bundle must pass --check-no-pending. Output:\n{combined}"


# ---------------------------------------------------------------------------
# Test 7: Proof includes final bundle metrics (ACCEL-003 hardening)
# ---------------------------------------------------------------------------

def test_auto_proof_includes_final_bundle_metrics(tmp_path):
    """Proof file must contain final bundle path, SHA-256, entries, bytes, metadata count."""
    contract = _write_contract(tmp_path, min_meta=5)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6)

    output = tmp_path / "mybundle.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok

    proof_text = (meta_dir / "final-bundle-validation-proof.txt").read_text(encoding="utf-8")

    # Final section header
    assert "FINAL BUNDLE" in proof_text, "Proof must contain 'FINAL BUNDLE' section"
    # Final bundle filename
    assert "mybundle.zip" in proof_text, "Proof must include the final bundle filename"
    # Final metrics
    assert "Final SHA-256:" in proof_text, "Proof must include Final SHA-256"
    assert "Final entries:" in proof_text, "Proof must include Final entries count"
    assert "Final bytes:" in proof_text, "Proof must include Final bytes"
    assert "Final metadata:" in proof_text, "Proof must include Final metadata count"
    # Final validation result
    assert "Final validation: PASS" in proof_text, "Proof must record Final validation: PASS"
    # Candidate section still present
    assert "CANDIDATE" in proof_text, "Proof must still contain CANDIDATE section"
    assert "-candidate.zip" in proof_text, "Proof must still name the candidate zip"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
