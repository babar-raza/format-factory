"""Semantic mutation roundtrip test for NRRD: raw -> gzip encoding change.

Generated via the /add-roundtrip-test governed skill
(edit_operation: ChangeEncodingRawToGzip, taskcard TC-PROLIB-NRRD-001,
transcript: reports/skills-r1/skill-transcripts/add-roundtrip-test-nrrd.json).

This is distinct from the existing *identity* roundtrip test in
tests/python/nrrd/test_nrrd_codec.py::TestRoundtrip (load -> write -> load,
value unchanged). Here a genuine edit (header encoding raw -> gzip, with the
data payload re-encoded to match) is applied *before* save, and the
assertions target the reloaded value — proving the edit survives a
save/reload cycle, not merely that identity is preserved.

Tier: L2 (behavior — writer roundtrip with a real mutation).
"""
from __future__ import annotations

import gzip
import tempfile
from pathlib import Path

from nrrd.nrrd_analytics import nrrd_element_count, nrrd_is_compressed
from nrrd.nrrd_codec import load_nrrd, write_nrrd

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd"
VALID_DIR = SAMPLES / "valid"
SOURCE_FILE = VALID_DIR / "1d-int8.nrrd"


def _raw_payload() -> bytes:
    """Extract the raw (uncompressed) data payload bytes from the fixture."""
    raw_bytes = SOURCE_FILE.read_bytes()
    return raw_bytes[raw_bytes.index(b"\n\n") + 2:]


class TestMutationRoundtripEncodingChange:
    """load -> mutate encoding raw->gzip -> save -> reload -> assert mutation present."""

    def test_source_fixture_starts_as_raw(self):
        model = load_nrrd(SOURCE_FILE)
        assert model["header"]["encoding"] == "raw"

    def test_encoding_survives_reload(self):
        model = load_nrrd(SOURCE_FILE)
        payload = _raw_payload()

        model["header"]["encoding"] = "gzip"  # the mutation

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated-encoding.nrrd"
            write_nrrd(model, dest, data=payload)
            reloaded = load_nrrd(dest)
            assert reloaded["header"]["encoding"] == "gzip"

    def test_element_count_preserved_after_encoding_change(self):
        model = load_nrrd(SOURCE_FILE)
        original_element_count = model["element_count"]
        payload = _raw_payload()

        model["header"]["encoding"] = "gzip"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated-count.nrrd"
            write_nrrd(model, dest, data=payload)
            reloaded = load_nrrd(dest)
            assert reloaded["element_count"] == original_element_count

    def test_data_bytes_preserved_after_encoding_change(self):
        payload = _raw_payload()
        model = load_nrrd(SOURCE_FILE)
        model["header"]["encoding"] = "gzip"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated-data.nrrd"
            write_nrrd(model, dest, data=payload)

            written_bytes = dest.read_bytes()
            header_end = written_bytes.index(b"\n\n") + 2
            compressed_payload = written_bytes[header_end:]
            decompressed = gzip.decompress(compressed_payload)
            assert decompressed == payload

    def test_analytics_functions_reflect_mutation(self):
        payload = _raw_payload()
        model = load_nrrd(SOURCE_FILE)

        assert nrrd_is_compressed(SOURCE_FILE) is False

        model["header"]["encoding"] = "gzip"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated-analytics.nrrd"
            write_nrrd(model, dest, data=payload)
            assert nrrd_is_compressed(dest) is True
            assert nrrd_element_count(dest) == 4

    def test_original_fixture_file_untouched(self):
        # Sanity: applying and saving the mutation must never affect the
        # source fixture file on disk.
        original_bytes_before = SOURCE_FILE.read_bytes()
        model = load_nrrd(SOURCE_FILE)
        payload = _raw_payload()
        model["header"]["encoding"] = "gzip"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated-untouched.nrrd"
            write_nrrd(model, dest, data=payload)

        original_bytes_after = SOURCE_FILE.read_bytes()
        assert original_bytes_before == original_bytes_after
