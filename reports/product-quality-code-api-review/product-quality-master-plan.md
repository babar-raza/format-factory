# Product Quality Master Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Executive Summary

Format Factory has 30 products (10 .NET commercial, 20 Python FOSS). This master plan
documents the current quality state, identifies 20 concrete problems (PQ-001 to PQ-020),
and prescribes 5 fix sprints (QF-1 through QF-5) to bring products to release quality.

**Current state:** 3 .NET products are commercial candidates with gaps; 7 are not product-grade.
14 Python products are at PY-3 (production-usable FOSS); 6 need more work.

**Key blocker:** ZST .NET has no compress capability (P0, CRITICAL). FODS .NET has a false
Gate 11 approval claim in its csproj (P0, contradicts source). FODS Python has dual API
confusion (P0, blocks user adoption).

---

## 25 Master Plan Questions and Answers

### Q1: What products exist and what is their maturity?

30 products across 2 ecosystems:

**.NET Commercial (10):**
- FODS: Commercial Candidate (3.4/5) — needs stream load, README, Gate 11 fix
- FODT: Commercial Candidate (3.3/5) — same as FODS
- NetPBM: Commercial Candidate (3.4/5) — image transforms strong; exporter scope needs docs
- NDJSON: POC Candidate (2.8/5) — JsonElement model needs typed wrapper
- CSV: Demo Prototype (2.0/5) — thin product; not standalone commercial
- TSV: Demo Prototype (2.2/5) — same
- ZST: Demo Prototype (1.5/5) — CRITICAL: no write capability
- HTML/Markdown/TXT: NOT_PRODUCT (0.5/5) — writer helpers, not standalone products

**Python FOSS (20):**
- FODS, FODT: PY-4 (release candidates, P8/P9 gaps)
- ODS, ODT, ZST, NDJSON, TOML, CSV, TSV, SYLK, DIF, GNUMERIC, ABW, FODG, PBM, PGM, PPM: PY-3
- QOI, XCF: PY-2 (missing consumer roundtrip or write capability)
- FODP: PY-2 (read-only, undocumented)

### Q2: What are the most critical problems?

1. **PQ-007** (CRITICAL): ZST .NET has no write/compress capability
2. **PQ-006** (HIGH): FODS .NET csproj claims "Gate 11 approved" when source says NOT approved
3. **PQ-002** (HIGH): FODS Python exports dual API with no guidance
4. **PQ-001** (HIGH): All Python packages use wildcard imports — uncontrolled namespace
5. **PQ-004** (HIGH): All Python pyproject.toml missing required metadata
6. **PQ-005** (HIGH): All .NET csproj reference README.md that doesn't exist
7. **PQ-009** (HIGH): FODP Python is read-only but no user-facing documentation says so
8. **PQ-014** (HIGH): No README.md for any of the 30 products

### Q3: Which problems block release?

8 problems block release (blocks_release=true):
PQ-001, PQ-002, PQ-004, PQ-005, PQ-006, PQ-007, PQ-009, PQ-014

### Q4: What is the public API quality per product?

See `public-api-matrix.json` for detailed scores. Summary:
- Highest API score: NetPBM .NET (4.0/5)
- Lowest API score: FODP Python (1.2/5), ZST .NET (1.5/5), HTML .NET (0.8/5)
- Most products: 2.5–3.8/5 (acceptable to good)

### Q5: Are API conventions consistent across products?

No. Significant inconsistencies:
- .NET: Some products use `Load(path)`, others use `LoadFile(path)`, others use `Parser.Parse(path)`
- Python: Load functions named `parse_fods`, `parse_fodt`, `load_ods`, `load_odt`, `load`, `parse_pbm`
- .NET: Some products have `Load(Stream)`, most don't
- Python: Some return typed objects; some return raw dicts; some return lists
- See `public-api-review-plan.md` consistency tables for full comparison

### Q6: What is the class architecture quality?

See `architecture-review-matrix.json`. Key findings:
- FODS .NET: Partial class split (3 files) is manageable but hides responsibility
- NetPBM .NET: Best architecture — NetpbmImage split into 4 files with clear domain boundaries
- ZST .NET: Missing writer class entirely — architectural gap
- Python: `_shared/` dead abstraction exists but is used by no formats

### Q7: What is the feature availability by format type?

See `feature-availability-matrix.json`. Summary by domain:
- Spreadsheet: Read FA-4, Edit FA-4, Write FA-4, Multi-sheet FA-4 (FODS .NET)
- Spreadsheet Python: FA-3 average
- Document: Paragraphs FA-4, Headings FA-4, Export FA-4 (FODT .NET)
- Image: Pixel access FA-5, Transforms FA-4, Binary FA-4 (NetPBM .NET)
- Compression: Decompress FA-3, Compress FA-0 (.NET), FA-4 (Python)

### Q8: What is the feature complexity level?

See `feature-complexity-matrix.json`. Best: FODS .NET (C4), NetPBM .NET (C4).
Worst: ZST .NET (C1 — compress=C0), FODP Python (C1 — no write).

