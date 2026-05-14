---
document_type: methodology
title: Assistant Supervision Methodology
version: "1.0"
created_at: "2026-05-13"
sprint: CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM
visibility: internal
publish_allowed: false
authority: methodology
---

# Format Factory — Assistant Supervision Methodology

**This is not a generic assistant personality document.**

This document captures the supervision and execution style expected by the human (Babar Raza)
for the Format Factory project. Future agents, local Claude Code sessions, and ChatGPT sessions
should read this before reviewing evidence, planning sprints, generating prompts, or deciding
next steps.

---

## 1. Purpose

This document defines how project supervision and execution should be conducted by any AI
assistant working on Format Factory.

It must be clear:

- This is not a description of assistant personality.
- This is a project operating methodology.
- Future agents and chats must use it when reviewing evidence, planning sprints, generating
  prompts, and deciding what to do next.
- Future agents that ignore this methodology will produce weaker work and require more
  human correction.

If there is ever a conflict between this document and `plans/master-plan.md`, `AGENTS.md`,
or `GOVERNANCE.md`, those authority documents take precedence. This document defines
*how* to reason about the project — those documents define *what* the rules are.

---

## 2. Core Principles

These principles apply at all times, in every session.

| Principle | What it means in practice |
|-----------|--------------------------|
| Evidence before acceptance | Never accept a claim without inspecting the artifact that supports it |
| Source before summary | Read the actual file, not the agent's description of it |
| Tests before claims | PASS claims must be verified against actual test output |
| Gates before release | Gate N must be approved before Gate N+1 work begins |
| Taskcards before drift | No untracked work; every task has a taskcard |
| Local memory before assumptions | Read the repo before guessing at project state |
| Repeatability before one-off fixes | Build systems that can be rerun, not patches that can't |
| Controlled swarm before uncontrolled parallelism | Multi-lane yes; uncoordinated chaos no |
| AI acceleration before manual bottlenecks | Use AI where it helps; govern its outputs |
| Validation before authority | AI output is a proposal; validation makes it fact |
| Clear next prompt before vague advice | Always provide a ready-to-send prompt, not "you should check X" |

---

## 3. Evidence-First Behavior

When a sprint claims to be complete, the default response is to inspect evidence, not to
accept the claim.

Future agents reviewing a sprint must:

1. Inspect the uploaded or referenced evidence bundle directly.
2. Validate the evidence contract (`tools/evidence/contracts/{sprint}.yaml`).
3. Review `bundle-metadata/` for required metadata files.
4. Inspect `final-bundle-validation-proof.txt` — confirm it is NOT a placeholder.
5. Inspect `git-status-final.txt` or `git-status.txt` for unintended dirty state.
6. Inspect `no-scope-drift-report.md` if present.
7. Read the actual source files referenced in the sprint claims.
8. Compare what was claimed against what the artifacts show.
9. Identify contradictions between claims and artifacts.
10. State uncertainty explicitly — do not paper over gaps.

**Never accept sprint claims from the final response text alone.**

When evidence is missing, the agent must:
- State clearly what is missing.
- Provide a verification prompt the human can paste to get that evidence.
- Not guess at the missing information.

### Specific evidence signals to look for

| Signal | What to check |
|--------|--------------|
| "PASS" claim | Test output file; test count; fail count |
| "complete" claim | Taskcards with status=completed; evidence files created |
| "Gate passed" claim | registry/format-registry.yaml gate entry; human approver name and date |
| "no scope drift" claim | no-scope-drift-report.md; git status against allowed paths |
| "commercial ready" claim | docs/commercial-product-capability-model.md level; Gate 11 sub-gates |
| "AI verified" claim | Verifier review YAML; schema validation output |
| "tests passed" claim | Actual test runner output; specific counts |
| "bundle validated" claim | BUNDLE_VALIDATION: PASS line in metadata |

---

## 4. Challenge-Agent-Claims Behavior

Future agents must actively challenge all "done" claims.

Claims to challenge:

- "PASS" claims in evidence — verify against source
- "complete" claims — verify against taskcard status
- "ready" claims — verify against gate criteria
- "commercial-ready" claims — verify against capability model (C7+ required)
- "Gate passed" claims — verify against registry and human approver
- "tests passed" claims — verify against test output count and names
- "no scope drift" claims — verify against allowed paths and git status
- "AI verified" claims — verify against verifier-review.yaml and schema output
- "requirement accepted" claims — verify against generated-requirements/

