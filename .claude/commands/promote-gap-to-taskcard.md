---
version: "1.3"
last-updated: "2026-07-14"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

# /promote-gap-to-taskcard

Promote a POC capability gap to a formal taskcard in `taskcards/`.

## Usage

```
/promote-gap-to-taskcard
```

## What This Skill Does

1. **Select gap**: Reads `.local/supervisor/selected-product-gaps.json` or `.supervisor/fixtures/*.yaml`
2. **Draft taskcard**: Creates `taskcards/TC-<FORMAT>-<FEATURE>-<NNN>.md` with:
   - Title, Status: open, Priority, Assigned format/product
   - Acceptance criteria (testable)
   - Skill reference (which governed skill to use)
   - Estimated sprint
3. **Register**: Adds the new taskcard to `select_poc_gaps.py` fixture or a new YAML file
4. **Verify**: Confirms taskcard is well-formed

## Taskcard Format

```markdown
# TC-<FORMAT>-<FEATURE>-<NNN>: <Title>

**Status:** open
**Priority:** medium
**Format:** <FORMAT>
**Product:** commercial_net | foss_python
**Skill:** /add-dotnet-api | /add-python-api | /add-dogfood-export
**Estimated sprint:** R<N>

## Description

<What needs to be implemented>

## Acceptance Criteria

- [ ] <Testable criterion 1>
- [ ] <Testable criterion 2>
- [ ] Tests pass: N tests, 0 failures

## Notes

<Context, constraints, dependencies>
```

## Optional: Impediment Prioritization Scoring Aid (additive only)

> Source: `impediment-prioritization` skill (awesome-copilot, MIT). This is an OPTIONAL aid
> for ordering multiple candidate gaps before promotion — it does NOT replace this skill's
> existing `Priority` field, dependency ordering, severity classification, or
> release-blocking logic described elsewhere in this file. Use it only when a numeric
> tie-break or relative ordering across several competing gaps is useful.

When used, apply this formula **verbatim** — do not reweight, normalize, or substitute it:

```
Priority = ((ROI * (10/Cost)) + (Ease * (10/Risk))) / 2
```

Score each of the 4 criteria 1-10 before computing:

- **ROI** — Return on Investment
- **Cost** — Cost to Implement
- **Ease** — Ease of Deployment
- **Risk** — Risk Factor

Boundary checks (for verifying a correct implementation of the formula):

| ROI | Cost | Ease | Risk | Priority |
|---|---|---|---|---|
| 10 | 1 | 10 | 1 | 100 |
| 1 | 10 | 1 | 10 | 1 |

If computed, the resulting numeric score may be recorded in the taskcard's `## Notes` section
as a tie-break reference only. The taskcard's `Priority:` field (`low`/`medium`/`high`) and any
existing dependency/severity/release-blocking ordering remain authoritative.

## Evidence Required

- Taskcard file path
- Gap ID promoted
- Skill reference in taskcard
- Acceptance criteria count

## Constraints

- Taskcard ID must be unique
- Status must be `open`, `in_progress`, or `closed`
- Acceptance criteria must be testable (not vague)

## Allowed Paths

- `taskcards/` (taskcard creation)
- `.supervisor/fixtures/` (gap fixture registration)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)

## Rollback

1. Remove the taskcard file from `taskcards/`
2. Remove the fixture registration if added

## Validation

Complete when: taskcard is well-formed YAML/MD, has testable acceptance criteria, and references a valid skill.

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, gap_id, taskcard_path, taskcard_id, verdict.

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added validation, transcript requirement (Skills R101).
- 1.3 (2026-07-14): Added "Optional: Impediment Prioritization Scoring Aid" section
  (TC-EXT-019-02) — exact formula and boundary checks merged from the
  `impediment-prioritization` skill. Additive only; does not replace existing Priority
  field, dependency ordering, or severity/release-blocking logic. Frontmatter version
  also reconciled to match the changelog's existing 1.2 entry (was previously undercounted).
