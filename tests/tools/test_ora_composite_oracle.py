"""Regression tests for tools/ora/producer_harness/composite_oracle.py.

Covers a real bug found and fixed 2026-08-12 (fourth continuation): the
Lighter operator's own combined alpha (alpha_s + alpha_b) can exceed
1.0, and composite_porter_duff() divided by that UNCLAMPED value when
unpremultiplying color, silently producing incorrect (too-dark) RGB
output -- Pixel.rgba8()'s own per-channel display clamp masked this by
correctly showing alpha=255, hiding that RGB had already been divided
by the wrong (too-large) denominator. Caught by comparing against
GEGL's own real, independent svg:plus implementation
(operations/generated/plus.c), whose real output for this obligation's
own canonical Lighter fixture did not match this oracle's own prior
output -- confirmed via direct hand-verification against the Porter &
Duff (1984) formula that GEGL was right and this oracle was wrong.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ora.producer_harness.composite_oracle import (  # noqa: E402
    Pixel,
    composite,
    composite_porter_duff,
)


def test_lighter_clamps_combined_alpha_before_unpremultiplying() -> None:
    """The obligation's own canonical Lighter discriminating fixture
    (destination (230,60,40) alpha 153/255 at (0,0)-(20,20); source
    (40,120,230) alpha 128/255 at (12,12)-(32,32)) has a combined alpha
    of 153/255 + 128/255 = 1.102 at the overlap point -- exceeding 1.0.
    Real, independent verification: GEGL's own operations/generated/
    plus.c (a real, separately-developed, spec-derived compositing
    library, not this project's own code) produces (158,96,139,255) for
    this exact input, confirmed via a real `gegl` CLI invocation this
    session. This must match exactly, not merely be close."""
    destination = Pixel(230 / 255, 60 / 255, 40 / 255, 153 / 255)
    source = Pixel(40 / 255, 120 / 255, 230 / 255, 128 / 255)

    result = composite(destination, source, "Normal", "Lighter")

    assert result.rgba8() == (158, 96, 139, 255)


def test_lighter_combined_alpha_is_clamped_in_the_stored_pixel_not_only_at_display_time() -> None:
    """The bug specifically hid behind Pixel.rgba8()'s own display-time
    clamp: the raw, unclamped alpha (1.102) still rounds to 255 there
    either way, so checking rgba8() alone would not have caught a
    regression back to the old, unclamped-divisor behavior. Assert the
    stored float alpha itself is clamped, not just its rounded display
    value."""
    destination = Pixel(230 / 255, 60 / 255, 40 / 255, 153 / 255)
    source = Pixel(40 / 255, 120 / 255, 230 / 255, 128 / 255)

    result = composite_porter_duff(destination, source, "Lighter")

    assert result.a == 1.0


def test_destination_in_alpha_never_exceeds_one_so_clamping_never_engages() -> None:
    """Contrast case: Destination In's own alpha formula (Fb=alpha_s)
    algebraically stays within [0,1] for any valid input, so this
    obligation's own already-established Destination In evidence
    (Krita agreement, already committed) is unaffected by this fix --
    confirmed directly, not merely asserted."""
    backdrop = Pixel(230 / 255, 60 / 255, 40 / 255, 153 / 255)
    source = Pixel(40 / 255, 120 / 255, 230 / 255, 128 / 255)

    result = composite_porter_duff(backdrop, source, "Destination In")

    expected_a = (128 / 255) * (153 / 255)
    assert abs(result.a - expected_a) < 1e-9
    assert result.a < 1.0
