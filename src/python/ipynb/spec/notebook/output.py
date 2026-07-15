"""
ipynb structural element: ipynb:output

Spec ref: Jupyter nbformat v4.5 Specification
Fact ref: FACT-IPYNB-003
QName: ipynb:output
Canonical class: Output
Facade: IpynbOutput

architecture_only: this class is a spec-shaped scaffold. It wraps a single
code-cell output dict and exposes read-only properties for output_type
and the fields associated with each output_type variant (stream,
display_data, execute_result, error). No parsing or write behavior
lives here — that is owned by ``ipynb_codec``.
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

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Output(output_type={self.output_type!r})"
