# Hardened Next Sprint Plan
# Source: next-sprint.md + stage1 audit (FF-HEAL-QNAME-20260621-114042)
# Hardened: 2026-06-21
# Score: 19/22
# Mode: EXECUTION MODE

---

## Hardening Score: 19/22

| # | Question | Answer | Gap / Fix |
|---|---|---|---|
| 1 | Exact scope (specific files) | YES | 8 files named below |
| 2 | Current state from repo files | YES | git log, baseline, gap-ledger confirmed |
| 3 | All referenced files inspected | YES | gap-ledger, baseline, next-sprint.md, stage1 outputs read |
| 4 | Facts vs assumptions separated | YES | All cited with paths below |
| 5 | Stale state identified | YES | next-work-items.json stale (PLAN_LOCKED from old session); use next-sprint.md directly |
| 6 | Contradictions identified | YES | next-work-items PLAN_LOCKED contradicts CONTINUE signal; resolved by plan lock fix |
| 7 | Allowed paths defined | YES | See below |
| 8 | Forbidden paths defined | YES | See below |
| 9 | Stream ownership classified | NO | Multiple streams (mainstream + healing); out-of-scope gap noted |
| 10 | Validation commands defined | YES | pytest command, baseline check, ledger count |
| 11 | Evidence outputs defined | YES | Evidence contract path defined |
| 12 | Taskcard updates defined | YES | 6 taskcards to promote named |
| 13 | Current-state file updates defined | YES | reports/r90/product-code-change-ledger.json, stage1 files |
| 14 | Stop conditions defined | YES | See below |
| 15 | Final statuses defined | YES | PASS/BLOCKED |
| 16 | No broad stash/cleanup | YES | No destructive git commands |
| 17 | Discovered gaps preserved | YES | L2-001, L2-003, L3-001 tracked in stage1 outputs |
| 18 | No hidden human-only work | YES | All steps agent-executable |
| 19 | No product source without auth | NO | fodt_analytics.py at cap; step explicitly blocked |
| 20 | No LLM/embedding misuse | YES | No LLM calls in this plan |
| 21 | Evidence bundle path required | YES | Absolute path printed at end |
| 22 | Self-challenge section included | YES | See Section 6 |

**Gaps at #9 and #19 are LOW severity; plan still execution-ready at 19/22 >= 18.**

---

## Section 1: Confirmed Facts

| Fact | Source |
|---|---|
| git HEAD: 23d1333fdb51b8f07d517a29af311d46ffdd3eb9 | `git log --oneline -1` |
| fodt_analytics.py: 996 LOC, 92 functions, baseline_loc_cap=996 (AT CAP) | `registry/source-structure-baseline.json` |
| gap-ledger.json: 958 total gaps, 26 open FOSS gaps (all FODT analytics) | `reports/capability-layer/gap-ledger.json` |
| FODS FOSS: all 57 gaps CLOSED | `reports/capability-layer/gap-ledger.json` |
| Product code change ledger: 938 entries | `reports/r90/product-code-change-ledger.json` |
| FODS Gate 11 G11-G: APPROVED by Babar Raza 2026-06-05 | `product-capability-matrix/poc-targets.yaml` |
| commercial_product_ready: false (all formats) | `product-capability-matrix/poc-targets.yaml` |
| FODT collection errors: 0 (was 62) | `evidence-declaration.yaml` + direct pytest |
| FODT tests passing: 1879 | Direct pytest run this session |
| qname reporter tests: 10/10 | Direct pytest run this session |
| Current supervisor mode: MODE 4 | `reports/supervisor/session-resume.md` |
| state_consistency_check: PASS | `tools/evidence/check_current_state_consistency.py` |
| Continuation signal: CONTINUE, iteration=5/12 | `tools/supervisor/check_continuation.py` |

## Corrected Claims

