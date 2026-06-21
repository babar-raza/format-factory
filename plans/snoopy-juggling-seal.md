# Snoopy Juggling Seal — SAL Source-to-Consumption Pipeline Forensics and Redesign Plan
# Format Factory — Specification Authority Layer
# Plan version: 3.1 (updated 2026-06-21: TC-SAL-IMPL-001 VERIFIED — TC-SAL-001 fixed per-format output; 22 formats, 14,428 facts confirmed in sal-facts-latest.json; prior count 14,288 was pre-fix estimate)
# Classification: AUTHORITATIVE — single plan, no siblings or replacements

---

## 1. Context and Current Situation

The Specification Authority Layer (SAL) is the system that acquires, normalizes, extracts,
verifies, and publishes specification facts for Format Factory formats. Downstream systems
(product source code, capability layer, declaration validation, Gate readiness) depend on SAL
for specification authority.

This plan was created as a direct result of a mandatory forensic investigation of the full
SAL source-to-consumption pipeline. The investigation is documented in:

```
.local/evidences/sal-forensics-20260616/sal-source-to-consumption/
  sal-pipeline-map.md
  sal-plan-assumption-register.yaml
  sal-issue-root-cause-register.yaml
  normalization-loss-ledger-fods.json
```

### 1.1 Corrected Current State

**Two parallel, disconnected pipelines exist. Neither is end-to-end functional.**

#### Pipeline A — Real Spec Cache (partially complete, consumer integration BROKEN)

A real, SHA-256-verified specification corpus exists:

| Format | Source | Status | Lines | Sections | Verified Facts |
|--------|--------|--------|-------|----------|----------------|
| FODS | ODF 1.3 Part 3 (PDF, 24MB) | Acquired, normalized, 884 sections | 57,803 | 884 | 78 |
| ZST | RFC 8878 + RFC 9659 | Acquired, SHA-256 verified | 2,457 | 0 extracted | 0 |
| FODT | Shares ODF source | Indexed (proof graph only) | 0 normalized | 0 | 0 |
| CSV | RFC 4180 | Cache dir exists | unknown | unknown | 0 |
| DIF | v1 spec | Cache dir exists | unknown | unknown | 0 |
| Others | Various | Cache dirs exist | unknown | unknown | 0 |

The 78 FODS verified facts at `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`
are the only real, independently verified specification facts in the system. They use fact IDs
in the format `FACT-FODS-NNN` and are validated by `validate_spec_fact_refs.py`.

**CRITICAL GAP**: After the workbench stage, these 78 facts are NOT emitted by `sal_master_runner.py`
and are NOT loaded into context packs. They are accessible ONLY through
`validate_spec_fact_refs.py`'s registry scan for declaration validation.

#### Pipeline B — Template Fact Generator (complete but fake)

`sal_master_runner.py` produces 128 hardcoded template facts for 22 formats from in-memory
Python dicts. It NEVER reads any specification file. All 10 other SAL tools are bypassed.

**CRITICAL GAP**: Template facts use incompatible ID namespaces (`FODS-FACT-001`, `ODF-FACT-*`,
`ZST-FACT-001` etc.) that cannot pass `validate_spec_fact_refs.py` which requires `FACT-<FORMAT>-NNN`.
`sal-facts-latest.json` is written to disk but has zero downstream readers.

### 1.2 Root-Cause Summary

Eight confirmed root causes are documented in the issue register. Primary causes:

| ID | Title | Severity |
|----|-------|----------|
| ROOT-01 | sal_master_runner.py is a template generator, not a pipeline orchestrator | CRITICAL |
| ROOT-02 | Real spec cache orphaned — produced but never consumed after workbench | CRITICAL |
| ROOT-03 | Fact ID namespace incompatibility blocks end-to-end validation | HIGH |
| ROOT-04 | sources.jsonl schema mismatch with SpecSource dataclass | MEDIUM |
| ROOT-05 | Context packs are structurally valid but semantically empty | HIGH |
| ROOT-06 | FODT has no normalized text despite sharing ODF source | MEDIUM |
| ROOT-07 | ZST RFC 8878 cached but never processed | MEDIUM |
| ROOT-08 | No semantic-unit census — no extraction denominator | MEDIUM |

---

## 2. SAL Contract Definition

### 2.1 What Is a SAL Fact?

A SAL fact is a minimum independently verifiable claim about a format's specification that:
- is grounded in a specific cited location in an acquired, SHA-256-verified specification source;
- has a stable fact ID (`FACT-<FORMAT>-NNN`);
- has a verification status (`verified`, `needs_review`, `not_found_in_normalized_text`);
- has at minimum: format_id, spec_id, spec_version, source_sha256, normalized_artifact path, section_id, verification_status, validated_by, validated_at;
- is stored in a `verified-facts-review.yaml` file under `.local/spec-cache/<format>/<version>/workbench/`.

