# Agent Methodology Index

**Document type:** Local Planning and Execution Entry Point
**Created:** 2026-05-08 (memory-methodology-linkage-and-enforcement sprint)
**Visibility:** internal
**Authority:** This is the starting point for agents and fresh chat sessions that need to
create, review, harden, or execute plans in the format-factory repo.

---

## 1. Purpose

This file is the local entry point for all plan and prompt work. Before creating a plan,
reviewing a plan, writing an execution handoff, or starting a fresh session, read this index.

It links all methodology docs, prompt templates, commands, and enforcement rules.

---

## 2. Required Read Order

Before taking any planning or execution action, read these files in order:

1. [AGENTS.md](../AGENTS.md) -- agent operating contract
2. [GOVERNANCE.md](../GOVERNANCE.md) -- human governance and policy
3. [plans/master-plan.md](../plans/master-plan.md) -- single operational authority
4. [ROADMAP.md](../ROADMAP.md) -- strategic direction and backlog
5. [memory/00-index.md](../memory/00-index.md) -- memory package index
6. [docs/agent-methodology-index.md](agent-methodology-index.md) -- this file
7. [docs/planning-methodology.md](planning-methodology.md) -- planning and execution standard
8. [docs/agent-execution-handoff-standard.md](agent-execution-handoff-standard.md) -- handoff standard
9. [docs/plan-hardening-checklist.md](plan-hardening-checklist.md) -- 22-item hardening checklist
10. [docs/fresh-chat-continuity-brief.md](fresh-chat-continuity-brief.md) -- fresh session orientation

---

## 3. Methodology Docs

| File | Description |
|------|-------------|
| [docs/planning-methodology.md](planning-methodology.md) | Core principles, plan quality test, plan hardening process, sprint types, prompt anatomy, single-go handoff standard, style rules. |
| [docs/agent-execution-handoff-standard.md](agent-execution-handoff-standard.md) | What a handoff is, when to use it, plan vs. execution prompt comparison, drift prevention, stream separation, state decisions. |
| [docs/plan-hardening-checklist.md](plan-hardening-checklist.md) | 22-item checklist in 6 sections. Plans must score at least 18/22 before execution. |
| [docs/fresh-chat-continuity-brief.md](fresh-chat-continuity-brief.md) | How to orient a fresh chat session without conversation history. First files to read, gate status summary, current strategic direction. |
| [docs/prompts/README.md](prompts/README.md) | Index of all prompt templates. Rules for adapting and using them. |
| [memory/12-planning-and-agent-handoff-methodology.md](../memory/12-planning-and-agent-handoff-methodology.md) | User preferences, planning style summary, prompt evolution pattern, key doc paths. |

---

## 4. Prompt Templates

All templates are in [docs/prompts/](prompts/).

| Template | Purpose | When to Use |
|----------|---------|-------------|
| [plan-hardening-prompt-template.md](prompts/plan-hardening-prompt-template.md) | Review and harden a plan against repo truth. | Before converting a prose plan to execution. |
| [execution-handoff-prompt-template.md](prompts/execution-handoff-prompt-template.md) | Convert a hardened plan into a full single-go execution prompt. | After plan hardening passes (18/22+). |
| [independent-verification-prompt-template.md](prompts/independent-verification-prompt-template.md) | DEC-034 verification of a prior sprint's claims. | Before human gate review. Always a separate session. |
| [evidence-bundle-review-prompt-template.md](prompts/evidence-bundle-review-prompt-template.md) | Inspect a bundle, challenge claims, and produce the next prompt. | After each execution sprint. Before starting the next. |
| [memory-sprint-prompt-template.md](prompts/memory-sprint-prompt-template.md) | Capture decisions, architecture, preferences into durable repo artifacts. | When strategy or architecture decisions need to be persisted. |
| [closure-hygiene-prompt-template.md](prompts/closure-hygiene-prompt-template.md) | Normalize emergency contracts to clean PASS mode after the fact. | When a bundle was produced with emergency_blocker_bundle: true but is actually clean. |
| [unblocking-patch-prompt-template.md](prompts/unblocking-patch-prompt-template.md) | Minimal targeted fix for a specific blocker. | When a single blocker prevents progress on a valid sprint. |
| [fresh-chat-bootstrap-prompt.md](prompts/fresh-chat-bootstrap-prompt.md) | Orientation prompt for a brand-new session with no prior context. | When opening a fresh chat window. |

---

## 5. Claude Commands

These commands are active and available in this project.
Use them rather than reinventing behavior ad hoc.

| Command | File | Purpose | Mode |
|---------|------|---------|------|
| `/plan-hardening` | [.claude/commands/plan-hardening.md](../.claude/commands/plan-hardening.md) | Apply 22-item hardening checklist to a plan. | PLAN MODE only. Does not create files or commit. |
| `/execution-handoff` | [.claude/commands/execution-handoff.md](../.claude/commands/execution-handoff.md) | Convert a hardened plan into a full single-go execution prompt. | PLAN MODE only. Does not create files or commit. |
| `/evidence-review-next-prompt` | [.claude/commands/evidence-review-next-prompt.md](../.claude/commands/evidence-review-next-prompt.md) | Review a bundle, challenge claims, produce next prompt. | PLAN MODE only. Does not create files or commit. |
| `/memory-sprint` | [.claude/commands/memory-sprint.md](../.claude/commands/memory-sprint.md) | Full memory sprint workflow from decision capture to bundle. | EXECUTION MODE. Creates files and commits. |

