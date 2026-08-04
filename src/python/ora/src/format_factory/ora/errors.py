"""OpenRaster error hierarchy.

Every error here descends from `format_factory.core`'s types, so a caller
handling `FormatParseError` across formats catches OpenRaster failures without
knowing this package exists.
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


class OraValidationError(FormatValidationError):
    """The archive is structurally sound but its content violates the format."""


class OraLimitError(ResourceLimitError):
    """A declared or observed resource bound was exceeded.

    Separate from `OraArchiveError` because the archive may be perfectly
    well-formed and simply larger than the caller allows -- that is a policy
    outcome, not a malformed file, and callers routinely want to retry with
    different limits rather than reject the input.
    """


__all__ = [
    "OraArchiveError",
    "OraError",
    "OraLimitError",
    "OraValidationError",
]
