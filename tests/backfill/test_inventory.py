"""Tests for TC-MACH-BACK-001: Backfill inventory scanner.

Verifies that:
- inventory.py scans FODS and finds production classes
- Classes have spec_qname populated for FODS (mature format)
- Compat/ and spec/ classes are flagged correctly
- Missing format returns error
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "backfill"))

from inventory import scan_format


class TestInventoryScanner:
    """TC-MACH-BACK-001 backfill inventory tests."""

    def test_fods_scan_finds_classes(self):
        """FODS scan produces >= 1 class entry."""
        result = scan_format("fods", repo_root=_REPO)
        assert "error" not in result or result.get("error") is None
        assert result["classes_found"] >= 1

    def test_fods_has_registry_entries(self):
        """FODS QName registry has entries."""
        result = scan_format("fods", repo_root=_REPO)
        assert result["registry_entries"] >= 1

    def test_fods_classes_have_spec_qname(self):
        """At least one FODS class has a spec_qname attribute."""
        result = scan_format("fods", repo_root=_REPO)
        classes_with_qname = [c for c in result["classes"] if c.get("spec_qname")]
        assert len(classes_with_qname) >= 1

    def test_compat_classes_flagged(self):
        """Compat/ classes are flagged as is_compat."""
        result = scan_format("fods", repo_root=_REPO)
        compat_classes = [c for c in result["classes"] if c["is_compat"]]
        # FODS has Compat/ facades
        assert len(compat_classes) >= 1
        for c in compat_classes:
            assert c["is_compat"] is True

    def test_missing_format_returns_error(self):
        """Non-existent format → error in result."""
        result = scan_format("nonexistent_format_xyz", repo_root=_REPO)
        assert result.get("error") is not None
        assert "not found" in result["error"].lower()

    def test_scan_result_schema(self):
        """Result dict has expected top-level keys."""
        result = scan_format("fods", repo_root=_REPO)
        for key in ["format", "format_dir", "registry_entries", "classes_found", "classes", "migration_needed"]:
            assert key in result, f"Missing key: {key}"
