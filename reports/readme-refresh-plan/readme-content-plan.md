# TC-README-PLAN-004: README Content Plan
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

For each README section: title, purpose, exact claims, evidence, stale content to replace, conditional content, risks.

---

## Section 1: `# Format Factory`

**Purpose:** One-paragraph project identity. Fast orientation for any reader.

**Claims to include:**
- "A File Format Acquisition System producing legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats."
- "The project never engages in unauthorized binary reverse engineering, bypasses access controls, or violates intellectual property rights."
- "commercial_product_ready: false. Gate 11 (commercial readiness) has not been approved."

**Evidence paths:**
- README.md lines 1–11 (retain core language)
- AGENTS.md (identity + legal constraints)
- reports/supervisor/approval-gates.md (commercial_product_ready: false)

**Stale content to replace:** None — this section is broadly accurate; expand with gate status caveat.

**Conditional/proposed:** None.

**Risk if overstated:** Claiming commercial readiness would be false; kept out.

---

## Section 2: `## Product-First Mission`

**Purpose:** Explain WHY the project is structured as it is — POC delivery first, machinery second.

**Claims to include:**
- "On 2026-06-03, a strategic correction was applied: Product-First POC Operating Model (master-plan §43)."
- "All machinery (supervisor automation, skills, acceleration) exists to serve POC delivery — not the reverse."
- "Evidence is required, but evidence is not the goal."
- POC goal: deliver proven capability for 3 commercial .NET products and 3+ FOSS Python products.
- "No machinery lane passes unless it removes a product blocker, prevents a false verdict, or improves Mainstream throughput."

**Evidence paths:**
- `plans/master-plan.md §43` (strategic correction)
- `state/current-state.md` (strategic correction date)
- `docs/governance/product-first-operating-model.md` (5 operating rules)
- `docs/governance/machinery-success-criteria.md` (machinery PASS criteria)

**Stale content to replace:** All of old "Project Goals" section (misleading "prepare FUTURE .NET").

**Conditional:** None.

**Risk if overstated:** Do not claim POC is complete; commercial_product_ready remains false.

---

## Section 3: `## Current POC Targets`

**Purpose:** Tell an incoming agent EXACTLY what is being built. Most important section.

**Claims to include:**

### Commercial .NET Products (3)
| Format | Description | Gate Status | Source | Tests |
|--------|-------------|-------------|--------|-------|
| FODS .NET | Flat OpenDocument Spreadsheet | Gates 1–10 PASSED; Gate 11 NOT_STARTED | src/net/fods/ | tests/net/fods/ |
| FODT .NET | Flat OpenDocument Text | Gates 1–10 PASSED; Gate 11 NOT_STARTED | src/net/fodt/ | tests/net/fodt/ |
| Netpbm .NET | Netpbm raster image format (PBM/PGM/PPM) | POC active | src/net/netpbm/ | tests/net/netpbm/ |

### FOSS / Reduced Python Products (3)
| Format | Description | POC Status | Source | Tests |
|--------|-------------|-----------|--------|-------|
| ZST | Zstandard compression codec | production_track_real | src/python/zst/ | tests/python/zst/ |
| Python Netpbm (PBM/PGM/PPM) | Netpbm raster image parser/writer | production_track_real | src/python/pbm/, pgm/, ppm/ | tests/python/ |
| SYLK | Symbolic Link Exchange format (spreadsheet) | POC active | src/python/sylk/ | tests/python/sylk/ |

### On-Hold
- DIF: ON_HOLD (empirical evidence exists; not promoted)
- QOI: ON_HOLD

**Additional required notes:**
- "Gate 11 (commercial readiness) has NOT been approved for any format. Requires written approval from Babar Raza."
- "commercial_product_ready: false for all formats."
- "SVG is NOT a POC target. Aspose already supports SVG; Netpbm (raster) is the imaging target."
- "Gnumeric: staged/conditional — Gate 1 approved but not in active POC iteration."

