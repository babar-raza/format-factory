# R93 Train O: Python Netpbm PPM→PGM installed workflow verification
# Governed skill: /verify-dogfood-path
# Ledger: R93-GOVERNED-PYTHON-NETPBM-PPM-PGM-WORKFLOW-001
# Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001
#
# Verifies the full PPM→PGM dogfood export path works end-to-end
# using only FormatFactory libraries (no external imaging backends).

import inspect
from pathlib import Path


from ppm.ppm_parser import write_ppm
from ppm.ppm_to_pgm import convert_ppm_to_pgm, ppm_pixels_to_pgm_pixels
from pgm.pgm_parser import parse_pgm_strict


def test_import_chain_no_external_backends():
    """All conversion code uses only FF libraries — no PIL, cv2, etc."""
    src = inspect.getsource(convert_ppm_to_pgm)
    for forbidden in ("PIL", "cv2", "imageio", "skimage", "matplotlib", "numpy"):
        assert forbidden not in src, f"External backend found in source: {forbidden}"


def test_convert_end_to_end_roundtrip(tmp_path: Path):
    """Full round-trip: write PPM → convert → load PGM → verify pixels."""
    ppm_path = tmp_path / "input.ppm"
    pgm_path = tmp_path / "output.pgm"

    pixels = [(100, 100, 100), (200, 200, 200), (0, 0, 0), (255, 255, 255)]
    write_ppm(pixels, width=2, height=2, maxval=255, file_path=ppm_path)

    result = convert_ppm_to_pgm(ppm_path, pgm_path)

    assert result["dogfood"] is True
    pgm = parse_pgm_strict(pgm_path)
    assert len(pgm.pixels) == 4
    # Uniform RGB → grayscale = same value (all channels equal)
    assert pgm.pixels[0] == 100
    assert pgm.pixels[1] == 200
    assert pgm.pixels[2] == 0
    assert pgm.pixels[3] == 255


def test_ppm_source_file_preserved(tmp_path: Path):
    """Source PPM file is not deleted or modified by conversion."""
    ppm_path = tmp_path / "source.ppm"
    pgm_path = tmp_path / "dest.pgm"
    write_ppm([(128, 64, 32)], width=1, height=1, maxval=255, file_path=ppm_path)
    size_before = ppm_path.stat().st_size
    convert_ppm_to_pgm(ppm_path, pgm_path)
    assert ppm_path.exists()
    assert ppm_path.stat().st_size == size_before


def test_ff_write_library_declared(tmp_path: Path):
    """Result metadata explicitly names the FF write library used."""
    ppm_path = tmp_path / "src.ppm"
    pgm_path = tmp_path / "dst.pgm"
    write_ppm([(0, 128, 255)], 1, 1, 255, ppm_path)
    result = convert_ppm_to_pgm(ppm_path, pgm_path)
    assert "ff_write_library" in result
    assert "pgm" in result["ff_write_library"]


def test_luminance_weighted_conversion_accuracy():
    """ITU-R BT.601 weighted grayscale is applied (not simple average)."""
    # Pure red: luminance ≈ 0.299 * 255 ≈ 76
    assert ppm_pixels_to_pgm_pixels([(255, 0, 0)]) == [76]
    # Pure green: luminance ≈ 0.587 * 255 ≈ 150
    assert ppm_pixels_to_pgm_pixels([(0, 255, 0)]) == [150]
    # Pure blue: luminance ≈ 0.114 * 255 ≈ 29
    assert ppm_pixels_to_pgm_pixels([(0, 0, 255)]) == [29]


def test_output_pgm_is_valid_netpbm(tmp_path: Path):
    """Converted PGM can be parsed back by the FF PGM parser."""
    ppm_path = tmp_path / "img.ppm"
    pgm_path = tmp_path / "img.pgm"
    write_ppm([(10, 20, 30), (40, 50, 60)], 2, 1, 255, ppm_path)
    convert_ppm_to_pgm(ppm_path, pgm_path)
    pgm = parse_pgm_strict(pgm_path)
    assert pgm.width == 2
    assert pgm.height == 1
    assert pgm.maxval == 255


def test_large_image_roundtrip(tmp_path: Path):
    """Larger 64x64 uniform image converts without error."""
    ppm_path = tmp_path / "large.ppm"
    pgm_path = tmp_path / "large.pgm"
    pixels = [(128, 128, 128)] * (64 * 64)
    write_ppm(pixels, 64, 64, 255, ppm_path)
    result = convert_ppm_to_pgm(ppm_path, pgm_path)
    assert result["dogfood"] is True
    pgm = parse_pgm_strict(pgm_path)
    assert pgm.width == 64
    assert pgm.height == 64
    assert all(p == 128 for p in pgm.pixels)


def test_output_pgm_file_created(tmp_path: Path):
    """After conversion, the output PGM file exists and has nonzero size."""
    ppm_path = tmp_path / "a.ppm"
    pgm_path = tmp_path / "a.pgm"
    write_ppm([(255, 0, 128)], 1, 1, 255, ppm_path)
    convert_ppm_to_pgm(ppm_path, pgm_path)
    assert pgm_path.exists()
    assert pgm_path.stat().st_size > 0
