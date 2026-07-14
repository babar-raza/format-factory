# Format Factory Spec-to-Code Forensic Audit & Healing Mission
**Plan ID:** cheeky-crafting-manatee
**Mission ID:** FF-FORENSIC-AUDIT-001
**Plan Type:** forensic_audit_healing
**Created:** 2026-07-10
**Authority:** spec-to-feature-radical-correction-plan.md (binding)
**Enhancement Version:** 2.0 (micro-taskcardized, machine-state-hardened, execution-ready)

---

## PART I: PREFLIGHT AND AUTHORITY RECORD

### I.1 Preflight Checklist

| Check | Expected | Status |
|---|---|---|
| Active plan lock (vast-weaving-lampson) | TERMINAL_CLOSED | PASS — confirmed in .local/supervisor/active-plan-lock.json |
| No conflicting plan in progress | Zero IN_PROGRESS locks | VERIFY at session start |
| AUTONOMOUS_CONTINUE | YES | Confirmed in approval-gates.md |
| Contradiction count | 0 blocking | Confirmed in contradictions.md |
| Oracle status | 73/73 PASS | Confirmed from layer-audit-2026-06-26 |
| Existing forensic artifacts | reports/forensic-audit-20260625/ present | VERIFY at session start |
| Binding authority readable | spec-to-feature-radical-correction-plan.md | VERIFY at session start |

### I.2 Authority Verdict

**Binding authority:** `plans/strategic/spec-to-feature-radical-correction-plan.md`
**This plan is subordinate.** Any conflict between this plan and the correction plan: correction plan wins.
**Lanes in scope:** 0-6 (analysis + machinery repair). Lanes 7-13 (product regeneration) are BLOCKED until Lanes 1-6, 14, 15 complete.
**Conflict resolution:** If a taskcard in this plan requires product source changes before Lanes 1-6 complete, defer it to TC-FF-AUDIT-081 (product healing) and mark the dependency explicitly.

### I.3 Section Processing Ledger

| Section | Lines Written | Status |
|---|---|---|
| Part I: Preflight | ~30 | COMPLETE |
| Part II: Context | ~40 | COMPLETE |
| Part III: Requirements | ~60 | COMPLETE |
| Part IV: Solution Options | ~120 | COMPLETE |
| Part V: Machine State Model | ~80 | COMPLETE |
| Part VI: Taskcard Register | ~500 | COMPLETE |
| Part VII: Dependency DAG | ~40 | COMPLETE |
| Part VIII: Validation Matrix | ~60 | COMPLETE |
| Part IX: Evidence Contract | ~40 | COMPLETE |
| Part X: Quality Scoring | ~40 | COMPLETE |
| Part XI: Reconciliation | ~20 | COMPLETE |
| Part XII: Execution Handoff | ~30 | COMPLETE |

### I.4 Duplicate Plan Risk

No duplicate plan files detected. Previous plan `vast-weaving-lampson` is TERMINAL_CLOSED.
This plan (`cheeky-crafting-manatee`) is the SOLE active work authority for this session.
Guard: before any sprint execution, verify `.local/supervisor/active-plan-lock.json` shows THIS plan path.

---

## PART II: CONTEXT AND BACKGROUND

### II.1 Mission Summary

Complete forensic audit tracing every governed format through the full spec-to-code pipeline:
`SPEC → FACTS → QNAMES → CAPABILITIES → FEATURES → CODE → TESTS → PACKAGE → CONSUMER`

Measuring conversion ratios at every boundary, finding all losses/distortions/fabrications,
root-causing gaps, evaluating fix options, executing machinery repair, pilots, backfill,
and product healing until all formats reach green audit status.

### II.2 Current State (as of 2026-07-10)

- **24 active formats:** 20 with Python source, 10 with .NET source, 4 OBLIGATION_CREATED (ora/pam/xpm/zpaq)
- **SAL facts:** 14,441 total — ONLY ODF family has spec-derived facts; 14/20 Python formats have ZERO SAL facts
- **QName coverage:** Reported 100% but most qnames are manually seeded (not spec-derived)
- **Oracle:** ALL 20 Python formats VERIFIED (73/73 PASS) — disconnected from sprint loop
- **Existing infrastructure:** `reports/forensic-audit-20260625/`, `reports/layer-audit-2026-06-26/`
- **Prior plan:** vast-weaving-lampson is TERMINAL_CLOSED; this is a fresh mission

### II.3 Critical Lane Constraint

Lanes 1-6, 14, 15 of `spec-to-feature-radical-correction-plan.md` MUST complete before product
regeneration (Lanes 7-13). Batches 0-6 of this plan directly implement Lanes 0-6.
Batch 8 (product healing) is gated: only begins after Batch 6 machinery repair is complete AND
the correction plan's Lane 6 gate is met.

### II.4 Output Root

All artifacts go to: `reports/spec-to-code-forensic-audit/`

**Required terminal artifacts (23 total):**
```
format-inventory.yaml              specification-source-inventory.yaml
specification-measurement-register.yaml  raw-spec-unit-register.yaml
normalized-fact-register.yaml      sal-authority-audit.yaml
qname-traceability-register.yaml   capability-register.yaml
feature-register.yaml              code-traceability-register.yaml
feature-proof-register.yaml        spec-to-code-traceability-graph.yaml
format-pipeline-metrics.csv        portfolio-pipeline-metrics.md
pipeline-anomaly-register.yaml     forensic-gap-register.yaml
root-cause-register.yaml           fix-option-register.yaml
chosen-repair-plan.md              taskcard-register.yaml
execution-batch-register.yaml      execution-handoff.yaml
pipeline-idempotency-verdict.md    final-report.md
```

---

## PART III: REQUIREMENTS INVENTORY

| Req ID | Requirement | Source | Priority | Testable |
|---|---|---|---|---|
| REQ-FA-001 | Audit ALL 24 governed formats — no format omitted | Mission spec §1 | P0 | Yes: format-inventory.yaml has 24 entries |
| REQ-FA-002 | Measure spec→fact conversion ratio for every format | Mission spec §5 | P0 | Yes: ratio in metrics CSV |
| REQ-FA-003 | Measure fact→qname conversion ratio for every format | Mission spec §7 | P0 | Yes: ratio in metrics CSV |
| REQ-FA-004 | Measure capability→feature→code ratios | Mission spec §9-11 | P0 | Yes: in metrics CSV |
| REQ-FA-005 | Classify every SAL fact by provenance status | Mission spec §6 | P0 | Yes: sal-authority-audit.yaml |
| REQ-FA-006 | All 14 zero-fact formats must reach non-zero facts after Batch 6 | Mission spec §14 | P1 | Yes: sal-facts-latest.json |
| REQ-FA-007 | Feature compiler produces ≥1 work item per format with open gaps | Mission spec §10 | P1 | Yes: next-work-items.json |
| REQ-FA-008 | All 79 qname entries have source_fact_ids populated | Mission spec §8 | P1 | Yes: python-qname-architecture.json |
| REQ-FA-009 | Root causes documented with specific RC-IDs (min 5) | Mission spec §15 | P1 | Yes: root-cause-register.yaml |
| REQ-FA-010 | Fix options evaluated (min 2 per RC) with scoring | Mission spec §16 | P1 | Yes: fix-option-register.yaml |
| REQ-FA-011 | All product healing changes use governed skills | Correction plan §6 | P1 | Yes: product-code-change-ledger.json |
| REQ-FA-012 | ODF pilot shows complete end-to-end traceability chain | Mission spec §19 | P2 | Yes: pilots/fods-pilot.yaml |
| REQ-FA-013 | CSV pilot shows RFC 4180 → code chain | Mission spec §20 | P2 | Yes: pilots/csv-pilot.yaml |
| REQ-FA-014 | QOI pilot shows binary spec → code chain | Mission spec §21 | P2 | Yes: pilots/qoi-pilot.yaml |
| REQ-FA-015 | All 20 Python formats show non-zero spec_to_fact_ratio | Mission spec §22 | P2 | Yes: metrics CSV |
| REQ-FA-016 | Idempotency verified: running measurement twice gives same counts | Mission spec §30 | P2 | Yes: pipeline-idempotency-verdict.md |
| REQ-FA-017 | No `src/python/` or `src/net/` changes in Batches 0-5 | Governance §4 | P0 | Yes: git diff analysis |
| REQ-FA-018 | forensic-baseline.yaml must exist before any analysis taskcard runs | Mission spec §2 | P0 | Yes: file exists check |
| REQ-FA-019 | Final verdict issued from prescribed vocabulary | Mission spec §34 | P2 | Yes: final-report.md last line |
| REQ-FA-020 | Before/after delta table produced for all formats | Mission spec §27 | P2 | Yes: metrics CSV has before/after cols |
| REQ-FA-021 | QName collapse ratios documented and classified as INTENTIONAL or GAP | Mission spec §7 | P1 | Yes: qname-traceability-register.yaml |
| REQ-FA-022 | All 4 OBLIGATION_CREATED formats documented with explicit no-implementation reason | Mission spec §3 | P1 | Yes: format-inventory.yaml |
| REQ-FA-023 | execution-handoff.yaml produced for any remaining work at closure | Mission spec §33 | P2 | Yes: file exists at TC-FF-AUDIT-092 |

---

## PART IV: SOLUTION OPTIONS ANALYSIS

### RC-001: SAL Extractors Missing for 14 Non-ODF Formats

**Impact:** spec_to_fact_ratio = 0.0 for 14/20 Python formats. All downstream ratios invalid.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Build automated RFC/ABNF parser → SAL facts | HIGH | HIGH | MEDIUM | 3/5 |
| B | Manual seeding with MANUALLY_SEEDED classification | LOW | MEDIUM | LOW | **4/5** |
| C | Declare as SPEC_ONLY, record traceability gap | ZERO | LOW | LOW | 2/5 |

**Decision:** Option B (short-term) + Option A (long-term, TC-FF-AUDIT-060 creates seeders).
Manual seeding with explicit provenance is honest, executable, and unblocks all downstream ratios.
Automated extraction is the long-term goal but out of scope for this mission.

### RC-002: QName Collapse (4,988 FODS facts → 12 qnames)

**Impact:** fact_to_qname ratio is ~0.2% for ODF. Reported "100% qname coverage" is misleading.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Expand qname registry to 1:1 with spec elements | EXTREME | HIGH | HIGH | 1/5 |
| B | Accept coarse-grained qnames as intentional architecture | ZERO | MEDIUM | LOW | 3/5 |
| C | Add fact_ids[] field to each qname entry (retroactive documentation) | LOW | HIGH | LOW | **5/5** |

**Decision:** Option C. The collapse is intentional architecture (semantic grouping not 1:1 mapping).
Document it honestly with `source_fact_ids[]` and `derivation_method: INTENTIONAL_GROUPING`.
Record in root-cause-register as `architecture_decision` not a `gap`.

