# /check-dom-contract

Check whether a format satisfies a machine-checkable DOM maturity contract.

## What This Command Does

1. Loads DOM contract criteria from `reports/dual-lane-deepening/dom-contracts/`.
2. Scans `src/python/<format-id>/` using AST inspection.
3. Evaluates the requested maturity level: `D2`, `D3`, `D4`, or `D5`.
4. Prints criterion-level evidence and exits non-zero when the contract is not satisfied.

## Command

```powershell
python tools/supervisor/dom_contract_checker.py --format <format-id> --level D3
```

## Inputs

- `format_id`: Python format key such as `fods` or `ods`
- `level`: `D2`, `D3`, `D4`, or `D5`

## Outputs

JSON on stdout with:

- `passed`
- `level`
- `format`
- `criteria`

## Validation

```powershell
python -m pytest tests/supervisor/test_dom_contract_checker.py -q
```

## skill_id

check-dom-contract

## Required Inputs

- `format_id` — format identifier from the format registry
- `dom_level` — depth of DOM analysis: `shallow` or `deep`

## Allowed Paths

- `tools/supervisor/dom_contract_checker.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if the DOM contract cannot be verified
- Stop if the execution would modify any file under src/

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
