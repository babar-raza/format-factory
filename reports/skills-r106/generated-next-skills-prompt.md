# Next Skills Agent Prompt (R107)

## MODE: SKILLS STREAM — ENFORCEMENT MATURITY AND LIVE PROOF

## Sprint ID
FORMAT-FACTORY-SKILLS-R107-ENFORCEMENT-MATURITY-AND-LIVE-PROOF-001

## Stream: skills (NOT mainstream, NOT supervisor, NOT acceleration)

## Read First
1. `reports/skills-r106/transcript-grading-integration.md`
2. `reports/skills-r106/skill-registry-maturity.md`
3. `reports/skills-r106/cross-stream-adoption-enforcement.md`
4. `reports/skills-r106/command-validator-hardening.md`
5. `reports/skills-r106/governed-handoff-proof.md`
6. `.supervisor/skill-registry.yaml`
7. `tools/supervisor/grade_declared_work.py`
8. `tools/supervisor/validate_skill_transcript.py`
9. `tools/supervisor/validate_claude_commands.py`
10. `tools/supervisor/inspect_declared_evidence.py`

## R106 Carry-Forward
- Transcript grading: 19 integration tests pass, grade_item behavior verified, inspector-level enrichment optional
- Registry: 23 active, 2 deferred, 0 orphan, 0 draft
- Validator: "deferred" status accepted in cross-reference
- Adoption enforcement: checklists + enforceable rules defined
- Handoff: 3 governed handoffs (2 from R105 + 1 new R106)
- Stream state: infrastructure limitation documented, Skills uses isolated evidence

## Tasks

### Task 1: Inspector-Level Transcript Enrichment
- Modify `inspect_declared_evidence.py` to detect transcript JSON in evidence_paths
- When found, run `validate_transcript()` and attach result to inspection
- grade_item() already handles outcomes correctly — this wires the last connection
- Tests: 3 (missing transcript in evidence, valid transcript enrichment, invalid transcript enrichment)

### Task 2: Execute First LIVE Handoff
- Mainstream must execute one of the 3 governed handoffs
- Skills validates the returned LIVE transcript
- If LIVE execution not authorized, produce a validated simulation proof
- Tests: transcript validation of LIVE transcript

### Task 3: Adoption Enforcement Validator
- Create `tools/supervisor/validate_adoption_compliance.py`
- Check: does evidence declaration reference skill_id for product work items?
- Check: do product items have transcript evidence?
- Check: do src-editing items have ledger entries?
- Tests: 5 (compliant declaration, missing skill_id, missing transcript, missing ledger, non-product exempt)

### Task 4: Registry Stability Tests
- Add tests verifying the registry at 23+ active skills, 0 draft, 0 orphan
- Test that every active skill's command file passes validation
- Test that deferred skills have deferred_reason field

### Task 5: Stream-Specific Supervisor Output
- When autonomous-cycle runs for Skills stream, tag outputs with stream identifier
- Prevent Skills evidence from being overwritten by next Mainstream run
- Tests: stream detection in autonomous_cycle.py

## Hard Quota
- 1 inspector-level transcript enrichment with 3 tests
- 1 adoption compliance validator with 5 tests
- 1 LIVE handoff proof (or validated simulation)
- Registry stability tests
- Stream output tagging

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
