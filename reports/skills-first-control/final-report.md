# Skills-First Governance — Final Report

**Sprint:** SKILLS-FIRST-CONTROL-2026-07-16 · **Repo:** format-factory · **Branch:** main
**Production verdict:** `READY_WITH_EXTERNAL_BLOCKERS` ·
**Independent verification:** `ACCEPT_WITH_EXTERNAL_BLOCKERS`

## 1. Intent
Establish a strict, technically-enforced **skills-first operating model** for every
agent (Claude Code primary): make ad-hoc repository work hard to do, easy to detect,
and **impossible to close as complete without skills-first execution evidence.**

## 2. Current-state findings (before)
The repo already had substantial skills-first machinery (canonical policy, 185-skill
registry, 185-command registry, 37 routes, mutation guard, CI attribution check,
installed pre-commit hook, two prior forensic sprints). But enforcement was
**detection-heavy, prevention-light**: the live tool-layer hook (`gate.py`) is
coordination-only and skill-blind (fail-open); the only mechanical skill gate
(pre-commit) is `src/`-only, time-window-based, and bypassable; EP-008/EP-009 had
scripts/schemas but no invocation; the policy's own EP-007/EP-009 statuses were
stale/contradictory; `run-loop` spawns `--dangerously-skip-permissions` binding no
skill; ~25 direct-mutation scripts bypass skills entirely; no command↔skill hash
binding existed (stale-command detection impossible); 2 command files were ownerless;
and governance state (skill counts, ad-hoc inventory, residual-bypass report) drifts.
Full detail + 8 root causes: `consolidated-audit.md`.

## 3. Root causes
RC-1 no tool-layer skill interception · RC-2 loose single commit gate · RC-3 headless
skip-perms loop · RC-4 direct-mutation scripts · RC-5 no execution-manifest primitive ·
RC-6 no command↔skill hash binding · RC-7 drifting governance state · RC-8 inverted
authority chain.

## 4. Target architecture (built this sprint)
A cohesive, fail-closed **Skills-First Control (SFC)** layer:
`resolve → manifest → work → audit/validate → closeout` (+ governed exceptions),
under `tools/governance/skills_first/` with the composite gate
`validate_skills_first_control.py`. Each primitive fails closed; the closeout gate
binds evidence to the **actual changed files** and detects command-hash drift — the
first mechanism that makes "named a skill" insufficient.

## 5. Skills work
Created 3 skills (`fix-exception-hierarchy`, `wire-analytics-module` — healed from
ownerless; `skills-first-audit` — new SFC governance skill). 0 ownerless commands
remain. No skills removed. The new skill was created through the governed
gap→rubric→create→register→use path (skill-gap pilot).

## 6. Claude command work
Registered the 2 orphan commands + the new `skills-first-audit` command in the command
registry; added the `skills_first_control` capability route. The new command is a
**thin interface** (no own policy) — the pattern the model requires. Command↔skill
parity is now auditable and hash-baselined.

## 7. Enforcement
Added EP-011 (execution manifest), EP-012 (fail-closed closeout gate), EP-013
(composite control validator) — all fail-closed and tested. Reconciled EP-007
(→ IMPLEMENTED_AND_INSTALLED) and EP-009 (→ IMPLEMENTED_MANUAL_ONLY). Documented the
three real ungoverned-mutation gaps (EP-010 tool-layer, RUNLOOP-SKIPPERMS,
DIRECT-GENERATOR) as first-class `known_gaps` with compensating controls. Policy → v2.1.

## 8. Healing
Two ownerless commands brought under governance (cross-confirmed: the pre-existing
`sync_skill_command_registry.py` now reports 0 flags). Policy statuses reconciled to
ground truth. The auditor now probes ground truth so a stale EP status fails closed.

## 9. Pilots
- **Machinery:** governed this sprint's own machinery via manifest+closeout → **CLOSE_OK**.
- **Skill-gap:** genuine gap handled via the governed path → **PASS**.
- **Autonomous (bounded):** out-of-scope work **BLOCKED** at closeout; live run-loop
  deferred (RUNLOOP-SKIPPERMS-GAP).
- **Product:** governance path proven; actual `src/` write DENY-listed → **external blocker**.

## 10. Adversarial results
13 bypass classes attempted (unregistered/empty skill, empty allowed_paths, bad agent,
out-of-scope change, missing evidence, hash drift, broad/expired/forbidden exception,
malformed registry, naming-without-evidence). **1** bypass found during build
(empty-allowed-paths) and **repaired**; **0** successful after repair. Verified by tests
and independently.

## 11. Independent verification
A separate agent ran every tool itself, attempted bypasses, and confirmed healing +
policy + honest disclosure → **ACCEPT_WITH_EXTERNAL_BLOCKERS** (see
`independent-verification.md`).

## 12. Remaining blockers (external / tracked)
1. `src/` write DENY in `.claude/settings.json` (operator authorization to run the full
   product pilot). 2. Headless `run-loop` manifest/closeout wiring (RUNLOOP-SKIPPERMS-GAP).
3. EP-010 PreToolUse skill gate still coordination-only (staged rollout on shared infra).
Also tracked (non-blocking): 137 command-registry `file`-field backfill; wire the
control validator into the 226-runner as V227; reconcile `.supervisor/skill-first-policy.md`
authority inversion.

## 13. Production verdict
**READY_WITH_EXTERNAL_BLOCKERS.** The skills-first control system is implemented,
fail-closed, tested (36/36), self-governing (machinery pilot CLOSE_OK), and
independently accepted. Full end-to-end prevention at the live tool layer and in the
headless loop requires the three tracked, honestly-disclosed follow-ups.