**Evidence paths:**
- `product-capability-matrix/poc-targets.yaml` (AUTHORITATIVE — primary source)
- `registry/format-registry.yaml` (gate status)
- `src/net/netpbm/` (Netpbm .NET confirmed)
- `reports/supervisor/approval-gates.md` (Gate 11 NOT_STARTED)
- `state/current-state.md` (POC targets section)

**Stale content to replace:**
- "First Pilots: FODS and FODT" section (Netpbm missing; FOSS targets missing)
- "Supported Format Families" section (SVG misleading; Netpbm absent)

**Conditional:** None — all three commercial .NET and three FOSS targets are CONFIRMED.

**Risk if overstated:** Do not claim Gnumeric or DIF are active targets without poc-targets.yaml confirmation.

---

## Section 4: `## Repository Layout`

**Purpose:** Accurate directory map for incoming agents and developers.

**Claims to include:** All directories CONFIRMED from glob:

```
src/                 Production source code
  net/fods/          FODS .NET (FodsDocument.cs, FodsParser.cs, FodsWriter.cs, exporters)
  net/fodt/          FODT .NET (FodtDocument.cs, FodtParser.cs, FodtWriter.cs, exporters)
  net/netpbm/        Netpbm .NET (NetpbmImage.cs, NetpbmParser.cs, NetpbmWriter.cs)
  net/csv/           FormatFactory.Csv writer library (CsvWriter.cs)
  net/html/          FormatFactory.Html writer library (HtmlWriter.cs)
  net/txt/           FormatFactory.Txt writer library (TxtWriter.cs)
  net/markdown/      FormatFactory.Markdown writer library (MarkdownWriter.cs)
  python/            Python FOSS format libraries (18+ format dirs including fods, fodt, pbm, pgm, ppm, sylk, zst)
tests/               Product tests
  net/fods/          FODS .NET tests (116+ files)
  net/fodt/          FODT .NET tests (115+ files)
  net/netpbm/        Netpbm .NET tests (48+ files)
  python/            Python FOSS tests (20+ format dirs)
examples/            Code examples
  net/               C# class file examples (fods, fodt, netpbm)
  dotnet/            dotnet-script .csx examples (fods, fodt, netpbm)
  python/            Python examples (10+ format dirs)
docs/                Documentation
  governance/        13 governance documents (four-stream model, AI authority, external tools)
  prompt-templates/  15 stream-specific execution templates
  automation/        Supervisor/worker contract
plans/               Living master plan (AUTHORITATIVE for decisions and phase state)
registry/            Format registry (22 formats with gate status)
product-capability-matrix/  POC readiness dashboard
tools/
  supervisor/        39 Python automation scripts (autonomous cycle, grading, routing, evidence)
  requirements_authority/   Requirements/capability authority tools
  specification-authority-layer/  Specification authority tools
.supervisor/         Skill registry, context pack, policies, project memory
.claude/             Claude Code configuration
  commands/          30 skill command files
reports/             Supervisor outputs and sprint artifacts
  supervisor/        session-resume.md, approval-gates.md, next-sprint.md, contradictions.md
.local/              Local-only sprint state (gitignored — NOT pushed to repo)
  evidences/         Evidence declarations per sprint
  supervisor/reviews/ Review package ZIPs per sprint
acquisition-packs/   Per-format evidence, legal notes (older sprints)
samples/             Licensed sample corpus with provenance records
```

**Evidence paths:** All from confirmed glob results + agent exploration.

**Stale content to replace:** Old repository structure section (missing tools/supervisor/, .supervisor/, examples/, reports/supervisor/, .local/)

**Risk if overstated:** Do not list directories that don't exist. Every listed dir is CONFIRMED.

---

## Section 5: `## Four-Stream Operating Model`

**Purpose:** Explain how the project executes via 4 parallel streams.

**Core claim:** "All work is structured across four parallel, isolated streams. Each stream has defined responsibilities, hard rules, and output requirements."

**Evidence:** `docs/governance/four-stream-operating-model.md`, `docs/governance/lane-definitions.md`

