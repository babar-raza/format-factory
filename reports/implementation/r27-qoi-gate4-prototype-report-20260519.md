# QOI Gate 4 Prototype Report
# Sprint: R27 Lane E
# Date: 2026-05-19

## Implementation

**Source:** src/python/qoi/qoi_parser.py
**Package:** src/python/qoi/__init__.py (v0.1.0.dev0, python-foss, alpha-foss-preview)

### Public API

- `parse_qoi(file_path)` — returns result dict (never raises)
- `parse_qoi_strict(file_path)` — raises QoiError on failure, returns QoiImage
- `probe_qoi(file_path)` — returns header metadata without pixel decode

### Data Model

- QoiImage (width, height, channels, colorspace, pixels, path)

### Technology

Python struct.unpack binary decoder (stdlib only)

### Security Guards

| Guard | Limit |
|-------|-------|
| Max file size | 64 MiB |
| Max dimensions | 16384 x 16384 |
| Max pixel count | 268,435,456 |
| Magic validation | exact b'qoif' |
| Channels validation | 3 or 4 only |
| Colorspace validation | 0 or 1 only |
| End marker validation | exact 8-byte sequence |

### Prototype Scope

| Feature | Status |
|---------|--------|
| Header probe | YES |
| Magic/format validation | YES |
| Full pixel decode (all 6 ops) | YES |
| QOI_OP_RGB | YES |
| QOI_OP_RGBA | YES |
| QOI_OP_INDEX | YES |
| QOI_OP_DIFF | YES |
| QOI_OP_LUMA | YES |
| QOI_OP_RUN | YES |
| Colorspace metadata | YES (reported, not transformed) |
| PNG export | NO (requires Pillow) |
| Write/encode | NO (Phase 2) |

## Tests

**File:** tests/python/qoi/test_qoi_parser.py
**Result:** 10/10 PASS

| Test | Status |
|------|--------|
| test_1x1_red | PASS |
| test_2x2_black | PASS |
| test_4x1_gradient | PASS |
| test_wrong_magic | PASS |
| test_wrong_magic_raises_strict | PASS |
| test_nonexistent_file | PASS |
| test_short_file | PASS |
| test_probe_valid | PASS |
| test_probe_nonexistent | PASS |
| test_dict_output | PASS |

## Gate 4 Status

- gate_4.status: prototype_complete
- production_source_authorized: true (prototype scope only)
- commercial_product_ready: false
- implementation_authorized: true (R27)

**LANE E STATUS: QOI GATE 4 PROTOTYPE COMPLETE — 10/10 TESTS PASS**
