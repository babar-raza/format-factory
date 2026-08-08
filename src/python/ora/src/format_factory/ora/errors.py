"""OpenRaster error hierarchy.

Every error here descends from `format_factory.core`'s types, so a caller
handling `FormatParseError` across formats catches OpenRaster failures without
knowing this package exists. `OraValidationError` and `OraLimitError` also
descend from `OraError` itself (multiple inheritance), matching the pattern
every other FF6 format's own error hierarchy uses -- a bare
``except OraError`` is meant to mean "any OpenRaster failure," and a caller
relying on that should not have to separately remember `OraValidationError`/
`OraLimitError` as unrelated types. (An earlier version of this file didn't
follow that pattern, which let `lifecycle.py`'s own `validate()` -- documented
to never raise -- crash uncaught on a malformed stack.xml or an unreadable
thumbnail/merged-image asset. Fixed together with the affected call sites.)
"""

from __future__ import annotations

from format_factory.core import FormatParseError, FormatValidationError, ResourceLimitError


class OraError(FormatParseError):
    """Base class for every OpenRaster failure raised while reading."""


class OraArchiveError(OraError):
    """The ZIP wrapper or its member directory is not a valid OpenRaster archive.

    Raised before any payload is decompressed. Covers a missing or misplaced
    mimetype sentinel, a traversal or absolute member name, duplicate members,
    an unsupported compression method, and a truncated or non-ZIP input.
    """


class OraValidationError(FormatValidationError, OraError):
    """The archive is structurally sound but its content violates the format.

    Also an `OraError` (multiple inheritance, matching the pattern every
    other FF6 format's own error hierarchy uses -- see e.g. `NrrdParseError`,
    `XliffValidationError`): a bare ``except OraError`` at a call site that
    only means "any OpenRaster failure" must actually catch this, not
    silently miss it the way `lifecycle.py`'s own `validate()` once did.
    """


class OraLimitError(ResourceLimitError, OraError):
    """A declared or observed resource bound was exceeded.

    Separate from `OraArchiveError` because the archive may be perfectly
    well-formed and simply larger than the caller allows -- that is a policy
    outcome, not a malformed file, and callers routinely want to retry with
    different limits rather than reject the input. Also an `OraError` for
    the same reason as `OraValidationError` above.
    """


__all__ = [
    "OraArchiveError",
    "OraError",
    "OraLimitError",
    "OraValidationError",
]