### 5.1 Mainstream Product
**Claims:** Builds real capability; owns POC readiness; runs as mega-train iteration; must produce 1+ API + tests per PASS; 8 hard stops (no continuation past: credentials needed, git push, Gate 8/11, etc.); 7 false stops (do not stop for: missing machinery, Ruflo absent, prompt failure, etc.)

**Evidence:** `docs/governance/mainstream-product-output-floor.md`, `docs/governance/mainstream-poc-mega-train.md`

### 5.2 Acceleration / AI Cognitive Layer
**Claims:** Two sub-lanes — Governance Harness (A) and AI Product Acceleration (B). AI may observe/plan/critique/accelerate (all ai_draft). AI may NOT approve gates/mark capability/override tests/push/publish. All AI output remains ai_draft until validated by tests. Anthropic Claude API is the only approved AI gateway.

**Evidence:** `docs/governance/acceleration-definition.md`, `docs/governance/ai-authority-boundary.md`

### 5.3 Skills / Governed Execution
**Claims:** 25 skills, 24 active. Skills provide reusable execution contracts with allowed files, validation commands, transcripts, rollback, and evidence. Skills make Mainstream faster/safer — skills that only validate other skills do not count. 30 skill command files under .claude/commands/.

**Evidence:** `.supervisor/skill-registry.yaml`, `docs/governance/superpowers-skill-intake.md`

### 5.4 Autonomous Supervisor / Continuation
**Claims:** Deterministic traffic controller. 39 Python tools. Reads evidence declarations; grades work; routes next sprint; detects stalls; prevents false PASS/STOP. Current mode: MODE 4 (MCP ACTIVE). Hard stops prevent autonomous continuation for: git push, Gate 8/11 approval, publication, MCP activation changes, destructive git ops.

**Evidence:** `docs/governance/autonomous-supervisor-role.md`, `tools/supervisor/supervisor_loop.py`, `reports/supervisor/approval-gates.md`

---

## Section 6: `## External Tools`

**Purpose:** Explain governance around 3 external tools: Ruflo, Superpowers, GhidraMCP.

### 6.1 Ruflo
**Claims:**
- Optional runtime orchestration for lane spawning, loop iteration, continuation
- Does NOT control: gate approval, taskcard closure, evidence verdict, git operations, secrets
- Current status: NOT installed in this repo [CONFIRMED: no Ruflo daemon running]
- Full loop requires Supervisor approval + human authorization (hard stop) [PROPOSED status]
- Fallback without Ruflo: sequential lane execution [CONFIRMED as current behavior]

**Evidence:** `docs/governance/ruflo-runtime-governance.md`, `docs/governance/external-tool-architecture.md`
**Risk:** Do not imply Ruflo is installed or active.

### 6.2 Superpowers Marketplace
**Claims:**
- External skill-pattern source; must be normalized into local wrappers before use
- No blind install; plugin install = HIGH risk (disabled by default)
- 5-step normalization: review → risk classification → local wrapper → registry entry → activation gate
- Current status: no Superpowers skills installed [CONFIRMED]

**Evidence:** `docs/governance/superpowers-skill-intake.md`
**Risk:** Do not imply any Superpowers skills are currently active.

### 6.3 GhidraMCP
**Claims:**
- Specialist tool for authorized binary/sample format analysis only
- DISABLED_BY_DEFAULT [CONFIRMED: docs/governance/ghidra-mcp-compliance-gate.md]
- Requires: ownership/license basis, input hash, compliance note, human auth, Supervisor approval
- Output labeled `ghidra_ai_draft`; no capability matrix update from output alone
- Hard prohibition: no MCP installation without compliance gate

**Evidence:** `docs/governance/ghidra-mcp-compliance-gate.md`
**Conditional:** Only describe as available; emphasize DISABLED status.

---

## Section 7: `## AI Usage and Authority Boundary`

**Claims:**
- Core rule: "AI thinks and drafts. Evidence decides." [CONFIRMED: ai-authority-boundary.md]
- AI output must be labeled `ai_draft` until tests validate
- AI MAY: observe state, reason about next steps, rank gaps, design approaches, critique evidence, route work, summarize results, generate prompts
- AI MAY NOT: mark capability complete, approve any gate, override tests/validators, push/commit/publish, write secrets, become authority over taskcard closure or registry mutations
- Approved AI gateway: Anthropic Claude API only (no paid third-party APIs in product path)

