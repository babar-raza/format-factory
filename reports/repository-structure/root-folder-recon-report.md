# Root Folder Reconnaissance Report

**Mission:** Repository root folder forensic reconnaissance, governance, and idempotency verification
**Date:** 2026-06-29
**Branch:** main
**HEAD:** 8acdcd8a
**Plan:** plans/.claude/idempotent-snuggling-wombat.md (TC-ROOT-001 through TC-ROOT-007)

---

## Repository Baseline

| Metric | Before | After |
|---|---|---|
| Top-level directories | 51 | 48 (3 deleted, 2 consolidated) |
| Directories with README | 9 | 36 |
| Directories without README (RETAIN) | 42 | 0 |
| Directories without README (EXEMPT) | 0 | 12 |
| Registry entries | 0 | 51 (original census preserved) |
| Format-scoped folders audited | 0 | 11 |
| Governance validator | none | V91 (blocks_sprint=True for unregistered dirs) |
| Regression tests | 0 | 7 |

---

## Folder Summary Table

### CORE_PRODUCT (5 folders)

| Folder | Classification | README | Format Scoped | Retention |
|---|---|---|---|---|
| `src/` | CORE_PRODUCT | README.md | Yes | RETAIN |
| `tests/` | CORE_PRODUCT | _readme.md | Yes | RETAIN |
| `samples/` | CORE_PRODUCT | README.md | Yes | RETAIN |
| `oracle/` | CORE_PRODUCT | README.md | Yes | RETAIN |
| `examples/` | CORE_PRODUCT | README.md | Yes | RETAIN |

### GOVERNANCE_INFRA (10 folders)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `.claude/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `.github/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `.governance/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `.hooks/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `.supervisor/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `plans/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `registry/` | GOVERNANCE_INFRA | README.md | RETAIN |
| `reports/` | GOVERNANCE_INFRA | _readme.md | RETAIN |
| `schemas/` | GOVERNANCE_INFRA | _readme.md | RETAIN |
| `tools/` | GOVERNANCE_INFRA | _readme.md | RETAIN |

### DOCUMENTATION (6 folders)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `docs/` | DOCUMENTATION | README.md | RETAIN |
| `memory/` | DOCUMENTATION | README.md | RETAIN |
| `taskcards/` | DOCUMENTATION | README.md | RETAIN |
| `reviews/` | DOCUMENTATION | _readme.md | RETAIN |
| `templates/` | DOCUMENTATION | _readme.md | RETAIN |
| `playbooks/` | DOCUMENTATION | _readme.md | RETAIN |

### PIPELINE_ARTIFACT (9 folders)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `acquisition-packs/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `migration-maps/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `product-capability-matrix/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `generated-requirements/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `gate-readiness/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `publication-readiness/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `release-manifests/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `packaging/` | PIPELINE_ARTIFACT | _readme.md | RETAIN |
| `requirements-authority/` | PIPELINE_ARTIFACT | README.md | RETAIN |

### SHARED_LIBRARY (3 folders)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `shared/` | SHARED_LIBRARY | _readme.md | RETAIN |
| `scripts/` | SHARED_LIBRARY | _readme.md | RETAIN |
| `drivers/` | SHARED_LIBRARY | _readme.md | RETAIN |

### STATE_TRACKING (1 folder)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `dependency-artifacts/` | STATE_TRACKING | README.md | RETAIN |

### HISTORICAL_REQUIRED (1 folder)

| Folder | Classification | README | Retention |
|---|---|---|---|
| `prototypes/` | HISTORICAL_REQUIRED | _readme.md | RETAIN |

### EXEMPT (13 folders, no README required)

| Folder | Classification | Reason |
|---|---|---|
| `.git/` | PLATFORM_MANAGED | Git internals |
| `.venv/` | PLATFORM_MANAGED | Gitignored virtualenv |
| `.vscode/` | PLATFORM_MANAGED | IDE settings |
| `.kilo/` | PLATFORM_MANAGED | Node tool metadata |
| `.benchmarks/` | EPHEMERAL_CACHE | Benchmark cache |
| `.hypothesis/` | EPHEMERAL_CACHE | Hypothesis PBT cache |
| `.mypy_cache/` | EPHEMERAL_CACHE | MyPy cache |
| `.pytest_cache/` | EPHEMERAL_CACHE | Pytest cache |
| `.ruff_cache/` | EPHEMERAL_CACHE | Ruff linter cache |
| `build/` | EPHEMERAL_CACHE | Build artifacts |
| `.local/` | LOCAL_RUNTIME | Runtime state |
| `bundle-metadata/` | EPHEMERAL_CACHE | Sprint bundle staging |
| `evidence-bundles/` | EPHEMERAL_CACHE | Evidence ZIP staging |

### DELETED (3 folders removed in TC-ROOT-002)

| Folder | Disposition | Evidence |
|---|---|---|
| `state/` | DELETED | Redundant with `.supervisor/state/`. 2 files, 27 days stale. Zero active consumers. |
| `skills/` | RELOCATED to `docs/procedures/` | 1 file. Redundant with `.supervisor/skill-registry.yaml`. Zero tool references. |
| `examples-docs-readiness/` | CONSOLIDATED into `examples/` | 1 file (summary.yaml). R83 snapshot. Zero tool references. |

