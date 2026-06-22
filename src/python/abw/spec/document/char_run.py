"""ABW spec CharRun — canonical implementation of abw:c.

spec_qname: abw:c
spec_fact_ref: FACT-ABW-004
Spec ref: AbiWord AWML 1.0 — character run inline element
"""
from __future__ import annotations


class CharRun:
    """Canonical implementation of the abw:c character run element.

    A character run is an inline element within a paragraph carrying
    formatting attributes (bold, italic, color, font, size, etc.).
    The neutral model merges character run text into the paragraph string,
    so this class operates on the raw attribute dict when available.
    """

    spec_qname = "abw:c"
    spec_fact_ref = "FACT-ABW-004"
    namespace_uri = "http://www.abisource.com/awml/"
    local_name = "c"
    facade_names = []

    def __init__(self, text: str, props: dict | None = None):
        self._text = str(text) if text is not None else ""
        self._props = dict(props) if props else {}

    @property
    def text(self) -> str:
        return self._text

    @property
    def props(self) -> dict:
        return dict(self._props)

    def is_bold(self) -> bool:
        return self._props.get("font-weight", "") == "bold"

    def is_italic(self) -> bool:
        return self._props.get("font-style", "") == "italic"

    def to_dict(self) -> dict:
        return {"text": self._text, "props": self._props}

    def __repr__(self) -> str:
        return f"CharRun(text={self._text!r})"
