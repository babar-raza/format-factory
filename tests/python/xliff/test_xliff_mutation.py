"""Semantic round-trip (mutation) tests for XLIFF: load -> edit -> save ->
reload -> assert the edit is present. Distinct from the Phase 1 identity
round-trip test (TestRoundtrip.test_roundtrip_minimal), which only asserts
structural shape is unchanged.

L2 class: TestSemanticRoundtrip.
L3 (edge/boundary) class: TestMutationEdgeCases.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from xliff.models import XliffDocument
from xliff.xliff_analytics import (
    xliff_translated_segment_count,
    xliff_untranslated_segment_count,
)
from xliff.xliff_codec import load_xliff, write_xliff

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"


class TestSemanticRoundtrip:
    def test_set_target_text_survives_roundtrip(self):
        """load -> mutate target -> save -> reload: new target text is present."""
        model = load_xliff(VALID_DIR / "minimal.xliff")
        model["files"][0]["units"][0]["segments"][0]["target"] = "New translation"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["target"] == "New translation"

    def test_set_target_preserves_source_text(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        original_source = model["files"][0]["units"][0]["segments"][0]["source"]
        model["files"][0]["units"][0]["segments"][0]["target"] = "New translation"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated2.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["source"] == original_source

    def test_untranslated_becomes_translated_after_edit_and_reload(self):
        xml = (
            b'<?xml version="1.0"?>'
            b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">'
            b'<file id="f1"><unit id="u1"><segment><source>Hi</source></segment></unit>'
            b"</file></xliff>"
        )
        model = load_xliff(xml)
        assert xliff_untranslated_segment_count(xml) == 1
        model["files"][0]["units"][0]["segments"][0]["target"] = "Translated now"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated3.xliff"
            write_xliff(model, dest)
            assert xliff_translated_segment_count(dest) == 1
            assert xliff_untranslated_segment_count(dest) == 0

    def test_edit_reflected_via_domain_model_after_reload(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        model["files"][0]["units"][1]["segments"][0]["target"] = "Monde nouveau"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated4.xliff"
            write_xliff(model, dest)
            doc = XliffDocument.from_file(str(dest))
            assert doc.units[1]["segments"][0]["target"] == "Monde nouveau"


class TestMutationEdgeCases:
    def test_clearing_target_reverts_to_untranslated_after_roundtrip(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        model["files"][0]["units"][0]["segments"][0]["target"] = ""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "cleared.xliff"
            write_xliff(model, dest)
            assert xliff_untranslated_segment_count(dest) == 1
            assert xliff_translated_segment_count(dest) == 0

    def test_mutation_on_multi_unit_only_affects_targeted_segment(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        model["files"][0]["units"][0]["segments"][0]["target"] = "Changed"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "partial.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["target"] == "Changed"
            assert reloaded["files"][0]["units"][1]["segments"][0]["target"] == "Monde"
            assert reloaded["files"][0]["units"][2]["segments"][0]["target"] == "Au revoir"

    def test_mutation_with_unicode_text_survives_roundtrip(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        model["files"][0]["units"][0]["segments"][0]["target"] = "éèê 日本語"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "unicode.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["target"] == "éèê 日本語"
