# Format Factory: Complete Repository Audit, Direction Assessment, and Healing Plan

**Plan type:** `machinery_hardening`
**Mission ID:** `PORTFOLIO-RECON-HEAL-20260627`
**Created:** 2026-06-27
**Status:** PLANNING

---

## Context

Format Factory has grown to ~360K LOC across 24 Python formats, 10 .NET formats, 4,334 test files, and 95 supervisor scripts (69.7K LOC). The user requires a **complete, forensic audit** covering:

1. Project direction assessment
2. Source professionalism per format
3. Real feature coverage per format
4. Gap-ledger reconciliation against source truth
5. Test architecture assessment
6. Machinery readiness
7. Authoritative healing plan with micro-taskcards

**Why now:** The project has accumulated significant infrastructure and product code. Claims of completion, gate readiness, and test coverage need revalidation against source truth — not existing reports.

**Key findings from exploration:**
- **Machinery-to-product LOC ratio is ~2.3:1** (147K tools vs 64K product)
- **1,277 gaps tracked** (1,245 closed, 32 open) — closure accuracy unverified
- **4,334 test files** but organization is sprint-numbered (R100-R355), not behavior-categorized
- **Analytics separation incomplete:** Only 4/20 Python formats have dedicated `_analytics.py` files
- **Known LOC violations:** 24 entries in source-structure-baseline.json, some with stale data
- **65/66 QName entries** (99.4%), 1 intentional gap
- **93 active capabilities**, 28 missing from command-registry

---

## Phase 1: Repository Baseline Capture (READ-ONLY)

### TC-BASE-001: Bind Repository State
- Capture git HEAD, branch, worktree status
- Record all source roots, registries, state files
- Snapshot current counts for idempotent comparison
- **Output:** `reports/portfolio-recon-20260627/baseline.yaml`

### TC-BASE-002: Complete Source File Inventory
For every `.py` under `src/python/` and every `.cs` under `src/net/`:
- Record: path, LOC, function count, layer classification (Spec/Domain/Parser/Writer/Analytics/Export/Compat/API)
- Cross-reference against `registry/source-structure-baseline.json`
- Flag files >800 LOC not in known_violations
- **Key paths:**
  - `src/python/` (24 format dirs, ~192 .py files excl build)
  - `src/net/` (10 format dirs, ~46 .cs files excl obj/bin)
  - `registry/source-structure-baseline.json`
- **Output:** `reports/portfolio-recon-20260627/source-inventory.yaml`

### TC-BASE-003: Format Universe Construction
- Union: format-registry.yaml + src dirs + qname registries + gap ledger + capability maps + test dirs
- For each format: record Python status, .NET status, test count, package status, gate status
- **Key paths:**
  - `registry/format-registry.yaml`
  - `shared/qname-registry/*.yaml` (21 files)
  - `reports/capability-layer/gap-ledger.json`
  - `.governance/capabilities/registry.yaml`
- **Output:** `reports/portfolio-recon-20260627/format-universe.yaml`

---

## Phase 2: Source Professionalism Audit (READ-ONLY)

### TC-SRC-001: Python Source Quality — ODF Family (fods, fodt, fodg, fodp, ods, odt)
For each format, assess 25 dimensions (spec fidelity, decomposition, API design, error handling, etc.) on 0-5 scale. Record:
- Domain model quality (classes vs dicts)
- Parser/writer separation
- Analytics mixing (functions in codec vs dedicated file)
- Monolithic files (>800 LOC)
- Public API clarity (__all__ exports)
- Known large files:
  - `src/python/fods/spreadsheet_document.py` (~1035 LOC)
  - `src/python/fods/neutral_model.py` (~1231 LOC)
  - `src/python/fodt/text_document.py` (~990 LOC)

### TC-SRC-002: Python Source Quality — Tabular/Text (csv, tsv, ndjson, dif, sylk, gnumeric, abw, toml)
Same assessment. Known large files:
- `src/python/abw/word_document.py` (~1026 LOC)
- `src/python/dif/interchange_document.py` (~994 LOC)
- `src/python/abw/abw_codec.py` (~663 LOC)

### TC-SRC-003: Python Source Quality — Binary/Image (pbm, pgm, ppm, qoi, xcf, zst)
Same assessment. Known large files:
- `src/python/zst/zst_codec.py` (~930 LOC)
- `src/python/xcf/xcf_parser.py` (~1272 LOC)

### TC-SRC-004: .NET Source Quality (fods, fodt, csv, tsv, ndjson, netpbm, zst)
Assess namespace organization, partial class decomposition, public API surface. Known issues:
- `src/net/fods/FodsDocument.cs` (1293 LOC, partial class)
- `src/net/fods/FodsDocumentAccessor.cs` (~2627 LOC, partial class — 146 public methods)
- `src/net/fodt/FodtDocumentExtendedApis.cs` (~2293 LOC, partial class)

### TC-SRC-005: Analytics Separation Assessment
Classify every function in each format's main codec/parser as: parse/read, write, analytics/stats, export, model.
- **Formats WITH dedicated _analytics.py:** csv, fodg, gnumeric, toml (4/20)
- **Formats with _stats/_metrics but not _analytics:** abw, dif, ndjson, ods, ppm, xcf, zst (7/20)
- **Formats with NO separation:** fodp, fods, fodt, odt, pbm, pgm, qoi, sylk, tsv (9/20)

