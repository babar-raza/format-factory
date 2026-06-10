# TC-README-PLAN-003: README Target Outline
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

## Strategy: Full Replacement

The README requires a complete structural rewrite. The 14-section target structure below
replaces all existing content. Each section maps to confirmed repo evidence.

Status markers: [CONFIRMED] = claim backed by repo files | [PROPOSED] = architecture intent not yet shipped | [CONDITIONAL] = true only if condition met

---

## Section 1: Project Summary (~15 lines)
**Heading:** `# Format Factory`

**Purpose:** One-paragraph description of what Format Factory is and does.

**Key claims (all CONFIRMED):**
- Legal file format acquisition system
- Produces parsers, converters, importers, exporters, validators for structured file formats
- Never engages in unauthorized binary reverse engineering, DRM bypass, or IP violations
- commercial_product_ready: false (Gate 11 not approved)

**Evidence:** README.md lines 1–11 (keep as base); AGENTS.md identity section

---

## Section 2: Product-First Mission (~20 lines)
**Heading:** `## Product-First Mission`

**Purpose:** Explain the 2026-06-03 strategic correction: evidence is required but not the goal; POC readiness is the goal.

**Key claims:**
- Strategic correction applied 2026-06-03 [CONFIRMED: state/current-state.md]
- All machinery (supervisor, skills, acceleration) exists to serve POC delivery [CONFIRMED: docs/governance/product-first-operating-model.md]
- POC goal: 3 commercial .NET products + 3+ FOSS reduced products [CONFIRMED: poc-targets.yaml]
- "Evidence is required, but evidence is not the goal."

**Evidence:** `plans/master-plan.md §43`, `docs/governance/product-first-operating-model.md`, `state/current-state.md`

---

## Section 3: Current POC Targets (~40 lines)
**Heading:** `## Current POC Targets`

**Purpose:** Authoritative list of what is being built RIGHT NOW. The most important section for an incoming agent.

**Key claims:**
- Three commercial .NET products: FODS, FODT, Netpbm [CONFIRMED: poc-targets.yaml, src/net/]
  - FODS/FODT: Gates 1–10 PASSED; Gate 11 NOT_STARTED (requires Babar Raza written approval)
  - Netpbm: POC active
- Three FOSS Python products: ZST, Python Netpbm (PBM/PGM/PPM), SYLK [CONFIRMED: poc-targets.yaml, src/python/]
- On-hold: DIF, QOI [CONFIRMED: poc-targets.yaml]
- commercial_product_ready: false for ALL [CONFIRMED: approval-gates.md, state/current-state.md]
- Gate 11 NOT approved for any format [CONFIRMED: approval-gates.md]
- Note: SVG is NOT a target — "Aspose already supports SVG" [CONFIRMED: governance intent from prior investigation]
- Note: Netpbm (raster image format) is the imaging target, not SVG [CONFIRMED: src/net/netpbm/]

**Evidence:** `product-capability-matrix/poc-targets.yaml`, `src/net/netpbm/`, `src/python/zst/`, `reports/supervisor/approval-gates.md`

---

## Section 4: Repository Layout (~35 lines)
**Heading:** `## Repository Layout`

**Purpose:** Accurate directory map of what actually exists in the repo.

**All directories CONFIRMED from glob:**
```
src/              Production source code
  net/fods/       FODS .NET commercial product
  net/fodt/       FODT .NET commercial product
  net/netpbm/     Netpbm .NET commercial product
  net/csv/        CSV target writer library
  net/html/       HTML target writer library
  net/txt/        TXT target writer library
  net/markdown/   Markdown target writer library
  python/         Python FOSS format libraries (18+ format dirs)
tests/            Product tests (net/fods/ 116+, net/fodt/ 115+, net/netpbm/ 48+; python/ 20+ dirs)
examples/         Code examples
  net/            C# class file examples (fods, fodt, netpbm)
  dotnet/         dotnet-script .csx examples (fods, fodt, netpbm)
  python/         Python examples (10+ format dirs)
docs/             Architecture, governance, and process documentation
  governance/     13 governance documents (four-stream model, AI authority, external tools, etc.)
  prompt-templates/ 15 stream-specific prompt templates
  automation/     Supervisor/worker contract docs
plans/            Living master plan (authoritative source)
registry/         Format registry and scoring model (22 formats)
product-capability-matrix/ POC readiness dashboard
tools/
  supervisor/     39 Python automation scripts (autonomous cycle, grading, evidence, routing)
  requirements_authority/ Requirements authority layer tools
  specification-authority-layer/ Spec authority tools
.supervisor/      Skill registry, context pack, policies, project memory, schemas
.claude/          Claude Code configuration and skill command files (30 commands)
reports/          Supervisor outputs, sprint grades, status
  supervisor/     session-resume.md, approval-gates.md, next-sprint.md, contradictions.md
  readme-refresh-plan/ This sprint's planning outputs
.local/           Local-only sprint state (gitignored)
  evidences/      Evidence declarations per sprint
  supervisor/reviews/ Review package ZIPs per sprint
acquisition-packs/ Per-format evidence, legal notes, samples (older sprints)
samples/          Licensed sample corpus with provenance
registry/         Format registry (22 formats, gate status)
```

