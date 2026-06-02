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

## Constraints

- Taskcard ID must be unique
- Status must be `open`, `in_progress`, or `closed`
- Acceptance criteria must be testable (not vague)
