"""
tests/python/fodt/test_r49_object_model_poc.py

R49 FODT Python editable object-model POC tests.

Proves the full POC chain:
  load → object model → edit block → save same format → reload → verify edit + preservation

Also verifies the R49 writer fix: parser output (blocks key) can be written back
and reloaded correctly (headings preserved as headings).

Sprint: FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
"""

import copy
import tempfile
from pathlib import Path

import pytest

from fodt import parse_fodt, write_fodt, document_to_xml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sample_document() -> dict:
    """Build a minimal document with headings and paragraphs for POC editing."""
    return {
        "blocks": [
            {"type": "heading", "text": "Introduction", "heading_level": 1},
            {"type": "paragraph", "text": "First paragraph content."},
            {"type": "heading", "text": "Section Two", "heading_level": 1},
            {"type": "paragraph", "text": "Second paragraph content."},
            {"type": "paragraph", "text": "Third paragraph."},
        ]
    }


def _edit_block_text(document: dict, block_idx: int, new_text: str) -> dict:
    """Return a new document dict with the text of one block changed."""
    doc = copy.deepcopy(document)
    doc["blocks"][block_idx]["text"] = new_text
    return doc


# ---------------------------------------------------------------------------
# MT5 FODT writer fix: blocks key acceptance
# ---------------------------------------------------------------------------