How to challenge:

- Read `registry/format-registry.yaml` for gate truth.
- Read `plans/master-plan.md` Section 33 for current state.
- Read relevant source files in `src/net/` or `src/python/`.
- Read actual test output files.
- Read evidence contracts and metadata.
- Read taskcards for the sprint.
- Compare what was claimed against what repo files show.

**Challenge is not hostility. Challenge is how errors get caught before they become
technical debt or governance violations.**

---

## 5. Design Capability Expectations

Future agents must think systemically, not reactively.

Prefer systems over patches:

| Instead of | Prefer |
|------------|--------|
| Repeated manual prompts | Reusable command or skill |
| Static assumptions about format structure | Generated requirements from local specs |
| Prose-only process | Tool + schema + validation |
| Copy-paste procedures | Skill/command workflow |
| Informal reports | Evidence contracts |
| Chat-only context | Local memory files |
| Vague TODOs | Structured taskcards with acceptance criteria |
| One-off outputs | Versioned, repeatable artifacts |
| Manual patches | Governed, reproducible pipelines |

### System design patterns already established

The project already has established patterns. Future agents should use them:

- Evidence bundle contracts (`tools/evidence/contracts/`) — do not invent new ad hoc formats
- Neutral model schemas (`schemas/neutral-model/`) — do not bypass for quick prototypes
- Generated requirements pipeline (`generated-requirements/`) — do not implement without accepted IDs
- Taskcard system (`taskcards/`) — do not track work informally
- Local memory files (`memory/`) — do not assume state from chat only
- Gate system (Gates 1-11 in `docs/gates.md`) — do not invent separate acceptance criteria

---

## 6. Prompt Generation Standards

When providing prompts, future agents must provide complete, ready-to-send prompts.

A ready-to-send prompt must include:

### Required label
```
MODE: [PLAN MODE | EXECUTION MODE | INDEPENDENT VERIFICATION MODE | REPAIR MODE]
SPRINT: [sprint-id]
```

### Required content
- Repository path
- Sprint identity and description
- Current accepted state (what has been verified and accepted)
- Scope (what this sprint covers)
- Non-goals (what this sprint must NOT do)
- Lane definitions (if multi-lane) with owner assignments
- Safety rules (no stash/reset/restore/clean; no broad staging; no push)
- Allowed files (exact paths only)
- Prohibited files and directories
- Validation commands (exact commands to run)
- Evidence contract requirements
- Final response format requirements
- Exact next step after this sprint

### What NOT to do
- Do not provide vague "ask the agent to check X" guidance when a full prompt is needed.
- Do not leave the human to infer allowed paths or validation commands.
- Do not mix plan-mode and execution-mode instructions.
- Do not omit safety rules because they seem obvious.

### Prompt modes defined

| Mode | When to use |
|------|------------|
| PLAN MODE | Before execution — produces plan only, no file changes |
| EXECUTION MODE | Authorized to create and modify files |
| INDEPENDENT VERIFICATION MODE | DEC-034 verification in a separate session |
| REPAIR MODE | Fixing a specific identified failure; restricted scope |

---

## 7. Controlled Swarm Execution Style

When safe to do so, future agents should default to larger controlled swarms rather than
serial micro-sprints.

### Why controlled swarms

- More work per sprint
- Fewer sessions needed for the human
- Better coordination across related lanes
- Single evidence bundle per sprint boundary

### Swarm anatomy

Every controlled swarm must have:

| Component | Purpose |
|-----------|---------|
| Sprint ID | Unique identifier, referenced everywhere |
| Coordinator lane | Integrates all lane outputs; produces final bundle |
| Per-lane ownership | Each lane is assigned one owner and one scope |
| Shared-file control | One lane owns each shared file; others read-only |
| Dirty-state preflight | Check git status before any edits |
| Overlap check | No two lanes may edit the same file |
| Lane-local evidence | Each lane produces metadata report |
| Final integration | Coordinator integrates all lane outputs |
| Cross-lane validation | Coordinator validates consistency after integration |
| Single evidence bundle | One ZIP per sprint boundary |

### What NOT to do

- Do not split related work into micro-sprints just to keep things short.
- Do not run lanes in parallel without declaring overlap check and shared-file control.
- Do not create a swarm that has no coordinator lane.
- Do not create a swarm that skips dirty-state preflight.

### Safety always active

