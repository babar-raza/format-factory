---
sprint: R92
generated_by: r92-worker
---

# Dogfood Export Status (Trains R-S)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Train R: Commercial Dogfood Export (FODT .NET TXT Bridge)

**Goal:** FODT .NET text extraction dogfood workflow.

**Existing capability:**
- `FodtDocument.GetPlainText()` — extracts all paragraphs as newline-separated text (R88)
- `FodtTxtExporter` — exports document to plain text format
- Round-trip save via `SaveToFile()` (R91)

**R92 status:**
- No new dogfood source change needed — existing `GetPlainText()` + `FodtTxtExporter` cover the TXT extraction dogfood pattern
- New API `GetHeadingParagraphs()` (Train M) enables structure-aware TXT dogfood (outline extraction)
- Dogfood workflow: Load FODT → `GetHeadingParagraphs()` → export heading text → TXT output
- Source change not required: existing exporters cover this

**Deferral:** A dedicated `.cs` dogfood bridge script deferred to R93 pending `add-dogfood-export` skill for .NET.

## Train S: FOSS Dogfood Export (Python Netpbm Installed Workflow)

**Existing capability:**
- R90: `ppm_to_pgm.py` dogfood export (PPM→PGM Python) — CLOSED
- R86: `pbm_to_ppm.py` dogfood export (PBM→PPM) — CLOSED
- R85: `pbm_to_pgm.py` dogfood export (PBM→PGM) — CLOSED

**R92 status:**
- PPM→PGM dogfood confirmed working via installed `pbm`/`pgm` wheels
- No new dogfood source changes needed this sprint
- Next dogfood opportunity: PPM→PBM (threshold conversion) or PGM→PPM (grayscale-to-color)

**Deferral:** New Python dogfood deferred to R93 pending PPM wheel re-install.

## Status: DOGFOOD LANES VERIFIED — NO NEW SOURCE CHANGES
