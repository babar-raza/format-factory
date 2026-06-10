# POC Gap Selector v3 — Train C

Sprint: FORMAT-FACTORY-ACCELERATION-R99-PRODUCT-FACTORY-ACCELERATION-LAYER-PARALLEL-MEGA-TRAIN-001

## What Changed

### 1. Stream-aware output
- `--stream-output-dir` flag writes per-stream JSON files
- Streams: mainstream, acceleration, skills, supervisor
- Each gap assigned a `stream` field via `_classify_stream()`

### 2. Depth-priority scoring
- `_depth_bonus()` adds +10 for save/export/write/dogfood/roundtrip/package/install
- Subtracts -5 for get/count/enumerate/list/inspect
- Ensures deep product capabilities rank higher than shallow queries

### 3. Skill registry integration
- `--skill-registry` flag reads `.supervisor/skill-registry.yaml`
- `load_skill_registry()` loads and passes to `choose_skill_or_handoff()`
- Gap selection enriched by dynamic skill matching

### 4. Build payload includes streams
- `build_payload()` returns `streams` dict with counts per stream
- `split_by_stream()` utility for downstream consumers

## Test Results

- 12 new tests in `test_select_poc_gaps_v3.py`
- All pass (depth bonus, stream classification, split, registry, ranking)

## CLI Proof

```
$ python tools/supervisor/select_poc_gaps.py --stream-output-dir .local/supervisor/streams
SELECTED_PRODUCT_GAPS: 14
STREAMS: {'mainstream': 8, 'acceleration': 0, 'skills': 0, 'supervisor': 6}
```
