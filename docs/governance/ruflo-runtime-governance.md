# Ruflo Runtime Governance

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Purpose

Ruflo is an optional runtime orchestration tool. This document defines how Ruflo is governed in the Format Factory project.

## Placement

- Primary: Supervisor + Mainstream
- Secondary: Acceleration (learning/telemetry only, if Supervisor-approved)

## Modes and Transitions

| Mode | Entry Condition | Exit Condition |
|---|---|---|
| ABSENT | Ruflo not detected | Ruflo installed and detected |
| AUDIT_ONLY | Ruflo detected, no approval for active use | Supervisor approves PLUGIN_LITE or higher |
| PLUGIN_LITE | Supervisor approves limited plugin access | Supervisor upgrades or downgrades |
| FULL_LOOP_PENDING_APPROVAL | Full loop requested but not yet approved | Human authorizes + Supervisor confirms |
| FULL_LOOP_APPROVED | Human + Supervisor approval granted | Timeout, risk detected, or human revokes |
| DISABLED_DUE_RISK | Supervisor detects risk (workspace mutation, unexpected hooks) | Human review and explicit re-enable |

## What Ruflo Controls (when approved)

- Lane worker spawning
- Continuation loop iteration
- Memory/learning telemetry (read-only by default)

## What Ruflo Never Controls

- Taskcard closure (only evidence + grading closes taskcards)
- Gate approval (human only)
- Evidence verdict (Supervisor grading only)
- Git push/commit/publish
- Secret/credential writing
- MCP server configuration

## Fallback

If Ruflo is ABSENT or unapproved, Mainstream uses sequential lane execution. Sprint continues without Ruflo. Do not stop or block for Ruflo absence.

## Workspace Mutation Risk

Full loop Ruflo may:
- Install hooks
- Start daemons
- Access memory paths
- Mutate workspace state

These risks require Supervisor approval AND human authorization before enabling FULL_LOOP mode.

## Ruflo and the Supervisor

The Supervisor is the authority over Ruflo mode. Ruflo may not:
- Override Supervisor continuation signals
- Bypass evidence validation
- Mark items complete without Supervisor grading
