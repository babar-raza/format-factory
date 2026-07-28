"""
Unit tests for run_fact_verification.py — TC-SAL-002.

Tests:
  1. calibration: ≥10/14 known-verified FODS facts found (precision gate)
  2. discovery: pending fact with matching terms remains conditional
  3. dry-run: YAML NOT modified when --dry-run passed
  4. no-spec-text: pending fact for format with no text.txt → skip, no error
  5. not-found: claim with terms not in spec text → stays pending
  6. regression guard: verified count does not decrease
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAL_TOOLS = _REPO / "tools" / "specification-authority-layer"
sys.path.insert(0, str(_SAL_TOOLS))

from run_fact_verification import (  # type: ignore
    _count_verified,
    _find_section_line,
    _process_format,
    _score_claim,
    _tokenize_claim,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fact(claim_id: str, claim: str, section_id: str, status: str) -> dict:
    return {
        "claim_id": claim_id,
        "claim": claim,
        "provenance": {
            "section_id": section_id,
            "verification_status": status,
            "extraction_method": "tier1_section",
        },
    }


def _write_review_yaml(path: Path, facts: list[dict]) -> None:
    """Write a minimal verified-facts-review.yaml in JSON format."""
    data = {"format_id": "test", "facts": facts}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _make_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: Calibration precision against known-verified FODS facts
# ---------------------------------------------------------------------------

def test_calibration_fods_precision():
    """
    Run calibration mode against real FODS workbench YAML and real text.txt.
    Must find ≥10 out of all verified facts (precision gate).
    Skips if real data not available (CI-safe).
    """
    review_file = _REPO / ".local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml"
    text_file = _REPO / ".local/spec-cache/fods/1.3/normalized/text.txt"

    if not review_file.is_file() or not text_file.is_file():
        pytest.skip("Real FODS workbench data not available")

    lines_cache: dict = {}
    res = _process_format(review_file, "fods", dry_run=False, calibrate=True, lines_cache=lines_cache)

    total = res["calibration_total"]
    found = res["calibration_found"]
    assert total > 0, "No verified facts found in FODS workbench"
    assert found >= 10, (
        f"Calibration precision too low: {found}/{total} verified facts found in spec text. "
        "Algorithm needs tuning before batch run is safe."
    )
    print(f"\n[calibration] FODS: {found}/{total} verified facts found ({100*found/total:.0f}%)")


# ---------------------------------------------------------------------------
# Test 2: Discovery — keyword overlap never promotes
# ---------------------------------------------------------------------------

def test_pending_fact_keyword_match_is_only_verified_with_note(tmp_path):
    """A pending fact whose terms appear stays conditional."""
    # Create fake text.txt with section and matching content
    text_content = "\n" * 10
    text_content += "9.99  Test Section\n"
    text_content += "The office:value-type attribute specifies the cell type.\n" * 5
    text_content += "string float boolean are valid value types.\n"

    text_file = tmp_path / "normalized" / "text.txt"
    _make_text_file(text_file, text_content)

    # Create review YAML with one pending fact
    facts = [
        _make_fact(
            "FACT-TEST-001",
            "office:value-type attribute specifies cell value type string float boolean",
            "9.99",
            "pending_verification",
        )
    ]
    workbench_dir = tmp_path / "workbench"
    workbench_dir.mkdir()
    review_file = workbench_dir / "verified-facts-review.yaml"
    _write_review_yaml(review_file, facts)

    lines_cache: dict = {}
    res = _process_format(review_file, "test", dry_run=False, calibrate=False, lines_cache=lines_cache)

    assert res["promoted_verified"] + res["promoted_verified_with_note"] >= 1, (
        f"Expected promotion but got: {res}"
    )
    # Verify YAML was updated
    updated = json.loads(review_file.read_text(encoding="utf-8"))
    fact = updated["facts"][0]
    new_status = fact["provenance"]["verification_status"]
    assert new_status == "verified_with_note"
    assert fact["provenance"]["validated_by"] == "deterministic_spec_text_search"


# ---------------------------------------------------------------------------
# Test 3: Dry-run — YAML must NOT be modified
# ---------------------------------------------------------------------------

def test_dry_run_does_not_write(tmp_path):
    """--dry-run must not modify the review YAML file."""
    text_content = "9.1.2  table:table\nThe table:name attribute specifies the name.\n" * 10
    text_file = tmp_path / "normalized" / "text.txt"
    _make_text_file(text_file, text_content)

    facts = [_make_fact("FACT-DRY-001", "table:name attribute specifies table name", "9.1.2", "pending_verification")]
    workbench_dir = tmp_path / "workbench"
    workbench_dir.mkdir()
    review_file = workbench_dir / "verified-facts-review.yaml"
    _write_review_yaml(review_file, facts)

    original_content = review_file.read_text(encoding="utf-8")

    lines_cache: dict = {}
    _process_format(review_file, "test", dry_run=True, calibrate=False, lines_cache=lines_cache)

    assert review_file.read_text(encoding="utf-8") == original_content, (
        "YAML was modified during --dry-run (must not write)"
    )


# ---------------------------------------------------------------------------
# Test 4: No spec text — pending fact skipped, no error
# ---------------------------------------------------------------------------

def test_no_spec_text_skipped(tmp_path):
    """When no normalized text.txt exists, facts are skipped gracefully."""
    # Do NOT create text.txt
    facts = [_make_fact("FACT-NOTEXT-001", "some claim about the format", "9.4", "pending_verification")]
    workbench_dir = tmp_path / "workbench"
    workbench_dir.mkdir()
    review_file = workbench_dir / "verified-facts-review.yaml"
    _write_review_yaml(review_file, facts)

    lines_cache: dict = {}
    res = _process_format(review_file, "test", dry_run=False, calibrate=False, lines_cache=lines_cache)

    assert res["text_path"] is None
    assert res["skipped_no_text"] == 1
    assert res["promoted_verified"] == 0
    assert res["promoted_verified_with_note"] == 0


# ---------------------------------------------------------------------------
# Test 5: Not found — claim terms absent from spec text → stays pending
# ---------------------------------------------------------------------------

def test_claim_not_found_stays_pending(tmp_path):
    """Claim with terms that don't appear in spec text → not promoted."""
    text_content = "9.99  Section Title\nThis section describes unrelated content only.\n" * 10
    text_file = tmp_path / "normalized" / "text.txt"
    _make_text_file(text_file, text_content)

    facts = [
        _make_fact(
            "FACT-NOTFOUND-001",
            "xyzzy quux frobnicate nonexistent attribute purple elephant",
            "9.99",
            "pending_verification",
        )
    ]
    workbench_dir = tmp_path / "workbench"
    workbench_dir.mkdir()
    review_file = workbench_dir / "verified-facts-review.yaml"
    _write_review_yaml(review_file, facts)

    lines_cache: dict = {}
    res = _process_format(review_file, "test", dry_run=False, calibrate=False, lines_cache=lines_cache)

    # Should not have promoted any fact
    assert res["promoted_verified"] == 0
    assert res["promoted_verified_with_note"] == 0

    # YAML should be unchanged (fact stays pending)
    data = json.loads(review_file.read_text(encoding="utf-8"))
    status = data["facts"][0]["provenance"]["verification_status"]
    assert status == "pending_verification", f"Expected pending, got: {status}"


