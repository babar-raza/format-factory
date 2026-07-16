# Skills-First Governance — Consolidated Audit, Root Cause & Architecture

**Sprint:** SKILLS-FIRST-CONTROL-2026-07-16 · **Date:** 2026-07-16 ·
**Repo:** format-factory · **Branch:** main

This is the current-state audit, root-cause analysis, and target architecture for
establishing a strict, technically-enforced skills-first operating model. It was
produced from four independent parallel audits (skill/command machinery,
enforcement points, agent entry points, ad-hoc/bypass history) cross-checked
against the deterministic auditor `tools/governance/skills_first/audit.py`.

---

## Part I — Current-state findings

### I.1 The system already had substantial skills-first machinery
Format Factory is **not** greenfield for this: a canonical machine-readable policy
(`docs/governance/skill-only-policy.yaml`, SKILL-ONLY-POLICY-001 v2.0), a
185-entry skill registry, a 185-entry command registry, a 37-route capability
registry, a mutation guard, a CI skill-attribution check, an installed pre-commit
hook, and two prior forensic sprints (`SKILL-GOV-FORENSIC-20260625` verdict
*DIRECT_MUTATION_BYPASSES_REMAIN*; `SKILLS-FIRST-ADHOC-HEAL-2026-07-16` verdict
*ACCEPT*, but scoped to nested-duplicate package removal, not registry governance).

So this sprint is **harden-and-prove**, not build-from-scratch. Its value is
closing the genuine gaps and adding *technical* enforcement where only prompt
enforcement existed.

### I.2 Enforcement is detection-heavy, prevention-light
The only tool-layer interception, `tools/supervisor/coordination/hooks/gate.py`
(PreToolUse Edit/Write/Bash), enforces **coordination leases only** — it is
skill-blind and **fails open**. The only mechanical skill gate is the installed
pre-commit hook, and it is **`src/`-scoped**, uses a **1-hour receipt time window
not bound to the staged files**, and is bypassable (`--no-verify`,
`.local/exceptions/`). EP-008 (taskcard schema) has **zero references**; EP-009
(plan route validator) is **manual-only**.

### I.3 The policy's own status fields were stale/contradictory
- **EP-007** declared `NOT_IMPLEMENTED` while the hook is in fact installed
  (`.git/hooks/pre-commit → ../../.hooks/pre-commit-skill-guard`).
- **EP-009** block said `IMPLEMENTED` while its own `known_gaps` entry said "not
  implemented."

### I.4 First-class ungoverned entry points
- `sprint_executor.py run-loop` spawns `claude --print --dangerously-skip-permissions`
  and binds **no skill** — a headless sub-agent can edit `src/` with no resolution.
- **~25** `tools/*.py` generator/repair/backfill/migrate scripts write `src/` and
  registries **directly**, no skill, no receipt.
- External MCP servers (`task-master-ai`, `claude-flow`) sit outside the skill system.
- Kilo has no dispatch hook (`BLOCKED_ON_KILO`).

### I.5 No content-hash binding between command and skill
Neither registry stores a hash/version. Editing a command `.md` body cannot be
detected as diverging from its registered skill — so **stale-command detection did
not exist** (prompt §19/§31 requirement had no mechanism).

### I.6 Two genuinely ownerless command files, and drift
- `.claude/commands/fix-exception-hierarchy.md` and `wire-analytics-module.md`
  existed on disk and in the Claude runtime but were in **neither** registry.
- Governance state drifts: skill counts reported as 173 / 177 / 185 / 187 across
  four sources; ad-hoc inventory 230 vs a fresh 241; the residual-bypass report
  says `0` ungoverned but a fresh run finds `3`.

### I.7 Authority chain partially inverted
`.supervisor/skill-first-policy.md` (a derived summary) never cites the canonical
`skill-only-policy.yaml` and points authority back at CLAUDE.md/AGENTS.md/registry;
CLAUDE.md EP-3 restates the rule without citing the policy path.

---

## Part II — Root causes (why ungoverned work was possible)

