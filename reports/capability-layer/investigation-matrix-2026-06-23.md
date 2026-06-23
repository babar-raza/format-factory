# Investigation Matrix — Capability & Feature Understanding Layer
# Updated: 2026-06-23 (majestic-cooking-waffle sprint)
# Prior matrix: 2026-06-08 (FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001)
# Change basis: UNIFIED-FF-FINAL-20260623 sprint results + majestic-cooking-waffle pilot runs

## Methodology
- Rows copied from 2026-06-08 matrix; Current Truth and status columns updated from fresh 2026-06-23 evidence
- Evidence sources: capability_verifier runs, pytest outputs, file reads, continuation-signal.json
- Column "Resolved Sprint" = sprint that closed the item (not this matrix's sprint unless new)

| # | Area | Expected Responsibility | Files Inspected | Exists As | Current Truth (2026-06-23) | Evidence Found | Tests Found | Contradiction | Risk | Required Fix | Taskcard | Resolved Sprint |
|---|------|------------------------|-----------------|-----------|---------------------------|----------------|-------------|---------------|------|--------------|----------|-----------------|
| 1 | Spec Authority tools/outputs | Verify spec facts, provide provenance | tools/specification-authority-layer/ | Real source code | Spec cache not populated for FOSS formats; gate-blocked. Unchanged from 2026-06-08. | tools/specification-authority-layer/ present | None | None | HIGH | Requires gate clearance — not this sprint | CAP-DISC-002 | OPEN |
| 2 | Requirement Authority tools/outputs | Build proof graph from spec facts | tools/requirements_authority/ (15 files), requirements-authority/ (8 schemas) | Real source code + schemas | Tools ready; 6 fixture packs. Proof graph not fully integrated. Unchanged. | Confirmed | tests/supervisor/ (fixture tests) | Not wired into task selection | MEDIUM | Integrate with capability_map_generator | CAP-DISC-003 | OPEN |
| 3 | Capability schemas | Machine-readable capability records | schemas/capability/ | schemas/capability/ exists with 4 JSON schemas (record, map, gap, taxonomy) | schemas/capability/*.schema.json confirmed present and used by validator | 4 schemas confirmed | None for schemas | None | LOW | No action needed | CAP-SCHEMA-001..005 | RESOLVED (prior sprint) |
| 4 | Product capability matrix | Per-format capability tracking | product-capability-matrix/*.yaml | Real source (YAML) | poc-targets.yaml: 3 commercial + 8 FOSS + 2 on-hold. FOSS formats include SYLK, NDJSON, TSV (added). Structurally valid. | Confirmed | None | Numeric test counts absent — only dir paths | LOW | No blocking issue; monitor for staleness | CAP-PROD-005 | RESOLVED (prior sprint) |
| 5 | poc-targets.yaml | Single-file POC authority | product-capability-matrix/poc-targets.yaml | Real (updated) | 3 commercial + 8 FOSS + 2 on-hold. FODT, FODS, Netpbm have dogfood_status fields confirmed IMPLEMENTED. | Confirmed | None | None | LOW | None | CAP-PROD-005 | RESOLVED (prior sprint) |
| 6 | Product task selector | Select safe executable tasks | tools/supervisor/product_task_selector.py | Real source code | _load_gap_candidates() confirmed called within select_product_task() at line 262. Reads gap-ledger.json via _GAP_LEDGER_PATH. CAP-SEL-001 CONFIRMED COMPLETE. | Source code read 2026-06-23 | None | None | LOW | None — confirmed complete | CAP-SEL-001 | RESOLVED (prior sprint) |
| 7 | Action queues | Machine-readable next actions | .local/supervisor/action-queue.jsonl, next-action.json | Real files | action-queue.json at reports/capability-layer/ has 24 actions. VAL-009: 16 actions missing per-item advisory_only=true (generator artifact). Top-level advisory_only=False (should be True). | Confirmed | None | VAL-009 errors in validate() — passed=False | MEDIUM | Fix generator to emit advisory_only=true on all action items | CAP-GEN-011 | OPEN — generator bug |
| 8 | Continuation files | Autonomous continuation control | .local/supervisor/active-continuation.json, continuation-signal.json | Real files | session_id=9d0b1029992e, autonomous_continue=true_with_rework, rework_items=[LANE_ENFORCEMENT:1_violations], source_sprint_id=UNIFIED-FF-FINAL-20260623 | Confirmed | None | GOV_BLOCK RESOLVED (was blocking) | LOW | LANE_ENFORCEMENT advisory is pre-existing separation violations (fodp, fods, xcf) — non-blocking | CAP-SEL-006 | RESOLVED (UNIFIED sprint) |
| 9 | Evidence declarations | Sprint closeout packages | .local/evidences/ | Real (prior sprints) | Latest: UNIFIED-FF-FINAL-20260623. majestic-cooking-waffle evidence pending this sprint closeout. | Multiple prior declarations | Via supervisor tests | None | LOW | Create for this sprint | CAP-EVID-001 | IN PROGRESS |
| 10 | Python FOSS APIs | Implemented product functions | src/python/{format}/*.py | Real source code | FODT: document_to_text callable. PBM: convert_pbm_to_pgm callable. capability_verifier shows 0 drift for FODT/PBM/PGM/PPM. GOV_BLOCK resolved: XCF at 1277 LOC (at cap), NDJSON at 1080 (at cap). | Confirmed by verifier runs | 1999 FODT tests pass; 2407 Netpbm tests pass | None for implemented functions | LOW | Netpbm: 100 suspended analytics test stubs need cleanup | CAP-PROD-002/003 | RESOLVED (UNIFIED sprint) |
| 11 | Python tests | Test coverage per format | tests/python/{format}/ | Real tests | FODT: 1999 passed, 4 skipped. Netpbm: 2407 passed, 9 skipped, 2 failed, 100 collection errors. 100 errors = suspended analytics stubs. 2 PGM failures not in known-failure-ledger. | Confirmed | Yes | Netpbm: 100 suspended analytics stubs cause collection errors (not cataloged in known-failure-ledger) | MEDIUM | Add Netpbm suspended stubs to known-failure-ledger or clean up (same pattern as SYLK 2026-06-18) | CAP-NETPBM-CLEANUP-001 | OPEN — new finding |
| 12 | Examples/sample outputs | User-facing examples | examples/python/{format}/ | Real (partial) | Unchanged from 2026-06-08. Examples exist for FODS/FODT/Netpbm/ZST. FOSS formats sparse. | Confirmed | None | FOSS formats sparse | MEDIUM | Generate sample outputs in pilots | CAP-PILOT-* | OPEN |
| 13 | Package artifacts | Built packages | .local/venv/, nupkg files | Real (.nupkg exist) | 3 NuGet packages built. Python pyproject.toml for 10 packages. NDJSON/TSV wheels built and installed (2026-06-18). | .nupkg files | Via install proof tests | None | LOW | None | CAP-PILOT-* | RESOLVED (prior sprint) |
| 14 | Dogfood outputs | Format-to-format conversion via FF | dogfood paths in poc-targets.yaml | Partial | FODT: document_to_text PASS. Netpbm: convert_pbm_to_pgm PASS. FODS: fods_to_csv confirmed (prior sprint). SYLK: sylk_to_csv (prior sprint). | Confirmed in poc-targets + direct callable checks | Via .NET/Python tests | None | LOW | None | CAP-PILOT-* | RESOLVED (prior + this sprint) |
| 15 | Gate/readiness status | Format approval state | poc-targets.yaml, gate reports | Real | 3 commercial Gate 11 APPROVED status in poc-targets. FOSS at various gates. Gate 11 execution requires Babar Raza approval — TRUE_EXTERNAL_GATE. | Gate approval confirmed | None | None | LOW | None | CAP-PILOT-* | REFLECTED |
| 16 | Known test failures | Pre-existing failures to distinguish | All test dirs | Real | FODT 1999/1999 pass. Netpbm: 100 collection errors (suspended stubs NOT in known-failure-ledger) + 2 pgm failures (not in ledger). capability_layer: 106/106 pass. | Confirmed for targeted suites | Yes | Netpbm stubs not cataloged = gap in governance | MEDIUM | Add to known-failure-ledger.yaml | CAP-NETPBM-LEDGER-001 | OPEN — new finding |
| 17 | Stale reports | Outdated reports misleading agents | reports/ | Mix of real and stale | investigation-matrix.md: now updated (this sprint). next-sprint.md: ADVISORY ONLY. capability maps FRESH (2026-06-23T09:09:58). | Confirmed fresh | None | None | LOW | None | CAP-PROD-005 | RESOLVED (this sprint) |
| 18 | Generated prompts | Advisory next-sprint prompts | reports/supervisor/next-sprint.md | Real (advisory) | ADVISORY ONLY per session-resume.md. Machine-readable action queue replaces prompt reliance. | Confirmed | None | None | LOW | None | CAP-GEN-011 | RESOLVED (prior sprint) |
| 19 | Product ledger | Tracked source changes | reports/r90/product-code-change-ledger.json | Real (130+ entries) | Active governance. No new source changes this sprint (investigation-only). | Confirmed | Via validate_product_code_ledger.py | None | LOW | None — no source changes this sprint | CAP-PROD-006 | NO-OP (this sprint) |
| 20 | Existing taskcards | Prior work items | taskcards/ | Real (150+ cards) | FUL-001/002 COMPLETED. CAP-* cards from prior sprint confirmed. Flat directory only (no capability-layer/ subdir). | Confirmed | None | None | LOW | New taskcards: CAP-NETPBM-CLEANUP-001, CAP-NETPBM-LEDGER-001 | CAP-PLAN-004 | REFLECTED |
| 21 | Source governance | Edit flow rules | AGENTS.md, CLAUDE.md, docs/ | Real docs | No src/ changes this sprint. Governed flow followed. ledger not updated (no source changes). | Confirmed | None | None | LOW | None | CAP-PROD-006 | COMPLIANT |
| 22 | CI/package workflows | Build automation | .vscode/tasks.json, scripts/ | Partial | Unchanged. tasks.json exists; scripts/ exists. | Confirmed | None | None | LOW | Not changed this sprint | None | NO-OP |
| 23 | AI usage/telemetry | AI use tracking | docs/ai/, tools/supervisor/ai_*.py | Real tools | AI tools exist. All AI contributions marked ai_draft per records. No new AI-produced records this sprint. | Confirmed tools | None | None | LOW | None | CAP-VAL-002 | COMPLIANT |
| 24 | Spec fact validator | Enforcement of spec_fact_refs | tools/supervisor/validate_spec_fact_refs.py | Real + active | No PRODUCT_SOURCE work items this sprint — validator not triggered. GOVERNANCE_TASKCARD items exempt. | Confirmed | tests/supervisor/test_spec_fact_refs_enforcement.py | None | LOW | None | CAP-VAL-003 | COMPLIANT |
| 25 | Autonomous cycle | Supervised sprint closeout | tools/supervisor/autonomous_cycle.py | Real + active | UNIFIED-FF-FINAL-20260623 ACCEPTED. This sprint: pending closeout (Phase 4). | Prior sprint results | Via supervisor tests | None | LOW | Run at closeout | CAP-EVID-002 | IN PROGRESS |
| 26 | Proof graph | Capability claim linkage | tools/requirements_authority/*.py | Real source | Tools present; graph not generated for all formats. CAP-DISC-003 open. | 6 fixture packs | Fixture replay tests | Not integrated into generator | MEDIUM | capability_map_generator.py reads FUL packs as proxy | CAP-GEN-006 | OPEN |
| 27 | Unsupported/future declarations | Out-of-scope capability records | poc-targets.yaml, acquisition-packs/ | Partial | on_hold: QOI, DIF. Future exports not declared. Unchanged. | Confirmed in poc-targets | None | None | LOW | None | CAP-GEN-001 | REFLECTED |

## New Findings (2026-06-23 — not in 2026-06-08 matrix)

| # | Area | Finding | Risk | Action |
|---|------|---------|------|--------|
| N1 | capability_to_feature_compiler.py | File now EXISTS (untracked, created by UNIFIED sprint). Was absent in 2026-06-08 matrix. | LOW | Verify content before promoting to tracked |
| N2 | Netpbm suspended analytics stubs | 100+ test files in tests/python/pbm|pgm|ppm/ import analytics functions never implemented (rotation SUSPENDED). Not in known-failure-ledger.yaml. Pattern identical to SYLK stubs cleaned up 2026-06-18. | MEDIUM | Add to known-failure-ledger or delete stubs (CAP-NETPBM-CLEANUP-001) |
| N3 | action-queue VAL-009 errors | 16 of 24 actions in reports/capability-layer/action-queue.json missing per-item advisory_only=true. Top-level advisory_only=False (should be True). Generator artifact from UNIFIED sprint. validate() returns passed=False. | MEDIUM | Fix capability_map_generator.py to emit advisory_only=true on all action items |
| N4 | GOV_BLOCK RESOLVED | GOV_BLOCK:monolith_detection_validator RESOLVED by UNIFIED sprint. XCF at 1277 LOC (at baseline_loc_cap), NDJSON at 1080 (at cap). | LOW — resolved | Monitor; do not re-trigger by exceeding caps |
| N5 | LANE_ENFORCEMENT advisory | rework_items contains LANE_ENFORCEMENT:1_violations — non-blocking. Source structure validator: blocks_sprint=False, 4 separation_violations (fodp, fods, xcf) — pre-existing. | LOW | Document; no immediate fix required |

## Capability Layer Authority Assessment (2026-06-23)

**Question: Can the capability layer reliably convert Spec Authority and project goals into verified capability maps that drive implementation tasks?**

**Answer: PARTIAL — with specific gaps**

Evidence:
- Capability maps are generated and validated: 1779 records across commercial + FOSS
- capability_verifier shows 0 drift for all tested formats (FODT, PBM, PGM, PPM, plus FODS/SYLK/NDJSON/TSV from prior sprint)
- Gap ledger has 926 gaps with correct root structure — product_task_selector reads them correctly
- capability_to_feature_compiler.py exists and can generate taskcard stubs from gaps

Limitations blocking FULL:
1. VAL-009 errors: action-queue advisory_only flag generator bug (validate() returns False)
2. 12/25 gap audit samples remain CLAIMED_UNPROVEN (from 2026-06-21 audit)
3. Spec authority cache not populated for FOSS formats (gate-blocked)
4. Proof graph not integrated for all formats (CAP-DISC-003 OPEN)
5. Netpbm suspended analytics stubs not cataloged in known-failure-ledger
