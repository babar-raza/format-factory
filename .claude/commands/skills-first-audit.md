---
version: "1.0"
last-updated: "2026-07-16"
phase-available: "3+"
gate-required: "None -- read-only audit + fail-closed control gate"
skill_type: ATOMIC_SKILL
idempotency: idempotent
generated_by: claude
visibility: generated
skill_id: skills-first-audit
---

# /skills-first-audit

Audit and enforce the **Skills-First Control (SFC)** system: verify that every
material agent action in this repository is governed by a resolved skill, that
skills and Claude commands are in parity, and that no task can close without
skills-first evidence.

This command is a **thin governed interface** over the SFC package
(`tools/governance/skills_first/`) and the control validator
(`tools/governance/validate_skills_first_control.py`). It contains **no policy of
its own** — the authoritative policy is `docs/governance/skill-only-policy.yaml`
(SKILL-ONLY-POLICY-001). Created 2026-07-16 by the Skills-First Control sprint as
the resolution of a genuine skill gap: no prior skill governed SFC consistency
(the nearest match, `sync-readmes`, has a different responsibility and layer and
was rejected by the extend-vs-create rubric).

## When to use

- Before closing any sprint that touched machinery, registries, commands, or skills.
- In CI, as a fail-closed gate on skills-first consistency.
- When onboarding a new skill or command, to confirm parity.

## Contract

**Inputs (handoff fields):**
- `mode`: `audit` (report only) | `gate` (fail-closed verdict) | `closeout`
- `execution_id` (closeout mode only): the execution manifest to close against
- `changed_files` (closeout mode only): files changed by the work

**Preconditions:**
- The three registries load cleanly (`.supervisor/skill-registry.yaml`,
  `.claude/commands/command-registry.yaml`,
  `.supervisor/capability-routing-registry.yaml`). A malformed registry is a hard
  CONFIG_ERROR (exit 2), never a clean pass.

**Steps:**
1. Resolve + record: `python -m tools.governance.skills_first.resolve --operation "<op>"`.
2. Audit parity/coverage:
   `python -m tools.governance.skills_first.audit --write` (writes
   `reports/skills-first-control/audit-summary.{json,md}` and seeds the
   command-skill hash baseline).
3. Gate: `python tools/governance/validate_skills_first_control.py`
   (exit 0 PASS / 1 FAIL / 2 CONFIG_ERROR).
4. Closeout (when finishing governed work):
   `python -m tools.governance.skills_first.closeout --manifest <execution_id>
   --changed-from-git --evidence <paths> --close`.

**Mandatory validations:**
- `skills_first_parity_no_critical` — audit reports 0 CRITICAL.
- `skills_first_policy_consistent` — policy references the execution-manifest
  schema and carries no stale EP status.
- `skills_first_closeout_evidence_present` — closeout gate passes (in-scope +
  evidence) before a task may close.

**Invariants:**
- Fails closed: missing/malformed registry, invalid manifest, out-of-scope change,
  command-hash drift, missing evidence, or an invalid/expired exception all block.
- Naming a skill is never sufficient — evidence must resolve on disk.

**Prohibited actions:**
- Do not edit product source or registries from this command — it is an
  audit/enforcement interface only.
- Do not downgrade a finding to pass the gate; use a governed exception in
  `reports/skills-first-control/accepted-findings.yaml` (narrow, owned, expiring).

**Required evidence:**
- `reports/skills-first-control/audit-summary.json`
- Control validator verdict line
- (closeout) the CLOSE_OK result + manifest transition to CLOSED

**Outputs:** `reports/skills-first-control/audit-summary.{json,md}`,
`reports/skills-first-control/command-skill-hash-baseline.json`.

## Composition

Composes with `/run-governance-validators` (broad governance) and
`/validate-skill-contracts` (per-skill schema). This command owns the
cross-registry parity + manifest + closeout dimension specifically.
