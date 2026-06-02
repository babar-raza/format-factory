---
sprint: R92
generated_by: r92-worker
---

# FOSS Reduced Status (Trains O-Q)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Train O: ZST Reduced/FOSS

- **Package:** `aspose-format-factory-zst 0.1.0.dev0`
- **Import status:** `import zst` — OK (installed in venv)
- **Dependency:** `zstandard 0.25.0` (third-party, ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED)
- **Test coverage:** Existing ZST tests pass as part of Python suite
- **Action this sprint:** No source changes — ZST dependency classification unchanged from R90

## Train P: Python Netpbm Reduced/FOSS

- **Installed packages:**
  - `aspose-format-factory-pbm 0.1.0.dev0` — `import pbm` (OK)
  - `aspose-format-factory-pgm 0.1.0.dev0` — `import pgm` (OK)
  - PPM not yet installed in venv (wheel exists at src/python/ppm/)
- **Test coverage:** PBM/PGM/PPM/Netpbm tests pass as part of Python suite
- **R90 dogfood:** `ppm_to_pgm.py` dogfood export (PPM→PGM) — ledger entry R90-GOVERNED-PYTHON-NETPBM-PPM-TO-PGM-001
- **Action this sprint:** No new source changes — PPM wheel build deferred to next sprint

## Train Q: SYLK/DIF Reduced/FOSS

- **SYLK:** Existing tests cover `sylk_to_csv` (R84). Tests pass.
- **DIF:** Existing tests cover `dif_to_csv` (R84). Tests pass.
- **Action this sprint:** No source changes — verification only

## Python Test Baseline (R92)

- Suite: `tests/python/` — 2467 passed, 11 skipped (CSV shadow isolation)
- Full suite including supervisor/evidence: 2570 passed, 11 skipped

## Status: FOSS REDUCED VERIFIED — NO NEW CHANGES REQUIRED
