"""
tests/repro/test_r82_reproduce_format_import_names.py

R82 Train F: Verify reproduce_format.py uses canonical import namespaces.

Defect fixed: D79-07 — tools/repro/reproduce_format.py used wrong import namespaces
(aspose_format_factory_fods instead of fods, etc.)
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPRO_TOOL = REPO_ROOT / "tools" / "repro" / "reproduce_format.py"


def _get_repro_source() -> str:
    return REPRO_TOOL.read_text(encoding="utf-8")


class TestReproFormatImportNamespaces:
    """Verify smoke scripts use canonical import namespaces (import fods, fodt, zst)."""

    def test_fods_smoke_uses_canonical_import(self):
        src = _get_repro_source()
        # Must use 'from fods import' not 'from aspose_format_factory_fods import'
        assert "from fods import" in src, "FODS smoke must use 'from fods import'"
        assert "aspose_format_factory_fods" not in src, \
            "Wrong namespace: aspose_format_factory_fods found in repro tool"

    def test_fodt_smoke_uses_canonical_import(self):
        src = _get_repro_source()
        assert "from fodt import" in src, "FODT smoke must use 'from fodt import'"
        assert "aspose_format_factory_fodt" not in src, \
            "Wrong namespace: aspose_format_factory_fodt found in repro tool"

    def test_zst_smoke_uses_canonical_import(self):
        src = _get_repro_source()
        assert "from zst import" in src, "ZST smoke must use 'from zst import'"
        assert "aspose_format_factory_zst" not in src, \
            "Wrong namespace: aspose_format_factory_zst found in repro tool"

    def test_canonical_namespace_table_present(self):
        src = _get_repro_source()
        assert "CANONICAL_IMPORT_NAMESPACES" in src, \
            "canonical namespace table must be defined in repro tool"

    def test_fodt_smoke_uses_root_blocks_not_body_blocks(self):
        src = _get_repro_source()
        # After GAP-FODT-STRUCT-001 fix, smoke must use root-level blocks
        assert 'doc = {"blocks": []}' in src, \
            "FODT smoke must use root-level blocks (GAP-FODT-STRUCT-001 fix)"
        assert 'doc = {"body": {"blocks": []}}' not in src, \
            "FODT smoke must not use body.blocks (old structure, pre-fix)"

    def test_repro_tool_has_require_wheel_option(self):
        src = _get_repro_source()
        assert "--require-wheel" in src, "repro tool must have --require-wheel option"

    def test_repro_tool_has_package_artifacts_dir_option(self):
        src = _get_repro_source()
        assert "--package-artifacts-dir" in src, \
            "repro tool must have --package-artifacts-dir option"

    def test_repro_tool_has_no_network_option(self):
        src = _get_repro_source()
        assert "--no-network" in src, "repro tool must have --no-network option"
