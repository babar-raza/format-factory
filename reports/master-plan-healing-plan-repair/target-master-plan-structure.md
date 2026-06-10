# Target Master Plan Structure

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10
**Target:** ~400-700 lines (from 2229 — 70-80% reduction)

## Proposed Lean Structure

```
Header block (20 lines)
  - version, last_verified, last_updated
  - phase summary (1 sentence)
  - canonical source pointers (poc-targets.yaml, session-resume.md, format-registry.yaml)

Section 1 — Non-Negotiable Operating Rules (20 lines, condensed from 21)
  - Remove stale rule about bundle upload (rule 6)
  - Update rule 6 to reference declaration-driven pipeline
  - Keep all safety rules intact

Section 2 — Project Purpose (15 lines, keep as-is)

Section 3 — Desired End State and POC Targets (40 lines)
  - Merge old Section 3 (end state) + Section 40.2 (POC targets)
  - Pointer to poc-targets.yaml as canonical product target list
  - 3 commercial .NET + 8 FOSS/reduced targets listed
  - Success criteria from Section 40.3

Section 4 — Feature Tier Model (15 lines, keep as-is)

Section 5 — Four-Stream Architecture (30 lines)
  - Condensed from Section 43
  - Pointer to docs/governance/four-stream-operating-model.md
  - Lane definitions summary
  - Cross-stream dependency model (5 lines)

Section 6 — Mainstream Product Lane (15 lines)
  - Pointer to docs/governance/mainstream-poc-mega-train.md
  - Product-output floor (pointer to mainstream-product-output-floor.md)
  - Dogfooding requirement (5 lines from Section 40.4)

Section 7 — Acceleration Layer (15 lines)
  - Pointer to docs/governance/acceleration-definition.md
  - Acceleration-A and Acceleration-B summary

Section 8 — Skills / Governed Execution (15 lines)
  - Pointer to .supervisor/skill-registry.yaml
  - Product Factory Acceleration Layer summary (from Section 42)

Section 9 — Autonomous Supervisor (15 lines)
  - Pointer to docs/governance/autonomous-supervisor-role.md
  - Declaration-driven pipeline summary (from Section 41)
  - Continuous autonomous loop protocol (5 lines from Section 41.6)

Section 10 — AI Authority Boundary (10 lines)
  - Pointer to docs/governance/ai-authority-boundary.md
  - "AI thinks and drafts. Evidence decides." principle

Section 11 — External Tool Architecture (10 lines)
  - Pointer to docs/governance/external-tool-architecture.md
  - Ruflo, Superpowers, GhidraMCP summary

Section 12 — Evidence and Review Package Model (15 lines)
  - Declaration-driven model (evidence-declaration.yaml + autonomous_cycle.py)
  - Review package build command
  - Grading model summary (8 levels)

Section 13 — Gate Model (20 lines)
  - 11 gates summary (from Section 20)
  - Gate rules (human approval required)
  - Pointer to registry/format-registry.yaml

Section 14 — Phase Model (25 lines)
  - Condensed from Section 8
  - Phase 0-4+ with allowed/forbidden paths
  - Pointer to Section 10 (forbidden paths) — keep Section 10 as-is

Section 15 — Legal and Oracle Models (15 lines)
  - Condensed from Sections 21 + 22
  - 6 legal categories
  - Spec-is-authority principle

Section 16 — Decision Register (80 lines, condensed)
  - Keep all DECs but condense notes column
  - Remove duplicate/stale entries

Section 17 — Current Status Summary (20 lines)
  - Source pointers only: poc-targets.yaml, session-resume.md, format-registry.yaml
  - No "next sprint" narrative
  - No run history
  - Gate 11 status from poc-targets.yaml

Section 18 — Governance, Visibility, Release Control (20 lines)
  - Condensed from Sections 17, 18
  - Pointer to docs/governance/ for detailed rules
  - Canonical source map pointer

Section 19 — Memory Layer (10 lines)
  - Condensed from Section 35

Section 20 — Agent Instructions (10 lines)
  - Condensed from Section 34

Section 21 — Independent Authority Layers (15 lines)
  - Condensed from Section 44
  - Pointer to docs/governance/independent-authority-layers.md

ARCHIVE-PTR block (10 lines)
  - Pointer to docs/history/master-plan-full-before-healing-<date>.md
  - Pointer to docs/history/master-plan-archived-sections-<date>.md
  - List of archived section numbers

Footer (3 lines)
  - Version, date, authority statement
```

**Estimated total: ~470 lines** (from 2229 — 79% reduction)

## Section Disposition Map

| Old Section | Action | New Section | Notes |
|-------------|--------|-------------|-------|
| Header | rewrite | Header | Remove stale narrative |
| §1 | condense | §1 | Update rule 6 |
| §2 | keep | §2 | Unchanged |
| §3 | merge | §3 | Merge with §40.2 |
| §4 | keep | §4 | Unchanged |
| §5 | rewrite | (rules in §1) | Amend split-out rule |
| §6 | condense | §17 | Replace with source pointers |
| §7 | archive | ARCHIVE | Superseded by §41 |
| §8 | condense | §14 | Keep phase definitions |
| §9 | archive | ARCHIVE | Phase 0 historical |
| §10 | keep | (in §14) | Forbidden paths |
| §11 | rewrite | (in §20) | Remove Codex |
| §12 | keep | (in §20) | Plan/execution mode |
| §13 | rewrite | (in §8) | Update command inventory |
| §14 | condense | (in §10) | LLM strategy |
| §15 | keep | (in §18) | Artifact model |
| §16 | keep | (in §18) | Reuse rules |
| §17 | condense | §18 | Release control |
| §18 | condense | §18 | Visibility schema |
| §19 | keep | (in §13) | Acquisition workflow |
| §20 | keep | §13 | Gate model |
| §21 | condense | §15 | Legal model |
| §22 | condense | §15 | Oracle model |
| §23 | condense | (in §3) | Pilot recommendation |
| §24 | rewrite | (in §13) | WIP limits |
| §25 | archive | ARCHIVE | Stale taskcards |
| §26 | condense | §16 | Decision register |
| §27 | archive | ARCHIVE | Gap register |
| §28 | archive | ARCHIVE | Healing gap register |
| §29 | condense | (in §16) | Risk register |
| §30 | keep | (in §13) | Gate reference |
| §31 | archive | ARCHIVE | Phase 0 checklist |
| §32 | archive | ARCHIVE | Run history table |
| §33 | archive | ARCHIVE | Run commit ledger |
| §34 | condense | §20 | Agent instructions |
| §35 | condense | §19 | Memory layer |
| §36 | archive | ARCHIVE | S-F2F roadmap |
| §37 | archive | ARCHIVE | Format understanding |
| §38 | condense | (in §3) | Expansion roadmap |
| §39 | archive | ARCHIVE | AI platform layer |
| §40 | keep | §3, §6 | POC direction |
| §41 | keep | §9, §12 | Declaration pipeline |
| §42 | keep | §8 | Acceleration layer |
| §43 | keep | §5, §6 | Product-first model |
| §44 | condense | §21 | Authority layers |
| Footer | rewrite | Footer | Fix version |

## Archived Sections (13 total, ~880 lines)

Sections to archive: §7, §9, §25, §27, §28, §31, §32, §33, §36, §37, §39

All archived content goes to `docs/history/master-plan-archived-sections-<date>.md` with the full backup at `docs/history/master-plan-full-before-healing-<date>.md`.
