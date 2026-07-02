# /select-deepening-lane

Select the next product-deepening lane for a format from the dual-lane ledger.

## What This Command Does

1. Loads `registry/product-deepening-ledger.yaml`.
2. Reads the format's `execution_mode`, lane maturity, DOM applicability, and starvation counters.
3. Returns the selected lane: `feature`, `dom`, or both for `PARALLEL`.
4. Reports the selection reason and any starvation warning.

## Command

```powershell
python tools/supervisor/lane_selector.py --format <format-id>
```

Optional mode override:

```powershell
python tools/supervisor/lane_selector.py --format <format-id> --mode AUTO
```

Starvation-only check:

```powershell
python tools/supervisor/lane_selector.py --format <format-id> --check-starvation
```

## Inputs

- `format_id`: format key such as `fods`, `ods`, or `zst`
- optional `mode`: `FEATURE_ONLY`, `DOM_ONLY`, `SEQUENTIAL_FEATURE_THEN_DOM`, `SEQUENTIAL_DOM_THEN_FEATURE`, `PARALLEL`, `BALANCED`, or `AUTO`

## Outputs

JSON on stdout with:

- `selected_lane`
- `mode`
- `reason`
- `starvation_warning`

## Validation

```powershell
python -m pytest tests/supervisor/test_lane_selector.py tests/supervisor/test_starvation_prevention.py -q
```

## skill_id

select-deepening-lane

## Required Inputs

- `format_id` — format identifier from the format registry

## Allowed Paths

- `tools/supervisor/lane_selector.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
