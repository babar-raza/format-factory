"""Exceptions for the mtlx codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class MtlxError(FormatFactoryError):
    """Base exception for mtlx operations."""


class MtlxParseError(MtlxError):
    """Raised when a mtlx file cannot be parsed."""


class MtlxWriteError(MtlxError):
    """Raised when a mtlx file cannot be written."""


class MtlxConnectionError(MtlxError):
    """Raised when a graph connection reference cannot be resolved.

    Covers: querying a node name that does not exist in the node graph,
    querying an input name that does not exist on a node, and a
    nodename/interfacename reference that points at a node absent from
    the graph (a dangling connection).
    """