**Evidence:** `docs/governance/ai-authority-boundary.md`
**Stale content to replace:** Old "Agent Methodology" section (stale doc references).
**Risk:** Do not overstate AI capabilities or imply AI is the decision-maker.

---

## Section 8: `## Governance and Safety Rules`

**Claims:**
- Read `AGENTS.md` before any action [CONFIRMED: AGENTS.md exists]
- Read `CLAUDE.md` for session-start instructions [CONFIRMED: CLAUDE.md exists]
- No gate self-approval (1–11); Gate 11 requires Babar Raza written approval [CONFIRMED: approval-gates.md]
- No git push without explicit user authorization [CONFIRMED: CLAUDE.md]
- All src/ edits since R90 require product-code ledger entry [CONFIRMED: validate_product_code_ledger.py]
- Skill invocation requires exact file scope per skill-registry.yaml [CONFIRMED: skill-registry.yaml]
- AI output remains ai_draft until validated [CONFIRMED: ai-authority-boundary.md]
- Format Factory authority is FINAL; supervisor is advisory [CONFIRMED: session-resume.md]
- MCP status: MODE 4 ACTIVE (`.vscode/mcp.json` verified) [CONFIRMED: approval-gates.md]

**Evidence paths:** `AGENTS.md`, `CLAUDE.md`, `.supervisor/policies.yaml`, `docs/governance/lane-definitions.md`
**Stale content to replace:** "Contributing" section (points to GOVERNANCE.md — may not exist).
**Risk:** Do not overstate or understate governance requirements.

---

## Section 9: `## Evidence, Taskcards, and Review Packages`

**Claims:**
- Each sprint produces `.local/evidences/<run_id>/evidence-declaration.yaml` [CONFIRMED: .local/evidences/ structure]
- Sprint closeout: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>` [CONFIRMED: autonomous_cycle.py]
- Exit codes: 0 = accepted; 3 = critical rework; 1 = invalid YAML; 9 = error [CONFIRMED: supervisor_loop.py]
- Review packages: `python tools/supervisor/build_declaration_review_package.py --declaration <path>` [CONFIRMED: script exists]
- Review package output: `.local/supervisor/reviews/<run_id>/declaration-review-package.zip` [CONFIRMED: evidence dirs]
- `.local/` is gitignored — local sprint state is NOT pushed [CONFIRMED: .gitignore]
- Always report evidence package with ABSOLUTE path and SHA-256 [CONFIRMED: MEMORY.md instructions]
- Taskcards promoted via `promote-gap-to-taskcard` skill or plans/master-plan.md sections

**Evidence paths:** `docs/automation/supervisor-worker-contract.md`, `tools/supervisor/autonomous_cycle.py`, `tools/supervisor/build_declaration_review_package.py`
**Risk:** Do not describe evidence workflow from memory; confirm from supervisor_loop.py.

---

## Section 10: `## How to Inspect Current State`

**Exact references (all CONFIRMED):**
1. `reports/supervisor/session-resume.md` — first file to read at session start
2. `reports/supervisor/approval-gates.md` — AUTONOMOUS_CONTINUE: YES/NO; gate authority
3. `reports/supervisor/contradictions.md` — fix contradictions before advancing
4. `state/current-state.md` — full project snapshot (human-readable)
5. `product-capability-matrix/poc-targets.yaml` — POC dashboard (AUTHORITATIVE)
6. `plans/master-plan.md` — all decisions (AUTHORITY)
7. `reports/supervisor/next-sprint.md` — next sprint task list (if autonomous continue)
8. `.supervisor/context-pack.yaml` — machine-readable project snapshot
9. `.supervisor/project-memory.md` — 175+ sprint memory entries

**Note:** `.local/supervisor/reviews/<latest>/declaration-review-package.zip` for last evidence package.

---