# ---------------------------------------------------------------------------
# Test 6: Regression guard — verified count does not decrease
# ---------------------------------------------------------------------------

def test_verified_count_does_not_decrease(tmp_path):
    """
    _count_verified returns correct count, and _process_format does not
    reduce already-verified facts.
    """
    text_content = "9.99  Section Title\noffice:value-type attribute specifies cell type.\n" * 10
    text_file = tmp_path / "normalized" / "text.txt"
    _make_text_file(text_file, text_content)

    # Mix: 2 already-verified + 1 pending that will be promoted
    facts = [
        _make_fact("FACT-V-001", "already verified fact", "9.99", "verified"),
        _make_fact("FACT-V-002", "second verified fact", "9.99", "verified"),
        _make_fact("FACT-P-001", "office:value-type attribute specifies cell type", "9.99", "pending_verification"),
    ]
    workbench_dir = tmp_path / "workbench"
    workbench_dir.mkdir()
    review_file = workbench_dir / "verified-facts-review.yaml"
    _write_review_yaml(review_file, facts)

    pre_count = _count_verified(facts)
    assert pre_count == 2

    lines_cache: dict = {}
    res = _process_format(review_file, "test", dry_run=False, calibrate=False, lines_cache=lines_cache)

    # Post count must be ≥ pre count
    data = json.loads(review_file.read_text(encoding="utf-8"))
    post_count = _count_verified(data["facts"])
    assert post_count >= pre_count, (
        f"Verified count decreased: {pre_count} → {post_count}"
    )


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

def test_tokenize_claim_drops_short_and_stop_words():
    claim = "the table:name attribute has data type string"
    terms = _tokenize_claim(claim)
    assert "the" not in terms
    assert "has" not in terms
    # `:` is a split delimiter, so `table:name` → ["table", "name"] as separate tokens
    assert "table" in terms
    assert "name" in terms
    assert "table:name" not in terms
    assert "attribute" in terms
    assert "string" in terms


def test_find_section_line_finds_correct_line():
    lines = [
        "3.1  Introduction\n",
        "9.4  Spreadsheet Document Content\n",
        "9.4.1  subtable\n",  # sub-section: must NOT match "9.4" (dot suffix excluded)
        "some other content 9.4 mentioned here\n",  # not at line start: must not match
    ]
    idx = _find_section_line(lines, "9.4")
    assert idx == 1  # line index 1 (0-based) matches "9.4  Spreadsheet..."


def test_score_claim_never_promotes_on_many_terms():
    lines = ["9.99  Test Section\n"] + [
        "table:name attribute specifies the name of table elements value-type string\n"
    ] * 5
    status, matched = _score_claim(lines, 0, ["table:name", "attribute", "specifies", "name", "value-type"])
    assert status == "verified_with_note"
    assert len(matched) >= 3


def test_score_claim_returns_not_found_on_no_terms():
    lines = ["9.99  Test Section\n", "totally unrelated paragraph.\n"]
    status, matched = _score_claim(lines, 0, ["xyzzy", "quux", "frobnicate", "nonexistent"])
    assert status == "not_found_in_normalized_text"
    assert len(matched) == 0