**Note:** `.local/` is gitignored — contains local sprint state only; not pushed to repo.

---

## Section 5: Four-Stream Operating Model (~50 lines)
**Heading:** `## Four-Stream Operating Model`

**Purpose:** Explain how work is structured across four parallel streams.

**Evidence:** `docs/governance/four-stream-operating-model.md`, `docs/governance/lane-definitions.md`

### Section 5.1: Mainstream Product (~15 lines)
**Heading:** `### Mainstream Product`

- Builds real product capability across commercial .NET and FOSS Python targets
- Owns POC readiness; runs as a mega-train iteration loop
- Must produce: 1+ new API per product + tests + capability matrix update per PASS
- Hard PASS quota: minimum deliverables; evidence-only passes do not count
- Continuation until POC_READY_CANDIDATE or a true external blocker

**Evidence:** `docs/governance/mainstream-product-output-floor.md`, `docs/governance/mainstream-poc-mega-train.md`

### Section 5.2: Acceleration / AI Cognitive Layer (~12 lines)
**Heading:** `### Acceleration / AI Cognitive Layer`

- Two sub-lanes: A (Governance Harness) and B (AI Product Acceleration)
- AI may: observe, reason, rank, plan, design, critique, route, summarize
- AI may NOT: approve gates, mark capability complete, override tests, push, publish
- All AI output labeled `ai_draft` until validated by tests
- Approved AI gateway: Anthropic Claude API only

**Evidence:** `docs/governance/acceleration-definition.md`, `docs/governance/ai-authority-boundary.md`

### Section 5.3: Skills / Governed Execution (~12 lines)
**Heading:** `### Skills / Governed Execution`

- Provides reusable skills, templates, source-change contracts, transcripts
- 25 skills registered; 24 active (skill-registry.yaml)
- Skills must make Mainstream faster/safer — skills-only validating skills do not count
- Skill invocation via `.claude/commands/` (30 command files)
- Skill consumption: Mainstream can use normalized skills without re-review

**Evidence:** `.supervisor/skill-registry.yaml`, `docs/governance/superpowers-skill-intake.md`

### Section 5.4: Autonomous Supervisor / Continuation (~12 lines)
**Heading:** `### Autonomous Supervisor / Continuation`

- Deterministic traffic controller; owns routing, continuation, and evidence validation
- 39 Python tools in `tools/supervisor/` (autonomous-cycle, grading, routing, evidence)
- Continuation decision: reads `reports/supervisor/approval-gates.md`
- Hard stops (never autonomous): git push/commit, Gate 8/11 approval, package publication, MCP activation
- Current mode: MODE 4 (MCP ACTIVE)
- Advisory AI overlay: non-authoritative observer; AI output advisory only

**Evidence:** `docs/governance/autonomous-supervisor-role.md`, `tools/supervisor/autonomous_cycle.py`, `reports/supervisor/approval-gates.md`

---

## Section 6: External Tools (~30 lines)
**Heading:** `## External Tools`

**Purpose:** Document Ruflo, Superpowers, GhidraMCP — their roles, governance, and current status.

**Evidence:** `docs/governance/external-tool-architecture.md`

### Section 6.1: Ruflo (~10 lines)
- Optional runtime orchestration (swarm/lane coordination, continuation helper)
- Primary fit: Supervisor + Mainstream
- NOT authority over gates, taskcard closure, evidence verdict, or git operations
- Current status: NOT installed; full loop requires Supervisor approval [PROPOSED]
- Modes: ABSENT → AUDIT_ONLY → PLUGIN_LITE → FULL_LOOP_PENDING_APPROVAL → FULL_LOOP_APPROVED

