"""L1 unit tests — additional probe/load correctness coverage beyond Phase 1.

Exercises the existing codec (probe_xliff / load_xliff / get_unit_count /
get_file_count) against the real sample corpus more deeply than the Phase 1
test suite, without touching any malformed/exception paths (those live in
the L3 sections of the analytics/compat/mutation test files).
"""

from __future__ import annotations

from pathlib import Path

from xliff.xliff_codec import get_file_count, get_unit_count, load_xliff, probe_xliff

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"


class TestProbeLoadExtra:
    def test_probe_valid_minimal_via_bytes(self):
        data = (VALID_DIR / "minimal.xliff").read_bytes()
        assert probe_xliff(data) is True

    def test_probe_returns_bool_type(self):
        assert isinstance(probe_xliff(VALID_DIR / "minimal.xliff"), bool)

    def test_load_with_inline_codes_structure(self):
        model = load_xliff(VALID_DIR / "with-inline-codes.xliff")
        seg = model["files"][0]["units"][0]["segments"][0]
        assert "here" in seg["source"]

    def test_load_source_language_field(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert model["source_language"] == "en"

    def test_load_target_language_field(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert model["target_language"] == "fr"

    def test_load_version_field(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        assert model["version"] == "2.0"

    def test_load_file_id_field(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert model["files"][0]["id"] == "f1"

    def test_load_unit_id_field(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        ids = [u["id"] for u in model["files"][0]["units"]]
        assert ids == ["u1", "u2", "u3"]

    def test_get_unit_count_matches_loaded_model(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        assert get_unit_count(model) == 3

    def test_get_file_count_matches_loaded_model(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert get_file_count(model) == 1
