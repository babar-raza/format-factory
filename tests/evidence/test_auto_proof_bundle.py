#!/usr/bin/env python3
"""
Tests for --auto-proof three-pass bundle build (ACCEL-003 repaired).

Verifies:
1. Auto-proof happy path: all three passes succeed, final ZIP exists.
2. Candidate validation failure stops final output.
3. On-disk proof content: candidate + pre-proof + final verification record.
4. sprint_id in proof matches contract sprint_id.
5. Without --auto-proof, build_bundle behavior unchanged.
6. Final bundle validates with --check-no-pending.
7. On-disk proof contains Final SHA-256/entries/bytes/metadata (ACCEL-003 hardening).
8. Proof INSIDE the final ZIP is NOT candidate-only (contains pre-proof section).
9. Proof INSIDE the final ZIP contains final path, entries, metadata, and Final validation: PASS.

Run from repo root:
    python -m pytest tests/evidence/test_auto_proof_bundle.py -v

Exits 0 if all tests pass, non-zero otherwise.
"""

import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from build_evidence_bundle import build_auto_proof_bundle, build_bundle  # noqa: E402

PROOF_ENTRY = "bundle-metadata/final-bundle-validation-proof.txt"


def _scoreboard_has_in_progress() -> bool:
    """Check if any scoreboard in reports/ contains IN_PROGRESS."""
    for sb in REPO_ROOT.rglob("*scoreboard*.md"):
        try:
            if "IN_PROGRESS" in sb.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            pass
    return False


_SKIP_SCOREBOARD = pytest.mark.skipif(
    _scoreboard_has_in_progress(),
    reason="Scoreboard has IN_PROGRESS lanes — auto-proof validation will fail on live repo state",
)


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
required_top_level_folders: ["bundle-metadata"]
required_metadata_files:
  - final-bundle-validation-proof.txt
forbidden_paths: []
""",
        encoding="utf-8",
    )
    return contract


def _write_metadata(metadata_dir: Path, count: int = 6,
                    sprint_id: str = SPRINT_ID) -> None:
    """Write enough metadata files to satisfy min_metadata_count.

    Includes AUTHORITATIVE_TEST_RESULT in validation-command-log.txt to satisfy
    P-EVID-003 when --check-no-pending is active.
    """
    metadata_dir.mkdir(parents=True, exist_ok=True)
    # P-EVID-003: at least one metadata file must contain AUTHORITATIVE_TEST_RESULT
    (metadata_dir / "validation-command-log.txt").write_text(
        f"sprint_id: {sprint_id}\nAUTHORITATIVE_TEST_RESULT: 1 passed, 0 skipped\n",
        encoding="utf-8",
    )
    for i in range(count):
        (metadata_dir / f"meta_{i:02d}.txt").write_text(
            f"sprint_id: {sprint_id}\ncontent: dummy {i}\n",
            encoding="utf-8",
        )


def _read_proof_from_zip(zip_path: Path) -> str:
    """Read the proof file from inside the final ZIP."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        if PROOF_ENTRY not in zf.namelist():
            return ""
        return zf.read(PROOF_ENTRY).decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Test 1: Happy path
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
def test_auto_proof_happy_path(tmp_path):
    """Auto-proof three-pass build succeeds: final ZIP exists and proof is not placeholder."""
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
    # Intermediate ZIPs must be cleaned up
    candidate = output.with_name(output.stem + "-candidate.zip")
    preproof = output.with_name(output.stem + "-preproof.zip")
    assert not candidate.exists(), "Candidate ZIP must be cleaned up after success"
    assert not preproof.exists(), "Pre-proof ZIP must be cleaned up after success"


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
# Test 3: On-disk proof file content
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
def test_auto_proof_proof_file_content(tmp_path):
    """On-disk proof must contain candidate name, sha256, entries, bytes, metadata."""
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
    assert "SHA-256:" in proof_text, "Proof must include a SHA-256"
    assert "entries:" in proof_text, "Proof must include entry count"
    assert "bytes:" in proof_text, "Proof must include byte size"
    assert "metadata:" in proof_text, "Proof must include metadata count"
    assert "PLACEHOLDER" not in proof_text, "Proof must not be a placeholder"
    # ACCEL-003 hardening: final metrics in external verification record
    assert "Final SHA-256:" in proof_text, "On-disk proof must include Pass 3 Final SHA-256"
    assert "Final entries:" in proof_text, "On-disk proof must include Final entries count"
    assert "Final bytes:" in proof_text, "On-disk proof must include Final bytes"
    assert "Final metadata:" in proof_text, "On-disk proof must include Final metadata count"
    assert "Final validation: PASS" in proof_text, "Proof must record final validation PASS"


# ---------------------------------------------------------------------------
# Test 4: sprint_id in proof matches contract sprint_id
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
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

