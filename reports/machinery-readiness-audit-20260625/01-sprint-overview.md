# Format Factory — Machinery Readiness Audit Sprint Overview
# Sprint ID: ff-machinery-readiness-audit-20260625
# Evidence Root: reports/machinery-readiness-audit-20260625/
# Generated: 2026-06-25

## Purpose

Answer the question: "Is the Format Factory machinery actually ready to produce the expected
product-deepening results, or will it continue creating malformed, non-qname, non-presentable,
non-repeatable source code?"

This is an INVESTIGATION + DESIGN sprint. No product source changes. No machinery source changes.
All artifacts are written to reports/machinery-readiness-audit-20260625/ only.

## Sprint Metadata

| Field | Value |
|---|---|
| Sprint ID | ff-machinery-readiness-audit-20260625 |
| Date | 2026-06-25 |
| Branch | main |
| Git HEAD | c7694fe4 |
| Head Message | chore(psl-close): immutable-percolating-forest CLOSED — §64 added, all-green convergence verified |
| Investigator | Claude Code (read-only) |
| Authority | Format Factory registry, AGENTS.md, CLAUDE.md |

## Preliminary Verdict

**READY_AFTER_TARGETED_MACHINERY_REPAIRS**

The existing product code is **professional quality** — QName-compliant, spec-literal, modular,
with meaningful tests. But the MACHINERY that should autonomously generate and govern new product
code has **6 documented systemic failures** that prevent repeatability and scalability:

1. **SAL pipeline is ghost infrastructure** — 3 of 20 tools active; 17 dormant; fact extraction
   ran once (2026-05-06) and stopped permanently.
2. **Capability layer output is never consumed** — 1,132 gaps generated but autonomous task
   generator ignores gap-ledger; uses hardcoded `_EXPANSION_GOALS` list instead.
3. **No capability-to-feature compiler** — pipeline ends at capability map; nothing converts
   gap → code skeleton or spec fact → implementation taskcard.
4. **Spec-literal parity not durably enforced** — 67+ wiring points exist prompt-only;
   agents follow instructions once then forget without code-enforced governance chain.
5. **Autonomous supervision partially wired** — lane ownership, DAG ordering, overclaim
   detection all prompt-only; not code-enforced.
6. **Zero durable learning** — no failure-memory.json; corrections don't propagate to
   skills/validators/schemas; system repeats same mistakes indefinitely.

## What Was Previously Done (Evidence)

- 14 Python FOSS formats: PROOF_LEVEL_4+ (consumer roundtrip verified) — human-supervised
- FODS/FODT/Netpbm: G11-G APPROVED by Babar Raza (2026-06-05); all 8 readiness criteria PASS
- 20 QName registries: created and populated (shared/qname-registry/)
- 9 domain model classes: created with spec_qname (models.py per format)
- 16 packages: built and installed (0.1.0 dev versions)
- 82 governance validator tests: PASS (48 validators active)

## What This Audit Covers

10 investigation lanes, 22 artifacts:

| Lane | Topic | Artifacts |
|---|---|---|
| A | Repository, governance, evidence state | 01, 02 |
| B | QName schema and source organization | 03, 04 |
| C | Product source quality | 05 |
| D | Skills and repeatability | 06 |
| E | SAL / Spec Authority Layer | 07 |
| F | Capability layer | 08 |
| G | Downstream product-generation layers | 09 |
| H | Autonomous supervisor and continuation | 10, 11 |
| I | Backfill and migration facility | 12 |
| J | Product deepening readiness | 13, 14 |
| All | Gap matrix, taskcards, repair plan | 15–18 |
| All | Verdict, next prompt, evidence index | 19–22 |

## Non-Negotiable Evidence Rules (enforced by this sprint)

1. Every claim cites source file path, test result, command output, or "not found / not proven"
2. No reliance on summaries — all claims verified against actual source
3. Separated: built / working / repeatable / governed / autonomous / production-ready
4. Passing tests alone are not sufficient proof — what they prove and what they don't is stated
5. QName compliance proven from code paths, not assertions
6. Source quality reviewed AS source code, not as feature behavior