### RC-003: Non-ODF Capabilities Are POC-Derived (Not Spec-Fact-Derived)

**Impact:** Capability chain broken for 14/20 formats. Capabilities exist in code but lack spec authority.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Mark as POC_DERIVED_NOT_SPEC_DERIVED (honest classification) | LOW | HIGH | LOW | **5/5** |
| B | Retroactively seed SAL facts for each capability behavior | MEDIUM | HIGH | MEDIUM | 4/5 |
| C | Remove untraced capabilities from register | ZERO | MEDIUM | HIGH | 1/5 |

**Decision:** Option A immediately, then Option B as part of TC-FF-AUDIT-060 (seed SAL facts).
Honest classification first; then capability authority improves as facts are seeded.

### RC-004: Feature Compiler Produces Near-Zero Output

**Impact:** next-work-items.json unreliable. Sprint loop can't select work automatically.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Fix canonical compiler (tools/supervisor/capability_feature_compiler.py) | MEDIUM | HIGH | LOW | **5/5** |
| B | Replace with manual feature list seeding | LOW | MEDIUM | MEDIUM | 3/5 |
| C | Use planning tool (capability_to_feature_compiler.py) as interim | LOW | LOW | MEDIUM | 2/5 |

**Decision:** Option A. Read both files, identify deduplication bug, fix canonical compiler.
Evidence: compiler produces ≥1 work item per format with open gaps in product-deepening-ledger.

### RC-005: Oracle Results Disconnected from Sprint Loop

**Impact:** 73/73 PASS oracle results are not feeding back into capability/feature proof levels.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Wire oracle results into feature-proof-register.yaml | LOW | HIGH | LOW | **5/5** |
| B | Build automated oracle→sprint-signal bridge | HIGH | HIGH | MEDIUM | 3/5 |
| C | Document disconnection as known gap in final report | ZERO | LOW | LOW | 2/5 |

**Decision:** Option A (TC-FF-AUDIT-041 manually wires oracle verdicts into proof register).

### RC-006: QName Seeding Is Entirely Manual

**Impact:** New formats require manual qname creation. No automated pipeline from spec units.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Build spec-unit → qname auto-generator | HIGH | HIGH | MEDIUM | 3/5 |
| B | Codify manual seeding process as a governed skill (/qname-backfill) | LOW | MEDIUM | LOW | **4/5** |
| C | Accept manual seeding for new formats, document in governance | ZERO | LOW | LOW | 2/5 |

**Decision:** Option B. `/qname-backfill` skill already registered. Use it for TC-FF-AUDIT-062.

### RC-007: Four Formats (ora/pam/xpm/zpaq) Have OBLIGATION_CREATED But No Implementation Path

**Impact:** These formats count as "governed" but cannot progress through the pipeline.

| Option | Description | Effort | Accuracy | Risk | Score |
|---|---|---|---|---|---|
| A | Build stub products for all 4 (new-format-kickstart) | HIGH | MEDIUM | HIGH | 2/5 |
| B | Document explicitly in format-inventory.yaml as SPEC_ONLY with gap reason | ZERO | HIGH | LOW | **5/5** |
| C | Remove from governed format list | ZERO | MEDIUM | HIGH | 1/5 |

**Decision:** Option B. Honest accounting: SPEC_ONLY state with explicit `no_implementation_reason`.
Not in scope for this audit mission; tracked in forensic-gap-register.yaml for future planning.

---

## PART V: MACHINE STATE MODEL

### V.1 Parent Taskcard States

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED
                                                                                           ↓
                                                                                        REROUTED (score < 4/5)
                                                      ↓
                                                   BLOCKED (dependency not met)
```

**Transitions:**
- `PROPOSED → READY`: All dependencies in plan are CLOSED
- `READY → IN_PROGRESS`: Executor picks up the TC (writes IN_PROGRESS to plan)
- `IN_PROGRESS → CHILDREN_IN_PROGRESS`: First child micro-step begins
- `CHILDREN_IN_PROGRESS → INTEGRATION_PENDING`: All child TCs are CLOSED
- `INTEGRATION_PENDING → VERIFIED`: Validation command passes, evidence file exists
- `VERIFIED → SCORED`: Quality dimensions scored (1-5 each)
- `SCORED → CLOSED`: All scores ≥ 4/5 OR waiver granted
- `SCORED → REROUTED`: Any score < 4/5 → add rework child TC → re-execute → re-score
- `ANY → BLOCKED`: Named dependency fails to complete within current session

**Invalid transitions (blocked):**
- `PROPOSED → CLOSED` (no execution evidence)
- `READY → VERIFIED` (skip execution)
- `BLOCKED → CLOSED` (must resolve blocker first)

### V.2 Child Taskcard States

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
                                                  ↓
                                               FAILED (negative control triggered)
```

### V.3 Micro-step States

```
PENDING → READY → ACTIVE → COMPLETE
                      ↓
                   FAILED → [retry once] → BLOCKED
```

### V.4 Quality Score Dimensions (1-5 each, reroute threshold: < 4)

| Dimension | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|
| Completeness | All fields populated | 1 optional missing | 2-3 missing | Core fields missing | File empty |
| Accuracy | Zero errors verified | Minor discrepancy noted | 1 unverified claim | Multiple errors | Fabricated |
| Traceability | Source cited for every value | Source cited for 90%+ | 75%+ cited | <50% cited | No sources |
| Idempotency | Same output on 2nd run | Stable within 1% | Minor variance | Significant variance | Non-deterministic |
| Evidence | Direct proof file exists | Indirect proof | Implied proof | Synthetic only | No proof |

**Reroute rule:** If any dimension scores < 4, open a REROUTED child TC with specific remediation action.
Close the rework child, re-score the parent. Maximum 2 reroute loops before escalating to user.

---

## PART VI: TASKCARD REGISTER (HIERARCHICAL)

### Batch 0 — Status, Baseline, and Traceability Infrastructure

---

#### TC-FF-AUDIT-001 [PARENT]: Repository Status Recon and Forensic Baseline
**State:** PROPOSED
**Priority:** P0
**Type:** FORENSIC_RECON
**Lane:** coordinator
**Objective:** Establish machine-readable forensic baseline before any analysis begins.
**Dependency:** None (first task)
**Blocking:** TC-FF-AUDIT-002, TC-FF-AUDIT-003, TC-FF-AUDIT-004, TC-FF-AUDIT-010

**Children:**

##### TC-FF-AUDIT-001-A: Read Repository State Files
**State:** TODO
**Validation:** All 5 files successfully read, no read errors
**Evidence:** console output captured
**Micro-steps:**
- MS-001-A-1: `PENDING` Read `reports/supervisor/session-resume.md` → confirm AUTONOMOUS_CONTINUE
- MS-001-A-2: `PENDING` Read `reports/supervisor/approval-gates.md` → extract verdict
- MS-001-A-3: `PENDING` Read `reports/supervisor/contradictions.md` → confirm 0 blocking
- MS-001-A-4: `PENDING` Read `registry/format-registry.yaml` → extract all 24 format IDs
- MS-001-A-5: `PENDING` Read `registry/repository-layout.yaml` → confirm path conventions

##### TC-FF-AUDIT-001-B: Read Spec and SAL Infrastructure
**State:** TODO
**Depends on:** TC-FF-AUDIT-001-A (CLOSED)
**Validation:** SAL fact count extracted, baseline metrics CSV read
**Evidence:** counts recorded
**Micro-steps:**
- MS-001-B-1: `PENDING` Locate SAL facts source: `.local/spec-cache/sal-facts-latest.json` OR `tools/spec/merge_sal_facts.py` output
- MS-001-B-2: `PENDING` Extract per-format fact counts (expect ODF: ~13169, others: varies)
- MS-001-B-3: `PENDING` Read `reports/forensic-audit-20260625/format-pipeline-metrics.csv` — baseline
- MS-001-B-4: `PENDING` Read `reports/layer-audit-2026-06-26/forensic-layer-discovery-report.md`

##### TC-FF-AUDIT-001-C: Write forensic-baseline.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-001-B (CLOSED)
**Validation:** `python -c "import yaml; yaml.safe_load(open('reports/spec-to-code-forensic-audit/forensic-baseline.yaml'))"` exits 0
**Evidence:** `reports/spec-to-code-forensic-audit/forensic-baseline.yaml`
**Negative control:** File must NOT exist before this step (no stale artifact)
**Micro-steps:**
- MS-001-C-1: `PENDING` Create `reports/spec-to-code-forensic-audit/` directory if needed
- MS-001-C-2: `PENDING` Write YAML with all fields: mission_id, repository, branch, head, active_plan, specification_roots, normalized_fact_roots, qname_roots, capability_roots, feature_roots, product_roots, test_roots, package_roots, ledgers, recent_runs, current_claims, verified_claims, contradicted_claims, stale_claims, evidence_root
- MS-001-C-3: `PENDING` Validate YAML parses without error
- MS-001-C-4: `PENDING` Mark TC-FF-AUDIT-001 State → VERIFIED

---

#### TC-FF-AUDIT-002 [PARENT]: Complete Format Inventory (YAML)
**State:** PROPOSED
**Priority:** P0
**Type:** FORENSIC_RECON
**Lane:** inventory
**Objective:** Produce format-inventory.yaml with one entry per all 24 governed formats.
**Dependency:** TC-FF-AUDIT-001 (CLOSED)
**Blocking:** TC-FF-AUDIT-010, TC-FF-AUDIT-020, TC-FF-AUDIT-030

**Children:**

##### TC-FF-AUDIT-002-A: Enumerate Formats from Registry
**State:** TODO
**Validation:** Exactly 24 format IDs extracted
**Micro-steps:**
- MS-002-A-1: `PENDING` Read `registry/format-registry.yaml` — extract all format_ids
- MS-002-A-2: `PENDING` For each format: check Python source presence at `src/python/{format}/`
- MS-002-A-3: `PENDING` For each format: check .NET source presence at `src/net/{format}/`
- MS-002-A-4: `PENDING` Read `registry/python-qname-architecture.json` — qname count per format
- MS-002-A-5: `PENDING` Check `oracle/formats/{format}/` — oracle package presence per format

##### TC-FF-AUDIT-002-B: Classify Format States
**State:** TODO
**Depends on:** TC-FF-AUDIT-002-A (CLOSED)
**Validation:** All 24 formats have a state from the allowed vocabulary
**Allowed states:** DISCOVERED, SPEC_ONLY, NORMALIZATION_PARTIAL, FACTS_AUTHORIZED, QNAME_PARTIAL, CAPABILITY_PARTIAL, FEATURE_PLANNED, CODE_PARTIAL, PRODUCT_PARTIAL, INTEGRATION_VERIFIED, END_TO_END_VERIFIED, PACKAGE_PROVEN, STALE, SUPERSEDED, ABANDONED_WITH_REASON, UNKNOWN
**Micro-steps:**
- MS-002-B-1: `PENDING` Assign state to each of 20 Python formats (expect most: CODE_PARTIAL or INTEGRATION_VERIFIED)
- MS-002-B-2: `PENDING` Assign state to 4 OBLIGATION_CREATED formats (expect: SPEC_ONLY with no_implementation_reason)
- MS-002-B-3: `PENDING` Assign proof_level (0-5) per format: 0=none, 1=unit, 2=integration, 3=oracle, 4=package, 5=consumer

