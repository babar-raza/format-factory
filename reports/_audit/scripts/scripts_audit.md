# Scripts Audit — format-factory

Audit date: 2026-06-23
Audited by: Autonomous convergence loop (scripts audit mode)
Repo: `c:\Users\prora\OneDrive\Documents\GitHub\format-factory`

---

## 1. Purpose of "Scripts" in This Repo

Format-factory is a multi-format document parsing library with an autonomous
supervision system. Scripts serve three distinct roles:

1. **Autonomous Supervision Infrastructure** — The `tools/supervisor/` directory
   (164 Python files) implements a self-governing sprint loop: plan locking,
   continuation checking, evidence grading, governance validation, and work
   generation. These scripts are invoked by CLAUDE.md directives and slash
   commands, not by humans directly.

2. **CI/CD and Release** — `.github/workflows/ci.yml` and `release.yml` run
   linting (ruff, bandit), tests (pytest via `tools/test_runner.py`), governance
   smoke checks, .NET builds, and PyPI publication.

3. **Development Utilities** — Spec normalization, oracle comparisons, sample
   validation, format understanding, and one-off data repairs (`.local/*.py`).

---

## 2. Current Script Map (Folders to Responsibilities)

| Folder | Files | Responsibility |
|--------|-------|---------------|
| `tools/supervisor/` | 164 | Autonomous supervision: cycle management, continuation, governance, grading, evidence, plan locks, work generation, AI advisors |
| `tools/ai/` | 43 | AI infrastructure: control plane, retrieval, synthesis, telemetry, validators, schema, agentic runner |
| `tools/skills/` | 25 | Skill execution: format context resolver, planning bundle, replay lineage, acquisition simulator |
| `tools/specification-authority-layer/` | 22 | SAL: spec parsing, indexing, digesting, requirement extraction, fact generation |
| `tools/requirements_authority/` | 17 | Requirements: graph store, replay fixtures, staleness invalidation |
| `tools/evidence/` | 15 | Evidence collection: git state, file inventory, repo invariants, bundle validation |
| `tools/spec-normalize/` | 13 | Spec normalization: requirement packs, section indexes, citation maps |
| `tools/` (root-level) | 11 | Top-level utilities: test_runner, audit scripts, health_check, gap closers |
| `tools/oracle/` | 9 | Oracle comparison: FODS/FODT/format oracle validators |
| `tools/validators/` | 8 | Source structure: LOC/function caps, architecture, analytics bucket detection, QName |
| `tools/playbook/` | 6 | Playbook: golden case creation, diff comparison |
| `tools/backfill/` | 5 | Data backfill utilities |
| `tools/capability_layer/` | 5 | Capability management |
| `tools/spec-cache/` | 4 | Spec cache: refresh checks, acquire, index |
| `tools/spec/` | 5 | Spec generation utilities |
| `tools/traceability/` | 4 | Traceability validators |
| `tools/llm/` | 4 | LLM endpoint client and utilities |
| `scripts/` | 6 | External host orchestration: PowerShell/Bash/CMD launchers |
| `.local/` (root) | 47 | One-off development scripts (metadata creation, ledger fixes, smoke tests) |
| `prototypes/` | 11 | Format prototype parsers (ABW, FODS, FODT, FODG, FODP, Gnumeric, ZST) |
| `packaging/python/` | 1 | Local package builder (`build-local-packages.py`) |
| `examples/` | 1 | Usage example (`dogfood_csv_export.py`) |
| `drivers/python/` | 5 | Test driver templates (`.py.tmpl`, not executable) |

(Smaller tools/ subdirs with 1-3 files: `model/`, `governance/`, `fuzz/`, `format_understanding/`, `feature_compiler/`, `state/`, `taskmaster/`, `scripts/`, `review/`, `package/`, `validation/`, `testing/`, `requirements/`, `repro/`, `packaging/`)

---

## 3. Canonical Script Folders (evidence-based)

**Primary (committed, referenced by CLAUDE.md / CI):**
- `tools/` — All production tooling (380+ Python files across 32 subdirs)
- `scripts/` — External host orchestration (6 files: PS1, SH, CMD)
- `.github/workflows/` — CI/CD (2 YAML files)