### Section 6.2: Superpowers Marketplace (~8 lines)
- External skill-pattern source; primary fit: Skills / Governed Execution
- No blind install; skills normalized into local Format Factory wrappers
- Risk classification required: LOW (Supervisor review), MEDIUM (Supervisor approval), HIGH (Supervisor + human)
- Current status: No Superpowers skills installed [PROPOSED for future]

### Section 6.3: GhidraMCP (~8 lines)
- Optional specialist tool for authorized binary/sample analysis
- DISABLED_BY_DEFAULT; requires human authorization + Supervisor approval
- Output labeled `ghidra_ai_draft`; no capability update from output alone
- Hard prohibition: no MCP installation without compliance gate
- Current status: DISABLED [CONFIRMED: docs/governance/ghidra-mcp-compliance-gate.md]

---

## Section 7: AI Usage and Authority Boundary (~25 lines)
**Heading:** `## AI Usage and Authority Boundary`

**Purpose:** Explain how AI is used in this project and what authority limits apply.

**Core rule (CONFIRMED):** "AI thinks and drafts. Evidence decides."

**AI MAY (all labeled ai_draft until tests pass):**
- Observe project state
- Reason about next steps, rank gaps, suggest plans
- Design implementation approaches
- Critique evidence and prior work
- Route work across streams
- Summarize results, generate prompts

**AI MAY NOT:**
- Mark capability complete without passing tests
- Approve any gate (1–11)
- Override test results or validators
- Push, commit, or publish
- Write API keys or secrets
- Become authority over taskcard closure or registry mutations

**Evidence:** `docs/governance/ai-authority-boundary.md`

---

## Section 8: Governance and Safety Rules (~30 lines)
**Heading:** `## Governance and Safety Rules`

**Purpose:** Non-negotiable operating rules for any agent or contributor.

**Key rules (all CONFIRMED):**
- Read `AGENTS.md` before any action
- Read `CLAUDE.md` for session-start instructions
- Gate approval is human-only: Babar Raza for Gate 11; human for all other gates
- No git push without explicit user authorization
- No self-approval of gates
- All src/ edits since R90 must have a product-code ledger entry
- Skill invocation requires exact allowed file scope
- AI output remains `ai_draft` until validated
- MCP status current: MODE 4 ACTIVE (`.vscode/mcp.json` verified)
- Supervisor pipeline is advisory; Format Factory authority is FINAL

**Evidence:** `AGENTS.md`, `CLAUDE.md`, `.supervisor/policies.yaml`, `docs/governance/lane-definitions.md`

---

## Section 9: Evidence, Taskcards, and Review Packages (~25 lines)
**Heading:** `## Evidence, Taskcards, and Review Packages`

**Purpose:** Explain the sprint evidence model and how to inspect it.

**Key facts (CONFIRMED):**
- Each sprint produces: `.local/evidences/<run_id>/evidence-declaration.yaml`
- Sprint closeout: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>`
- Exit code 0 = accepted; 3 = critical rework; 1 = invalid declaration; 9 = error
- Review packages built by: `python tools/supervisor/build_declaration_review_package.py --declaration <path>`
- Review package format: ZIP at `.local/supervisor/reviews/<run_id>/declaration-review-package.zip`
- All local evidence and review packages are gitignored; not pushed to repo
- Taskcards: now tracked in plans/master-plan.md sections and reports/ taskcard directories

**Evidence:** `docs/automation/supervisor-worker-contract.md`, `tools/supervisor/autonomous_cycle.py`, `tools/supervisor/build_declaration_review_package.py`

---

## Section 10: How to Inspect Current State (~20 lines)
**Heading:** `## How to Inspect Current State`

**Purpose:** Exact commands and files for an agent or developer to quickly orient themselves.

**Ordered list (all CONFIRMED):**
1. `reports/supervisor/session-resume.md` — start of session; last sprint outcome, supervisor mode, what to do next
2. `reports/supervisor/approval-gates.md` — AUTONOMOUS_CONTINUE: YES/NO; who unblocks
3. `state/current-state.md` — full stream state snapshot (human-readable)
4. `product-capability-matrix/poc-targets.yaml` — POC readiness dashboard (authoritative)
5. `plans/master-plan.md` — living master plan, all decisions (AUTHORITY)
6. `reports/supervisor/contradictions.md` — check before autonomous continuation
7. `reports/supervisor/next-sprint.md` — next sprint task list

