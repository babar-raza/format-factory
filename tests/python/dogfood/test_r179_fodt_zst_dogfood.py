"""
test_r179_fodt_zst_dogfood.py -- Dogfood pipeline: FODT parse → text/headings → ZST compress.

Pipeline proof: parse a real FODT document, extract text using new Sprint 3 functions
(document_paragraph_texts, document_heading_texts, document_table_row_count), then
round-trip the extracted content through ZST compress/decompress.

Sprint: FORMAT-FACTORY-SAL-PHASE3-PRODUCT-DEEPENING-SPRINT3-001
Dogfood coverage:
  - FODT Sprint 3 functions used in real pipeline
  - ZST compress/decompress wraps FODT-extracted text
  - Full round-trip: file → parse → extract → compress → decompress → verify
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_paragraph_texts,
    document_heading_texts,
    document_table_row_count,
    document_text_content,
)
from zst.zst_codec import compress_string, decompress_to_string, compress_bytes, decompress_bytes

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_HEADINGS_FILE = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE_FILE = str(_SAMPLES / "table-basic.fodt")
_MINIMAL_FILE = str(_SAMPLES / "minimal-document.fodt")


class TestFodtZstPipeline:
    """Dogfood: FODT parse → extract → ZST compress → decompress."""

    def test_paragraph_texts_zst_roundtrip(self):
        """Parse FODT, extract paragraph texts, compress all as joined string, recover exact text."""
        doc = parse_fodt(_HEADINGS_FILE)
        paragraphs = document_paragraph_texts(doc)
        assert isinstance(paragraphs, list)
        joined = "\n".join(paragraphs)
        # Compress and decompress
        compressed = compress_string(joined)
        recovered = decompress_to_string(compressed)
        assert recovered == joined

    def test_heading_texts_zst_roundtrip(self):
        """Parse FODT, extract heading texts, compress as bytes, recover exact content."""
        doc = parse_fodt(_HEADINGS_FILE)
        headings = document_heading_texts(doc)
        assert len(headings) >= 1
        payload = "|".join(headings).encode("utf-8")
        compressed = compress_bytes(payload)
        recovered = decompress_bytes(compressed)
        assert recovered == payload

    def test_full_text_content_zst_roundtrip(self):
        """Full text content extraction + ZST round-trip produces exact original."""
        doc = parse_fodt(_HEADINGS_FILE)
        full_text = document_text_content(doc)
        assert isinstance(full_text, str)
        assert len(full_text) > 0
        # Compress and recover
        compressed = compress_string(full_text)
        recovered = decompress_to_string(compressed)
        assert recovered == full_text

    def test_table_row_count_feeds_pipeline(self):
        """Table row count from Sprint 3 can drive a ZST encoding of metadata."""
        doc = parse_fodt(_TABLE_FILE)
        row_count = document_table_row_count(doc, 0)
        assert isinstance(row_count, int)
        # Encode row_count as metadata and compress it
        metadata = f"table_index=0,row_count={row_count}".encode("utf-8")
        compressed = compress_bytes(metadata)
        recovered = decompress_bytes(compressed)
        assert recovered == metadata

    def test_empty_doc_produces_compressible_output(self):
        """Even an empty-content FODT document produces valid compressible output."""
        doc = parse_fodt(_MINIMAL_FILE)
        texts = document_paragraph_texts(doc)
        headings = document_heading_texts(doc)
        all_text = "\n".join(texts + headings)
        compressed = compress_string(all_text)
        recovered = decompress_to_string(compressed)
        assert recovered == all_text

    def test_sprint3_functions_agree_with_text_content(self):
        """paragraph_texts + heading_texts combined must not produce more words than text_content."""
        doc = parse_fodt(_HEADINGS_FILE)
        para_texts = document_paragraph_texts(doc)
        head_texts = document_heading_texts(doc)
        combined = " ".join(para_texts + head_texts)
        full = document_text_content(doc)
        # Combined word count <= full word count (full includes list/table text too)
        combined_words = len(combined.split())
        full_words = len(full.split())
        assert combined_words <= full_words + 5  # small tolerance for whitespace splits
