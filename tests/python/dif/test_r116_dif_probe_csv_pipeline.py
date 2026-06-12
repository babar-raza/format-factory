"""R116 DIF: probe_dif + dif_to_csv pipeline deepening.

Tests probe_dif metadata inspection, dif_to_csv workflow,
parse_dif_strict cell types, and full dogfood pipeline.
"""
from pathlib import Path

import pytest

from src.python.dif.dif_parser import (
    parse_dif,
    parse_dif_strict,
    probe_dif,
    dif_to_csv,
    DifDocument,
    DifError,
)

# Minimal valid DIF fixture (TABLE/VECTORS/TUPLES/DATA sections)
_MINIMAL_DIF = """\
TABLE
0,1
"Minimal"
VECTORS
0,2
""
TUPLES
0,3
""
DATA
0,0
""
1,1
""
-1,0
"EOD"
"""

_GRID_DIF = """\
TABLE
0,1
"Sheet1"
VECTORS
0,2
""
TUPLES
0,3
""
DATA
0,0
""
1,10
""
0,1
"Name"
1,20
""
0,1
"Score"
-1,0
""
1,10
""
0,1
"Alice"
1,20
""
1,95
""
-1,0
""
-1,0
"EOD"
"""


def _write_dif(tmp_path: Path, content: str, name: str = "test.dif") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="ascii")
    return p


class TestProbeDif:
    def test_probe_returns_dict(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = probe_dif(p)
        assert isinstance(result, dict)

    def test_probe_valid_header_flag(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = probe_dif(p)
        assert result.get("valid_header") is True

    def test_probe_exists_flag(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = probe_dif(p)
        assert result.get("exists") is True

    def test_probe_missing_file_exists_false(self, tmp_path):
        result = probe_dif(tmp_path / "nonexistent.dif")
        assert result.get("exists") is False

    def test_probe_has_title(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = probe_dif(p)
        assert "title" in result


class TestDifToCsv:
    def test_dif_to_csv_returns_string(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = dif_to_csv(p)
        assert isinstance(result, str)

    def test_dif_to_csv_missing_file_raises(self, tmp_path):
        with pytest.raises((DifError, FileNotFoundError, OSError)):
            dif_to_csv(tmp_path / "nosuchfile.dif")

    def test_dif_to_csv_nonexistent_raises(self, tmp_path):
        with pytest.raises((DifError, FileNotFoundError, OSError)):
            dif_to_csv(tmp_path / "missing.dif")


class TestParseDifStrict:
    def test_parse_dif_strict_returns_document(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        doc = parse_dif_strict(p)
        assert isinstance(doc, DifDocument)

    def test_parse_dif_strict_missing_file_raises(self, tmp_path):
        with pytest.raises(DifError):
            parse_dif_strict(tmp_path / "missing.dif")

    def test_parse_dif_returns_dict_with_ok(self, tmp_path):
        p = _write_dif(tmp_path, _MINIMAL_DIF)
        result = parse_dif(p)
        assert isinstance(result, dict)
        assert "ok" in result


class TestDifDogfoodPipeline:
    def test_dogfood_pipeline(self, tmp_path):
        """Full pipeline: write DIF → probe → parse_strict → dif_to_csv."""
        p = _write_dif(tmp_path, _MINIMAL_DIF, "dogfood.dif")

        # Probe
        probe = probe_dif(p)
        assert probe.get("exists") is True

        # Parse strict
        doc = parse_dif_strict(p)
        assert doc is not None

        # parse_dif (permissive)
        result = parse_dif(p)
        assert result.get("ok") is True

        # CSV export
        csv_text = dif_to_csv(p)
        assert isinstance(csv_text, str)
