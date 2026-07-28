"""Roundtrip test for ODT: load sample, edit paragraph text, save, reload, verify.

edit_operation: ReplaceText
Proves: parse/load, domain model, same-format save, reload verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.models import OdtModelDocument
from odt.odt_writer import write_odt
from odt.odt_parser import parse_odt_strict

_SAMPLE = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"


class TestOdtSampleRoundtrip:
    """Roundtrip: load from sample → verify model → write with new text → reload → verify."""

    @pytest.mark.roundtrip
    def test_from_file_loads_sample(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "office:document"
        assert doc.paragraph_count >= 1

    @pytest.mark.roundtrip
    def test_spec_qname_matches_registry(self):
        assert OdtModelDocument.spec_qname == "office:document"
        assert OdtModelDocument.spec_fact_ref == "SAL-ODT-01067"

    @pytest.mark.roundtrip
    def test_sample_model_typed_properties(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert isinstance(doc.paragraph_count, int)
        assert isinstance(doc.heading_count, int)
        d = doc.to_dict()
        assert "paragraph_count" in d
        assert "heading_count" in d

    @pytest.mark.roundtrip
    def test_write_reload_preserves_text(self, tmp_path):
        """Full roundtrip: write new text → reload → verify paragraph present."""
        dest = tmp_path / "roundtrip.odt"
        expected_text = "Roundtrip verification paragraph"
        write_odt([expected_text, "Second paragraph"], dest)

        reloaded = parse_odt_strict(str(dest))
        texts = [p.text for p in reloaded.paragraphs]
        assert expected_text in texts

    @pytest.mark.roundtrip
    def test_write_reload_via_domain_model(self, tmp_path):
        """Roundtrip through OdtModelDocument: write → reload via from_file → check count."""
        dest = tmp_path / "model_roundtrip.odt"
        write_odt(["Alpha", "Beta", "Gamma"], dest)

        reloaded_doc = OdtModelDocument.from_file(dest)
        assert reloaded_doc.spec_qname == "office:document"
        assert reloaded_doc.paragraph_count == 3

    @pytest.mark.roundtrip
    def test_edit_operation_replace_text(self, tmp_path):
        """Edit operation: load sample paragraphs, replace first, save, reload."""
        # Load original
        original = OdtModelDocument.from_file(_SAMPLE)
        original_count = original.paragraph_count

        # Write with replaced first paragraph
        new_texts = ["REPLACED_PARA"] + [
            p.text for p in original.paragraphs[1:]
        ]
        dest = tmp_path / "replaced.odt"
        write_odt(new_texts, dest)

        # Reload and verify
        reloaded = parse_odt_strict(str(dest))
        texts = [p.text for p in reloaded.paragraphs]
        assert "REPLACED_PARA" in texts
        assert len(reloaded.paragraphs) == len(new_texts)