### TC-SRC-006: Anti-Pattern Sweep
Search all source for: NotImplementedError, TODO, FIXME, empty pass bodies, broad exception catches, hardcoded paths, test-specific production logic.
- Known: 1 intentional NotImplementedError in `src/python/fodp/fodp_codec.py:214`
- Known: 0 TODO/FIXME from exploration

**Output:** `reports/portfolio-recon-20260627/source-professionalism-matrix.yaml`

---

## Phase 3: Feature Coverage and Gap Reconciliation (READ-ONLY)

### TC-FEAT-001: Feature Definition Standard
Establish strict taxonomy: load, parse, validate, inspect metadata, expose domain objects, edit domain objects, add/remove elements, preserve unknown content, save same format, roundtrip, export, convert, stream APIs, file APIs, error handling, package consumption.
- Exclude from product feature count: trivial getters, analytics summaries, test helpers, aliases

### TC-FEAT-002: Per-Format Feature Coverage (Python — all 20)
For each format, measure:
- Total authoritative required features (from capability map + spec authority)
- Fully implemented with proof
- Partially implemented
- Structural shell only
- Stubbed / missing
- Implemented but untested
- Tested but unpackaged

### TC-FEAT-003: Per-Format Feature Coverage (.NET — all 7)
Same measurement for .NET formats.

### TC-FEAT-004: Gap Ledger Reconciliation
- For each of 32 open gaps: verify still valid against source
- For 1,245 closed gaps: spot-check 10% (125 gaps) against source
- Flag incorrectly closed, missing, wrong state, wrong priority, duplicate
- Normalize format name casing inconsistencies (FODS vs fods vs Fods)
- **File:** `reports/capability-layer/gap-ledger.json`

### TC-FEAT-005: QName Registry vs Source Truth
For each of ~80 QName entries across 20 registry files:
- Verify python_file path exists
- Verify dotnet_file path exists (if declared)
- Verify status matches actual implementation
- Verify spec_fact_ref is valid
- **Files:** `shared/qname-registry/*.yaml`

### TC-FEAT-006: Capability Registry vs Command Registry
Fix 28 capabilities missing from command-registry.
- **Files:** `.governance/capabilities/registry.yaml`, `.governance/capabilities/parity-report.yaml`

**Output:** `reports/portfolio-recon-20260627/feature-coverage-matrix.yaml`, `reports/portfolio-recon-20260627/gap-reconciliation.yaml`

---

## Phase 4: Test Architecture Audit (READ-ONLY)

### TC-TEST-001: Test Organization Assessment
- Classify all 2,145 Python test files and 2,189 .NET test files by: unit, component, integration, roundtrip, conformance, package, consumer
- Identify sprint-numbered tests (R100-R355 pattern) vs behavior-named tests
- Measure test-to-feature traceability
- Flag duplicate coverage from successive deepening sprints

### TC-TEST-002: Test Quality Deep Dive
Sample 5-10 test files per format tier:
- Check assertion quality (behavior vs implementation detail)
- Check fixture provenance
- Check negative/boundary cases
- Check roundtrip proof
- Check independence from production internals
- Known: Zero weak assertions (assert True) from exploration

### TC-TEST-003: Package and Consumer Proof
For each of 20 Python formats:
- Verify pyproject.toml valid
- Verify pip install succeeds
- Verify `import {fmt}` works
- Verify representative feature from installed package
- **Known issue:** Non-editable installs require site-packages sync

### TC-TEST-004: Oracle Layer Verification
- Confirm all 20 Python formats at VERIFIED (73/73 PASS per MEMORY.md)
- Re-run `tools/oracle/execute_oracle.py` for spot-check
- **File:** `tools/oracle/execute_oracle.py` (1428 LOC)

**Output:** `reports/portfolio-recon-20260627/test-architecture-assessment.yaml`

---

## Phase 5: Machinery Readiness Audit (READ-ONLY)

### TC-MACH-001: Supervisor Machinery Classification
Classify each of 95 scripts in `tools/supervisor/` as:
- Actively used by autonomous loop
- Used by slash commands only
- Used by governance validators
- Unused/stale
- Top files: governance_validators.py (3183 LOC), autonomous_cycle.py (2656 LOC), autonomous_task_generator.py (1920 LOC)

### TC-MACH-002: Machinery Value Assessment
- Calculate machinery-to-product ratio per category
- Current: ~2.3:1 (tools:product LOC)
- Identify consolidation or retirement candidates
- Assess 33 tool subdirectories for necessity

### TC-MACH-003: Governance Validator Health
- Verify all 85+ validators callable
- Run test suite (138 tests per MEMORY.md)
- Identify WARN-only stubs vs real enforcement
- Check overclaim detector wiring (known: never called)
- Check failure-memory.json activity (known: static)

### TC-MACH-004: Skill and Command Wiring
- Verify 93 capabilities → commands → skills chain is complete
- Fix 28 missing command-registry entries
- Verify skill-registry.yaml entries match actual implementations

