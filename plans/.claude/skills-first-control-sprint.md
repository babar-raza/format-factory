# Plan — Skills-First Control Sprint (SKILLS-FIRST-CONTROL-2026-07-16)

**Type:** machinery_hardening · **Owner:** Claude Code · **Authority:**
`docs/governance/skill-only-policy.yaml`. Objective: establish a strict,
technically-enforced skills-first operating model — make ad-hoc work hard to do,
easy to detect, and impossible to close without skills-first evidence.

This plan was authored and executed in one session. Status reflects actual
outcomes; see `reports/skills-first-control/` for evidence.

## Taskcards

| ID | Title | Status | Evidence |
|----|-------|--------|----------|
| TC-SFC-001 | Four-lane current-state audit (skills/commands/entry-points/enforcement/ad-hoc) | CLOSED | `reports/skills-first-control/consolidated-audit.md` |
| TC-SFC-002 | Fail-closed registry loaders (`registries.py`) | CLOSED | module + tests |
| TC-SFC-003 | Deterministic parity/coverage auditor (`audit.py`) incl. command↔skill hash baseline | CLOSED | `audit-summary.json`, tests |
| TC-SFC-004 | Execution-manifest schema + `manifest.py` (fail-closed) | CLOSED | `.supervisor/schemas/execution-manifest.schema.json`, tests |
| TC-SFC-005 | Skill resolution (`resolve.py`) with MISSING_SKILL_CAPABILITY + low-confidence flag | CLOSED | module + tests |
| TC-SFC-006 | Fail-closed closeout evidence gate (`closeout.py`) | CLOSED | tests: scope/drift/evidence blocking |
| TC-SFC-007 | Governed exception mechanism (`exceptions.py`) + store | CLOSED | `accepted-findings.yaml`, tests |
| TC-SFC-008 | Composite control validator (`validate_skills_first_control.py`, EP-013) | CLOSED | validator verdict PASS |
| TC-SFC-009 | Reconcile canonical policy → v2.1 (EP-007/009 fixes; EP-010/011/012/013; known_gaps) | CLOSED | `skill-only-policy.yaml` diff |
| TC-SFC-010 | Human-readable operating model | CLOSED | `docs/governance/skills-first-operating-model.md` |
| TC-SFC-011 | Heal 2 ownerless commands (fix-exception-hierarchy, wire-analytics-module) | CLOSED | registry entries; audit 0 ownerless |
| TC-SFC-012 | Skill-gap pilot: create+register+use `skills-first-audit` skill/command/route | CLOSED | 3 registries + route; resolve routes to it |
| TC-SFC-013 | Unit/integration/regression/adversarial tests | CLOSED | 36 passing |
| TC-SFC-014 | Machinery pilot: govern this sprint's own machinery work via manifest+closeout | CLOSED | `pilots/pilot-machinery.json` |
| TC-SFC-015 | Autonomous pilot (bounded): manifest-in-loop contract demonstration | CLOSED | `pilots/pilot-autonomous.json` |
| TC-SFC-016 | Product pilot dry-run (write perms deny src/) | CLOSED_EXTERNAL_BLOCKER | `pilots/pilot-product.json` |
| TC-SFC-017 | Independent verification (fresh agent) | CLOSED | `independent-verification.md` |
| TC-SFC-018 | Evidence bundle + final verdict | CLOSED | `evidence-bundle.zip` |

## Open follow-ups (registered as policy known_gaps, not silently dropped)
- EP-010-GAP: wire skill-resolution into the PreToolUse hook via staged advisory→enforcing rollout.
- RUNLOOP-SKIPPERMS-GAP: `sprint_executor.py run-loop` must create a manifest + run closeout per sprint.
- DIRECT-GENERATOR-GAP: wrap ~25 direct-mutation scripts in governed skills or mark read-only.
- Backfill 137 command-registry `file` fields via `normalize-skill-registry`.
- Wire `validate_skills_first_control.py` into the 226-validator runner as the next reserved id (V227).

---

## Convergence hardening — iteration 1 (2026-07-16, prompt2 role)

Stage-1 audit (`reports/skills-first-control/convergence/stage1-audit.yaml`) produced 7
findings. Every actionable finding is taskcarded below (no prose-only findings).

| Taskcard | Source finding | Class | Status | In-scope | Disposition |
|----------|---------------|-------|--------|----------|-------------|
| TC-SFC-CONV-001 | CF-001 skill-first-policy.md authority inversion | PARTIAL→fix | CLOSED | YES | EXECUTED this iteration (see below) |
| TC-SFC-CONV-002 | CF-002 EP-010 tool-layer skill gate | VALID_DEFERRED | DEFERRED | NO | successor mission; known_gap EP-010-GAP; compensating EP-007/012/013 |
| TC-SFC-CONV-003 | CF-003 run-loop skip-perms | VALID_DEFERRED | DEFERRED | NO | successor mission; known_gap RUNLOOP-SKIPPERMS-GAP |
| TC-SFC-CONV-004 | CF-004 direct-mutation scripts | VALID_DEFERRED | DEFERRED | NO | successor mission; known_gap DIRECT-GENERATOR-GAP |
| TC-SFC-CONV-005 | CF-005 137 file-field backfill | VALID_DEFERRED | DEFERRED | NO | MEDIUM non-mandatory; governed via /normalize-skill-registry |
| TC-SFC-CONV-006 | CF-006 wire validator to 226-runner (V227) | VALID_DEFERRED | DEFERRED | NO | count-fragile shared runner; standalone validator works |
| TC-SFC-CONV-007 | CF-007 product src/ write | BLOCKED_TRUE_EXTERNAL | BLOCKED | NO | Write(src/**) DENY in settings; operator authorization required |

**TC-SFC-CONV-001 (executed):** Reconcile `.supervisor/skill-first-policy.md` to name
`docs/governance/skill-only-policy.yaml` (SKILL-ONLY-POLICY-001) as the PRIMARY canonical
authority and mark this file explicitly subordinate. `allowed_paths: [.supervisor/skill-first-policy.md]`;
`forbidden_paths: [src/**]`; validation: re-run `validate_skills_first_control.py` (still PASS)
and confirm the file now cites the canonical policy.

**Scope boundary (authority for deferral):** This plan's mandate was to BUILD the SFC control
system, heal in-scope governance inconsistencies, test, pilot, verify, and DOCUMENT residual
gaps as tracked follow-ups. TC-SFC-CONV-002..006 are structural changes to shared live
infrastructure (the coordination hook, the headless actuator, ~25 scripts, the 226-runner)
that require their own staged-rollout missions and are unsafe to hot-patch under many
concurrent live agents; they are recorded as first-class policy `known_gaps` with compensating
controls. TC-SFC-CONV-007 is a true external permission blocker. None is an in-scope mandatory
requirement of THIS plan.
