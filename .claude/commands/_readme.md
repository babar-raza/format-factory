# Project Commands — format-factory

**Document type:** Configuration Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-15
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

## Implemented Methodology Commands

The following commands are active and available now. When a command exists for a methodology
task, agents must use it rather than reinventing behavior ad hoc.

| Command | File | Purpose | Mode | Creates Files | Commits | Methodology Doc | Template |
|---------|------|---------|------|--------------|---------|----------------|---------|
| `/plan-hardening` | [plan-hardening.md](plan-hardening.md) | Apply 22-item hardening checklist to a plan | PLAN MODE | No | No | [docs/plan-hardening-checklist.md](../docs/plan-hardening-checklist.md) | [plan-hardening-prompt-template.md](../docs/prompts/plan-hardening-prompt-template.md) |
| `/execution-handoff` | [execution-handoff.md](execution-handoff.md) | Convert hardened plan to full single-go execution prompt | PLAN MODE | No | No | [docs/agent-execution-handoff-standard.md](../docs/agent-execution-handoff-standard.md) | [execution-handoff-prompt-template.md](../docs/prompts/execution-handoff-prompt-template.md) |
| `/evidence-review-next-prompt` | [evidence-review-next-prompt.md](evidence-review-next-prompt.md) | Review evidence bundle, challenge claims, produce next prompt | PLAN MODE | No | No | [docs/planning-methodology.md](../docs/planning-methodology.md) | [evidence-bundle-review-prompt-template.md](../docs/prompts/evidence-bundle-review-prompt-template.md) |
| `/memory-sprint` | [memory-sprint.md](memory-sprint.md) | Full memory sprint workflow: capture decisions, update memory, build bundle | EXECUTION MODE | Yes | Yes | [docs/planning-methodology.md](../docs/planning-methodology.md) | [memory-sprint-prompt-template.md](../docs/prompts/memory-sprint-prompt-template.md) |
| `/export-plan-context` | [export-plan-context.md](export-plan-context.md) | Bundle long-term plan context files into a zip for sharing with an LLM | EXECUTION MODE | No | No | — | — |
| `/add-dotnet-api` | [add-dotnet-api.md](add-dotnet-api.md) | Add one bounded .NET API through ledger validation | EXECUTION MODE | Yes | No | [product-factory-acceleration-layer.md](../../docs/product-factory/product-factory-acceleration-layer.md) | N/A |
| `/add-python-api` | [add-python-api.md](add-python-api.md) | Add one bounded Python API through ledger validation | EXECUTION MODE | Yes | No | [product-factory-acceleration-layer.md](../../docs/product-factory/product-factory-acceleration-layer.md) | N/A |
| `/add-dogfood-export` | [add-dogfood-export.md](add-dogfood-export.md) | Add one Format Factory-backed export with reload proof | EXECUTION MODE | Yes | No | [product-factory-acceleration-layer.md](../../docs/product-factory/product-factory-acceleration-layer.md) | N/A |
| `/update-capability-matrix` | [update-capability-matrix.md](update-capability-matrix.md) | Reconcile proven POC status without gate authority changes | EXECUTION MODE | Yes | No | [product-factory-acceleration-layer.md](../../docs/product-factory/product-factory-acceleration-layer.md) | N/A |

See [docs/agent-methodology-index.md](../docs/agent-methodology-index.md) for the full methodology entry point.

---

## Planned Commands (Phase 1 -- TC-0004)

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

> **NOTE:** Implementing any planned command requires first removing its `Write(...)` deny entry from `.claude/settings.json`. Deny entries exist for all 7 planned commands (lines 105–111). This settings update must occur in an authorized sprint before TC-0004 execution. See TC-0004 PREREQUISITES section.

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