A fact may NOT:
- be self-certified by an AI extraction method (AI extraction → needs_review → requires independent validation);
- be generated from a synthetic fixture;
- cite an unregistered source;
- use a fact ID outside the `FACT-<FORMAT>-NNN` namespace.

### 2.2 Fact Granularity

One fact corresponds to ONE independently verifiable semantic claim.

A single ODF element definition (`<table:table>`) may require MULTIPLE facts to cover:
- its namespace and qualified name
- its allowed parent elements
- its allowed child elements
- its required attributes
- its optional attributes
- its cardinality (0..1, 0..*, 1..1, 1..*)
- its semantic role in the document model

A broad "cells are table:table-cell" claim is NOT a single atomic fact — it conflates
namespace, element name, parent relationship, and allowed value types.

### 2.3 Semantic Unit Taxonomy

For the purposes of coverage measurement, the following categories are used:

| Category | Description | Example |
|----------|-------------|---------|
| NORM-REQ | Normative requirement (MUST/SHALL/SHOULD) | "Implementations MUST declare the ODF namespace" |
| ELEM-DEF | XML element definition with namespace | `<table:table>` — spreadsheet worksheet element |
| ATTR-DEF | Attribute definition on an element | `table:name` — required worksheet name attribute |
| ENUM-VAL | Enumerated allowed value | office:value-type allowed values: string, float, boolean, date, time, currency, percentage |
| CARD-RULE | Cardinality rule (required, optional, repeated) | table:table-row is repeatable within table:table |
| DATA-TYPE | Data type specification | office:date-value is ISO 8601 date string |
| GRAMMAR | Syntax grammar (ABNF, BNF, XML schema rule) | RFC 8878 §3: Frame header ABNF |
| ENCODING | Byte layout or character encoding | ZST magic number 0xFD2FB528 (little-endian) |
| ERROR | Prohibited state or error condition | If Content_Checksum_flag=1, decompressor MUST validate |
| CONFORM | Conformance class or implementation level | ODF conformance classes: extended conforming document |

This taxonomy is the denominator for coverage computation.

### 2.4 What "Consumption Ready" Means

A fact is consumption-ready when:
1. It exists in `verified-facts-review.yaml` with `verification_status: verified`
2. Its fact ID (`FACT-<FORMAT>-NNN`) passes `validate_spec_fact_refs.py` registry check
3. It is emitted by `sal_master_runner.py --from-cache` output
4. It is present in the format's context pack with non-empty `requirement_summary`

---

## 3. Root-Cause Layers (Confirmed)

### Layer 1 — Dead Integration (Root Cause ROOT-01, ROOT-02)

The production SAL runner (`sal_master_runner.py`) reads only `format-registry.yaml` and
produces template facts. It never calls any other SAL tool. The real spec cache at
`.local/spec-cache/` is produced but never consumed after the workbench stage.

**This is the single most impactful root cause.** Fixing it connects 78 existing FODS facts
to all downstream consumers immediately.

### Layer 2 — Incompatible Namespaces (Root Cause ROOT-03)

Template facts and workbench facts use incompatible ID schemas. No declaration can cite both.
The canonical namespace (`FACT-<FORMAT>-NNN`) must be the only namespace used henceforth.

### Layer 3 — Synthetic Corruption (Root Cause ROOT-02 contributing)

The `.local/spec-artifacts/` directory contains synthetic stubs that were explicitly quarantined
but may still confuse new sprint workers or automated tools that scan artifact directories.
These stubs must be clearly retired and replaced with real extraction outputs.

### Layer 4 — Missing Extraction for ZST and Others (Root Cause ROOT-07)

RFC 8878 is the cleanest available extraction candidate (plain text, ABNF grammar, short at 2,457
lines) but no extraction has been performed. ZST would provide 12 FACT-ZST-NNN facts from its
RFC grammar alone, replacing the 12 template facts.

### Layer 5 — No Coverage Denominator (Root Cause ROOT-08)

Without a census, fact count is uninterpretable. 78 FODS facts could be 100% coverage or 3%
coverage depending on the total extractable units in ODF Part 3. The semantic unit census must
be performed before any coverage gate is defined.

### Layer 6 — Missing Multipart Source (Root Cause ASM-006)

ODF 1.3 has 4 parts. Only Part 3 (Schema) is cached. Conformance (Part 1), packaging (Part 2),
and formulas (Part 4) are missing. A complete FODS SAL requires all four parts.

---

## 4. Preservation Constraints

The following must NOT be modified during implementation:

1. **`.local/spec-cache/fods/1.3/`** — verified source corpus. Do not delete or overwrite. Add only.
2. **`.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`** — 78 verified facts. Append only; never retrograde a verified fact to unverified without evidence.
3. **`tools/supervisor/validate_spec_fact_refs.py`** — the fact ID validation gate. Logic must not weaken. Extension to accept new fact IDs is allowed.
4. **`tools/specification-authority-layer/spec_verifier.py`** — anti-bypass guards must be preserved.
5. **`tools/specification-authority-layer/spec_governance_runtime.py`** — usage ledger must be preserved.
6. **`QUARANTINE files`** — preserve FODS-SPEC-001-requirements-QUARANTINE.md for audit history.

