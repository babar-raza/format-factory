# Skills R100 — Skill System Gap Analysis
Sprint: FORMAT-FACTORY-SKILLS-R100-GOVERNED-EXECUTION-DEEP-SKILL-SYSTEM-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Category 1: Missing Registry Entries (5 skills)

| Skill | Type | Command File Exists | Action |
|-------|------|-------------------|--------|
| materialize-declaration-review | Supervisor tool | NO | Register as draft |
| record-lane-execution | Supervisor tool | NO | Register as draft |
| build-context-pack | Supervisor tool | NO | Register as draft |
| check-mcp-status | Supervisor tool | NO | Register as draft |
| select-poc-gap | Supervisor tool | NO | Register as draft |

These are Python scripts in tools/supervisor/ — not Claude commands. They should be registered with `status: draft` and `product_track: planning` to acknowledge them without claiming they are ready for governed invocation.

## Category 2: Ledger Data Quality (fixed in preflight)

| Issue | Count | Severity | Fixed |
|-------|-------|----------|-------|
| placeholder SHA-256 hashes | 10 entries | HIGH | YES |
| state:modified (invalid) | 1 entry | HIGH | YES |
| Stale hashes for modified files | 3 files | HIGH | YES |

## Category 3: Command File Gaps

| Gap | Affected Commands | Count |
|-----|-------------------|-------|
| Missing frontmatter | plan-hardening, execution-handoff, evidence-review-next-prompt, memory-sprint, export-plan-context | 5 (legacy commands, not product skills) |
| Missing sample invocation | 10 commands | 10 |
| Missing rollback section | 7 commands (pre-R99) | 7 |
| Missing transcript output | all 18 | 18 |

Note: R99 added frontmatter + rollback to 6 commands. The remaining gaps are in legacy planning commands that are not governed product skills.

## Category 4: Schema Gaps

| Gap | Description |
|-----|-------------|
| No negative test coverage | Validator has no test suite |
| No transcript schema | Transcript format defined in R99 but no JSON Schema |
| No ledger-to-transcript link | Ledger entries reference skills but not transcript IDs |

## Priority Actions for R100

1. Register 5 missing supervisor skills as draft
2. Add negative tests to registry validator
3. Create transcript validator with tests
4. Harden ledger validator (transcript linkage)
5. Multi-skill dry-run proof (6 skills)
6. Controlled governed flow with real evidence
