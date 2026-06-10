# Adoption Enforcement Campaign (Skills R104 Wave 1)

## Purpose

R103 produced conceptual adoption proofs. R104 converts these into enforceable YAML packages that each stream MUST consume.

## Enforcement Packages Produced

| Package | Stream | File | Rules | Enforcement Level |
|---------|--------|------|-------|-------------------|
| mainstream-enforcement-r104 | Mainstream | `adoption-enforcement/mainstream-enforcement.yaml` | 4 | required |
| supervisor-enforcement-r104 | Supervisor | `adoption-enforcement/supervisor-enforcement.yaml` | 4 | required + recommended |
| acceleration-enforcement-r104 | Acceleration | `adoption-enforcement/acceleration-enforcement.yaml` | 4 | required |

## Key Rules Per Stream

### Mainstream (4 rules)
1. **Skill routing:** Product lanes MUST use skill_id from registry
2. **Transcript generation:** Every skill invocation produces validated transcript
3. **Ledger requirement:** LIVE src-editing skills need ledger_entry_id
4. **Handoff consumption:** Structured handoffs preferred over ad-hoc

### Supervisor (4 rules)
1. **Transcript grading:** Work items with skill_id checked for valid transcript
2. **Command validation:** Pre-sprint command file validation
3. **Registry consistency:** Active skills checked for command files
4. **Declaration skill_id field:** Optional field with mandatory validation when present

### Acceleration (4 rules)
1. **Gap-to-skill routing:** Gaps flow through governed skills
2. **Handoff generation standard:** Required fields enforced
3. **Gap selection from matrix:** No ad-hoc gap selection
4. **No direct source edits:** All source changes via mainstream

## Failure Mode Coverage

| Failure | Stream | Grade Impact |
|---------|--------|-------------|
| Missing skill_id | Mainstream | OVERCLAIMED |
| Missing transcript | Mainstream, Supervisor | OVERCLAIMED |
| Invalid transcript | Mainstream, Supervisor | OVERCLAIMED |
| Missing ledger for LIVE | Mainstream | OVERCLAIMED |
| Gap without skill route | Acceleration | OVERCLAIMED |
| Handoff missing fields | Acceleration | PARTIAL |
| Direct source edit | Acceleration | REJECTED |
| FAIL transcript result | Supervisor | PARTIAL |

## Difference from R103

R103 produced adoption-handoffs/ with conceptual YAML snippets showing how each stream *could* use skills. R104 produces adoption-enforcement/ with enforceable contracts specifying what happens when streams violate the rules (grade impact, failure reason).
