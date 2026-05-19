# QOI Gate 4 Parser Plan
# Format: Quite OK Image Format (.qoi)
# Sprint: R26
# Date: 2026-05-19
# Status: parser_plan_complete
# Authorization: PLANNING ONLY — no production source authorized

## Parser API

**Class:** `QoiParser`
**Method:** `parse(path: str) -> QoiImage`

### QoiImage Structure

```
QoiImage
  width: int           # Image width in pixels
  height: int          # Image height in pixels
  channels: int        # 3 (RGB) or 4 (RGBA)
  colorspace: int      # 0 (sRGB with linear alpha) or 1 (all channels linear)
  pixels: list[tuple]  # List of (R, G, B) or (R, G, B, A) tuples
```

## Technology

- **Binary parsing:** Python `struct.unpack` (stdlib) — big-endian header fields
- **File I/O:** `open(path, 'rb')` — raw byte reading
- **No third-party dependencies** for core parsing

## QOI Binary Structure

### Header (14 bytes)

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 4 | bytes | magic | `b'qoif'` (0x71, 0x6F, 0x69, 0x66) |
| 4 | 4 | uint32 BE | width | Image width in pixels |
| 8 | 4 | uint32 BE | height | Image height in pixels |
| 12 | 1 | uint8 | channels | 3 = RGB, 4 = RGBA |
| 13 | 1 | uint8 | colorspace | 0 = sRGB + linear alpha, 1 = all linear |

### Chunk Types (6 operations)

| Op | Tag Byte | Size | Description |
|----|----------|------|-------------|
| `QOI_OP_RGB` | `0xFE` | 4 bytes (tag + R + G + B) | Literal RGB pixel |
| `QOI_OP_RGBA` | `0xFF` | 5 bytes (tag + R + G + B + A) | Literal RGBA pixel |
| `QOI_OP_INDEX` | `0b00xxxxxx` | 1 byte | Index into 64-color running hash array |
| `QOI_OP_DIFF` | `0b01xxxxxx` | 1 byte | Small RGB delta (dr/dg/db each -2..1) |
| `QOI_OP_LUMA` | `0b10xxxxxx` | 2 bytes | Larger green-channel delta with dr-dg, db-dg |
| `QOI_OP_RUN` | `0b11xxxxxx` | 1 byte | Run-length repeat (1-62 pixels) |

### End Marker (8 bytes)

```
0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01
```

Seven zero bytes followed by `0x01`.

## Decoder Algorithm

1. Read and validate 14-byte header (magic must be `b'qoif'`)
2. Initialize 64-entry color hash array to `(0, 0, 0, 0)`
3. Set previous pixel to `(0, 0, 0, 255)`
4. Read chunks until `width * height` pixels decoded:
   - `0xFE` (QOI_OP_RGB): read 3 bytes, update R/G/B, keep previous A
   - `0xFF` (QOI_OP_RGBA): read 4 bytes, update R/G/B/A
   - `0b00xxxxxx` (QOI_OP_INDEX): look up pixel from hash array at index (low 6 bits)
   - `0b01xxxxxx` (QOI_OP_DIFF): compute dr/dg/db from 2-bit fields, add to previous
   - `0b10xxxxxx` (QOI_OP_LUMA): read second byte, compute dg from low 6 bits minus 32, dr = dg + high nibble minus 8, db = dg + low nibble minus 8
   - `0b11xxxxxx` (QOI_OP_RUN): emit previous pixel (low 6 bits + 1) times
5. After each non-run op, update hash array: `index = (r*3 + g*5 + b*7 + a*11) % 64`
6. Verify 8-byte end marker

## Security Guards

| Guard | Limit | Rationale |
|-------|-------|-----------|
| Max file size | 64 MiB | Prevent memory exhaustion |
| Max image dimensions | 16384 x 16384 | Prevent memory exhaustion from decompressed pixel array |
| Max pixel count | 268,435,456 (16384^2) | Explicit cap on `width * height` |
| Magic validation | exact `b'qoif'` | Reject non-QOI files immediately |
| Channels validation | must be 3 or 4 | Reject invalid channel count |
| Colorspace validation | must be 0 or 1 | Reject invalid colorspace |
| End marker validation | exact 8-byte sequence | Detect truncated or corrupted files |

## Test Cases (Gate 4 Plan)

| Test Case | Sample | Expected Result |
|-----------|--------|-----------------|
| Valid 1x1 red pixel | `valid/1x1-red.qoi` | 1x1 RGBA, pixel (255, 0, 0, 255) |
| Valid 2x2 black (run-length) | `valid/2x2-black.qoi` | 2x2 RGBA, 4 pixels all (0, 0, 0, 255) |
| Valid 4x1 gradient | `valid/4x1-gradient.qoi` | 4x1 RGB, 4 greyscale pixels |
| Invalid wrong magic | `invalid/wrong-magic.qoi` | Raise `InvalidMagic` or equivalent error |
| Invalid truncated file | synthetic | Raise error on premature EOF |
| Header probe only | `valid/1x1-red.qoi` | Return width=1, height=1, channels=4, colorspace=0 |
| All 6 chunk types | synthetic | Decode QOI_OP_RGB, RGBA, INDEX, DIFF, LUMA, RUN correctly |
| Dimension guard exceeded | synthetic 20000x20000 header | Reject before decoding pixels |
| File size guard exceeded | synthetic >64MiB | Reject before parsing |
| Missing end marker | synthetic | Raise error on missing/incorrect end marker |

## Prototype Scope (Gate 4)

| Feature | Included | Notes |
|---------|----------|-------|
| Header probe (dimensions, channels) | YES | |
| Magic/format validation | YES | |
| Full pixel decode (all 6 chunk types) | YES | |
| Raw pixel array output | YES | List of (R, G, B[, A]) tuples |
| Colorspace metadata | YES | Reported but not transformed |
| PNG export | NO | Requires Pillow (not stdlib) |
| Animation | NO | QOI is still-image only |
| Write/encode | NO | Phase 2 |

## Gate 4 Status

```
gate_4_status: parser_plan_complete
production_source_authorized: false
commercial_product_ready: false
implementation_authorized: false
```

## References

- QOI Specification 1.0: https://qoif.org/ / https://qoi.phoboslab.org/
- Reference implementation: https://github.com/phoboslab/qoi (MIT license)
- Parser notes: `acquisition-packs/qoi/parser-notes.md`
- Sample corpus: `samples/by-format/qoi/_corpus-manifest.yaml`
- Gate 3 IV report: `reports/planning/r25-qoi-iv-gate4-readiness-report-20260518.md`
