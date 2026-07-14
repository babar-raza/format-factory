---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target capability description + same RED-GREEN-REFACTOR cycle
  + same 7-step FF registration pipeline produce the same authored skill file and
  the same registration outcome. Re-running the pipeline against an already-registered
  skill_id updates the existing entry in place (create_or_update) rather than
  duplicating it; re-running Phase F (REFACTOR) against an already-hardened skill
  file with no new rationalization found is a no-op."
loc_budget: "0 lines of executable code (prompt-driven authoring workflow only;
  no bundled script of its own — every step invokes an existing, already-governed
  tool or skill by name)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the
  dry-run registration proof recorded under TC-EXT-022-05"
synthesized_from:
  - source: obra/superpowers
    skill: writing-skills
    license: MIT
    commit: d884ae04edebef577e82ff7c4e143debd0bbec99
  - source: getsentry/skills
    skill: skill-writer
    license: Apache-2.0
    commit: 5a64b36c62d042d3981b7937d9d6ca7bd1753b9a
  - source: trailofbits/skills
    skill: workflow-skill-design
    license: CC-BY-SA-4.0
    commit: cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af
risk_level: MEDIUM
created-by: TC-EXT-022-01
product_track: governance
---

# /create-ff-skill

Author and register a new governed skill in this repository. This is not a
single-source import — it is a synthesis of three external methodologies into
one authoring workflow scoped to this repo's own real skill-registration
machinery: a RED-GREEN-REFACTOR authoring discipline (writing-skills), a
6-step authoring backbone (skill-writer), and an anti-pattern review checklist
(workflow-skill-design). Every "register/deploy" step in all three upstream
sources is replaced end to end by this repository's own 7-step pipeline —
never by any upstream deployment mechanism.

## Attribution