### Stale subdirectories removed (TC-ROOT-002)

| Path | Evidence |
|---|---|
| `shared/generation-rules/` | 2 files. Zero tool references across entire codebase. |
| `shared/spec-manifests/` | 1 file. Zero tool references across entire codebase. |

---

## Format Coverage Matrix

11 format-scoped folders audited against `registry/format-registry.yaml` (25 formats).

| Folder | Basis | Eligible | Present | Missing | Verdict |
|---|---|---|---|---|---|
| `src/python/` | Python products | 20 | 20 | 0 | COMPLETE |
| `src/net/` | .NET products | 6 | 6 | 0 | COMPLETE |
| `tests/python/` | Mirrors src/python | 20 | 20 | 0 | COMPLETE |
| `tests/net/` | Mirrors src/net | 6 | 6 | 0 | COMPLETE |
| `samples/by-format/` | All with samples | 22 | 22 | 0 | COMPLETE |
| `oracle/formats/` | All with products | 20 | 20 | 0 | COMPLETE |
| `examples/python/` | Mirrors src/python | 20 | 20 | 0 | COMPLETE |
| `examples/net/` | Mirrors src/net | 6 | 6 | 0 | COMPLETE |
| `acquisition-packs/` | All registered | 24 | 22 | 2 | MINOR_GAPS |
| `migration-maps/` | All with QName maps | 20 | 20 | 0 | COMPLETE |
| `prototypes/by-format/` | Prototype formats | 7 | 7 | 0 | COMPLETE |

**Minor gaps:** acquisition-packs missing ndjson and toml (NOT_YET_ONBOARDED — have product source but no acquisition pack).

**Valid global exclusions (5):** odf-shared (infrastructure), ora/pam/xpm/zpaq (OBLIGATION_CREATED, no product source).

**Overall verdict:** COMPLETE_WITH_DOCUMENTED_EXCLUSIONS

Full audit: `reports/repository-structure/format-folder-coverage.yaml`

---

## README Backfill Log

**Preserved (9 existing READMEs, no changes):**
- `.pytest_cache/README.md` (platform-generated)
- `dependency-artifacts/README.md`
- `memory/README.md`
- `requirements-authority/README.md`
- `prototypes/_readme.md`
- `reports/_readme.md`
- `schemas/_readme.md`
- `tests/_readme.md`
- `tools/_readme.md`

**Created (~27 new READMEs):**
- Template A (_readme.md, directory orientation): `acquisition-packs`, `migration-maps`, `product-capability-matrix`, `generated-requirements`, `gate-readiness`, `publication-readiness`, `release-manifests`, `packaging`, `shared`, `scripts`, `drivers`, `reviews`, `templates`, `playbooks`
- Template B (README.md, operational): `src`, `oracle`, `samples`, `examples`, `docs`, `plans`, `registry`, `taskcards`, `.claude`, `.github`, `.governance`, `.hooks`, `.supervisor`

**Convention:** `_readme.md` for directory-orientation docs (internal/reference); `README.md` for operational authority docs (core/governance).

**Result:** 0 RETAIN folders missing README. All 12 folders without README are EXEMPT.

---

## Governance System

| Component | Path | Purpose |
|---|---|---|
| Root folder registry | `registry/repository-root-folders.yaml` | Canonical catalog of all 51 directories |
| Format coverage audit | `reports/repository-structure/format-folder-coverage.yaml` | Coverage matrix for 11 format-scoped folders |
| V91 root structure validator | `tools/supervisor/governance_validators_root_struct.py` | Enforces registry, README, resurrection, coverage checks |
| Governance runner integration | `tools/supervisor/governance_validator_runner.py` | V91 runs on every sprint closeout |
| Regression tests | `tests/supervisor/test_validate_root_structure.py` | 7 test cases (all PASS) |
| This report | `reports/repository-structure/root-folder-recon-report.md` | Final audit trail |

**Validator behavior:**
- FAIL + blocks_sprint=True for unregistered top-level directories
- WARN for missing READMEs on RETAIN folders
- WARN for resurrected DELETED folders
- WARN for format coverage gaps (MAJOR_GAP verdict)

**Agent discoverability:** Agents locate folders via `registry/repository-root-folders.yaml`. Each entry contains `purpose`, `classification`, `producers`, `consumers`, and `readme_convention` — sufficient for any agent to determine where files belong without prior session memory.

---

## Idempotency Verification

**Run 1:** V91 returns PASS (0 FAIL, 0 WARN, 51 registered folders)
**Run 2:** V91 returns PASS (0 FAIL, 0 WARN, 51 registered folders) — identical

README re-generation: all files already exist, zero changes on second pass.
Format coverage re-audit: identical YAML output on second run.

---

## Final Verdict

`ROOT_FOLDERS_RECONCILED_DOCUMENTED_GOVERNED_AND_IDEMPOTENT`

- All 48 active directories registered (51 census entries including 3 DELETED)
- All 36 RETAIN folders have READMEs (12 EXEMPT folders correctly excluded)
- 11 format-scoped folders audited with documented exclusions
- V91 validator integrated and returning PASS
- 7 regression tests passing
- Second run produces zero material changes
