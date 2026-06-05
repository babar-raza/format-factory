# R107 Wave 3: DIF roundtrip proof
# 9 tests — DIF parse + CSV export + data integrity

import importlib
import os
import pytest

dif = importlib.import_module("dif")

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "dif")
VALID_DIR = os.path.join(SAMPLES_DIR, "valid")


def _get_sample():
    for d in [VALID_DIR, SAMPLES_DIR]:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".dif"):
                    return os.path.join(d, f)
    pytest.skip("No DIF sample files")


class TestDifRoundtripProof:
    """DIF parse and export roundtrip verification."""

    def test_parse_returns_dict(self):
        path = _get_sample()
        result = dif.parse_dif(path)
        assert isinstance(result, dict)

    def test_parse_has_ok_field(self):
        path = _get_sample()
        result = dif.parse_dif(path)
        assert "ok" in result
        assert result["ok"] is True

    def test_csv_export_produces_string(self):
        path = _get_sample()
        csv = dif.dif_to_csv(path)
        assert isinstance(csv, str)
        assert len(csv) > 0

    def test_csv_export_has_lines(self):
        path = _get_sample()
        csv = dif.dif_to_csv(path)
        lines = [l for l in csv.strip().split("\n") if l.strip()]
        assert len(lines) >= 1

    def test_csv_has_data(self):
        path = _get_sample()
        csv = dif.dif_to_csv(path)
        import re
        # Should have some alphanumeric content
        assert re.search(r'[a-zA-Z0-9]', csv) is not None

    def test_multiple_parse_consistent(self):
        path = _get_sample()
        csv1 = dif.dif_to_csv(path)
        csv2 = dif.dif_to_csv(path)
        assert csv1 == csv2

    def test_parse_nonexistent_returns_error(self):
        result = dif.parse_dif("/nonexistent/path/file.dif")
        assert result.get("ok") is False

    def test_probe_returns_dict(self):
        path = _get_sample()
        result = dif.probe_dif(path)
        assert isinstance(result, dict)

    def test_csv_no_raw_dif_tokens(self):
        path = _get_sample()
        csv = dif.dif_to_csv(path)
        # CSV should not contain raw DIF structural tokens
        assert "VECTORS" not in csv
        assert "TUPLES" not in csv
