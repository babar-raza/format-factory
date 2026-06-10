# Router Deepening v3 — Train C

## Changes
- Added `classify_work_type()` function with 8 work types
- Added `WORK_TYPE_RULES` tuple mapping gap keywords to work types
- Integrated `work_type` into all decision output dicts
- Added `package-proof` skill rule

## Work Types
1. `product_source_change` — save, write, edit, add, remove, set, create
2. `test_only_change` — test, roundtrip, regression, hardening
3. `docs_examples` — example, documentation, readme, usage
4. `package_proof` — package, wheel, install, pip, sdist
5. `dogfood_export` — dogfood, export, convert
6. `supervisor_tooling` — supervisor, tooling, automation, acceleration
7. `external_gate` — gate 11, gate 8, approval, publish, credential
8. `dry_run_proof` — dry-run, dry_run, simulation, proof

## Tests
10 new tests in `test_choose_skill_or_handoff_v2.py` (20 total)
