"""Compare a real producer's own exported PNG for a scene against
format-factory's own render of the identical scene, and emit a
machine-readable result the obligation reconciler can consume.

This module's own logic is fully buildable and testable WITHOUT any
producer application installed (see test_compare_contract.py, which drives
it with mocked/synthetic producer PNGs standing in for real GIMP output).
Only `run_producer(...)` -- which actually shells out to a producer binary
-- needs one installed; everything else here is pure comparison math over
already-decoded pixel bytes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

_ORA_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"
if str(_ORA_SRC) not in sys.path:
    sys.path.insert(0, str(_ORA_SRC))

from format_factory.ora.render import DecodedRaster, decode_png  # noqa: E402

from .format_factory_side import render_scene  # noqa: E402
from .scene_matrix import Scene, scene_by_id  # noqa: E402


@dataclass(frozen=True)
class SceneComparisonResult:
    scene_id: str
    producer_name: str
    producer_version: str
    dimensions_match: bool
    pixel_exact_match: bool
    #: Fraction of bytes that differ, 0.0 if pixel_exact_match. None if
    #: dimensions_match is False (no meaningful per-pixel comparison).
    byte_diff_fraction: float | None
    #: Max per-channel absolute difference observed, for a documented
    #: tolerance-based pass/fail distinct from pixel_exact_match.
    max_channel_delta: int | None
    within_tolerance: bool
    tolerance: int
    error: str | None = None


def compare_rasters(
    producer_raster: DecodedRaster,
    format_factory_raster: DecodedRaster,
    *,
    tolerance: int = 0,
) -> tuple[bool, float | None, int | None]:
    """Returns (pixel_exact_match, byte_diff_fraction, max_channel_delta).
    Pure function over already-decoded pixels -- no file I/O, no producer
    dependency, fully unit-testable."""
    if (producer_raster.width, producer_raster.height) != (
        format_factory_raster.width,
        format_factory_raster.height,
    ):
        return False, None, None

    a, b = producer_raster.pixels, format_factory_raster.pixels
    if a == b:
        return True, 0.0, 0

    diffs = 0
    max_delta = 0
    for x, y in zip(a, b):
        delta = abs(x - y)
        if delta:
            diffs += 1
            max_delta = max(max_delta, delta)
    return False, diffs / len(a), max_delta


def compare_scene(
    scene_id: str,
    producer_png_bytes: bytes,
    *,
    producer_name: str,
    producer_version: str,
    tolerance: int = 0,
) -> SceneComparisonResult:
    """Compare one producer's own exported PNG (its flattened render of
    `scene_id`) against format-factory's own render of the identical scene
    definition. `producer_png_bytes` is the producer's own output -- for a
    real GIMP run this is the .ora's own embedded mergedimage.png (or a
    plain PNG exported alongside it); for a contract test it is a
    synthetic stand-in, always labeled as such by the caller."""
    scene = scene_by_id(scene_id)
    try:
        producer_raster = decode_png(producer_png_bytes)
    except Exception as exc:  # noqa: BLE001 - reported, not raised, by design
        return SceneComparisonResult(
            scene_id=scene_id,
            producer_name=producer_name,
            producer_version=producer_version,
            dimensions_match=False,
            pixel_exact_match=False,
            byte_diff_fraction=None,
            max_channel_delta=None,
            within_tolerance=False,
            tolerance=tolerance,
            error=f"producer PNG failed to decode: {exc}",
        )

    ff_raster = render_scene(scene)
    dimensions_match = (producer_raster.width, producer_raster.height) == (
        ff_raster.width,
        ff_raster.height,
    )
    exact, diff_fraction, max_delta = compare_rasters(
        producer_raster, ff_raster, tolerance=tolerance
    )
    within_tolerance = dimensions_match and (
        exact or (max_delta is not None and max_delta <= tolerance)
    )
    return SceneComparisonResult(
        scene_id=scene_id,
        producer_name=producer_name,
        producer_version=producer_version,
        dimensions_match=dimensions_match,
        pixel_exact_match=exact,
        byte_diff_fraction=diff_fraction,
        max_channel_delta=max_delta,
        within_tolerance=within_tolerance,
        tolerance=tolerance,
    )


def write_manifest(results: list[SceneComparisonResult], output_path: Path) -> None:
    """Machine-readable manifest the obligation reconciler could consume as
    execution_evidence -- schema deliberately mirrors this repo's own
    execution_evidence conventions (a `result` field the reconciler cross
    -checks against a declared `expected_result`)."""
    payload = {
        "schema": "ora-producer-harness/comparison-manifest@1",
        "result": "PASS" if all(r.within_tolerance for r in results) else "FAIL",
        "scenes": [asdict(r) for r in results],
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_producer(command: list[str], *, timeout_seconds: int = 120) -> subprocess.CompletedProcess:
    """Shell out to a real producer binary (GIMP, in batch mode). The ONLY
    function in this module that needs a producer actually installed --
    everything above is pure comparison logic, independently testable."""
    return subprocess.run(
        command, capture_output=True, timeout=timeout_seconds, check=False
    )


__all__ = [
    "SceneComparisonResult",
    "compare_rasters",
    "compare_scene",
    "run_producer",
    "write_manifest",
]