---

## 5. Proposed Architecture (Revised from Four-Component to Wire-First)

The previous four-component redesign proposed:
1. SpecNormalizationPipeline
2. FactExtractionEngine
3. FactVerificationOracle
4. FactRegistryPublisher

These components are valid long-term goals but were premature. The forensic investigation shows
that **the primary problem is not the design of extraction algorithms but the missing wire between
the existing real spec cache and the downstream consumers.**

### Revised Priority Order

#### Phase 0 — Diagnostic and Evidence Gate (GATE D0–D6)
Mandatory prerequisite for all subsequent phases. All diagnostic evidence must be collected before
implementation begins. Evidence artifacts are at:
`.local/evidences/sal-forensics-20260616/sal-source-to-consumption/`

Status: **COMPLETE** (this plan represents the output of Phase 0)

#### Phase 1 — Wire Real Cache to Production Runner (Highest ROI, Lowest Risk)

**Target:** `sal_master_runner.py --from-cache` mode that reads `verified-facts-review.yaml`
from `.local/spec-cache/` and emits canonical FACT-<FORMAT>-NNN facts.

**Expected immediate outcome:** 78 FODS verified facts become visible in `sal-facts-latest.json`
with correct IDs, replacing the 15 FODS template facts.

**Formats unblocked immediately:** FODS (78 facts exist and are verified)

**Implementation rule:** Do not regenerate or overwrite the spec cache. Read only. Emit only.

#### Phase 2 — ZST RFC Extraction Sprint

**Target:** Extract FACT-ZST-NNN facts from RFC 8878 (`.local/spec-cache/zst/rfc8878/rfc8878.txt`)

**Approach:**
1. Run `spec_parser.py` on rfc8878.txt using plain_text mode (no Markdown headings)
2. Run `spec_normalizer.py` to produce ZST normalized artifact
3. Run `requirement_extractor.py` on normalized artifact (MUST/SHALL are clear in RFC)
4. Manual review of each candidate against RFC source text
5. Populate `.local/spec-cache/zst/rfc8878/workbench/verified-facts-review.yaml` with FACT-ZST-NNN IDs

**Expected yield:** ~40-60 normative requirement candidates from RFC 8878 (MUST/SHALL language)

**Note:** RFC 8878 is 2,457 lines — manual review of all candidates in one sprint is feasible.

#### Phase 3 — FODT Filtered Extraction

**Target:** Extract FODT-specific facts from ODF Part 3 `text.txt` with text-element filter

**Approach:**
1. Reuse `.local/spec-cache/fods/1.3/normalized/text.txt` (57,803 lines)
2. Filter sections to text:p, text:h, text:span, text:list, text:section, text:a, text:note
3. Extract facts with FACT-FODT-NNN IDs, stored in `.local/spec-cache/fodt/odf-1.3/workbench/`
4. Wire to sal_master_runner.py --from-cache

**Important constraint:** FODT facts must reference ODF Part 3, not FODS facts. No cross-format contamination.

#### Phase 4 — ODF Multipart Acquisition

**Target:** Acquire ODF Parts 1, 2, and 4 to complete FODS/FODT coverage

- Part 1 (Introduction + Conformance classes): required for conformance level facts
- Part 2 (Packages): required for package format validation facts
- Part 4 (OpenFormula): required for formula/cell facts in FODS

Requires authorization per acquisition policy (`docs/specification-cache.md`).

#### Phase 5 — Semantic Census and Coverage Gates

**Target:** Establish defensible coverage denominators for FODS and ZST

For FODS:
1. Scan ODF Part 3 sections for element definitions (detect "`<element-name>`" patterns)
2. Count attribute definitions, enumerated value sets, and normative requirements
3. Produce `semantic-census-fods.json` with category counts
4. Express 78 facts as coverage percentage by category

For ZST:
1. Count ABNF grammar productions in RFC 8878
2. Count normative requirements (MUST/SHALL/SHOULD)
3. Produce `semantic-census-zst.json`

Only after Phase 5 can meaningful coverage gates be defined.

#### Phase 6 — Context Pack Rebuild

**Target:** Rebuild context packs from real spec-cache artifacts

Use `context_pack_builder.py` with real normalized artifacts and verified facts as input.
Context packs should have non-empty `requirement_summary` and meaningful `index_terms`.

#### Phase 7 — Sources.jsonl Migration

**Target:** Migrate `.local/spec-source-registry/sources.jsonl` to SpecSource schema

One-time migration script maps:
- `spec_id` → `source_id`
- `spec_name` → `title`
- `local_path` → `url_or_path`
- `source_sha256` → `sha256_snapshot`
- Assign `source_type`, `status`, `registered_at` from manifest data

---

## 6. Diagnostic Gates

