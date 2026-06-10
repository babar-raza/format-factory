# Next Skills Agent Prompt (R110)

## MODE: SKILLS STREAM — LIVE HANDOFF EXECUTION AND ENFORCEMENT HARDENING

## Sprint ID
FORMAT-FACTORY-SKILLS-R110-LIVE-HANDOFF-AND-ENFORCEMENT-HARDENING-001

## Stream: skills

## Read First
1. `reports/skills-r109/final-adversarial-independent-verification.md`
2. `reports/skills-r109/generated-handoffs/`
3. `reports/skills-r109/adoption-fixtures/` (test file)
4. `tests/python/supervisor/test_r109_adoption_consumption.py`
5. `tests/python/supervisor/test_r109_stream_isolation.py`
6. `tools/supervisor/validate_adoption_compliance.py`
7. `tools/supervisor/grade_declared_work.py`
8. `.supervisor/skill-registry.yaml`

## R109 Carry-Forward
- Adoption consumption proven: 3 receiver-side fixtures (25 tests) load and validate packages
- Enforcement fixtures: compliant + failing items demonstrated for all 3 streams
- 3 generated handoffs: Mainstream, Acceleration, Supervisor
- 5 transcripts validated (2 product, 1 supervisor, 1 acceleration, 1 anti-bypass)
- Stream isolation: 8 tests verify Skills outputs are stream-local
- 205 total supervisor tests (33 new in R109)
- Stream-state limitation: reports/supervisor/ is last-writer-wins (documented, not fixed)

## Tasks

### Task 1: Execute First LIVE Handoff
- Mainstream must execute one generated handoff (FODS RenameSheet or Netpbm ExtractChannel)
- Generate a LIVE transcript (mode: "live", actual_files_changed populated)
- If LIVE not authorized, produce detailed simulation with actual file paths verified

### Task 2: Wire Adoption Compliance into autonomous_cycle.py
- Add Step 4b after grading: call validate_adoption() on declaration
- Include adoption result in cycle output and review package
- Tests: 3 (adoption integrated into cycle, blocking behavior, non-blocking behavior)

### Task 3: Wire Stream Isolation into autonomous_cycle.py
- Tag outputs with stream_id from declaration/run_id
- Write stream-scoped outputs to reports/supervisor/{stream_id}/
- Tests: 3 (stream detection, output path, no contamination)

### Task 4: Registry Promotion Decision
- record-lane-execution: Lane ledger now proven in R108/R109 — promote to active
- check-mcp-status: Still no demand — keep deferred with updated rationale

### Task 5: Enforcement Gate Activation for Acceleration
- Change acceleration adoption package gates from "planned" to "active"
- Add tests verifying active status

## Hard Quota
- 1 LIVE handoff transcript (or detailed simulation with file verification)
- Adoption compliance wired into autonomous_cycle
- Stream isolation wired into autonomous_cycle
- Registry promotion for record-lane-execution
- Acceleration gates activated

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
