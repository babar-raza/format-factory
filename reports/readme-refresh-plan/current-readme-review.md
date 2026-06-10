# TC-README-PLAN-001: Current README Review
# Sprint: FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001
# Generated: 2026-06-05

## Overview

The current README.md is 160 lines, last substantively updated before sprint R93 (committed 2026-06-02).
The project has undergone a major strategic correction on 2026-06-03 (Product-First POC Operating Model,
master-plan §43) plus formalization of the Four-Stream Operating Model, AI authority boundary,
external tool governance, and autonomous supervisor. None of these appear in README.md.

**Verdict: README requires FULL REPLACEMENT.**

---

## Current README Sections

### Section 1: Header + What This Project Does (lines 1–12)
> "A File Format Acquisition System that produces legal parsers, converters, importers, exporters,
> validators, and compatibility tools for structured file formats."

**Assessment:** Broadly accurate; good opener. Missing: POC-first framing, autonomous AI execution model.

---

### Section 2: Project Goals (lines 15–26)
Six goals:
1. Understand file formats using official specifications
2. Create verified format knowledge
3. Build open-source Python libraries for selected formats
4. Prepare future .NET and commercial products under stricter approval rules
5. Use gates, tests, security review, and evidence bundles
6. Make the process repeatable

**Assessment:** Partially stale. Goal 4 ("prepare FUTURE .NET") misrepresents reality — .NET product
(FODS, FODT, Netpbm) is already built and actively developed. Goal 3 is accurate for Python OSS.
Missing: POC delivery as the immediate goal (not "future preparation").

---

### Section 3: Products Table (lines 30–38)

| Track | Technology | License | Status |
|-------|------------|---------|--------|
| Python open-source | Python 3.11+ | Apache 2.0 | Source created for FODS and FODT; no public release yet |
| .NET product library | net8.0, net10.0 | Proprietary | C4-C6 vertical slice for FODS and FODT; not commercial-ready |

**STALE / MISLEADING:**
- .NET product table lists only FODS and FODT. **Netpbm .NET is a third commercial product**
  confirmed at `src/net/netpbm/` with NetpbmImage.cs, NetpbmParser.cs, NetpbmWriter.cs,
  and tests under `tests/net/netpbm/` (116+ test files).
- "C4-C6 vertical slice" framing is outdated. FODS has 116+ test files, FODT has 115+ test files.
  Both have examples, dogfood exports, writer libraries. This is no longer a vertical slice.
- Python OSS: Only FODS/FODT listed. ZST, PBM/PGM/PPM, SYLK are active FOSS POC targets
  confirmed in `product-capability-matrix/poc-targets.yaml` and `src/python/` subdirs.
- "net8.0, net10.0" — need to confirm current target framework (likely net10.0 only now).

---

### Section 4: First Pilots: FODS and FODT (lines 40–54)

> "FODS Gates 1-10 passed. FODT Gates 1-10 passed."
> "commercial_readiness_in_progress (NOT approved)"

**Assessment:** Accurate baseline — gates 1-10 confirmed passed for both. Gate 11 NOT approved
is correct. However:
- Missing: Netpbm .NET as third commercial POC product
- Missing: FOSS POC products (ZST, PBM/PGM/PPM, SYLK)
- Missing: Four-stream model that drives execution
- Missing: Product-first POC direction (strategic correction 2026-06-03)
- The framing "First Pilots" is outdated — these are now part of a broader POC strategy

---

### Section 5: Supported Format Families (lines 56–70)

| Family | Examples |
|--------|---------|
| Cells | FODS, ODS, XLSX |
| Words | FODT, ODT, DOCX |
| Slides | FODP, ODP, PPTX |
| Imaging | SVG, PNG with metadata |
| Diagram/CAD | DrawingML, DXF |
| Archive | ZIP, TAR |

**STALE / MISLEADING:**
- "Six format families" framing implies equal treatment of all families. In reality, only specific
  POC targets are in active development: FODS, FODT, Netpbm (.NET commercial) and ZST, PBM/PGM/PPM,
  SYLK (Python FOSS). Other families are in registry but not in POC targets.
