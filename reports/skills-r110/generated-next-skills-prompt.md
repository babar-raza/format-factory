# Next Skills Agent Prompt (R111)

## MODE: SKILLS STREAM — LIVE HANDOFF AND AUTONOMOUS CYCLE INTEGRATION

## Sprint ID
FORMAT-FACTORY-SKILLS-R111-LIVE-HANDOFF-AND-CYCLE-INTEGRATION-001

## Stream: skills

## Read First
1. `reports/skills-r110/final-adversarial-independent-verification.md`
2. `reports/skills-r110/generated-handoffs/` (v2 hardened)
3. `reports/skills-r110/sample-outputs/` (6 machine-readable JSON)
4. `tests/python/supervisor/test_r110_sample_outputs_and_enforcement.py`
5. `tools/supervisor/validate_adoption_compliance.py`
6. `tools/supervisor/autonomous_cycle.py`

## R110 Carry-Forward
- 6 machine-readable sample outputs (anti-skip missing_sample_outputs CLOSED)
- 3 hardened handoffs (v2: validation_command, transcript_requirement, raw_log_requirement, fail_conditions)
- 7 transcripts validated (2 product + 2 acceleration + 2 supervisor + 1 anti-bypass)
- 24 new tests (229 total): sample packaging, adoption hardening, handoff enforcement, continuation semantics
- Continuation semantics: YES requires all_pass=true, low-severity → YES_WITH_LIMITATIONS

## Tasks

### Task 1: Wire Adoption Compliance into autonomous_cycle.py
- Add Step 4b after grading: validate_adoption(declaration)
- Include adoption_result in cycle output
- Tests: 3 (integrated, blocking, non-blocking)

### Task 2: Wire Stream Isolation into autonomous_cycle.py
- Tag outputs with stream_id from run_id
- Write to reports/supervisor/{stream_id}/ instead of reports/supervisor/
- Tests: 3 (detection, output path, no contamination)

### Task 3: Execute First LIVE Handoff
- Use hardened handoff v2 YAML as template
- Generate LIVE transcript with actual_files_changed populated
- Validate via validate_skill_transcript.py

### Task 4: Promote record-lane-execution Skill
- Lane ledger proven across R108/R109/R110
- Promote from deferred to active in skill-registry.yaml
- Create command file

### Task 5: Continuation Semantics in autonomous_cycle
- Wire YES_WITH_LIMITATIONS into continuation-signal.json
- Low-severity anti-skip → autonomous_continue=true + caveat

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
