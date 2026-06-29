# Final Verdict

**Sprint/Run ID:** ff-archaeology-20260625
**Audit Date:** 2026-06-25
**Investigator:** Forensic Archaeology Agent (3 parallel Explore agents)

---

## VERDICT

```
READY_AFTER_TARGETED_MACHINERY_REPAIRS
```

---

## Verdict Rationale

Format Factory IS producing professional, QName-aligned, spec-hierarchy-based format libraries.
The machinery is operational. The product output is real. The gaps are targeted and fixable.

**System IS:**
- Generating Gen4 (Live DOM / Spec-Identity) libraries for 13/20 Python formats
- Consuming 14,284 SAL facts in capability map generation (proven via sal_enrichment block)
- Enforcing 50 governance validators across all sprint submissions
- Running 1,609 tests with 0 failures as of audit date
- Producing typed domain models with `from_file()` factory, `spec_qname: ClassVar[str]`,
  `to_dict()`, and typed property access for 13 Python formats
- Maintaining `Compat/` facades in the correct location for ALL format-prefixed names
- Enforcing the spec/ hierarchy architecture pattern across all 20 Python formats

**System IS NOT (yet):**
- Producing Gen4 for 7 Python formats (ODS, ODT, PBM, PGM, PPM, QOI, SYLK) — domain models missing
- Fully connecting capability compiler to supervisor loop (gap_ledger_to_work_items.py standalone)
- Auto-backfilling spec_qname from registry (still manual task-driven)
- QName-compliant for DIF (2 gaps) and FODG (1 gap) — production classes still use instance field

**Why NOT "NOT_READY_REPAIR_MACHINERY_FIRST":**
- 10/20 Python formats are in GREEN state with no immediate blockers
- Gate 11 sub-gate is APPROVED for FODS/FODT (the commercial product)
- The 3 critical gaps are surgical fixes (<2 hours), not architectural overhauls
- Autonomous supervisor is GREEN with CONTINUE verdict

**Why NOT "READY_FOR_PRODUCT_DEEPENING":**
- 3 HIGH-severity gaps block clean sprint submission for DIF and FODG
- 7 Gen3 formats need domain models before they can claim Gen4 parity
- Capability compiler is not fully integrated (open gaps may be invisible to task selection)

---

## 21-Question Self-Check

### Repository & State

**Q1: Is the repository in a clean, known-good state?**
PARTIAL. HEAD c6b24706 is stable. ~130 dirty files are classified sprint artifacts and evidence files, not corrupted state. No data loss risk. Continuation signal is GREEN (autonomous_continue=true). Working tree has no uncommitted merge conflicts or broken state. Verdict: ACCEPTABLE for continued sprint work.

**Q2: Are all plan files and governance docs consistent?**
YES. `plans/master-plan.md`, `plans/strategic/spec-to-feature-radical-correction-plan.md`, `approval-gates.md`, `session-resume.md` all reflect consistent state (iteration 1/12, last sprint c6b24706, AUTONOMOUS_CONTINUE YES). No contradictions detected in `reports/supervisor/contradictions.json` at audit time.

**Q3: Is the continuation signal authentic and current?**
YES. `continuation-signal.json` contains `session_id: f9145814a1ee`, `autonomous_continue: true`, `iteration: 1`, 0 rework_items, 0 hard_stops. CCI-MVP enforces session_id matching. Signal is not stale (matches HEAD commit).

### Source & Quality

**Q4: Is the Python source inventory complete and accurate?**
YES. 20 Python formats verified: abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst. All have `src/python/{format}/` directory. All have spec/ hierarchy and Compat/ facades. 13 have domain model classes (models.py). 7 do not (Gen3). Per-format details in `source-inventory.md`.

**Q5: Is the .NET source inventory complete and accurate?**
YES. 10 .NET projects: csv, fods, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst. FODS and FODT are commercial-grade (Gate 11 sub-gate approved). HTML, Markdown, TXT are exporter targets (not standalone products). Others are library-grade (NDJSON, TSV, ZST) or prototype-grade (CSV, NetPBM).

**Q6: Is the source hygiene acceptable?**
YES with caveats. Nested `build/lib/` in 8 packages — normal development artifacts, excluded from pip install. 20 `.egg-info/` directories — normal. 17 architecture_only Python spec stubs + 12 .NET — intentional by design, governed by V48. 16 analytics masquerade files (GAP-PROD-INV-MASQ-001, deferred). No corrupt files, no unresolvable conflicts. Hygiene: GOOD.

