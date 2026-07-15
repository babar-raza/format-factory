"""Tests for markdown/raw cell attachments support (FACT-IPYNB-102).

Prior to this fix, ``attachments`` (embedded base64 image data referenced
by markdown cells) was silently discarded on write because write_ipynb
rebuilt each cell from an explicit key allow-list that omitted it. These
tests prove attachments now survive a real load/write/reload cycle,
byte-for-byte, and remain scoped to non-code cells.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ipynb.ipynb_codec import load_ipynb, write_ipynb
from ipynb.models import IpynbDocument

# A real base64-encoded 1x1 transparent PNG, used as realistic attachment
# payload bytes (not just a placeholder string).
PNG_1X1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _markdown_cell_with_attachment() -> dict:
    return {
        "cell_type": "markdown",
        "source": "![img](attachment:pixel.png)",
        "metadata": {},
        "attachments": {
            "pixel.png": {"image/png": PNG_1X1_BASE64}
        },
    }


class TestAttachmentsRoundTrip:
    def test_attachment_survives_load_write_reload(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [_markdown_cell_with_attachment()],
        }

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.ipynb"
            src.write_text(json.dumps(model), encoding="utf-8")

            loaded = load_ipynb(src)
            assert loaded["cells"][0]["attachments"]["pixel.png"]["image/png"] == PNG_1X1_BASE64

            dest = Path(td) / "dest.ipynb"
            write_ipynb(loaded, dest)
            reloaded = load_ipynb(dest)

        # Byte-for-byte: the exact same base64 string, not merely "some" attachment.
        assert reloaded["cells"][0]["attachments"]["pixel.png"]["image/png"] == PNG_1X1_BASE64

    def test_attachment_present_in_raw_written_json(self):
        """Confirm the bytes actually on disk carry attachments, not just
        the in-memory model (guards against an in-memory-only fix)."""
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [_markdown_cell_with_attachment()],
        }
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ipynb"
            write_ipynb(model, dest)
            raw = json.loads(dest.read_text(encoding="utf-8"))

        assert raw["cells"][0]["attachments"] == {
            "pixel.png": {"image/png": PNG_1X1_BASE64}
        }

    def test_raw_cell_attachment_also_survives(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "raw",
                    "source": "raw content",
                    "metadata": {},
                    "attachments": {"note.txt": {"text/plain": "aGVsbG8="}},
                }
            ],
        }
        result = json.loads(write_ipynb(model))
        assert result["cells"][0]["attachments"]["note.txt"]["text/plain"] == "aGVsbG8="

    def test_code_cell_attachments_key_not_fabricated(self):
        """Spec: attachments is only valid on markdown/raw cells. Code
        cells that never had one should not gain a spurious empty dict."""
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "code", "source": "x = 1", "metadata": {}}],
        }
        result = json.loads(write_ipynb(model))
        assert "attachments" not in result["cells"][0]

    def test_cell_without_attachments_unaffected(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{"cell_type": "markdown", "source": "no attachment here", "metadata": {}}],
        }
        result = json.loads(write_ipynb(model))
        assert "attachments" not in result["cells"][0]

    def test_multiple_mime_types_within_one_attachment(self):
        model = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": "multi",
                    "metadata": {},
                    "attachments": {
                        "fig.png": {
                            "image/png": PNG_1X1_BASE64,
                            "text/plain": "<image>",
                        }
                    },
                }
            ],
        }
        result = json.loads(write_ipynb(model))
        fig = result["cells"][0]["attachments"]["fig.png"]
        assert fig["image/png"] == PNG_1X1_BASE64
        assert fig["text/plain"] == "<image>"

    def test_cell_class_attachments_property(self):
        from ipynb.spec.notebook.cell import Cell

        cell = Cell(_markdown_cell_with_attachment())
        assert cell.attachments["pixel.png"]["image/png"] == PNG_1X1_BASE64

    def test_cell_class_attachments_defaults_empty(self):
        from ipynb.spec.notebook.cell import Cell

        cell = Cell({"cell_type": "code"})
        assert cell.attachments == {}

    def test_document_mutation_add_cell_with_attachments_via_metadata_path(self):
        """IpynbDocument.add_cell doesn't special-case attachments (they're
        optional), but a caller-populated attachments dict on a manually
        appended cell must still survive a save/reload — proving the
        write path isn't allow-listing fields anymore."""
        doc = IpynbDocument({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []})
        doc.cells.append(_markdown_cell_with_attachment())

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "m.ipynb"
            write_ipynb(doc.to_dict(), dest)
            reloaded = load_ipynb(dest)

        assert reloaded["cells"][0]["attachments"]["pixel.png"]["image/png"] == PNG_1X1_BASE64
