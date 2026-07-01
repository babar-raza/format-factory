# Agent Swarm AI Orchestration

**Document type:** Operational guidance
**Authority level:** Normative
**Created:** 2026-05-13

---

## Purpose

This document defines how AI is used within controlled swarm execution, what AI lanes may do, and what the coordinator controls.

---

## Swarm Structure with AI Lanes

Controlled swarm execution (ACCEL-001/002) remains the preferred model for large implementation work. AI may be used within lanes, but the coordinator retains authority over:

- Lane definitions and scope
- Shared file writes (master-plan, registry, AGENTS.md, GOVERNANCE.md)
- Gate status decisions
- Evidence bundle acceptance
- Human review packet content

AI lane workers may:
- Generate code drafts within their assigned scope
- Generate test drafts
- Produce adversarial review findings
- Summarize evidence from their lane outputs
- Propose documentation updates (not commit directly)

---

## Lane AI Policy

Each AI lane must follow these rules:

1. **Declare AI use:** Lane reports must list models used, purposes, and output statuses
2. **Validate before accepting:** AI code drafts must compile and pass tests before coordinator acceptance
3. **Scope enforcement:** AI lanes must not write outside their assigned file scope
4. **No shared-file writes:** Lanes write to their assigned output files; coordinator merges to authority files
5. **No gate claims:** AI lanes must not claim gate advancement or commercial readiness
6. **Report rejected findings:** Rejected AI outputs must be reported, not silently discarded

---

## LANE K: AI Usage Documentation

**Status:** Completed (this sprint, 2026-05-13)
**Purpose:** Document all durable AI goals, expectations, patterns, and boundaries

**Allowed files for LANE K:**
- docs/ai/ai-usage-operating-model.md + .yaml
- docs/ai/ai-assisted-commercial-development.md + .yaml
- docs/ai/spec-retrieval-and-rag-policy.md + .yaml
- docs/ai/agent-swarm-ai-orchestration.md
- taskcards/AI-*.md
- memory/23-ai-usage-operating-model-20260513.md
- reports/governance/ai-usage-local-documentation-sync-20260513.*
- reports/ai/ai-usage-documentation-gap-audit-20260513.*
- AGENTS.md (narrow additions only — no removal of existing rules)
- GOVERNANCE.md (narrow additions only)

---

## Future AI Lane Types

| Lane Type | Purpose | AI Role |
|-----------|---------|---------|
| LANE-SPEC | Spec retrieval and requirement extraction | RAG over local normalized spec |
| LANE-MODEL | Object model design | Design proposal generation |
| LANE-CODE | Implementation drafting | C# code generation |
| LANE-TEST | Test generation | Test case and fixture drafting |
| LANE-REVIEW | Adversarial review | Finding classification |
| LANE-EVIDENCE | Evidence summarization | Human review packet drafting |
| LANE-K | AI documentation and governance | Documentation creation |

---

## AI Lane Reporting Requirements

Each AI lane must produce:
- **Lane output files:** Implementation, tests, or documentation as assigned
- **AI usage log:** Entries in `.local/llm-logs/<sprint-id>.jsonl`
- **Lane report:** Summary including: models used, calls made, outputs accepted/rejected, validation results

The coordinator aggregates lane reports into the sprint report and evidence bundle.

---

## Memory and Governance Sync

After any sprint using AI lanes:
- Durable AI decisions captured in memory file
- New governance rules go to AGENTS.md and/or GOVERNANCE.md via coordinator
- No lane agent writes to memory or governance directly

---

## Coordinator Checklist for AI-Assisted Sprints

Before accepting AI lane outputs:

- [ ] Code compiles (`dotnet build` or `python -m pytest`)
- [ ] Tests pass (no regressions)
- [ ] AI output status logged (ACCEPTED, REJECTED, etc.)
- [ ] No spec claims without citation
- [ ] No gate advancement claims without evidence
- [ ] No commercial readiness claims without C-level evidence
- [ ] Evidence bundle passes `BUNDLE_VALIDATION: PASS`
- [ ] Secrets not present in committed files
- [ ] `CURRENT_STATE_CONSISTENCY: PASS`

---

## Cross-References

- Controlled swarm policy: taskcards/ACCEL-001-controlled-parallel-lanes.md, ACCEL-002-larger-sprint-policy.md
- AI operating model: docs/ai/ai-usage-operating-model.md
- AI commercial patterns: docs/ai/ai-assisted-commercial-development.md
- Gate integrity: docs/gates.md
- Evidence bundle policy: AGENTS.md §Y, GOVERNANCE.md §18
