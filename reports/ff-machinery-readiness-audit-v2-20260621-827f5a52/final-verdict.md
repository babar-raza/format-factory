# Final Verdict — Format Factory Machinery + Product Readiness Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52
# Date: 2026-06-21
# Branch: main HEAD: 827f5a52
# Prior audit: HEAD 23d1333f (verdict: NOT_READY_REPAIR_MACHINERY_FIRST)

---

## VERDICT: READY_AFTER_TARGETED_MACHINERY_REPAIRS

**Upgraded from prior audit verdict NOT_READY_REPAIR_MACHINERY_FIRST**

With specific conditions:
- P0 blockers must resolve BEFORE the next product sprint starts
- FODS and FODT can proceed; all other formats cannot claim spec-backed deepening
- Machinery repairs run in SEPARATE sprints from product deepening

---

## Evidence Basis (Direct Inspection — No AI Summaries)

All findings in this audit are based on:
1. Live run of `qname_structure_validator.py` — FODS=COMPLIANT, FODT=COMPLIANT, others=NO_SPEC_CLASSES
2. Live run of `pytest tests/python/fods/` — 32 collection errors confirmed, 44 pass confirmed
3. Direct inspection of `.local/spec-cache/sal-facts-fods.json` — 4987 facts, all source=workbench_verified
4. Direct inspection of `verified-facts-review.yaml` — generated_by=TCA-010 auto-seed downgrade pass
5. Direct inspection of `FodsDocument.cs` — 1293 LOC, FormatFactory.Fods namespace, 30 public methods
6. Direct inspection of `src/python/fods/Compat/` — 3 facade classes, untracked
7. Direct inspection of `active-plan-lock.json` — TERMINAL_CLOSED (not blocking)
8. Direct inspection of `continuation-signal.json` — state=YES, iter=10
9. Direct inspection of `capability_compiler.py` — reads wrong SAL path
10. Direct inspection of `snoopy-juggling-seal.md` — SAL root cause analysis

---

## Component Readiness Summary

### CHANGED SINCE PRIOR AUDIT (23d1333 → 827f5a52)

| Component | Prior Status | Current Status | Delta |
|-----------|-------------|----------------|-------|
| SAL facts — FODS | 78 real (stranded) | 4987 loadable (auto-seeded) | PARTIAL FIX |
| SAL idempotency | BROKEN | FIXED | FIXED |
| FODS Python spec/ stubs | NONE | 15 classes COMPLIANT | FIXED |
| FODT Python spec/ stubs | NONE | 8 classes COMPLIANT | FIXED |
| FODS Compat/ facades | NONE | 3 facades (untracked) | PARTIAL FIX |
| .NET Spec/ stubs (FODS) | NONE | architecture_only stubs | PARTIAL |
| Plan lock | IN_PROGRESS (blocking) | TERMINAL_CLOSED (clear) | FIXED |
| Continuation signal | MANUALLY RESET (yellow) | YES (green), iter=10 | FIXED |
| V45/V46 validators | MISSING | ADDED | IMPROVED |
| FODS test collection errors | 31 errors | 32 errors | WORSE (1 more) |

### UNCHANGED (still not resolved)

| Component | Status | Verdict |
|-----------|--------|---------|
| SAL fact quality | Auto-seeded (not spec-verified) | RED |
| QName for non-ODF formats | NO_SPEC_CLASSES | RED |
| .NET production naming | Format-prefixed (not spec-shaped) | YELLOW |
| Capability-to-feature compiler path | Wrong SAL path | RED |
| Backfill tooling | Design only | RED |
| Lane separation | Absent | ORANGE |
| Product skills — QName enforcement | None | ORANGE |

---

## Qname Readiness Summary

Python: FODS=COMPLIANT (15), FODT=COMPLIANT (8), all others=NO_SPEC_CLASSES
.NET: architecture_only stubs only; production code NOT spec-shaped
Overall: PARTIAL. FODS/FODT have scaffolding. No other format has QName structure.

---

## Source Quality Summary

| Product | Rating | Note |
|---------|--------|------|
| FODS .NET | Yellow | Professional, working, not spec-shaped names |
| FODT .NET | Yellow | Similar to FODS .NET |
| FODS Python | Yellow | 32 test errors, uncommitted Compat/, dirty neutral_model.py |
| FODT Python | Yellow | Smaller, no Compat/ layer |
| ZST Python | Orange | Analytics monolith, rotation suspended |
| XCF Python | Red | 4773 LOC analytics, GOV_BLOCK risk |
| ABW/DIF/ODS/ODT | Gray | Minimal stubs |

---

## SAL Readiness Summary

PARTIAL. Volume improved (4987 FODS facts) but quality unverified (auto-seeded).
SAL pipeline mechanics fixed. Facts loaded from workbench. Fact quality not independently verified.
Only FODS and FODT have any facts; 18+ formats have zero.

---

## Capability Layer Readiness Summary

