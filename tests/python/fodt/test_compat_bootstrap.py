"""SAFETY TEST: Verify compat.py imports from spec/ stubs (post-switch state).

TC-FODT-002: compat.py has been switched from models.py to spec/ imports.
The spec/ stubs (Paragraph, Span, Heading) are fully implemented and
behaviourally equivalent to models.py — verified in TestSpecStubBehavioralEquivalence.

This test:
- Verifies compat.py imports succeed
- Verifies imported FodtParagraph has real properties (.kind, .text, .spans)
- Verifies the imported class comes from spec/ (post-switch guard)
"""
import inspect
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent.parent
_PYTHON_SRC = _REPO / "src" / "python"
if str(_PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(_PYTHON_SRC))


class TestCompatBootstrapImports:
    def test_compat_import_succeeds(self):
        """from fodt.compat import FodtParagraph must succeed."""
        from fodt.compat import FodtParagraph
        assert FodtParagraph is not None, "FodtParagraph is None after compat import"

    def test_compat_fodtdocument_import_succeeds(self):
        """from fodt.compat import FodtDocument must succeed."""
        from fodt.compat import FodtDocument
        assert FodtDocument is not None, "FodtDocument is None after compat import"

    def test_compat_fodtspan_import_succeeds(self):
        """from fodt.compat import FodtSpan must succeed."""
        from fodt.compat import FodtSpan
        assert FodtSpan is not None, "FodtSpan is None after compat import"

    def test_compat_all_exports(self):
        """compat.__all__ must export FodtDocument, FodtParagraph, FodtSpan."""
        import fodt.compat as compat
        assert "FodtParagraph" in compat.__all__
        assert "FodtDocument" in compat.__all__
        assert "FodtSpan" in compat.__all__


class TestCompatFromSpec:
    """Verify the imports come from spec/ stubs (TC-FODT-002 post-switch guard)."""

    def test_fodtparagraph_is_from_spec(self):
        """FodtParagraph from compat must be the spec/text/paragraph.py class."""
        from fodt.compat import FodtParagraph
        source_file = inspect.getfile(FodtParagraph)
        assert "spec" in source_file, (
            f"FodtParagraph imported from wrong file: {source_file}\n"
            "Expected spec/text/paragraph.py — compat.py switch may not have completed"
        )

    def test_fodtspan_is_from_spec(self):
        """FodtSpan from compat must be the spec/text/span.py class."""
        from fodt.compat import FodtSpan
        source_file = inspect.getfile(FodtSpan)
        assert "spec" in source_file, (
            f"FodtSpan imported from wrong file: {source_file}"
        )


class TestCompatRealProperties:
    """Verify the imported classes have real properties (not empty architecture_only stubs)."""

    def test_fodtparagraph_has_kind_property(self):
        """FodtParagraph from compat must have a .kind property."""
        from fodt.compat import FodtParagraph
        assert hasattr(FodtParagraph, "kind") or "kind" in dir(FodtParagraph), (
            "FodtParagraph has no .kind property — may be importing architecture_only stub"
        )

    def test_fodtparagraph_has_text_property(self):
        """FodtParagraph from compat must have a .text property."""
        from fodt.compat import FodtParagraph
        assert hasattr(FodtParagraph, "text") or "text" in dir(FodtParagraph), (
            "FodtParagraph has no .text property — may be importing architecture_only stub"
        )

    def test_fodtparagraph_has_spans_property(self):
        """FodtParagraph from compat must have a .spans property."""
        from fodt.compat import FodtParagraph
        assert hasattr(FodtParagraph, "spans") or "spans" in dir(FodtParagraph), (
            "FodtParagraph has no .spans property — may be importing architecture_only stub"
        )

    def test_fodtspan_has_text_property(self):
        """FodtSpan from compat must have a .text property."""
        from fodt.compat import FodtSpan
        assert hasattr(FodtSpan, "text") or "text" in dir(FodtSpan), (
            "FodtSpan has no .text property — may be importing architecture_only stub"
        )


