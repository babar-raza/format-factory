# R59 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Date:** 2026-05-24

## Core Policy

1. Any train that finishes early MUST look for adjacent work.
2. Blockers in one train do not stop other trains.
3. No train waits for human review within the sprint (DEC-034 applies to gate approvals, not sprint execution).
4. No final COMPLETE verdict until all trains are COMPLETE.
5. Final bundle is built only after all trains complete and validator passes.

## Anti-Shrink Rules

- Train B must fix the validator before Train M builds the bundle.
- Train E must produce both wheels AND sdists before PYTHON_RC claim.
- Train F must have .nupkg in manifest before DOTNET_RC claim.
- Train D must normalize packaging tests before PACKAGE_REPLAY claim.

## Adjacent Work Expansion

- Train G (deepening) may expand into new format tracks if done early.
- Train H may advance any of CSV/TSV/PGM/PBM/DIF/SYLK/PPM/QOI.
- Train I may expand Phase Audit 10 scope.
- Train J may audit more spec-cache entries than minimum required.
