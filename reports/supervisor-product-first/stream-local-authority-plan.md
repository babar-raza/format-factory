# Stream-Local Authority Plan

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Authority Model

Each stream has a local `reports/supervisor-streams/{stream}/` directory.
The global `reports/supervisor/` directory is advisory reference.

## Per-Stream Authority Verification

| Stream | Stream-Local Dir | Authority File | Status |
|--------|-----------------|---------------|--------|
| supervisor | reports/supervisor-streams/supervisor/ | authority-map.json | STREAM_LOCAL |
| mainstream | reports/supervisor-streams/mainstream/ | authority-map.json | TBD |
| acceleration | reports/supervisor-streams/acceleration/ | authority-map.json | TBD |
| skills | reports/supervisor-streams/skills/ | authority-map.json | TBD |

## Supervisor Stream Authority

From `reports/supervisor-streams/supervisor/authority-map.json`:
- `"authority": "STREAM_LOCAL"`
- `"global_status": "ADVISORY_REFERENCE"`

## Authority Rules

1. Stream-local evidence review is authoritative for that stream
2. Global supervisor outputs are advisory reference
3. No cross-stream authority — stream A cannot override stream B's verdict
4. Human gates (1-11) override all stream-local decisions
