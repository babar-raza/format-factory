"""
tests/evidence/test_r82_rejects_wrong_repro_imports.py

R82 Train P: reproduce_format.py must not use aspose_format_factory_* import namespaces.

Defect fixed: D79-07.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPRO_TOOL = REPO_ROOT / "tools" / "repro" / "reproduce_format.py"

WRONG_NAMESPACES = [
    "aspose_format_factory_fods",
    "aspose_format_factory_fodt",
    "aspose_format_factory_zst",
    "aspose_format_factory_pbm",
    "aspose_format_factory_pgm",
    "aspose_format_factory_sylk",
]


class TestRejectWrongReproImports:
    """reproduce_format.py must use canonical import namespaces."""

    def test_no_wrong_namespace_in_repro_tool(self):
        src = REPRO_TOOL.read_text(encoding="utf-8")
        for ns in WRONG_NAMESPACES:
            assert ns not in src, (
                f"reproduce_format.py contains wrong import namespace: '{ns}'. "
                f"Must use canonical module name (e.g. 'fods' not 'aspose_format_factory_fods')"
            )

    def test_fods_canonical_namespace_present(self):
        src = REPRO_TOOL.read_text(encoding="utf-8")
        assert "from fods import" in src

    def test_fodt_canonical_namespace_present(self):
        src = REPRO_TOOL.read_text(encoding="utf-8")
        assert "from fodt import" in src

    def test_zst_canonical_namespace_present(self):
        src = REPRO_TOOL.read_text(encoding="utf-8")
        assert "from zst import" in src