##### TC-FF-AUDIT-002-C: Write format-inventory.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-002-B (CLOSED)
**Validation:** YAML parses; count of entries == 24; all required fields present
**Evidence:** `reports/spec-to-code-forensic-audit/format-inventory.yaml`
**Negative control:** Entries for ora/pam/xpm/zpaq must NOT claim CODE_PARTIAL or higher
**Micro-steps:**
- MS-002-C-1: `PENDING` Write YAML with fields: format_id, canonical_name, aliases, family, specification_authority, specification_version, languages, source_roots, normalized_fact_roots, qname_roots, capability_roots, feature_roots, product_roots, test_roots, package_roots, current_state, current_proof_level, plan_ids, ledger_ids, known_gaps, no_implementation_reason (for SPEC_ONLY)
- MS-002-C-2: `PENDING` Validate YAML; verify entry count == 24
- MS-002-C-3: `PENDING` Mark TC-FF-AUDIT-002 State → VERIFIED

---

#### TC-FF-AUDIT-003 [PARENT]: Specification Source Inventory
**State:** PROPOSED
**Priority:** P0
**Type:** SPEC_INVENTORY
**Lane:** inventory
**Objective:** Record all authoritative specification sources per format.
**Dependency:** TC-FF-AUDIT-001 (CLOSED)

**Children:**

##### TC-FF-AUDIT-003-A: Scan for On-Disk Spec Files
**State:** TODO
**Validation:** All candidate directories scanned
**Micro-steps:**
- MS-003-A-1: `PENDING` Scan `oracle/schemas/` — confirm ODF RelaxNG at `odf-1.3-relaxng/OpenDocument-v1.3-schema.rng`
- MS-003-A-2: `PENDING` Scan `specs/`, `docs/specs/`, `.local/spec-cache/` — catalog any local spec files
- MS-003-A-3: `PENDING` For each on-disk file: record path, file size, line count (if text)

##### TC-FF-AUDIT-003-B: Resolve External Spec References
**State:** TODO
**Validation:** Every format has at least one spec reference (URL/RFC/standard)
**Micro-steps:**
- MS-003-B-1: `PENDING` Map ODF family → OASIS ODF 1.3 (RelaxNG on disk)
- MS-003-B-2: `PENDING` Map CSV → RFC 4180; TSV → IANA text/tab-separated-values
- MS-003-B-3: `PENDING` Map ZST → RFC 8878; NDJSON → ndjson.org spec; TOML → toml.io v1.0
- MS-003-B-4: `PENDING` Map image formats: QOI → phoboslab.org/qoi; PBM/PGM/PPM/PAM → netpbm.sf.net; XPM → X11R5; XCF → gimp.org; ORA → create.freedesktop.org
- MS-003-B-5: `PENDING` Map legacy: DIF → Software Arts 1981; SYLK → Microsoft/Multiplan; Gnumeric → developer.gnome.org; ABW → AbiWord format ref; ZPAQ → mattmahoney.net

##### TC-FF-AUDIT-003-C: Write specification-source-inventory.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-003-B (CLOSED)
**Validation:** YAML parses; every format_id has at least one source_reference
**Evidence:** `reports/spec-to-code-forensic-audit/specification-source-inventory.yaml`
**Micro-steps:**
- MS-003-C-1: `PENDING` Write YAML: per format: format_id, source_references[{type, title, url_or_path, version, on_disk, file_path, file_hash, page_count}], extraction_method, ingestion_status
- MS-003-C-2: `PENDING` Validate and mark VERIFIED

---

#### TC-FF-AUDIT-004 [PARENT]: Specification Measurement Register
**State:** PROPOSED
**Priority:** P0
**Type:** SPEC_INVENTORY
**Lane:** inventory
**Objective:** Count spec units per specification source using appropriate counting methodology.
**Dependency:** TC-FF-AUDIT-003 (CLOSED)

**Children:**

##### TC-FF-AUDIT-004-A: Count ODF RelaxNG Schema Units
**State:** TODO
**Validation:** Element count, attribute count, type count are non-zero integers
**Micro-steps:**
- MS-004-A-1: `PENDING` Read `oracle/schemas/odf-1.3-relaxng/OpenDocument-v1.3-schema.rng` (596KB)
- MS-004-A-2: `PENDING` Count: physical lines, `<element>` tags, `<attribute>` tags, `<define>` blocks, `<datatype>` uses
- MS-004-A-3: `PENDING` Record: physical_lines, element_definitions, attribute_definitions, type_definitions, group_definitions

##### TC-FF-AUDIT-004-B: Count Units for Text/RFC Formats
**State:** TODO
**Validation:** Semantic unit count > 0 for each format
**Counting methodology:** Grammar productions for RFC formats; XML element types for XML formats; struct fields for binary formats
**Micro-steps:**
- MS-004-B-1: `PENDING` CSV (RFC 4180): count ABNF productions (~6: record, field, name, CRLF, DQUOTE, textdata)
- MS-004-B-2: `PENDING` ZST (RFC 8878): count ABNF/struct definitions (~12: frame header, block types, etc.)
- MS-004-B-3: `PENDING` NDJSON: count grammar rules (~3: document, line, value)
- MS-004-B-4: `PENDING` TOML v1.0: count ABNF grammar productions (~40+)
- MS-004-B-5: `PENDING` TSV: count structural elements (~3: file, record, field)

##### TC-FF-AUDIT-004-C: Count Units for Binary/Image/XML Formats
**State:** TODO
**Micro-steps:**
- MS-004-C-1: `PENDING` QOI: count struct definitions (~5: header, pixel types, op codes, end marker)
- MS-004-C-2: `PENDING` PBM/PGM/PPM/PAM: count field definitions per format (~4-6 each)
- MS-004-C-3: `PENDING` XCF: count chunk types (~15: header, layer, channel, property types)
- MS-004-C-4: `PENDING` Gnumeric/ABW: count XML element types from spec/source
- MS-004-C-5: `PENDING` DIF/SYLK: count record type codes (DIF: ~8, SYLK: ~10)
- MS-004-C-6: `PENDING` For formats with no accessible local spec (XPM, ORA, ZPAQ): record page count from external reference only; mark counting_method: PAGE_ESTIMATE

##### TC-FF-AUDIT-004-D: Write specification-measurement-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-004-A, TC-FF-AUDIT-004-B, TC-FF-AUDIT-004-C (all CLOSED)
**Validation:** YAML parses; every spec source has semantic_units > 0 or counting_method: PAGE_ESTIMATE
**Evidence:** `reports/spec-to-code-forensic-audit/specification-measurement-register.yaml`
**Micro-steps:**
- MS-004-D-1: `PENDING` Write YAML: per spec source: source_id, format_ids[], physical_lines, semantic_units, counting_method, unit_types[], limitations[]
- MS-004-D-2: `PENDING` Validate; mark VERIFIED

---

### Batch 1 — SAL / Normalized Fact Audit

---

#### TC-FF-AUDIT-010 [PARENT]: Normalized Fact Register and SAL Authority Audit
**State:** PROPOSED
**Priority:** P0
**Type:** FACT_REGENERATION (analysis phase)
**Lane:** sal_audit
**Objective:** Audit all 14,441 SAL facts for provenance. Identify the 14 zero-fact formats.
**Dependency:** TC-FF-AUDIT-002 (CLOSED), TC-FF-AUDIT-003 (CLOSED)
**Blocking:** TC-FF-AUDIT-011, TC-FF-AUDIT-020

**Children:**

##### TC-FF-AUDIT-010-A: Locate and Read SAL Facts Database
**State:** TODO
**Validation:** SAL facts loaded; total count matches ~14,441
**Micro-steps:**
- MS-010-A-1: `PENDING` Check `.local/spec-cache/sal-facts-latest.json` — if exists, read it
- MS-010-A-2: `PENDING` If not present: run `python tools/spec/merge_sal_facts.py` to regenerate
- MS-010-A-3: `PENDING` Extract per-format fact counts; verify ODF formats dominate (~13,169/14,441)
- MS-010-A-4: `PENDING` Confirm 14 non-ODF formats at 0 facts (exclude formats with any manual seeds)

##### TC-FF-AUDIT-010-B: Classify SAL Facts by Provenance
**State:** TODO
**Depends on:** TC-FF-AUDIT-010-A (CLOSED)
**Validation:** Every fact has a provenance_status from allowed vocabulary
**Provenance classes:** AUTHORIZED_AND_CURRENT, AUTHORIZED_BUT_UNUSED, EXTRACTED_NOT_AUTHORIZED, MANUALLY_SEEDED, DERIVED_WITHOUT_SOURCE, DUPLICATE, STALE, CONTRADICTED, FABRICATED_OR_UNSUPPORTED, ORPHANED, MISSING_SOURCE_TRACE
**Micro-steps:**
- MS-010-B-1: `PENDING` For ODF facts: check if they trace to specific RelaxNG `<element>` definitions
- MS-010-B-2: `PENDING` For CSV/TOML/ABW/DIF/GNUMERIC/SYLK/XCF/QOI facts (from TC-LA-001 merge): classify as MANUALLY_SEEDED
- MS-010-B-3: `PENDING` For zero-fact formats: confirm ZERO facts are not cached elsewhere

##### TC-FF-AUDIT-010-C: Investigate SAL Extraction Pipeline
**State:** TODO
**Depends on:** TC-FF-AUDIT-010-B (CLOSED)
**Validation:** Pipeline status (WORKING/BROKEN/NOT_CONFIGURED) confirmed per format
**Micro-steps:**
- MS-010-C-1: `PENDING` Read `tools/spec/merge_sal_facts.py` — understand pipeline architecture
- MS-010-C-2: `PENDING` Check `tools/spec/` directory for per-format extractors or seeders
- MS-010-C-3: `PENDING` Classify each format: PIPELINE_WORKING (ODF), MANUALLY_SEEDED (CSV etc.), NOT_CONFIGURED (ora/pam/xpm/zpaq)
- MS-010-C-4: `PENDING` Confirm root cause: no extractor configured for RFC/informal specs