---

## 6. When to Use Each Template

| Situation | Template or Command |
|-----------|---------------------|
| Human gives a goal or plan draft | Start with `/plan-hardening` or plan-hardening-prompt-template.md |
| Plan passes hardening (18/22+) | Use `/execution-handoff` or execution-handoff-prompt-template.md |
| Prior sprint bundle needs review | Use `/evidence-review-next-prompt` or evidence-bundle-review-prompt-template.md |
| Need to verify prior sprint (DEC-034) | Use independent-verification-prompt-template.md in a separate session |
| Strategy decision needs capturing | Use `/memory-sprint` or memory-sprint-prompt-template.md |
| Emergency contract needs normalizing | Use closure-hygiene-prompt-template.md |
| Specific blocker prevents progress | Use unblocking-patch-prompt-template.md |
| Opening a fresh chat window | Use fresh-chat-bootstrap-prompt.md and read docs/fresh-chat-continuity-brief.md |

---

## 7. Enforcement Rules

These rules are non-negotiable for all plan and prompt work in this repo.

1. Challenge plans before execution. Every plan has a hardening step (see docs/plan-hardening-checklist.md). Do not skip it.
2. Inspect referenced files. Read every file referenced in a plan before acting. Do not trust summaries alone.
3. Inspect evidence bundles. Before starting the next sprint, review the prior bundle using /evidence-review-next-prompt.
4. No reliance on summaries alone. Agent summaries are hypotheses. Evidence bundle metadata and repo files are the source of truth.
5. No broad stash or broad cleanup. Do not use git stash -u, git reset --hard, or git clean -fd as catch-all defaults. Scope any cleanup exactly.
6. No stream mixing. MEMORY SPRINT work must not include gate changes. MAIN SPRINT commits must not include memory-only files. Classify every dirty file before staging.
7. Evidence-producing sprints must produce final evidence bundle path. Print: EVIDENCE_BUNDLE: <absolute Windows path to zip>
8. Discovered gaps must be captured. Any missing architecture or capability must go into backlog, roadmap, taskcard, or memory. Not just chat.

---

## 8. Fresh Chat Bootstrap

When starting a fresh session with no prior conversation history:

1. Read [docs/fresh-chat-continuity-brief.md](fresh-chat-continuity-brief.md) for project context and gate status.
2. Use [docs/prompts/fresh-chat-bootstrap-prompt.md](prompts/fresh-chat-bootstrap-prompt.md) as an orientation template.
3. Read [memory/00-index.md](../memory/00-index.md) for the memory package index.
4. Read [memory/12-planning-and-agent-handoff-methodology.md](../memory/12-planning-and-agent-handoff-methodology.md) for user preferences.
5. Read [plans/master-plan.md](../plans/master-plan.md) for current operational state.

---

## 9. Local Validation

Run the methodology link checker to verify all docs, templates, commands, and cross-links are present:

```
python tools/governance/check_methodology_links.py
```

Expected output: METHODOLOGY_LINK_CHECK: PASS

If the check fails, address all listed issues before proceeding with plan or sprint work.

---

## 10. Relationship to Other Docs

- [AGENTS.md](../AGENTS.md) Sections AD, AB, AC: enforcement rules for agents
- [GOVERNANCE.md](../GOVERNANCE.md) Sections 23, 24: governance policy for planning work
- [memory/12-planning-and-agent-handoff-methodology.md](../memory/12-planning-and-agent-handoff-methodology.md): user preferences and planning style
- [docs/planning-methodology.md](planning-methodology.md): detailed methodology reference
- [tools/governance/check_methodology_links.py](../tools/governance/check_methodology_links.py): automated link validator

---

## 11. ChatGPT Supervision Context (added 2026-05-09)

These memory files provide the external AI supervision context. Read them when working on
AI/LLM strategy, Phase 4 planning, or multi-stream sprint driving.

| File | Purpose |
|------|---------|
| [memory/13-chatgpt-initial-project-analysis-20260509.md](../memory/13-chatgpt-initial-project-analysis-20260509.md) | ChatGPT first project analysis: what the project is, the real user requirement, where it stands, strengths, gaps, and next-level interpretation. |
| [memory/14-ai-supervision-and-three-pilot-direction-20260509.md](../memory/14-ai-supervision-and-three-pilot-direction-20260509.md) | AI supervision workflow, three-pilot proof path, parallel sprint stream handling, what AI may and must not do, what is not yet authorized. |
| [memory/15-ai-modules-and-state-management-architecture-20260509.md](../memory/15-ai-modules-and-state-management-architecture-20260509.md) | Governed LLM module, embedding retrieval, agent role, source generation, Format Factory State Manager, community component, sequencing, and no-drift architecture direction. |

Note: The `/evidence-review-next-prompt` command and the `evidence-bundle-review-prompt-template.md`
are the correct tools for reviewing sprint bundles and generating next prompts.

When the review results in architectural direction changes or sprint supervision decisions, those
must be captured in a memory sprint before the next execution sprint begins. This ensures
discoverability for future agents.

Use `memory/15-ai-modules-and-state-management-architecture-20260509.md` as a methodology and
architecture reference for AI modules, embeddings, state management, no-drift work, workflow
orchestration, playbook replay, review queues, and Phase 4 source generation. It is context only.
Prompts must distinguish design direction from implemented state.