- **SVG is listed under Imaging.** The governance explicitly states: "SVG must NOT replace Netpbm
  because Aspose already supports SVG." Listing SVG creates false equivalence.
- Netpbm/PBM/PGM/PPM is NOT listed anywhere in this section despite being a confirmed POC target.
- DIF is listed by implication (Archive) but is actually ON_HOLD per poc-targets.yaml.
- FODP/FODG are Gate 1 approved only; not active POC targets.

---

### Section 6: Acquisition Pipeline (lines 72–89)

Lists all 11 gates with descriptions.

**Assessment:** Still accurate as a description of the gate model. However:
- Missing: Gate approval authority (only humans can approve; Babar Raza for Gate 11)
- Missing: Current gate status for each active format
- Missing: Context that POC iteration runs concurrently with gate pipeline
- No reference to autonomous supervisor, which now drives continuation decisions

---

### Section 7: Project Status (lines 91–109)

> "Current phase: Phase 3/4. FODS Gates 1-10 passed. FODT Gates 1-10 passed.
> Gate 11 commercial_readiness_in_progress (NOT approved).
> ZST Gates 1-4 prototype COMPLETE (R18, 2026-05-16)."

**SEVERELY STALE:**
- References sprint R18 (2026-05-16). Latest sprint is R118 (2026-06-05). 100 sprints stale.
- "Phase 3/4" — the four-stream operating model replaced this phase framing.
- "FODP Gate 1 APPROVED, FODG Gate 1 APPROVED, Gnumeric Gate 1 APPROVED, ABW Gate 1 APPROVED"
  in R18 — these were in R18; status has evolved.
- "ZST Gates 1-4 prototype COMPLETE (R18)" — ZST is now a confirmed FOSS POC target.
- Missing: Netpbm .NET commercial product (introduced after R18).
- Missing: SYLK as FOSS POC target.
- Missing: Four-stream model, AI authority boundary, autonomous supervisor.
- Missing: Product-code ledger (R90+), skill registry, MCP MODE 4.
- Missing: autonomous-cycle pipeline and evidence declaration workflow.
- The status section is misleadingly stale and will confuse any reader about current project state.

---

### Section 8: Repository Structure (lines 112–129)

```
docs/         Architecture, policy, and process documentation
plans/        Living master plan
taskcards/    Atomic work units
registry/     Format registry
acquisition-packs/  Per-format evidence
samples/      Licensed sample corpus
schemas/      Neutral-model schemas
prototypes/   Reference prototype parsers
src/          Production source code
tests/        Test fixtures
tools/        Acquisition, scoring, validation, evidence
reports/      Security and legal reports
.claude/      Claude Code configuration
```

