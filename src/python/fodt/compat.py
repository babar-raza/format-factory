# src/python/fodt/compat.py — TC-FODT-002: SWITCHED to spec/ imports
#
# Switched from models.py to spec/ stubs after TC-FODT-001 confirmed
# behavioral equivalence (test_compat_bootstrap.py::TestSpecStubBehavioralEquivalence).
#
# text:p (Paragraph), text:h (Heading), text:span (Span) are now implemented in spec/.
# FodtDocument remains in models.py — no spec equivalent yet.
#
# Facade aliases (FodtParagraph, FodtSpan) are preserved for backward compatibility.

try:
    from .spec.text.paragraph import Paragraph as FodtParagraph
    from .spec.text.span import Span as FodtSpan
    from .models import FodtDocument
except ImportError:
    FodtDocument = None  # type: ignore[assignment]
    FodtParagraph = None  # type: ignore[assignment]
    FodtSpan = None  # type: ignore[assignment]

__all__ = ["FodtDocument", "FodtParagraph", "FodtSpan"]
