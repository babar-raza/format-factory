# Next Agent Execution Prompt
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333
# EXECUTION MODE

---

## Context

A deep machinery + product readiness audit was completed in sprint
`ff-machinery-readiness-audit-20260621-23d1333`. The verdict is:

**NOT_READY_REPAIR_MACHINERY_FIRST** — but P0 repairs can start immediately.

## Immediate Tasks (P0 — execute in order)

### Step 1: Resolve Stale Plan Lock (TC-SUPERVISOR-LOCK-001)

```
1. Read: C:/Users/prora/.claude/plans/polished-hopping-glacier.md
2. Find the status of TC-HARD-011 and any remaining open taskcards
3. If ALL taskcards in the plan are complete:
   python tools/supervisor/write_plan_lock.py \
     --plan-path "C:/Users/prora/.claude/plans/polished-hopping-glacier.md" \
     --terminal
4. If not complete: execute remaining taskcards, then run --terminal
5. Verify: .local/supervisor/active-plan-lock.json shows status != IN_PROGRESS
```

### Step 2: Fix 31 FODS Python ImportErrors (TC-FODS-TEST-FIX-001)

```
1. Run: .venv/Scripts/pytest tests/python/fods/ --collect-only 2>&1 | grep "ImportError"
2. For each broken test file, identify the missing function
3. Decision rule:
   - If function is a REAL capability (get_*, set_*, write_*, export_*): IMPLEMENT IT
   - If function is an analytics-arithmetic function (no spec backing): DELETE TEST FILE
4. After each batch of fixes: .venv/Scripts/pytest tests/python/fods/ -q --tb=no
5. Target: zero collection errors; at least 1000 passing tests
6. Create ledger entry: reports/r90/product-code-change-ledger.json
```

### Step 3: Prepare FODS Gate 11 Submission Packet

```
1. Read: reports/gate11/fods-gate11-readiness-packet.md
2. Update test counts (run .venv/Scripts/pytest tests/python/fods/ -q --tb=no after Step 2)
3. Create submission summary for Babar Raza:
   - Current .NET test count: 547
   - Current Python test count: (updated after Step 2)
   - Feature capabilities: all PASS from poc-targets.yaml
   - Gate status: G11-G APPROVED 2026-06-05 — requesting final commercial sign-off
4. STOP — this is a TRUE_EXTERNAL_GATE. Report to user for submission.
```

## P1 Machinery Repairs (after P0 complete)

### Step 4: Wire FODS SAL Facts (TC-SAL-FIX-001)

```
1. Read: tools/specification-authority-layer/sal_master_runner.py
2. Read: .local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml
3. Modify sal_master_runner.py to:
   a. Load verified-facts-review.yaml for each format that has it
   b. Emit facts with FACT-{FORMAT}-NNN IDs to sal-facts-latest.json
   c. Keep existing template facts as fallback for formats without verified facts
4. Run: .venv/Scripts/pytest tests/specification-authority-layer/ -q
5. Verify: test_sal_facts_has_fods_facts PASSES
```

### Step 5: Build QName Ontology Generator (TC-QNAME-GEN-001)

```
1. Create: tools/supervisor/qname_ontology_generator.py
2. Input: --format FODS, reads .local/spec-cache/fods/
3. Output: reports/specification-authority-layer-mwp/qname-ontology/qname-to-code-map-fods.json
4. Test with: python tools/supervisor/qname_ontology_generator.py --format FODS
5. Verify output is valid JSON matching existing qname-to-code-map.yaml schema
```

## Evidence Requirements

After each step:
1. Write `.local/evidences/<run_id>/evidence-declaration.yaml`
2. Run `python tools/supervisor/autonomous_cycle.py autonomous-cycle --declaration ...`
3. Log any exit codes and continue regardless

## Forbidden During This Prompt

- Do NOT add any new analytics functions to xcf_analytics.py, zst_codec.py, or fodg_codec.py
- Do NOT start product deepening for new formats
- Do NOT edit any src/ files for product features until Step 2 is complete
- Do NOT claim QName compliance without actual implementation
- Do NOT commit without explicit user authorization

## Success Criteria

- Zero ImportError collection failures in tests/python/fods/
- FODS Gate 11 submission packet ready for Babar Raza
- SAL test passes: FODS facts in sal-facts-latest.json
- Active plan lock resolved (not IN_PROGRESS)

## Audit Reference

Full audit: `reports/ff-machinery-readiness-audit-20260621-23d1333/`
Gap matrix: `reports/ff-machinery-readiness-audit-20260621-23d1333/system-gap-matrix.yaml`
Taskcards: `reports/ff-machinery-readiness-audit-20260621-23d1333/taskcards.yaml`
