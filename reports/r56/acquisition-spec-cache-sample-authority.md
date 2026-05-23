# Acquisition / Spec-Cache / Sample Authority Audit — Train H Report

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Train:** H — Acquisition/Spec-Cache/Sample Authority Audit
**Date:** 2026-05-23

---

## 1. Spec-Cache Audit

### 1.1 Cached Spec Inventory

```
python tools/spec-cache/spec_index.py list
```

| Format | Version | Status |
|--------|---------|--------|
| fods | ODF 1.3 | VALID [CURRENT] |
| zst | RFC 8878 | VALID [CURRENT] |
| zst | RFC 9659 | VALID [CURRENT] |
| abw | AWML 1.0 | INVALID (missing fields) |
| gnumeric | v10 | INVALID (missing fields) |

### 1.2 Invalid Spec Entries

**ABW** and **Gnumeric** spec-index.yaml entries are missing required fields:
`local_only`, `redistribution_permitted`, `canonical_url`, `source_url`.

These are pre-existing validation gaps. The ABW and Gnumeric parsers are not
in active development in R56. Deferred to R57 spec-cache repair sprint.

### 1.3 Unregistered Specs (formats without spec-cache entries)

The following formats are in active use but have no spec-cache entry:
- CSV (IETF RFC 4180 — public, online URL available)
- TSV (IANA text/tab-separated-values — public)
- SYLK (Microsoft 1986 — public documentation only, no canonical file)
- DIF (Software Arts 1981 — public documentation only)
- PGM/PBM/PPM (Netpbm man pages — public domain)

These are informational: spec-cache is not required for Gate passage.
Their spec URLs and versions are recorded in pack.yaml acquisition packs.

---

## 2. Sample Corpus Audit

```
samples/by-format/ — 20 format directories present
```

| Format | Sample Count | Notes |
|--------|-------------|-------|
| csv | 4 (3 valid + 1 invalid) | Gate 3 verified R31 |
| tsv | 4 (3 valid + 1 invalid) | Gate 3 verified R31 |
| sylk | 2 | Gate 3 pass R29 |
| dif | 2 | Gate 3 pass R29 |
| ppm | 2 | Gate 3 pass R29 |
| pgm | 2 | Gate 3 pass R29 |
| pbm | 2 | Gate 3 pass R29 |
| fods | multiple | R46 samples |
| fodt | multiple | R46 samples |
| zst | multiple | R34 samples |

---

## 3. Acquisition Pack Audit

### Active tracks (Gate 4+)

| Format | Highest Gate | Spec Authority | Legal Category |
|--------|-------------|---------------|---------------|
| FODS | Gate 10 | OASIS ODF 1.3 | 1 (open standard) |
| FODT | Gate 10 | OASIS ODF 1.3 | 1 (open standard) |
| CSV | Gate 5 | IETF RFC 4180 | 1 (IETF RFC) |
| TSV | Gate 5 | IANA media type | 1 (IANA) |
| PPM | Gate 10 | Netpbm man pages | 1 (public domain) |
| DIF | Gate 10 | Software Arts 1981 | 1 (public documentation) |
| SYLK | Gate 9 | Microsoft 1986 | 2 (legacy Microsoft, public) |
| PGM | Gate 9 | Netpbm man pages | 1 (public domain) |
| PBM | Gate 9 | Netpbm man pages | 1 (public domain) |

### Commercial product readiness

All `commercial_product_ready: false` confirmed across all active pack.yaml files.

---

## 4. R56 Acquisition Changes

- **CSV pack.yaml**: gate_5 added (R56 Train F)
- **TSV pack.yaml**: gate_5 added (R56 Train F)
- No new format candidates added in R56

---

## 5. Deferred Items

| Item | Format | Sprint |
|------|--------|--------|
| Spec-cache repair: add `local_only`/`redistribution_permitted`/`canonical_url`/`source_url` | ABW, Gnumeric | R57 |
| CSV/TSV spec-cache entries creation | CSV, TSV | R57 |
| PGM/PBM Gate 10 local release candidate | PGM, PBM | R57 |
| SYLK Gate 10 | SYLK | R57 |

---

**STATUS: TRAIN_H_COMPLETE — Audit complete; 2 pre-existing spec-cache gaps documented; no blocking issues**