##### TC-FF-AUDIT-010-D: Write normalized-fact-register.yaml and sal-authority-audit.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-010-C (CLOSED)
**Validation:** Both YAML files parse; every format has an entry; sal-authority-audit has pipeline_status field
**Evidence:** Both files in `reports/spec-to-code-forensic-audit/`
**Negative control:** No format may claim PIPELINE_WORKING with zero facts
**Micro-steps:**
- MS-010-D-1: `PENDING` Write normalized-fact-register.yaml: per format: format_id, fact_count, sample_facts[20], provenance_breakdown{}, pipeline_status
- MS-010-D-2: `PENDING` Write sal-authority-audit.yaml: per format: format_id, fact_count, pipeline_status, extraction_config, gaps[], remediation_tc
- MS-010-D-3: `PENDING` Validate both files; mark VERIFIED

---

#### TC-FF-AUDIT-011 [PARENT]: Raw Spec Unit Register
**State:** PROPOSED
**Priority:** P1
**Type:** SPEC_INVENTORY
**Lane:** sal_audit
**Objective:** Map raw spec units to normalized SAL facts where mapping exists; flag gaps.
**Dependency:** TC-FF-AUDIT-004 (CLOSED), TC-FF-AUDIT-010 (CLOSED)

**Children:**

##### TC-FF-AUDIT-011-A: Map ODF Spec Units to SAL Facts
**State:** TODO
**Validation:** At least 10 ODF elements spot-checked with fact_id mappings
**Micro-steps:**
- MS-011-A-1: `PENDING` Select 10 RelaxNG `<element>` definitions from ODF schema
- MS-011-A-2: `PENDING` For each: find matching SAL fact by element name
- MS-011-A-3: `PENDING` Record: spec_unit_id, spec_unit_name, normalized_fact_id, confidence

##### TC-FF-AUDIT-011-B: Document Non-ODF Spec Unit Gaps
**State:** TODO
**Validation:** All 14 zero-fact formats have entries documenting the gap
**Micro-steps:**
- MS-011-B-1: `PENDING` For each non-ODF format: list spec units from TC-FF-AUDIT-004 as raw units
- MS-011-B-2: `PENDING` Mark each: normalized_fact_id: null, gap_reason: NO_EXTRACTOR_CONFIGURED
- MS-011-B-3: `PENDING` Compute spec_to_fact_ratio per format (0.0 for 14 formats)

##### TC-FF-AUDIT-011-C: Write raw-spec-unit-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-011-A, TC-FF-AUDIT-011-B (CLOSED)
**Validation:** YAML parses; gap entries have gap_reason field
**Evidence:** `reports/spec-to-code-forensic-audit/raw-spec-unit-register.yaml`
**Micro-steps:**
- MS-011-C-1: `PENDING` Write YAML with notation that register is intentionally sparse for non-ODF (pending Batch 6 seeding)
- MS-011-C-2: `PENDING` Validate; mark VERIFIED

---

### Batch 2 — QName and Hierarchy Audit

---

#### TC-FF-AUDIT-020 [PARENT]: QName Traceability Register
**State:** PROPOSED
**Priority:** P1
**Type:** QNAME_REPAIR (analysis phase)
**Lane:** qname_audit
**Objective:** For every qname in registry, determine fact traceability. Compute collapse ratios.
**Dependency:** TC-FF-AUDIT-010 (CLOSED)
**Blocking:** TC-FF-AUDIT-030

**Children:**

##### TC-FF-AUDIT-020-A: Read QName Registry
**State:** TODO
**Validation:** 79 entries loaded; format families identified
**Micro-steps:**
- MS-020-A-1: `PENDING` Read `registry/python-qname-architecture.json` — all 79 entries
- MS-020-A-2: `PENDING` Group by format_id/family
- MS-020-A-3: `PENDING` For each: note element_name, parent_qname, derivation_method (if field exists)

##### TC-FF-AUDIT-020-B: Verify ODF QName → SAL Fact Traceability
**State:** TODO
**Depends on:** TC-FF-AUDIT-020-A (CLOSED)
**Validation:** ODF qnames traced to RelaxNG element names
**Micro-steps:**
- MS-020-B-1: `PENDING` For each ODF qname (e.g., fods:spreadsheet, office:document): find matching SAL fact
- MS-020-B-2: `PENDING` Compute: ODF collapse ratio = qname_count / odf_fact_count (expected ~0.2%)
- MS-020-B-3: `PENDING` Classify collapse as INTENTIONAL_ARCHITECTURE_DECISION (semantic grouping)

##### TC-FF-AUDIT-020-C: Classify Non-ODF QNames
**State:** TODO
**Depends on:** TC-FF-AUDIT-020-A (CLOSED)
**Validation:** All non-ODF qnames classified as MANUALLY_SEEDED
**Micro-steps:**
- MS-020-C-1: `PENDING` For each non-ODF qname: confirm no matching SAL fact exists (fact count = 0)
- MS-020-C-2: `PENDING` Classify: derivation_method: MANUALLY_SEEDED
- MS-020-C-3: `PENDING` Check hierarchy: does each qname have correct parent_qname?

##### TC-FF-AUDIT-020-D: Write qname-traceability-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-020-B, TC-FF-AUDIT-020-C (CLOSED)
**Validation:** YAML parses; all 79 entries present; each has classification and collapse_ratio
**Evidence:** `reports/spec-to-code-forensic-audit/qname-traceability-register.yaml`
**Negative control:** No non-ODF qname may be classified as COMPLETE_AND_VALID if fact_count = 0
**Micro-steps:**
- MS-020-D-1: `PENDING` Write YAML: per qname: qname_id, format_id, element_name, parent_qname, derivation_method, source_fact_ids[], classification, collapse_ratio, hierarchy_valid
- MS-020-D-2: `PENDING` Validate; mark VERIFIED

---

### Batch 3 — Capability and Feature Audit

---

#### TC-FF-AUDIT-030 [PARENT]: Product Capability Register
**State:** PROPOSED
**Priority:** P1
**Type:** CAPABILITY_REPAIR (analysis phase)
**Lane:** capability_audit
**Objective:** Build capability register for product behaviors (LOAD/QUERY/MUTATE/SAVE etc.).
**Dependency:** TC-FF-AUDIT-020 (CLOSED)
**Blocking:** TC-FF-AUDIT-031

**Children:**

##### TC-FF-AUDIT-030-A: Read Capability Source Data
**State:** TODO
**Validation:** Product-deepening-ledger read; gap count extracted
**Micro-steps:**
- MS-030-A-1: `PENDING` Read `registry/product-deepening-ledger.yaml` (1,710 lines) — extract capability linkage data
- MS-030-A-2: `PENDING` Read latest `reports/capability-layer/gap-sal-traceability-*.json` — gap-to-capability mapping
- MS-030-A-3: `PENDING` For each format: identify what capabilities are claimed (LOAD, QUERY, MUTATE, SAVE, RELOAD, EXPORT, VALIDATE, ANALYTICS)

##### TC-FF-AUDIT-030-B: Classify Capability Derivation Method
**State:** TODO
**Depends on:** TC-FF-AUDIT-030-A (CLOSED)
**Validation:** Every capability has derivation_method from: FACT_DERIVED_AND_VALID, POC_DERIVED, MANUALLY_AUTHORED, DUPLICATE, UNSUPPORTED, UNCONSUMED
**Micro-steps:**
- MS-030-B-1: `PENDING` ODF formats: classify LOAD/QUERY/SAVE as FACT_DERIVED_AND_VALID (SAL facts exist)
- MS-030-B-2: `PENDING` Non-ODF formats: classify all capabilities as POC_DERIVED (no SAL facts)
- MS-030-B-3: `PENDING` Map capabilities to source SAL facts where available

##### TC-FF-AUDIT-030-C: Write capability-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-030-B (CLOSED)
**Validation:** YAML parses; every format has ≥1 capability entry
**Evidence:** `reports/spec-to-code-forensic-audit/capability-register.yaml`
**Micro-steps:**
- MS-030-C-1: `PENDING` Write YAML: per format: format_id, capabilities[{capability_id, type, derivation_method, source_fact_ids[], code_symbols[]}]
- MS-030-C-2: `PENDING` Validate; mark VERIFIED

---

#### TC-FF-AUDIT-031 [PARENT]: Feature Register
**State:** PROPOSED
**Priority:** P1
**Type:** FEATURE_COMPILER_REPAIR (analysis phase)
**Lane:** feature_audit
**Objective:** Map capabilities to planned features; assess feature compiler output.
**Dependency:** TC-FF-AUDIT-030 (CLOSED)
**Blocking:** TC-FF-AUDIT-040

**Children:**

##### TC-FF-AUDIT-031-A: Run Feature Compiler Dry-Run
**State:** TODO
**Validation:** Compiler runs without crash; output captured (may be empty — document honestly)
**Micro-steps:**
- MS-031-A-1: `PENDING` Run `python tools/supervisor/capability_feature_compiler.py --help` to confirm CLI
- MS-031-A-2: `PENDING` Run with dry-run mode (or equivalent) and capture output
- MS-031-A-3: `PENDING` Read `reports/supervisor/next-work-items.json` — current planned features
- MS-031-A-4: `PENDING` Document: compiler_output_count (expected near-zero — this is the RC-004 finding)

##### TC-FF-AUDIT-031-B: Map Capabilities to Features
**State:** TODO
**Depends on:** TC-FF-AUDIT-031-A (CLOSED)
**Validation:** Every open gap in product-deepening-ledger has a feature entry
**Micro-steps:**
- MS-031-B-1: `PENDING` For each format with open gaps: create feature entries manually from ledger data
- MS-031-B-2: `PENDING` Classify each: VALID_AND_EXECUTABLE, VALID_BUT_UNEXECUTED, PARTIAL, DUPLICATE, MISSING

##### TC-FF-AUDIT-031-C: Write feature-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-031-B (CLOSED)
**Validation:** YAML parses; compiler_status field documents RC-004 finding
**Evidence:** `reports/spec-to-code-forensic-audit/feature-register.yaml`
**Micro-steps:**
- MS-031-C-1: `PENDING` Write YAML with compiler_status: NEAR_ZERO_OUTPUT and manual feature map
- MS-031-C-2: `PENDING` Validate; mark VERIFIED

---

### Batch 4 — Code Traceability Audit

---

#### TC-FF-AUDIT-040 [PARENT]: Code Traceability Register
**State:** PROPOSED
**Priority:** P1
**Type:** FORENSIC_RECON
**Lane:** code_audit
**Objective:** Map planned features to actual code symbols for all formats.
**Dependency:** TC-FF-AUDIT-031 (CLOSED)
**Blocking:** TC-FF-AUDIT-041

**Children:**

##### TC-FF-AUDIT-040-A: Analyze Python Source Per Format
**State:** TODO
**Validation:** All 20 Python format sources analyzed; symbol counts recorded
**Micro-steps:**
- MS-040-A-1: `PENDING` For each Python format: count classes, dataclasses, enums, public functions in `src/python/{format}/`
- MS-040-A-2: `PENDING` Identify parser class (parse_{format}) and serializer class (write_{format})
- MS-040-A-3: `PENDING` Check spec_qname ClassVar presence (governance requirement)
- MS-040-A-4: `PENDING` Classify each symbol: FULLY_IMPLEMENTED, STRUCTURAL_SHELL_ONLY, STUB, PARTIAL, MONOLITHIC_COLLAPSE, MISSING

