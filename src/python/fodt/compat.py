# src/python/fodt/compat.py — TC-PH-005: unified re-exports from Compat/ layer
#
# This module is the backward-compat shim. All names now resolve to the
# spec-backed production facades in fodt/Compat/. Do NOT add new names here —
# use fodt.Compat directly for new code.

try:
    from .Compat import (
        FodtDocument,
        FodtParagraph,
        FodtHeading,
        FodtSpan,
        FodtTableCell,
    )
except ImportError:
    FodtDocument = None  # type: ignore[assignment]
    FodtParagraph = None  # type: ignore[assignment]
    FodtHeading = None  # type: ignore[assignment]
    FodtSpan = None  # type: ignore[assignment]
    FodtTableCell = None  # type: ignore[assignment]

__all__ = ["FodtDocument", "FodtParagraph", "FodtHeading", "FodtSpan", "FodtTableCell"]
