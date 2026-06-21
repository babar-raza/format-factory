"""Sprint R443 — NDJSON/PBM/PGM/PPM/QOI deepening round 7 (composite analytics)."""
import sys, pathlib, json

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

# ── NDJSON ────────────────────────────────────────────────────────────
from src.python.ndjson.ndjson_codec import (
    ndjson_record_count_times_two,
    ndjson_numeric_field_count_times_two,
    ndjson_record_count,
    ndjson_numeric_field_count,
)

class TestNdjsonRecordCountTimesTwo:
    def test_type(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert isinstance(ndjson_record_count_times_two(str(p)), int)
    def test_value(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert ndjson_record_count_times_two(str(p)) == ndjson_record_count(str(p)) * 2
    def test_nonneg(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_record_count_times_two(str(p)) >= 0

class TestNdjsonNumericFieldCountTimesTwo:
    def test_type(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert isinstance(ndjson_numeric_field_count_times_two(str(p)), int)
    def test_value(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": 1, "b": "x"}) + "\n")
        assert ndjson_numeric_field_count_times_two(str(p)) == ndjson_numeric_field_count(str(p)) * 2
    def test_nonneg(self, tmp_path):
        p = tmp_path / "t.ndjson"
        p.write_text(json.dumps({"a": "x"}) + "\n")
        assert ndjson_numeric_field_count_times_two(str(p)) >= 0

# ── PBM ───────────────────────────────────────────────────────────────
from src.python.pbm.pbm_parser import (
    pbm_width_squared,
    pbm_height_squared,
    pbm_width,
    pbm_height,
)

_pbm_path = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")

class TestPbmWidthSquared:
    def test_type(self):
        assert isinstance(pbm_width_squared(_pbm_path), int)
    def test_value(self):
        w = pbm_width(_pbm_path)
        assert pbm_width_squared(_pbm_path) == w * w
    def test_nonneg(self):
        assert pbm_width_squared(_pbm_path) >= 0

class TestPbmHeightSquared:
    def test_type(self):
        assert isinstance(pbm_height_squared(_pbm_path), int)
    def test_value(self):
        h = pbm_height(_pbm_path)
        assert pbm_height_squared(_pbm_path) == h * h
    def test_nonneg(self):
        assert pbm_height_squared(_pbm_path) >= 0

# ── PGM ───────────────────────────────────────────────────────────────
from src.python.pgm.pgm_parser import (
    pgm_width_squared,
    pgm_height_squared,
    pgm_width,
    pgm_height,
)

_pgm_path = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")

class TestPgmWidthSquared:
    def test_type(self):
        assert isinstance(pgm_width_squared(_pgm_path), int)
    def test_value(self):
        w = pgm_width(_pgm_path)
        assert pgm_width_squared(_pgm_path) == w * w
    def test_nonneg(self):
        assert pgm_width_squared(_pgm_path) >= 0

class TestPgmHeightSquared:
    def test_type(self):
        assert isinstance(pgm_height_squared(_pgm_path), int)
    def test_value(self):
        h = pgm_height(_pgm_path)
        assert pgm_height_squared(_pgm_path) == h * h
    def test_nonneg(self):
        assert pgm_height_squared(_pgm_path) >= 0

# ── PPM ───────────────────────────────────────────────────────────────
from src.python.ppm.ppm_parser import (
    ppm_width_squared,
    ppm_height_squared,
    ppm_width,
    ppm_height,
)

_ppm_path = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")

class TestPpmWidthSquared:
    def test_type(self):
        assert isinstance(ppm_width_squared(_ppm_path), int)
    def test_value(self):
        w = ppm_width(_ppm_path)
        assert ppm_width_squared(_ppm_path) == w * w
    def test_nonneg(self):
        assert ppm_width_squared(_ppm_path) >= 0

class TestPpmHeightSquared:
    def test_type(self):
        assert isinstance(ppm_height_squared(_ppm_path), int)
    def test_value(self):
        h = ppm_height(_ppm_path)
        assert ppm_height_squared(_ppm_path) == h * h
    def test_nonneg(self):
        assert ppm_height_squared(_ppm_path) >= 0

# ── QOI ───────────────────────────────────────────────────────────────
from src.python.qoi.qoi_parser import (
    qoi_width_squared,
    qoi_file_size_squared,
    qoi_width,
    qoi_file_size_bytes,
)

_qoi_path = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")

class TestQoiWidthSquared:
    def test_type(self):
        assert isinstance(qoi_width_squared(_qoi_path), int)
    def test_value(self):
        w = qoi_width(_qoi_path)
        assert qoi_width_squared(_qoi_path) == w * w
    def test_nonneg(self):
        assert qoi_width_squared(_qoi_path) >= 0

class TestQoiFileSizeSquared:
    def test_type(self):
        assert isinstance(qoi_file_size_squared(_qoi_path), int)
    def test_value(self):
        fs = qoi_file_size_bytes(_qoi_path)
        assert qoi_file_size_squared(_qoi_path) == fs * fs
    def test_positive(self):
        assert qoi_file_size_squared(_qoi_path) > 0
