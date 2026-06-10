# Stream Isolation Repair (Skills R103 Wave 4)

## Problem

Supervisor outputs reference wrong streams:
- `evidence-review.md` reviews Supervisor R103, not Skills R103
- `contradictions.md` reviews Supervisor R103, not Skills R103
- `next-sprint.md` is mainstream stream, not skills
- `selected-product-gaps.json` contains stale R98 data

## Root Cause

The supervisor autonomous-cycle generates these outputs from the last declaration processed. The Skills R102 declaration ran through the supervisor, but a subsequent Supervisor R103 autonomous-cycle overwrote the outputs. The supervisor loop is stream-unaware — it always overwrites the same files regardless of stream.

## Stream Isolation Analysis

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| context-pack latest_sprint.run_id | skills-r102 or skills-r103 | R102 | PARTIAL (correct run but no stream tag) |
| evidence-review sprint_id | Skills R103 | Supervisor R103 | FAIL (wrong stream) |
| contradictions sprint_id | Skills R103 | Supervisor R103 | FAIL (wrong stream) |
| next-sprint.md stream | skills | mainstream | FAIL (wrong stream) |
| selected-product-gaps.json | current | stale R98 | STALE |

## Skills-Only Next Prompt

The skills stream generates its own next prompt at `reports/skills-r103/next-skills-agent-prompt.md` which is stream-isolated. The supervisor's `next-sprint.md` is a mainstream concern and should not be consumed by the skills stream.

## Wrong-Stream Prompt Detection

If a skills agent consumed `reports/supervisor/next-sprint.md`, it would receive mainstream product tasks. This is detectable by checking:
1. The `# Stream:` header in next-sprint.md — currently says "mainstream"
2. The sprint ID references — currently references acceleration/supervisor, not skills
3. Task content — contains product implementation tasks, not skill governance

## Mitigation

R103 produces its own stream-isolated outputs:
- `reports/skills-r103/next-skills-agent-prompt.md` (skills-only)
- `reports/skills-r103/three-sprint-forecast.md` (skills-only)
- All validator results under `reports/skills-r103/validator-results/`
- All transcripts under `reports/skills-r103/skill-transcripts/`

The supervisor's `reports/supervisor/` files remain cross-stream contaminated. This is a supervisor infrastructure limitation, not a skills stream defect.

## Recommendation for R104

Add a `stream` field to the evidence declaration schema so the supervisor can generate stream-specific outputs (e.g., `reports/supervisor/skills/next-sprint.md`).
