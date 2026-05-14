---
memory_file: 25
title: Assistant Supervision Methodology (2026-05-13)
created_at: 2026-05-13
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
visibility: internal
publish_allowed: false
---

# Memory 25: Assistant Supervision Methodology (2026-05-13)

## 1. Why This Memory Exists

This file was created because the human (Babar Raza) observed that across the ChatGPT session
that preceded this sync, a specific working style emerged that made the project go faster,
stay honest, and catch problems before they compounded.

That working style should not be lost when a chat session ends or when a new agent starts.
This memory file captures it in a compact, durable form.

The full methodology is in `docs/assistant-supervision-methodology.md`.
The execution standards are in `docs/project-execution-standards.md`.

---

## 2. Human's Expectation From Future Chats

The human expects future chats and agents to:

1. Inspect evidence before accepting any sprint claim.
2. Challenge "PASS", "complete", "ready", and "commercial-ready" claims.
3. Provide complete ready-to-send prompts — not vague guidance.
4. Use controlled swarm execution for related work rather than micro-sprinting.
5. Use AI aggressively for acceleration, but govern every output.
6. Design for repeatability — prefer systems over one-off patches.
7. Sync durable decisions to local memory before the session ends.
8. Never overstate what has been achieved.
9. Distinguish between prototype, vertical slice, and commercial product.
10. Always drive to a clear verdict and a specific next action.

---

## 3. Evidence-First Supervision

Never accept a sprint claim from the final response text alone.

When reviewing a sprint, inspect:
- The evidence bundle (ZIP file)
- The evidence contract
- `bundle-metadata/final-bundle-validation-proof.txt` — is it a real PASS, not a placeholder?
- `bundle-metadata/git-status-final.txt` — are there unintended dirty files?
- `bundle-metadata/no-scope-drift-report.md`
- The actual source files and test output referenced in the claims

When evidence is missing, say what is missing and provide an IV prompt.
Do not guess at project state.

---

## 4. Controlled Swarm Execution

Prefer larger governed swarms over serial micro-sprints.

A governed swarm has:
- A sprint ID
- A coordinator lane
- Per-lane ownership (one owner per lane, one scope per lane)
- Shared-file control (no two lanes edit the same file)
- Dirty-state preflight
- Overlap check before editing begins
- Lane-local evidence reports
- Final integration by coordinator
- Cross-lane consistency validation
- Single evidence bundle

Do NOT run uncontrolled parallel lanes that share files without explicit ownership.

---

## 5. Ready-to-Send Prompts

When advising on next steps, provide a complete ready-to-send prompt.

The prompt must include:
- Mode label (PLAN / EXECUTION / IV / REPAIR)
- Sprint ID
- Repository path
- Current accepted state
- Scope and non-goals
- Lane definitions (if multi-lane)
- Safety rules (always include)
- Allowed files (exact paths)
- Prohibited files
- Validation commands
- Evidence contract requirements
- Final response format
- Exact next step

Do not say "ask the agent to check X." Write the prompt.

---

## 6. System Design Preference

When the human asks for help, design for the system, not the session.

Prefer:
- Reusable commands and skills over repeated manual prompts
- Generated requirements over static assumptions
- Evidence contracts over informal reports
- Structured taskcards over vague TODOs
- Versioned pipelines over one-off patches
- Local memory over chat-only context

Patterns already established in the project:
- `tools/evidence/contracts/` — evidence contracts
- `generated-requirements/` — AI-generated, validated requirements
- `taskcards/` — taskcard system
- `memory/` — local memory
- `schemas/` — schema validation
- Gates 1-11 — quality gates

---

## 7. AI Acceleration With Governance

Use AI where it helps. Do not use AI as final authority.

AI is authorized for:
retrieval, requirements generation, code drafting, test generation, gap analysis,
adversarial review, evidence summarization, skill generation, orchestration

AI must NOT be used for:
gate approval, inventing spec facts, claiming readiness without evidence,
bypassing tests, hiding uncertainty

AI output lifecycle:
→ validate (schema if structured)
→ test (if code)
→ verifier review (if requirements)
→ accept/reject explicitly
→ log in .local/llm-logs/ (if repo-changing)
→ cite source where applicable

---

## 8. Generated-Requirements-First Direction

For commercial format work:
1. Human requirements define goals.
2. System generates per-format requirements using governed AI.
3. Requirements must come from local specs, format understanding, product goals.
4. Generated requirements must be schema-validated and verifier-reviewed.
5. Only accepted requirement IDs (`ACCEPTED_FOR_VERTICAL_SLICE`) feed implementation.
6. Implementation reports which IDs were consumed, implemented, deferred, rejected.

Current state: FODS and FODT requirements are generated and verifier-reviewed.
They are PENDING independent verification (DEC-034 IV) before implementation can consume them.

---

## 9. Gate and Evidence Safety

Key gates:
- Gates 1-11 require human approval — no exceptions
- Gate 11 requires C7+ capability, all sub-gate evidence, and human approval
- DEC-034: IV in a separate session before human review
- commercial_product_ready stays false until criteria are actually met

Current: FODS and FODT are at C4-C6-vertical-slice. Gate 11 NOT approved.

Evidence:
- Evidence bundles required for every major sprint
- BUNDLE_VALIDATION: PASS required before accepting any sprint
- Evidence contracts define the floor — no short-cutting

---

## 10. New-Chat Behavior

When starting a new chat, read these in order:
1. `docs/fresh-chat-project-bootstrap.md`
2. `memory/24-chatgpt-session-memory-sync-20260513.md`
3. `memory/25-assistant-supervision-methodology-20260513.md` (this file)
4. `docs/assistant-supervision-methodology.md`
5. `docs/project-execution-standards.md`
6. `plans/master-plan.md` Section 33

Then:
- Do not accept project state from ChatGPT saved memory — use local files
- Do not claim the project is further along than the registry shows
- Do not approve gates
- Do not proceed with implementation without accepted requirement IDs

---

## 11. Next-Agent Behavior Checklist

Before starting any sprint, confirm:

- [ ] Read all files in "Standard Local Files to Read First" (docs/project-execution-standards.md §10)
- [ ] Checked registry/format-registry.yaml for current gate status
- [ ] Checked plans/master-plan.md §33 for current state
- [ ] Reviewed most recent memory file for session continuity
- [ ] Confirmed no active sprint lock (`.local/active-sprint-lock.json`)
- [ ] Confirmed git status is clean or dirty-state is classified
- [ ] Verified accepted requirement IDs exist (if implementation sprint)
- [ ] Prepared complete evidence contract for the sprint
- [ ] Safety rules clearly stated in the prompt

Before ending any sprint, confirm:

- [ ] CURRENT_STATE_CONSISTENCY: PASS
- [ ] BUNDLE_VALIDATION: PASS (--check-no-pending)
- [ ] No PENDING markers in committed files
- [ ] final-bundle-validation-proof.txt is real PASS, not placeholder
- [ ] git-safety-policy-check.md in bundle metadata
- [ ] NO_STASH_RESET_RESTORE_CLEAN_USED: YES in final response
- [ ] Memory synced if durable direction changed
- [ ] EVIDENCE_BUNDLE: <path> as final line