**STALE / INCOMPLETE:**
- Missing: `tools/supervisor/` (39 Python scripts — the autonomous supervisor engine)
- Missing: `.supervisor/` (skill registry, context pack, policies, project memory, schemas)
- Missing: `.local/evidences/` (sprint evidence declarations — local only, gitignored)
- Missing: `reports/supervisor/` (session-resume, approval-gates, next-sprint, contradictions)
- Missing: `reports/readme-refresh-plan/` (this sprint's outputs)
- Missing: `examples/` (dotnet/, net/, python/ — confirmed from glob)
- `reports/` listed as "Security and legal reports" — now primarily supervisor outputs
- `tools/` listed as "Acquisition, scoring, validation, evidence" — now primarily supervisor tools
- `prototypes/` — still exists but is not the primary development path (src/ is)
- `acquisition-packs/` — exists but not the primary agent focus

---

### Section 9: Agent Methodology (lines 131–154)

References:
- `docs/agent-methodology-index.md`
- `docs/planning-methodology.md`
- `docs/agent-execution-handoff-standard.md`
- `docs/plan-hardening-checklist.md`
- `docs/fresh-chat-continuity-brief.md`
- `docs/prompts/README.md`
- `memory/00-index.md`

**STALE / PARTIALLY OUTDATED:**
- The primary session start instruction is now in `CLAUDE.md` (read session-resume.md first)
- `docs/prompt-templates/` (15 files) and `docs/governance/` (13 files) are the current operating
  documents — not referenced
- `reports/supervisor/session-resume.md` is the correct start-of-session file — not referenced
- `reports/supervisor/approval-gates.md` controls autonomous continuation — not referenced
- Skill registry at `.supervisor/skill-registry.yaml` (25 skills) — not referenced
- The four-stream model, autonomous supervisor, and AI authority boundary docs — not referenced

---

### Section 10: Contributing (lines 148–152)

References GOVERNANCE.md, AGENTS.md, docs/legal-and-licensing.md.

**Assessment:** AGENTS.md reference is correct and current. GOVERNANCE.md may not exist (not
confirmed in recent file listings). docs/legal-and-licensing.md is a pre-R90 doc. Mostly OK as
a pointer but needs governance docs update.

---

### Section 11: License (lines 155–160)

> "Open-source components: Apache 2.0. Commercial components: Proprietary. Evidence: Internal only."

**Assessment:** Still accurate. No change needed.

---

## Summary: What Is Missing

| Missing Topic | Source of Truth | Severity |
|--------------|----------------|----------|
| Product-First POC direction (2026-06-03) | state/current-state.md, master-plan §43 | CRITICAL |
| Four-Stream Operating Model | docs/governance/four-stream-operating-model.md | CRITICAL |
| Netpbm .NET as third commercial product | src/net/netpbm/, poc-targets.yaml | CRITICAL |
| FOSS targets: ZST, Python Netpbm, SYLK | poc-targets.yaml, src/python/ | CRITICAL |
| AI authority boundary ("AI drafts; evidence decides") | docs/governance/ai-authority-boundary.md | HIGH |
| External tools: Ruflo, Superpowers, GhidraMCP | docs/governance/external-tool-architecture.md | HIGH |
| Autonomous supervisor + continuation model | docs/governance/autonomous-supervisor-role.md | HIGH |
| Skill registry + governed execution | .supervisor/skill-registry.yaml | HIGH |
| Product-code ledger (R90+) | tools/supervisor/validate_product_code_ledger.py | HIGH |
| MCP status (MODE 4 ACTIVE) | reports/supervisor/approval-gates.md | MEDIUM |
| How agents onboard (CLAUDE.md, session-resume.md) | CLAUDE.md, AGENTS.md | HIGH |
| Evidence packages and review packages | .local/evidences/, docs/automation/ | HIGH |
| Supervisor pipeline commands | supervisor_loop.py, autonomous_cycle.py | HIGH |
| Missing directories (tools/supervisor/, .supervisor/) | confirmed from glob | HIGH |
| Current stream state (R118, not R18) | state/current-state.md | CRITICAL |

## Summary: What Is Stale

| Stale Content | Correct Current State |
|--------------|----------------------|
| Products table: only FODS/FODT .NET | Three commercial .NET: FODS, FODT, Netpbm |
| "Prepare future .NET" in goals | .NET products built and actively iterated |
| "C4-C6 vertical slice" framing | Full product with tests, examples, writers |
| Six format families with SVG | Six POC targets (Netpbm, not SVG) |
| Status references R18/ZST Gate 4 | R118, autonomous POC train complete |
| Phase 3/4 framing | Four-stream operating model |
| Repository structure missing 6+ dirs | tools/supervisor/, .supervisor/, examples/, reports/supervisor/ |
| Agent methodology docs are stale refs | CLAUDE.md + session-resume.md is the start |

## Verdict

**README requires FULL REPLACEMENT.** The structural changes are too large for targeted edits:
- 14 new sections to add
- Every existing section needs rewrite or major expansion
- Core architecture (four streams, AI boundary, external tools, autonomous supervisor) is entirely absent
- Current status section is 100 sprints stale
