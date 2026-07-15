"""
ipynb structural element: ipynb:output

Spec ref: Jupyter nbformat v4.5 Specification
Fact ref: FACT-IPYNB-003
QName: ipynb:output
Canonical class: Output
Facade: IpynbOutput

Real, wired-in production class: wraps a single code-cell output dict and
exposes read-only properties for output_type and the fields associated
with each output_type variant (stream, display_data, execute_result,
error), plus a real mutation API (get_representation/add_representation/
remove_representation) for the multi-representation MIME ``data`` bundle
carried by display_data/execute_result outputs. Top-level parsing/writing
of the notebook document itself remains owned by ``ipynb_codec`` — but the
module-level get_output_representation/add_output_representation/
remove_output_mime_type helpers there are thin wrappers over this class,
so Output is the single implementation of MIME-bundle mutation, not a
parallel/dead-code path.
"""
from __future__ import annotations

from typing import Any


class Output:
    """Canonical spec-shaped class for ipynb:output (a code cell output)."""

    spec_qname = "ipynb:output"
    spec_fact_ref = "FACT-IPYNB-003"
    namespace_uri = "urn:format:ipynb:4.5"
    local_name = "output"
    facade_names = ["IpynbOutput"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def output_type(self) -> str:
        """Return the output type: stream, display_data, execute_result, or error."""
        return self._data.get("output_type", "")

    @property
    def data(self) -> dict[str, Any]:
        """Return the MIME-bundle data dict (display_data/execute_result outputs)."""
        return self._data.get("data", {})

    @property
    def text(self) -> Any:
        """Return the stream text (stream outputs)."""
        return self._data.get("text", "")

    @property
    def name(self) -> str:
        """Return the stream name, e.g. 'stdout' or 'stderr' (stream outputs)."""
        return self._data.get("name", "")

    @property
    def ename(self) -> str:
        """Return the exception name (error outputs)."""
        return self._data.get("ename", "")

    @property
    def evalue(self) -> str:
        """Return the exception value/message (error outputs)."""
        return self._data.get("evalue", "")

    @property
    def traceback(self) -> list[str]:
        """Return the list of traceback line strings (error outputs)."""
        return self._data.get("traceback", [])

    def get_representation(self, mime_type: str) -> Any:
        """Return the value for ``mime_type`` in this output's ``data`` bundle.

        Returns None if there is no ``data`` bundle or ``mime_type`` is not
        present in it. Applies to display_data/execute_result outputs.
        """
        return self.data.get(mime_type)

    def add_representation(self, mime_type: str, value: Any) -> None:
        """Add or replace a MIME representation in this output's ``data`` bundle.

        Mutates the underlying output dict in place, creating the ``data``
        key if it does not yet exist. Other MIME representations already
        present in the bundle are left untouched.
        """
        bundle = self._data.setdefault("data", {})
        bundle[mime_type] = value

    def remove_representation(self, mime_type: str) -> bool:
        """Remove a MIME representation from this output's ``data`` bundle.

        Mutates the underlying output dict in place. Returns True if
        ``mime_type`` was present and removed, False otherwise (no-op —
        other representations are left untouched either way).
        """
        bundle = self._data.get("data")
        if isinstance(bundle, dict) and mime_type in bundle:
            del bundle[mime_type]
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Output(output_type={self.output_type!r})"
