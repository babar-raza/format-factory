"""ABW spec Paragraph — canonical implementation of abw:p.

spec_qname: abw:p
spec_fact_ref: FACT-ABW-003
Spec ref: AbiWord AWML 1.0 — paragraph block element
Facade: AbwParagraph (Compat/abw_paragraph.py)
"""
from __future__ import annotations
from typing import ClassVar


class Paragraph:
    """Canonical implementation of the abw:p paragraph element.

    A paragraph contains plain text (with optional inline character runs
    merged into the text string by the neutral model parser).
    """

    spec_qname: ClassVar[str] = "abiword:p"
    spec_fact_ref: ClassVar[str] = "FACT-ABW-003"
    namespace_uri: ClassVar[str] = "http://www.abisource.com/awml/"
    local_name: ClassVar[str] = "p"
    facade_names: ClassVar[list] = ["AbwParagraph"]

    def __init__(self, text: str):
        self._text = str(text) if text is not None else ""

    @property
    def text(self) -> str:
        return self._text

    @property
    def word_count(self) -> int:
        return len(self._text.split()) if self._text.strip() else 0

    @property
    def char_count(self) -> int:
        return len(self._text)

    def is_empty(self) -> bool:
        return not self._text.strip()

    def words(self) -> list[str]:
        return self._text.split()

    def to_dict(self) -> dict:
        return {"text": self._text}

    def __repr__(self) -> str:
        preview = self._text[:40] + "..." if len(self._text) > 40 else self._text
        return f"Paragraph(text={preview!r})"
