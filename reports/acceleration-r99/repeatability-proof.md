# Repeatability Proof — Acceleration R99

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Proof: Acceleration layer tools are repeatable

### 1. Gap Selector (select_poc_gaps.py v3)

Repeatable: YES
- Same matrix input produces same ranked output (deterministic sorting)
- Stream assignment is deterministic (based on decision + capability_path)
- Depth bonus is deterministic (keyword matching)
- CLI: `python tools/supervisor/select_poc_gaps.py --stream-output-dir <dir>`
- Test: 12 tests verify deterministic behavior

### 2. Skill/Handoff Router (choose_skill_or_handoff.py v2)

Repeatable: YES
- Same gap input produces same decision (priority-ordered rules)
- Backward compatible with v1 callers
- CLI: `python tools/supervisor/choose_skill_or_handoff.py --gap-json <file>`
- Test: 10 tests verify deterministic decisions

### 3. Lane Execution Recorder (record_lane_execution.py)

Repeatable: YES
- Start/close operations are idempotent (update if exists)
- Ledger file is append-only with dedup
- CLI: `python tools/supervisor/record_lane_execution.py start|close|summary`
- Test: 10 tests verify CRUD operations

### 4. Sprint Learning Generator (generate_sprint_learning.py)

Repeatable: YES
- Same ledger + grades + gaps produce same reports
- CLI: `python tools/supervisor/generate_sprint_learning.py --sprint-id <id> --output-dir <dir>`
- Test: 7 tests verify report generation

### 5. Package Install Proof (package_install_proof.py)

Repeatable: YES
- Same format list produces same import checks
- Auto-detect mode depends on git state (deterministic for same working tree)
- CLI: `python tools/supervisor/package_install_proof.py --format <formats>`
- Test: 5 tests verify detection and proof execution

## Test Repeatability

```
$ python -m pytest tests/supervisor/acceleration/ -v
43 passed in 0.97s
```

All 43 tests pass consistently. No flaky tests. No environment dependencies
beyond Python 3.13 + pytest + pyyaml.