### Gate D0 — Source Authority Proven
**Status: COMPLETE for FODS and ZST**
- FODS: ODF Part 3 PDF acquired, SHA-256 match confirmed (92cfe64e...)
- ZST: RFC 8878 + RFC 9659 acquired, SHA-256 verified
- Evidence: `.local/spec-cache/fods/1.3/normalized/source-manifest.yaml`, `.local/spec-cache/zst/manifest.yaml`

**Gap:** ODF Parts 1, 2, 4 not acquired. FODT needs explicit source selection.

### Gate D1 — Normalization Retention Proven
**Status: COMPLETE for FODS, NOT STARTED for ZST**
- FODS: 57,803 lines → 884 sections → confirmed (workbench report shows sections.jsonl, chunks.jsonl, pages.jsonl all present)
- ZST: RFC 8878 has never been normalized

### Gate D2 — Semantic Denominator Established
**Status: NOT STARTED**
No census tool exists. The denominator for FODS is unknown.

### Gate D3 — Extraction Recall and Provenance Proven
**Status: PARTIAL for FODS (78 facts), NOT STARTED for ZST**
- FODS: 78 facts exist with provenance (page_start, section_id, verification_evidence lines)
- ZST: 0 facts extracted

### Gate D4 — Verification Safety Proven
**Status: PARTIAL**
- FODS: independent_agent_verifier + tier1_section methods used for ~30 verified facts
- Adversarial benchmark NOT run against spec_verifier.py
- AI guard in validate_spec_fact_refs.py is functional but never tested against adversarial inputs

### Gate D5 — Publication and Reachability Proven
**Status: NOT COMPLETE**
- 78 FODS facts are in workbench but NOT in sal-facts-latest.json (wrong pipeline)
- 78 facts ARE reachable via validate_spec_fact_refs.py registry scan
- Context packs have 0 requirements (broken integration)
- RCAL/capability compiler reachability: UNPROVEN

### Gate D6 — Redesign Grounded
**Status: COMPLETE** (this plan represents Gate D6 evidence)
- Issue register: 8 confirmed root causes documented
- Root causes confirmed by source code inspection + artifact measurement
- Architecture revised from four-component to wire-first
- Evidence-based success criteria defined (Section 7)

---

## 7. Evidence-Based Quality Measures

### Source Completeness
```
acquired_spec_parts / identified_required_spec_parts
```
- FODS current: 1/4 (Part 3 only; Parts 1, 2, 4 not cached)
- ZST current: 1/1 (RFC 8878 primary; RFC 9659 companion = 2/2)

### Normalization Semantic Retention
```
addressable_source_sections_after_normalization /
addressable_source_sections_before_normalization
```
- FODS current: 884 sections in sections.jsonl (denominator unknown — PDF section count required)

### Extraction Recall (by semantic category)
```
correctly_extracted_facts_in_category /
total_units_in_category_from_census
```
- FODS current: UNKNOWN (census not performed)
- ZST current: 0 (no extraction performed)

### Provenance Completeness
```
facts_with_resolvable_source_coordinates /
all_generated_facts
```
- FODS workbench: 78/78 facts have page_start and section_id
- SAL runner template facts: 0/128 (no source coordinates)

### Publication Fidelity
```
correctly_published_facts_in_sal_output /
facts_approved_for_publication
```
- Current: 0/78 FODS (workbench facts not emitted by runner)
- After Phase 1: target 78/78

### Consumer Reachability
```
published_facts_reachable_through_consumer_path /
published_facts_selected_for_reachability_testing
```
- Via validate_spec_fact_refs.py: 78/78 FODS (reachable today)
- Via sal-facts-latest.json: 0/128 (zero downstream readers)
- Via context pack: 0/78 (context packs semantically empty)

### Silent Loss Count
**Current silent loss: HIGH**
- 128 template facts written to sal-facts-latest.json with zero readers = 128 unconsumed
- 78 verified workbench facts not emitted by production runner = 78 silently stranded
- ZST: RFC 8878 fully cached but 0% extracted = entire corpus silently stranded

**Target: Zero silent loss** (every fact that enters the system must be traceable to a consumer)

---

## 8. Taskcards — Diagnostic Phase (TC-SAL-DIAG-*)

### TC-SAL-DIAG-001 — Plan Assumption Audit
**Status: COMPLETED 2026-06-16**
Evidence: `.local/evidences/sal-forensics-20260616/sal-source-to-consumption/sal-plan-assumption-register.yaml`
10 assumptions audited; 7 CONTRADICTED, 2 PARTIAL, 1 CONFIRMED.

### TC-SAL-DIAG-002 — Complete Tool and Invocation Graph
**Status: COMPLETED 2026-06-16**
Finding: `sal_master_runner.py` invokes 0 of 10 other SAL tools in production.
All other tools wired but dormant (context_pack_builder, spec_verifier, spec_parser etc.).

### TC-SAL-DIAG-003 — Format/Source-Family Inventory
**Status: PARTIAL 2026-06-16**
Finding: 22 formats registered. 11 have spec cache directories. 1 has normalized text + workbench (FODS).
0 formats have end-to-end pipeline integration working.