| ID | Root cause |
|----|------------|
| RC-1 | No tool-layer skill-resolution interception; the one PreToolUse hook is coordination-only and fail-open. |
| RC-2 | The single mechanical skill gate (pre-commit) is `src/`-only, time-window-based (not file-bound), and bypassable. |
| RC-3 | Headless `run-loop` runs with `--dangerously-skip-permissions` and binds no skill. |
| RC-4 | ~25 direct-mutation scripts are first-class entry points outside any skill. |
| RC-5 | No execution-manifest primitive bound {task, skill, command, allowed paths, validators, evidence} before mutation; the mutation guard was opt-in and permissive. |
| RC-6 | No content-hash binding between command and skill → drift undetectable; closeout couldn't prove the command used matched the registered skill. |
| RC-7 | Governance state artifacts drift because they are snapshots with no freshness gate → the audit surface itself was unreliable. |
| RC-8 | Authority chain partially inverted/duplicated → agents could follow a stale derived summary. |

---

## Part III — Target architecture (what this sprint built)

A cohesive **Skills-First Control (SFC)** layer under
`tools/governance/skills_first/`, all fail-closed, all tested:

```
resolve → manifest → (work) → audit/validate → closeout   (+ governed exceptions)
```

- **`registries.py`** — the single fail-closed loader for the three registries.
  Malformed/missing → `RegistryError`, never a clean pass. (RC-7 surface hardened.)
- **`resolve.py`** — deterministic operation→route→skill resolution implementing the
  policy selection order; returns `MISSING_SKILL_CAPABILITY` rather than guessing,
  and flags `low_confidence` when a match rests only on generic tokens. (RC-1 aid.)
- **`manifest.py`** + `.supervisor/schemas/execution-manifest.schema.json` — the
  concrete skill-resolution + execution record. Captures each selected skill's
  **command content hash**. Refuses unregistered/inactive skills or empty
  allowed_paths. (RC-5, RC-6.)
- **`closeout.py`** — the fail-closed closeout gate: blocks on invalid manifest,
  out-of-scope change, **command-hash drift since resolution**, or missing evidence.
  Covers **all** governed paths and binds evidence to the **actual changed files**
  (compensates for RC-2). Naming a skill is never sufficient.
- **`audit.py`** — deterministic parity/coverage auditor: skill↔command matrix,
  ownerless-command detection, **command↔skill hash baseline** (new stale-command
  mechanism, RC-6), material-action matrix, enforcement-point report with
  ground-truth probes (auto-detects stale EP status, RC-3), ungoverned-generator
  signal scan (RC-4). Fail-closed with calibrated CRITICAL/HIGH/MEDIUM/INFO tiers.
- **`exceptions.py`** — narrow governed exception mechanism; expired/broad/ownerless/
  forbidden-reason exceptions fail closed and can never launder a finding.
- **`validate_skills_first_control.py`** — the composite CI/closeout gate (EP-013):
  audit + manifest self-test + policy self-consistency + exception validity.

Policy reconciled to **v2.1**: EP-007/EP-009 statuses corrected; the three real
ungoverned-mutation gaps (EP-010 tool-layer, RUNLOOP-SKIPPERMS, DIRECT-GENERATOR)
documented as first-class `known_gaps` with compensating controls; the SFC
primitives registered as EP-011/012/013.

---

## Part IV — What remains OPEN (honest)

- **EP-010** (tool-layer PreToolUse skill gate) — the live `gate.py` is coordination-
  only. Wiring a skill-resolution check into it is deferred because it is shared
  infrastructure across many concurrent live agents and must not be hot-patched to a
  blocking mode without a staged advisory→enforcing rollout. Compensated by
  EP-007/012/013.
- **RUNLOOP-SKIPPERMS** — the headless actuator must create a manifest per sprint and
  run the closeout gate; wiring that into `sprint_executor.py` is the next step.
- **DIRECT-GENERATOR** — ~25 scripts need skill wrappers or read-only/deprecated
  marking; the auditor now emits the signal list to drive that backfill.
- **137** command-registry entries lack a `file` field (MEDIUM, non-blocking) —
  backfill via `normalize-skill-registry`.

These are tracked in `skill-only-policy.yaml` `known_gaps` and are the honest basis
for the production verdict.
