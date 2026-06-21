"""End-to-end consumer path test for compat.py.

Proves the full chain:
  parse_fodt(real_file) → neutral_model dict → FodtDocument → FodtParagraph
  AND that compat.FodtParagraph is the SAME class as models.FodtParagraph.

This complements test_compat_bootstrap.py (which only tests import/attributes)
by exercising a real .fodt file through the complete parse chain.

TC-HARD-006 — Finding AF-006.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent.parent
_PYTHON_SRC = _REPO / "src" / "python"
if str(_PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(_PYTHON_SRC))

_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


@pytest.fixture(scope="module")
def fodt_doc():
    """Parse a real .fodt file and return FodtDocument."""
    pytest.importorskip("fodt")
    from fodt.parser import parse_fodt
    from fodt.models import FodtDocument
    neutral = parse_fodt(str(_SAMPLE))
    return FodtDocument(neutral)


@pytest.fixture(scope="module")
def compat_classes():
    from fodt.compat import FodtDocument, FodtParagraph, FodtSpan
    from fodt.models import FodtParagraph as ModelsParagraph
    return {"CompatParagraph": FodtParagraph, "ModelsParagraph": ModelsParagraph}


class TestSampleFileExists:
    def test_sample_fodt_file_exists(self):
        assert _SAMPLE.exists(), f"Sample .fodt file not found: {_SAMPLE}"


class TestParseAndDocument:
    def test_parse_returns_dict(self):
        from fodt.parser import parse_fodt
        result = parse_fodt(str(_SAMPLE))
        assert isinstance(result, dict), f"parse_fodt must return dict, got {type(result)}"

    def test_fodtdocument_wraps_neutral(self, fodt_doc):
        from fodt.models import FodtDocument
        assert isinstance(fodt_doc, FodtDocument)

    def test_block_count_nonzero(self, fodt_doc):
        assert fodt_doc.block_count > 0, "Document must have at least one block"

    def test_paragraphs_method_returns_list(self, fodt_doc):
        paras = fodt_doc.paragraphs()
        assert isinstance(paras, list), f"paragraphs() must return list, got {type(paras)}"
        assert len(paras) > 0, "Must have at least one paragraph"


class TestParagraphProperties:
    def test_paragraph_kind_is_string(self, fodt_doc):
        para = fodt_doc.paragraphs()[0]
        assert isinstance(para.kind, str), f"kind must be str, got {type(para.kind)}"

    def test_paragraph_text_is_string(self, fodt_doc):
        para = fodt_doc.paragraphs()[0]
        assert isinstance(para.text, str), f"text must be str, got {type(para.text)}"

    def test_paragraph_spans_is_list(self, fodt_doc):
        para = fodt_doc.paragraphs()[0]
        assert isinstance(para.spans, list), f"spans must be list, got {type(para.spans)}"

    def test_paragraph_kind_values_are_known(self, fodt_doc):
        known_kinds = {"paragraph", "heading"}
        for para in fodt_doc.paragraphs():
            assert para.kind in known_kinds, f"Unexpected paragraph kind: {para.kind!r}"


class TestCompatClassIdentity:
    def test_compat_paragraph_is_same_as_models_paragraph(self, compat_classes):
        """compat.FodtParagraph must be the identical class as models.FodtParagraph."""
        assert compat_classes["CompatParagraph"] is compat_classes["ModelsParagraph"], (
            "compat.FodtParagraph must be the same class as models.FodtParagraph "
            "(bootstrap rule: compat imports from models.py only)"
        )

    def test_paragraph_from_parse_is_compat_type(self, fodt_doc, compat_classes):
        """Paragraphs returned from FodtDocument.paragraphs() must be CompatParagraph instances."""
        CompatPara = compat_classes["CompatParagraph"]
        para = fodt_doc.paragraphs()[0]
        assert isinstance(para, CompatPara), (
            f"Paragraph type {type(para).__name__} is not an instance of compat.FodtParagraph. "
            "compat.py may be importing from wrong location."
        )
