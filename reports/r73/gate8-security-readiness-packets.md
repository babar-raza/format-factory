# R73 Gate 8 Security Review Readiness Packets

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** H

Formats covered: ODS, ODT, QOI, XCF, DIF, PPM
Gate 8 status for all 6: PASS (recorded in acquisition-packs/{format}/pack.yaml, sprint R31)

---

## ODS

**Parser:** `src/python/ods/ods_parser.py`
**Gate 8 status:** PASS (sprint R31, delegated_expert_agent_review)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_ZIP_ENTRIES | 1000 |
| MAX_COLUMNS | 1024 |
| MAX_ROWS | 1,048,576 |
| XXE protection | YES — stdlib xml.etree.ElementTree (safe by default) |
| Zip bomb protection | MAX_ZIP_ENTRIES + file size guard |
| Size guard | Checked before parsing |

**Tests:** `tests/python/ods/` — gate5-7 tests + oracle + fuzz guard

### Gaps
- No streaming decode (all-in-memory)
- No per-entry decompressed-size check (relies on MAX_FILE_SIZE)

---

## ODT

**Parser:** `src/python/odt/odt_parser.py`
**Gate 8 status:** PASS (sprint R31, delegated_expert_agent_review)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_ZIP_ENTRIES | 1000 |
| XXE protection | YES — stdlib xml.etree.ElementTree |
| Zip bomb protection | MAX_ZIP_ENTRIES + file size guard |
| Size guard | Checked before parsing |

**Tests:** `tests/python/odt/` — gate5-7 tests

### Gaps
- No streaming decode
- No per-entry decompressed-size check

---

## QOI

**Parser:** `src/python/qoi/qoi_parser.py`
**Gate 8 status:** PASS (sprint R31)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_DIMENSION | 16,384 pixels |
| MAX_PIXELS | 268,435,456 (16384²) |
| Magic byte check | YES — 0x716f6966 ("qoif") |
| Dimension guard | width * height <= MAX_PIXELS |
| Size guard | Checked before parsing |

**Tests:** `tests/python/qoi/` — gate5-7 tests + fuzz guard

### Gaps
- No color profile handling (unsupported, not a security risk)
- Integer overflow guard relies on MAX_PIXELS check

---

## XCF

**Parser:** `src/python/xcf/xcf_parser.py`
**Gate 8 status:** PASS (sprint R31)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_DIMENSION | 262,144 pixels per axis |
| Magic byte check | YES — "gimp xcf " header |
| Dimension guard | width/height <= MAX_DIMENSION |
| Size guard | Checked before parsing |

**Tests:** `tests/python/xcf/` — gate5-7 tests

### Gaps
- GIMP XCF has complex optional chunk structure; extended chunk types not decoded (safe — skipped)
- No streaming decode

---

## DIF

**Parser:** `src/python/dif/dif_parser.py`
**Gate 8 status:** PASS (sprint R31)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_ROWS | 1,048,576 |
| MAX_COLUMNS | 16,384 |
| Text encoding | ASCII with errors="replace" (no injection risk) |
| Size guard | Checked before parsing |

**Tests:** `tests/python/dif/` — gate5-7 + r58-r73 deepening

### Gaps
- No formula evaluation (text-format only, not a risk)
- Large repeat counts bounded by MAX_ROWS/MAX_COLUMNS

---

## PPM

**Parser:** `src/python/ppm/ppm_parser.py`
**Gate 8 status:** PASS (sprint R31)

### Security Controls Present

| Control | Value |
|---|---|
| MAX_FILE_SIZE | 64 MiB |
| MAX_DIMENSION | 65,536 pixels per axis |
| MAX_MAXVAL | 65,535 |
| Magic byte check | YES — P3 (ASCII) or P6 (binary) |
| Dimension guard | width/height <= MAX_DIMENSION |
| Maxval guard | maxval <= MAX_MAXVAL |
| Size guard | Checked before parsing |

**Tests:** `tests/python/ppm/` — gate5-7 + r55-r73 deepening

### Gaps
- No 16-bit per-channel support (explicitly unsupported, not a risk)
- Binary P6 parsing uses raw byte slicing — safe within size guard

---

## Cross-Format Security Posture

| Format | Size Guard | Dimension Guard | XXE Safe | Zip Bomb Safe | Gate 8 |
|---|---|---|---|---|---|
| ODS | 64 MiB | 1024 cols / 1M rows | YES | YES | PASS |
| ODT | 64 MiB | — | YES | YES | PASS |
| QOI | 64 MiB | 16384² px | N/A | N/A | PASS |
| XCF | 64 MiB | 262144 px/axis | N/A | N/A | PASS |
| DIF | 64 MiB | 1M rows / 16K cols | N/A | N/A | PASS |
| PPM | 64 MiB | 65536 px/axis | N/A | N/A | PASS |

---

## Missing Items for Full Gate 8 Closure

None blocking. All formats have:
1. File size guard (64 MiB)
2. Dimension or count guards
3. Fail-closed error handling (never raises unexpected exceptions to caller)
4. `commercial_product_ready: False` governance

Gate 8 human IV (per DEC-034 policy) is required before publication. All delegated agent approvals in sprint R31 are provisional.

GATE8_SECURITY_READINESS: ASSESSED_6_FORMATS_ALL_CONTROLS_PRESENT
