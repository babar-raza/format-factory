# AI Authority Boundary

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 43 + local-memory-sync sprint 2026-06-04

## Core Rule

**AI thinks and drafts. Evidence decides.**

AI is not authority, but AI is allowed to act aggressively as a non-authoritative cognitive layer.

---

## What AI MAY Do

All of the following are permitted. All outputs must be labeled `ai_draft`.

### Observation and Analysis
- Observe product state
- Reason about gaps, priorities, risks
- Rank product gaps by impact
- Summarize sprint state

### Planning and Design
- Plan implementation approaches
- Design APIs and test structures
- Draft implementation code
- Propose handoffs to Mainstream

### Critique and Routing
- Critique evidence quality
- Detect drift between goals and actions
- Route blockers to the right stream
- Propose sprint adaptation

### Acceleration
- Extract requirements from format specs (LLM-assisted)
- Mine source patterns for code generation
- Generate test cases from spec requirements
- Manage sprint-to-sprint learning loop
- Propose implementation designs (labeled ai_draft)

---

## What AI MAY NOT Do

The following actions are FORBIDDEN regardless of AI confidence:

### Capability Authority
- Mark a capability as complete
- Update capability matrix as authoritative (only Mainstream test results are authoritative)
- Override test results

### Gate Authority
- Approve any gate (G1-G11)
- Self-approve commercial readiness
- Override supervisor decisions

### Evidence Authority
- Suppress test failures
- Change evidence verdicts
- Skip required evidence steps

### System Authority
- Push to git remote
- Publish packages
- Write secrets or credentials
- Modify MCP configuration
- Install external tools (Ruflo, Superpowers, GhidraMCP)
- Become the final authority on any decision

---

## AI Output Labeling

All AI-generated output in Acceleration must be labeled:

```
ai_draft: true
authority: non-authoritative
requires_human_verification: true
```

AI output in Mainstream (e.g., code-generation handoffs received from Acceleration) must be:
1. Reviewed by the Mainstream executor before use
2. Tested with actual test suite before crediting
3. Not claimed as product output until tests pass

---

## Live / Fixture / Skipped Modes

| Mode | Meaning |
|---|---|
| live | AI calls a real external API/model in real time |
| fixture | AI uses a cached/pre-recorded response for testing |
| skipped | AI step is skipped (no model call, no fixture) |

Mode must be declared at sprint start. `live` mode requires approved gateway provider only.

---

## Approved AI Gateway

Only approved provider endpoints may be used in `live` mode:
- Anthropic Claude API (via approved credentials)
- No unapproved third-party AI endpoints

---

## Acceleration vs. Supervisor AI Advisory

| Context | Role |
|---|---|
| Acceleration-B | Active AI cognitive layer — proposes, drafts, ranks, designs |
| Supervisor AI advisory | Passive observer — annotates, flags, summarizes (never decides) |

The supervisor's continuation decisions are deterministic (code-based), not AI-voted.
