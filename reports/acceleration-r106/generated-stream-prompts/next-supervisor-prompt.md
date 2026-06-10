# Supervisor R106 Sprint Prompt

## Sprint ID
FORMAT-FACTORY-SUPERVISOR-R106-PIPELINE-QUALITY-AND-CONTINUATION-HARDENING-001

## Mission
Harden the supervisor pipeline quality checks and continuation signal logic.

## Lane A: Continuation State Hardening
- Add new continuation states for R106 anti-skip expansion
- Test continuation classification with evidence quality violations

## Lane B: Grading Engine Hardening
- Ensure evidence_quality_score is reflected in next-sprint prompt generation
- Add grading engine tests for edge cases

## Lane C: Evidence Review Enrichment
- Include anti-skip results in evidence-review.md output
- Include evidence quality score in evidence-review.json

## Evidence Closeout
Write evidence-declaration.yaml and run autonomous-cycle.

## File Boundaries
- ALLOWED: tools/supervisor/*, tests/supervisor/*
- FORBIDDEN: src/net/*, src/python/*
