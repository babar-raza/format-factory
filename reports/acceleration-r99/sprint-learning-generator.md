# Sprint Learning Generator — Train F

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## Tool Created

`tools/supervisor/generate_sprint_learning.py`

## Capabilities

Generates 4 learning reports from lane execution data:

1. **agent-learning-notes.md** — what was fast, slow, blocked; grade summary
2. **speed-bottlenecks.md** — total time, blocked/failed lanes, longest lanes
3. **next-agent-briefing.md** — incomplete lanes, remaining gaps, recommendations
4. **manual-process-to-skill-candidates.md** — manual patterns to automate

## Inputs

- `--lane-ledger`: lane-execution-ledger.json
- `--grades`: work-item-grades.json
- `--gaps`: selected-product-gaps.json
- `--output-dir`: where to write reports

## CLI Proof

```
$ python tools/supervisor/generate_sprint_learning.py --sprint-id R99-TEST --output-dir reports/acceleration-r99/learning-test
agent-learning-notes: reports/acceleration-r99/learning-test/agent-learning-notes.md
speed-bottlenecks: reports/acceleration-r99/learning-test/speed-bottlenecks.md
next-agent-briefing: reports/acceleration-r99/learning-test/next-agent-briefing.md
manual-process-to-skill-candidates: reports/acceleration-r99/learning-test/manual-process-to-skill-candidates.md
```

## Test Results

- 7 tests in `test_generate_sprint_learning.py`, all pass
