# Orphan Command Decision (Skills R105 Train D)

## Definition
An orphan command is a `.claude/commands/*.md` file that exists on disk but is not registered in `.supervisor/skill-registry.yaml`.

## R105 Decisions

### REGISTERED: evidence-review-next-prompt
- **File:** `.claude/commands/evidence-review-next-prompt.md`
- **Skill ID:** evidence-review-next-prompt
- **Status:** active
- **Reason:** Core workflow for evidence review. Used in skills/supervisor streams. Has all 12 sections. Version 1.2.

### DEFERRED: execution-handoff
- **File:** `.claude/commands/execution-handoff.md`
- **Reason:** Superseded by `/generate-execution-handoff` which is already active. The original was a manual process template; the new one is structured and governed.

### DEFERRED: export-plan-context
- **File:** `.claude/commands/export-plan-context.md`
- **Reason:** Plan context export is a low-frequency operation. Not needed for cross-stream adoption. Can be registered in a future sprint if demand arises.

### DEFERRED: memory-sprint
- **File:** `.claude/commands/memory-sprint.md`
- **Reason:** Memory sync is handled by supervisor tools (`sync_local_memory.py`). The command file is a legacy manual process.

### DEFERRED: plan-hardening
- **File:** `.claude/commands/plan-hardening.md`
- **Reason:** Plan changes require human authorization. Hardening a plan is not a self-executing skill.

## Impact
- Orphan count reduced from 5 to 4
- No orphan commands are errors — they are all valid, just not registered
- Future sprints can register more if cross-stream demand arises
