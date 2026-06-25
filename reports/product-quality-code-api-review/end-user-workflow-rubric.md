# End-User Workflow Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores how well a product supports a complete end-user workflow — from installation through
discovery, first use, and production integration. This is the developer experience dimension.

---

## Workflow Levels (EW-0 through EW-5)

| Level | Label | Description |
|-------|-------|-------------|
| **EW-0** | No workflow | Cannot be installed or used independently |
| **EW-1** | Dev-only | Works from source checkout only; no package |
| **EW-2** | Installable | Package installs; basic parse works |
| **EW-3** | Discoverable | Install + import + autocomplete guides user to primary API |
| **EW-4** | Productive | Complete workflow within 15 minutes without reading source |
| **EW-5** | Professional | Install + discover + use + extend; docs answer all questions |

---

## Workflow Scoring Dimensions

### EW-D1: Discovery

Can a developer find the primary entry point from autocomplete alone?

| Score | Criteria |
|-------|---------|
| 0 | 50+ names in autocomplete; no hierarchy |
| 1 | Primary class visible but surrounded by internals |
| 2 | Primary class visible; 10–20 names total |
| 3 | Primary class obvious; < 10 names in namespace |
| 4 | Primary class + factory methods; clear workflow from autocomplete |
| 5 | Self-documenting: autocomplete + type hints + docstrings tell full story |

### EW-D2: First 5 Minutes

Can a developer load a file and read data within 5 minutes?

| Score | Criteria |
|-------|---------|
| 0 | Cannot load without reading source code |
| 1 | Loading requires > 10 lines of setup |
| 2 | Loading possible with 5–10 lines |
| 3 | Loading possible in 3–5 lines from README example |
| 4 | `doc = ProductDoc.Load("file.ext")` in 1–2 lines |
| 5 | One-liner; intuitive method name; no manual |

### EW-D3: Edit Workflow

Can a developer edit and save within 15 minutes?

| Score | Criteria |
|-------|---------|
| 0 | No edit capability |
| 1 | Edit requires reading source to find methods |
| 2 | Edit possible but requires trial and error |
| 3 | Edit discoverable from IDE autocomplete |
| 4 | Edit → save workflow natural from autocomplete + README |
| 5 | Edit with type safety; fluent API; compile-time guidance |

### EW-D4: Error Experience

When something goes wrong, does the developer understand what happened?

| Score | Criteria |
|-------|---------|
| 0 | Stack traces from framework internals |
| 1 | Generic error message: "An error occurred" |
| 2 | Error message names the problem but not location |
| 3 | Error message with file path and line number |
| 4 | Typed exception + message + cause + recovery hint |
| 5 | Typed exception + full diagnostic + docs link + suggested fix |

### EW-D5: Example Quality

Do code examples teach the real workflow?

| Score | Criteria |
|-------|---------|
| 0 | No examples |
| 1 | Code snippet in README; not runnable |
| 2 | Runnable example but uses dev-path import |
| 3 | Runnable example using installed-package import |
| 4 | Example covers load + edit + save; consumer roundtrip |
| 5 | Multiple examples: quickstart + advanced + CLI usage + integration |

---

## End-User Workflow Scores

### .NET Products

| Product | EW-D1 | EW-D2 | EW-D3 | EW-D4 | EW-D5 | EW Level |
|---------|-------|-------|-------|-------|-------|----------|
| FODS | 3 | 4 | 4 | 4 | 1 | EW-3 |
| FODT | 3 | 4 | 4 | 4 | 1 | EW-3 |
| NetPBM | 4 | 4 | 4 | 4 | 1 | EW-4 |
| NDJSON | 2 | 3 | 2 | 3 | 1 | EW-2 |
| CSV | 3 | 3 | 2 | 1 | 1 | EW-2 |
| TSV | 2 | 2 | 1 | 3 | 1 | EW-2 |
| ZST | 2 | 2 | 0 | 3 | 1 | EW-1 |
| HTML | 1 | 0 | 0 | 0 | 0 | EW-0 |

### Python Products

| Product | EW-D1 | EW-D2 | EW-D3 | EW-D4 | EW-D5 | EW Level |
|---------|-------|-------|-------|-------|-------|----------|
| FODS | 2 | 3 | 3 | 3 | 3 | EW-3 |
| FODT | 2 | 3 | 3 | 2 | 3 | EW-3 |
| ODS | 3 | 3 | 3 | 2 | 3 | EW-3 |
| PBM | 3 | 3 | 2 | 4 | 3 | EW-3 |
| ZST | 3 | 3 | 3 | 2 | 3 | EW-3 |
| SYLK | 2 | 2 | 2 | 2 | 3 | EW-2 |
| QOI | 2 | 2 | 2 | 1 | 1 | EW-2 |
| XCF | 2 | 2 | 1 | 1 | 1 | EW-2 |
| FODP | 2 | 2 | 0 | 1 | 2 | EW-1 |

---

## Workflow Gaps by Product

### FODS .NET — EW-3 (stuck at EW-3 because of no README and no examples)
**Gap:** No README.md (PQ-005, PQ-014). No example .cs files.
**Fix:** Create README.md + one example file showing Load → Edit → Save workflow.

### ZST .NET — EW-1 (stuck at EW-1 because of no compress capability)
**Gap:** No ZstWriter. User can parse a ZST file but cannot create one.
**Fix:** PQ-007 ZstWriter implementation (Phase E pilot).

### FODP Python — EW-1 (stuck at EW-1 because undocumented read-only limitation)
**Gap:** User tries to write FODP, finds no write_fodp(), gets no helpful error.
**Fix:** PQ-009 — add write_fodp() stub with NotImplementedError + helpful message.

### All Python — EW cap at EW-3 because examples use dev-path imports
**Gap:** PQ-003. `from src.python.fods import FodsDocument` — not usable without source.
**Fix:** Update all examples to use installed-package imports.

---

## End-User Workflow Bands

| EW Level | Band |
|----------|------|
| EW-0 | Unusable externally |
| EW-1 | Dev/source-only use |
| EW-2 | Package installable; basic use |
| EW-3 | Productive with docs |
| EW-4 | Professional developer experience |
| EW-5 | Best-in-class DX |