### Q9: What is the object model depth?

See `object-model-rubric.md`. Range: OM-1 (ZST .NET, FODP Python) to OM-4 (FODS .NET, NetPBM .NET).
Key gap: NDJSON .NET uses raw JsonElement (OM-2) — should be OM-3 with NdjsonRecord wrapper.

### Q10: What claim contradictions exist?

9 contradictions found. Most critical:
- CONTRADICTION-001: FODS .NET csproj says "Gate 11 approved" — source says NOT approved
- CONTRADICTION-002: ZST capability map may claim compress — source confirms NOT available
- CONTRADICTION-006: HTML/Markdown/TXT marketed as products — they are internal helpers
- CONTRADICTION-008: FODP "consumer_roundtrip.py" name implies write — FODP is read-only

See `product-claim-vs-reality-matrix.json` for full list.

### Q11: Are the test suites meaningful?

Partially. Key issues:
- FODS .NET, FODT .NET: 70%+ test files named by sprint (R87, R100) — hard to navigate
- PBM Python: TQ-4 (strongest — malformed security tests present)
- FODP Python: TQ-1 (smoke only)
- ZST .NET: No roundtrip tests (can't compress)
- See `test-meaningfulness-matrix.json` for full scores

### Q12: Are examples usable as reference?

Partially. All Python examples use dev-path imports (`from src.python.fods import ...`).
This means they cannot be run by a user who installed the package via pip.
No .NET examples exist at all. Only `docs/api/pbm.md`, `pgm.md`, `ppm.md` exist.

### Q13: Is packaging release-ready?

No. Critical gaps:
- Python: All 20 pyproject.toml missing authors, urls, keywords, classifiers, readme
- .NET: All 10 src/net/{format}/README.md missing (csproj references them)
- No CLI entry points for any Python package
- No type stubs for any Python package

### Q14: What is the end-user workflow quality?

EW-3 for most products (productive with docs) but limited by missing README and dev-path examples.
FODP Python and ZST .NET are EW-1 (workflow blocked by missing capability).

### Q15: Which products are closest to commercial release?

FODS .NET, FODT .NET, NetPBM .NET — all at POC_CANDIDATE (3.3–3.4/5).
With 4–6 weeks of fixes (QF-1 through QF-4), these could reach COMMERCIAL_CANDIDATE (4.0+).

### Q16: Which Python products are closest to FOSS release?

FODS Python, FODT Python — both PY-4. With P6/P7/P8 fixes (pyproject.toml, README, __all__),
these would be PY-5 (FOSS release).

### Q17: What is the recommended fix priority order?

1. P0 release blockers: QF-1 sprint (ZstWriter, Gate 11 fix, dual API, FODP stub)
2. P1 packaging: QF-2 sprint (pyproject.toml, README for all 30 products)
3. P1 API: QF-3 sprint (wildcard imports, stream loads, NdjsonRecord)
4. P2 examples: QF-4 sprint (installed-package imports, CLI entry points)
5. P3 deferred: QF-5 sprint (test renaming, type stubs, dead code)

### Q18: How long will fixes take?

QF-1: 1–2 days (4 targeted fixes)
QF-2: 3–5 days (30 README files + 20 pyproject.toml enrichments)
QF-3: 2–3 days (wildcard import cleanup + stream overloads + NdjsonRecord)
QF-4: 1–2 days (example updates + CLI entry points)
QF-5: 4–7 days (test renaming + type stubs — low urgency)

Total: ~2–3 weeks of focused fix sprints.

### Q19: Are there any architectural blockers to release?

Yes — ZST .NET is architecturally incomplete (no writer). This is a structural gap, not a
configuration issue. See `pilot-product-quality-fix-plan.md` for ZstWriter specification.

### Q20: Are HTML, Markdown, TXT real products?

No. They are internal writer helpers used by FODS and FODT exporters:
- `src/net/html/HtmlWriter.cs` — used by FodsHtmlExporter, FodtHtmlExporter
- `src/net/markdown/MarkdownWriter.cs` — used by FodtMarkdownExporter
- `src/net/txt/TxtWriter.cs` — used by FodtTxtExporter

They should be re-classified as internal helpers in the registry. Do not market as standalone products.

### Q21: What is the Gate 11 status for .NET products?

**NOT APPROVED.** Gate 11 requires Babar Raza's explicit sign-off. Current status per product:
- FODS .NET: commercial_readiness_in_progress (source header confirms NOT approved)
- csproj description claims approval — this is a contradiction (PQ-006, P0)
- No .NET product has Gate 11 approval
- After QF-1 through QF-4, FODS/FODT/NetPBM will be Gate 11 ELIGIBLE, not approved

### Q22: What is the Python FOSS gate status?

No Python product is at PY-5 (FOSS release). All fail on P6 (pyproject.toml), P7 (README),
P8 (explicit __all__). After QF-2 and QF-3, FODS/FODT Python would be PY-5.

### Q23: Are there security concerns in any product?

- FODS .NET: DTD injection guard present (confirmed by source)
- NetPBM Python: Security bounds on oversized input (confirmed — malformed security tests)
- NDJSON .NET: JsonElement is framework-safe (no arbitrary code execution risk)
- ZST: No compress = no zlib bomb risk for writer; decompression memory limits not confirmed
- FODG/FODP: Dict-based parsers may not validate input bounds

No critical security vulnerabilities confirmed. Recommend explicit security audit before commercial release.

### Q24: What evidence exists that products work as claimed?

- FODS .NET: 638 tests pass (load/edit/save/export all confirmed)
- FODT .NET: ~450 tests pass (load/edit/export confirmed)
- NetPBM .NET: ~496 tests pass (transforms, filters, binary formats confirmed)
- Python FOSS: consumer_roundtrip.py examples confirmed PASS for 14+ formats
- ZST .NET: No roundtrip evidence (no compress capability)

### Q25: What is the overall product quality verdict?

**PRODUCT_QUALITY_VERDICT: POC_CANDIDATE_WITH_GAPS**

Format Factory is a serious engineering effort with substantial depth in FODS, FODT, NetPBM,
and 14+ Python FOSS formats. The products are not vaporware — they work. However:

1. Critical packaging gaps (P6, P7, P8) prevent PyPI/NuGet publication today
2. ZST .NET is functionally incomplete (no write capability) — P0
3. Claim contradictions (Gate 11) must be resolved before any commercial announcement
4. Dual API confusion (FODS Python) undermines developer trust
5. No product has documentation or examples at professional quality

With the 5 QF fix sprints (~3 weeks), Format Factory would have:
- 3 commercial-ready .NET products (FODS, FODT, NetPBM)
- 2 FOSS-release Python products (FODS, FODT)
- 14 production-usable Python packages
- A credible launch story

---

## Master Plan Files Index

| File | Purpose |
|------|---------|
| `src-product-inventory.json` | Full product inventory with maturity |
| `product-format-matrix.json` | 30-product capability matrix |
| `product-source-map.md` | File-by-file source role map |
| `public-api-review-plan.md` | API review methodology |
| `public-api-matrix.json` | API quality scores |
| `api-quality-rubric.md` | API scoring rubric |
| `class-segregation-review-plan.md` | Architecture review method |
| `architecture-review-matrix.json` | Architecture scores |
| `component-boundary-map.json` | Component boundary details |
| `feature-availability-review-plan.md` | Feature availability method |
| `feature-availability-matrix.json` | FA-0–FA-5 per feature |
| `feature-comprehensiveness-rubric.md` | Domain coverage scoring |
| `feature-complexity-review-plan.md` | Complexity review method |
| `feature-complexity-matrix.json` | C0–C5 complexity scores |
| `dotnet-product-quality-review-plan.md` | .NET review method |
| `dotnet-product-quality-matrix.json` | .NET commercial scores |
| `dotnet-commercial-readiness-rubric.md` | .NET readiness rubric |
| `python-product-quality-review-plan.md` | Python review method |
| `python-product-quality-matrix.json` | Python FOSS scores |
| `python-foss-readiness-rubric.md` | Python readiness rubric |
| `test-quality-review-plan.md` | Test quality method |
| `test-meaningfulness-matrix.json` | TQ-0–TQ-5 scores |
| `end-user-workflow-review-plan.md` | Workflow review method |
| `examples-docs-package-matrix.json` | Examples/docs/packaging status |
| `product-claim-vs-reality-plan.md` | Claim verification method |
| `product-claim-vs-reality-matrix.json` | 9 contradictions classified |
| `product-quality-problem-matrix-template.md` | 30 problems documented |
| `product-quality-problem-schema.json` | 20 problems with full metadata |
| `product-quality-confirmation-process.md` | Confirmation workflow |
| `review-execution-phases.md` | Phase A–F definitions |
| `dry-run-plan.md` | Phase C validation |
| `live-readonly-run-plan.md` | Phase D execution |
| `pilot-product-quality-fix-plan.md` | Phase E pilot (ZstWriter) |
| `unified-product-quality-fix-plan.md` | Phase F all-product fixes |
| `code-quality-rubric.md` | Code quality scoring |
| `feature-quality-rubric.md` | Feature quality scoring |
| `feature-complexity-rubric.md` | Complexity scoring |
| `class-segregation-rubric.md` | Architecture scoring |
| `object-model-rubric.md` | Domain model scoring |
| `commercial-readiness-rubric.md` | .NET commercial rubric |
| `foss-readiness-rubric.md` | Python FOSS rubric |
| `test-meaningfulness-rubric.md` | Test quality rubric |
| `end-user-workflow-rubric.md` | Workflow quality rubric |
| `initial-product-quality-risk-register.md` | Risk register |
| `recommended-product-quality-review-sequence.md` | Review sequence |
| `final-plan-mode-summary.md` | Sprint summary |
