# Next Agent Execution Prompt
# Sprint: ff-machinery-readiness-audit-20260625
# Generated: 2026-06-25

## Context for Next Agent

You are resuming Format Factory autonomous product deepening after a machinery readiness
audit sprint (ff-machinery-readiness-audit-20260625). Read this prompt completely before
acting. Do not resume prior product deepening until you have read the audit findings.

---

## FIRST ACTION — Read These Files

Read ALL of the following before any work:
1. `plans/master-plan.md` — strategic authority
2. `plans/spec-to-feature-radical-correction-plan.md` — binding correction plan
3. `reports/machinery-readiness-audit-20260625/21-final-verdict.md` — audit result
4. `reports/machinery-readiness-audit-20260625/17-machinery-repair-plan.md` — repair sequence
5. `reports/machinery-readiness-audit-20260625/15-system-gap-matrix.yaml` — 19 gaps
6. `reports/machinery-readiness-audit-20260625/16-taskcards.yaml` — 19 taskcards
7. `reports/supervisor/session-resume.md` — current continuation state

---

## MANDATORY CONTEXT

### Audit Verdict

```
VERDICT: READY_AFTER_TARGETED_MACHINERY_REPAIRS
Sprint: ff-machinery-readiness-audit-20260625
```

The system has professional-quality source code and working product proof (14 formats at
PROOF_LEVEL_4). BUT 4 BLOCKER gaps prevent autonomous spec-backed product deepening:

| Blocker | Status | Taskcard |
|---|---|---|
| SAL pipeline dormant | NOT STARTED | SAL-REPAIR-001 |
| _EXPANSION_GOALS hardcoded | NOT STARTED | CAPABILITY-REPAIR-001 |
| Overclaim detector not wired | NOT STARTED | SUPERVISOR-CONTINUATION-001 |
| Lane DAG not code-enforced | NOT STARTED | SUPERVISOR-LANES-001 |

### What Is Working

- Product quality: PROFESSIONAL (7/10 senior dev rating)
- QName compliance: FULL for 9 Python formats; IMPLEMENTING for 11
- Test suite: 1609+ tests pass; 0 failures at audit time
- Consumer roundtrip proofs: 14/20 Python formats PASS
- Gate 11 candidates: FODS/FODT/PBM/PGM/PPM all TECHNICALLY READY
- Session isolation: EXCELLENT (CCI-MVP; 45 tests pass)
- Plan lock enforcement: EXCELLENT
- 19-state continuation machine: EXCELLENT

### What Is Broken

- SAL pipeline: 3 active / 17 dormant tools
- Task generator: hardcoded _EXPANSION_GOALS (not gap-ledger-driven)
- Feature compiler: design exists; Phase 2 not implemented
- Overclaim detector: exists but never called
- Lane DAG: prompt-only enforcement only
- Durable learning: FailureMemory imported but not integrated
- Backfill coverage: 1/20 formats (ABW only)

---

## NEXT SPRINT SELECTION LOGIC

**If check_continuation.py returns CONTINUE:**
1. Select from the MACHINERY lane first (REPAIR-01 through REPAIR-05 from artifact 17)
2. Do NOT start product deepening on Wave B formats (CSV, NDJSON, TSV, etc.) until
   SAL-REPAIR-001 and CAPABILITY-REPAIR-001 are CLOSED
3. AUTHORIZED NOW for Wave C (ODS, ODT) and Wave D (FODP, QOI) product work
   — these do NOT require SAL-REPAIR-001

**Recommended next sprint:**

```
Sprint: REPAIR-01 — Overclaim Detector Wiring
Type: Machinery Lane 14
Taskcard: SUPERVISOR-CONTINUATION-001
Target file: tools/supervisor/autonomous_cycle.py
Evidence: tests/supervisor/test_overclaim_detector_wiring.py
No product source changes
Estimated LOC change: <50 LOC in autonomous_cycle.py
```

Why REPAIR-01 first: SUPERVISOR-CONTINUATION-001 has no prerequisites and is lowest effort.
It can be completed in a single sprint and provides immediate safety improvement.

**Alternative if user authorizes product work:**

```
Sprint: PILOT-ODS-001 — ODS Consumer Roundtrip
Type: Product Lane 9, Wave C
Target format: ODS (SAL CHAIN_INTACT — authorized without SAL-REPAIR-001)
Skill: /add-installed-package-example
Evidence: examples/python/ods/ods_consumer_roundtrip.py + 5+ tests
```

---

## IMPORTANT CONSTRAINTS

1. **Do NOT run product deepening for CSV/NDJSON/TSV/GNUMERIC/SYLK/TOML/ZST/ABW/DIF**
   until SAL-REPAIR-001 closes. These formats are CHAIN_BROKEN_AT_SAL.

2. **Do NOT add arithmetic analytics functions** (rotation suspended since 2026-06-18).
   New analytics MUST trace to GAP-* entry in gap-ledger.json + FACT-{FORMAT}-* in SAL cache.

3. **Always use /add-python-api skill** for product source changes.
   Ad-hoc edits are blocked by V50 (forbidden targets) and TC-GUARD-001.

4. **Stale plan locks**: If check_continuation returns ACTIVE_PLAN_INCOMPLETE,
   run: `python -c "import json,glob; [open(f,'w').write(json.dumps({**json.load(open(f)), 'status':'SUPERSEDED'})) for f in glob.glob('.local/supervisor/plan-locks/*.json') if json.load(open(f)).get('status') == 'IN_PROGRESS']"`

5. **GOV_BLOCK**: If continuation signal contains GOV_BLOCK:monolith_detection_validator,
   the NEXT sprint MUST be the analytics separation refactor for the blocking format.
   Do NOT proceed to product deepening until GOV_BLOCK is resolved.

---

## KEY FILE PATHS

| Resource | Path |
|---|---|
| Gap ledger | reports/capability-layer/gap-ledger.json |
| SAL facts | .local/spec-cache/sal-facts-{format}.json |
| QName registry | shared/qname-registry/{format}.yaml |
| Source baseline | registry/source-structure-baseline.json |
| Skill registry | .supervisor/skill-registry.yaml |
| Continuation signal | .local/supervisor/continuation-signal.json |
| Next work items | .local/supervisor/next-work-items.json |
| Audit findings | reports/machinery-readiness-audit-20260625/ (22 artifacts) |
| Backfill inventory | docs/audits/python-qname-backfill-inventory.csv |
| Product deepening ledger | registry/product-deepening-ledger.yaml |
| Gap matrix | reports/machinery-readiness-audit-20260625/15-system-gap-matrix.yaml |
| Taskcards | reports/machinery-readiness-audit-20260625/16-taskcards.yaml |

---

## GOVERNANCE CHECKS BEFORE ANY SPRINT

```bash
# 1. Check continuation
python tools/supervisor/check_continuation.py

# 2. Verify no GOV_BLOCK rework items
cat .local/supervisor/continuation-signal.json | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('rework_items', []))"

# 3. Check source baseline for target format file
python -c "import json; b=json.load(open('registry/source-structure-baseline.json')); print(b['known_violations'].get('src/python/TARGET/TARGET_file.py', 'NOT_TRACKED'))"

# 4. Verify skill is available for planned work type
grep -l "your_intended_skill" .claude/commands/
```

If all checks pass: proceed. If any fail: address the failure first.
