# Context Pack Generation Report — R2
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001
Generated: 2026-06-05

## Overview

All 4 format context packs built from real sources. FODS context pack completed in R2
(deferred from R1). All packs deterministic across two independent runs.

## Context Packs Built

| Format | Context Pack ID | Manifest SHA-256 | Verified |
|--------|----------------|-----------------|---------|
| ZST | CP-ZST-9707e015c308 | 9707e015c3081ce2... | PASS |
| Netpbm | CP-NETPBM-9dee4b8f8608 | 9dee4b8f8608ff87... | PASS |
| DIF | CP-DIF-9ccc23683556 | 9ccc23683556d1b6... | PASS |
| FODS | CP-FODS-418cb43b3ad8 | 418cb43b3ad808ea... | PASS |

## Determinism Proof

Each context pack was built twice (identical inputs, same artifacts_dir). SHA-256 identical.

| Format | Run 1 SHA-256 | Run 2 SHA-256 | Deterministic |
|--------|--------------|--------------|---------------|
| ZST | 9707e015c3081ce2... | 9707e015c3081ce2... | YES |
| Netpbm | 9dee4b8f8608ff87... | 9dee4b8f8608ff87... | YES |
| DIF | 9ccc23683556d1b6... | 9ccc23683556d1b6... | YES |
| FODS | 418cb43b3ad808ea... | 418cb43b3ad808ea... | YES |

All 4 formats: DETERMINISTIC.

## Context Pack Files

Output location: .local/evidences/spec-authority-real-pilot-r2/context-packs/
- zst-context-pack.json
- netpbm-context-pack.json
- dif-context-pack.json
- fods-context-pack.json

Determinism run outputs:
- det1/{zst,netpbm,dif,fods}-context-pack.json
- det2/{zst,netpbm,dif,fods}-context-pack.json

## Anti-Bypass Contract

All context packs include:
- manifest.sha256: present and non-empty
- format_id: present
- context_pack_id: deterministic from manifest SHA prefix
- included_sources: at least 1 entry per pack
- No capability_claims: only spec-derived requirements

## R2 vs R1 Improvement

| Metric | R1 | R2 |
|--------|----|----|
| Sources real vs fixture | 0/4 real | 3/4 real |
| FODS context pack | DEFERRED | COMPLETE |
| Total context packs | 3 (ZST/Netpbm/DIF) | 4 (all formats) |
| Total requirements | 46 | 86 |
| ZST source type | Fixture (~100 words) | Real RFC 8878 (112KB) |
