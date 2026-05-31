# R79 Parallel Execution Map

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30

## Execution Phases

### Phase 0 — Planning (Wave 0)
All trains blocked until complete:
- 00-preflight.md ✓
- r78-independent-verification.md ✓
- multi-mega-train-scoreboard.md ✓
- lane-ownership.md ✓
- risk-register.md ✓
- parallel-execution-map.md (this file) ✓
- r78-defect-ledger.md ← next
- r78-defect-ledger.json ← next
- package-source-sync-investigation.md ← next

### Phase 1 — Root Cause Analysis (Train A)
Confirm all 17 D78 defects. Must complete before Phase 2.
- Train A: R78 IV Confirmation → COMPLETE

### Phase 2 — Core Engineering (Trains B, H, I, N — parallel)

```
Train B: Package Pipeline Repair          Train H: ZST Dep Truth
  - Fix PACKAGE_VERSION (fods + fodt)       - Classify ZST dep status
  - Fix FODT structural gap                 - Write zst-dependency-replay-truth.md
  - Add sdist dist*/ excludes
  - Rebuild all 10 packages               Train I: .NET Test Projects
                                            - Create tests/net/fods/FodsTests.csproj
Train N: Metadata Cleanup                   - Create tests/net/fodt/FodtTests.csproj
  - Fix stale wording in R78 IV             - Write dotnet-test-project-creation.md
  - Fix stale R77 names
  - Fix stale placeholder scan
```

### Phase 3 — Validation Builds (Trains C, D, F, G, M, O — parallel after B completes)

```
Train C: Validator Hardening           Train D: FODS Installed-Wheel Workflow
  - test_r79_installed_api.py            - Fresh venv outside repo
  - test_r79_fods_smoke.py               - Install rebuilt wheel
                                         - Run full workflow test
Train F: FODT Package Source Sync
  - Write fodt-package-source-sync.md  Train G: FODT Structural Repair
                                         - Verify GAP fix works
Train M: Next Format Workahead           - Write fodt-structural-model-repair.md
  - Write next-format-workahead.md
                                       Train O: AI Gap Extraction
                                         - Write ai-gap-extraction.md
```

### Phase 4 — Documentation + Truth (Trains E, J, K, L — parallel after D completes)

```
Train E: FODS Product Completion Truth     Train J: Package README + Metadata
  - Write fods-product-completion-truth.md   - Write package-readme-metadata-baseline.md

Train K: Installed Package Examples        Train L: Package Track Truth
  - Write installed-package-examples.md      - Write probe-package-track-truth.md
```

### Phase 5 — Final Validation (Train P)
Adversarial IV + final replay. Requires E, F, G, H, I complete.

### Phase 6 — Closure (Train Q)
State sync + memory update. Requires P complete.

### Phase 7 — Evidence Bundle Sequence (sequential)
1. Full test suite run (authoritative)
2. Commit all R79 work
3. Pass 1 bundle build
4. Update final-verdict.md with Pass 1 SHA
5. Commit Pass 1 SHA
6. Pass 2 bundle build + sidecar
7. Delivery package build
8. Supervisor review package build
9. Print EVIDENCE_BUNDLE path

## Parallelism Summary

- Phase 2: 4 trains parallel (B, H, I, N)
- Phase 3: 6 trains parallel (C, D, F, G, M, O) — after B gates
- Phase 4: 4 trains parallel (E, J, K, L)
- Total parallel gain: ~6× vs sequential