**Output:** `reports/portfolio-recon-20260627/machinery-readiness.yaml`

---

## Phase 6: Synthesis and Healing Plan (WRITE)

### TC-SYNTH-001: Project Direction Verdict
Based on Phases 1-5, assess:
- Is the project producing professional format libraries? YES/NO with evidence
- Is it drifting toward analytics/test-count optimization? Assessment
- Verdict: one of CORRECT_AND_PROVING, CORRECT_BUT_INCOMPLETELY_EXECUTED, PARTIALLY_CORRECT_WITH_SYSTEMIC_DRIFT, MAJOR_COURSE_CORRECTION_REQUIRED, DIRECTION_NOT_PROVEN

### TC-SYNTH-002: Root Cause Analysis
For each systemic issue found, identify:
- First failing boundary (why did machinery accept this?)
- Recurrence path
- Blast radius

### TC-SYNTH-003: Authoritative Healing Plan
Create `plans/healing/portfolio-product-machinery-recon-and-healing-plan.md` with:
- Priority model (P0-P4) with scoring
- Dependency graph
- Execution waves (W0-W8)
- Parallel lanes with ownership
- Micro-taskcards per confirmed issue
- Pilot definitions (15 pilots per user request)
- Backfill strategy
- Completion gates

### TC-SYNTH-004: Final Report
Produce structured report at `reports/portfolio-recon-20260627/final-report.md` covering all 12 user questions with evidence.

---

## Execution Strategy

Given the massive scope (every file in src/, every test, every gap), execution requires **multiple context windows**:

| Session | Scope | Taskcards | Estimated Work |
|---------|-------|-----------|----------------|
| 1 | Baseline + Source Inventory (Phase 1) | TC-BASE-001 through TC-BASE-003 | Heavy read, structured output |
| 2 | Source Professionalism (Phase 2) | TC-SRC-001 through TC-SRC-006 | Read every src file, classify |
| 3 | Feature Coverage + Gaps (Phase 3) | TC-FEAT-001 through TC-FEAT-006 | Gap ledger reconciliation |
| 4 | Test Architecture (Phase 4) | TC-TEST-001 through TC-TEST-004 | Test file sampling + oracle check |
| 5 | Machinery Audit (Phase 5) | TC-MACH-001 through TC-MACH-004 | Tool classification |
| 6 | Synthesis + Healing Plan (Phase 6) | TC-SYNTH-001 through TC-SYNTH-004 | Write healing plan + report |

**Within each session:** Use parallel Agent subagents for independent format batches. Use Explore agents for discovery, Plan agents for design.

---

## Verification

After all phases complete:
1. **Idempotent rerun:** Re-execute baseline capture; verify counts match
2. **Full test suite:** `.venv/Scripts/pytest tests/python/ -v` and `dotnet test` — confirm no regressions
3. **Governance validators:** Run all 85+ validators — confirm no new FAILs
4. **Gap ledger zero:** No unledgered confirmed gaps remain
5. **Source baseline:** No file >800 LOC outside known_violations
6. **Healing plan completeness:** Every finding has a governed taskcard

---

## Critical File Paths

| Purpose | Path |
|---------|------|
| Source baseline | `registry/source-structure-baseline.json` |
| Format registry | `registry/format-registry.yaml` |
| Gap ledger | `reports/capability-layer/gap-ledger.json` |
| Capability registry | `.governance/capabilities/registry.yaml` |
| QName registries | `shared/qname-registry/*.yaml` |
| Production standard | `docs/code-quality/production-library-standard-v2.md` |
| Skill registry | `.supervisor/skill-registry.yaml` |
| Session resume | `reports/supervisor/session-resume.md` |
| Master plan | `plans/master-plan.md` |
| Correction plan | `plans/strategic/spec-to-feature-radical-correction-plan.md` |
| Oracle executor | `tools/oracle/execute_oracle.py` |
| Governance validators | `tools/supervisor/governance_validators.py` |

---

## Expected Deliverables

1. `reports/portfolio-recon-20260627/baseline.yaml` — Repository state snapshot
2. `reports/portfolio-recon-20260627/source-inventory.yaml` — Every source file classified
3. `reports/portfolio-recon-20260627/format-universe.yaml` — All formats with status
4. `reports/portfolio-recon-20260627/source-professionalism-matrix.yaml` — Per-format quality scores
5. `reports/portfolio-recon-20260627/feature-coverage-matrix.yaml` — Per-format feature status
6. `reports/portfolio-recon-20260627/gap-reconciliation.yaml` — Ledger accuracy report
7. `reports/portfolio-recon-20260627/test-architecture-assessment.yaml` — Test quality report
8. `reports/portfolio-recon-20260627/machinery-readiness.yaml` — Tool health report
9. `plans/healing/portfolio-product-machinery-recon-and-healing-plan.md` — Authoritative healing plan
10. `reports/portfolio-recon-20260627/final-report.md` — Complete audit report answering all 12 questions


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-06-27T09:49:04.664313+00:00"
  locked_by: "1f738aa0cc70"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
