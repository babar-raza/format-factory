# Phase Audit 2 — Sample Acquisition and Sample Provenance

**Sprint:** FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
**Date:** 2026-05-22
**Phase:** 2 of 7
**Status:** COMPLETE

---

## Scope

For each format with committed test samples, verify:
1. Sample provenance file (`_provenance.yaml`) exists
2. Source type is clearly classified: `project-owned-synthetic`, `upstream-project-fixture`, `public-domain-reference`
3. License/redistribution status is documented
4. SHA-256 hashes are recorded for each sample
5. Test traceability: which tests use each sample
6. Generator recipe is deterministic (for synthetic samples)
7. No unlicensed upstream samples committed without attribution

---

## Format-by-Format Audit

### FODS — Flat OpenDocument Spreadsheet

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | **ABSENT** | GAP |
| Sample files | 4 (formula-basic, minimal-spreadsheet, multi-sheet-basic, typed-values-basic) | OK |
| Sample type | Project-authored XML (confirmed by file header: `<!-- minimal-spreadsheet.fods / format-factory`)  | INFERRED |
| License | Project-owned (inferred) | NOT_DOCUMENTED |
| Added | commit 8871777 (run026) | TRACEABLE |
| SHA-256 recorded | No | GAP |

**Finding:** PARTIAL — FODS samples appear to be project-authored XML but have no `_provenance.yaml`.
**Action:** Create `samples/by-format/fods/_provenance.yaml` in R48.
**Sample hashes (recorded here for traceability):**
- formula-basic.fods: `72b065415748db3e3c7796608f50b488db6d23b2439d2468baf88ea41b38db1e` (1973 bytes)
- minimal-spreadsheet.fods: `a790b18a811c47d634603ad0dd3e42c41c102a36c74b6349b46b9770a2825543` (1421 bytes)
- multi-sheet-basic.fods: `669b60befc7206a08578815e781ff72526c98d07be53f20e37f062b73b7dcc41` (2008 bytes)
- typed-values-basic.fods: `c873322d69fa93ff64519a37a5f87f4efc9cd244a18488f03adc342524e51977` (2435 bytes)

---

### FODT — Flat OpenDocument Text

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | **ABSENT** | GAP |
| Sample files | 4 (headings-and-paragraphs, list-basic, minimal-document, table-basic) | OK |
| Sample type | Project-authored XML (confirmed by file structure) | INFERRED |
| License | Project-owned (inferred) | NOT_DOCUMENTED |
| Added | commit bc92729 (run043) | TRACEABLE |
| SHA-256 recorded | No | GAP |

**Finding:** PARTIAL — FODT samples appear project-authored but no `_provenance.yaml`.
**Action:** Create `samples/by-format/fodt/_provenance.yaml` in R48.
**Sample hashes:**
- headings-and-paragraphs.fodt: `c3c1463327360ca265af8ab0d09e46c5e68104060603ce64393c816b78fd3a39` (2063 bytes)
- list-basic.fodt: `5a32987e2b7aec4bb10c1328a6954007cc533a3e215ab9f4b4f35e99207698a4` (2492 bytes)
- minimal-document.fodt: `ed118bbaacea1779a3ce381ad1d0288e243f16a06bb233fa3e9723cd6afce738` (1030 bytes)
- table-basic.fodt: `0996d75e18cda81af9fcec568d03c8ccc8a90bb39fba3b60bedd3300345a6049` (2848 bytes)

---

### ZST — Zstandard

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Provenance version | 1.0, dated 2026-05-15 | OK |
| Source type | `upstream-project-fixture` (facebook/zstd, BSD-3-Clause) | OK |
| License | BSD-3-Clause (Meta Platforms) | DOCUMENTED |
| Attribution | Present | OK |
| SHA-256 per sample | Recorded (source_blob_sha + download hash) | OK |
| Generator recipe | N/A (upstream files, source_commit recorded) | OK |

**Finding:** **PASS** — ZST sample provenance is complete, honest, and reproducible.

---

