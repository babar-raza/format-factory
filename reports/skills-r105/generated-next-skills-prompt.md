# Next Skills Agent Prompt (R106)

## MODE: SKILLS STREAM — PIPELINE INTEGRATION AND ENFORCEMENT GATES

## Sprint ID
FORMAT-FACTORY-SKILLS-R106-PIPELINE-INTEGRATION-AND-ENFORCEMENT-GATES-001

## Stream: skills (NOT mainstream, NOT supervisor, NOT acceleration)

## Read First
1. `reports/skills-r105/transcript-grading-integration.md`
2. `reports/skills-r105/cross-stream-adoption-enforcement.md`
3. `reports/skills-r105/skill-registry-hardening.md`
4. `reports/skills-r105/r104-work-item-regrading.md`
5. `reports/skills-r105/stream-state-isolation.md`
6. `.supervisor/skill-registry.yaml`
7. `tools/supervisor/grade_declared_work.py`
8. `tools/supervisor/validate_skill_transcript.py`

## R105 Carry-Forward
- Transcript grading integration: rules tested but not yet in grade_declared_work.py
- Stream-state contamination: documented but not fixed (infra limitation)
- 4 orphan commands: deferred, can register if demand arises
- 2 draft skills: record-lane-execution, check-mcp-status

## Tasks

### Task 1: Integrate Transcript Validation into grade_declared_work.py
- Add skill_id awareness to `grade_item()` function
- When work item has transcript JSON in evidence_paths, validate it
- Apply the decision matrix from `transcript-grade-matrix.json`
- Tests: 3 integration tests (missing transcript, invalid transcript, valid transcript)

### Task 2: Hard Enforcement Gates for Mainstream
- Mainstream product sprints MUST reference skill_id in work items
- If skill_id present but no valid transcript: grade as OVERCLAIMED (hard gate)
- Add this to autonomous-cycle pre-check or grading pipeline

### Task 3: Execute 2 LIVE Handoffs via Mainstream Delegation
- Produce LIVE-ready handoffs for FODS RenameSheet and Netpbm ExtractChannel
- Validate handoff completeness
- Mainstream executes and produces LIVE transcripts
- Skills validates the returned transcripts

### Task 4: Convert 2 More Orphan Commands
- Candidates: execution-handoff, export-plan-context
- Register in skill-registry.yaml with active status

### Task 5: Stream-Specific Supervisor Outputs
- Add `stream` field to evidence declaration schema
- Modify autonomous_cycle.py to check stream field
- Generate stream-specific paths for next-sprint.md

## Hard Quota
- 1 grade_declared_work.py integration with 3 tests
- 1 enforcement gate proven
- 2 LIVE-ready handoffs validated
- 2 orphan commands converted
- Stream-specific output proof

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