## Section 11: `## How to Run Safe Local Checks`

**Safe commands (no side effects):**
```bash
# Supervisor pipeline info
python tools/supervisor/supervisor_loop.py --help

# Read-only state snapshot
python tools/supervisor/build_context_pack.py

# Python tests (read-only)
python -m pytest tests/python/ -x -q

# .NET tests (read-only)
dotnet test

# Git state
git status --short
git log --oneline -10
```

**Unsafe without authorization:**
```bash
# NEVER without explicit user approval:
git push
git commit
# Gate approval
# Package publication
```

---

## Section 12: `## How Agents Should Work in This Repo`

**Mandatory onboarding sequence:**
1. Read `AGENTS.md` (agent operating contract)
2. Read `CLAUDE.md` (session instructions + sprint closeout procedure)
3. Read `reports/supervisor/session-resume.md` (last sprint briefing)
4. Check `reports/supervisor/approval-gates.md` (AUTONOMOUS_CONTINUE)
5. If contradictions: read `reports/supervisor/contradictions.md`, fix before advancing
6. Read `plans/master-plan.md` (AUTHORITY)
7. Begin work only from `reports/supervisor/next-sprint.md` tasks (if AUTONOMOUS_CONTINUE: YES)

**All agents must:**
- Source every claim from repo files — not from memory or prior prompts
- Declare all work in `evidence-declaration.yaml` at sprint end
- Run `autonomous-cycle` at sprint end; check exit code
- Use product-code ledger for all src/ edits (R90+)
- Label all AI output `ai_draft`; validate with tests before promoting
- Report evidence package with ABSOLUTE path + SHA-256

---

## Section 13: `## Current Status`

**All CONFIRMED from repo files:**
- Latest sprint: R118 (2026-06-05)
- Last committed sprint: R93 (2026-06-02)
- commercial_product_ready: false
- Gate 11: NOT_STARTED
- AUTONOMOUS_CONTINUE: YES
- Critical contradictions: 0
- Tests (last sprint): 1423 passed / 0 failed
- MCP: MODE 4 ACTIVE

**Production blockers (from state/current-state.md):**
1. G11-G_NOT_STARTED: Gate 11 requires Babar Raza written approval
2. GATE8_AWAITING_HUMAN_APPROVAL: Security review pending for several formats
3. PACKAGE_NOT_PUSHED: All POC artifacts are local-only
4. NO_PUSH_AUTHORIZATION: git push requires explicit user approval
5. PRODUCT_BREADTH_WEAK: Breadth insufficient for full POC goal (in progress)

**Note:** "For the authoritative current state, always read `state/current-state.md` and `reports/supervisor/session-resume.md` — not this README, which may lag."

**Risk:** README will become stale again. Instruct readers to trust state/current-state.md over README.

---

## Section 14: `## What Not To Do`

**All backed by governance documents:**

| Prohibition | Source |
|------------|--------|
| Do not push without explicit user authorization | CLAUDE.md; AGENTS.md |
| Do not self-approve any gate (1–11) | AGENTS.md; docs/governance/ |
| Do not claim commercial_product_ready = true | approval-gates.md |
| Do not edit src/ without a product-code ledger entry (R90+) | validate_product_code_ledger.py |
| Do not install Ruflo without Supervisor approval + human auth | ruflo-runtime-governance.md |
| Do not install Superpowers plugins (HIGH risk — disabled) | superpowers-skill-intake.md |
| Do not activate GhidraMCP without compliance gate | ghidra-mcp-compliance-gate.md |
| Do not treat AI output as authoritative without test validation | ai-authority-boundary.md |
| Do not trust MEMORY.md or prior prompts without repo confirmation | CLAUDE.md; AGENTS.md |
| Do not commit without user authorization | CLAUDE.md |
| Do not mark capability complete without passing tests + capability matrix update | machinery-success-criteria.md |
| Do not skip evidence declaration at sprint closeout | docs/automation/supervisor-worker-contract.md |
| Do not use SVG as the imaging POC target (Aspose already supports SVG) | governance intent; poc-targets.yaml |