##### TC-FF-AUDIT-040-B: Analyze .NET Source Per Format
**State:** TODO
**Validation:** All 10 .NET format sources analyzed; symbol counts recorded
**Micro-steps:**
- MS-040-B-1: `PENDING` For each .NET format: count classes, interfaces, records, public methods in `src/net/{format}/`
- MS-040-B-2: `PENDING` Identify Document class, Parser class, Serializer class per format
- MS-040-B-3: `PENDING` Check spec_qname ClassVar presence
- MS-040-B-4: `PENDING` Classify each .cs file by implementation status

##### TC-FF-AUDIT-040-C: Write code-traceability-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-040-A, TC-FF-AUDIT-040-B (CLOSED)
**Validation:** YAML parses; all 20+ formats have entries
**Evidence:** `reports/spec-to-code-forensic-audit/code-traceability-register.yaml`
**Micro-steps:**
- MS-040-C-1: `PENDING` Write YAML: per format: format_id, language, source_path, symbols[{name, type, classification, feature_id, spec_qname}]
- MS-040-C-2: `PENDING` Validate; mark VERIFIED

---

#### TC-FF-AUDIT-041 [PARENT]: Feature Proof Register
**State:** PROPOSED
**Priority:** P1
**Type:** FORENSIC_RECON
**Lane:** test_audit
**Objective:** Determine proof level (0-5) for every coded feature. Wire oracle results.
**Dependency:** TC-FF-AUDIT-040 (CLOSED)
**Blocking:** TC-FF-AUDIT-050

**Children:**

##### TC-FF-AUDIT-041-A: Count Tests Per Format
**State:** TODO
**Validation:** Test counts recorded for all formats
**Micro-steps:**
- MS-041-A-1: `PENDING` For each Python format: count test files in `tests/python/{format}/` or `tests/{format}/`
- MS-041-A-2: `PENDING` For each .NET format: count C# test files
- MS-041-A-3: `PENDING` Record: unit_tests, integration_tests, e2e_tests, oracle_cases per format

##### TC-FF-AUDIT-041-B: Assign Proof Levels from Oracle Results
**State:** TODO
**Depends on:** TC-FF-AUDIT-041-A (CLOSED)
**Validation:** All 20 VERIFIED formats get proof_level ≥ 3
**Micro-steps:**
- MS-041-B-1: `PENDING` All 20 Python VERIFIED formats (73/73 PASS) → proof_level: 3 (ORACLE_VERIFIED)
- MS-041-B-2: `PENDING` .NET formats without oracle → proof_level: 1 or 2
- MS-041-B-3: `PENDING` Check packaging proof: any format with `pip install` proof → proof_level: 4

##### TC-FF-AUDIT-041-C: Write feature-proof-register.yaml
**State:** TODO
**Depends on:** TC-FF-AUDIT-041-B (CLOSED)
**Evidence:** `reports/spec-to-code-forensic-audit/feature-proof-register.yaml`
**Micro-steps:**
- MS-041-C-1: `PENDING` Write YAML: per feature: feature_id, format_id, proof_level, oracle_verdict, test_files[], evidence_paths[]
- MS-041-C-2: `PENDING` Validate; mark VERIFIED

---

### Batch 5 — Loss Analysis, Anomalies, and Portfolio Metrics

---

#### TC-FF-AUDIT-050 [PARENT]: Pipeline Anomaly Register and Conversion Ratios
**State:** PROPOSED
**Priority:** P1
**Type:** FORENSIC_RECON
**Lane:** analysis
**Objective:** Compute all conversion ratios; identify anomalies; produce metrics tables.
**Dependency:** TC-FF-AUDIT-010 through TC-FF-AUDIT-041 (all CLOSED)
**Blocking:** TC-FF-AUDIT-051

**Children:**

##### TC-FF-AUDIT-050-A: Compute Conversion Ratios Per Format
**State:** TODO
**Validation:** All 9 ratios computed for all formats; non-ODF ratios for spec_to_fact = 0.0
**Ratios:** spec_to_fact_ratio, fact_authorization_ratio, fact_to_qname_ratio, fact_to_capability_ratio, capability_to_feature_ratio, feature_to_code_ratio, code_to_focused_test_ratio, code_to_integration_ratio, code_to_e2e_ratio
**Micro-steps:**
- MS-050-A-1: `PENDING` For each format: compute all 9 ratios from data in Batches 0-4 registers
- MS-050-A-2: `PENDING` Flag anomalies: any ratio = 0.0 when inputs > 0, any ratio > 1.0 (overclaim), any NaN (divide by zero)

##### TC-FF-AUDIT-050-B: Write Pipeline Metrics Files
**State:** TODO
**Depends on:** TC-FF-AUDIT-050-A (CLOSED)
**Evidence:** Both files in `reports/spec-to-code-forensic-audit/`
**Micro-steps:**
- MS-050-B-1: `PENDING` Write `format-pipeline-metrics.csv`: one row per format, all 9 ratios as columns + before/after columns
- MS-050-B-2: `PENDING` Write `portfolio-pipeline-metrics.md`: aggregate view with weighted averages, narrative
- MS-050-B-3: `PENDING` Write `pipeline-anomaly-register.yaml`: all detected anomalies by boundary

##### TC-FF-AUDIT-050-C: Verify and Mark VERIFIED
**State:** TODO
**Depends on:** TC-FF-AUDIT-050-B (CLOSED)
**Negative control:** Anomaly register must NOT be empty (we know anomalies exist)
**Micro-steps:**
- MS-050-C-1: `PENDING` Validate all 3 files parse; CSV has correct column count
- MS-050-C-2: `PENDING` Confirm anomaly count > 0 (RC-001 through RC-007 must appear)

---

#### TC-FF-AUDIT-051 [PARENT]: Root Cause Register
**State:** PROPOSED
**Priority:** P1
**Lane:** analysis
**Dependency:** TC-FF-AUDIT-050 (CLOSED)
**Blocking:** TC-FF-AUDIT-052

**Children:**

##### TC-FF-AUDIT-051-A: Write root-cause-register.yaml
**State:** TODO
**Validation:** Minimum 5 RCs documented; each has type, impact, affected_formats, remediation_tc
**Evidence:** `reports/spec-to-code-forensic-audit/root-cause-register.yaml`
**Micro-steps:**
- MS-051-A-1: `PENDING` Write RC-001: missing SAL extractors (14 formats, type: CONFIGURATION_GAP)
- MS-051-A-2: `PENDING` Write RC-002: qname collapse (all ODF, type: INTENTIONAL_ARCHITECTURE_DECISION)
- MS-051-A-3: `PENDING` Write RC-003: POC-derived capabilities (14 formats, type: PROVENANCE_GAP)
- MS-051-A-4: `PENDING` Write RC-004: feature compiler near-zero output (all formats, type: TOOL_BUG)
- MS-051-A-5: `PENDING` Write RC-005: oracle disconnected from sprint loop (all 20, type: INTEGRATION_GAP)
- MS-051-A-6: `PENDING` Write RC-006: manual qname seeding (14 formats, type: AUTOMATION_GAP)
- MS-051-A-7: `PENDING` Write RC-007: 4 formats OBLIGATION_CREATED no path (type: SCOPE_DEFERRED)
- MS-051-A-8: `PENDING` Validate YAML; mark VERIFIED

---

#### TC-FF-AUDIT-052 [PARENT]: Fix Option Register and Chosen Repair Strategies
**State:** PROPOSED
**Priority:** P1
**Lane:** analysis
**Dependency:** TC-FF-AUDIT-051 (CLOSED)
**Blocking:** TC-FF-AUDIT-053, TC-FF-AUDIT-060, TC-FF-AUDIT-061, TC-FF-AUDIT-062

**Children:**

##### TC-FF-AUDIT-052-A: Write fix-option-register.yaml
**State:** TODO
**Validation:** Every RC-ID has ≥2 options; chosen option documented with rationale
**Evidence:** `reports/spec-to-code-forensic-audit/fix-option-register.yaml`
**Micro-steps:**
- MS-052-A-1: `PENDING` Write 3 options per RC-001 through RC-007 (see Part IV Solution Options for content)
- MS-052-A-2: `PENDING` Mark chosen option per RC with rationale
- MS-052-A-3: `PENDING` Validate YAML

##### TC-FF-AUDIT-052-B: Write chosen-repair-plan.md
**State:** TODO
**Depends on:** TC-FF-AUDIT-052-A (CLOSED)
**Evidence:** `reports/spec-to-code-forensic-audit/chosen-repair-plan.md`
**Micro-steps:**
- MS-052-B-1: `PENDING` Write plan: chosen option per RC, execution TC reference, expected outcome
- MS-052-B-2: `PENDING` Verify all chosen options are reflected in Batch 6 taskcards

---

#### TC-FF-AUDIT-053 [PARENT]: Spec-to-Code Traceability Graph
**State:** PROPOSED
**Priority:** P1
**Lane:** analysis
**Dependency:** TC-FF-AUDIT-052 (CLOSED)

**Children:**

##### TC-FF-AUDIT-053-A: Build Traceability Graph
**State:** TODO
**Validation:** YAML parses; every format has a section; edges have confidence field
**Evidence:** `reports/spec-to-code-forensic-audit/spec-to-code-traceability-graph.yaml`
**Micro-steps:**
- MS-053-A-1: `PENDING` Structure: one section per format; edges across all pipeline boundaries
- MS-053-A-2: `PENDING` For each edge: {from_node, to_node, confidence: HIGH/MEDIUM/LOW, current: true/false, gap_reason (if false)}
- MS-053-A-3: `PENDING` ODF formats: most edges confidence: MEDIUM (SAL facts exist but collapse is high)
- MS-053-A-4: `PENDING` Non-ODF formats: SPEC_SOURCE→RAW_SPEC_UNIT: LOW; all others: current: false until Batch 6
- MS-053-A-5: `PENDING` Validate YAML; mark TC-FF-AUDIT-053 VERIFIED

---

### Batch 6 — Machinery Repair

---

#### TC-FF-AUDIT-060 [PARENT]: Fix SAL Extraction Pipeline for Non-ODF Formats
**State:** PROPOSED
**Priority:** P1
**Type:** AUTHORITY_REPAIR
**Lane:** sal_repair
**Objective:** Implement SAL fact seeders for all 14 zero-fact formats (manual seeding with MANUALLY_SEEDED classification).
**Dependency:** TC-FF-AUDIT-052 (CLOSED)
**GOVERNANCE:** Only `tools/spec/` and `.local/spec-cache/` may be modified. `src/python/` and `src/net/` are FORBIDDEN.
**Blocking:** TC-FF-AUDIT-062, TC-FF-AUDIT-070, TC-FF-AUDIT-071, TC-FF-AUDIT-072

