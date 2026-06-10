# Cross-Stream Dependency Map

## Skills Dependencies on Other Streams
| Dependency | Source Stream | Type | Status |
|-----------|--------------|------|--------|
| autonomous_cycle.py | supervisor | shared infrastructure | Skills modifies, all consume |
| skill-registry.yaml | skills | owned | Authoritative |
| validate_skill_transcript.py | skills | owned | Authoritative |
| validate_adoption_compliance.py | skills | owned | Authoritative |
| anti_skip_checker.py | supervisor | shared infrastructure | Read-only by Skills |
| grade_declared_work.py | supervisor | shared infrastructure | Read-only by Skills |
| generate_next_worker_prompt.py | supervisor | shared infrastructure | Read-only by Skills |

## Other Streams' Dependencies on Skills
| Consumer Stream | Dependency | Type |
|----------------|-----------|------|
| mainstream | skill-registry.yaml | skill lookup |
| mainstream | validate_skill_transcript.py | transcript validation |
| acceleration | skill-registry.yaml | skill lookup |
| acceleration | validate_adoption_compliance.py | adoption check |
| supervisor | skill-registry.yaml | registry status |

## Unresolved Dependencies
- Skills modifies autonomous_cycle.py which is supervisor infrastructure
- Changes to classify_continuation_state() affect all streams
- Receiver fixtures are stream-specific but format is shared

## Deliverable
- `reports/skills-r113/cross-stream-dependency-map.json` — machine-readable dependency edges
