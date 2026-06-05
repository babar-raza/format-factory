---
version: "1.1"
last-updated: "2026-06-03"
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