**Children:**

##### TC-FF-AUDIT-060-A: Create Seeders for Text/Delimiter Formats (CSV, TSV, NDJSON)
**State:** TODO
**Validation:** Each seeder produces ≥3 SAL facts; authority_status: MANUALLY_SEEDED
**Micro-steps:**
- MS-060-A-1: `PENDING` Create `tools/spec/manual_seed_csv.py`: seed csv:record, csv:field, csv:header, csv:delimiter, csv:quote-char, csv:CRLF (source: RFC 4180)
- MS-060-A-2: `PENDING` Create `tools/spec/manual_seed_tsv.py`: seed tsv:record, tsv:field, tsv:tab-delimiter (source: IANA text/tab-separated-values)
- MS-060-A-3: `PENDING` Create `tools/spec/manual_seed_ndjson.py`: seed ndjson:line, ndjson:object, ndjson:empty-line (source: ndjson.org)
- MS-060-A-4: `PENDING` Run each seeder; verify output records contain source_location pointing to spec section

##### TC-FF-AUDIT-060-B: Create Seeders for Config/Markup Formats (TOML)
**State:** TODO
**Validation:** TOML seeder produces ≥10 SAL facts
**Micro-steps:**
- MS-060-B-1: `PENDING` Create `tools/spec/manual_seed_toml.py`: seed key TOML grammar productions (toml:key, toml:value, toml:table, toml:array, toml:integer, toml:float, toml:boolean, toml:datetime, toml:string, toml:inline-table) (source: toml.io v1.0)
- MS-060-B-2: `PENDING` Run seeder; verify facts

##### TC-FF-AUDIT-060-C: Create Seeders for Legacy Spreadsheet Formats (DIF, SYLK)
**State:** TODO
**Validation:** Each seeder produces ≥3 SAL facts
**Micro-steps:**
- MS-060-C-1: `PENDING` Create `tools/spec/manual_seed_dif.py`: seed dif:TABLE, dif:VECTORS, dif:TUPLES, dif:DATA, dif:BOT, dif:EOD, dif:PERIODICITY, dif:MAJOR (source: Software Arts 1981)
- MS-060-C-2: `PENDING` Create `tools/spec/manual_seed_sylk.py`: seed sylk:ID, sylk:C, sylk:F, sylk:E, sylk:W, sylk:B, sylk:NN, sylk:E-EOD (source: Microsoft SYLK spec)

##### TC-FF-AUDIT-060-D: Create Seeders for XML-Based Formats (Gnumeric, ABW)
**State:** TODO
**Micro-steps:**
- MS-060-D-1: `PENDING` Create `tools/spec/manual_seed_gnumeric.py`: seed key XML element names from Gnumeric format (gnumeric:Workbook, gnumeric:Sheet, gnumeric:Cells, gnumeric:Cell) (source: developer.gnome.org)
- MS-060-D-2: `PENDING` Create `tools/spec/manual_seed_abw.py`: seed abw:abiword, abw:section, abw:p, abw:c, abw:image (source: AbiWord format reference)

##### TC-FF-AUDIT-060-E: Create Seeders for Image Formats (QOI, PBM/PGM/PPM, XCF)
**State:** TODO
**Micro-steps:**
- MS-060-E-1: `PENDING` Create `tools/spec/manual_seed_qoi.py`: seed qoi:header, qoi:pixel-rgb, qoi:pixel-rgba, qoi:op-rgb, qoi:op-rgba, qoi:op-index, qoi:op-diff, qoi:op-luma, qoi:op-run, qoi:end-marker (source: phoboslab.org/qoi)
- MS-060-E-2: `PENDING` Create `tools/spec/manual_seed_pbm.py`, `manual_seed_pgm.py`, `manual_seed_ppm.py`: seed magic-number, width, height, maxval (pgm/ppm), pixel-data (source: netpbm.sf.net)
- MS-060-E-3: `PENDING` Create `tools/spec/manual_seed_xcf.py`: seed xcf:header, xcf:version, xcf:layer, xcf:channel, xcf:property, xcf:tile (source: gimp.org XCF spec)

##### TC-FF-AUDIT-060-F: Run All Seeders and Update SAL Cache
**State:** TODO
**Depends on:** TC-FF-AUDIT-060-A through TC-FF-AUDIT-060-E (all CLOSED)
**Validation:** All 14 non-ODF formats now have non-zero fact counts; total > 14,441
**Evidence:** Updated `.local/spec-cache/sal-facts-latest.json`
**Negative control:** ODF fact counts must NOT change (seeders only add new format facts)
**Micro-steps:**
- MS-060-F-1: `PENDING` Run `python tools/spec/merge_sal_facts.py` (or equivalent) to regenerate cache
- MS-060-F-2: `PENDING` Verify per-format counts: expect 3-50 facts per non-ODF format
- MS-060-F-3: `PENDING` Verify ODF counts unchanged
- MS-060-F-4: `PENDING` Update `sal-authority-audit.yaml` with new counts and pipeline_status: MANUALLY_SEEDED

---

#### TC-FF-AUDIT-061 [PARENT]: Fix Capability Feature Compiler
**State:** PROPOSED
**Priority:** P1
**Type:** FEATURE_COMPILER_REPAIR
**Lane:** feature_compiler_repair
**Dependency:** TC-FF-AUDIT-052 (CLOSED)
**Blocking:** TC-FF-AUDIT-080

**Children:**

##### TC-FF-AUDIT-061-A: Read and Compare Both Compiler Files
**State:** TODO
**Validation:** Root cause of near-zero output identified with specific line reference
**Micro-steps:**
- MS-061-A-1: `PENDING` Read `tools/supervisor/capability_feature_compiler.py` (canonical)
- MS-061-A-2: `PENDING` Read `tools/capability_layer/capability_to_feature_compiler.py` (planning tool — non-canonical)
- MS-061-A-3: `PENDING` Identify: deduplication issue, incorrect ledger path, or other bug causing zero output
- MS-061-A-4: `PENDING` Document root cause with file:line reference

##### TC-FF-AUDIT-061-B: Fix Canonical Compiler
**State:** TODO
**Depends on:** TC-FF-AUDIT-061-A (CLOSED)
**Validation:** Compiler produces ≥1 work item per format with open gaps in product-deepening-ledger
**Micro-steps:**
- MS-061-B-1: `PENDING` Apply minimal fix to `tools/supervisor/capability_feature_compiler.py`
- MS-061-B-2: `PENDING` Run compiler with product-deepening-ledger as input
- MS-061-B-3: `PENDING` Verify output: `next-work-items.json` has ≥1 item per open-gap format
- MS-061-B-4: `PENDING` Update `feature-register.yaml` with actual compiler output count

---

#### TC-FF-AUDIT-062 [PARENT]: QName Fact-Reference Backfill
**State:** PROPOSED
**Priority:** P2
**Type:** QNAME_REPAIR
**Lane:** qname_repair
**Dependency:** TC-FF-AUDIT-060 (CLOSED), TC-FF-AUDIT-020 (CLOSED)

**Children:**

##### TC-FF-AUDIT-062-A: Add source_fact_ids to All 79 QName Entries
**State:** TODO
**Validation:** All 79 entries in `registry/python-qname-architecture.json` have source_fact_ids field
**Micro-steps:**
- MS-062-A-1: `PENDING` Read current `registry/python-qname-architecture.json` (79 entries)
- MS-062-A-2: `PENDING` For each ODF qname: find matching SAL fact IDs from normalized-fact-register
- MS-062-A-3: `PENDING` For each non-ODF qname: reference the newly seeded SAL fact IDs from TC-FF-AUDIT-060
- MS-062-A-4: `PENDING` Add `source_fact_ids: [...]` and `derivation_method:` to each entry
- MS-062-A-5: `PENDING` Write updated `registry/python-qname-architecture.json`
- MS-062-A-6: `PENDING` Validate JSON parses; verify all 79 entries have source_fact_ids field

---

### Batch 7 — Representative Format Pilots

---

#### TC-FF-AUDIT-070 [PARENT]: ODF Pilot (FODS — Full Traceability Chain)
**State:** PROPOSED
**Priority:** P2
**Type:** PILOT
**Lane:** pilot_odf
**Dependency:** TC-FF-AUDIT-060 (CLOSED), TC-FF-AUDIT-062 (CLOSED)

**Children:**

##### TC-FF-AUDIT-070-A: Trace 3 FODS Capabilities End-to-End
**State:** TODO
**Validation:** For each of 3 capabilities: all edges from spec → oracle have confidence ≥ MEDIUM
**Micro-steps:**
- MS-070-A-1: `PENDING` Select 3 capabilities: LOAD, QUERY_CELL_VALUE, SAVE
- MS-070-A-2: `PENDING` LOAD: trace office:document RelaxNG element → SAL fact → qname → FodsDocument class → load test → oracle PASS
- MS-070-A-3: `PENDING` QUERY_CELL_VALUE: trace table:table-cell → SAL fact → qname → get_cell_value() → test → oracle PASS
- MS-070-A-4: `PENDING` SAVE: trace office:document → write_fods() → roundtrip test → oracle PASS
- MS-070-A-5: `PENDING` Write `reports/spec-to-code-forensic-audit/pilots/fods-pilot.yaml` with all edges

---

#### TC-FF-AUDIT-071 [PARENT]: Simple Text Pilot (CSV — RFC 4180 Chain)
**State:** PROPOSED
**Priority:** P2
**Type:** PILOT
**Lane:** pilot_text
**Dependency:** TC-FF-AUDIT-060 (CLOSED), TC-FF-AUDIT-062 (CLOSED)

**Children:**

##### TC-FF-AUDIT-071-A: Trace 3 CSV Capabilities After SAL Seeding
**State:** TODO
**Validation:** csv:record SAL fact exists; chain to test passes
**Micro-steps:**
- MS-071-A-1: `PENDING` Verify CSV SAL facts exist in updated sal-facts-latest.json
- MS-071-A-2: `PENDING` LOAD: RFC 4180 §2 → csv:record SAL fact → csv qname → parse() → oracle PASS
- MS-071-A-3: `PENDING` QUERY_ROW: csv:record → row property → test → oracle PASS
- MS-071-A-4: `PENDING` WRITE: csv:record → write_csv() → roundtrip → oracle PASS
- MS-071-A-5: `PENDING` Write `reports/spec-to-code-forensic-audit/pilots/csv-pilot.yaml`

---

#### TC-FF-AUDIT-072 [PARENT]: Binary Format Pilot (QOI — Spec Header Chain)
**State:** PROPOSED
**Priority:** P2
**Type:** PILOT
**Lane:** pilot_binary
**Dependency:** TC-FF-AUDIT-060 (CLOSED), TC-FF-AUDIT-062 (CLOSED)

