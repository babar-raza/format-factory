# Machinery Claim Verification Matrix
**Mission:** MACHINERY-TRUTH-PRODUCT-CONTRACT-20260624
**Generated:** 2026-06-24

---

## Verification Classifications

- `IMPLEMENTED_AND_CONSUMED` — exists, tested, wired into running pipeline
- `IMPLEMENTED_NOT_CONSUMED` — exists but not called by production pipeline
- `PARTIALLY_IMPLEMENTED` — code exists but missing wiring, tests, or consumers
- `ADVISORY_ONLY` — prompt text or documentation only, no enforcement code
- `TEST_FIXTURE_ONLY` — only exists in test infrastructure
- `STALE` — code/documentation reflects a prior state superseded by current reality
- `BYPASSED` — claimed to be active but evidence shows it is skipped/overridden
- `CONTRADICTED` — claim is factually wrong against current HEAD
- `MISSING` — referenced but does not exist

---

## Core Pipeline Claims

| Claim | Classification | Proof Level | Evidence |
|-------|---------------|-------------|----------|
| SAL extracts spec facts for all formats | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | sal-facts-latest.json: 14,309 facts, 23 formats, generated 2026-06-21 |
| Capability layer generates gap-ledger | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | gap-ledger.json: 1,003 gaps, 969 closed; generated 2026-06-24 |
| Capability-to-feature compiler exists and is wired | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | autonomous_cycle.py line 1481 imports compile_gaps; Step 3a-pre injects gap_ledger_ref |
| Gap-ledger feeds work item generation | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | gap_ledger_to_work_items.py + generate_next_work_items.py both consume gap-ledger |
| 50 governance validators enforce policy | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | 50 validate_* in governance_validators.py; V67 in governance_validators_signal.py; runner registers all |
| Source structure LOC caps enforced | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | source_structure_validator.py checks LOC + function counts against baseline.json; blocks sprint on worsening |
| Product deepening gate blocks 17/20 formats | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | product-deepening-ledger.yaml: continuation_allowed=False for 17 formats; enforced in autonomous_cycle.py |
| Spec-parity QName registry exists | PARTIALLY_IMPLEMENTED | PROOF_LEVEL_2 | 21 YAML files exist; only 3/20 at 'verified'; no automated advancement |
| QName compliance advances automatically | MISSING | PROOF_LEVEL_0 | No automated pipeline from SAL facts → QName advancement; requires manual skill execution |
| Overclaim detector (10 patterns) is called | PARTIALLY_IMPLEMENTED | PROOF_LEVEL_2 | TC-GUARD-001 and TC-GUARD-002 enforce gap_ledger_ref and purpose checks; full 10-pattern detector claim needs verification |
| Durable failure learning (failure-memory.json) | MISSING | PROOF_LEVEL_0 | No failure-memory.json found; MEMORY.md is prose (200-line limit); corrections don't auto-propagate |
| Lane ownership enforced by code | ADVISORY_ONLY | PROOF_LEVEL_1 | SUP-GAP-001 from correction plan: no code enforcement; prompt text only |
| DAG ordering enforced by code | ADVISORY_ONLY | PROOF_LEVEL_1 | SUP-GAP-002 from correction plan: no code enforcement; prompt text only |

---

## Documentation Claims

| Claim | Classification | Proof Level | Evidence |
|-------|---------------|-------------|----------|
| docs/architecture.md reflects current system | STALE | N/A | Last reviewed 2026-05-04; describes Phase 0 (11 validators, src/dotnet/, basic folder tree) — system is now Phase 4+ with 50+ validators, src/net/, 172 supervisor scripts |
| spec-to-feature-radical-correction-plan.md systemic failure #1: SAL ghost infrastructure | CONTRADICTED | PROOF_LEVEL_5 | SAL has 14,309 facts, 22 tools, runs from autonomous_cycle.py |
| spec-to-feature-radical-correction-plan.md failure #3: no capability-to-feature compiler | CONTRADICTED | PROOF_LEVEL_3 | tools/capability_layer/capability_to_feature_compiler.py exists and is imported |
| spec-to-feature-radical-correction-plan.md failure #2: capability layer output unconsumed | SUPERSEDED | PROOF_LEVEL_3 | autonomous_cycle.py Step 3a-pre consumes gap_ledger and injects refs |
| spec-to-feature-radical-correction-plan.md failure #6: zero durable learning | CURRENT | PROOF_LEVEL_0 | Still true: no failure-memory.json, no auto-propagation |
| master-plan.md has current open work section | STALE | N/A | Last section (49) is CLOSED; no new section opened; check next-sprint.md for current work |
| Gate 11 approved for FODS, FODT | PARTIALLY_IMPLEMENTED | PROOF_LEVEL_4 | G11-G sub-gate approved by Babar Raza 2026-06-05; full Gate 11 (commercial release) still requires final sign-off |

---

## Product Claims

| Format | Claim | Classification | Proof Level | Note |
|--------|-------|---------------|-------------|------|
| FODS | Python POC complete (load→inspect→edit→save→reload→export) | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml all ops PASS; installed_workflow PASS |
| FODS | .NET dotnet_tests=618, all ops PASS | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml dotnet_status all PASS |
| FODT | Python POC complete | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml all ops PASS; installed_workflow PASS |
| FODT | .NET all ops PASS | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml dotnet_status all PASS |
| Netpbm | .NET POC ops PASS | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | poc-targets.yaml PASS entries; dogfood status not listed |
| ZST | Python compress/decompress/probe PASS | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml PASS; continuation_allowed=False (qname not verified) |
| ABW | Python POC complete, 34 test files, installed | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | continuation_allowed=True; poc-targets.yaml PASS |
| Gnumeric | Python POC complete, 30 test files, installed | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml PASS |
| FODS Compat/ facades (FodsCell/Sheet/Document) | PARTIALLY_IMPLEMENTED | PROOF_LEVEL_1 | Architecture markers only; inherit from empty spec classes; no behavior; real FODS ops in models.py |
| xcf_layer_name_list | PARTIALLY_IMPLEMENTED | PROOF_LEVEL_2 | Returns synthetic "Layer N" names, NOT real XCF layer names; GAP-XCF-LAYER-NAMES logged |
| SYLK 893 tests pass | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | After 33 analytics stub test files deleted; 893 core tests pass |
| TOML exception hierarchy (TomlInputError) | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_3 | exceptions.py fixed in prior sprint; 149 TOML tests pass |

---

## Package / Distribution Claims

| Claim | Classification | Proof Level | Evidence |
|-------|---------------|-------------|----------|
| All 20 Python formats installable | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | 20 egg-info directories in src/python/; pip install -e confirmed for FODG, NDJSON, TSV |
| .NET packages buildable | IMPLEMENTED_NOT_CONSUMED | PROOF_LEVEL_3 | .csproj files exist; NuGet publication not executed (TRUE_EXTERNAL_GATE) |
| Dogfood export path (FODS→CSV via FF-CSV) | IMPLEMENTED_AND_CONSUMED | PROOF_LEVEL_4 | poc-targets.yaml dogfood_status IMPLEMENTED for FODS, FODT, ABW, Gnumeric, TSV |
