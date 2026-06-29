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
