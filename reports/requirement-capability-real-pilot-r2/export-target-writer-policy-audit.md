# Export Target Writer Policy Audit
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## Architecture-Blocked Export Claims

| Claim | Required Library | R1 Gap Queue Lane | R2 Gap Queue Lane | Fixed? |
|-------|-----------------|------------------|------------------|-------|
| claim:fods:export_csv | FormatFactory.Csv | Mainstream-Dogfood | Target-Writer-Architecture | YES |
| claim:fods:export_html | FormatFactory.Html | Mainstream-Dogfood | Target-Writer-Architecture | YES |
| claim:fodt:export_markdown | FormatFactory.Markdown | Mainstream-Dogfood | Target-Writer-Architecture | YES |
| claim:fodt:export_txt | FormatFactory.Txt | Mainstream-Dogfood | Target-Writer-Architecture | YES |

## Detection Method
Gap queue generator now checks:
1. `blocked_by` edge to UnsupportedFeature node (primary)
2. `blocked_reason` metadata contains 'target writer' or 'architecture_blocked'
3. `coverage_status` == 'ARCHITECTURE_BLOCKED_MISSING_TARGET_WRITER'

## Policy Enforcement
- Architecture-blocked claims → Target-Writer-Architecture lane
- next_action: 'Create missing target writer library FormatFactory.X'
- stop_conditions: 'Do NOT proceed with /add-dogfood-export until writer library exists'
- No generic 'Provide ImplementationProof' for missing-writer claims
