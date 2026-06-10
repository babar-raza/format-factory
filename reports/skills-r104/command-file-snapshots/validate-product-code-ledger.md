---
version: "1.0"
last-updated: "2026-06-03"
created-by: skills-r104
---

# /validate-product-code-ledger

Run the product-code change ledger validator and report pass/fail results.

## Usage

Validate the product-code change ledger JSON file against actual source file SHA-256 hashes. Reports which entries match, which have drifted, and overall PASS/FAIL.

## Required Inputs

- `ledger_path`: Path to the ledger JSON file (default: `reports/r90/product-code-change-ledger.json`)

## What This Skill Does

1. Read the product-code change ledger JSON
2. For each entry, compute the current SHA-256 of the declared source file
3. Compare computed hash against the declared hash in the ledger
4. Report PASS (match), DRIFT (hash changed), or MISSING (file not found)
5. Overall verdict: PASS if all entries match, FAIL if any drift or missing

## Allowed Paths

- `tools/supervisor/validate_product_code_ledger.py` (read-only)
- `reports/r90/product-code-change-ledger.json` (read-only)
- `src/net/**` (read-only, for SHA computation)
- `src/python/**` (read-only, for SHA computation)
- `reports/skills-r*/validator-results/` (write validation results)

## Forbidden Paths

- `registry/format-registry.yaml` (no gate authority)
- `plans/master-plan.md` (no plan changes)
- Any write to `src/` directories

## Stop Conditions

- Ledger file not found
- Ledger JSON is malformed
- Validator script not found

## Evidence Output

Write validation result to `reports/skills-r{N}/validator-results/ledger-validation.json`.

## Validation

```bash
.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py --json
```

## Rollback

No state changes to roll back. This is a read-only validation tool.

## Transcript Requirement

When used as part of a sprint, record the validation result in the evidence declaration.

## Sample Invocation

```bash
.local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py --json
```

## Changelog

- v1.0 (2026-06-03): Initial command file for promotion from draft to active (Skills R104)