**Q7: Are known_violations correctly capped and not worsening?**
YES. 47 known violations with write-once `baseline_loc_cap` values. 4 files are currently at-cap (neutral_model.py, fodg_codec.py, ndjson_analytics.py, fods/neutral_model.py). All others are under-cap (analytics extraction healed them). No new violations detected at audit time. GOV_BLOCK:validate_source_architecture NOT triggered.

### QName & Spec

**Q8: Is QName compliance production-ready?**
MOSTLY. 84.5% overall compliance. 15/20 formats at 95-100%. Three HIGH gaps: DIF (dif:data, dif:cell instance fields instead of ClassVar), FODG (draw:frame missing entirely). All `Compat/` facades are correctly placed. `spec/` hierarchy exists for all 20 formats. V53 validator is registered and enforcing. Target: 100% after QNAME-BACKFILL-001/002.

**Q9: Does the QName translation standard hold throughout the codebase?**
YES for spec/ and Compat/. PARTIAL for production codecs. The standard (`ns:localName` → `Ns.LocalName` in spec/ → `FormatLocalName` in Compat/ only) is correctly applied in all 20 Compat/ directories. It is partially violated in 2 production codecs (DIF, FODG) where spec_qname is either absent or an instance field. Fix is surgical (2 files).

**Q10: Is the spec/ hierarchy correct and complete?**
YES. All 20 Python formats have `spec/{namespace}/` directories. All C# `Spec/` directories follow the same pattern. All stubs have `# GENERATED — architecture_only` markers. V48 blocks any of these from being cited as RELEASE_GATE evidence. The hierarchy is scaffolding, not behavioral implementation — this is by design.

### SAL & Capability

**Q11: Is the SAL operational and producing value?**
YES. 14,284 facts, FACT-FORMAT-NNN stable IDs. SAL enrichment block present in unified-capability-map.json proves active consumption. 10 formats CHAIN_INTACT, 10 CHAIN_BROKEN_AT_SAL (expected for text/table/compression formats where spec parser is not extended). Refresh mechanism operational (refresh_check.py).

**Q12: Is the capability layer accurate and connected to features?**
PARTIAL. 1,909 records, SAL enrichment proven. Gap ledger 87.9% closed (995/1132). capability_feature_compiler.py is wired. gap_ledger_to_work_items.py is NOT wired into supervisor loop (standalone). This means some open gaps are invisible to automated task selection. Fix: CAP-REPAIR-001 (see machinery-repair-plan.md).

**Q13: Is the spec-to-feature pipeline repeatable?**
PARTIAL. SAL → capability map → gap ledger → work items pipeline exists but has the standalone-compiler gap. The pipeline is repeatable for the wired portion (capability_feature_compiler.py). Once CAP-REPAIR-001 is fixed, the full pipeline is repeatable end-to-end.

### Downstream Generation

**Q14: Is the downstream code generation producing professional output?**
YES for Gen4 formats. The pattern (spec/ → Compat/ → models.py → analytics.py) is correct and professional. No monolithic files for Gen4 formats. For Gen3 formats, the parser+Compat pattern is present but domain models are missing — output is functional but not typed-API-grade.

**Q15: Where is malformed or legacy code being produced?**
NONE currently being produced. All new sprint work uses skill-governed patterns. Legacy malformed code from pre-governance era (pre-June-2026) has been healed (analytics extraction sprints). 16 analytics masquerade files remain but are frozen (write-once cap, GAP-PROD-INV-MASQ-001 deferred).

### Skills & Supervisor

**Q16: Are the skills producing governed, QName-aligned output?**
YES. 37 command files categorized and governed. V41 enforces analytics.py placement. V43/V44 enforce skill attribution. V45 enforces transcript before acceptance. V48 blocks architecture_only in RELEASE_GATE. V53 enforces spec_qname ClassVar. 4 skill gaps identified (no auto-backfill skill, no Gen3→Gen4 upgrade skill, no .NET spec_qname injection, no cross-language parity skill) — these are additive gaps, not failures.

**Q17: Is the autonomous supervisor reliable?**
YES with known gaps. 50 validators registered. Session state GREEN. 5 known gaps: lane ownership prompt-only (not code-enforced), DAG ordering prompt-only, overclaim detector not auto-called, no durable failure memory, evidence_quality_zero degrades gracefully. All gaps are documented and in the plan backlog. None are blocking autonomous continuation.

