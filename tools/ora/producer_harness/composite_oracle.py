"""Independent mathematical oracle for ORA-COMPOSITE-001's own claimed
composite-op inventory (COMPOSITE_OP_REGISTRY, model/composite_ops.py).

Deliberately NOT importing or calling format_factory.ora.render's own
compositing code. PRECISE, HONEST scope of what "independent" means here
(corrected 2026-08-12 after an independent review found the original
docstring overclaimed this -- the per-channel review compared this file's
own code against render.py's line by line and found the blend-function
BODIES near-identical in structure, only the wrapper genuinely
independent; that finding is accurate and this note replaces the original
overclaim rather than hiding it):

- The COMPOSITING/BOUNDS control flow -- how a layer's own pixels combine
  with the canvas, straight-alpha throughout, structured as a single-pixel
  pure function rather than render.py's own premultiplied-canvas
  bounds-iterating sweep -- IS genuinely independently structured, and
  this is what actually caught the real Destination In/Atop bounds defect
  documented below: the oracle has no "iterate only the layer's own
  bounds" concept to share the bug with, because it never adopted that
  optimization at all.
- The per-channel BLEND-FUNCTION formula bodies (_multiply, _screen,
  _hard_light, etc.) are direct transcriptions of the W3C Compositing and
  Blending Level 1 spec's own published equations, which for most of
  these functions have essentially one sane way to write a single
  arithmetic expression -- these bodies are structurally similar to
  render.py's own, not independently varied. A bug in one of these
  specific formula bodies that ALSO happened to exist in render.py's own
  version would not be caught by cross-checking against this oracle. This
  oracle's own real value is (a) the independently-structured compositing
  wrapper, which found a genuine defect outside the per-channel formulas
  entirely, and (b) giving every producer-comparison result a citable,
  written-down expected value distinct from "whatever render.py happens
  to output," not a claim that every line of arithmetic was independently
  re-derived.

Scope matches COMPOSITE_OP_REGISTRY exactly: 15 blend functions (all
paired with Source Over) and 6 Porter-Duff operators (all paired with
Normal blend, i.e. no color mixing) -- 20 total composite-op values, not
independently combinable, matching the registry's own real structure
(this is not a full blend x Porter-Duff cross-product; the registry never
claims one).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

RGB = tuple[float, float, float]


def _multiply(cb: float, cs: float) -> float:
    return cb * cs


def _screen(cb: float, cs: float) -> float:
    return cb + cs - cb * cs


def _hard_light(cb: float, cs: float) -> float:
    return _multiply(cb, 2 * cs) if cs <= 0.5 else _screen(cb, 2 * cs - 1)


def _overlay(cb: float, cs: float) -> float:
    return _hard_light(cs, cb)


def _color_dodge(cb: float, cs: float) -> float:
    if cb == 0.0:
        return 0.0
    if cs >= 1.0:
        return 1.0
    return min(1.0, cb / (1.0 - cs))


def _color_burn(cb: float, cs: float) -> float:
    if cb >= 1.0:
        return 1.0
    if cs <= 0.0:
        return 0.0
    return 1.0 - min(1.0, (1.0 - cb) / cs)


def _soft_light(cb: float, cs: float) -> float:
    if cs <= 0.5:
        return cb - (1 - 2 * cs) * cb * (1 - cb)
    d = ((16 * cb - 12) * cb + 4) * cb if cb <= 0.25 else cb ** 0.5
    return cb + (2 * cs - 1) * (d - cb)


SEPARABLE_BLEND: dict[str, Callable[[float, float], float]] = {
    "Normal": lambda cb, cs: cs,
    "Multiply": _multiply,
    "Screen": _screen,
    "Overlay": _overlay,
    "Darken": min,
    "Lighten": max,
    "Color Dodge": _color_dodge,
    "Color Burn": _color_burn,
    "Hard Light": _hard_light,
    "Soft Light": _soft_light,
    "Difference": lambda cb, cs: abs(cb - cs),
}


def _lum(c: RGB) -> float:
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _clip_colour(c: RGB) -> RGB:
    r, g, b = c
    lum = _lum(c)
    lo, hi = min(r, g, b), max(r, g, b)
    if lo < 0.0 and lum != lo:
        scale = lum / (lum - lo)
        r, g, b = (lum + (v - lum) * scale for v in (r, g, b))
    if hi > 1.0 and hi != lum:
        scale = (1.0 - lum) / (hi - lum)
        r, g, b = (lum + (v - lum) * scale for v in (r, g, b))
    return (r, g, b)


def _set_lum(c: RGB, lum: float) -> RGB:
    d = lum - _lum(c)
    return _clip_colour((c[0] + d, c[1] + d, c[2] + d))


def _sat(c: RGB) -> float:
    return max(c) - min(c)


def _set_sat(c: RGB, s: float) -> RGB:
    order = sorted(range(3), key=lambda i: c[i])
    lo, mid, hi = order
    out = [0.0, 0.0, 0.0]
    if c[hi] > c[lo]:
        out[mid] = (c[mid] - c[lo]) * s / (c[hi] - c[lo])
        out[hi] = s
    return (out[0], out[1], out[2])


NONSEPARABLE_BLEND = {
    "Hue": lambda cb, cs: _set_lum(_set_sat(cs, _sat(cb)), _lum(cb)),
    "Saturation": lambda cb, cs: _set_lum(_set_sat(cb, _sat(cs)), _lum(cb)),
    "Color": lambda cb, cs: _set_lum(cs, _lum(cb)),
    "Luminosity": lambda cb, cs: _set_lum(cb, _lum(cs)),
}

ALL_BLEND_NAMES = tuple(SEPARABLE_BLEND) + tuple(NONSEPARABLE_BLEND)
assert len(ALL_BLEND_NAMES) == 15, f"expected 15 blend functions, got {len(ALL_BLEND_NAMES)}"

PORTER_DUFF_OPERATORS = (
    "Source Over",
    "Lighter",
    "Destination In",
    "Destination Out",
    "Source Atop",
    "Destination Atop",
)


def porter_duff_coeffs(operator: str, alpha_s: float, alpha_b: float) -> tuple[float, float]:
    """(Fa, Fb) per Porter & Duff (1984) such that
    Co_premult = Fa*(alpha_s*Cs) + Fb*Cb_premult, alpha_o = Fa*alpha_s + Fb*alpha_b."""
    if operator == "Source Over":
        return 1.0, 1.0 - alpha_s
    if operator == "Lighter":
        return 1.0, 1.0
    if operator == "Destination In":
        return 0.0, alpha_s
    if operator == "Destination Out":
        return 0.0, 1.0 - alpha_s
    if operator == "Source Atop":
        return alpha_b, 1.0 - alpha_s
    if operator == "Destination Atop":
        return 1.0 - alpha_b, alpha_s
    raise ValueError(f"unknown Porter-Duff operator {operator!r}")


@dataclass(frozen=True)
class Pixel:
    """Straight (non-premultiplied) RGBA, each channel 0.0-1.0."""

    r: float
    g: float
    b: float
    a: float

    def rgba8(self) -> tuple[int, int, int, int]:
        def c(v: float) -> int:
            scaled = round(v * 255.0)
            return 0 if scaled < 0 else 255 if scaled > 255 else scaled

        return (c(self.r), c(self.g), c(self.b), c(self.a))


def composite_source_over_with_blend(
    backdrop: Pixel, source: Pixel, blend_name: str
) -> Pixel:
    """W3C Compositing and Blending Level 1, section 8.1/8.2: general
    formula Co = (1-alpha_s)*Cb + alpha_s*[(1-alpha_b)*Cs + alpha_b*B(Cb,Cs)],
    alpha_o = alpha_s + alpha_b*(1-alpha_s). Independently re-derived in
    straight alpha throughout (render.py's own implementation instead
    works in a premultiplied canvas) -- Cb is undefined color when
    alpha_b==0, matching the spec's own explicit statement that blend
    results are irrelevant there since they get scaled by alpha_b anyway."""
    cb = (backdrop.r, backdrop.g, backdrop.b)
    cs = (source.r, source.g, source.b)
    if blend_name == "Normal":
        cm = cs
    elif blend_name in NONSEPARABLE_BLEND:
        cm = NONSEPARABLE_BLEND[blend_name](cb, cs)
    else:
        fn = SEPARABLE_BLEND[blend_name]
        cm = (fn(cb[0], cs[0]), fn(cb[1], cs[1]), fn(cb[2], cs[2]))
    mixed = tuple(
        (1 - backdrop.a) * cs[i] + backdrop.a * cm[i] for i in range(3)
    )
    alpha_s, alpha_b = source.a, backdrop.a
    out_rgb = tuple(
        (1 - alpha_s) * (backdrop.r, backdrop.g, backdrop.b)[i] + alpha_s * mixed[i]
        for i in range(3)
    )
    out_a = alpha_s + alpha_b * (1 - alpha_s)
    return Pixel(out_rgb[0], out_rgb[1], out_rgb[2], out_a)


def composite_porter_duff(backdrop: Pixel, source: Pixel, operator: str) -> Pixel:
    """Pure Porter-Duff compositing (Normal blend, i.e. Cm=Cs always) in
    premultiplied space (required -- Porter-Duff coefficients are only
    meaningful applied to premultiplied color), then converted back to
    straight alpha for the final pixel value."""
    fa, fb = porter_duff_coeffs(operator, source.a, backdrop.a)
    src_premult = (source.a * source.r, source.a * source.g, source.a * source.b)
    dst_premult = (backdrop.a * backdrop.r, backdrop.a * backdrop.g, backdrop.a * backdrop.b)
    out_premult = tuple(fa * src_premult[i] + fb * dst_premult[i] for i in range(3))
    out_a = fa * source.a + fb * backdrop.a
    if out_a > 0.0:
        out_rgb = tuple(v / out_a for v in out_premult)
    else:
        out_rgb = (0.0, 0.0, 0.0)
    return Pixel(out_rgb[0], out_rgb[1], out_rgb[2], out_a)


def composite(backdrop: Pixel, source: Pixel, blend_name: str, operator: str) -> Pixel:
    if operator == "Source Over":
        return composite_source_over_with_blend(backdrop, source, blend_name)
    assert blend_name == "Normal", f"registry never pairs {blend_name!r} with {operator!r}"
    return composite_porter_duff(backdrop, source, operator)


__all__ = [
    "ALL_BLEND_NAMES",
    "NONSEPARABLE_BLEND",
    "PORTER_DUFF_OPERATORS",
    "Pixel",
    "SEPARABLE_BLEND",
    "composite",
    "composite_porter_duff",
    "composite_source_over_with_blend",
    "porter_duff_coeffs",
]
