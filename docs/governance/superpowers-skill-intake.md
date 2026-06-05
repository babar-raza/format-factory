# Superpowers Marketplace Skill Intake

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Purpose

Superpowers Marketplace provides external skill patterns and Claude Code workflow examples. This document defines how Superpowers skills are safely intake'd into the Format Factory project.

## Placement

Skills / Governed Execution stream.

## What Superpowers Provides

- External skill-pattern library
- Claude Code workflow examples
- Brainstorming/planning/execution pattern source
- Possible local skill wrappers after normalization

## Hard Prohibitions

- No blind plugin install
- No direct registry import
- No SessionStart or context injection until reviewed
- No skill usage in any stream without prior normalization
- Do not install Superpowers plugins into Claude Code without explicit Supervisor approval and human authorization

## Normalization Process

Every Superpowers skill that may be used in Format Factory MUST be normalized:

### Step 1: Review
- Read the skill description and review its scope
- Identify what files it reads/writes
- Identify what commands it runs
- Identify what external services it calls

### Step 2: Risk Classification
| Risk | Criteria |
|---|---|
| LOW | Read-only, no external calls, no workspace mutation |
| MEDIUM | Limited write, no secrets, bounded scope |
| HIGH | Workspace mutation, daemon, hooks, external calls |
| CRITICAL | Secret access, git push, MCP modification |

### Step 3: Local Wrapper Creation
Create a local wrapper in `.claude/commands/` with:
- `allowed_paths`: exact list of files the skill may read/write
- `forbidden_paths`: explicit list of forbidden paths
- `validation_command`: command to verify output correctness
- `transcript_schema`: expected output format
- `rollback_plan`: how to undo the skill's effects
- `evidence_rules`: what counts as evidence of completion
- `activation_gate`: what approval is required before first use

### Step 4: Registry Entry
Add to `.supervisor/skill-registry.yaml` with:
```yaml
superpowers_origin: true
superpowers_skill_name: <original_name>
risk_level: LOW|MEDIUM|HIGH|CRITICAL
normalized_by: <sprint_id>
activation_gate: <gate_level>
```

### Step 5: Activation Gate
| Risk Level | Gate Required |
|---|---|
| LOW | Supervisor review |
| MEDIUM | Supervisor approval |
| HIGH | Supervisor + human authorization |
| CRITICAL | Not permitted |

## Mainstream Consumption

Skills normalized through this process become available to Mainstream as governed execution tools. Mainstream may use a normalized skill without re-reviewing it as long as:
- The skill registry entry is current
- The skill version has not changed
- The activation gate has been cleared
