# Project Commands — format-factory

**Document type:** Configuration Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-03
**Status:** Directory created in Phase 0. Actual command files are implemented in Phase 1 via TC-0004.

---

## Purpose

This directory contains Claude Code project-level slash commands for format-factory. Commands in this directory are available to anyone using Claude Code on this project. They encode the canonical behavior for recurring acquisition pipeline tasks.

Commands are Markdown files. The filename (without `.md`) becomes the slash command name. For example, `score-format.md` creates the `/score-format` command.

---

## Why Commands Matter

Without commands, each agent session may implement recurring tasks differently, producing inconsistent results. Commands are the consistency mechanism: they define the canonical behavior for each operation so that every session produces results in the same format with the same checks.

Per `AGENTS.md` Section J: "When a project command exists for a task, the agent must use that command rather than re-implementing the task ad hoc."

---

## Planned Commands (Phase 1 — TC-0004)

The following commands are designed but not yet implemented. They will be created in Phase 1 as part of taskcard TC-0004.

| Command | File | Purpose | Phase Available | Gate Required |
|---|---|---|---|---|
| `/score-format` | `score-format.md` | Apply scoring model to a format candidate | 1 | None |
| `/create-acquisition-pack` | `create-acquisition-pack.md` | Initialize a format acquisition pack from template | 1 | Gate 1 passed |
| `/check-gate` | `check-gate.md` | Verify whether a format has met criteria for a given gate | 1 | None |
| `/create-taskcard` | `create-taskcard.md` | Create a new taskcard from the template | 1 | None |
| `/reproduce-master-plan` | `reproduce-master-plan.md` | Generate a current-state summary from repo artifacts | 1 | None |
| `/build-evidence-bundle` | `build-evidence-bundle.md` | Build and validate an evidence bundle for the current phase/gate | 1 | None |
| `/check-release-boundary` | `check-release-boundary.md` | Verify no commercial artifacts are in OSS release scope | 3+ | Gate 9 passed |

---

## Command File Format

Each command file must include a front-matter block followed by the prompt template:

```markdown
---
version: "1.0"
last-updated: "YYYY-MM-DD"
phase-available: "1"
gate-required: null
---

# /command-name

[Description of what the command does]

## Steps

[Numbered list of steps the agent must follow]

## Output Format

[What the command produces]

## Validation

[How to verify the command ran correctly]

## Changelog

- 1.0 (YYYY-MM-DD): Initial version
```

---

## Command Versioning

Version numbers follow `MAJOR.MINOR` format:
- Increment `MINOR` for additions that do not break existing behavior.
- Increment `MAJOR` for changes that alter the output format or required inputs.

The change must be noted in the command file's changelog section.

---

## Commands vs. Taskcards

Commands and taskcards are different:
- **Commands** (this directory): reusable, invokable on demand, define the canonical procedure for a recurring task. Think of them as functions.
- **Taskcards** (`taskcards/`): one-time work items with a specific goal and acceptance criteria. Think of them as tickets.

A command may be used by many taskcards. A taskcard is used exactly once (then marked complete).

---

## Adding New Commands

To propose a new command:
1. Log a gap in `plans/master-plan.md` if a command is missing for a frequently needed task.
2. Create a TC-NNNN taskcard for command design and implementation.
3. Implement the command file in this directory in the phase specified by the taskcard.

Do not create command files directly without an associated taskcard.
