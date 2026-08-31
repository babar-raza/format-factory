# 01 — Product Definition

**Baseline commit:** dd909cf3a
**Evidence:** Direct file reading + package installation experiments

## What Format Factory Is
Format Factory is a repository intended to produce independently publishable format-conversion libraries. It has two product generations:

- **Gen-1 (legacy):** ~21 Python packages with flat layout (e.g., `src/python/fods/fods/`). Bare imports (`import fods`). Published as individual PyPI packages. Targets Python >=3.9.
- **Gen-2 (current mission):** 7 Python packages (core + 6 formats) using PEP 420 namespace packages under `format_factory.*`. Targets Python >=3.11. Distribution via `format-factory-{format}` wheel packages.

## FF6 Mission Scope
Goal ID: FF6-PRODUCTION-LIBRARIES-001 — produce 6 certified Python libraries.

## Current Product Matrix

| Format | Package | Version | Py ver | Declared namespace | Actual namespace | Match? | Source .py | Test files | Obligations | Evidence entries | Real certification |
|--------|---------|---------|--------|-------------------|-----------------|--------|-----------|------------|-------------|-----------------|-------------------|
| ipynb | format-factory-ipynb | 0.2.0.dev0 | >=3.11 | format_factory.ipynb | format_factory.ipynb | YES | 32 | 41 | 68 | 68 | NOT CERTIFIED |
| ora | format-factory-ora | 0.1.0.dev0 | >=3.11 | format_factory.openraster | format_factory.ora | **NO** | 16 | 24 | 134 | 134 | NOT CERTIFIED |
| nrrd | format-factory-nrrd | 0.2.0.dev0 | >=3.11 | format_factory.nrrd | format_factory.nrrd | YES | 24 | 53 | 65 | 65 | NOT CERTIFIED |
| xliff | format-factory-xliff | 0.2.0.dev0 | >=3.11 | format_factory.xliff | format_factory.xliff | YES | 25 | 54 | 142 | 142 | NOT CERTIFIED |
| safetensors | format-factory-safetensors | 0.2.0.dev0 | >=3.11 | format_factory.safetensors | format_factory.safetensors | YES | 22 | 29 | 86 | 86 | NOT CERTIFIED |
| ubl | format-factory-ubl | 0.2.0.dev0 | >=3.11 | format_factory.ubl | format_factory.ubl | YES | 44 | 71 | 195 | 195 | NOT CERTIFIED |

**Real certification is NOT CERTIFIED for all six formats.** The promotion labels in controller-state.yaml (4/6 CERTIFIED) are contradicted by the same file's truth_boundary ("0/6 technically certified"), production_certifications (0), and explicit directive ("Do not claim certification for any format").

## Supporting Distribution
- **format-factory-core** (0.1.0.dev0, >=3.11): Shared primitives (CheckedArithmeticError, diagnostics, error hierarchy, resource limits, XML security, IO protocols). Zero runtime dependencies.

## What "Certified" Means (per source)

### product-goal.yaml (normative definition)
Certification requires ALL simultaneously:
1. Every stable normative obligation classified, implemented, and proven
2. Every capability meets production standard
3. No mandatory obligation satisfied by filename, test count, or prose deferral
4. Passes: installed-wheel, independent-oracle, corpus, security, resource, typing, docs, compatibility, performance, reproducible-build gates
5. Extracts to independent repository with preserved canonical source
6. All six co-install without collisions
7. Certification computed from current proof; publication requires external authority

### goal_driver.py (mechanical implementation)
`promotion.get(format_id) == "CERTIFIED"` — reads a string label from controller-state.yaml. Does NOT verify any of the above requirements. PROVEN: setting all 6 strings to CERTIFIED causes GOAL_ACHIEVED exit code 0, regardless of test state, evidence freshness, or proof chains.

### controller-state.yaml invariant (line 291)
"Product promotion is computed from current proof and cannot be edited here." — this invariant is violated by the current state where promotion strings ARE manually edited labels.

## Evidence Classification
- Product matrix: PROVEN (files read and verified)
- ORA namespace mismatch: PROVEN (product-goal.yaml vs pyproject.toml vs directory structure)
- False certification vulnerability: PROVEN (experiment in worktree — set all 6 to CERTIFIED -> GOAL_ACHIEVED)
- Real certification status (0/6): PROVEN (truth_boundary, production_certifications, explicit directive all agree)
