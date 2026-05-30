"""
tests/python/abw/test_r76_abw_advancement.py

R76 Train N — ABW (AbiWord) shallow track drift correction.

Adds new ABW coverage using in-memory bytes:
- load() from bytes
- get_section_count() on minimal document
- get_paragraph_count() on document with paragraphs
- extract_text() returns paragraph text
- DOCTYPE stripping (security: no external DTD fetch)

Sprint: FORMAT-FACTORY-R76-PARALLEL-FINISH-LINE-ARTIFACT-AUTHORITY-PRODUCT-DEEPENING-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.abw.abw_codec import load, get_section_count, get_paragraph_count, extract_text


_MINIMAL_ABW = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<abiword version="1.9.2">
  <section>
    <p>First paragraph R76.</p>
    <p>Second paragraph.</p>
  </section>
</abiword>
"""

_ABW_WITH_DOCTYPE = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE abiword PUBLIC "-//ABISOURCE//DTD AWML 1.0//EN" "http://www.abisource.com/awml.dtd">
<abiword version="1.9.2">
  <section>
    <p>With DOCTYPE.</p>
  </section>
</abiword>
"""

_TWO_SECTION_ABW = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<abiword version="1.9.2">
  <section><p>Section one.</p></section>
  <section><p>Section two.</p></section>
</abiword>
"""


class TestAbwLoadFromBytes:
    def test_load_returns_dict(self):
        result = load(_MINIMAL_ABW)
        assert isinstance(result, dict)

    def test_load_with_doctype_does_not_crash(self):
        """DOCTYPE is stripped before parsing — should not fetch external DTD."""
        result = load(_ABW_WITH_DOCTYPE)
        assert isinstance(result, dict)


class TestAbwSectionCount:
    def test_one_section(self):
        count = get_section_count(_MINIMAL_ABW)
        assert count == 1

    def test_two_sections(self):
        count = get_section_count(_TWO_SECTION_ABW)
        assert count == 2


class TestAbwParagraphCount:
    def test_two_paragraphs(self):
        count = get_paragraph_count(_MINIMAL_ABW)
        assert count == 2

    def test_zero_in_empty_section(self):
        empty = b'<?xml version="1.0"?><abiword version="1.9.2"><section/></abiword>'
        count = get_paragraph_count(empty)
        assert count == 0


class TestAbwExtractText:
    def test_returns_list(self):
        texts = extract_text(_MINIMAL_ABW)
        assert isinstance(texts, list)

    def test_finds_paragraph_text(self):
        texts = extract_text(_MINIMAL_ABW)
        combined = " ".join(texts)
        assert "First paragraph R76" in combined