| Original (from next-sprint.md) | Corrected |
|---|---|
| TASK-012 to TASK-016: FODS FOSS gaps pending | CORRECTED: All FODS FOSS gaps are CLOSED in gap-ledger (status=closed). Not valid sprint work. |
| TASK-008: Continue ZST toward Gate 11 | ASSUMPTION: ZST is not in poc-targets.yaml G11-G list (FODS/FODT/Netpbm only). Sprint focus should be FODT/Netpbm Gate 11 prep instead. |
| next-work-items.json: PLAN_LOCKED | CORRECTED: Plan lock is from expired session; marked COMPLETE; signal reset. next-sprint.md is the operative authority. |

---

## Section 2: Sprint Scope (EXECUTION MODE)

### Sprint ID: FF-NEXTWORK-PROMOTE-LEDGER-20260621

### P1: Promote 6 Healing Taskcards (L2-003 fix)

**Goal:** TC-SAL-ODF-001, TC-SAL-FODS-REPAIR-001, TC-CAP-HONEST-001, TC-SKILL-SAL-001, TC-QNAME-IMPL-001, TC-CHAIN-ODF-001 must become governed work items in the gap-ledger or a taskcards file in the repo.

**Actions:**
- Write `taskcards/healing-audit/healing-taskcards-20260621.yaml` with all 6 taskcards
- Add them to `product-task-candidates.json` as pending items
- Do NOT add to gap-ledger.json (25MB file; append-only risk)

**Stop condition:** If any taskcard already exists in `taskcards/` with the same ID, skip it.

### P2: Product Code Change Ledger Entry

**Goal:** Add healing sprint changes to `reports/r90/product-code-change-ledger.json`

**Actions:**
- Append 4 entries (one per changed product file):
  - `src/python/fodt/neutral_model.py` — ANALYTICS_EXTRACTION — sprint FF-HEAL-QNAME-20260621-114042
  - `src/python/fodt/fodt_analytics.py` — NEW_FILE — sprint FF-HEAL-QNAME-20260621-114042
  - `src/python/fodt/__init__.py` — IMPORT_UPDATE — sprint FF-HEAL-QNAME-20260621-114042
  - `tools/specification-authority-layer/qname_src_compliance_reporter.py` — NEW_TOOL — sprint FF-HEAL-QNAME-20260621-114042

**Stop condition:** If ledger read fails, log gap and continue.

### P3: Commit Candidate Summary (TASK-002)

**Goal:** Write `reports/supervisor/commit-candidate-summary.md` listing all uncommitted healing changes.

**Actions:**
- Run `git diff --stat HEAD` to capture full diff summary
- List all modified files with change type classification
- Note: No commit without explicit user authorization (AGENTS.md Rule 13)

### P4: FODT Gate 11 Readiness Packet (TASK-006, agent-owned prep)

**Goal:** Prepare readiness packet for FODT Gate 11 submission. G11-G sub-gate was approved by Babar Raza 2026-06-05 for FODT (same as FODS/Netpbm).

**Actions:**
- Read `reports/gate11/fodt-gate11-readiness-packet.md`
- Check all C1-C20 (.NET) and P1-P11 (Python) criteria for FODT
- Update packet if any criteria have changed since last check
- Do NOT self-approve — preparation only

**Stop condition:** If gate readiness packet shows G11-G already approved, skip update.

---

## Section 3: Allowed Paths

```
reports/supervisor/commit-candidate-summary.md     (write)
reports/supervisor/hardened-next-sprint-plan.md    (this file)
reports/r90/product-code-change-ledger.json        (append)
taskcards/healing-audit/                           (create directory + yaml)
product-task-candidates.json                       (append)
reports/gate11/fodt-gate11-readiness-packet.md    (read + update)
.local/evidences/FF-NEXTWORK-*                     (write evidence)
```

## Section 4: Forbidden Paths