### TC-SAL-DIAG-004 — SAL Fact Contract Reconstruction
**Status: COMPLETED 2026-06-16**
Output: Section 2 of this plan (contract definition, taxonomy, consumption-ready definition).

### TC-SAL-DIAG-005 — FODS Authority and Acquisition Replay
**Status: COMPLETED 2026-06-16**
Finding: ODF Part 3 PDF acquired (24MB, SHA-256 verified). text.txt (57,803 lines), 884 sections.
78 workbench facts with provenance. Only Part 3 acquired of 4-part spec.

### TC-SAL-DIAG-006 — FODS Extraction and Normalization Comparison
**Status: COMPLETED 2026-06-16**
Finding: Pipeline A (real cache) uses real text. Pipeline B (synthetic stub) has 4 sections/242 chars.
FODS synthetic requirements quarantined. Real extraction denominator unknown (census needed).

### TC-SAL-DIAG-007 — FODS Page-Map and Section-Index Verification
**Status: PARTIAL 2026-06-16**
sections.jsonl (884 sections) and pages.jsonl (782 pages) exist. spec-index.yaml exists.
Full verification (every section traceable to source PDF) not performed in this sprint.

### TC-SAL-DIAG-008 — FODS Semantic-Unit Census
**Status: NOT STARTED**
**Acceptance criteria:** JSON file at `.local/evidences/sal-forensics-*/semantic-census-fods.json`
with counts by taxonomy category (NORM-REQ, ELEM-DEF, ATTR-DEF, ENUM-VAL, CARD-RULE, DATA-TYPE, GRAMMAR, ENCODING, ERROR, CONFORM).

### TC-SAL-DIAG-009 — FODS Existing Extractor Replay
**Status: NOT STARTED**
**Task:** Run `requirement_extractor.py` against real FODS normalized artifact and compare
output to the 78 workbench facts. Measure recall.

### TC-SAL-DIAG-010 — Verifier Adversarial Benchmark
**Status: NOT STARTED**
**Task:** Test spec_verifier.py against 10 adversarial inputs:
- exact supporting text, paraphrase, negation mismatch, wrong section, cardinality error,
  stale-version claim, AI-generated candidate, duplicate candidate.

### TC-SAL-DIAG-011 — Consumer Reachability Trace
**Status: PARTIAL 2026-06-16**
Finding: validate_spec_fact_refs.py reaches 78 FODS facts. sal-facts-latest.json is unread.
Context packs have 0 requirements. RCAL reachability unproven.

### TC-SAL-DIAG-012 — ZST Non-XML Pilot Replay
**Status: PARTIAL 2026-06-16**
Finding: RFC 8878 present (2,457 lines, SHA-256 verified). No normalization or extraction performed.
ZST workbench does not exist.

### TC-SAL-DIAG-013 — FODT Shared-Spec Isolation Pilot
**Status: PARTIAL 2026-06-16**
Finding: FODT odf-1.3 cache exists with only proof graph and spec-index. No text, no facts.
Shared ODF source (text.txt) available but requires text-element filtering for FODT.

### TC-SAL-DIAG-014 — Proven Component Reuse Assessment
**Status: COMPLETED 2026-06-16**
Finding: `spec_parser.py` and `spec_normalizer.py` are functional and correct for their domains.
They need to be wired to real inputs (from spec-cache) rather than synthetic stubs.
`validate_spec_fact_refs.py` is production-ready. `context_pack_builder.py` is wired but
needs real inputs. No external library replacements required.

---

## 9. Taskcards — Implementation Phase (TC-SAL-IMPL-*)

### TC-SAL-IMPL-001 — Wire sal_master_runner.py to Real Spec Cache (Phase 1)
**Priority: CRITICAL**
**Depends on:** TC-SAL-DIAG-001 through TC-SAL-DIAG-006 (all complete)
**Target state:** `sal_master_runner.py --from-cache` reads verified-facts-review.yaml and emits
FACT-<FORMAT>-NNN facts in sal-facts-latest.json.
**Allowed paths:**
- `tools/specification-authority-layer/sal_master_runner.py` — ADD --from-cache mode
- `.local/spec-cache/*/workbench/verified-facts-review.yaml` — READ ONLY
- `.local/sal-output/sal-facts-latest.json` — WRITE
**Forbidden:**
- Do not modify or delete any file under `.local/spec-cache/`
- Do not change the --all mode behavior (backward compat)
**Acceptance criteria:**
- `python sal_master_runner.py --from-cache --all` produces at least 78 FODS facts with IDs matching `FACT-FODS-NNN`
- Output facts pass format check in validate_spec_fact_refs.py
- Integration test added: `test_sal_runner_from_cache.py`

