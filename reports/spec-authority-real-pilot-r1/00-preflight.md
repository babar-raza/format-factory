# Preflight — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Date: 2026-06-05

---

## Runtime Environment

- PYTHON: `.local/venv/Scripts/python` (Python 3.13.2) — RESOLVED
- REPO_ROOT: `C:/Users/prora/OneDrive/Documents/GitHub/format-factory`
- Git HEAD: `3a86a05295cb4b82ed40a3408b0612a90f93643c`
- Platform: win32 (Windows 11 Pro)

## Governance Reads

| File | Status | Key Finding |
|------|--------|-------------|
| CLAUDE.md | PRESENT | No push/commit/gate approval without explicit human auth |
| AGENTS.md | ABSENT | Not found in repo root; sprint proceeds without it |
| GOVERNANCE.md | ABSENT | Not found; checked docs/governance/ |
| plans/master-plan.md | PRESENT | R93 complete; spec authority healing done |
| reports/supervisor/session-resume.md | PRESENT | Autonomous Continue: False (prompt quality gate, non-blocking) |
| reports/supervisor/next-sprint.md | PRESENT | Mainstream spec authority pilot recommended |
| .supervisor/policies.yaml | PRESENT | Autonomous continuation max_iterations: 12 |
| .supervisor/project-memory.md | PRESENT | SAL healing sprint complete, MWP ready |
| registry/format-registry.yaml | READ-ONLY | ZST, Netpbm, DIF, FODS/FODT present |
| product-capability-matrix/poc-targets.yaml | READ-ONLY | ZST/Netpbm/DIF/FODS/FODT in matrix |
| docs/governance/** | CHECKED | Spec Authority governance docs present |
| tools/specification-authority-layer/** | PRESENT | 12 modules — all subsystems implemented |
| tests/specification-authority-layer/ | PRESENT | test_spec_authority_mwp.py — 28 tests |
| reports/specification-authority-layer-production-healing/** | READ | Complete healing sprint artifacts present |
| .local/spec-source-registry/ | NOT FOUND | No prior registry — pilot will create pilot-local registry |
| .local/spec-vault/ | NOT FOUND | No prior vault — pilot will create pilot-local vault |

## Dirty State Classification

All dirty files are from prior R93 sprint (pre-existing uncommitted changes). This sprint makes no product source edits.

- `src/net/fods/FodsDocument.cs` → PRE_EXISTING_DIRTY_STATE (R93)
- `src/net/fodt/FodtDocument.cs` → PRE_EXISTING_DIRTY_STATE (R93)
- `src/net/netpbm/Model/NetpbmImage.cs` → PRE_EXISTING_DIRTY_STATE (R93)
- `src/python/sylk/sylk_parser.py` → PRE_EXISTING_DIRTY_STATE (R93)
- All untracked test/example files → PRE_EXISTING_DIRTY_STATE (prior sprints)

Overall: ALLOWED_DIRTY_STATE

## SAL Implementation Discovery

**Primary path:** `tools/specification-authority-layer/`

All 12 expected subsystem modules found:
1. `spec_source_registry.py` → SpecSourceRegistry
2. `spec_vault_ingest.py` → SpecVault
3. `spec_parser.py` → SpecParser
4. `spec_normalizer.py` → SpecNormalizer
5. `spec_indexer.py` → SpecIndexer
6. `spec_digestor.py` → SpecDigestor
7. `requirement_extractor.py` → RequirementExtractor
8. `spec_verifier.py` → SpecVerifier
9. `requirement_graph.py` → RequirementGraph
10. `context_pack_builder.py` → ContextPackBuilder
11. `spec_governance_runtime.py` → SpecGovernanceRuntime
12. `__init__.py` → package init

**Test path:** `tests/specification-authority-layer/test_spec_authority_mwp.py` — 28 tests, all pass

## Evidence Root Labels

- PILOT_REGISTRY_DIR: `.local/evidences/spec-authority-real-pilot-r1/spec-source-registry/`
- PILOT_VAULT_DIR: `.local/evidences/spec-authority-real-pilot-r1/spec-vault/`
- PILOT_ARTIFACT_DIR: `.local/evidences/spec-authority-real-pilot-r1/artifacts/`
- PILOT_CP_DIR: `.local/evidences/spec-authority-real-pilot-r1/context-packs/`
- PILOT_LEDGER_PATH: `.local/evidences/spec-authority-real-pilot-r1/spec-usage-ledger/ledger.jsonl`
- REPORT_DIR: `reports/spec-authority-real-pilot-r1/`
- EVIDENCE_ROOT: `.local/evidences/spec-authority-real-pilot-r1/`
- REVIEW_ROOT: `.local/supervisor/reviews/spec-authority-real-pilot-r1/`

## Hard Prohibitions — Confirmed Active

- No git push
- No git commit
- No src/net/** edits
- No src/python/** edits
- No tests/net/** edits
- No tests/python/** edits
- No poc-targets.yaml mutation
- No registry/format-registry.yaml mutation (proposed patches only)
- No Gate 8 or Gate 11 approval
- No commercial_product_ready=true
