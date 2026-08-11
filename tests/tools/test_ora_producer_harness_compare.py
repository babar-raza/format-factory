"""Contract tests for tools/ora/producer_harness/compare.py, using MOCKED
producer output -- synthetic PNG bytes built directly by this test file,
clearly standing in for a real GIMP export, never presented as one.

This is the harness logic this repository CAN fully build and verify
without any producer application installed (no GIMP, no display server --
see tools/ora/producer_harness/README.md for why, and for the exact
external command a capable environment runs to supply the real thing these
mocks stand in for). These tests prove compare.py's own comparison math,
error handling, and manifest generation are correct; they do NOT, and
cannot, prove anything about real independent-producer agreement -- that
remains EXTERNAL_EXECUTION_READY, not implemented, per this session's own
state-machine discipline.
"""

from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path

import pytest

_ORA_SRC = Path(__file__).resolve().parents[2] / "src" / "python" / "ora" / "src"
sys.path.insert(0, str(_ORA_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ora.producer_harness.compare import (  # noqa: E402
    SceneComparisonResult,
    compare_rasters,
    compare_scene,
    write_manifest,
)
from tools.ora.producer_harness.format_factory_side import render_scene  # noqa: E402
from tools.ora.producer_harness.scene_matrix import SCENES, scene_by_id  # noqa: E402

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(
        ">I", zlib.crc32(kind + data) & 0xFFFFFFFF
    )


def _mock_producer_png(width: int, height: int, pixels: bytes) -> bytes:
    """A synthetic PNG built directly (not through format_factory.ora's own
    encoder), standing in for what a real producer application would have
    exported. `pixels` must already be width*height*4 RGBA bytes."""
    assert len(pixels) == width * height * 4
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    rows = b"".join(bytes([0]) + pixels[y * width * 4 : (y + 1) * width * 4] for y in range(height))
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(rows)) + _chunk(b"IEND", b"")


def _mock_matching_producer_png(scene_id: str) -> bytes:
    """A mock 'producer' PNG that is DELIBERATELY IDENTICAL to
    format-factory's own render -- for testing the "producers agree" path
    without needing a real second implementation to agree with."""
    raster = render_scene(scene_by_id(scene_id))
    return _mock_producer_png(raster.width, raster.height, raster.pixels)


# ── compare_rasters: pure comparison math ───────────────────────────────


def test_compare_rasters_reports_exact_match() -> None:
    scene = scene_by_id("single-opaque-layer")
    raster = render_scene(scene)

    exact, diff_fraction, max_delta = compare_rasters(raster, raster)

    assert exact is True
    assert diff_fraction == 0.0
    assert max_delta == 0


def test_compare_rasters_reports_dimension_mismatch_as_no_comparison() -> None:
    from format_factory.ora.render import DecodedRaster

    a = DecodedRaster(width=4, height=4, pixels=bytes(4 * 4 * 4))
    b = DecodedRaster(width=8, height=8, pixels=bytes(8 * 8 * 4))

    exact, diff_fraction, max_delta = compare_rasters(a, b)

    assert exact is False
    assert diff_fraction is None
    assert max_delta is None


def test_compare_rasters_reports_the_exact_diff_fraction_and_max_delta() -> None:
    from format_factory.ora.render import DecodedRaster

    a = DecodedRaster(width=2, height=1, pixels=bytes((10, 10, 10, 255, 0, 0, 0, 0)))
    b = DecodedRaster(width=2, height=1, pixels=bytes((10, 10, 10, 255, 5, 5, 5, 5)))

    exact, diff_fraction, max_delta = compare_rasters(a, b)

    assert exact is False
    assert diff_fraction == pytest.approx(4 / 8)
    assert max_delta == 5


# ── compare_scene: end-to-end against mocked producer PNGs ─────────────


@pytest.mark.parametrize("scene", SCENES, ids=lambda s: s.scene_id)
def test_compare_scene_against_a_mock_that_deliberately_agrees(scene) -> None:
    """A mock producer whose output is deliberately identical to
    format-factory's own render must be reported as an exact, in-tolerance
    match -- proves the "agreement" path fires correctly for every real
    scene in the matrix, not just one hand-picked example."""
    mock_png = _mock_matching_producer_png(scene.scene_id)

    result = compare_scene(
        scene.scene_id, mock_png, producer_name="mock-agreeing-producer", producer_version="0.0.0-mock"
    )

    assert result.dimensions_match is True
    assert result.pixel_exact_match is True
    assert result.within_tolerance is True
    assert result.error is None


def test_compare_scene_detects_a_genuine_disagreement() -> None:
    """A mock producer whose output deliberately DIFFERS must be reported
    as not matching -- proves the harness would actually catch a real
    disagreement, not just rubber-stamp everything."""
    scene = scene_by_id("single-opaque-layer")
    wrong_pixels = bytes((0, 0, 0, 255)) * (scene.canvas_width * scene.canvas_height)
    mock_png = _mock_producer_png(scene.canvas_width, scene.canvas_height, wrong_pixels)

    result = compare_scene(
        scene.scene_id, mock_png, producer_name="mock-disagreeing-producer", producer_version="0.0.0-mock"
    )

    assert result.pixel_exact_match is False
    assert result.within_tolerance is False
    assert result.byte_diff_fraction is not None and result.byte_diff_fraction > 0


def test_compare_scene_within_tolerance_but_not_pixel_exact() -> None:
    """A near-match within a declared tolerance is reported as passing
    (within_tolerance) while still honestly disclosing it was not byte
    -exact -- the two flags are independently meaningful, not conflated."""
    scene = scene_by_id("single-opaque-layer")
    raster = render_scene(scene)
    nudged = bytes(min(255, b + 1) if i % 4 != 3 else b for i, b in enumerate(raster.pixels))
    mock_png = _mock_producer_png(scene.canvas_width, scene.canvas_height, nudged)

    result = compare_scene(
        scene.scene_id, mock_png, producer_name="mock-near-producer", producer_version="0.0.0-mock",
        tolerance=2,
    )

    assert result.pixel_exact_match is False
    assert result.within_tolerance is True
    assert result.max_channel_delta is not None and result.max_channel_delta <= 2


def test_compare_scene_reports_a_malformed_producer_png_as_an_error_not_a_crash() -> None:
    result = compare_scene(
        "single-opaque-layer", b"not a real png", producer_name="broken-producer", producer_version="0.0.0"
    )

    assert result.error is not None
    assert result.within_tolerance is False


def test_compare_scene_rejects_an_unknown_scene_id() -> None:
    with pytest.raises(KeyError):
        compare_scene("no-such-scene", b"", producer_name="x", producer_version="0")


# ── write_manifest: machine-readable output the reconciler could consume ──


def test_write_manifest_reports_pass_only_when_every_scene_is_within_tolerance(tmp_path: Path) -> None:
    passing = SceneComparisonResult(
        scene_id="a", producer_name="mock", producer_version="0", dimensions_match=True,
        pixel_exact_match=True, byte_diff_fraction=0.0, max_channel_delta=0,
        within_tolerance=True, tolerance=0,
    )
    failing = SceneComparisonResult(
        scene_id="b", producer_name="mock", producer_version="0", dimensions_match=True,
        pixel_exact_match=False, byte_diff_fraction=0.5, max_channel_delta=200,
        within_tolerance=False, tolerance=0,
    )
    out = tmp_path / "manifest.json"

    write_manifest([passing], out)
    assert json.loads(out.read_text())["result"] == "PASS"

    write_manifest([passing, failing], out)
    payload = json.loads(out.read_text())
    assert payload["result"] == "FAIL"
    assert payload["schema"] == "ora-producer-harness/comparison-manifest@1"
    assert len(payload["scenes"]) == 2


# ── Scene-matrix drift guard (GIMP-side vs. Python-side) ────────────────


def test_gimp_script_scene_ids_are_a_subset_of_the_canonical_matrix() -> None:
    """generate_scene.py deliberately duplicates scene data (GIMP's own
    Python-Fu interpreter cannot import this repo's packages) rather than
    importing scene_matrix.py. This test is the drift guard: every scene_id
    the GIMP script claims to support must exist in the canonical matrix,
    so a rename here is caught by this repo's own CI without needing GIMP
    installed to notice the mismatch."""
    script_path = Path(__file__).resolve().parents[2] / "tools" / "ora" / "producer_harness" / "gimp_scripts" / "generate_scene.py"
    script_text = script_path.read_text(encoding="utf-8")
    canonical_ids = {scene.scene_id for scene in SCENES}

    scripted_ids = {
        line.split('"')[1]
        for line in script_text.splitlines()
        if line.strip().startswith('"') and line.count('"') >= 2 and ": {" in line
    }

    assert scripted_ids, "expected at least one scripted scene_id in generate_scene.py"
    assert scripted_ids <= canonical_ids, scripted_ids - canonical_ids
