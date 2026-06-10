# Supervisor Hard-Stop Reclassification Policy

## Signal Classes and Actions

| Signal | Reclassification | Action |
|--------|-----------------|--------|
| evidence_quality_zero | LOCAL_REPAIR_CONTINUE | Build missing artifacts, continue |
| prompt_quality_failure | LOCAL_REPAIR_CONTINUE | Repair prompt sections, continue |
| missing_sample_outputs | LOCAL_REPAIR_CONTINUE | Generate sample outputs, continue |
| wrong_stream_next_sprint | LOCAL_REPAIR_CONTINUE | Strip boundary section, continue |
| anti_skip_false_positive | SUPERVISOR_FALSE_STOP_ROUTED | Archive, continue |
| missing_evidence_artifact | LOCAL_REPAIR_CONTINUE | Create artifact, continue |
| ACCEPTED_WITH_REWORK | REWORK_THEN_CONTINUE | Fix items, rerun cycle, continue |
| autonomous_continue=false | INSPECT_REASON | If local/evidence/prompt → continue |
| credentials_required | STOP_EXTERNAL_GATE | Hard stop |
| push_required | STOP_EXTERNAL_GATE | Hard stop |
| Gate_8_or_11 | STOP_EXTERNAL_GATE | Hard stop |
| source_corruption | STOP_UNSAFE_WORKSPACE | Hard stop |
| repeated_foundational_failure_3x | STOP_UNSAFE_WORKSPACE | Hard stop |

## Hard Invariants

- Supervisor ACCEPTED is NOT terminal by itself.
- Evidence package created is NOT terminal by itself.
- One iteration complete is NOT terminal by itself.
- max_iterations reached is a CHECKPOINT_ROLLOVER, not a stop.
- CONTINUE_NEXT_ITERATION is the default when no terminal criterion is met.