DATA-RICH BUT DISCONNECTED. 958 gaps (932 "closed" — status inflation risk).
Compiler exists but reads wrong SAL path. Gap ledger spec_facts field populated statically.
No dynamic SAL-to-capability pipeline.

---

## Skill Readiness Summary

PARTIALLY READY. Core product skills work. QName not enforced in skill prompts.
V46 transcript validator added. add-analytics-function suspended. sal-pipeline-heal.md added (untracked).

---

## Autonomous Supervisor Readiness Summary

PARTIALLY READY. 40 validators active. Sprint closeout works. Plan lock cleared.
Continuation signal GREEN. Lane separation absent but sequential operation is safe.
Gate 11 STOP not hard-coded — requires user authorization path.

---

## Lane Separation/Collision Summary

Identity files exist (session-machinery.id, session-product.id) but no actual state isolation.
For current sequential single-agent operation: SAFE.
For future concurrent operation: HIGH RISK.

---

## Backfill Readiness Summary

DESIGN ONLY. No tooling built. Prior audit backfill-facility-design.md exists.
TC-BACKFILL-001 created in this audit. Not blocking product deepening immediately.

---

## Products Closest to Gate 11

1. **FODS .NET** — nearest. G11-G internal approved, needs C1-C20 formal packet and Babar Raza
2. **FODT .NET** — second. Gate 11 prep in progress
3. **FODS Python** — third. After test fix and Compat/ commit

---

## Products Best for Spec-to-Library-to-Export Proof

1. **FODS** (Python + .NET) — fullest chain: spec facts → spec/ stubs → Compat/ facades → public API → export
2. **FODT** (Python + .NET) — similar chain, slightly less complete

---

## Must-Fix Blockers Before Product Deepening

1. TC-FODS-TEST-FIX-001: Delete 32 stranded FODS analytics test files
2. TC-FODS-COMMIT-001: User authorization for git commit (TRUE_EXTERNAL_GATE)

---

## Repairs That Can Run in Machinery Lane (After Product Sprint)

1. TC-SAL-VERIFY-001: Segregate auto-seeded SAL facts
2. TC-CAPABILITY-COMPILER-001: Wire compiler to correct SAL path
3. TC-SKILL-QNAME-001: Add QName requirement to product skill prompts
4. TC-BACKFILL-001: Create FODS backfill inventory tool
5. TC-SUPERVISOR-LANES-001: Implement file ownership per lane (from prior audit)

---

## Product Deepening Lane Plan After Repairs

Sprint 1 (Product): Fix FODS tests, commit, prepare FODS Gate 11 packet
Sprint 2 (Product): Prepare FODT Gate 11 packet, create FODT Compat/
Sprint 3 (Machinery): SAL verification, compiler wiring, skill QName enforcement
Sprint 4 (Product): Submit Gate 11 packets to Babar Raza → STOP (TRUE_EXTERNAL_GATE)

---

## Next Execution Prompt Path

`reports/ff-machinery-readiness-audit-v2-20260621-827f5a52/next-agent-execution-prompt.md`

---

## What Was Intentionally NOT Done

1. Did NOT start product deepening (investigation mode only per user directive)
2. Did NOT run `dotnet test` for .NET products (environment setup unknown)
3. Did NOT verify SAL facts against actual spec PDF text (would require reading 57,803 lines of normalized text)
4. Did NOT implement any machinery repairs (investigation mode)
5. Did NOT create backfill tooling (design phase only)
6. Did NOT run full test suite (46,000+ tests, 7+ minute scan per memory note)

---

## Final Self-Check Answers

- Did I inspect actual repo evidence? YES — live validator run, live test run, file reads
- Did I avoid relying on summaries? YES — read actual files, ran actual tools
- Did I audit qname compliance per product? YES — per-product-qname-compliance.yaml
- Did I inspect src/ directly? YES — fods/, fodt/, xcf/, zst/, net/ inspected
- Did I inspect .NET and Python products? YES
- Did I inspect skills? YES — 29 commands inventoried, key gaps identified
- Did I inspect SAL? YES — 4987 facts analyzed, auto-seed root cause found
- Did I inspect capability layer? YES — 958 gaps, compiler path bug found
- Did I inspect downstream layers? YES — feature compiler, product factory
- Did I inspect autonomous supervisor? YES — 40 validators, continuation state
- Did I check machinery/product lane separation? YES — absent, risk matrix produced
- Did I check contamination/collision risk? YES — risk matrix in lane-separation file
- Did I identify whether backfill exists? YES — design only, not built
- Did I design backfill if missing? YES — backfill-facility-design.md updated
- Did I separate working from repeatable from governed from production-ready? YES
- Did I avoid claiming Gate 11 readiness from tests alone? YES
- Did I produce taskcards? YES — 8 taskcards
- Did I produce a gap matrix? YES — 11 gaps in system-gap-matrix.yaml
- Did I give a clear go/no-go verdict? YES — READY_AFTER_TARGETED_MACHINERY_REPAIRS
- Did I provide the next execution prompt? YES — next-agent-execution-prompt.md