A larger swarm does not get weaker safety. All AE rules (AGENTS.md Section AE) apply
regardless of swarm size.

---

## 8. Safety Discipline

These prohibitions apply in every sprint without exception.

### Git prohibitions
- No `git stash`
- No `git reset` / `git reset --hard`
- No `git restore`
- No `git checkout -- .` or `git checkout -- <path>`
- No `git clean`
- No `git add .` / `git add -A`
- No `git push` without explicit human authorization in the current session

### Sprint prohibitions
- No gate self-approval
- No broad destructive file operations
- No package publish unless explicitly authorized
- No secrets printed, logged, or persisted
- No raw LLM transcripts committed
- No embeddings or vector DB files committed
- No DEC-033 violation (no .NET FOSS source)

### External service probes
When a sprint touches GitHub, tokens, LLM endpoints, or package managers:
- Use non-mutating probes first
- Log secret-safety status in the sprint evidence
- Do not proceed with mutations until probe confirms safe state

---

## 9. Gate and Readiness Discipline

Future agents must use precise language about readiness.

| Term | What it means |
|------|--------------|
| Prototype | Internal-only; not promoted to src/; design reference only |
| Tier 0 | Basic streaming parse; capability C2 (metadata/count extraction) |
| Vertical slice | Demonstrates architecture with limited entity coverage |
| Partial implementation | Some entities covered; not all required for commercial product |
| Release readiness | All Gate 11 sub-gates passed, C7+ capability, evidence bundle, human approval |
| Commercial readiness | Specific synonym for release readiness at commercial quality level |
| Human approval | Must name approver and date; cannot be delegated to AI |

### Format Factory specific rules

- C2 (Tier 0 parser) is NOT commercial readiness.
- C4-C6 vertical slice is progress, not a full commercial product.
- Gate 11 must not be approved without C7+ evidence AND explicit human approval.
- `commercial_product_ready` must remain `false` until criteria are actually met.
- An agent that claims a format is commercially ready without evidence is violating governance.

### Current state (as of 2026-05-13)
Both FODS and FODT are at C4-C6-vertical-slice capability. Gate 11 is in progress, not approved.
Commercial product readiness requires C7+ per `docs/commercial-product-capability-model.md`.

---

## 10. AI Usage Methodology

Use AI confidently. Govern its outputs rigorously.

### Where AI helps

- Retrieval (spec navigation, fact extraction from local artifacts)
- Requirements generation (from specs, format understanding, product goals)
- Code drafting (implementation, tests, validation scripts)
- Test generation (must fail on broken implementation)
- Gap analysis (adversarial challenge of claims)
- Adversarial review (find contradictions in evidence)
- Evidence summarization (coordinator verifies all claims)
- Skill and command generation
- Orchestration planning

### What AI must not do

- Approve gates
- Invent spec facts not supported by local cached spec
- Claim commercial readiness without evidence
- Bypass tests or validation
- Hide uncertainty
- Produce AI output that gets committed without validation

### AI output lifecycle

```
AI produces output
  → Validate: schema-validate structured output
  → Test: run tests if code
  → Verify: verifier-review if requirements
  → Accept/Reject explicitly
  → Log in .local/llm-logs/ if repo-changing
  → Cite source where applicable
  → Include in evidence bundle
```

### Authority hierarchy (do not invert)

```
1. Local cached specs (highest)
2. Verified test results
3. Committed source (tested)
4. Evidence bundles
5. Human decisions
6. Gate records
7. AI-generated artifacts (lowest — proposal until validated)
```

---

## 11. Requirement Generation Methodology

For commercial file-format work, requirements must flow through a governed pipeline.

### Requirements pipeline

```
Format name
  → Format context resolver
     (local spec, format understanding, acquisition pack, product goals)
  → Local retrieval
     (spec chunks, neutral model, acquisition pack, existing tests)
  → AI-generated requirements
     (YAML with requirement IDs; from local sources)
  → Schema validation
     (schemas/requirements/*.schema.json — hard fail if invalid)
  → Verifier review
     (adversarial challenge; verifier-review.yaml)
  → Human review and acceptance
     (DEC-034 independent verification; then human decision)
  → Requirement IDs marked ACCEPTED_FOR_VERTICAL_SLICE
  → Implementation swarm prompt
     (references accepted requirement IDs)
  → Implementation
  → IV (DEC-034)
  → Capability level update
```

### Rules

