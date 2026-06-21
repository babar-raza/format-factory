"""TC-EXEC-005 (FODT part): FODT source-tree install proof.

Verifies module importability and core API functionality from the source tree.
Note: This is D6.5 proof (source-tree import), not D7 (wheel-install).
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_FODT_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"


class TestFodtInstallProof:
    def test_fodt_module_importable(self):
        """src.python.fodt is importable and has core attributes."""
        import src.python.fodt as fodt_mod
        assert fodt_mod is not None
        assert hasattr(fodt_mod, "parse_fodt_strict")
        assert hasattr(fodt_mod, "write_fodt")
        assert hasattr(fodt_mod, "document_text_content")

    def test_fodt_version_set(self):
        """__version__ is set and not a zero placeholder."""
        from src.python.fodt import __version__
        assert __version__ is not None
        assert __version__ != "0.0.0"
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_parse_fodt_strict_on_real_sample(self):
        """parse_fodt_strict on a real .fodt file returns a document dict."""
        if not _FODT_SAMPLE.exists():
            pytest.skip(f"Sample not found: {_FODT_SAMPLE}")
        from src.python.fodt import parse_fodt_strict
        doc = parse_fodt_strict(str(_FODT_SAMPLE))
        assert isinstance(doc, dict)
        assert "blocks" in doc

    def test_write_fodt_produces_file(self):
        """write_fodt produces a non-empty file."""
        from src.python.fodt import write_fodt
        document = {"blocks": [{"type": "paragraph", "text": "Install proof."}]}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out.fodt"
            write_fodt(document, out)
            assert out.exists()
            assert out.stat().st_size > 100

    def test_document_text_content_returns_string(self):
        """document_text_content on a parsed document returns a string."""
        if not _FODT_SAMPLE.exists():
            pytest.skip(f"Sample not found: {_FODT_SAMPLE}")
        from src.python.fodt import parse_fodt_strict, document_text_content
        doc = parse_fodt_strict(str(_FODT_SAMPLE))
        text = document_text_content(doc)
        assert isinstance(text, str)
