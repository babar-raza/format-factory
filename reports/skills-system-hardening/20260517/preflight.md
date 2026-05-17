# Sprint Preflight Report
**Sprint:** FORMAT-FACTORY-SKILLS-PRD-HARDENING-001
**Date:** 2026-05-17
**Gate:** A

---

## Git State

| Item | Value |
|------|-------|
| HEAD (actual) | `0392354d61f59ec1a2080b99abf651d044cb36fc` |
| HEAD (plan pinned) | `2dcd7f869845e9c21b3de88f9776cdf9b989b74a` |
| HEAD match | MISMATCH — plan written at R19, repo now at R20+R20-evidence |
| HEAD rebaseline | **HEAD_REBASELINED_SAFE** — R20 commits touched zero sprint-owned files |
| Branch | `main` |
| Merge/rebase state | NONE |
| Consistency check | `CURRENT_STATE_CONSISTENCY: PASS` |

### R20 Commits (since plan was written)

| Commit | Message |
|--------|---------|
| `0392354` | `chore(evidence): add R20 evidence bundle with BUNDLE_VALIDATION: PASS` |
| `0d7e8c7` | `feat(acquisition): complete R20 productization train (ZST/FODP/FODG/Gnumeric/ABW source, evidence hygiene)` |

**Sprint-owned files diff (2dcd7f8..HEAD):** EMPTY — no sprint-owned files changed in R20 commits.

---

## Dirty File Classification

### R21 Pre-staged Files (NOT sprint-owned — do not touch)

These files were staged by a prior R21 sprint and exist in the git index. This sprint must NOT include them in its commit. A commit while they are staged would bundle R21 + skills-hardening work together.

**COMMIT BLOCKER:** Human must decide whether to unstage R21 files before this sprint's commit, or commit all staged work together in one commit.

| File | Status | Classification |
|------|--------|----------------|
| `acquisition-packs/fods/gate11-architecture-approval.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fods/gate11-commercial-licensing.md` | `M ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fods/gate11-conversion-export-technical-design.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fods/gate11-nuget-package-plan.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fodt/gate11-architecture-approval.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fodt/gate11-commercial-licensing.md` | `M ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fodt/gate11-conversion-export-technical-design.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `acquisition-packs/fodt/gate11-nuget-package-plan.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `docs/python-foss/api-guidelines.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `docs/python-foss/examples-index.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `docs/python-foss/format-support-matrix.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `docs/python-foss/release-process.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `docs/python-foss/security-model.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `memory/38-r21-foss-release-readiness-and-gate11-preexecution-20260517.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `packaging/python/README.md` | `A ` staged | R21_PREEXISTING — do not touch |
| `packaging/python/build-local-packages.py` | `A ` staged | R21_PREEXISTING — do not touch |
| `packaging/python/package-matrix.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `packaging/python/pyproject.template.toml` | `A ` staged | R21_PREEXISTING — do not touch |
| `registry/format-registry.yaml` | `M ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/_matrix.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/abw.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/fodg.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/fodp.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/gnumeric.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `release-manifests/python-foss/zst.yaml` | `A ` staged | R21_PREEXISTING — do not touch |
| `src/python/abw/__init__.py` | `M ` staged | R21_PREEXISTING + FORBIDDEN PATH — do not touch |
| `src/python/fodg/__init__.py` | `M ` staged | R21_PREEXISTING + FORBIDDEN PATH — do not touch |
| `src/python/fodp/__init__.py` | `M ` staged | R21_PREEXISTING + FORBIDDEN PATH — do not touch |
| `src/python/gnumeric/__init__.py` | `M ` staged | R21_PREEXISTING + FORBIDDEN PATH — do not touch |
| `src/python/zst/__init__.py` | `M ` staged | R21_PREEXISTING + FORBIDDEN PATH — do not touch |
| `tests/evidence/test_python_package_matrix.py` | `A ` staged | R21_PREEXISTING — do not touch |
| `tests/evidence/test_python_release_manifests.py` | `A ` staged | R21_PREEXISTING — do not touch |
| `tests/examples/test_python_examples_smoke.py` | `A ` staged | R21_PREEXISTING — do not touch |
| `tools/evidence/contracts/r21-foss-release-readiness-and-gate11-preexecution-swarm.yaml` | `A ` staged | R21_PREEXISTING — do not touch |

### Untracked Files

| File | Classification | This Sprint |
|------|----------------|-------------|
| `.claude/commands/export-plan-context.md` | **SPRINT_OWNED** | TC-SKILL-PRD-000 — stage after TC-SKILL-PRD-004 edits |
| `format-factory.zip` | DEFERRED | Out of scope |
| `examples/` | R21_PREEXISTING | Out of scope |
| `reports/architecture/r21-*.md` | R21_PREEXISTING | Out of scope |
| `reports/docs/` | R21_PREEXISTING | Out of scope |
| `reports/examples/` | R21_PREEXISTING | Out of scope |
| `reports/governance/r21-*.md` (7 files) | R21_PREEXISTING | Out of scope |
| `reports/packaging/` | R21_PREEXISTING | Out of scope |
| `reports/planning/r21-*.md` | R21_PREEXISTING | Out of scope |
| `reports/release/r21-*.md` (2 files) | R21_PREEXISTING | Out of scope |
| `reports/testing/r21-*.md` | R21_PREEXISTING | Out of scope |
| `reports/verification/r21-*.md` (3 files) | R21_PREEXISTING | Out of scope |
| `taskcards/FODS-FODT-GATE11-G11A-G11C.md` | R21_PREEXISTING | Out of scope |
| `taskcards/PYTHON-FOSS-*.md` (6 files) | R21_PREEXISTING | Out of scope |
| `taskcards/R22-*.md` (2 files) | R21_PREEXISTING | Out of scope |

---

## File Ownership Map (This Sprint)

| File | Lane | Owned by Sprint | Change |
|------|------|----------------|--------|
| `reports/skills-system-hardening/20260517/` | 0 | YES | NEW directory |
| `.claude/settings.json` | 1 | YES | EDIT |
| `.claude/commands/_readme.md` | 1 | YES | EDIT |
| `taskcards/TC-0004-commands-skills.md` | 1 | YES | EDIT |
| `.claude/commands/evidence-review-next-prompt.md` | 2 | YES | EDIT |
| `.claude/commands/memory-sprint.md` | 2 | YES | EDIT |
| `.claude/commands/export-plan-context.md` | 2 | YES | EDIT + git add |
| `AGENTS.md` | 3 | YES | EDIT (J4 additive) |
| `docs/agent-methodology-index.md` | 4 | YES | EDIT (add row) |
| `tools/evidence/contracts/skills-prd-hardening-001.yaml` | 6 | YES | NEW |

---

## Gate A Result

**GATE A: PASS**
- HEAD rebaselined safe (R20 commits zero overlap with sprint-owned files)
- No merge/rebase state
- Consistency check PASS
- Dirty file classification complete
- Commit blocker documented: R21 pre-staged files present — human decision required before commit
