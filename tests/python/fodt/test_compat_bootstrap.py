"""KEY SAFETY TEST: Verify compat.py imports from models.py (bootstrap rule).

This is the critical guard against premature spec/ stub usage.
If compat.py accidentally imports from architecture_only stubs, FodtParagraph
will have no .kind, .text, .spans properties and ALL existing FODT tests break.

This test:
- Verifies compat.py imports succeed
- Verifies imported FodtParagraph has real properties (.kind, .text, .spans)
- Verifies the imported class comes from models.py (not spec/)
- If this test fails: compat.py has been switched to spec/ prematurely
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


class TestCompatFromModels:
    """Verify the imports come from models.py, not spec/ stubs."""

    def test_fodtparagraph_is_from_models(self):
        """FodtParagraph from compat must be the models.py class (not spec/ stub)."""
        from fodt.compat import FodtParagraph
        source_file = inspect.getfile(FodtParagraph)
        assert "models" in source_file, (
            f"FodtParagraph imported from wrong file: {source_file}\n"
            "Expected models.py — compat.py may have been prematurely switched to spec/ stubs"
        )
        assert "spec" not in source_file.replace("spec_", "").replace("spec_fact", ""), (
            f"FodtParagraph appears to come from spec/ stubs: {source_file}\n"
            "Bootstrap rule violation: compat.py must use models.py until stubs are implemented"
        )

    def test_fodtspan_is_from_models(self):
        """FodtSpan from compat must be the models.py class."""
        from fodt.compat import FodtSpan
        source_file = inspect.getfile(FodtSpan)
        assert "models" in source_file, (
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
