"""TC-FL-009: PBM consumer roundtrip proof tests.

Verifies that PBM read + write + re-read roundtrip works correctly
using the write_pbm function and parse_pbm_strict parser.
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

import pytest


@pytest.fixture
def sample_pbm():
    return _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


class TestPbmConsumerRoundtrip:
    def test_read_produces_pbm_image(self, sample_pbm):
        from src.python.pbm.pbm_parser import parse_pbm_strict
        img = parse_pbm_strict(sample_pbm)
        assert img.width > 0
        assert img.height > 0
        assert len(img.pixels) == img.width * img.height

    def test_domain_model_spec_qname(self, sample_pbm):
        from src.python.pbm.models import PbmDocument
        doc = PbmDocument.from_file(sample_pbm)
        assert doc.spec_qname == "pbm:image"

    def test_write_produces_file(self, sample_pbm, tmp_path):
        from src.python.pbm.pbm_parser import parse_pbm_strict, write_pbm
        img = parse_pbm_strict(sample_pbm)
        dest = tmp_path / "out.pbm"
        write_pbm(img.pixels, img.width, img.height, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_roundtrip_preserves_pixels(self, sample_pbm, tmp_path):
        from src.python.pbm.pbm_parser import parse_pbm_strict, write_pbm
        img = parse_pbm_strict(sample_pbm)
        dest = tmp_path / "roundtrip.pbm"
        write_pbm(img.pixels, img.width, img.height, dest)
        img2 = parse_pbm_strict(dest)
        assert img2.width == img.width
        assert img2.height == img.height
        assert img2.pixels == img.pixels

    def test_roundtrip_preserves_dimensions(self, sample_pbm, tmp_path):
        from src.python.pbm.pbm_parser import parse_pbm_strict, write_pbm, get_dimensions
        img = parse_pbm_strict(sample_pbm)
        dest = tmp_path / "dims.pbm"
        write_pbm(img.pixels, img.width, img.height, dest)
        w, h = get_dimensions(dest)
        assert w == img.width
        assert h == img.height

    def test_all_sample_files_parse(self):
        from src.python.pbm.pbm_parser import parse_pbm_strict
        samples_dir = _REPO / "samples" / "by-format" / "pbm" / "valid"
        files = list(samples_dir.glob("*.pbm"))
        assert len(files) >= 1
        for f in files:
            img = parse_pbm_strict(f)
            assert img.width > 0 and img.height > 0


class TestQoiConsumerProof:
    def test_domain_model_spec_qname(self):
        from src.python.qoi.models import QoiDocument
        sample = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"
        doc = QoiDocument.from_file(sample)
        assert doc.spec_qname == "qoi:image"

    def test_domain_model_dimensions(self):
        from src.python.qoi.models import QoiDocument
        sample = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"
        doc = QoiDocument.from_file(sample)
        assert doc.width > 0
        assert doc.height > 0

    def test_to_dict_has_required_fields(self):
        from src.python.qoi.models import QoiDocument
        sample = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"
        doc = QoiDocument.from_file(sample)
        d = doc.to_dict()
        assert "width" in d
        assert "height" in d

    def test_analytics_pixel_count(self):
        from src.python.qoi.image_document import qoi_pixel_count, qoi_dimensions
        sample = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"
        dims = qoi_dimensions(str(sample))
        count = qoi_pixel_count(str(sample))
        assert count == dims["width"] * dims["height"]

    def test_analytics_average_brightness(self):
        from src.python.qoi.image_document import qoi_average_brightness
        sample = _REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi"
        brightness = qoi_average_brightness(str(sample))
        assert 0.0 <= brightness <= 255.0

    def test_all_samples_parse(self):
        from src.python.qoi.models import QoiDocument
        samples_dir = _REPO / "samples" / "by-format" / "qoi" / "valid"
        files = list(samples_dir.glob("*.qoi"))
        assert len(files) >= 1
        for f in files:
            doc = QoiDocument.from_file(f)
            assert doc.spec_qname == "qoi:image"