### ODS — OpenDocument Spreadsheet (ZIP-based)

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Provenance version | 1.0, dated 2026-05-18 | OK |
| Source type | `project-owned-synthetic` | OK |
| License | project-owned-synthetic | OK |
| Generation tool | Python 3.13 stdlib (zipfile, io) | OK |
| SHA-256 per sample | Recorded | OK |
| Deterministic | Yes (same Python version + stdlib) | OK |

**Finding:** **PASS** — ODS sample provenance complete.

---

### ODT — OpenDocument Text (ZIP-based)

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Source type | `project-owned-synthetic` | OK |
| Generation tool | Python 3.13 stdlib | OK |
| SHA-256 per sample | Recorded | OK |

**Finding:** **PASS** — ODT sample provenance complete.

---

### QOI — Quite OK Image Format

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Source type | `project-owned-synthetic` | OK |
| License | project-owned-synthetic (QOI spec: MIT) | OK |
| Generation tool | Python 3.13 stdlib (struct + bytes) | OK |
| SHA-256 per sample | Recorded | OK |

**Finding:** **PASS** — QOI sample provenance complete.

---

### XCF — GIMP Native Format

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Source type | `project-owned-synthetic` | OK |
| SHA-256 per sample | Recorded | OK |

**Finding:** **PASS** — XCF sample provenance complete.

---

### DIF — Data Interchange Format

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Source type | `project-owned-synthetic` | OK |
| SHA-256 per sample | Recorded | OK |

**Finding:** **PASS** — DIF sample provenance complete.

---

### PPM / PGM / PBM — Netpbm Image Formats

| Format | `_provenance.yaml` | Source Type | SHA-256 | Status |
|--------|-------------------|-------------|---------|--------|
| PPM | PRESENT | project-owned-synthetic | Recorded | **PASS** |
| PGM | PRESENT | project-owned-synthetic | Recorded | **PASS** |
| PBM | PRESENT | project-owned-synthetic | Recorded | **PASS** |

**Finding:** **PASS** — Netpbm formats all have complete provenance.

---

### SYLK — Symbolic Link

| Item | Value | Status |
|------|-------|--------|
| `_provenance.yaml` | PRESENT | OK |
| Source type | `project-owned-synthetic` | OK |
| SHA-256 per sample | Recorded | OK |

**Finding:** **PASS** — SYLK sample provenance complete.

---

## Summary Matrix

| Format | `_provenance.yaml` | Source Type | License | SHA-256 | Status |
|--------|-------------------|-------------|---------|---------|--------|
| FODS | ABSENT | Inferred project-authored | Not documented | Not recorded | **PARTIAL** |
| FODT | ABSENT | Inferred project-authored | Not documented | Not recorded | **PARTIAL** |
| ZST | PRESENT | upstream-project-fixture (BSD-3) | DOCUMENTED | RECORDED | **PASS** |
| ODS | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| ODT | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| QOI | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| XCF | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| DIF | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| PPM | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| PGM | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| PBM | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |
| SYLK | PRESENT | project-owned-synthetic | project-owned | RECORDED | **PASS** |

**PASS: 10 formats | PARTIAL: 2 formats (FODS, FODT)**

---

## Gaps and Actions

| Format | Gap | Action | Sprint |
|--------|-----|--------|--------|
| FODS | No `_provenance.yaml` | Create with `project-authored-xml` source type + SHA-256 | R48 |
| FODT | No `_provenance.yaml` | Create with `project-authored-xml` source type + SHA-256 | R48 |

**Note:** FODS and FODT sample hashes are recorded in this document (above) as
interim provenance evidence until formal `_provenance.yaml` files are created.

---

## Phase Audit 2 Result

**PHASE_AUDIT_2: MAJORITY_PASS_CORE_FORMATS_PARTIAL**

10 of 12 formats have complete, documented sample provenance. The 2 PARTIAL formats
(FODS, FODT) are the core product formats — their samples are inferred project-authored
XML from git history but lack formal `_provenance.yaml` files. Hashes are recorded
in this document as interim provenance.

No unlicensed upstream samples were found. No redistribution-restricted samples
are committed.
