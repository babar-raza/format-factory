# Skills R106 Sprint Prompt

## Sprint ID
FORMAT-FACTORY-SKILLS-R106-GOVERNED-EXECUTION-AND-TRANSCRIPT-HARDENING-001

## Mission
Continue governed skill execution, transcript validation, and skill registry maintenance.

## Lane A: Skill Registry Maintenance
- Audit current 21 skills for staleness
- Add any new skills surfaced by acceleration R106

## Lane B: Transcript Validation Hardening
- Add transcript validation for new skill types
- Ensure handoff contracts are enforced

## Lane C: Cross-Stream Governance
- Verify stream boundary enforcement in skill execution
- Add governed execution tests

## Evidence Closeout
Write evidence-declaration.yaml and run autonomous-cycle.

## File Boundaries
- ALLOWED: .supervisor/skill-registry.yaml, tests/supervisor/skills/*
- FORBIDDEN: src/net/*, src/python/*