---

## Section 11: How to Run Safe Local Checks (~15 lines)
**Heading:** `## How to Run Safe Local Checks`

**Read-only / safe commands:**
- `python tools/supervisor/supervisor_loop.py --help` — list available commands
- `python tools/supervisor/build_context_pack.py` — regenerate context pack snapshot
- `python -m pytest tests/python/` — run Python test suite (no side effects)
- `dotnet test` — run .NET test suite (no side effects)
- `git status --short` — check working tree state
- `git log --oneline -10` — recent commit history

**Do NOT run without authorization:**
- `git push` — requires explicit user approval
- `git commit` — requires explicit user approval
- Gate approval commands
- Package publication commands

---

## Section 12: How Agents Should Work in This Repo (~20 lines)
**Heading:** `## How Agents Should Work in This Repo`

**Mandatory onboarding (CONFIRMED):**
1. Read `AGENTS.md` (agent operating contract)
2. Read `CLAUDE.md` (session-start instructions)
3. Read `reports/supervisor/session-resume.md` (last sprint outcome)
4. Check `reports/supervisor/approval-gates.md` (continuation authorization)
5. If contradictions exist: fix before advancing (`reports/supervisor/contradictions.md`)
6. Read `plans/master-plan.md` (AUTHORITY document)

**All agents must:**
- Source every claim from repo files (not memory or prior prompts)
- Declare all work in `evidence-declaration.yaml`
- Run `supervisor_loop.py autonomous-cycle` at sprint end
- Use product-code ledger for all src/ edits since R90
- Mark AI output `ai_draft` until tests validate

---

## Section 13: Current Status and Next Steps (~20 lines)
**Heading:** `## Current Status`

**Confirmed facts (all CONFIRMED):**
- Latest sprint: R118 (2026-06-05) — FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001
- Last committed sprint: R93 (2026-06-02) — 20+ sprints uncommitted, awaiting user authorization
- commercial_product_ready: false
- Gate 11: NOT_STARTED (requires Babar Raza written approval)
- AUTONOMOUS_CONTINUE: YES (per approval-gates.md)
- Critical contradictions: 0
- MCP: MODE 4 ACTIVE

**Production blockers:**
- G11-G_NOT_STARTED: Gate 11 commercial approval (human required)
- GATE8_AWAITING_HUMAN_APPROVAL: Several formats pending security review
- PACKAGE_NOT_PUSHED: All POC artifacts local-only
- NO_PUSH_AUTHORIZATION: git push requires explicit user approval

---

## Section 14: What Not To Do (~15 lines)
**Heading:** `## What Not To Do`

**Hard prohibitions (all CONFIRMED from governance):**
- Do not push without explicit user authorization
- Do not self-approve any gate (1–11)
- Do not claim commercial_product_ready = true
- Do not edit src/ without a product-code ledger entry (R90+)
- Do not install Ruflo, Superpowers, or GhidraMCP without going through the compliance gate
- Do not treat AI output as authoritative (label ai_draft; run tests)
- Do not trust MEMORY.md or prior prompts without confirming against repo files
- Do not commit without user authorization
- Do not mark capability complete without passing tests and capability matrix update
- Do not skip evidence declaration at sprint close

---

## Total Estimated README Length

| Section | Estimated Lines |
|---------|----------------|
| 1. Project Summary | 15 |
| 2. Product-First Mission | 20 |
| 3. Current POC Targets | 40 |
| 4. Repository Layout | 40 |
| 5. Four-Stream Model + subsections | 55 |
| 6. External Tools + subsections | 30 |
| 7. AI Usage and Authority | 25 |
| 8. Governance and Safety | 30 |
| 9. Evidence, Taskcards, Review Packages | 25 |
| 10. How to Inspect Current State | 20 |
| 11. How to Run Safe Local Checks | 15 |
| 12. How Agents Should Work | 20 |
| 13. Current Status | 20 |
| 14. What Not To Do | 15 |
| **Total** | **~370 lines** |

This is roughly 2.3x the current 160-line README — appropriate given the structural increase.
