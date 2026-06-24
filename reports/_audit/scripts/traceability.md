# Script Traceability — format-factory

Audit date: 2026-06-23

Format: Workflow/Use-case -> Script(s) -> Evidence -> Gaps

---

## W1: Autonomous Sprint Loop

**Workflow:** Agent reads session-resume.md -> checks continuation -> executes sprint -> closes out -> repeats

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Plan lock | `tools/supervisor/write_plan_lock.py` | CLAUDE.md L13-15 | Wired |
| Continuation check | `tools/supervisor/check_continuation.py` | CLAUDE.md L321 | Wired |
| Sprint execution | `tools/supervisor/sprint_executor.py run-loop` | CLAUDE.md L430 | Wired |
| Declaration validation | `tools/supervisor/sprint_executor_validate.py --repair` | CLAUDE.md L285 | Wired |
| Autonomous cycle | `tools/supervisor/supervisor_loop.py autonomous-cycle` | CLAUDE.md L294 | Wired |
| Review package | `tools/supervisor/build_declaration_review_package.py` | CLAUDE.md L308 | Wired |
| Plan terminal | `tools/supervisor/write_plan_lock.py --terminal` | CLAUDE.md L22-25 | Wired |
| Session reset | `tools/supervisor/reset_track_signal.py --track product` | CLAUDE.md L104 | Recovery tool |

**Gaps:** None — all steps have CLAUDE.md callsite evidence.

---

## W2: CI/CD Pipeline (Pull Requests)

**Workflow:** PR opened -> lint -> security scan -> layered tests -> governance smoke -> .NET build

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Lint | `ruff check src/ tests/ tools/` (external) | ci.yml L19 | Wired |
| Security | `bandit -r src/` (external) | ci.yml L30 | Wired |
| Tests | `python tools/test_runner.py --layer 3` | ci.yml L45 | Wired |
| Governance smoke | `python -c "from governance_validators import ..."` | ci.yml L63 | Wired |
| .NET build | `dotnet build` / `dotnet test` | ci.yml L73-88 | Wired |
| Coverage | `pytest --cov` + `coverage report --fail-under=85` | ci.yml L111-113 | Wired (main only) |

**Gaps:**
- `tools/test_runner.py` is the ONLY tools/ script called by CI. No other tools/ scripts are in CI.
- Governance validators are tested via Python import smoke test, not full validation run.
- Source structure validator (`tools/validators/source_structure_validator.py`) is NOT in CI directly — runs implicitly via autonomous_cycle governance chain.

---

## W3: Release Pipeline

**Workflow:** Tag push -> build wheel -> upload to PyPI

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Build | `python -m build` (external) | release.yml L30 | Wired |
| Upload | `twine upload dist/*` (external) | release.yml L37 | Wired |
| Gate 11 | Human approval (Babar Raza) | CLAUDE.md (Gate 11) | TRUE_EXTERNAL_GATE |

**Gaps:**
- `packaging/python/build-local-packages.py` is NOT used by release.yml. Release uses `python -m build` directly. Local builder is for development/testing only.

---

## W4: External Host Orchestration

