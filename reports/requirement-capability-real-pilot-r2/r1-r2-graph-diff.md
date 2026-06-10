# R1 vs R2 Graph Diff
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## Key Changes

### FODT spec source upgraded
- R1: spec:fodt:fixture (FIXTURE_BACKED)
- R2: spec:fodt:r3 (ACCEPTED_WITH_CAVEAT, ODF 1.3 scoped, Spec R3)
- Impact: FODT requirements now derived from real spec source, not fixture

### Architecture-blocked claim metadata corrected
- R1: blocked_reason='No standalone target writer library...' (generic string)
- R2: blocked_reason='architecture_blocked_missing_target_writer' (canonical value)
- R2: coverage_status='ARCHITECTURE_BLOCKED_MISSING_TARGET_WRITER' (explicit field)
- Impact: Gap queue generator correctly detects and routes these claims

### Gap queue routing fixed
- R1: FODS/FODT blocked exports → Mainstream-Dogfood (WRONG)
- R2: FODS/FODT blocked exports → Target-Writer-Architecture (CORRECT)

### Node/edge count change
- R1: 81 nodes, 102 edges
- R2: 70 nodes, 103 edges
