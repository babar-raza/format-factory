"""Deterministic contact sheets for ORA-BASELINEASSET-001's amended
visual-assurance procedure (step 7 of
reports/format-contract-layer/ora-baseline-asset-visual-assurance-amendment.md).

No image-processing library is available in this project's own venv
(stdlib-only, matching render.py's own PNG codec) -- panels are laid out
as nearest-neighbor-upscaled color blocks separated by a fixed-color
gutter, not annotated with baked-in text (a bitmap font would be
disproportionate effort for this step); panel order and metrics are
documented in the accompanying manifest/prompt instead.

Layout, left to right: format-factory output | GIMP-decoded read-back |
Krita-decoded read-back | amplified per-pixel diff (max over the two
producers, amplified so all-zero panels remain visibly checkable as
"flat black", not merely computed).
"""
from __future__ import annotations

import json
import re
import struct
import sys
import zlib
from pathlib import Path

_ORA_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"
if str(_ORA_SRC) not in sys.path:
    sys.path.insert(0, str(_ORA_SRC))
from format_factory.ora.render import DecodedRaster, encode_png  # noqa: E402

SCALE = 10
GUTTER = 4
GUTTER_RGBA = (255, 255, 0, 255)  # bright yellow, unambiguous against any scene palette


def _upscale(pixels: bytes, w: int, h: int, scale: int) -> bytes:
    out = bytearray(w * scale * h * scale * 4)
    row_bytes = w * scale * 4
    for y in range(h):
        src_row = pixels[y * w * 4:(y + 1) * w * 4]
        up_row = bytearray(w * scale * 4)
        for x in range(w):
            px = src_row[x * 4:x * 4 + 4]
            for s in range(scale):
                up_row[(x * scale + s) * 4:(x * scale + s) * 4 + 4] = px
        for s in range(scale):
            out[(y * scale + s) * row_bytes:(y * scale + s + 1) * row_bytes] = up_row
    return bytes(out)


def _gutter_column(h: int) -> bytes:
    return bytes(GUTTER_RGBA) * (GUTTER * h)


def _load_csv_pixels(path: Path, is_gimp: bool) -> dict:
    result: dict = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if is_gimp:
            m = re.match(r"^script-fu-Warning: (.+)$", line)
            if m:
                line = m.group(1)
        parts = line.split(",")
        if len(parts) != 7:
            continue
        scene_id, x_s, y_s, r_s, g_s, b_s, a_s = parts
        try:
            x, y, r, g, b, a = int(x_s), int(y_s), int(r_s), int(g_s), int(b_s), int(a_s)
        except ValueError:
            continue
        result.setdefault(scene_id, {})[(x, y)] = (r, g, b, a)
    return result


def _raster_from_table(table: dict, w: int, h: int) -> bytes:
    out = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * 4
            r, g, b, a = table.get((x, y), (255, 0, 255, 255))  # magenta = missing pixel, should never appear
            out[o:o + 4] = bytes((r, g, b, a))
    return bytes(out)


def build(scratch: Path, out_dir: Path) -> None:
    manifest = json.loads((scratch / "expected-manifest.json").read_text())
    gimp_px = _load_csv_pixels(scratch / "gimp-pixel-dump.log", is_gimp=True)
    krita_px = _load_csv_pixels(scratch / "krita-baseline-pixel-dump.log", is_gimp=False)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for row in manifest:
        scene_id, w, h = row["scene_id"], row["width"], row["height"]
        expected = bytes.fromhex(row["expected_pixels_hex"])
        gimp_raster = _raster_from_table(gimp_px.get(scene_id, {}), w, h)
        krita_raster = _raster_from_table(krita_px.get(scene_id, {}), w, h)

        diff = bytearray(w * h * 4)
        max_delta = 0
        mismatch_count = 0
        for i in range(0, len(expected), 4):
            worst = 0
            for producer_raster in (gimp_raster, krita_raster):
                d = max(abs(expected[i + c] - producer_raster[i + c]) for c in range(4))
                worst = max(worst, d)
            max_delta = max(max_delta, worst)
            if worst:
                mismatch_count += 1
            amplified = min(255, worst * 16)
            diff[i:i + 3] = bytes((amplified, amplified, amplified))
            diff[i + 3] = 255

        panels = [
            _upscale(expected, w, h, SCALE),
            _upscale(gimp_raster, w, h, SCALE),
            _upscale(krita_raster, w, h, SCALE),
            _upscale(bytes(diff), w, h, SCALE),
        ]
        sheet_w = w * SCALE * 4 + GUTTER * 3
        sheet_h = h * SCALE
        sheet = bytearray(sheet_w * sheet_h * 4)
        panel_w = w * SCALE
        col = 0
        for i, panel in enumerate(panels):
            for y in range(sheet_h):
                dst_off = (y * sheet_w + col) * 4
                src_off = y * panel_w * 4
                sheet[dst_off:dst_off + panel_w * 4] = panel[src_off:src_off + panel_w * 4]
            col += panel_w
            if i < len(panels) - 1:
                for y in range(sheet_h):
                    dst_off = (y * sheet_w + col) * 4
                    sheet[dst_off:dst_off + GUTTER * 4] = GUTTER_RGBA * GUTTER
                col += GUTTER

        png_bytes = encode_png(DecodedRaster(width=sheet_w, height=sheet_h, pixels=bytes(sheet)))
        out_path = out_dir / f"contact-sheet-{scene_id}.png"
        out_path.write_bytes(png_bytes)
        summary.append({
            "scene_id": scene_id,
            "path": str(out_path),
            "panel_order": ["format-factory", "gimp-decoded", "krita-decoded", "amplified-diff(x16, max-over-producers)"],
            "panel_width_px": panel_w,
            "sheet_width_px": sheet_w,
            "sheet_height_px": sheet_h,
            "max_delta": max_delta,
            "mismatch_pixel_count": mismatch_count,
            "total_pixels": w * h,
        })
        print(f"{scene_id}: max_delta={max_delta} mismatches={mismatch_count}/{w*h} -> {out_path}")

    (out_dir / "contact-sheet-manifest.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build(Path(sys.argv[1]), Path(sys.argv[2]))
