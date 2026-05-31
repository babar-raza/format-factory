# Replay Self-Containment Proof

**sprint_id:** FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530

## Supervisor Replay Result

```
supervisor_loop.py run-on-latest — executed 2026-05-30

DISCOVERY: OK
  Bundle: .local/evidence/dual-orchestration-supervisor-e2e-20260530-165603.zip
  Entries: 3172

EVIDENCE_REVIEW: ACCEPTED
  Tests: 0 passed / 0 failed
  PENDING markers: 0

CONTRADICTION_CHECK: WARNING_CONTRADICTIONS
  Critical: 0, Warning: 1
  [WARNING] Sprint ID mismatch: evidence vs contract (R80 contract loaded, R40 bundle used)
  Autonomous continue: True

PACKET_GENERATION: COMPLETE
  next-sprint.md, next-sprint-taskmaster.json, next-ruflo-lanes.json,
  approval-gates.md, session-resume.md — all written

MEMORY_SYNC: SKIPPED_IDEMPOTENT

SUPERVISOR LOOP: COMPLETE (exit 0)
```

## Replay Fixture Information

The supervisor discovered `.local/evidence/dual-orchestration-supervisor-e2e-20260530-165603.zip` as the latest evidence bundle. This is the previous supervisor sprint's bundle.

**Replay input fixture:** `.local/evidence/dual-orchestration-supervisor-e2e-20260530-165603.zip`
- Entries: 3172
- Size: 5,554,751 bytes
- SHA-256: `8edb18ae7c7030e6618b233b6dcced329a1609943e831dfacfc998fabca5005f`

## Limitation: Replay Fixture Not Bundled (TC-SUP-REPLAY-001)

The replay fixture is in `.local/evidence/` (gitignored). It is NOT included in the R80 ZIP. An external verifier cannot reproduce the replay from the ZIP alone.

**Taskcard:** TC-SUP-REPLAY-001
**Description:** Include a copy of the replay input bundle (or a small fixture) in the evidence ZIP so an external verifier can reproduce the supervisor replay.
**Workaround for R80:** The bundle includes the supervisor scripts + all supervisor outputs. The replay itself runs successfully (exit 0) and outputs are in `reports/supervisor/`. The limitation is documented and taskcard created.

## What Replay Proves

1. supervisor_loop.py discovers available evidence bundle
2. Evidence review runs and produces evidence-review.json
3. Contradiction detection runs (1 warning: sprint ID mismatch — expected when using old bundle)
4. Next-sprint packet generated: 5 output files
5. Memory sync runs (skipped as idempotent — correct)
6. All 8 runtime outputs present in reports/supervisor/
7. Exit code: 0