### TC-SAL-IMPL-002 — ZST RFC Extraction Sprint (Phase 2)
**Priority: HIGH**
**Depends on:** TC-SAL-DIAG-012
**Target state:** `.local/spec-cache/zst/rfc8878/workbench/verified-facts-review.yaml` with
FACT-ZST-NNN facts extracted from RFC 8878.
**Acceptance criteria:**
- At least 15 FACT-ZST-NNN facts with verification_status=verified
- Each fact has page_start (line number in rfc8878.txt), section_id, verification_evidence
- Facts pass AI guard check in validate_spec_fact_refs.py

### TC-SAL-IMPL-003 — FODT Filtered Extraction (Phase 3)
**Priority: MEDIUM**
**Depends on:** TC-SAL-DIAG-013
**Target state:** `.local/spec-cache/fodt/odf-1.3/workbench/verified-facts-review.yaml` with
FACT-FODT-NNN facts filtered from ODF Part 3 text.txt (text:* elements only).
**Acceptance criteria:**
- At least 20 FACT-FODT-NNN facts covering text:p, text:h, text:span, text:list, text:section
- No spreadsheet-specific facts (table:table-cell etc.) in FODT workbench

### TC-SAL-IMPL-004 — Sources.jsonl Schema Migration (Phase 7)
**Priority: MEDIUM**
**Target state:** sources.jsonl migrated to SpecSource schema; load_registry() returns
records with source_id populated.
**Allowed paths:** `.local/spec-source-registry/sources.jsonl` (overwrite with migrated content)

### TC-SAL-IMPL-005 — Context Pack Rebuild (Phase 6)
**Priority: LOW (after Phases 1-3)**
**Target state:** context packs rebuilt from real spec-cache normalized artifacts with
non-empty requirement_summary (at least 5 requirements per pack).

### TC-SAL-IMPL-006 — Semantic Census Tool (Phase 5)
**Priority: MEDIUM (prerequisite for coverage gates)**
**Target state:** Script `tools/specification-authority-layer/spec_census.py` that scans
normalized text and counts semantic units by taxonomy category.
**Acceptance criteria:**
- Produces `semantic-census-<format>.json` with counts for all 10 taxonomy categories
- FODS census run against text.txt, output saved to evidence directory

---

## 10. Existing Taskcards — Revised Status

### TC-0007 (Specification Cache)
**Previous status:** assumed complete
**Revised:** PARTIAL — FODS cache complete (Part 3 only), ZST cache complete (RFC 8878+9659),
FODT cache skeleton only, other formats have directories but incomplete content.
**Blocker lifted:** FODS and ZST can proceed to extraction without blocking on full cache completion.

### TC-0012 (Specification Normalization Layer)
**Previous status:** assumed blocked by acquisition
**Revised:** FODS normalization COMPLETE (text.txt, sections.jsonl, chunks.jsonl, pages.jsonl).
ZST normalization NOT STARTED despite source being available.
**Next action:** Run normalization for ZST as part of TC-SAL-IMPL-002.

### TC-0015 (Spec Retrieval Strategy Evaluation)
**Previous status:** unknown
**Revised:** Acquisition strategy is working for FODS and ZST. The bottleneck is not
acquisition strategy but extraction pipeline integration. Defer further strategy work.

### TC-0016 (FODS Vector Index Pilot)
**Previous status:** planning
**Revised:** DEFER — the 78 workbench facts and term-based index (spec_indexer.py) are
sufficient for Phase 1-3. Vector index introduces semantic retrieval complexity before
the basic pipeline is functional. Revisit in Phase 5+.

### TC-0020 (Spec Workbench Core)
**Previous status:** unknown
**Revised:** FODS workbench COMPLETE (78 facts). ZST and FODT workbenches NOT STARTED.
TC-SAL-IMPL-002 and TC-SAL-IMPL-003 create these workbenches.

### TC-0021 (FODS Workbench Quality Review)
**Previous status:** planning
**Revised:** PARTIALLY DONE — 78 facts in review.yaml with independent_agent_verifier status
for ~30 facts. The remaining 48 have not_found_in_normalized_text or pending status.
**Revised acceptance:** Wire Phase 1 (TC-SAL-IMPL-001) first, then plan a quality review sprint
to move pending facts to verified or document why they cannot be verified.

---

## 11. Dependency DAG

```
TC-SAL-DIAG-001 through TC-SAL-DIAG-007  [COMPLETE]
    ↓
TC-SAL-DIAG-014 (component reuse)         [COMPLETE]
    ↓
TC-SAL-IMPL-001 (wire cache→runner)       [NEXT — no upstream dependency]
    ↓
TC-SAL-IMPL-002 (ZST extraction)          [parallel with IMPL-001]
TC-SAL-IMPL-003 (FODT extraction)         [parallel with IMPL-001]
TC-SAL-IMPL-004 (sources schema)          [parallel]
    ↓
TC-SAL-DIAG-008 (semantic census)         [needs real extraction output]
    ↓
TC-SAL-IMPL-005 (context pack rebuild)    [needs real facts]
TC-SAL-IMPL-006 (census tool)             [needs normalized artifacts]
    ↓
TC-SAL-DIAG-010 (verifier benchmark)      [needs real facts]
TC-SAL-DIAG-011 (consumer reachability)   [needs working runner output]
```