**Q18: Is lane separation enforced?**
PARTIAL. GOV_BLOCK signals (2 named, non-overridable) are FULL enforcement. TC-GUARD-001 is FULL enforcement (code-level BLOCK). Wave 3 gate is plan-enforced only (not code-enforced). Lane ownership is prompt-only. V42 deepening suspension is partial (arithmetic pattern only). DAG ordering is prompt-only. Overall: GOOD with documented gaps for DAG and lane ownership.

### Readiness & Gates

**Q19: Is Gate 11 achievable for any product?**
YES. FODS and FODT have Gate 11 sub-gate G11-G APPROVED (2026-06-05). All C1-C20 (.NET) and P1-P11 (Python) criteria pass. V48 confirms architecture_only stubs are excluded from RELEASE_GATE evidence. Gate 11 EXECUTION requires Babar Raza commercial sign-off (TRUE_EXTERNAL_GATE). Packet preparation is agent-owned work (G11-001 taskcard).

**Q20: Which formats are safe for immediate product deepening?**
10 Python formats: ABW, CSV, FODS, FODT, GNUMERIC, NDJSON, TOML, TSV, XCF, ZST (all Gen4 GREEN).
2 .NET formats: FODS, FODT (Green, Gate 11 sub-gate approved).
BLOCKED for deepening: DIF, FODG (QName gaps must be fixed first). ODS, ODT, PBM, PGM, PPM, QOI, SYLK (domain models needed first).

**Q21: Is the system generating professional, repeatable, maintainable format libraries or prototype-shaped products?**

**PROFESSIONAL LIBRARIES (10 Python formats):** ABW, CSV, FODS, FODT, GNUMERIC, NDJSON, TOML, TSV, XCF, ZST — all have typed domain models, `from_file()` factory, `spec_qname: ClassVar[str]`, `Compat/` facades, analytics in separate files, exceptions.py, and 50+ tests each.

**FUNCTIONAL BUT NOT FULLY TYPED (7 Python formats):** ODS, ODT, PBM, PGM, PPM, QOI, SYLK — parsers and Compat/ work correctly but lack the domain model class that makes them professional-grade typed APIs.

**COMMERCIAL-GRADE .NET (2):** FODS, FODT — XML docs, nullable annotations, NuGet metadata, release notes.

**LIBRARY-GRADE .NET (3):** NDJSON, TSV, ZST — typed but thin test coverage, no NuGet metadata.

**Answer:** The system IS generating professional libraries for 10/20 Python formats and 2/10 .NET products. For 7 Python formats, it is generating functional-but-not-typed output. For 3 .NET products, it is generating library-grade output. For 5 .NET products, it is generating prototype or exporter-target output. The machinery producing these outputs is strong; the gaps are in the product coverage (7 formats missing domain models) not in the machinery itself.

---

## Verdict Summary

| Dimension | Score | Grade |
|-----------|-------|-------|
| Machinery health | 9/10 | A |
| QName compliance | 8.5/10 | B+ |
| Python product quality (Gen4) | 9/10 | A |
| Python product quality (Gen3) | 6/10 | C+ |
| .NET product quality (commercial) | 9.5/10 | A |
| .NET product quality (library) | 7/10 | B |
| SAL integrity | 9/10 | A |
| Capability layer | 8/10 | B+ |
| Test coverage | 8/10 | B+ |
| Governance enforcement | 9/10 | A |
| **Overall** | **8.4/10** | **B+** |

---

## Next Actions (Ordered)

1. Fix QNAME-BACKFILL-001 (DIF dif_parser.py — 2 ClassVar injections)
2. Fix QNAME-BACKFILL-002 (FODG fodg_codec.py — 1 ClassVar injection or authority class)
3. Wire CAP-REPAIR-001 (gap_ledger_to_work_items.py into autonomous_cycle Step 3a)
4. Create ODS domain model (SRC-STD-001) as first Gen3→Gen4 upgrade
5. Prepare G11-001 Gate 11 sign-off packet for Babar Raza review

After items 1-3: resume autonomous product deepening loop for 10 GREEN Python formats.
After items 1-5 + Babar Raza approval: execute Gate 11 for FODS and FODT commercial release.
