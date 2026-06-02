---
sprint: R91
generated_by: r91-worker
---

# Python Netpbm Reduced FOSS Product Hardening

## Summary

Python Netpbm R91 hardening adds an installed-package example demonstrating the PPM→PGM dogfood export path. The PPM→PGM dogfood export itself was added in R90. R91 adds the installed workflow example via the `/add-installed-package-example` governed skill.

## R90 Baseline: PPM→PGM Dogfood Export

Already implemented in R90:
- `src/python/ppm/ppm_to_pgm.py` — conversion function
- 5 passing tests in `tests/python/ppm/test_r90_ppm_to_pgm.py`
- Dogfood status: IMPLEMENTED

No changes to R90 PPM→PGM work in R91.

## R91 Addition: Installed Package Example

Skill used: `/add-installed-package-example`

File created: `examples/python/ppm/installed_workflow.py`

Content demonstrates:
1. Importing `parse_ppm_strict` from the installed `ppm` package
2. Parsing a PPM image from bytes
3. Converting to PGM using `ppm_to_pgm`
4. Writing the output PGM file

The example uses only the public API surface — no internal imports, no PYTHONPATH manipulation.

## Tests: Installed Package Smoke

Test file: `tests/python/ppm/test_r91_installed_example.py`

Tests:
1. `test_installed_example_imports_work` — verifies `from ppm import parse_ppm_strict, ppm_to_pgm` succeeds from installed package path
2. `test_installed_example_runs_without_error` — runs the installed_workflow.py example as a subprocess and verifies exit code 0

Both tests pass.

## FOSS Matrix Update

`product-capability-matrix/foss-matrix.yaml` updated for Python Netpbm:

```yaml
ppm:
  gate_status: gate_10_local_rc_ready
  dogfood_status: IMPLEMENTED
  dogfood_path: ppm_to_pgm
  installed_package_example: true
  installed_example_path: examples/python/ppm/installed_workflow.py
  r91_hardening: complete
```

## Evidence Artifacts

- `examples/python/ppm/installed_workflow.py` — installed workflow example
- `tests/python/ppm/test_r91_installed_example.py` — 2 passing smoke tests
- `product-capability-matrix/foss-matrix.yaml` — updated entry