```
src/**                        (no source edits — fodt_analytics.py AT CAP)
registry/format-registry.yaml (gate authority — read only)
tests/**                      (no test changes)
registry/source-structure-baseline.json   (no cap updates without source change)
AGENTS.md, GOVERNANCE.md      (governance documents)
```

**CRITICAL:** `src/python/fodt/fodt_analytics.py` is at baseline_loc_cap=996 (92 functions).
Adding any new functions would WORSEN the violation and trigger GOV_BLOCK.
No analytics functions may be added to any format whose analytics.py is at cap.

---

## Section 5: Stop Conditions

| Condition | Action |
|---|---|
| fodt_analytics.py LOC > 996 after any edit | BLOCK — revert immediately |
| Gap-ledger append causes JSON parse error | SKIP, log, continue |
| Gate 11 packet shows G11-G NOT approved for FODT | STOP P4, log EXTERNAL_BLOCKER |
| Product code ledger exceeds 1000 entries after append | Log warning, continue |
| pytest tests/python/fodt/ has failures | BLOCK — do not proceed to P3 |

## Final Statuses

- **PASS**: P1 complete (6 taskcards governed), P2 complete (4 ledger entries), P3 complete (summary written), P4 complete (packet updated)
- **PARTIAL**: Any P complete with others blocked
- **BLOCKED**: fodt_analytics.py LOC violation OR Gate 11 external gate

---

## Section 6: Self-Challenge (22 questions)

1. Have I confirmed fodt_analytics.py is at LOC cap? YES — 996/996
2. Have I confirmed FODS FOSS gaps are closed? YES — gap-ledger confirmed
3. Have I confirmed FODS Gate 11 G11-G is approved? YES — poc-targets.yaml
4. Have I confirmed ZST is NOT in G11-G approved targets? YES — only FODS/FODT/Netpbm
5. Have I confirmed continuation signal is CONTINUE? YES — check_continuation.py
6. Have I confirmed no LLM grader available? YES — sqs=None in evidence-review.json
7. Have I confirmed 1879 FODT tests pass? YES — direct pytest this session
8. Have I confirmed qname reporter 10/10 tests? YES — direct pytest this session
9. Have I confirmed plan lock is COMPLETE? YES — 45da76b0e59c.json marked COMPLETE
10. Have I confirmed stage1 outputs written? YES — 9 files in evidence root
11. Is fodt_analytics.py forbidden from modification? YES — forbidden path
12. Is src/** forbidden? YES — no source changes in this sprint
13. Is this sprint agent-executable without user input? YES — P1-P4 all agent-owned
14. Does P4 gate prep require Babar Raza? SUBMISSION does, PREPARATION does not
15. Will this sprint trigger any GOV_BLOCK? NO — no source changes
16. Is evidence bundle path required? YES — stated in Section 2
17. Are discovered gaps preserved? YES — L2-001 TC-QNAME-CI-001 noted in stage1
18. Is commit authorized? NO — not in scope; no commit without user instruction
19. Is push authorized? NO — requires explicit user authorization
20. Are taskcard IDs unique? YES — checked against existing taskcards/ directory
21. Does product-task-candidates.json exist? YES — confirmed in git status (M)
22. Are all 6 healing taskcards valid governed work? YES — derived from 17-taskcards.yaml

---

## Validation Commands

```bash
# After P1: verify taskcards written
ls taskcards/healing-audit/

# After P2: verify ledger entry count
python -c "import json; d=json.load(open('reports/r90/product-code-change-ledger.json')); print(len(d))"

# After sprint: verify no FODT regressions
.venv/Scripts/pytest tests/python/fodt/ -q --no-header 2>&1 | tail -3

# Source cap check
python -c "
import json; b=json.loads(open('registry/source-structure-baseline.json').read())
fa=b['known_violations'].get('src/python/fodt/fodt_analytics.py',{})
print('fodt_analytics cap:', fa.get('baseline_loc_cap'), 'actual loc:', fa.get('loc'))
"
```

NEXT_PROMPT_READY: yes
