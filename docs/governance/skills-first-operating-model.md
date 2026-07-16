# Skills-First Operating Model (human-readable)

**Status:** active · **Authority:** this document is the human-readable companion to
the machine-readable canonical policy `docs/governance/skill-only-policy.yaml`
(SKILL-ONLY-POLICY-001). Where the two differ, **the YAML wins**. Do not restate
governance semantics elsewhere — reference this pair.

This model applies to **every agent** working in Format Factory — Claude Code
(primary), Codex, Kilo, the supervisor, autonomous workers, repair agents,
planning agents, and any future integration. Claude Code gets the strongest,
most explicit implementation because it performs most material work.

---

## 1. The one rule

> **No material action without a resolved skill, and no task closes without
> skills-first evidence.**

Skills are the authoritative operational layer. Claude **commands** are the thin
interface that exposes skills. Agents must not invent a local workflow when a
skill already governs the operation.

## 2. What counts as a "material action"

Creating/editing/moving/deleting files; changing product source or machinery;
modifying SAL, QName, capabilities, oracle bindings, validators, tests, evidence,
state, plans, task registries; adding exceptions; changing autonomous behavior;
creating or modifying commands or skills; changing CI/release/packaging; running
repairs or migrations; generating source; closing tasks; issuing verdicts.

Read-only inspection needs no skill — **but it may not silently become a
mutation.** The moment inspection turns into a change, skill resolution is required.

## 3. The governed lifecycle (what Claude does)

```
classify → resolve → manifest → work → validate → evidence → closeout
```

1. **Classify** the operation and its target paths.
2. **Resolve** a skill (or composition):
   `python -m tools.governance.skills_first.resolve --operation "<op>" --paths <p>...`
   - `RESOLVED` → use the named skill/command. If `review_required` is set, apply
     the **extend-vs-create rubric** (section 5) before accepting it.
   - `MISSING_SKILL_CAPABILITY` → **do not implement directly.** Run the skill-gap
     review (section 5).
3. **Manifest** — bind the work before mutating:
   `python -m tools.governance.skills_first.manifest create --task-id … --agent-type
   CLAUDE_CODE --operation … --skill <id> --allowed-paths <globs> --write`
   The manifest records the selected skills + their command hashes, allowed/forbidden
   paths, validators, tests, and evidence requirements. It **refuses** an
   unregistered/inactive skill or empty allowed_paths.
4. **Work** through the skill's command. Stay inside `allowed_paths`.
5. **Validate** — run the skill's mandatory validators.
6. **Evidence** — produce the skill-use evidence the skill requires.
7. **Closeout** — the gate that decides whether the task may close:
   `python -m tools.governance.skills_first.closeout --manifest <execution_id>
   --changed-files … --evidence … --close`
   It **blocks** on: invalid manifest, out-of-scope change, command-hash drift
   since resolution, or missing evidence. **Naming a skill is never enough.**

## 4. Selection priority (do them in order)

1. Exact applicable skill.
2. Exact workflow skill that composes lower-level skills.
3. Composition of compatible existing skills.
4. Extension review of the nearest existing skill.
5. New-skill review.
6. Reject/redesign the work.

Never jump straight to creating a new skill. Never pick a loosely-related skill
just to satisfy "a skill must be named" — the resolver flags such matches
`low_confidence`.

## 5. Extend-vs-create rubric (when no exact skill fits)

**Extend** an existing skill only if the new behavior shares its core
responsibility, layer, invariants, and evidence model, keeps current callers
compatible, and does not turn the skill into a catch-all.

**Create** a new skill when the operation has a distinct responsibility, governs
different layers, has different invariants/validation/failure-model/risk, or would
otherwise create hidden coupling.

**Compose** when responsibilities stay separate but the workflow needs several
governed operations.

Record the decision. Material skill changes require independent review. This is
exactly how the `skills-first-audit` skill itself was created (2026-07-16): the
nearest match `sync-readmes` was **rejected** — different responsibility and layer —
and a new skill was justified and registered.

## 6. Exceptions (narrow, owned, expiring)

When strict skill use is temporarily impossible, record a governed exception in
`reports/skills-first-control/accepted-findings.yaml` with **all** of:
`exception_id, finding_signature, severity, owner, reason, remediation_task,
created, expires, compensating_control`. Forbidden reasons (`urgent`, `small_change`,
`documentation_only`, `one_time`, `convenience`, …) are rejected. Expired, broad,
ownerless, or malformed exceptions **fail the gate** — they can never launder a
finding. **Target: zero active exceptions.**

## 7. Enforcement layers (defense in depth)

| Layer | Mechanism | Scope | Fails |
|---|---|---|---|
| EP-007 pre-commit | `.hooks/pre-commit-skill-guard` (installed) | `src/` commits | closed |
| EP-011 manifest | `manifest.py` | pre-mutation record | closed |
| EP-012 closeout | `closeout.py` | all governed paths, file-bound evidence | closed |
| EP-013 control validator | `validate_skills_first_control.py` | CI / closeout | closed |
| EP-003/005 declaration | supervisor grading | declared work | partial |
| EP-010 tool-layer gate | `gate.py` (coordination-only) | live edits | **OPEN — documented gap** |

EP-010 (the live `PreToolUse` hook is coordination-only / skill-blind) is the
**known residual gap**, acknowledged with compensating controls (EP-007/012/013).
See `skill-only-policy.yaml` `known_gaps` for the full list, including the headless
`run-loop --dangerously-skip-permissions` gap and the direct-generator-script gap.

## 8. Startup (Claude, every session touching material work)

1. Identify the repo. 2. Load this model + the YAML policy. 3. Classify the task.
4. Resolve the skill/composition. 5. Load the matching command. 6. Establish path
ownership (manifest `allowed_paths`). 7. Establish validators + evidence. 8. Create
the execution record (manifest). 9. Work. 10. Closeout gate.

Do not rely on the user to mention skills. The repository provides the guidance;
`/skills-first-audit` verifies the whole system stays consistent.
