# Preflight State Report

**Sprint:** forensics-archaeology-20260621
**Captured:** 2026-06-21

---

## Git State

```
Branch:  main
HEAD:    827f5a52915f1ee3b285bf13965b5f65f3532a69
Message: fix(governance+sal): V45 test path correction, SAL idempotency fix, V46 skill transcript validator
```

### Recent Commits (10)
```
827f5a52 fix(governance+sal): V45 test path correction, SAL idempotency fix, V46 skill transcript validator
3104e1c1 chore(machinery): Phase 2 sprint closeout — fix approval-gates signal conflict (iteration 2)
8ca43a12 feat(spec): canonical Python spec stubs for FODS and FODT (GAP-ARCH-003, GAP-ARCH-005)
4b42e25d chore(reports): update materialized evidence review for machinery forensics sprint
0d5b73ca fix(machinery): add per-chat nonce to session_id derivation (SC-005)
c10be781 chore(machinery): add skill coverage pre-check, register infra skills, add FODS install proof
f03234b0 fix(machinery): add track_type to plan locks (GAP-WF-004)
fed7b6b3 feat(machinery): forensics sprint lifecycle root-cause analysis Phase 1 repairs
dd136460 test: add 1036 format analytics tests
2b422f69 fix(validate): use UTF-8 for manifest open; add adequacy/layer tests; update baseline
```

### Modified (dirty) Files

| File | Classification |
|------|---------------|
| `registry/source-structure-baseline.json` | machinery source — current sprint artifact |
| `src/python/fods/neutral_model.py` | product source — current sprint artifact |
| `tests/specification-authority-layer/test_qname_structure_validator.py` | machinery source — current sprint artifact |
| `tests/supervisor/test_governance_validators.py` | machinery source — current sprint artifact |
| `tools/supervisor/governance_validator_runner.py` | machinery source — current sprint artifact |
| `tools/supervisor/governance_validators.py` | machinery source — current sprint artifact |

### Untracked Files

| File | Classification |
|------|---------------|
| `.claude/commands/sal-pipeline-heal.md` | new skill — generated evidence |
| `reports/r129-fodt-install-proof-sprint2/` | generated evidence — prior sprint |
| `reports/skills-r127/` | generated evidence — prior sprint |
| `src/python/fods/Compat/` | product source — current sprint artifact (new facade layer) |

**Risk classification:** LOW. All dirty/untracked files are current sprint artifacts or
generated evidence. No risky/conflicting files detected. No stale working-tree corruption.

---

## Repository Structure

```
format-factory/
├── src/
│   ├── python/        (20 format packages + _shared + egg-info)
│   └── net/           (11 format packages)
├── tests/             (46,000+ tests organized by domain)
├── tools/
│   ├── supervisor/    (80+ supervisor infrastructure files)
│   ├── specification-authority-layer/  (15 SAL tools)
│   ├── validators/    (5 validators)
│   └── [many others]
├── plans/             (master-plan.md + correction plan + active plans)
├── reports/           (supervisor reports + capability layer + forensics)
├── registry/          (format-registry.yaml + scoring + matrices + baseline)
├── docs/              (architecture + governance + spec docs)
├── .local/supervisor/ (state files: continuation, plan locks, session)
└── .claude/commands/  (40+ registered skills)
```

---

## Existing Plans

| Plan File | Status |
|-----------|--------|
| `plans/master-plan.md` | Active master authority |
| `plans/strategic/spec-to-feature-radical-correction-plan.md` | Active correction authority (27 sections, ~3200 lines) |
| `plans/strategic/snoopy-juggling-seal.md` | Active plan context |
| `plans/strategic/capability-fact-to-feature-production-plan.md` | Supporting plan |
| `plans/strategic/continuation-isolation-plan.md` | Supporting plan |
| `plans/healing/product-code-healing-plan.md` | Supporting plan |

---

## Supervisor State

- Last sprint: `sal-skill-gov-20260621-3104e1c1`
- Evidence verdict: ACCEPTED
- Tests: 1490 passed / 0 failed
- AUTONOMOUS_CONTINUE: YES
- Current mode: MODE 4 (ACTIVE_MCP_ACTIVATION)
- Continuation signal: active, product track

---

## Evidence Directories

```
.local/evidences/           — sprint evidence bundles
.local/supervisor/reviews/  — declaration review packages
.local/spec-cache/          — SAL fact files (22 formats)
reports/supervisor/         — session-resume, approval-gates, next-sprint
reports/capability-layer/   — gap-ledger, capability maps
reports/forensics-archaeology-20260621/  — THIS REPORT
```

---

## Governance Documents

- `CLAUDE.md` — supreme directive and session instructions
- `AGENTS.md` — agent protocol and governance rules
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — master correction authority
- `docs/spec-to-feature-correction-plan-summary.md` — quick reference
- `registry/gate11-criteria.yaml` — gate 11 criteria
- `registry/format-registry.yaml` — format authority
- `docs/automation/supervisor-worker-contract.md` — worker contract