- Human requirements define product goals — agents interpret, not invent.
- Generated requirements must come from local specs, tests, and product goals — not from AI imagination.
- Schema validation is a hard gate — invalid YAML does not enter the pipeline.
- Verifier agents must challenge generated requirements adversarially.
- Only accepted requirement IDs (marked `ACCEPTED_FOR_VERTICAL_SLICE`) may drive implementation.
- Implementation must report: requirement IDs consumed, implemented, deferred, rejected.
- Do not collapse generation + validation + acceptance into one step.

---

## 12. Review and Next-Step Methodology

When reviewing a completed sprint, the response must drive the project forward.

### Required review output

1. **Normalized verdict** — ACCEPTED / ACCEPTED_WITH_CONDITIONS / REJECTED / INCOMPLETE
2. **Accepted facts** — list of verified claims with evidence citations
3. **Rejected or unverified claims** — list of claims that could not be verified
4. **Gaps** — missing evidence, missing tests, stale files
5. **Risks** — what could go wrong if the project proceeds
6. **What NOT to do next** — anti-patterns to avoid
7. **What to do next** — specific, ranked recommended actions
8. **Ready-to-send prompt** — complete, pasteable prompt for the recommended next step

The review must NOT stop at "this looks good." The review must drive the next action.

### Review format rule

Every sprint review must produce a clear verdict section before anything else.
Do not make the human infer the verdict from context.

---

## 13. Memory and Local Continuity Methodology

Future agents must sync durable decisions to local memory when any of these events occur:

- Product direction changes
- AI policy changes
- Gate interpretation changes
- Workflow methodology changes
- Requirements model changes
- Safety governance changes
- Major sprint result accepted
- A fundamental decision is made that will affect future prompts

### Rules for memory sync

- Do not cause broad documentation churn. Update what needs updating, not everything.
- Update or create the specific memory file for the topic.
- Update `memory/00-index.md` with the new entry.
- Note the sprint and date in the memory file.
- Do not duplicate information already in AGENTS.md or GOVERNANCE.md — reference those.
- Memory files are context; authority files are rules.

### Memory file naming

```
memory/NN-topic-slug-YYYYMMDD.md
```

Where NN is the next sequential number (requires GOV-006 authorization for numbers 16+, but
human-authorized sprint prompts may explicitly grant creation of specific files).

---

## 14. Communication Style Expected by the Human

These rules define how the assistant should communicate in this project.

| Rule | Detail |
|------|--------|
| Be direct | State the verdict first, then the reasoning |
| Be honest | If evidence is thin, say so; do not rationalize |
| Challenge weak work | "PASS" claims without evidence deserve challenge |
| Do not flatter agent outputs | "Great sprint" is useless; evidence is useful |
| Do not overstate | If C4, say C4; if Gate 11 is not ready, say not ready |
| Explain implications | Tell the human what the finding means for next steps |
| Give clear verdicts | ACCEPTED / REJECTED / INCOMPLETE — not "seems good" |
| Provide ready-to-send prompts | Paste-ready, not "you should ask the agent to..." |
| Do not ask unnecessary questions | If evidence is available, inspect it; do not ask about it |
| If unsure, inspect or provide IV prompt | Never guess at project state |

---

## 15. Anti-Patterns to Avoid

These are the failure modes most likely to cause project drift or wasted sprints.

| Anti-pattern | Why it is harmful |
|-------------|------------------|
| Accepting sprint final response without bundle inspection | Claims are hypotheses; bundles are evidence |
| Calling thin parsers commercial-ready | Misleads the human; sets false expectations |
| Approving Gate N before criteria are met | Breaks the integrity of the gate system |
| Generating static manual requirements instead of system-generated | Does not scale; can't be verified; drifts |
| Using AI output as truth | AI makes mistakes; validation catches them |
| Producing vague prompts | Agent can't execute on "check if things look OK" |
| Micro-sprinting every small note | Creates too many sessions; loses throughput |
| Skipping evidence contracts | Makes sprint results unverifiable |
| Broad staging in git | Risks committing files outside sprint scope |
| Hiding unresolved gaps | Gaps compound; they don't go away |
| Leaving future agents without local memory | Next session loses context; errors repeat |
| Claiming "independent verification" without a separate session | Violates DEC-034; makes IV meaningless |
| Updating gate status without evidence bundle | Changes cannot be audited or reversed |
| Mixing stream ownership in one commit | Creates bundle attribution problems |
