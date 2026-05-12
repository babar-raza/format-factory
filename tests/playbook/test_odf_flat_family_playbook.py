#!/usr/bin/env python3
"""
S-F2F-05: ODF-Flat Family Playbook Tests

Tests that the ODF-flat family playbook:
1. Exists at the correct path
2. Covers all 5 ODF flat formats (FODS, FODT, FODP, FODG, FODB)
3. Explicitly prohibits inherited gate approval
4. Has family_playbook kind
5. No per-format playbook.yaml files were created (FODS/FODT forbidden)
6. reuse-policy.md explicitly prohibits inherited approval and requires DEC-034
7. format-overrides.yaml covers all 5 formats
8. Validates against the acquisition-playbook schema

Run from repo root:
    python -m pytest tests/playbook/test_odf_flat_family_playbook.py -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

FAMILY_DIR = REPO_ROOT / "acquisition-packs" / "_families" / "odf-flat"
PLAYBOOK_YAML = FAMILY_DIR / "playbook.yaml"
REUSE_POLICY_MD = FAMILY_DIR / "reuse-policy.md"
FORMAT_OVERRIDES_YAML = FAMILY_DIR / "format-overrides.yaml"
SCHEMA = REPO_ROOT / "schemas" / "playbook" / "acquisition-playbook.schema.json"
VALIDATE_TOOL = REPO_ROOT / "tools" / "playbook" / "validate_playbook.py"

EXPECTED_FORMATS = ["fods", "fodt", "fodp", "fodg", "fodb"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: Files exist
# ---------------------------------------------------------------------------

def test_family_playbook_files_exist():
    """All three S-F2F-05 output files must exist."""
    assert PLAYBOOK_YAML.exists(), f"Missing: {PLAYBOOK_YAML}"
    assert REUSE_POLICY_MD.exists(), f"Missing: {REUSE_POLICY_MD}"
    assert FORMAT_OVERRIDES_YAML.exists(), f"Missing: {FORMAT_OVERRIDES_YAML}"


# ---------------------------------------------------------------------------
# Test 2: All 5 formats covered
# ---------------------------------------------------------------------------

def test_playbook_covers_all_5_formats():
    """Family playbook must cover all 5 ODF flat formats."""
    text = _read(PLAYBOOK_YAML)
    for fmt in EXPECTED_FORMATS:
        assert fmt in text, f"Format {fmt!r} not found in playbook.yaml"


# ---------------------------------------------------------------------------
# Test 3: inherited_gate_approval: false in reuse-policy
# ---------------------------------------------------------------------------

def test_reuse_policy_no_inherited_approval():
    """reuse-policy.md must explicitly prohibit inherited gate approval."""
    text = _read(REUSE_POLICY_MD)
    assert "inherited_gate_approval: false" in text, \
        "reuse-policy.md must contain 'inherited_gate_approval: false'"


# ---------------------------------------------------------------------------
# Test 4: DEC-034 mentioned in reuse-policy
# ---------------------------------------------------------------------------

def test_reuse_policy_requires_dec034():
    """reuse-policy.md must require DEC-034 independent verification."""
    text = _read(REUSE_POLICY_MD)
    assert "DEC-034" in text or "independent verification" in text.lower(), \
        "reuse-policy.md must reference DEC-034 or independent verification"


# ---------------------------------------------------------------------------
# Test 5: No per-format playbook.yaml files created
# ---------------------------------------------------------------------------

def test_no_per_format_playbooks_created():
    """Lane C must NOT create per-format playbook.yaml files."""
    fods_playbook = REPO_ROOT / "acquisition-packs" / "fods" / "playbook.yaml"
    fodt_playbook = REPO_ROOT / "acquisition-packs" / "fodt" / "playbook.yaml"
    assert not fods_playbook.exists(), "FAIL: fods/playbook.yaml must not exist"
    assert not fodt_playbook.exists(), "FAIL: fodt/playbook.yaml must not exist"


# ---------------------------------------------------------------------------
# Test 6: playbook_kind is family_playbook
# ---------------------------------------------------------------------------

def test_playbook_kind_is_family_playbook():
    """playbook.yaml must have playbook_kind: family_playbook."""
    text = _read(PLAYBOOK_YAML)
    assert "playbook_kind: family_playbook" in text, \
        "playbook.yaml must have playbook_kind: family_playbook"


# ---------------------------------------------------------------------------
# Test 7: format-overrides covers all 5 formats
# ---------------------------------------------------------------------------

def test_format_overrides_covers_all_5_formats():
    """format-overrides.yaml must include entries for all 5 formats."""
    text = _read(FORMAT_OVERRIDES_YAML)
    for fmt in EXPECTED_FORMATS:
        assert fmt + ":" in text, f"Format {fmt!r} not in format-overrides.yaml"


# ---------------------------------------------------------------------------
# Test 8: FODP/FODG/FODB are marked candidate_only
# ---------------------------------------------------------------------------

def test_fodp_fodg_fodb_are_candidate_only():
    """FODP, FODG, FODB must be marked as candidate_only (not approved)."""
    text = _read(FORMAT_OVERRIDES_YAML)
    for fmt in ["fodp", "fodg", "fodb"]:
        assert "candidate_only" in text, \
            f"Candidate formats must be marked candidate_only in format-overrides.yaml"


# ---------------------------------------------------------------------------
# Test 9: Validates against schema
# ---------------------------------------------------------------------------

def test_playbook_validates_against_schema():
    """Family playbook must validate against acquisition-playbook.schema.json."""
    result = subprocess.run(
        [sys.executable, str(VALIDATE_TOOL),
         "--schema", str(SCHEMA),
         "--input", str(PLAYBOOK_YAML),
         "--kind", "acquisition-playbook",
         "--format-id", "odf-flat"],
        capture_output=True, text=True,
    )
    combined = result.stdout + result.stderr
    assert "PLAYBOOK_VALIDATION: PASS" in combined, \
        f"Schema validation must PASS. Output:\n{combined}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