**Children:**

##### TC-FF-AUDIT-072-A: Trace 3 QOI Capabilities After SAL Seeding
**State:** TODO
**Validation:** qoi:header SAL fact exists; chain to oracle passes
**Micro-steps:**
- MS-072-A-1: `PENDING` Verify QOI SAL facts exist
- MS-072-A-2: `PENDING` LOAD: QOI spec §2 → qoi:header SAL fact → qoi qname → load() → oracle PASS
- MS-072-A-3: `PENDING` DECODE_PIXELS: qoi:op-rgb/rgba → pixel list → test → oracle PASS
- MS-072-A-4: `PENDING` VALIDATE_MAGIC: qoi:header magic bytes → validate() → oracle PASS
- MS-072-A-5: `PENDING` Write `reports/spec-to-code-forensic-audit/pilots/qoi-pilot.yaml`

---

### Batch 8 — Portfolio Backfill and Product Healing

---

#### TC-FF-AUDIT-080 [PARENT]: Portfolio Backfill (All 14 Non-ODF Formats)
**State:** PROPOSED
**Priority:** P2
**Type:** PRODUCT_BACKFILL
**Lane:** backfill
**Dependency:** TC-FF-AUDIT-070 (CLOSED), TC-FF-AUDIT-071 (CLOSED), TC-FF-AUDIT-072 (CLOSED)

**Children:**

##### TC-FF-AUDIT-080-A: Update Code Traceability for All 14 Non-ODF Formats
**State:** TODO
**Validation:** All 14 formats have updated code-traceability-register entries with SAL fact links
**Micro-steps:**
- MS-080-A-1: `PENDING` For each of 14 non-ODF formats: update code-traceability-register.yaml entries
- MS-080-A-2: `PENDING` Link existing code symbols to newly seeded SAL facts from TC-FF-AUDIT-060
- MS-080-A-3: `PENDING` Update proof levels in feature-proof-register.yaml

##### TC-FF-AUDIT-080-B: Regenerate Pipeline Metrics
**State:** TODO
**Depends on:** TC-FF-AUDIT-080-A (CLOSED)
**Validation:** format-pipeline-metrics.csv shows non-zero spec_to_fact_ratio for all 20 Python formats
**Micro-steps:**
- MS-080-B-1: `PENDING` Recompute all conversion ratios with updated fact counts
- MS-080-B-2: `PENDING` Update `format-pipeline-metrics.csv` with before/after columns
- MS-080-B-3: `PENDING` Update `portfolio-pipeline-metrics.md` with after-repair aggregate

---

#### TC-FF-AUDIT-081 [PARENT]: Product-Specific Healing (Priority Gaps)
**State:** PROPOSED
**Priority:** P3
**Type:** PRODUCT_SPECIFIC_REPAIR
**Lane:** product_heal
**Dependency:** TC-FF-AUDIT-080 (CLOSED)
**GATE:** Only begins after Lanes 1-6 of spec-to-feature-radical-correction-plan.md are complete

**Children:**

##### TC-FF-AUDIT-081-A: Identify Priority STRUCTURAL_SHELL_ONLY Items
**State:** TODO
**Validation:** Priority list produced; only STRUCTURAL_SHELL_ONLY and STUB items in scope
**Micro-steps:**
- MS-081-A-1: `PENDING` Read code-traceability-register.yaml; filter to STRUCTURAL_SHELL_ONLY and STUB symbols
- MS-081-A-2: `PENDING` Cross-reference with product-deepening-ledger.yaml open gaps
- MS-081-A-3: `PENDING` Produce priority list (top 5 items by impact)

##### TC-FF-AUDIT-081-B: Execute Product Healing via Governed Skills
**State:** TODO
**Depends on:** TC-FF-AUDIT-081-A (CLOSED)
**Validation:** Each healed item passes oracle + focused test; code-change-ledger updated
**Micro-steps:**
- MS-081-B-1: `PENDING` For each priority item: run appropriate governed skill (/add-python-api, /add-dotnet-api, etc.)
- MS-081-B-2: `PENDING` Record each change in `reports/r90/product-code-change-ledger.json`
- MS-081-B-3: `PENDING` Run oracle for affected format; confirm PASS

---

### Batch 9 — Final Reaudit and Closure

---

#### TC-FF-AUDIT-090 [PARENT]: Post-Repair Reaudit and Portfolio Metrics Update
**State:** PROPOSED
**Priority:** P2
**Lane:** reaudit
**Dependency:** TC-FF-AUDIT-081 (CLOSED)

**Children:**

##### TC-FF-AUDIT-090-A: Remeasure All Pipeline Ratios
**State:** TODO
**Validation:** All 20 Python formats show non-zero spec_to_fact_ratio; delta tables complete
**Micro-steps:**
- MS-090-A-1: `PENDING` Recount SAL facts: expect >14,441 (new facts added by TC-FF-AUDIT-060)
- MS-090-A-2: `PENDING` Recount qname coverage: all 79 entries have source_fact_ids (from TC-FF-AUDIT-062)
- MS-090-A-3: `PENDING` Recount proof levels: all 20 Python at PROOF_LEVEL_3+
- MS-090-A-4: `PENDING` Compute delta per format: before_ratio vs after_ratio for all 9 pipeline ratios
- MS-090-A-5: `PENDING` Update `format-pipeline-metrics.csv` (final version with delta columns)
- MS-090-A-6: `PENDING` Update `portfolio-pipeline-metrics.md` with weighted aggregate improvement

---

#### TC-FF-AUDIT-091 [PARENT]: Taskcard Register and Execution Batch Register
**State:** PROPOSED
**Priority:** P2
**Lane:** closure
**Dependency:** TC-FF-AUDIT-090 (CLOSED)

**Children:**

##### TC-FF-AUDIT-091-A: Write Closure Ledger Files
**State:** TODO
**Validation:** All 3 YAML files parse; taskcard-register has all 23 parent TCs
**Evidence:** 3 files in `reports/spec-to-code-forensic-audit/`
**Micro-steps:**
- MS-091-A-1: `PENDING` Write `taskcard-register.yaml`: all parent TCs with final state and evidence refs
- MS-091-A-2: `PENDING` Write `execution-batch-register.yaml`: batches 0-9 with TC lists and completion timestamps
- MS-091-A-3: `PENDING` Write `execution-handoff.yaml`: any remaining work not completed in this mission

---

#### TC-FF-AUDIT-092 [PARENT]: Final Report and Idempotency Verdict
**State:** PROPOSED
**Priority:** P2
**Lane:** closure
**Dependency:** TC-FF-AUDIT-091 (CLOSED)
**Terminal:** After this TC closes → run `write_plan_lock.py --terminal`

**Children:**

##### TC-FF-AUDIT-092-A: Run Idempotency Check
**State:** TODO
**Validation:** Running all measurement reads a second time produces same counts (±0)
**Micro-steps:**
- MS-092-A-1: `PENDING` Re-read sal-facts-latest.json; confirm fact count unchanged
- MS-092-A-2: `PENDING` Re-read format-pipeline-metrics.csv; confirm ratios unchanged
- MS-092-A-3: `PENDING` Write `pipeline-idempotency-verdict.md`: STABLE or UNSTABLE with details

##### TC-FF-AUDIT-092-B: Write Final Report
**State:** TODO
**Depends on:** TC-FF-AUDIT-092-A (CLOSED)
**Validation:** final-report.md exists; contains all 15 sections from mission spec §34; final verdict on last line
**Evidence:** `reports/spec-to-code-forensic-audit/final-report.md`
**Micro-steps:**
- MS-092-B-1: `PENDING` Write 15-section final report (executive summary, scope, methodology, format inventory, spec sources, SAL audit, qname audit, capability audit, feature audit, code audit, proof audit, anomalies, root causes, repair plan, final verdict)
- MS-092-B-2: `PENDING` Final verdict line: one of prescribed vocabulary terms (expected: SPEC_TO_CODE_PIPELINE_AUDITED_HEALED_AND_PORTFOLIO_RECONCILED if all repairs complete, or TRACEABILITY_AUDIT_COMPLETE_MACHINERY_REPAIR_REQUIRED if some gaps remain)
- MS-092-B-3: `PENDING` Validate file exists and is non-empty
- MS-092-B-4: `PENDING` Run `write_plan_lock.py --plan-path plans/.claude/cheeky-crafting-manatee.md --terminal`
- MS-092-B-5: `PENDING` Report plan completion to user: "Plan cheeky-crafting-manatee complete. All 23 parent taskcards closed."

---

## PART VII: DEPENDENCY DAG AND PARALLEL SAFETY

### VII.1 Serial Dependencies (strict ordering required)

```
TC-001 → TC-002 → TC-010 → TC-011 → TC-020 → TC-030 → TC-031 → TC-040 → TC-041
TC-001 → TC-003 → TC-004
TC-041 → TC-050 → TC-051 → TC-052 → TC-053
TC-052 → TC-060, TC-061, TC-062 (can run in parallel after TC-052)
TC-060 → TC-062
TC-060 + TC-062 → TC-070, TC-071, TC-072 (can run in parallel)
TC-070 + TC-071 + TC-072 → TC-080 → TC-081 → TC-090 → TC-091 → TC-092
```

### VII.2 Parallel Execution Groups

| Group | TCs | Condition |
|---|---|---|
| G-A | TC-003, TC-004 | After TC-001 CLOSED (independent of TC-002) |
| G-B | TC-060, TC-061 | After TC-052 CLOSED (independent of each other) |
| G-C | TC-062 | After TC-060 CLOSED and TC-020 CLOSED |
| G-D | TC-070, TC-071, TC-072 | After TC-060, TC-062 CLOSED (all independent pilots) |

### VII.3 File Ownership (write conflicts prevented)

| File | Owner TC | Other TCs that READ |
|---|---|---|
| `registry/python-qname-architecture.json` | TC-062 (write) | TC-020 (read only) |
| `.local/spec-cache/sal-facts-latest.json` | TC-060 (write) | TC-010 (read only) |
| `format-pipeline-metrics.csv` | TC-050 (write), TC-080 (update), TC-090 (final update) | All analysis TCs read |
| `code-traceability-register.yaml` | TC-040 (write), TC-080 (update) | TC-041, TC-050 read |
| `sal-authority-audit.yaml` | TC-010 (write), TC-060 (update) | All audit TCs read |

**Conflict rule:** No two TCs in parallel groups may write the same file. Verify before parallel execution.

---

## PART VIII: VALIDATION MATRIX

