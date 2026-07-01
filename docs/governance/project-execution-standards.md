---
document_type: standards
title: Project Execution Standards
version: "1.0"
created_at: "2026-05-13"
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
visibility: internal
publish_allowed: false
authority: standards
---

# Format Factory — Project Execution Standards

This document provides a concise reference for how every execution sprint in Format Factory
must be conducted. Read it alongside `docs/automation/assistant-supervision-methodology.md`.

---

## 1. Standard Sprint Lifecycle

Every execution sprint follows this lifecycle. No step may be skipped.

| Step | Name | What happens |
|------|------|-------------|
| 1 | Preflight | Read authority files; check git status; verify dirty-state classification; check active sprint lock; verify no forbidden files are staged |
| 2 | Lane execution | Each lane executes its authorized scope; no lane modifies another lane's files |
| 3 | Integration | Coordinator lane integrates all lane outputs; confirms consistency |
| 4 | Validation | Run all validation commands; confirm PASS for all required checks |
| 5 | No-scope-drift | Create or verify no-scope-drift-report.md; confirm all staged files are in authorized paths |
| 6 | Consistency check | Run `python tools/evidence/check_current_state_consistency.py`; confirm CURRENT_STATE_CONSISTENCY: PASS |
| 7 | Evidence bundle | Build bundle with `tools/evidence/build_evidence_bundle.py`; validate with `validate_evidence_bundle.py --check-no-pending`; confirm BUNDLE_VALIDATION: PASS |
| 8 | Exact-path commit | Stage exact authorized paths only; verify no unintended files staged; commit only when human explicitly requests |
| 9 | Final response | Include verdict, evidence summary, BUNDLE_VALIDATION status, NO_STASH_RESET_RESTORE_CLEAN_USED: YES; end with `EVIDENCE_BUNDLE: <path>` |
| 10 | Memory sync | If durable direction changed: create or update memory file; update memory/00-index.md |

---

## 2. Standard Evidence Requirements

Every production evidence bundle must:

- Be built by `tools/evidence/build_evidence_bundle.py` (manual zip is forbidden)
- Be validated by `tools/evidence/validate_evidence_bundle.py --check-no-pending`
- Achieve `BUNDLE_VALIDATION: PASS`
- Have exactly two top-level folders: `repo/` and `bundle-metadata/`
- Have `min_metadata_count >= 30` (base contract floor)
- Contain `final-bundle-validation-proof.txt` that is NOT a placeholder
- Contain `git-status-final.txt` (or `git-status.txt`)
- Contain `no-scope-drift-report.md`
- Contain lane metadata files (one per lane for multi-lane sprints)
- Contain `git-safety-policy-check.md`
- NOT contain `.local/`, `.env`, raw spec text, embeddings, LLM transcripts, secrets

---

## 3. Standard Final Response Requirements

Every sprint final response must include:

```
SPRINT: <sprint-id>
VERDICT: [PASS | FAIL | INCOMPLETE | BLOCKED]
BUNDLE_VALIDATION: [PASS | FAIL]
NO_STASH_RESET_RESTORE_CLEAN_USED: YES
CURRENT_STATE_CONSISTENCY: [PASS | FAIL]
<summary of work done — referenced artifacts, not prose claims>
EVIDENCE_BUNDLE: <absolute Windows path to .zip>
```

The final line must be `EVIDENCE_BUNDLE: <path>`. No other line may follow it.

---

## 4. Standard Prompt Requirements

Every execution prompt provided to an agent must include:

1. Mode label (PLAN MODE / EXECUTION MODE / IV MODE / REPAIR MODE)
2. Sprint ID
3. Repository path
4. Current accepted state (what has been verified before this sprint)
5. Scope — what to do
6. Non-goals — what NOT to do
7. Lane definitions (if multi-lane) with explicit ownership
8. Safety rules — always include no-stash/reset/restore/clean/broad-staging
9. Allowed files (exact paths)
10. Prohibited files and directories
11. Validation commands (exact, runnable)
12. Evidence contract requirements (contract file path or inline spec)
13. Final response format requirements
14. Exact next step expected after this prompt

---

## 5. Standard Independent Verification (IV) Requirements