@_SKIP_SCOREBOARD
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
# Test 7: On-disk proof contains Final SHA-256/entries/bytes/metadata (ACCEL-003)
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
def test_auto_proof_includes_final_bundle_metrics(tmp_path):
    """On-disk proof must contain final bundle path, SHA-256, entries, bytes, metadata."""
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

    # PASS 3 external verification record
    assert "PASS 3" in proof_text or "Final SHA-256:" in proof_text, \
        "On-disk proof must contain Pass 3 verification record"
    assert "mybundle.zip" in proof_text, "Proof must include the final bundle filename"
    assert "Final SHA-256:" in proof_text, "Proof must include Final SHA-256"
    assert "Final entries:" in proof_text, "Proof must include Final entries count"
    assert "Final bytes:" in proof_text, "Proof must include Final bytes"
    assert "Final metadata:" in proof_text, "Proof must include Final metadata count"
    assert "Final validation: PASS" in proof_text, "Proof must record Final validation: PASS"
    assert "CANDIDATE" in proof_text, "Proof must still contain CANDIDATE section"
    assert "-candidate.zip" in proof_text, "Proof must still name the candidate zip"


# ---------------------------------------------------------------------------
# Test 8: Proof INSIDE the final ZIP is NOT candidate-only (ACCEL-003 repair)
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
def test_proof_inside_zip_is_not_candidate_only(tmp_path):
    """The proof embedded inside the final ZIP must contain pre-proof metrics.

    This is the core ACCEL-003 repair test: verifies the final ZIP itself
    contains more than just candidate data.
    """
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

    # Read proof FROM INSIDE THE ZIP — not from metadata_dir
    proof_in_zip = _read_proof_from_zip(output)
    assert proof_in_zip, f"Proof file must exist at {PROOF_ENTRY!r} inside the final ZIP"

    # Must not be candidate-only
    assert "CANDIDATE" in proof_in_zip, "ZIP proof must contain CANDIDATE section"
    candidate_section_only = (
        "PRE-PROOF" not in proof_in_zip
        and "Pre-proof" not in proof_in_zip
        and "FINAL" not in proof_in_zip
    )
    assert not candidate_section_only, (
        "ZIP proof must NOT be candidate-only. "
        "Expected pre-proof and final sections. Got:\n" + proof_in_zip[:500]
    )

    # Must contain pre-proof section
    assert "PRE-PROOF" in proof_in_zip or "Pre-proof" in proof_in_zip, \
        "ZIP proof must contain pre-proof section"

    # Must NOT still be a placeholder
    assert "PLACEHOLDER" not in proof_in_zip, \
        "ZIP proof must not still be PLACEHOLDER"
    assert "in progress" not in proof_in_zip, \
        "ZIP proof must not contain 'in progress' (unfinished pass marker)"


# ---------------------------------------------------------------------------
# Test 9: Proof INSIDE the final ZIP has required fields (ACCEL-003 repair)
# ---------------------------------------------------------------------------

@_SKIP_SCOREBOARD
def test_proof_inside_zip_has_required_fields(tmp_path):
    """Proof inside the final ZIP must contain path, entries, metadata, and final validation."""
    contract = _write_contract(tmp_path, min_meta=5)
    meta_dir = tmp_path / "metadata"
    _write_metadata(meta_dir, count=6)

    output = tmp_path / "target.zip"
    ok = build_auto_proof_bundle(
        str(REPO_ROOT), str(contract), str(output), str(meta_dir),
        allow_legacy_root_metadata=False,
        require_clean_git=False,
    )
    assert ok

    # Read proof FROM INSIDE THE ZIP
    proof_in_zip = _read_proof_from_zip(output)
    assert proof_in_zip, "Proof must be present inside the final ZIP"

    assert "target.zip" in proof_in_zip, \
        "Proof inside ZIP must reference the final bundle filename"
    assert "Pre-proof SHA-256:" in proof_in_zip, \
        "Proof inside ZIP must include Pre-proof SHA-256 (verifiable)"
    assert "Pre-proof entries:" in proof_in_zip, \
        "Proof inside ZIP must include Pre-proof entries"
    assert "Pre-proof bytes:" in proof_in_zip, \
        "Proof inside ZIP must include Pre-proof bytes"
    assert "Final entries:" in proof_in_zip, \
        "Proof inside ZIP must include Final entries"
    assert "Final metadata:" in proof_in_zip, \
        "Proof inside ZIP must include Final metadata"
    assert "Final validation: PASS" in proof_in_zip, \
        "Proof inside ZIP must record Final validation: PASS"
    assert "Self-reference note" in proof_in_zip, \
        "Proof inside ZIP must include self-reference note explaining the hash limitation"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
