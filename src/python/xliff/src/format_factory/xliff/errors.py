"""XLIFF exception hierarchy."""

from format_factory.core import (
    FormatFactoryError,
    FormatParseError,
    FormatValidationError,
    FormatWriteError,
)


class XliffError(FormatFactoryError):
    """Base exception for XLIFF operations."""


class XliffParseError(FormatParseError, XliffError):
    """The input is malformed, unsafe, or outside the selected profile."""


class XliffWriteError(FormatWriteError, XliffError):
    """The document cannot be serialized without violating its profile."""


class XliffValidationError(FormatValidationError, XliffError):
    """The document violates an XLIFF processing invariant."""


class SchemaValidationUnavailable(XliffError):
    """The optional `xmlschema` dependency is not installed.

    Install the ``schema`` extra (``pip install format-factory-xliff[schema]``)
    to enable XSD conformance checking against the bundled core schema.
    """