| Taskcard | Positive Validation | Negative Control | Failure Action |
|---|---|---|---|
| TC-001 | forensic-baseline.yaml parses as valid YAML | File must NOT exist before MS-001-C-1 | Delete stale artifact; re-run |
| TC-002 | format-inventory.yaml has exactly 24 entries | ora/pam/xpm/zpaq must NOT be CODE_PARTIAL | Reclassify to SPEC_ONLY; re-validate |
| TC-003 | Every format has ≥1 spec reference | No format may have source_references: [] | Add PAGE_ESTIMATE entry; mark gap |
| TC-004 | Every spec has semantic_units > 0 OR counting_method: PAGE_ESTIMATE | No format may have semantic_units: null | Add PAGE_ESTIMATE + note limitations |
| TC-010 | ODF fact count ≥ 13000 | Non-ODF formats must NOT show PIPELINE_WORKING | Override to MANUALLY_SEEDED |
| TC-020 | All 79 qnames have classification field | No non-ODF qname classified COMPLETE_AND_VALID with 0 facts | Reclassify; re-validate |
| TC-050 | anomaly-register has ≥5 anomalies | Register must NOT be empty | Investigate suppression; add anomalies |
| TC-060 | All 14 non-ODF formats have >0 facts after seeders | ODF fact counts must NOT decrease | Check for accidental deletion; restore |
| TC-061 | Compiler produces ≥1 work item per open-gap format | Output must NOT be empty | Debug RC-004; fix dedup logic |
| TC-062 | All 79 qname entries have source_fact_ids field | No qname may have source_fact_ids: [] | Match to seeded facts; add entries |
| TC-092 | final-report.md has final verdict on last line | Verdict must come from prescribed vocabulary | Replace with correct term |

---

## PART IX: EVIDENCE CONTRACT AND OBLIGATION MATRIX

### IX.1 Artifact Obligation Matrix

| Artifact | Producing TC | Consuming TCs | Format | Required By |
|---|---|---|---|---|
| forensic-baseline.yaml | TC-001 | All TCs | YAML | Before any analysis |
| format-inventory.yaml | TC-002 | TC-010, TC-020, TC-030, TC-050 | YAML | Batch 1+ |
| specification-source-inventory.yaml | TC-003 | TC-004, TC-011, TC-060 | YAML | Batch 1+ |
| specification-measurement-register.yaml | TC-004 | TC-011, TC-050 | YAML | Batch 1+ |
| normalized-fact-register.yaml | TC-010 | TC-011, TC-020, TC-030 | YAML | Batch 2+ |
| sal-authority-audit.yaml | TC-010 (write), TC-060 (update) | TC-020, TC-050 | YAML | Batch 2+ |
| raw-spec-unit-register.yaml | TC-011 | TC-020, TC-050 | YAML | Batch 2+ |
| qname-traceability-register.yaml | TC-020 | TC-030, TC-050, TC-062 | YAML | Batch 3+ |
| capability-register.yaml | TC-030 | TC-031, TC-050 | YAML | Batch 3+ |
| feature-register.yaml | TC-031, TC-061 | TC-040, TC-050 | YAML | Batch 4+ |
| code-traceability-register.yaml | TC-040, TC-080 | TC-041, TC-050 | YAML | Batch 4+ |
| feature-proof-register.yaml | TC-041, TC-080 | TC-050, TC-090 | YAML | Batch 5+ |
| format-pipeline-metrics.csv | TC-050, TC-080, TC-090 | TC-051, TC-091 | CSV | Final |
| portfolio-pipeline-metrics.md | TC-050, TC-080, TC-090 | TC-091, TC-092 | MD | Final |
| pipeline-anomaly-register.yaml | TC-050 | TC-051 | YAML | Batch 5+ |
| root-cause-register.yaml | TC-051 | TC-052, TC-092 | YAML | Batch 5+ |
| fix-option-register.yaml | TC-052 | TC-060, TC-061 | YAML | Batch 6 |
| chosen-repair-plan.md | TC-052 | TC-060, TC-061 | MD | Batch 6 |
| spec-to-code-traceability-graph.yaml | TC-053 | TC-092 | YAML | Final |
| pilots/fods-pilot.yaml | TC-070 | TC-080, TC-092 | YAML | Batch 8 |
| pilots/csv-pilot.yaml | TC-071 | TC-080, TC-092 | YAML | Batch 8 |
| pilots/qoi-pilot.yaml | TC-072 | TC-080, TC-092 | YAML | Batch 8 |
| taskcard-register.yaml | TC-091 | TC-092 | YAML | Final |
| execution-batch-register.yaml | TC-091 | TC-092 | YAML | Final |
| execution-handoff.yaml | TC-091 | External | YAML | Final |
| pipeline-idempotency-verdict.md | TC-092 | External | MD | Final |
| final-report.md | TC-092 | External | MD | Terminal |

### IX.2 Evidence Path Convention

All artifacts: `reports/spec-to-code-forensic-audit/{artifact-name}`
Pilot artifacts: `reports/spec-to-code-forensic-audit/pilots/{format}-pilot.yaml`
Session evidence: `.local/evidences/{run_id}/evidence-declaration.yaml`
Product code changes (Batch 8 only): `reports/r90/product-code-change-ledger.json`

---

## PART X: QUALITY SCORING RULES

### X.1 Scoring Dimensions (5 dimensions, each 1-5)

| # | Dimension | Weight | Reroute Trigger |
|---|---|---|---|
| 1 | Completeness | 1x | Score < 4 |
| 2 | Accuracy | 2x | Score < 4 |
| 3 | Traceability | 2x | Score < 4 |
| 4 | Idempotency | 1x | Score < 4 |
| 5 | Evidence | 1x | Score < 4 |

**Weighted score = (C×1 + A×2 + T×2 + I×1 + E×1) / 7**
**Pass threshold: weighted score ≥ 4.0 AND no individual dimension < 3**

### X.2 Reroute Rules

1. **On any dimension < 4:** Open a REROUTED child TC with the specific remediation action.
2. **Remediation TC naming:** `TC-FF-AUDIT-{parent}-RW{n}` where n is the reroute count (e.g., TC-FF-AUDIT-010-RW1)
3. **Max reroutes:** 2 per parent TC before escalating to user.
4. **Reroute does not block other TCs** unless the parent TC is in the dependency chain of blocked TCs.

### X.3 Auto-Pass Conditions

These conditions skip full scoring and auto-pass (score 5/5 for all dimensions):
- Artifact is a read-only register with no computed values (e.g., specification-source-inventory.yaml with external URLs only)
- Artifact is explicitly marked `best_effort: true` in its obligation matrix entry

---

## PART XI: RECONCILIATION AND IDEMPOTENCY

### XI.1 Idempotency Protocol

After TC-FF-AUDIT-090 completes, run TC-FF-AUDIT-092-A (idempotency check):
1. Re-read all produced artifacts without modifications
2. Re-compute all conversion ratios
3. Verify: ratio values match to within ±0 (integer counts) or ±0.001 (float ratios)
4. If any ratio drifts: classify as UNSTABLE and investigate before closing

### XI.2 Reconciliation Checkpoints

| After Batch | What to Reconcile |
|---|---|
| Batch 0 | forensic-baseline.yaml fact counts vs actual JSON counts |
| Batch 1 | normalized-fact-register fact counts vs sal-facts-latest.json |
| Batch 2 | qname-traceability-register count (must be 79) vs registry entry count |
| Batch 5 | All conversion ratios: confirm ODF spec_to_fact != non-ODF spec_to_fact |
| Batch 6 | Before/after fact counts: expect all 14 non-ODF formats to show increase |
| Batch 9 | Final ratio stability: all ratios identical on second measurement |

---

## PART XII: EXECUTION HANDOFF

### XII.1 Step-by-Step Execution Protocol

1. **Session start:** Read CLAUDE.md Step 0; verify vast-weaving-lampson is TERMINAL_CLOSED
2. **Plan lock:** Run `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/cheeky-crafting-manatee.md`
3. **Migrate plan (if not done):** Copy `C:\Users\prora\.claude\plans\cheeky-crafting-manatee.md` → `plans/.claude/cheeky-crafting-manatee.md` and redirect lock
4. **Execute Batch 0:** TC-001 → TC-002 → TC-003+TC-004 (parallel) — write all 4 baseline artifacts
5. **Execute Batch 1:** TC-010 → TC-011 — write SAL audit artifacts
6. **Execute Batch 2:** TC-020 — write qname traceability
7. **Execute Batch 3:** TC-030 → TC-031 — write capability and feature registers
8. **Execute Batch 4:** TC-040 → TC-041 — write code and proof registers
9. **Execute Batch 5:** TC-050 → TC-051 → TC-052 → TC-053 — write analysis artifacts
10. **Execute Batch 6:** TC-060 + TC-061 (parallel) → TC-062 (after TC-060) — repair machinery
11. **Execute Batch 7:** TC-070 + TC-071 + TC-072 (parallel) — run pilots
12. **Execute Batch 8:** TC-080 → TC-081 — backfill and heal
13. **Execute Batch 9:** TC-090 → TC-091 → TC-092 — reaudit, close, write final report
14. **Terminal:** `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/cheeky-crafting-manatee.md --terminal`
15. **Report:** "Plan cheeky-crafting-manatee complete. All 23 parent taskcards closed. Awaiting next instruction."

### XII.2 Per-Session Resume Protocol

If session breaks mid-execution:
1. Read this plan file; find lowest-numbered parent TC that is NOT `VERIFIED` or `CLOSED`
2. Read all artifact files that are already produced (to avoid re-doing work)
3. Resume from the first incomplete child TC of the first incomplete parent TC
4. Do NOT restart from TC-FF-AUDIT-001 if artifacts already exist — check and validate existing artifacts first

### XII.3 Execution Handoff YAML Location

On closure: `reports/spec-to-code-forensic-audit/execution-handoff.yaml`
Contains: remaining_work[], blockers[], recommended_next_session, produced_artifacts[], final_state

---

## Governance Rules (Non-Negotiable)

1. No product source (`src/python/`, `src/net/`) changes in Batches 0-5 (analysis only)
2. All `src/` changes in Batch 8 must use governed skills and be recorded in product-code-change-ledger
3. `spec-to-feature-radical-correction-plan.md` is the binding authority — this plan is subordinate
4. If any taskcard conflicts with the correction plan, the correction plan wins
5. POST_PLAN_TERMINAL applies at final TC-FF-AUDIT-092 completion — STOP and report to user
6. Batch 8 (TC-081) is gated on correction plan Lanes 1-6 being complete
7. Parallel groups (G-A, G-B, G-C, G-D) may execute concurrently only if file ownership is verified

## Known Risk: ODF Qname Collapse

ODF has ~4,988 FODS SAL facts → 12 FODS qnames. This 0.2% collapse is INTENTIONAL_ARCHITECTURE_DECISION.
Do NOT interpret this as a gap requiring all 4,988 qnames to be created. Document as architecture decision in root-cause-register RC-002. The qname model is semantic grouping, not 1:1 spec element mapping.
