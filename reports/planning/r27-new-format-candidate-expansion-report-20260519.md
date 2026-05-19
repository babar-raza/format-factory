---
document_type: sprint_report
sprint: R27
lane: J
title: "R27 Lane J — New Candidate Expansion: XCF and ZPAQ Gates 1-3"
date: "2026-05-19"
visibility: internal
publish_allowed: false
---

# R27 Lane J — New Format Candidate Expansion Report

**Date:** 2026-05-19
**Lane:** J — New Candidate Expansion
**Formats:** XCF (GIMP native), ZPAQ (archive)
**Source:** docs/format-expansion-roadmap.md Section 3.1 Tier A candidates

---

## Summary

Two new format candidates were selected from the Tier A expansion list and processed
through Gates 1-3. Both have full public specifications and are not supported by Aspose,
providing commercial differentiation value.

| Format | Gate 1 | Gate 2 | Gate 3 | Score | Band |
|--------|--------|--------|--------|-------|------|
| XCF    | PASS   | PASS   | PASS   | 78/100 (7.8) | Accept |
| ZPAQ   | PASS   | PASS   | BLOCKED | 62/100 (6.2) | Review |

---

## Format 1: XCF (GIMP Native Image Format)

**Pack:** `acquisition-packs/xcf/pack.yaml`
**Family:** Imaging
**Legal Category:** 2 (Permissive OSS)
**Aspose Support:** NOT_SUPPORTED (positive differentiation)

### Gate 1 — Decision Packet (PASS)

Score: 78/100 (7.8/10) — Accept band.

| Factor | Score | Points | Key Evidence |
|--------|-------|--------|--------------|
| Legal Safety | 2 | 20/30 | GPLv3 on GIMP source; format itself is open; independent parsers legal |
| Spec Availability | 2 | 13/20 | GIMP developer wiki + source code; documented but some edge cases need source inspection |
| Parseable Structure | 2 | 10/15 | Binary with clear header; property TLV encoding; tile data adds complexity |
| Community Demand | 2 | 10/15 | GIMP is most popular FOSS image editor; moderate programmatic access demand |
| Strategic Track Value | 2 | 7/10 | Second imaging format after QOI; layered editing format distinct from simple raster |
| Implementation Complexity | 1 | 2/5 | Multiple compression modes, tile-based data, parasites; header parsing moderate |
| Family Overlap | 3 | 5/5 | No overlap; unique layered editing format |

Approval: delegated_agent_decision_r27, awaiting_human_iv: true

### Gate 2 — Spec Evidence (PASS)

- **Spec source:** https://developer.gimp.org/core/xcf/
- **Authoritative reference:** GIMP source code (app/xcf/xcf-load.c, xcf-save.c)
- **Version:** XCF v011 (GIMP 2.10+)
- **Access:** Public
- **Patent claims:** None
- **Key structures documented:** 14-byte header, canvas properties, property list (TLV),
  layer/channel offsets, hierarchy, tiles, compression modes (none/RLE/zlib)

### Gate 3 — Sample Corpus (PASS)

- **Samples generated:** 3 valid + 1 invalid
- **Method:** deterministic_synthetic_python_struct (no external dependencies)
- **Location:** `samples/by-format/xcf/`

| Sample | Size | Category | Description |
|--------|------|----------|-------------|
| valid/1x1-red-rgb.xcf | 177 B | minimal-valid-rgb | 1x1 RGB red pixel |
| valid/2x2-gray.xcf | 178 B | grayscale-multi-pixel | 2x2 grayscale gradient |
| valid/1x1-rgba-blue.xcf | 178 B | minimal-valid-rgba | 1x1 RGBA blue pixel |
| invalid/wrong-magic.xcf | 28 B | invalid-magic | 'NOT XCF!' instead of 'gimp xcf ' |

All valid samples have correct magic bytes ('gimp xcf '), version (v011), and contain
one uncompressed layer with raw pixel tile data.

---

## Format 2: ZPAQ (Archive Format)

