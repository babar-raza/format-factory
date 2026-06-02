"""R90 governed dogfood export tests for PPM to PGM."""

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from pgm.pgm_parser import parse_pgm_strict
from ppm.ppm_parser import write_ppm
from ppm.ppm_to_pgm import convert_ppm_to_pgm, ppm_pixels_to_pgm_pixels


def test_rgb_to_grayscale_values() -> None:
    assert ppm_pixels_to_pgm_pixels([(0, 0, 0), (255, 255, 255), (255, 0, 0)]) == [
        0,
        255,
        76,
    ]


def test_invalid_maxval_rejected() -> None:
    with pytest.raises(ValueError, match="maxval"):
        ppm_pixels_to_pgm_pixels([(0, 0, 0)], maxval=0)


def test_invalid_channel_rejected() -> None:
    with pytest.raises(ValueError, match="out of range"):
        ppm_pixels_to_pgm_pixels([(256, 0, 0)])


def test_export_uses_ff_writer_and_reloads(tmp_path: Path) -> None:
    source = tmp_path / "source.ppm"
    exported = tmp_path / "exported.pgm"
    write_ppm([(255, 0, 0), (0, 255, 0)], 2, 1, 255, source)

    result = convert_ppm_to_pgm(source, exported)

    assert result["dogfood"] is True
    assert result["ff_write_library"] == "pgm.pgm_parser.write_pgm"
    image = parse_pgm_strict(exported)
    assert image.pixels == [76, 150]


def test_export_source_names_ff_writer_without_external_backend() -> None:
    source = inspect.getsource(convert_ppm_to_pgm)
    assert "write_pgm" in source
    assert "from pgm" in source
    for forbidden in ("PIL", "cv2", "imageio", "skimage", "matplotlib"):
        assert forbidden not in source