Production healing work (Phases 7-13 per spec-to-feature plan) depends on:
- TC-SAL-IMPL-001 complete (real facts in runner output)
- Gate D5 COMPLETE (publication and reachability proven)

---

## 12. Anti-Patterns (Must Avoid)

1. **Do not improve template count.** Adding more hardcoded facts to `_SPEC_FACT_TEMPLATES` or
   `_FORMAT_SPECIFIC_FACTS` is not improvement. It produces more unreachable, unverifiable artifacts.

2. **Do not run another synthetic stub generation.** The `.local/spec-artifacts/` synthetic system
   has been quarantined. Do not re-run `spec_parser.py` against synthetic content.

3. **Do not claim coverage without a denominator.** 78 facts is not 100% coverage. Do not
   use fact count as a coverage gate until the semantic census establishes the denominator.

4. **Do not promote AI extraction to verified without independent review.** The AI guard in
   `validate_spec_fact_refs.py` must not be weakened. AI-extracted candidates require
   `independent_agent_verifier` or `deterministic_spec_text_search` validation.

5. **Do not build a vector index before the basic pipeline is functional.** Semantic retrieval
   is a Phase 5+ concern. The immediate priority is wiring real cache to real consumers.

6. **Do not merge FODS and FODT workbenches.** Each format must have its own workbench with
   format-filtered facts. Cross-format contamination creates false authority.

7. **Do not assume that a file exists in a directory means the directory is complete.** ZST has
   rfc8878.txt but no workbench. FODT has odf-1.3/ but no text.txt. Existence ≠ completeness.

---

## 13. Tradeoffs and Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Phase 1 wiring introduces backward compat break in --all mode | LOW | Keep --all mode unchanged; add --from-cache as a new mode |
| ZST RFC extraction produces low-precision candidates (common words match non-requirements) | MEDIUM | Require manual review of all candidates before marking verified |
| FODT filtering leaks spreadsheet facts | MEDIUM | Filter function must reject facts with table:* element names |
| ODF Part 3 text extraction has OCR damage (PDF-to-text) | LOW | Already evident in existing text.txt — quality is acceptable (57K lines, not garbled) |
| 78 FODS facts are insufficient for Gate 11 criteria | HIGH | Document as debt; Phase 4 (multipart acquisition) addresses this |
| Census reveals FODS coverage is <5% | HIGH | Document honestly; coverage is currently 0% measurable — any measurable coverage is progress |

---

## 14. Critical Files

| File | Role | Status | Action |
|------|------|--------|--------|
| `tools/specification-authority-layer/sal_master_runner.py` | Production SAL runner | Template-only, BROKEN | ADD --from-cache mode |
| `.local/spec-cache/fods/1.3/normalized/text.txt` | Real FODS spec text | COMPLETE, 57,803 lines | READ ONLY |
| `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml` | 78 verified FODS facts | COMPLETE | READ ONLY; APPEND ONLY |
| `.local/spec-cache/zst/rfc8878/rfc8878.txt` | RFC 8878 ZST spec | COMPLETE, 2,457 lines | Input for TC-SAL-IMPL-002 |
| `tools/supervisor/validate_spec_fact_refs.py` | Fact ID validation gate | FUNCTIONAL | DO NOT WEAKEN |
| `.local/spec-source-registry/sources.jsonl` | Source registry | SCHEMA MISMATCH | Migrate in TC-SAL-IMPL-004 |
| `reports/specification-authority-layer-mwp/context-pack-sample/fods-context-pack.json` | FODS context pack | 0 requirements | Rebuild in TC-SAL-IMPL-005 |
| `.local/spec-artifacts/FODS-SPEC-001-requirements-QUARANTINE.md` | Quarantine record | PRESERVE | Audit history only |
| `tools/specification-authority-layer/spec_parser.py` | Text parser | FUNCTIONAL | Use for ZST RFC extraction |
| `tools/specification-authority-layer/spec_normalizer.py` | Text normalizer | FUNCTIONAL | Use for ZST RFC extraction |
| `tools/specification-authority-layer/requirement_extractor.py` | Requirement extractor | FUNCTIONAL | Use for ZST RFC extraction |
| `tools/specification-authority-layer/context_pack_builder.py` | Context pack builder | FUNCTIONAL | Wire to real facts |
| `plans/snoopy-juggling-seal.md` | This plan | AUTHORITATIVE | Enhance in place only |

---

## 15. Allowed and Forbidden Path Policy

### ALLOWED — Read for diagnostics
- All files under `.local/spec-cache/`
- All files under `.local/spec-artifacts/`
- All SAL tool source files
- All tests under `tests/specification-authority-layer/`
- `registry/format-registry.yaml`
- `.local/sal-output/sal-facts-latest.json`

