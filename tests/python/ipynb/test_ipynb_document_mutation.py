"""Semantic mutation roundtrip test for ipynb: edit-survives-reload.

Distinct from the existing identity roundtrip test in test_ipynb_codec.py
(``TestRoundtrip.test_roundtrip_minimal``), which only proves an unchanged
load -> write -> load cycle. This test mutates the document (appends a
new markdown cell) before saving, and asserts the mutation is present
after a full save + reload cycle.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from ipynb.ipynb_codec import write_ipynb
from ipynb.models import IpynbDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"


class TestMutationRoundtrip:
    def test_append_markdown_cell_survives_reload(self):
        """load -> append markdown cell -> save -> reload: new cell present."""
        doc = IpynbDocument.from_file(str(VALID_DIR / "minimal.ipynb"))
        original_count = doc.cell_count
        doc.cells.append({"cell_type": "markdown", "source": "New cell", "metadata": {}})

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = IpynbDocument.from_file(str(dest))

            assert reloaded.cell_count == original_count + 1
            sources = [c.get("source") for c in reloaded.cells]
            assert "New cell" in sources

    def test_appended_cell_type_is_markdown(self):
        doc = IpynbDocument.from_file(str(VALID_DIR / "minimal.ipynb"))
        doc.cells.append({"cell_type": "markdown", "source": "Another cell", "metadata": {}})

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated2.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = IpynbDocument.from_file(str(dest))

            new_cell = reloaded.markdown_cells[-1]
            assert new_cell["cell_type"] == "markdown"
            assert new_cell["source"] == "Another cell"

    def test_original_cells_preserved_after_mutation(self):
        doc = IpynbDocument.from_file(str(VALID_DIR / "code-and-markdown.ipynb"))
        original_sources = [c.get("source") for c in doc.cells]
        doc.cells.append({"cell_type": "markdown", "source": "Appended", "metadata": {}})

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated3.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = IpynbDocument.from_file(str(dest))

            reloaded_sources = [c.get("source") for c in reloaded.cells]
            for original in original_sources:
                assert original in reloaded_sources

    def test_mutation_increases_markdown_count(self):
        doc = IpynbDocument.from_file(str(VALID_DIR / "with-outputs.ipynb"))
        original_markdown_count = len(doc.markdown_cells)
        doc.cells.append({"cell_type": "markdown", "source": "M", "metadata": {}})

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated4.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = IpynbDocument.from_file(str(dest))

            assert len(reloaded.markdown_cells) == original_markdown_count + 1
