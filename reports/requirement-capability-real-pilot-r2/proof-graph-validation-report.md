# Proof Graph Validation Report
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## Result
- Is Valid: True
- Errors: 0
- Nodes: 70
- Edges: 103
- Graph Hash: adf6e1cad05c31d833f35fcc7558d98f6232336beafce9a8662dc240277b6b7c

## FODT Improvement
FODT spec input upgraded from FIXTURE_BACKED (R1) to ACCEPTED_WITH_CAVEAT Spec R3.

## Architecture-Blocked Claims
- claim:fods:export_csv: blocked_reason=architecture_blocked_missing_target_writer
- claim:fods:export_html: blocked_reason=architecture_blocked_missing_target_writer
- claim:fodt:export_markdown: blocked_reason=architecture_blocked_missing_target_writer
- claim:fodt:export_txt: blocked_reason=architecture_blocked_missing_target_writer
All have blocked_by edges to UnsupportedFeature nodes for correct gap queue routing.
