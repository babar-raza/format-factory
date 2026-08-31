# 11 — ORA Proof Chain Trace

**Baseline commit:** dd909cf3a
**Evidence:** Source code reading + import experiments + grep analysis

## Namespace Disagreement Summary

The ORA format has a systemic namespace mismatch between the mission declaration and reality:

| Source | Distribution name | Import namespace | Format ID |
|--------|------------------|-----------------|-----------|
| product-goal.yaml | format-factory-openraster | format_factory.openraster | ora |
| pyproject.toml (actual) | format-factory-ora | format_factory.ora | N/A |
| package-matrix.yaml | format-factory-ora | format_factory.ora | ora |
| production_program.py | N/A | N/A | ora (contract) / openraster (source_package) |
| Tests (all 24 files) | N/A | format_factory.ora | N/A |
| SAL facts | N/A | N/A | ora |
| Obligations | N/A | N/A | ora |
| controller-state.yaml | N/A | N/A | ora |

## Impact Map: Where "openraster" Appears (phantom name)

| Location | Field | Consequence |
|----------|-------|-------------|
| product-goal.yaml line 21 | distribution: format-factory-openraster | Dead data — nothing reads it |
| product-goal.yaml line 22 | import_namespace: format_factory.openraster | Dead data — nothing reads it |
| production_program.py line 112 | ProductTarget("openraster", "ora", "openraster") | source_package_id points to nonexistent src/python/openraster/ |
| product_action_guard.py lines 81, 87 | "src/python/openraster/", "tests/python/openraster/" | Guards phantom paths that don't exist |
| .supervisor/knowledge/registry.yaml line 57 | "src/python/openraster/" | References phantom path |
| execution-recovery-directive.yaml line 826 | format-factory-openraster | Uses phantom distribution name |
| autonomous execution plan lines 554, 775, 1018 | Various openraster references | Uses phantom names |
| test_production_program.py line 941 | Asserts paths include "src/python/openraster" | Tests the WRONG expectation |

## Why It Doesn't Break (Yet)

The goal_driver.py only reads `format_id` (not `distribution` or `import_namespace`) from product-goal.yaml. `format_id: ora` is correct everywhere. So:
- Obligation lookup: `obligations/ora.yaml` → EXISTS, WORKS
- Reconciliation lookup: `ora-obligation-reconciliation.json` → EXISTS, WORKS
- Promotion lookup: `promotion.ora` → EXISTS, WORKS (UNASSESSED)

The mismatch is currently DORMANT because no production code path consumes the broken fields.

## Where It WOULD Break

1. `pip install format-factory-openraster` → package not found (actual: format-factory-ora)
2. `import format_factory.openraster` → ModuleNotFoundError (PROVEN)
3. production_program.py chassis audit → looks for src/python/openraster/ → directory not found
4. Any tool that reads product-goal.yaml's import_namespace and tries to import it

## Chain Analysis

| Edge | Status | Detail |
|------|--------|--------|
| Authority → SAL facts | OK | Uses format_id: ora (correct) |
| SAL facts → Contract | OK | FC-ORA-V1, format_id: ora |
| Contract → Obligations | OK | 134 obligations, format_id: ora |
| Obligations → Evidence | Same BROKEN pattern as IPYNB | Historical snapshots, no live execution |
| Evidence → Reconciliation | Same BROKEN pattern as IPYNB | File/symbol existence only |
| Reconciliation → Promotion | Promotion is UNASSESSED (honest) | goal_driver reads format_id correctly |
| product-goal.yaml → production_program.py | BROKEN | source_package_id points to phantom directory |
| product-goal.yaml → pip install | BROKEN (untested) | Wrong distribution name |
| product-goal.yaml → import | BROKEN (PROVEN) | ModuleNotFoundError |

## Evidence Classification
- Namespace mismatch: PROVEN (file comparison + import test)
- Double mismatch (distribution + namespace): PROVEN (product-goal.yaml vs pyproject.toml)
- production_program.py phantom path: PROVEN (source code + directory nonexistence)
- Test assertion for wrong path: PROVEN (test_production_program.py line 941)
- Dormant status (no prod code consumes broken fields): PROVEN (goal_driver.py only reads format_id)
