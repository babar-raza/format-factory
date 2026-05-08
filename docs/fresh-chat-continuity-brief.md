# Fresh Chat Continuity Brief

**Document type:** Fresh Chat Orientation Guide
**Created:** 2026-05-08 (memory-planning-methodology-and-agent-handoff sprint)
**Visibility:** internal
**Purpose:** Allow the human to open a fresh chat window and continue format-factory work without needing the full original conversation history.

---

## 1. What Format Factory Is

Format Factory is an 11-gate acquisition pipeline for legal file format parsers and converters.
It produces two product tracks:
- Python FOSS: src/python/{format}/ (Tier 0-4 features, open-source release)
- .NET product: src/net/{format}/ (Tier 0-6 features, commercial full-feature)

The pipeline currently covers FODS (flat XML spreadsheet) and FODT (flat XML text document).
Both are ODF 1.3 formats from OASIS. Format source is Category 1 (royalty-free, open spec).

The pipeline has three streams:
- MAIN SPRINT: advances gates, produces artifacts, requires human approval at each gate.
- SECONDARY SPRINT: executes authorized secondary plans (e.g., S-F2F full-to-FOSS split).
- MEMORY SPRINT: captures decisions, strategy, architecture into durable local artifacts.

---

## 2. Current Strategic Direction (as of 2026-05-08)

### XML-First Focus
Current work focuses on XML-type formats (text_xml). The pipeline is validated for XML.
Non-XML formats (zip_container, binary_records, etc.) are planned but not yet started.

### Format Understanding Layer (backlog)
Before Phase 4 product source begins, each format should produce a compiled set of
understanding artifacts (format-profile.yaml, verified-facts.yaml, implementation-requirements.yaml,
parser-strategy.yaml, security-surface.yaml, product-readiness.yaml).
See: docs/format-understanding-layer.md. Taskcards: FUL-001 through FUL-004.

### Non-XML Adaptability (backlog)
The pipeline architecture must avoid hardcoding XML-only assumptions.
Non-XML adaptability is backlog only until explicitly authorized.
See: docs/format-representation-model.md. Taskcards: REP-001, REP-003.

### Controlled LLM and Embedding Strategy (backlog)
Future governed use of LLMs via llm.professionalize.com.
GPT OSS, Qwen Next, and embedding models are authorized for future use.
LLMs are not gate authority. Embeddings are retrieval tools, not truth authority.
See: docs/llm-and-embedding-strategy.md. Taskcards: LLM-001, EMB-001.

### Non-Aspose Candidate Registry (backlog)
A registry of formats underserved by Aspose products is planned but not created.
See: docs/non-aspose-format-candidate-registry-plan.md. Taskcard: NAC-001.

### Planning Methodology (new 2026-05-08)
Local planning docs, prompt templates, and execution handoff standards have been created.
See: docs/planning-methodology.md, docs/agent-execution-handoff-standard.md.

---

## 3. Planning Style

The planning style used in this project:

1. Challenge first. Every plan must be hardened before execution. Read the referenced files.
2. Verify repo truth. Do not trust agent summaries. Read the actual files and evidence bundles.
3. Evidence is necessary. Gates require evidence bundles. Bundles require contracts.
4. Missing architecture must be captured. Discovered gaps go into backlog, roadmap, taskcards, and memory.
5. Single-go execution. Complex plans are encoded as single prompts with internal gates.
6. No broad cleanup. Git stash, reset, and clean commands are not used as defaults.
7. No push unless authorized. Every session defaults to no push.

---

## 4. Prompt Style

Prompts in this project are:

1. LLM-consumable. Each step is an atomic, executable instruction.
2. Direct. "Run X and confirm Y" not "verify that the output looks reasonable."
3. Detailed. Each section lists exact files, exact commands, exact expected output.
4. Execution-ready. The agent can paste the prompt and execute without manual interpolation.
5. Internally gated. If check A fails, stop with BLOCKED label. Do not skip ahead.
6. Clearly prohibited. Hard prohibitions are explicit and non-negotiable.
7. No em dash. Use commas, colons, semicolons, or periods instead.

---

## 5. How to Ask for Next Prompts

Example messages that get the right response:

- "Check this evidence bundle and provide the next execution prompt."
  (Agent inspects the bundle, then produces the next prompt based on what is actually in it.)

- "Review this draft plan and make it execution-ready."
  (Agent reads all referenced files, applies the hardening checklist, and produces a hardened version.)

- "Create a single-go autonomous handoff for the next FODS gate."
  (Agent reads master-plan, confirms current gate status, and creates a complete execution prompt.)

- "Create a memory sprint to store this decision locally."
  (Agent reads memory files, creates a new memory file, updates the index, and builds an evidence bundle.)

- "Challenge the agent summary against repo evidence."
  (Agent reads the referenced files and bundle, identifies any discrepancies, and reports them.)

---

## 6. Files a New Chat Should Read First

Ask the agent to read these files before producing any prompt:

1. plans/master-plan.md (authoritative operational state)
2. ROADMAP.md (phase model and milestones)
3. AGENTS.md (non-negotiable agent rules)
4. GOVERNANCE.md (human governance rules)
5. docs/planning-methodology.md (planning style and sprint type rules)
6. docs/agent-execution-handoff-standard.md (execution rules)
7. docs/format-understanding-layer.md (required backlog layer before Phase 4)
8. memory/00-index.md (memory index -- read priority files listed there)
9. memory/09-current-state-before-phase1.md (current gate status record)
10. memory/11-prompting-and-agent-style-rules.md (user preferences)
11. registry/format-registry.yaml (exact current gate statuses)
12. Latest evidence bundle (most recent passing bundle in .local/evidence-bundles/)

Also run:
- git log --oneline -10
- git status --short
- python tools/evidence/check_current_state_consistency.py

---

## 7. How to Continue Safely

1. Read the required files listed above before asking the agent to do anything.
2. Ask the agent for a bootstrap orientation first (use docs/prompts/fresh-chat-bootstrap-prompt.md).
3. Confirm the agent's orientation summary is correct against the files you have read.
4. Ask for the next prompt only after confirming orientation.
5. Do not advance a gate without a passing evidence bundle and human approval.
6. Do not authorize product source (src/python/ or src/net/) until FUL-001 is approved and Gates 1-9 are passed.
7. If the agent produces a summary without reading files, ask it to read the files first.

---

## 8. Current Gate Status Summary (as of 2026-05-08, run048)

| Format | Gates Passed | Current State | Next |
|---|---|---|---|
| FODS | 1-10 | Gate 10 PASSED (run048) | Gate 11: TC-0047, DEC-033 resolution |
| FODT | 1-8 | Gate 8 PASSED (run048) | Gate 9: TC-0048 explicit prompt |

FODS Gate 10 = OSS implementation readiness. Gate 11 = commercial implementation readiness.
FODT Gate 9 = product mapping (tier map, delivery plan).

FUL-001 through FUL-004: proposed_pending_human_approval (not started).
LLM-001, EMB-001, REP-001, REP-003, NAC-001, GOV-001, GOV-002: proposed_pending_human_approval.