class TestSpecStubBehavioralEquivalence:
    """TC-FODT-001: spec/ Paragraph/Heading/Span must be behaviourally equivalent to models.py."""

    _PARA_DATA = {"kind": "paragraph", "text": "Hello world", "style_name": "Text_Body",
                  "spans": [{"text": "Hello", "style_name": "Bold"}]}
    _HEAD_DATA = {"kind": "heading", "text": "My Heading", "style_name": "Heading_1",
                  "outline_level": 2, "spans": []}
    _SPAN_DATA = {"text": "World", "style_name": "Emphasis"}

    def test_paragraph_spec_equivalent_to_models(self):
        """spec/ Paragraph has same .kind, .text, .style_name, .outline_level as FodtParagraph."""
        from fodt.models import FodtParagraph
        from fodt.spec.text.paragraph import Paragraph
        m = FodtParagraph(self._PARA_DATA)
        s = Paragraph(self._PARA_DATA)
        assert s.kind == m.kind
        assert s.text == m.text
        assert s.style_name == m.style_name
        assert s.outline_level == m.outline_level

    def test_paragraph_spec_spans_match_models(self):
        """spec/ Paragraph.spans has same text/style_name as FodtParagraph.spans."""
        from fodt.models import FodtParagraph
        from fodt.spec.text.paragraph import Paragraph
        m = FodtParagraph(self._PARA_DATA)
        s = Paragraph(self._PARA_DATA)
        assert len(s.spans) == len(m.spans)
        if s.spans:
            assert s.spans[0].text == m.spans[0].text
            assert s.spans[0].style_name == m.spans[0].style_name

    def test_heading_spec_equivalent_to_models_heading(self):
        """spec/ Heading has same .text, .outline_level as FodtParagraph heading."""
        from fodt.models import FodtParagraph
        from fodt.spec.text.heading import Heading
        m = FodtParagraph(self._HEAD_DATA)
        h = Heading(self._HEAD_DATA)
        assert h.text == m.text
        assert h.outline_level == m.outline_level
        assert h.kind == "heading"

    def test_span_spec_equivalent_to_models(self):
        """spec/ Span has same .text, .style_name as FodtSpan."""
        from fodt.models import FodtSpan
        from fodt.spec.text.span import Span
        m = FodtSpan(self._SPAN_DATA)
        s = Span(self._SPAN_DATA)
        assert s.text == m.text
        assert s.style_name == m.style_name


class TestCompatSwitchGuard:
    """TC-FODT-003: Guard tests that prevent future regression back to models.py imports."""

    def test_compat_imports_from_spec(self):
        """FodtParagraph.__module__ must contain 'spec' — not 'models'."""
        from fodt.compat import FodtParagraph
        assert "spec" in FodtParagraph.__module__, (
            f"FodtParagraph module is {FodtParagraph.__module__!r} — expected spec/. "
            "compat.py may have been reverted to models.py imports."
        )
        assert "models" not in FodtParagraph.__module__, (
            f"FodtParagraph still from models.py: {FodtParagraph.__module__!r}"
        )

    def test_spec_stub_status_in_registry(self):
        """fodt.yaml must show text:p, text:h, text:span as status: implemented."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")
        registry_path = _REPO / "shared" / "qname-registry" / "fodt.yaml"
        assert registry_path.exists(), f"fodt.yaml missing at {registry_path}"
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        by_qname = {e["qname"]: e for e in entries if e}
        for qname in ("text:p", "text:h", "text:span"):
            assert qname in by_qname, f"{qname} not in fodt.yaml"
            status = by_qname[qname].get("status")
            assert status == "implemented", (
                f"{qname} has status={status!r} in fodt.yaml — expected 'implemented'"
            )

    def test_compat_not_regressed_has_kind(self):
        """FodtParagraph from compat still has .kind, .text, .spans (no regression)."""
        from fodt.compat import FodtParagraph
        p = FodtParagraph({"kind": "paragraph", "text": "test", "spans": []})
        assert p.kind == "paragraph"
        assert p.text == "test"
        assert p.spans == []