<!--
This skill is a synthesis of three cited sources, not a single-vendor import,
per `synthesized_from` in the frontmatter above (replacing the single-source
`external_skill_origin`/`external_skill_source`/`external_skill_commit`/
`external_skill_license` fields used by this plan's other TC-EXT-0XX imports).

One of the three sources (trailofbits/skills, CC-BY-SA-4.0) carries a
share-alike term. Per that license's ShareAlike clause, this derivative file
(`.claude/commands/create-ff-skill.md`) is distributed under CC-BY-SA-4.0 terms
for the specific content adapted from workflow-skill-design (the anti-pattern
review checklist and pattern-selection framing below). This obligation applies
only to that adapted content in this one file — it does not relicense any
other file in this repository.
-->

- **RED-GREEN-REFACTOR cycle** (Phase R / Phase F below) is adapted from
  `obra/superpowers`'s `writing-skills` skill (MIT), commit
  `d884ae04edebef577e82ff7c4e143debd0bbec99`. The three-phase discipline
  (pressure-scenario baseline → author → close loopholes and re-test) is
  carried over; the skill's own **Deployment** checklist step — publish the
  finished skill to the author's personal copy of the source project and open
  a review request back upstream — is **explicitly not imported**. See
  "Explicit Exclusion" below.
- **6-step authoring backbone** (Phase G below) is adapted from `getsentry/skills`'s
  `skill-writer` skill (Apache-2.0), commit
  `5a64b36c62d042d3981b7937d9d6ca7bd1753b9a`. Steps 1-5 (resolve target/shape,
  run synthesis when needed, run iteration first when improving from examples,
  author the artifact, optimize description/trigger quality) are carried over;
  Step 6 ("apply repository registration steps for the active layout, run
  quick validation for structural checks") is replaced entirely by this repo's
  own named pipeline (below) — a concrete, already-proven procedure rather
  than a generic instruction to look one up.
- **Anti-pattern review checklist** (below) is adapted from `trailofbits/skills`'s
  `workflow-skill-design` skill (CC-BY-SA-4.0), commit
  `cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. The essential principles
  (description-is-the-trigger, numbered phases, tools-match-executor,
  progressive disclosure under 500 lines, scalable tool patterns) and the
  pattern-selection concept are restated here for this repository's own
  prompt-only `.claude/commands/*.md` skill format — this is an adaptation of
  the cataloged anti-pattern categories, not a verbatim reproduction of the
  upstream catalog's exact wording; items that presuppose a multi-file skill
  package or a bundled executable tool (neither of which this repo's
  prompt-spec skills use) are dropped, with the drop reasoned inline.

License note: no upstream code, script, or bundled asset from any of the three
sources is vendored or executed anywhere in this repository — only the
documented methodology is adapted into prose, per each license's attribution
terms. Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule
(recorded under TC-EXT-022-05).

## Purpose

Give every future skill this repository creates a repeatable, evidence-backed
authoring path instead of an ad hoc one: prove the gap exists before writing
prose (RED), author against this repo's own real conventions rather than a
generic upstream template (GREEN), harden against predictable rationalizations
before calling it done (REFACTOR), and close every cycle through the same
7-step registration pipeline this repository has already run for roughly a
dozen prior skill imports this session — so the new skill is never "written"
without also being "wired in."

## When to Use

- Whenever a new capability needs a governed skill under `.claude/commands/`
  — this is the EP-3 case from CLAUDE.md's Espanso-Sourced Production Rules:
  "If no skill exists for the operation: create or register the missing skill
  first, then invoke it."
- Whenever an ad hoc procedure has been repeated 2+ times across taskcards
  without a governed skill wrapping it (a durable-learning signal, not a
  one-off convenience).
- Whenever an external methodology (a new upstream skill/plugin, or — as with
  this skill itself — a synthesis of several) is being imported into this
  repository's own registry.
- **Not** for a small prose edit to an already-registered skill's existing
  file (a version bump + `Edit` is sufficient there); this skill is for
  net-new `skill_id` creation, or a rewrite substantial enough to justify
  re-running the full RED-GREEN-REFACTOR cycle from scratch.

## Steps

The outer discipline is RED-GREEN-REFACTOR (writing-skills). The GREEN phase's
internal structure is skill-writer's 6-step workflow, with Step 6 replaced by
this repository's own registration pipeline.

### Phase R — RED: Pressure-Scenario Baseline

1. **Spawn a subagent** and give it the target task the new skill is meant to
   cover, under a **pressure framing** (tight deadline, "just get it done,"
   ambiguous instructions) — deliberately the framing most likely to surface
   the corner-cutting the new skill exists to prevent. Do not give it the
   skill; it does not exist yet.
2. **Record the baseline failure verbatim** — the exact wrong shortcut,
   omitted step, or unjustified assumption the subagent made. This becomes
   the skill's evidence for existing, not a bullet-point guess at what might
   go wrong.
3. If the subagent does not fail under pressure, the skill's premise is not
   yet established — sharpen the pressure scenario (a more ambiguous prompt,
   a more plausible-looking wrong shortcut) and retry before proceeding to
   Phase G. Do not author a skill for a failure that could not be reproduced.

### Phase G — GREEN: Author (skill-writer's 6-step backbone)

**Step 1 — Resolve target, path, and shape.** Confirm the exact `skill_id`,
its `.claude/commands/<skill_id>.md` path, and whether it is net-new or a
substantial rewrite of an existing skill. Inspect this repository's own prior
art first — `.claude/commands/*.md` files with a similar `product_track` or
similar Steps shape — rather than starting from a blank template. If the
target's shape is genuinely unclear, resolve it with one direct question
(to the invoking agent/user) rather than guessing.

**Step 2 — Run synthesis when needed.** If the new skill draws on more than
one upstream methodology (as this skill itself does), collect each source's
methodology text, score its relevance, and record its provenance (repo, pinned
commit, license) — this is exactly the `synthesized_from` frontmatter pattern
this skill introduces (see "Frontmatter Fields" below). A single-source import
uses the simpler `external_skill_origin`/`external_skill_source`/
`external_skill_commit`/`external_skill_license` fields already established by
this plan's other TC-EXT-0XX skills instead.

**Step 3 — Run iteration first when improving from existing examples.** If the
new skill extends or replaces prior art (an existing skill file, a prior draft,
an upstream example), read that prior art in full before drafting — do not
draft from a mental model of what it probably contains.

**Step 4 — Author the skill artifact.** Write `.claude/commands/<skill_id>.md`
as a **router, not an encyclopedia** — Purpose, When to Use, Steps, Output
Format, Allowed/Forbidden Paths, Constraints, Idempotency Contract — matching
**this repository's own established frontmatter and section conventions**
(see "Frontmatter Fields" below), not the generic `name:`/`description:`-only
shape a from-scratch SKILL.md would use elsewhere. Reference — do not inline —
any long reusable content a future skill might also need.

**Step 5 — Optimize description/trigger quality.** This repo's `.claude/commands/*.md`
files do not carry a standalone `description: "Use when..."` frontmatter
field the way a portable Claude Skill package does; the equivalent trigger
surface is the "When to Use" section (Step 4) plus the `purpose` string that
gets copied into `.supervisor/skill-registry.yaml`. Validate both:
should-trigger cases (the concrete scenarios that must invoke this skill) and
should-not-trigger cases (adjacent scenarios an already-existing skill already
owns — check `/detect-duplicate-skills` and `/check-skill-coverage` here, not
only at registration time) are both explicit, not implied.

**Step 6 — Register and validate.** Upstream's own Step 6 is "apply repository
registration steps for the active layout... run quick validation for
structural checks" — a placeholder for whatever a target repo's pipeline
happens to be. This repository already has a concrete one, proven across
roughly a dozen prior skill imports this session. Run the full pipeline below
— every step is mandatory, none are placeholders.

### Phase F — REFACTOR: Close Loopholes, Re-Test

1. **Identify new rationalizations.** Ask: how would an agent under the same
   pressure framing as Phase R talk itself out of following this skill once
   it exists ("this is a trivial one-off, the full pipeline is overkill,"
   "I'll register it later," "this doesn't really need Phase R because I
   already know what's wrong")? List each plausible rationalization found.
2. **Add explicit counters** for each rationalization identified — a Stop
   Condition, a Mandatory Validation, or a sentence in the relevant Step that
   forecloses the shortcut by name, not just by implication.
3. **Re-test.** Re-run the Phase R pressure scenario, this time with the new
   skill available to the subagent. Confirm the previously-recorded baseline
   failure (Phase R, step 2) no longer occurs, and record the delta. A REFACTOR
   pass that finds no new rationalization to counter is a valid, idempotent
   no-op — it does not need to invent one.

## Frontmatter Fields (this repository's real convention, not upstream's generic shape)

Every skill authored by this workflow carries, at minimum:
`version`, `last-updated`, `phase-available`, `gate-required`, `skill_type`,
`idempotency`, `loc_budget`, `test_path`, `risk_level`, `created-by`,
`product_track`. A skill adapted from exactly one external source additionally
carries `external_skill_origin: true` + `external_skill_source` +
`external_skill_commit` + `external_skill_license` (see `test-driven-development.md`,
`skill-scanner.md`, `sharp-edges.md` for precedent). A skill synthesized from
**more than one** external source — like this one — uses `synthesized_from:`
instead: a list of `{source, skill, license, commit}` entries, one per
upstream methodology drawn on. Do not force a multi-source synthesis into the
single-source field shape; the list form is the correct one whenever more than
one upstream methodology is cited in the same file's Attribution section.

## FF's Real Registration Pipeline (Phase G Step 6, expanded — MANDATORY, no step is optional)

This replaces, in full, every upstream "register/deploy" step from all three
synthesized sources. It is the same pipeline this session has already run,
successfully, roughly a dozen times prior to this skill's own registration.

1. **Security-review the drafted file.** Run `/skill-scanner` against the new
   `.claude/commands/<skill_id>.md` (mandatory gate per TC-EXT-012, before any
   registry insertion).
2. **Preflight-validate the proposed entry.**
   `python tools/supervisor/preflight_skill_entry.py <entry.yaml or --inline>`
   — must PASS (no `FIELD_MISSING`/`STATUS_INVALID`/`COMMAND_FILE_MISSING`)
   before insertion.
3. **Insert the entry into `.supervisor/skill-registry.yaml`.** This file is
   large and under active concurrent edit by other taskcards in this same
   plan wave — **re-read it fresh immediately before writing**, and insert the
   new entry alongside unfamiliar content added since the last read rather
   than overwriting around it.
4. **Sync the command registry, twice.**
   `python tools/supervisor/sync_skill_command_registry.py` — run once to
   propagate the new entry into `.claude/commands/command-registry.yaml`, then
   run a **second time** and confirm `auto_repaired: 0` — the required
   rerun-idempotency proof (§9 Validation Matrix of the governing plan).
5. **Check for duplicates.** Run `/detect-duplicate-skills` and confirm the
   new `skill_id` produces no `DUPLICATE` (identical `purpose` + `command_file`)
   finding against any existing active skill. An `OVERLAPPING` finding is not
   automatically disqualifying but must be reconciled (ownership boundary
   clarified in either file) before closing.
6. **Validate skill contracts.**
   `python tools/supervisor/validate_skill_contracts.py` — confirm the new
   skill adds **0 new FAIL** results (required fields present,
   `command_file` exists, status is a valid enum value).
7. **MANDATORY FINAL STEP — layer-attribute via the extended reconciler.**
   Run `/reconcile-layer-index` (TC-EXT-005's extended version, which added
   step 6 to that skill: comparing `plans/layers/index.yaml`'s `skill_ids`
   array against `.supervisor/skill-registry.yaml` per layer) and confirm the
   new `skill_id` is attributed to its layer — append it to that layer's
   `skill_ids`, `command_ids`, and `evidence_paths` entries in
   `plans/layers/index.yaml` (re-read that file fresh immediately before
   writing, for the same concurrent-edit reason as step 3 above), then
   re-run the reconciler and confirm it reports the skill as attributed, not
   as an unattributed addition.

   **This step is not optional and is not deferrable to a later session.**
   Per the plan governing this skill's own creation: "every new skill
   registration must run through the TC-EXT-005 extended reconciler... this
   is the integration guarantee," and the plan's own Validation Matrix lists
   "TC-EXT-005 extended `/reconcile-layer-index` shows 0 unattributed" as a
   mandatory `integration_test` for **every** new `skill_id`, with the
   parenthetical "(the integration guarantee)." A skill that is drafted,
   security-scanned, preflighted, registered, synced, and contract-validated
   but never layer-attributed is still an orphan from the layer-governance
   system's point of view — invisible to `/reconcile-layer-index`'s own
   consistency audit, and therefore silently exempt from every future
   layer-health check that depends on that audit. Registration without this
   step is **not** a completed registration.

## Explicit Exclusion

`writing-skills`' Deployment checklist item — publish the finished skill file
to the author's own copy of the upstream source repository, then open a
review request to merge it back upstream — is **not** part of this skill's
Step 6, anywhere, under any framing. This repository's skill registry
(`.supervisor/skill-registry.yaml`, `.claude/commands/command-registry.yaml`,
`plans/layers/index.yaml`) is internal governance machinery, not a public
skill marketplace with an upstream project to publish back to. The 7-step
pipeline above is the complete substitute, end to end — there is no residual
upstream deployment action left to perform after step 7.

## Anti-Pattern Quick Reference (review checklist, adapted from workflow-skill-design)

Run this checklist against the drafted file during Phase F (REFACTOR), before
Step 6/registration. Adapted for this repository's prompt-only
`.claude/commands/*.md` format — no bundled executable, no multi-file package,
no plugin manifest. Four upstream anti-pattern categories that presuppose a
multi-file skill package or a bundled executable tool are dropped outright
(noted at the end) rather than force-fit into a format that has neither.

| ID | Anti-Pattern | What it looks like in this repo's skills | Check |
|---|---|---|---|
| AP-1 | Vague trigger | "When to Use" lists a generic goal instead of concrete scenarios; an agent can't tell from the description alone whether this skill or another applies | Concrete should-trigger scenarios present (Phase G Step 5) |
| AP-2 | No should-not-trigger boundary | Skill over-triggers into a neighboring skill's territory (over-claims scope) | Explicit "Not for..." carve-out present when overlap risk exists |
| AP-3 | Unstructured prose instead of numbered phases | Steps section is a paragraph, not an ordered list an agent can execute one item at a time | Steps are numbered and independently completable |
| AP-4 | Blurred phase boundaries | Two steps' completion criteria overlap so it's unclear when one ends and the next begins | Each step has its own distinct completion signal |
| AP-5 | Tools mismatch (tools-match-executor) | A read-only reviewer skill's Allowed Paths imply write/Bash access it never needs, or vice versa | Allowed Paths granted match exactly what the Steps require, no more |
| AP-6 | Missing Allowed/Forbidden Paths | Skill has no explicit path scope at all | Both sections present and non-empty |
| AP-7 | Monolithic file (progressive-disclosure, <500 lines) | Single `.md` file balloons past ~500 lines by inlining everything instead of referencing | File kept under budget; long reusable content referenced, not inlined (this file's own line count is a live instance of this check) |
| AP-8 | Encyclopedic reference embedded inline | A large static reference table that rarely changes is duplicated inline instead of pointed to | Large static references cited by path, not copy-pasted, where a stable reference file already exists |
| AP-9 | No worked example for non-trivial logic | A multi-branch Step is described abstractly with no concrete example of the expected output | Output Format section includes a literal example shape |
| AP-10 | Non-scalable tool pattern | A Step implies "repeat this one call per item" for an unbounded item count instead of a batch-capable approach | Steps that could face N>~20 items name a batch mechanism, not a per-item loop |
| AP-11 | Missing idempotency contract | No statement of what happens on a second run against the same input | Idempotency Contract section present and specific |
| AP-12 | No stop conditions | Skill has no explicit "stop here" signal for a bad state, only implicit assumptions of success | Stop Conditions / Mandatory Validations enumerate concrete halt triggers |
| AP-13 | No output format | Steps produce a result with no specified shape, making downstream consumption ad hoc | Output Format section present |
| AP-14 | Missing attribution on adapted content | Methodology text adapted from an external source with no license/commit citation | Attribution section present with source, license, and pinned commit for every external methodology used |
| AP-15 | Wrong pattern selection | A destructive or hard-to-reverse operation is framed as a plain Sequential Pipeline with no approval/precondition gate, when a Safety Gate pattern applies | Destructive/external-call steps (e.g. `gh api` replies, registry mutation) are gated behind an explicit precondition or approval, matching the Safety Gate pattern rather than a bare Sequential Pipeline |
| AP-16 | Orphaned from governance | Skill is drafted and even registered, but never appears in any layer's `skill_ids` | Step 7 of the registration pipeline (mandatory layer-attribution) always closes the loop |

Dropped as not applicable to this repository's prompt-only skill format (no
bundled executable, no multi-file package, no plugin manifest to misconfigure):
anti-patterns concerning bundled-script packaging/dependency declarations,
plugin-manifest misconfiguration, multi-file skill-directory layout mistakes,
and hook-wiring mistakes (`hooks.json`/`SessionStart`/`Stop` hook errors) —
this repository's skills are single-file prompt specs with no hook mechanism
of their own (see `/skill-improver`'s explicit hook exclusion, TC-EXT-023, for
the same reasoning applied to a different import).

### Pattern Selection (brief context for Phase G Step 1)

workflow-skill-design's decision tree names five shapes a skill's Steps can
take: **Routing** (dispatch to one of several sub-procedures based on input),
**Sequential Pipeline** (fixed ordered steps, no branching), **Linear
Progression** (a cycle that repeats, e.g. this skill's own RED-GREEN-REFACTOR
outer loop), **Safety Gate** (an approval/precondition check before a
consequential action), and **Task-Driven** (steps vary by the specific task
handed in). Resolve which shape the new skill's Steps actually are (Phase G
Step 1) before drafting — most authoring mistakes in AP-3/AP-4/AP-15 above
trace back to picking Sequential Pipeline by default when the skill's real
Steps are actually Safety Gate (a consequential action needs a precondition
first) or Task-Driven (behavior branches on what's handed in).

## Mandatory Validations

- `pressure_scenario_baseline_documented` — Phase R produced a verbatim,
  reproduced baseline failure before Phase G began.
- `ff_conventions_used_not_upstream_generic` — the drafted file's frontmatter
  and section structure match this repository's established convention
  (Frontmatter Fields above), not a bare upstream `name:`/`description:`-only
  template.
- `synthesized_from_used_for_multi_source` — a skill drawing on more than one
  external methodology uses the `synthesized_from:` list field, not the
  single-source `external_skill_origin` field shape.
- `anti_pattern_checklist_applied` — every applicable AP-N item above was
  checked against the drafted file during Phase F, with the outcome recorded.
- `registration_pipeline_completed` — all 7 steps of the FF Real Registration
  Pipeline ran, in order, with no step skipped.
- `layer_attribution_completed` — step 7 (mandatory, non-optional) completed:
  the new `skill_id` appears in the correct layer's `skill_ids`, `command_ids`,
  and `evidence_paths` in `plans/layers/index.yaml`, confirmed by a
  post-write `/reconcile-layer-index` run.
- `no_upstream_deployment_step_present` — the drafted file contains no
  reference to publishing the skill to an external copy of a source
  repository or opening a review request back to one; the negative-control
  check for this is a plain-text scan of the finished file for that concept.

## Output Format

```
## Skill Creation: <skill_id>

### Phase R — RED
- Pressure scenario: <one sentence>
- Baseline failure (verbatim): <what the subagent did wrong>

### Phase G — GREEN
- Step 1 target/path/shape: <skill_id, path, net-new|rewrite>
- Step 2 synthesis sources (if any): <source, license, commit> x N
- Step 3 prior art read: <path(s), or "none — net-new">
- Step 4 artifact authored: <path>
- Step 5 trigger validation: should-trigger / should-not-trigger cases listed

### Phase F — REFACTOR
- Rationalizations identified: <list>
- Counters added: <list, mapped 1:1 to rationalizations>
- Re-test result: <baseline failure no longer occurs — delta described>

### Registration Pipeline (7/7)
1. skill-scanner: <verdict>
2. preflight: <PASS/FAIL>
3. registry insertion: <done>
4. sync x2: <auto_repaired on 2nd run>
5. duplicate check: <verdict>
6. contract validation: <PASS/FAIL, new FAIL count>
7. layer attribution: <layer_id, reconciler verdict>
```

## Allowed Paths

- `.claude/commands/<new-skill-id>.md` — write (the new/rewritten skill file)
- `.supervisor/skill-registry.yaml` — insert one new entry (or update one
  existing entry on a rewrite); re-read fresh immediately before writing
- `.claude/commands/command-registry.yaml` — written only via
  `sync_skill_command_registry.py`, never edited directly by this skill
- `plans/layers/index.yaml` — append the new `skill_id` to exactly one
  layer's `skill_ids`/`command_ids`/`evidence_paths`; re-read fresh
  immediately before writing
- `.local/evidences/**` — cycle evidence output (write)
- Any existing `.claude/commands/*.md` file — read only, for Phase G Step 1
  (prior art) and Step 3 (iteration from existing examples)

## Forbidden Paths

- `src/**` — this skill creates skill-definition files only; it never touches
  product source and creates no product-source mutation pathway of its own
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a skill-creation cycle
- Any per-chat plan file under `plans/.claude/**` — skill creation is a
  distinct concern from plan bookkeeping; a taskcard executing this skill
  amends its own plan file through its own normal taskcard-update mechanism,
  not through this skill
- `plans/strategic/**` — strategic plans are read-only from this skill's
  perspective
- `registry/found-issue-register.yaml`, `registry/root-cause-register.yaml` —
  written only via `/found-issue-ownership`, not by this skill

## Stop Conditions

- Stop before Phase G if Phase R could not reproduce a baseline failure — the
  skill's premise is unestablished (see Phase R, step 3).
- Stop before Step 6/registration if `/skill-scanner` returns any Critical or
  High finding — resolve it in the drafted file first.
- Stop before completing the registration pipeline if step 4's second
  `sync_skill_command_registry.py` run reports nonzero `auto_repaired` — the
  first run did not fully converge; investigate before proceeding to step 5.
- Stop and reconcile before proceeding past step 5 if `/detect-duplicate-skills`
  reports `DUPLICATE` against an existing active skill.
- **Never** consider the cycle closed while step 7 (layer attribution) is
  outstanding — this is the one step this skill's own governing plan calls
  a mandatory, non-deferrable integration guarantee, not an optional nicety.

## Idempotency Contract

Given the same target capability description, the same drafted skill file
content, and the same repository state, re-running the registration pipeline
(steps 1-7) against an already-registered `skill_id` updates the existing
entry in place rather than creating a duplicate — `sync_skill_command_registry.py`
is itself idempotent (`auto_repaired: 0` on a clean second run) and
`/reconcile-layer-index` is read-only and reports the same attribution state
each time it is re-run against unchanged inputs. Re-running Phase F against an
already-hardened file that surfaces no new rationalization is a valid no-op.

## Governance Note

This skill is itself an instance of the pipeline it describes: drafted under
TC-EXT-022-01 through -04, cleared by `/skill-scanner`, registered via
`/preflight-skill-entry` + `.supervisor/skill-registry.yaml` insertion, synced
via `sync_skill_command_registry.py` (run twice), checked via
`/detect-duplicate-skills`, validated via `validate_skill_contracts.py`, and
layer-attributed via `/reconcile-layer-index` — all under TC-EXT-022-05. Its
`risk_level: MEDIUM` reflects that it creates and edits real skill-definition
and registry files (the same bounded domain this repository's own
`create-taskcard`-class skills already mutate routinely), not that it touches
product source or any external system.
