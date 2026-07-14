"""test_governance_block_registry.py — Tests for governance_block_registry.py

TC-CQGA2-R1 (mutable-exploring-hellman / CQGA-002)

Tests:
  1. All 5 structural GOV_BLOCK validators are present in the registry
  2. is_structural_block returns True for exact matches
  3. is_structural_block returns True for prefix matches (e.g., "GOV_BLOCK:monolith... [format]")
  4. is_structural_block returns False for non-structural rework items
  5. filter_structural_blocks returns only structural items from a mixed list
  6. CLAUDE.md alignment: validate_multi_responsibility_file and validate_analytics_naming_enforced
     are in the registry (previously missing from code while documented in CLAUDE.md)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.supervisor.governance_block_registry import (
    STRUCTURAL_GOV_BLOCKS,
    filter_structural_blocks,
    is_structural_block,
)


# ---------------------------------------------------------------------------
# Test 1: Registry completeness
# ---------------------------------------------------------------------------

def test_registry_contains_original_two():
    """Original 2 GOV_BLOCKs from TC-GOVBLK-001 must be present."""
    assert "GOV_BLOCK:monolith_detection_validator" in STRUCTURAL_GOV_BLOCKS
    assert "GOV_BLOCK:validate_source_architecture" in STRUCTURAL_GOV_BLOCKS


def test_registry_contains_claude_md_validators():
    """RCA-A fix: CLAUDE.md listed 4 GOV_BLOCKs; code only wired 2. Now all 4 are present."""
    assert "GOV_BLOCK:validate_multi_responsibility_file" in STRUCTURAL_GOV_BLOCKS
    assert "GOV_BLOCK:validate_analytics_naming_enforced" in STRUCTURAL_GOV_BLOCKS


def test_registry_contains_stub_validator():
    """V149 validate_source_stubs is a structural block (no stubs in src/)."""
    assert "GOV_BLOCK:validate_source_stubs" in STRUCTURAL_GOV_BLOCKS


def test_registry_minimum_size():
    """Registry must have at least 6 entries."""
    assert len(STRUCTURAL_GOV_BLOCKS) >= 6


def test_registry_contains_v119():
    """REQ-STRUCT-003: V119 promote-without-reopen must be in structural blocks."""
    assert "GOV_BLOCK:validate_promoted_code_changed_without_reopening" in STRUCTURAL_GOV_BLOCKS


# ---------------------------------------------------------------------------
# Test 2: is_structural_block — exact match
# ---------------------------------------------------------------------------

def test_is_structural_block_exact_match():
    assert is_structural_block("GOV_BLOCK:monolith_detection_validator") is True
    assert is_structural_block("GOV_BLOCK:validate_source_architecture") is True
    assert is_structural_block("GOV_BLOCK:validate_multi_responsibility_file") is True
    assert is_structural_block("GOV_BLOCK:validate_analytics_naming_enforced") is True
    assert is_structural_block("GOV_BLOCK:validate_source_stubs") is True


# ---------------------------------------------------------------------------
# Test 3: is_structural_block — prefix match (format suffix)
# ---------------------------------------------------------------------------

def test_is_structural_block_prefix_match():
    """Rework items may carry a format suffix: 'GOV_BLOCK:monolith_detection_validator [fods]'"""
    assert is_structural_block(
        "GOV_BLOCK:monolith_detection_validator [fods]"
    ) is True
    assert is_structural_block(
        "GOV_BLOCK:validate_source_architecture (src/python/csv/csv_codec.py)"
    ) is True


# ---------------------------------------------------------------------------
# Test 4: is_structural_block — non-structural items return False
# ---------------------------------------------------------------------------

def test_is_structural_block_false_for_non_structural():
    assert is_structural_block("exit_3") is False
    assert is_structural_block("V87_blocks_sprint") is False
    assert is_structural_block("GOV_BLOCK:unknown_validator") is False
    assert is_structural_block("") is False
    assert is_structural_block("monolith_detection_validator") is False  # no prefix


# ---------------------------------------------------------------------------
# Test 5: filter_structural_blocks
# ---------------------------------------------------------------------------

def test_filter_structural_blocks_mixed_list():
    rework_items = [
        "GOV_BLOCK:monolith_detection_validator [csv]",
        "V100_suspicious_filenames",
        "GOV_BLOCK:validate_source_stubs",
        "some_other_rework_item",
        "GOV_BLOCK:validate_multi_responsibility_file",
    ]
    result = filter_structural_blocks(rework_items)
    assert len(result) == 3
    assert "GOV_BLOCK:monolith_detection_validator [csv]" in result
    assert "GOV_BLOCK:validate_source_stubs" in result
    assert "GOV_BLOCK:validate_multi_responsibility_file" in result


def test_filter_structural_blocks_empty_list():
    assert filter_structural_blocks([]) == []


def test_filter_structural_blocks_no_structural_items():
    rework_items = ["exit_3_on_closeout", "V87_warn", "schema_mismatch"]
    assert filter_structural_blocks(rework_items) == []


def test_filter_structural_blocks_all_structural():
    items = list(STRUCTURAL_GOV_BLOCKS)
    result = filter_structural_blocks(items)
    assert len(result) == len(items)