class TestFodtWriterBlocksKeyFix:
    """R49 fix: writer now accepts 'blocks' key (parser canonical output)."""

    def test_writer_accepts_blocks_key(self):
        """document_to_xml must produce non-empty output when 'blocks' key is used."""
        import xml.etree.ElementTree as ET
        doc = {"blocks": [
            {"type": "paragraph", "text": "hello"},
        ]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        paras = root.findall(f".//{{{NS_T}}}p")
        assert len(paras) == 1, f"Expected 1 paragraph, got {len(paras)}"
        assert paras[0].text == "hello"

    def test_writer_emits_heading_for_heading_block(self):
        """Heading blocks must produce text:h elements, not text:p."""
        import xml.etree.ElementTree as ET
        doc = {"blocks": [
            {"type": "heading", "text": "My Heading", "heading_level": 2},
        ]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        headings = root.findall(f".//{{{NS_T}}}h")
        paras = root.findall(f".//{{{NS_T}}}p")
        assert len(headings) == 1, f"Expected 1 heading, got {len(headings)}"
        assert len(paras) == 0, f"Expected 0 paragraphs for heading block, got {len(paras)}"
        assert headings[0].text == "My Heading"

    def test_writer_heading_outline_level_attribute(self):
        """text:h must carry text:outline-level attribute matching heading_level."""
        import xml.etree.ElementTree as ET
        doc = {"blocks": [
            {"type": "heading", "text": "H2", "heading_level": 2},
        ]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        h = root.findall(f".//{{{NS_T}}}h")[0]
        level = h.get(f"{{{NS_T}}}outline-level")
        assert level == "2", f"Expected outline-level=2, got {level!r}"

    def test_writer_legacy_paragraphs_key_still_works(self):
        """Legacy 'paragraphs' key still produces valid output (backward compat)."""
        import xml.etree.ElementTree as ET
        doc = {"paragraphs": [{"text_content": "legacy paragraph"}]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        paras = root.findall(f".//{{{NS_T}}}p")
        assert len(paras) == 1

    def test_blocks_takes_precedence_over_paragraphs(self):
        """When both 'blocks' and 'paragraphs' are present, 'blocks' takes precedence."""
        import xml.etree.ElementTree as ET
        doc = {
            "blocks": [{"type": "paragraph", "text": "from blocks"}],
            "paragraphs": [{"text_content": "from paragraphs"}],
        }
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        paras = root.findall(f".//{{{NS_T}}}p")
        assert len(paras) == 1
        assert paras[0].text == "from blocks", (
            f"blocks key should take precedence; got {paras[0].text!r}"
        )

    def test_parser_output_produces_correct_xml(self):
        """Parser output passed directly to writer must produce correct headings and paragraphs."""
        import xml.etree.ElementTree as ET
        samples = list(Path("samples/by-format/fodt").glob("*.fodt"))
        src = next((s for s in samples if "heading" in s.name), None)
        if src is None:
            pytest.skip("No heading sample found")
        doc = parse_fodt(src)
        blocks = doc.get("blocks", [])
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        NS_T = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        headings = root.findall(f".//{{{NS_T}}}h")
        paras = root.findall(f".//{{{NS_T}}}p")
        expected_h = sum(1 for b in blocks if b.get("type") == "heading")
        expected_p = sum(1 for b in blocks if b.get("type") == "paragraph")
        assert len(headings) == expected_h, f"Expected {expected_h} headings, got {len(headings)}"
        assert len(paras) == expected_p, f"Expected {expected_p} paragraphs, got {len(paras)}"


# ---------------------------------------------------------------------------
# MT5 FODT Python POC: edit/save/reload/verify
# ---------------------------------------------------------------------------

class TestFodtPythonObjectModelPOC:
    """FODT_PYTHON_OBJECT_MODEL_EDIT_SAVE_RELOAD tests."""

    def test_load_parse_produces_block_structure(self):
        """Parser output has blocks structure for object-model POC."""
        doc = _make_sample_document()
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc, tmp)
            result = parse_fodt(tmp)
            assert "blocks" in result
            assert len(result["blocks"]) == 5
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_paragraph_text_save_reload_verify(self):
        """Edit a paragraph's text, save FODT, reload, verify the edit is present."""
        doc = _make_sample_document()
        doc_edited = _edit_block_text(doc, block_idx=1, new_text="EDITED paragraph text.")
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc_edited, tmp)
            reloaded = parse_fodt(tmp)
            blocks = reloaded["blocks"]
            assert blocks[1]["text"] == "EDITED paragraph text.", (
                f"Expected edited text, got {blocks[1]['text']!r}"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_heading_text_save_reload_verify(self):
        """Edit a heading's text, save FODT, reload, verify the edit."""
        doc = _make_sample_document()
        doc_edited = _edit_block_text(doc, block_idx=0, new_text="EDITED Introduction")
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc_edited, tmp)
            reloaded = parse_fodt(tmp)
            blocks = reloaded["blocks"]
            assert blocks[0]["text"] == "EDITED Introduction", (
                f"Expected edited heading, got {blocks[0]['text']!r}"
            )
            assert blocks[0]["type"] == "heading", "Block type must remain 'heading'"
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_one_block_preserves_other_blocks(self):
        """Editing block 1 leaves all other blocks unchanged."""
        doc = _make_sample_document()
        doc_edited = _edit_block_text(doc, block_idx=1, new_text="Only this changed.")
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc_edited, tmp)
            reloaded = parse_fodt(tmp)
            blocks = reloaded["blocks"]
            assert blocks[0]["text"] == "Introduction", f"Block 0 unchanged: {blocks[0]}"
            assert blocks[2]["text"] == "Section Two", f"Block 2 unchanged: {blocks[2]}"
            assert blocks[3]["text"] == "Second paragraph content.", f"Block 3: {blocks[3]}"
            assert blocks[4]["text"] == "Third paragraph.", f"Block 4: {blocks[4]}"
        finally:
            tmp.unlink(missing_ok=True)

    def test_block_count_preserved_after_edit(self):
        """Block count remains the same after edit/save/reload."""
        doc = _make_sample_document()
        doc_edited = _edit_block_text(doc, block_idx=0, new_text="New heading")
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc_edited, tmp)
            reloaded = parse_fodt(tmp)
            assert len(reloaded["blocks"]) == len(doc["blocks"]), "Block count must be preserved"
        finally:
            tmp.unlink(missing_ok=True)

    def test_heading_type_preserved_after_edit(self):
        """Heading type preserved after editing heading text."""
        doc = _make_sample_document()
        doc_edited = _edit_block_text(doc, block_idx=2, new_text="New Section Two")
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc_edited, tmp)
            reloaded = parse_fodt(tmp)
            assert reloaded["blocks"][2]["type"] == "heading", (
                "Heading block type must survive edit/save/reload"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_parser_output_roundtrip_without_edit(self):
        """Parser output can be written back without changes and reloaded correctly."""
        samples = list(Path("samples/by-format/fodt").glob("*.fodt"))
        src = next((s for s in samples if "heading" in s.name), None)
        if src is None:
            pytest.skip("No heading sample found")
        doc = parse_fodt(src)
        orig_blocks = doc.get("blocks", [])
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc, tmp)
            reloaded = parse_fodt(tmp)
            reload_blocks = reloaded.get("blocks", [])
            assert len(reload_blocks) == len(orig_blocks), (
                f"Block count must survive round-trip: {len(orig_blocks)} → {len(reload_blocks)}"
            )
            for i, (ob, rb) in enumerate(zip(orig_blocks, reload_blocks)):
                assert ob["type"] == rb["type"], f"Block {i} type mismatch"
                assert ob["text"] == rb["text"], f"Block {i} text mismatch"
        finally:
            tmp.unlink(missing_ok=True)


class TestFodtPreservationProof:
    """Preservation matrix: verify unedited blocks survive edit/save/reload."""

    def test_heading_level_preserved(self):
        """Heading level (h1 vs h2) is preserved in round-trip."""
        doc = {
            "blocks": [
                {"type": "heading", "text": "H1", "heading_level": 1},
                {"type": "heading", "text": "H2", "heading_level": 2},
            ]
        }
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc, tmp)
            r = parse_fodt(tmp)
            assert r["blocks"][0]["heading_level"] == 1
            assert r["blocks"][1]["heading_level"] == 2
        finally:
            tmp.unlink(missing_ok=True)

    def test_mixed_block_types_preserved(self):
        """Mixed heading+paragraph sequence preserves block types."""
        doc = {
            "blocks": [
                {"type": "heading", "text": "H"},
                {"type": "paragraph", "text": "P1"},
                {"type": "paragraph", "text": "P2"},
            ]
        }
        with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fodt(doc, tmp)
            r = parse_fodt(tmp)
            types = [b["type"] for b in r["blocks"]]
            assert types == ["heading", "paragraph", "paragraph"]
        finally:
            tmp.unlink(missing_ok=True)
