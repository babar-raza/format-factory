# AI Authority Boundary

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## May/May-Not Table (18 rows)

| # | Subject | Action | Authority Rule |
|---|---------|--------|---------------|
| 1 | AI tools | Read poc-targets.yaml | MAY — read-only |
| 2 | AI tools | Modify poc-targets.yaml | MAY NOT |
| 3 | AI tools | Read src/ files | MAY — read-only corpus |
| 4 | AI tools | Create files in src/ | MAY NOT |
| 5 | AI tools | Write to reports/ | MAY — advisory outputs only |
| 6 | AI tools | Write to .supervisor/ | MAY NOT (except ai-usage-ledger.jsonl) |
| 7 | AI tools | Use gateway_chat() | MAY — via approved gateway only |
| 8 | AI tools | Import openai/anthropic directly | MAY NOT |
| 9 | AI tools | Write authority_state: authoritative | MAY NOT — must stay ai_draft |
| 10 | AI tools | Block autonomous-cycle on MACHINERY_CREEP | MAY NOT — advisory only |
| 11 | AI tools | Produce fixture as live AI output in evidence | MAY NOT |
| 12 | AI tools | Update capability matrix | MAY NOT without test evidence |
| 13 | ai_sprint_manager | Use fixture for agentic_low_risk | MAY NOT — skipped mode required |
| 14 | ai_evidence_critic | Modify evidence declaration | MAY NOT |
| 15 | ai_learning_loop | Overwrite sprint history | MAY NOT — append only |
| 16 | mainstream_acceleration_packet | Set external_tool_activation_required: true | MAY NOT |
| 17 | Any AI tool | Store API key values in output | MAY NOT |
| 18 | Any AI tool | Advance artifact past ai_draft | MAY NOT without test evidence |

## 12-State Artifact Lifecycle

AI tools may only produce artifacts in state 1 (ai_draft):

```
1: ai_draft           ← All AI tool outputs start and stay here
2: runtime_advisory   ← External tool signals only (Ruflo)
3: proposed           ← Acceleration internal (non-AI)
4: under_review       ← Supervisor pipeline
5: review_blocked     ← Supervisor pipeline
6: accepted_with_limitations ← Human reviewer
7: accepted           ← Human reviewer
8: rejected           ← Supervisor pipeline
9: deferred           ← Human decision
10: authoritative_after_gate ← Gate approval
11: withdrawn         ← Supervisor pipeline
12: archived          ← Supervisor pipeline
```

Only test evidence + human gates advance artifacts past state 2.
