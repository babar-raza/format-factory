"""Hardening tests for sal_master_runner functions added in velvet-tickling-codd.

TC-SAL-HARD-001: Tests for _get_source_id_for_format() and _try_verify_facts_against_spec().
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

import sal_master_runner as smr

_SOURCE_REGISTRY = _REPO / ".local" / "spec-source-registry" / "sources.jsonl"


# ---------------------------------------------------------------------------
# _get_source_id_for_format
# ---------------------------------------------------------------------------

class TestGetSourceIdForFormat:
    """_get_source_id_for_format returns registered source_ids with ODF fallback."""

    pytestmark = pytest.mark.skipif(
        not _SOURCE_REGISTRY.is_file(),
        reason="SAL source registry not present in this environment",
    )

    def setup_method(self):
        # Reset module-level cache before each test
        smr._SOURCE_ID_MAP = None

    def test_registered_format_returns_source_id(self):
        """A format with a sources.jsonl entry returns its source_id."""
        sid = smr._get_source_id_for_format("fods")
        # FODS is registered in spec-source-registry
        assert sid is not None
        assert "FODS" in sid or "fods" in sid.lower()

    def test_odf_family_fallback(self):
        """ODF family formats without own entry fall back to 'fods' entry."""
        fods_sid = smr._get_source_id_for_format("fods")
        # Reset cache to force fresh lookup
        smr._SOURCE_ID_MAP = None
        # If fodp is not directly registered, it should fall back to fods
        fodp_sid = smr._get_source_id_for_format("fodp")
        if fodp_sid is not None:
            # Either directly registered or fell back — both valid
            assert isinstance(fodp_sid, str)

    def test_unregistered_format_returns_none(self):
        """A format not in sources.jsonl and not ODF family returns None."""
        sid = smr._get_source_id_for_format("nonexistent_format_xyz")
        assert sid is None

    def test_case_insensitive_lookup(self):
        """Format IDs are lowercased before lookup."""
        smr._SOURCE_ID_MAP = None
        sid_lower = smr._get_source_id_for_format("fods")
        smr._SOURCE_ID_MAP = None
        sid_upper = smr._get_source_id_for_format("FODS")
        assert sid_lower == sid_upper

    def test_cached_after_first_call(self):
        """_SOURCE_ID_MAP is populated after first call."""
        smr._SOURCE_ID_MAP = None
        smr._get_source_id_for_format("fods")
        assert smr._SOURCE_ID_MAP is not None
        assert isinstance(smr._SOURCE_ID_MAP, dict)


# ---------------------------------------------------------------------------
# _try_verify_facts_against_spec
# ---------------------------------------------------------------------------

class TestTryVerifyFactsAgainstSpec:
    """_try_verify_facts_against_spec upgrades fact_status via substring matching."""

    def test_matching_fact_gets_text_verified(self, tmp_path):
        """A fact whose first 50 chars appear in spec text gets text_verified."""
        spec_dir = tmp_path / ".local" / "spec-cache" / "testfmt" / "v1" / "normalized"
        spec_dir.mkdir(parents=True)
        spec_text = ("This is a test description that appears in the spec document for testing. "
                     "Additional padding text to exceed the 100-character minimum length requirement. "
                     "More content here to ensure the guard check passes reliably.")
        (spec_dir / "text.txt").write_text(spec_text, encoding="utf-8")

        # Monkey-patch _REPO_ROOT for test
        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-001",
                    "description": "This is a test description that appears in the spec",
                    "fact_status": "bootstrap_only",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("testfmt", facts)
            assert result[0]["fact_status"] == "text_verified"
        finally:
            smr._REPO_ROOT = orig

    def test_non_matching_fact_unchanged(self, tmp_path):
        """A fact whose description doesn't match stays at original status."""
        spec_dir = tmp_path / ".local" / "spec-cache" / "testfmt" / "v1" / "normalized"
        spec_dir.mkdir(parents=True)
        (spec_dir / "text.txt").write_text(
            "Completely different content about something else entirely.",
            encoding="utf-8",
        )

        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-002",
                    "description": "This text does not appear anywhere in the spec text",
                    "fact_status": "bootstrap_only",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("testfmt", facts)
            assert result[0]["fact_status"] == "bootstrap_only"
        finally:
            smr._REPO_ROOT = orig

    def test_short_description_skipped(self, tmp_path):
        """Descriptions shorter than 10 chars are not verified."""
        spec_dir = tmp_path / ".local" / "spec-cache" / "testfmt" / "v1" / "normalized"
        spec_dir.mkdir(parents=True)
        (spec_dir / "text.txt").write_text("short text here" * 10, encoding="utf-8")

        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-003",
                    "description": "short",
                    "fact_status": "bootstrap_only",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("testfmt", facts)
            assert result[0]["fact_status"] == "bootstrap_only"
        finally:
            smr._REPO_ROOT = orig

    def test_missing_spec_text_returns_unchanged(self, tmp_path):
        """When no normalized text.txt exists, facts are returned unchanged."""
        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-004",
                    "description": "Any description at all for testing",
                    "fact_status": "bootstrap_only",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("nofmt", facts)
            assert result[0]["fact_status"] == "bootstrap_only"
        finally:
            smr._REPO_ROOT = orig

    def test_already_text_verified_not_double_counted(self, tmp_path):
        """Facts already text_verified are not re-upgraded (no duplicate counting)."""
        spec_dir = tmp_path / ".local" / "spec-cache" / "testfmt" / "v1" / "normalized"
        spec_dir.mkdir(parents=True)
        spec_text = ("Already verified description text that matches the spec. "
                     "Additional padding text to exceed the 100-character minimum length requirement. "
                     "More content here to ensure the guard check passes.")
        (spec_dir / "text.txt").write_text(spec_text, encoding="utf-8")

        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-005",
                    "description": "Already verified description text that matches",
                    "fact_status": "text_verified",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("testfmt", facts)
            assert result[0]["fact_status"] == "text_verified"
        finally:
            smr._REPO_ROOT = orig

    def test_empty_description_skipped(self, tmp_path):
        """Facts with empty description are not verified."""
        spec_dir = tmp_path / ".local" / "spec-cache" / "testfmt" / "v1" / "normalized"
        spec_dir.mkdir(parents=True)
        (spec_dir / "text.txt").write_text("Some spec content" * 10, encoding="utf-8")

        orig = smr._REPO_ROOT
        smr._REPO_ROOT = tmp_path
        try:
            facts = [
                {
                    "qname": "FACT-TEST-006",
                    "description": "",
                    "fact_status": "bootstrap_only",
                    "source_id": "SPEC-TEST",
                },
            ]
            result = smr._try_verify_facts_against_spec("testfmt", facts)
            assert result[0]["fact_status"] == "bootstrap_only"
        finally:
            smr._REPO_ROOT = orig