Every item submitted for human review must first be verified in a separate session (DEC-034).

An IV sprint must:

- Use a different session/run from the producing sprint
- Re-read all source files referenced in the producing sprint's claims
- Re-compute or re-check all quantitative claims independently
- Produce an IV audit document in the evidence bundle
- Log any contradictions found as gaps — fix before human review
- Not be the same session that produced the work

IV waiver: if the human explicitly waives DEC-034 in the execution prompt for the current session,
the agent must note the waiver in the run record.

---

## 6. Standard Repair Sprint Requirements

A repair sprint fixes a specific identified failure.

It must:
- Define the exact failure being fixed (one failure per repair sprint when possible)
- Cite the evidence artifact that identified the failure
- List allowed files (only files needed for the fix)
- Define a validation command that will confirm the fix
- NOT expand scope to "clean up surrounding code" or "improve while here"
- Produce an evidence bundle documenting the before/after state

---

## 7. Standard Memory Sync Requirements

When any of these events occur, sync local memory before the sprint ends:

| Trigger | Memory action |
|---------|--------------|
| Product direction changes | Update or create `memory/NN-commercial-product-direction-*.md` |
| AI policy changes | Update `memory/23-ai-usage-operating-model-*.md` or create new |
| Gate interpretation changes | Update gate-related memory and 00-index.md |
| Workflow methodology changes | Create new memory file and update 00-index.md |
| Major sprint accepted | Update session continuity memory (most recent NN-*.md) |
| New chat bootstrap needed | Update `docs/automation/fresh-chat-project-bootstrap.md` |

Memory files must not duplicate AGENTS.md or GOVERNANCE.md. Reference those; don't repeat them.

---

## 8. Standard AI Usage Requirements

When using AI in a sprint:

1. Log all AI usage for repo-changing work in `.local/llm-logs/` (JSONL)
2. Schema-validate all structured AI outputs before accepting them
3. Run tests on AI-generated code before including in evidence
4. Run verifier review on AI-generated requirements
5. Cite local source in AI-generated claims where applicable
6. Accept or reject AI outputs explicitly — not implicitly
7. Do not send secrets, credentials, or raw spec text to AI endpoints
8. Do not commit raw LLM transcripts
9. Do not use AI to approve gates

---

## 9. Standard Safety Prohibitions

These are absolute. No exception without explicit human authorization in the current session.

```
NO:  git stash
NO:  git reset
NO:  git reset --hard
NO:  git restore
NO:  git checkout -- . / git checkout -- <path>
NO:  git clean
NO:  git add .
NO:  git add -A
NO:  git push (without explicit authorization this session)
NO:  gate self-approval
NO:  package publish without authorization
NO:  secrets committed or logged
NO:  raw LLM transcripts committed
NO:  embeddings committed
NO:  DEC-033 violation (.NET FOSS)
NO:  .NET FOSS source (DEC-033 Option B)
```

---

## 10. Standard Local Files to Read First

Before any sprint, read in this order:

| # | File | Purpose |
|---|------|---------|
| 1 | `docs/automation/fresh-chat-project-bootstrap.md` | Current session entry point |
| 2 | `plans/master-plan.md` Section 33 | Current state and next action |
| 3 | `AGENTS.md` | All agent rules |
| 4 | `GOVERNANCE.md` | Human governance rules |
| 5 | `memory/00-index.md` | Index of all memory files |
| 6 | Most recent `memory/NN-*.md` | Most recent session continuity |
| 7 | `registry/format-registry.yaml` | Gate status and capability levels |
| 8 | `docs/product-factory/commercial-product-capability-model.md` | C-level definitions |
| 9 | `docs/governance/current-state-and-evidence-authority.md` | Run-state authority model |
| 10 | `docs/automation/assistant-supervision-methodology.md` | This project's supervision standards |
| 11 | `docs/governance/project-execution-standards.md` | This document |

For implementation sprints, also read:
- `generated-requirements/{format}/` — accepted requirement IDs
- `src/net/{format}/` — current .NET source
- `tests/net/{format}/` — current test status

For IV sprints, also read:
- The evidence bundle from the sprint being verified
- The evidence contract for that sprint
- The source files referenced in the sprint claims