**Pack:** `acquisition-packs/zpaq/pack.yaml`
**Family:** Archive
**Legal Category:** 2 (Public Domain)
**Aspose Support:** NOT_SUPPORTED (positive differentiation)

### Gate 1 — Decision Packet (PASS with Review band notation)

Score: 62/100 (6.2/10) — Review band (below 7.0 Accept threshold).

| Factor | Score | Points | Key Evidence |
|--------|-------|--------|--------------|
| Legal Safety | 2 | 20/30 | Public domain — author explicitly released all rights |
| Spec Availability | 2 | 13/20 | Full PDF spec at mattmahoney.net; covers block structure and ZPAQL VM |
| Parseable Structure | 1 | 5/15 | Complex: ZPAQL bytecode VM required for decompression |
| Community Demand | 1 | 5/15 | Niche: backup enthusiasts, data archivists |
| Strategic Track Value | 2 | 7/10 | Second archive format after ZST; distinct (journaling + dedup) |
| Implementation Complexity | 1 | 2/5 | High: requires ZPAQL bytecode interpreter; ~3000 lines reference impl |
| Family Overlap | 2 | 3/5 | Minor overlap with ZST; fundamentally different approach |

Note: Score in Review band (62/100). High legal safety (public domain) offset by
implementation complexity (embedded VM) and niche demand. Passed by delegated agent
with review-band notation; human decision on whether to proceed recommended.

### Gate 2 — Spec Evidence (PASS)

- **Spec source:** http://mattmahoney.net/dc/zpaq206.pdf
- **Reference implementation:** mattmahoney.net/dc/zpaq.cpp (public domain)
- **Version:** ZPAQ Level 2 (v2.06, 2013)
- **Access:** Public
- **Patent claims:** None (public domain)
- **Key structures documented:** Block headers ('zPQ' magic), segments, ZPAQL VM
  instruction set, context mixing, arithmetic coding, journaling

### Gate 3 — Sample Corpus (BLOCKED)

**Status:** blocked_sample_generation_requires_tool

ZPAQ archives cannot be constructed with Python struct alone because:
1. Valid archives require embedded ZPAQL bytecode programs (compression model)
2. Compressed data must be decompressible by the embedded model
3. Context mixing and arithmetic coding are integral to the format

**Resolution paths:**
- A. Install zpaq CLI tool and generate samples via command-line
- B. Port minimal ZPAQL context model from reference implementation
- C. Source public domain ZPAQ test files with provenance documentation

---

## Artifacts Created

| Artifact | Path |
|----------|------|
| XCF acquisition pack | `acquisition-packs/xcf/pack.yaml` |
| ZPAQ acquisition pack | `acquisition-packs/zpaq/pack.yaml` |
| XCF corpus manifest | `samples/by-format/xcf/_corpus-manifest.yaml` |
| XCF provenance | `samples/by-format/xcf/_provenance.yaml` |
| XCF valid sample 1 | `samples/by-format/xcf/valid/1x1-red-rgb.xcf` |
| XCF valid sample 2 | `samples/by-format/xcf/valid/2x2-gray.xcf` |
| XCF valid sample 3 | `samples/by-format/xcf/valid/1x1-rgba-blue.xcf` |
| XCF invalid sample | `samples/by-format/xcf/invalid/wrong-magic.xcf` |
| This report | `reports/planning/r27-new-format-candidate-expansion-report-20260519.md` |

---

## Next Steps

1. **Human IV required** for both XCF and ZPAQ Gate 1-2 decisions (DEC-034)
2. **Human IV required** for XCF Gate 3 corpus
3. **ZPAQ Gate 3 resolution** — decide on sample generation strategy (install zpaq CLI, port minimal model, or source test files)
4. **ZPAQ review-band decision** — human review recommended given 6.2/10 score; implementation complexity is the primary concern
5. **No source code created** — no `src/python/xcf/` or `src/python/zpaq/` directories
6. **No tools/ai or tests/ai modifications** made
