# Next Skills Agent Prompt (R108)

## MODE: SKILLS STREAM — TRANSCRIPT-GRADE PIPELINE DEEPENING AND LIVE PROOF

## Sprint ID
FORMAT-FACTORY-SKILLS-R108-TRANSCRIPT-GRADE-PIPELINE-DEEPENING-AND-LIVE-PROOF-001

## Stream: skills (NOT mainstream, NOT supervisor, NOT acceleration)

## Read First
1. `reports/skills-r107/transcript-cycle-integration.md`
2. `reports/skills-r107/skill-registry-maturity.md`
3. `reports/skills-r107/command-validator-advancement.md`
4. `reports/skills-r107/cross-stream-adoption-enforcement.md`
5. `reports/skills-r107/governed-handoff-proof.md`
6. `.supervisor/skill-registry.yaml`
7. `tools/supervisor/inspect_declared_evidence.py`
8. `tools/supervisor/grade_declared_work.py`
9. `tools/supervisor/validate_skill_transcript.py`
10. `tools/supervisor/autonomous_cycle.py`

## R107 Carry-Forward
- Inspector now enriches with transcript_validation (R107 Lane B)
- Registry: 23 active, 2 deferred, 0 orphan, 0 draft (R107 Lane C: 13 stability tests)
- Validator: 12 pipeline/edge case tests (R107 Lane F)
- 144 total supervisor tests pass (43 new in R107)
- Stream-state contamination: documented as known limitation (reports/supervisor/ is last-writer-wins)
- Deferred skills: record-lane-execution, check-mcp-status — no change

## Tasks

### Task 1: Use transcript_validation in grade_item for VERIFIED Boost
- Modify grade_item() to treat transcript_validation.all_valid=True as a concrete proof dimension
- Items with valid transcript + evidence should get ACCEPTED_VERIFIED (not just ACCEPTED_WITH_LIMITATIONS)
- This will increase evidence_quality_score for sprints that include transcript JSON
- Tests: 5 (transcript boosts VERIFIED, invalid transcript doesn't boost, no transcript unchanged, mixed transcript, transcript with tests)

### Task 2: Execute First LIVE Handoff
- Mainstream must execute one of the 4 governed handoffs (FODS RenameSheet, Netpbm ExtractChannel, FODT roundtrip, or R107 new)
- Skills validates the returned LIVE transcript
- If LIVE execution not authorized, produce a validated simulation proof
- Tests: transcript validation of LIVE transcript

### Task 3: Adoption Compliance Validator
- Create `tools/supervisor/validate_adoption_compliance.py`
- Check: does evidence declaration reference skill_id for product work items?
- Check: do product items have transcript evidence?
- Check: do src-editing items have ledger entries?
- Tests: 5 (compliant declaration, missing skill_id, missing transcript, missing ledger, non-product exempt)

### Task 4: Stream-Specific Supervisor Output
- When autonomous-cycle runs for Skills stream, tag outputs with stream identifier
- Prevent Skills evidence from being overwritten by next Mainstream run
- Option A: Write to reports/supervisor/skills/ subdirectory
- Option B: Prefix files with stream name
- Tests: stream detection in autonomous_cycle.py

### Task 5: Registry Promotion Decision
- Re-evaluate deferred skills (record-lane-execution, check-mcp-status)
- If still no demand, keep deferred with updated rationale
- If demand exists (e.g., multi-lane R107 proved lane tracking value), promote to active

## Hard Quota
- 1 grade_item transcript boost with 5 tests
- 1 adoption compliance validator with 5 tests
- 1 LIVE handoff proof (or validated simulation)
- Stream output tagging
- Registry promotion decision

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