**Workflow:** Manual launch -> unset CLAUDECODE -> run Claude CLI subprocess -> hard-stop enforcement

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Launch (PS1) | `scripts/start_format_factory_orchestrator.ps1` | File exists | Wired |
| Launch (CMD) | `scripts/start_format_factory_orchestrator.cmd` | File exists | Wired |
| Launch (Bash) | `scripts/autonomous_external_host.sh` | File exists | Wired |
| Core loop | `tools/supervisor/external_host_loop.py` | Called by scripts/*.ps1/sh | Wired |
| Orchestrator | `tools/supervisor/autonomous_orchestrator.py` | Called by scripts/*.cmd/ps1 | Wired |
| Hard-stop | Keywords in external_host_loop.py L76-91 | Code evidence | Enforced |

**Gaps:**
- `scripts/install_format_factory_orchestrator_task.ps1` is PROPOSAL ONLY (DryRun=true). Task Scheduler integration is not active.

---

## W5: Source Architecture Governance

**Workflow:** autonomous_cycle -> governance_validator_runner -> 63 validators -> source_structure_validator

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Runner | `tools/supervisor/governance_validator_runner.py` | Import in autonomous_cycle.py | Wired |
| Core validators | `tools/supervisor/governance_validators.py` | Imported by runner | Wired |
| Extended validators | `tools/supervisor/governance_validators_ext.py` | Imported by runner | Wired |
| Structure | `tools/validators/source_structure_validator.py` | Called by governance chain | Wired |
| Architecture | `tools/validators/validate_source_architecture.py` | Called by governance chain | Wired |
| Monolith | `tools/validators/monolith_detection_validator.py` | Called by governance chain | Wired |

**Gaps:** None — full chain is traceable.

---

## W6: Specification Authority Layer (SAL)

**Workflow:** Spec files -> parse -> index -> extract requirements -> generate facts

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Master runner | `tools/specification-authority-layer/sal_master_runner.py` | Sprint evidence | Wired |
| Parser | `tools/specification-authority-layer/spec_parser.py` | Imported | Wired |
| Indexer | `tools/specification-authority-layer/spec_indexer.py` | Imported | Wired |
| Extractor | `tools/specification-authority-layer/requirement_extractor.py` | Imported | Wired |
| Refresh | `tools/spec-cache/refresh_check.py` | autonomous_cycle.py Step 0a-refresh | Wired |

**Gaps:**
- SAL scripts are called by autonomous sprints, not by CI.
- `spec_vault_ingest.py` — unverified callsite.

---

## W7: Evidence Collection

**Workflow:** Sprint ends -> collect git state -> inventory files -> validate bundle -> package

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Git state | `tools/evidence/collect_git_state.py` | Imported by autonomous_cycle | Wired |
| File inventory | `tools/evidence/collect_file_inventory.py` | Imported by autonomous_cycle | Wired |
| Bundle validation | `tools/evidence/validate_evidence_bundle.py` | Imported by commands | Wired |
| Repo invariants | `tools/evidence/check_repo_invariants.py` | Imported by autonomous_cycle | Wired |

**Gaps:** None for core chain.

---

## W8: Prototype Development

**Workflow:** New format -> create prototype parser -> validate against samples -> graduate to src/

| Step | Script | Evidence | Status |
|------|--------|----------|--------|
| Parser proto | `prototypes/by-format/{fmt}/{fmt}_parser.py` | 8 format prototypes | Archived |
| Validation | `prototypes/by-format/{fmt}/validate_against_samples.py` | 2 validators (fods, fodt) | Archived |

**Gaps:**
- Prototypes are historical — all active formats have graduated to `src/python/`. These are reference implementations only.
- No workflow connects prototypes to production code generation.

---

## Untraced Scripts (No Callsite Found)

These scripts exist but no callsite was found in CI, CLAUDE.md, commands, or imports:

| Script | Likely Purpose | Risk if Dead |
|--------|---------------|-------------|
| tools/supervisor/build_proof_graph_iter001.py | Historical proof graph builder | LOW — safe to archive |
| tools/supervisor/build_proof_graph_iter002.py | Historical proof graph builder | LOW — safe to archive |
| tools/supervisor/build_proof_graph_iter003.py | Historical proof graph builder | LOW — safe to archive |
| tools/close_comm_gaps.py | Commercial gap closer | LOW — utility |
| tools/close_fods_fodt_ppm_gaps.py | Format gap closer | LOW — utility |
| tools/close_xcf_zst_gaps.py | Format gap closer | LOW — utility |
| tools/audit_parity_compliance.py | Parity audit | LOW — utility |
| tools/audit_qname_coverage.py | QName audit | LOW — utility |
| tools/audit_sal_to_qname.py | SAL-QName audit | LOW — utility |
| reports/repo-sharing-plan/untrack-commands-plan.sh | Plan file (not executable) | NONE — exit 0 |