**Secondary (committed, used by specific workflows):**
- `prototypes/by-format/` — Format parser prototypes (11 files)
- `packaging/python/` — Local package builds (1 file)
- `examples/` — Usage examples (1 file)
- `drivers/python/` — Test driver templates (5 `.py.tmpl` files)

**Non-canonical (not committed or development-only):**
- `.local/*.py` — 47 one-off scripts (gitignored, development debris)

---

## 4. Script Inventory Summary

| Language | Count | Locations |
|----------|-------|-----------|
| Python (.py) | ~393 | tools/ (380+), prototypes/ (11), packaging/ (1), examples/ (1) |
| PowerShell (.ps1) | 4 | scripts/ |
| Bash (.sh) | 1 | scripts/ |
| CMD (.cmd) | 1 | scripts/ |
| Python templates (.py.tmpl) | 5 | drivers/python/ |
| YAML workflows | 2 | .github/workflows/ |
| **Total (repo scripts)** | **~406** | |
| Python one-offs (.local/) | 47 | .local/ (not committed) |

---

## 5. Top Workflows Supported by Scripts

### W1: Autonomous Sprint Loop
`CLAUDE.md` → `check_continuation.py` → `sprint_executor.py` / `autonomous_cycle.py` → `supervisor_loop.py` → `governance_validator_runner.py` → `grade_declared_work.py` → `build_declaration_review_package.py` → `check_continuation.py` (repeat)

### W2: CI/CD Pipeline
`.github/workflows/ci.yml` → `ruff check` → `bandit -r` → `tools/test_runner.py --layer 3` → `governance_validators.py` (smoke) → `dotnet build/test` → `pytest --cov`

### W3: Release Pipeline
`.github/workflows/release.yml` → `python -m build` → `twine upload` (TWINE_PASSWORD secret)

### W4: Plan Management
`CLAUDE.md` → `write_plan_lock.py --plan-path <path>` → execution → `write_plan_lock.py --terminal`

### W5: External Host Orchestration
`scripts/*.ps1/.sh/.cmd` → `tools/supervisor/external_host_loop.py` / `autonomous_orchestrator.py`

### W6: Evidence Collection and Grading
`sprint_executor_validate.py --repair` → `autonomous_cycle.py --declaration` → `build_declaration_review_package.py --declaration`

### W7: Source Architecture Governance
`governance_validator_runner.py` → `governance_validators.py` (63 validators) + `governance_validators_ext.py` → `source_structure_validator.py`

### W8: Specification Authority
`tools/specification-authority-layer/sal_master_runner.py` → `spec_parser.py` → `spec_indexer.py` → `requirement_extractor.py`

---

## 6. Security and Risk Summary

### High-Risk Scripts
| Script | Risk | Evidence |
|--------|------|----------|
| `external_host_loop.py` | HIGH | subprocess.run for Claude CLI; mitigated by HARD_STOP_KEYWORDS (lines 76-91): blocks git mutations, gate approvals, package publication |
| `sprint_executor.py` | HIGH | Calls Claude CLI subprocess; headless sprint execution |
| `autonomous_orchestrator.py` | HIGH | Multi-cycle autonomous execution |
| `release.yml` | MEDIUM | Uses TWINE_PASSWORD GitHub Secret for PyPI upload |

### Credential Surface
- 4 env vars: `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY`, `PROFESSIONALIZE_BASE_URL`, `PROFESSIONALIZE_API_KEY`
- All optional; system degrades gracefully without them
- Used by: `tools/llm/endpoint_client.py` and ~15 supervisor scripts (grading, inspection)
- No hardcoded secrets found anywhere

### Safety Controls
- No `shell=True` in subprocess calls (all use argument lists)
- No `git reset --hard`, `git clean`, `shutil.rmtree` in supervisor or scripts
- `external_host_loop.py` enforces hard-stop keyword list blocking destructive operations
- `install_format_factory_orchestrator_task.ps1` defaults to DryRun=true (governance gate)