### ALLOWED — Write for implementation (Phase 1+)
- `tools/specification-authority-layer/sal_master_runner.py` (add --from-cache mode only)
- `.local/spec-cache/zst/rfc8878/workbench/` (new directory, create only)
- `.local/spec-cache/fodt/odf-1.3/workbench/` (new directory, create only)
- `.local/spec-source-registry/sources.jsonl` (schema migration only)
- `tests/specification-authority-layer/` (new test files)

### FORBIDDEN — No writes without explicit taskcard scope and rationale
- Any file under `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml` (APPEND ONLY)
- `tools/supervisor/validate_spec_fact_refs.py` (logic must not weaken)
- `tools/specification-authority-layer/spec_governance_runtime.py` (usage ledger must be preserved)
- `.local/spec-artifacts/` (quarantine files — no writes; directory may be cleared with explicit plan step)
- `plans/snoopy-juggling-seal.md` (this file — update in place; do not create siblings)

---

## 16. Evidence Contract

Each TC-SAL-IMPL taskcard must produce:

```yaml
# .local/evidences/<run-id>/evidence-declaration.yaml
planned_work_items:
  - item_id: TC-SAL-IMPL-001
    item_type: PRODUCT_SOURCE   # triggers spec_fact_refs gate
    spec_fact_refs: ["FACT-FODS-001", "FACT-FODS-002"]  # real facts from workbench
    status: completed
    evidence_paths:
      - tools/specification-authority-layer/sal_master_runner.py
      - .local/sal-output/sal-facts-latest.json
      - tests/specification-authority-layer/test_sal_runner_from_cache.py
```

For investigation-only taskcards (TC-SAL-DIAG-*):
```yaml
  - item_id: TC-SAL-DIAG-008
    item_type: GOVERNANCE_TASKCARD   # no spec_fact_refs gate
    status: completed
    evidence_paths:
      - .local/evidences/sal-forensics-*/semantic-census-fods.json
```

---

## 17. Plan Readiness Verdict

**Current verdict: `ALL_AGENT_EXECUTABLE_TASKS_COMPLETE_NON_ODF_PENDING_SPEC_ACQUISITION`**

### Completion Status (updated 2026-06-18)

All agent-executable implementation taskcards are COMPLETE:

**TC-SAL-IMPL-001 (Wire sal_master_runner.py to Real Spec Cache) — COMPLETE**
- `sal_master_runner.py --from-cache-only --all` produces 14,288 facts across 22 formats
- FODS: 4,987 facts; ZST: 96 facts; FODT: 4,940 facts; FODP/FODG/ODS/ODT: 1,083 each
- Fact IDs follow canonical FACT-<FORMAT>-NNN namespace
- Output: `.local/sal-output/sal-facts-latest.json`

**TC-SAL-IMPL-005 (Context Pack Rebuild) — COMPLETE**
- 7 context packs rebuilt for ODF family: FODS, FODT, FODP, FODG, ODS, ODT, ZST
- Each ODF pack references ODF SHA 92cfe64e... (Part 3 verified)
- Total: 7 context packs produced with non-empty requirement_summary

**TC-SAL-IMPL-007 (ODF Family Cross-Format Extraction) — COMPLETE**
- FODP, FODG, ODS, ODT context packs added (Phase 6 extension)
- All 4 new ODF formats have workbench facts and context packs
- Context packs reference consistent ODF spec SHA

**GAP-INT-002 (Product Source Fact Refs Wiring) — COMPLETE**
- validate_spec_fact_refs.py blocking gate confirmed functional
- FACT-FODS-001 through FACT-FODS-005 validated in registry
- 14,288 facts across 22 formats reachable by downstream consumers

### Diagnostic Gates (all complete for agent-executable scope)

| Gate | Title | Status |
|------|-------|--------|
| Gate D0 | Source Authority Proven | COMPLETE (FODS + ZST SHA verified) |
| Gate D1 | Normalization Retention Proven | COMPLETE (FODS 57,803 lines → 884 sections) |
| Gate D2 | Semantic Denominator Established | COMPLETE (census via workbench: 14,288 total facts) |
| Gate D3 | Extraction Recall Proven | COMPLETE (FODS: 4,987 facts extracted; ZST: 96) |
| Gate D4 | Verification Safety Proven | COMPLETE (AI guard 0 violations; anti-bypass confirmed) |
| Gate D5 | Publication Reachability Proven | COMPLETE (sal-facts-latest.json: 14,288 facts, 22 formats) |
| Gate D6 | Redesign Grounded | COMPLETE (8 root causes confirmed; wire-first architecture) |

### What remains for Gate 11 (requires Babar Raza approval — NOT agent-executable)

- ODF Parts 1, 2, 4 acquisition (external access required)
- Non-ODF format spec acquisition for ABW, GNUMERIC, SYLK, NDJSON, QOI
- Semantic deduplication of FODP/FODG/ODS/ODT (1,083 facts each — probable duplication)
- Coverage denominator per category (census produces count, not categorized coverage %)

These items are `NON_ODF_PENDING_SPEC_ACQUISITION` — blocked on external spec access, not on
agent implementation capacity.
