# FODS Product-Code Governance — Production Incident: Full Execution Plan
# Plan ID: splendid-squishing-orbit
# Type: machinery_hardening
# Authority: SINGLE AUTHORITATIVE PLAN — all execution agents must read this file only
# Version: 3.0 (micro-taskcardized, machine-state hardened)
# Last enhanced: 2026-07-10

authoritative_plan: plans/.claude/splendid-squishing-orbit.md
execution_authority: true
supporting_artifacts_root: reports/product-quality/fods-govheal/

---

# PART I — PREFLIGHT AND AUTHORITY

## Repository Preflight

```
Repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
Branch: main
Plan path: plans/.claude/splendid-squishing-orbit.md  (migrated from external at session start)
Plan authority source: CLAUDE.md Step 0 + session message
Format: Markdown with embedded YAML state blocks
Sections: 10 parts, 25 parent taskcards, ~100 child taskcards, ~400 micro-steps
State vocabulary: PROPOSED | READY | IN_PROGRESS | CHILDREN_IN_PROGRESS | INTEGRATION_PENDING
                  VERIFIED | SCORED | CLOSED | BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON
Duplicate plan risk: NONE — only this file is authoritative; no v2/final/revised copies exist
```

## Corrections to First Pass (preserved)

| First-pass claim | Actual state |
|---|---|
| FodsDocumentExtendedApis.cs was removed | **File still exists in HEAD** |
| Gap ledger entries are for removed files | **Files still exist**; ledger references match filesystem |
| ~4 remnant dict fields | **43 dict fields** across the partial class |
| No roundtrip tests exist | **FodsGI001CategoryBRoundtripTests.cs has 10 real Save/Load tests** — correct, preserve |
| Validators V88/V90/V104/V108 missing | **All exist** — but V88 has ~70-80% false-negative rate; V90/V91 warn-only; V87 exempts PRODUCT_SOURCE |

---

# PART II — ANALYSIS (PRESERVED)

## Actual State (Ground Truth)

### The Stub Landscape

**FodsDocumentExtendedApis.cs** (in HEAD, ~1556 LOC, ~194 public methods):
Partially migrated — some methods now delegate to XML-backed paths; some still write to dicts only.

**43 dict fields across the FodsDocument partial class** in three categories:

**Category B** (dict cache + XML grounding, partially remediated):
18 cell-styling fields — alignment, font, color, underline, rotation, indent, border, shrink-to-fit,
strikethrough. GAP-NET-XG-010/011/012 claim CLOSED. Roundtrip tests exist in
FodsGI001CategoryBRoundtripTests.cs (10 tests). Verification needed that tests exercise XML paths,
not dict paths.

**COLLECTION_STUB** (dict-only, ODF target identified, "deferred indefinitely"):
- `_filters` / `_allFilterRanges` — ODF: `table:database-range` (§9.5.2)
- `_pageBreaks` — ODF: `table:table-row/@fo:break-before` (§9.4.4)
- `_groups` — ODF: `table:row-group` (§9.4.2)
- `_sheetProtection` / `_sheetProtectionPasswords` — ODF: `table:table-protection`

**TODO(GI-FODS-NET-NNN)** (in-memory only, no persistence):
- GI-003: `_sheetProtection` password (SHA256 hash)
- GI-006: `_charts` — chart:chart objects
- GI-007: `_conditionalFormats` — ODF §11.6
- GI-008: `_dataValidations` — ODF §11.4
- GI-009: `_cellHyperlinks` / `_hyperlinks` — text:a
- GI-010: `_rowHeights` — table:table-row/@table:default-row-height
- GI-011: `_namedRanges` — table:named-expressions/table:named-range
- GI-012: `_sheetPivotTables` / `_pivotTables` / `_sheetSparklines` / `_sparklines`

**One hardcoded false return:**
`GetSheetRightToLeft()` → `return false;` always. Comment correctly notes no ODF config path.

### Governance Failure Analysis

**V88** (`validate_dotnet_detached_dictionary_fields`): File-wide proximity heuristic.
If dict field + ANY XML pattern exist in same file → PASS. In FodsDocumentReadOps.cs,
`_rowHeights`, `_namedRanges`, `_cellComments` (dict-only) coexist with `RestoreFilterStateFromDocument()`
(XML parsing). V88 passes silently. **Estimated false-negative rate: ~70-80% for mixed partial-class files.**

**V87** (`validate_dotnet_constant_return_public_api`): WARN for PRODUCT_SOURCE; FAIL+blocks_sprint
only for RELEASE_GATE. Gate 11 requires Babar Raza → RELEASE_GATE is never reached autonomously.
**Effect: constant-return public methods are permanently permitted in product code.**

**V90/V91** (`setter_without_xml_write` / `getter_without_xml_read`): Both `blocks_sprint=False`.
Fires WARNs that the loop logs and ignores.

**Whitelist** (`registry/dotnet-semantic-stub-whitelist.yaml`): Bypasses V87 detection.
No review date, no expiry, no approver audit trail. Any method can be exempted.

**Task generation** (`autonomous_task_generator.py`): `_EXPANSION_GOALS` uses
`"spec_authority": "schema_authority_available"` as a free-form unvalidated string. No `spec_fact_id`
or `odf_qname` required. "implement GetChartTitle" can be tasked without spec grounding.

**Oracle D1**: Measures "expected properties == observed properties". Does not record data source.
A getter returning from `_charts[sheetName][0].Title` scores D1 identically to one parsing XML.

**Sprint acceptance**: `sprint_executor_validate.py` does not require Save/Load evidence for
PERSISTENT_PROPERTY items. "1571 tests passing" is accepted without test-quality classification.

## Symptoms, Root Causes, and Structural Weaknesses

### Symptoms
- 43 dict fields across the partial class
- 9 GI-FODS-NET-* TODO items with no persistence
- 8 COLLECTION_STUB markers with "XML write deferred"
- `GetSheetRightToLeft()` always returns false
- PCG-006/007 OPEN for months without enforcement
- Sprints accepted despite WARN-only validator fires

### Root Causes
1. Three named stub categories create permanent managed debt — tracked but never blocked
2. V88 ~70-80% false-negative in mixed files — proximity heuristic cannot isolate per-setter violations
3. V87 PRODUCT_SOURCE exemption is effectively permanent — RELEASE_GATE unreachable autonomously
4. V90/V91 warn-only — dict-backed setters/getters never blocked
5. Whitelist is ungoverned — any method exempted without review
6. Task generation requires no spec grounding — speculative APIs generated freely
7. Oracle D1 proves comparison, not data provenance

### Structural Weaknesses
1. "Best-effort closeout" doctrine — failing validators silently skipped
2. No persistent-property test requirement in sprint validator
3. Gap ledger write-only — no machine reconciliation with current code topology
4. PRODUCT_SOURCE/RELEASE_GATE split creates permanent two-class system
5. "Deferred" has no enforcement mechanism — COLLECTION_STUB can age indefinitely

## What to Preserve vs Redesign

### Preserve
| What | Why |
|---|---|
| XDocument DOM backend | Correct; proven by roundtrip tests |
| FodsStyleResolver / FodsStyleEditor | Correct separation; model for XML grounding |
| spec_qname constants in Model/ classes | Correct spec alignment |
| Security hardening (DTD prohibition, 50 MB limit) | Non-negotiable |
| Roundtrip test pattern in FodsGI001CategoryBRoundtripTests.cs | 10 real Save/Load tests; right pattern |
| Oracle framework and depth-level concept | Right abstraction, wrong measurement |
| V89 (suspicious filename) + V78 (LOC cap) | Working and effective |
| Gap ledger YAML structure | Right format; needs live reconciliation |
| `capability_feature_compiler.py` QName validation | Keep and strengthen |

### Must Redesign
| What | Root cause addressed | Risk of keeping |
|---|---|---|
| V88 file-proximity heuristic | RC-2 | Dict state never caught |
| V87 PRODUCT_SOURCE exemption | RC-3 | False behavior in production |
| V90/V91 warn-only | RC-4 | Dict APIs accumulate indefinitely |
| Whitelist ungoverned | RC-5 | Validators silently nullified |
| Three stub categories | RC-1 | Managed debt with no deadline |
| Task generation without spec ground | RC-6 | Speculative API surface grows |
| Oracle D1 without data provenance | RC-7 | Quality scores misleading |
| Sprint acceptance without roundtrip proof | SW-2 | False closure |

## Solution Design

### Core Principle
**Binary contract** for every public API:
```
IMPLEMENTED:  getter reads from XElement | setter writes to XElement | roundtrip test proves it
UNSUPPORTED:  throws NotSupportedException | test proves the exception | comment cites ODF section
```
No Category B, no COLLECTION_STUB, no TODO(GI-*). Not IMPLEMENTED → UNSUPPORTED. Not "deferred."

## Tradeoffs and Known Limits

**T1**: V87 blocking PRODUCT_SOURCE eliminates phased development via `return false;`. Devs must
choose IMPLEMENTED or UNSUPPORTED now. Intentional — eliminates the Category B on-ramp.

**T2**: V88 per-method analysis misses helper-method delegation (e.g., `_WriteProtectionXml(_field)`).
Accepted residual false-positive rate ~15% — far better than current ~70-80% false-negative.

**T3**: Abolishing COLLECTION_STUB requires implementing or removing 5+ features immediately.
Some features become UNSUPPORTED temporarily — honest degradation replacing silent data loss.

**T4**: Oracle data_source cannot be auto-verified without instrumentation. Process-enforced, not
machine-enforced. Requires declaration + reviewer check.

**T5**: 25 parent taskcards cannot complete in one sprint — 5-6 sprints estimated. Governance (Lane B)
must go first so future stubs are caught even if all existing ones aren't fixed yet.

**R1**: GI-009 hyperlinks — text:a inside text:p may break preservation tests. Add preservation
test before implementing.
**R2**: Filter XML must match LibreOffice table:database-range structure exactly.
**R3**: Removing dict-backed APIs is a breaking change for consumers using them.
**R4**: V88 per-method parsing adds 2-5 seconds to validator run. Accept this.
**R5**: 87+ blocking validators risk validator fatigue. Improve accuracy, don't just add more.

**L1** (Known Limit): This plan cannot force RELEASE_GATE approval. Babar Raza sign-off is external.
**L2**: Oracle data_source provenance is process-enforced. A bad actor can declare parsed for dict data.
**L3**: Cross-product scan is heuristic — false positives require human review.
**L4**: V88 cannot trace through helper method calls. Helper delegation is an accepted false-negative.
**L5**: Charts, pivot tables, sparklines, conditional formats become explicitly UNSUPPORTED.

---

# PART III — REQUIREMENTS INVENTORY

| REQ ID | Description | Lane | Parent Taskcards |
|---|---|---|---|
| REQ-FGSQ-001 | Complete method-level incident record for ExtendedApis.cs | A | TC-001 |
| REQ-FGSQ-002 | Gap ledger references match current code topology | A | TC-002 |
| REQ-FGSQ-003 | V88 per-method detection accuracy ≥85% recall | B | TC-003 |
| REQ-FGSQ-004 | V87 blocks PRODUCT_SOURCE constant-return methods | B | TC-004 |
| REQ-FGSQ-005 | V90/V91 block dict-backed setter/getter sprint closure | B | TC-005 |
| REQ-FGSQ-006 | Whitelist entries have expiry dates, reviewed quarterly | B | TC-006 |
| REQ-FGSQ-007 | Oracle D1 requires data_source=parsed declaration | B | TC-007 |
| REQ-FGSQ-008 | Sprint validator requires roundtrip proof for PERSISTENT_PROPERTY | B | TC-008 |
| REQ-FGSQ-009 | COLLECTION_STUB comment pattern blocks sprint on new occurrences | B | TC-009 |
| REQ-FGSQ-010 | Task generation requires spec_fact_id or odf_qname or UNSUPPORTED | B | TC-010 |
| REQ-FGSQ-011 | Gap ledger drift reported per autonomous cycle | B | TC-011 |
| REQ-FGSQ-012 | All COLLECTION_STUB methods: IMPLEMENTED or UNSUPPORTED | C | TC-012 |
| REQ-FGSQ-013 | All TODO(GI-FODS-NET-*) stubs: IMPLEMENTED or UNSUPPORTED | C | TC-013 |
| REQ-FGSQ-014 | Category B dict fields verified as XML-backed (not dict-backed) | C | TC-014 |
| REQ-FGSQ-015 | GetSheetRightToLeft throws NotSupportedException | C | TC-015 |
| REQ-FGSQ-016 | FodsDocumentExtendedApis.cs absent from HEAD | C | TC-016 |
| REQ-FGSQ-017 | FodsDocument.cs and FodsDocumentReadOps.cs each ≤800 LOC | C | TC-017 |
| REQ-FGSQ-018 | Python FODS PCG-003/004/005 closed | D | TC-018 |
| REQ-FGSQ-019 | No test asserts only a dict-backed default without roundtrip | E | TC-019 |
| REQ-FGSQ-020 | Roundtrip tests exist for every newly-IMPLEMENTED capability | E | TC-020 |
| REQ-FGSQ-021 | All .NET product libraries scanned for semantic-stub patterns | F | TC-021 |
| REQ-FGSQ-022 | All Python product libraries scanned for semantic-stub patterns | F | TC-022 |
| REQ-FGSQ-023 | Gate 11 criteria referencing stub-backed capabilities reopened | G | TC-023 |
| REQ-FGSQ-024 | All 10 required pilots executed and recorded | H | TC-024 |
| REQ-FGSQ-025 | All required counters = 0 on two consecutive runs (idempotent) | H | TC-025 |

---

# PART IV — EXECUTION CONTROL: TASKCARDS

## Taskcard State Vocabulary

**Parent states:** PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED | BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

**Child states:** TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED | REROUTED | BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

**Micro-step states:** PENDING → READY → ACTIVE → COMPLETE | FAILED | BLOCKED | SKIPPED_NOT_APPLICABLE

**Invalid transitions (hard-blocked):**
- Child TODO → CLOSED (must pass through IMPLEMENTED + VERIFIED)
- Child IMPLEMENTED → CLOSED (must be VERIFIED + SCORED first)
- Parent CLOSED while any mandatory child is not CLOSED
- REROUTED → CLOSED without documented rework evidence
- Any taskcard CLOSED without evidence artifact recorded

---

## Lane A — Incident Capture and Gap Ledger Repair

> **Gate A:** Lane A must reach CLOSED before Lane B work items may proceed to INTEGRATION_PENDING.
> Lane A is read-only for product source code.

---

### TC-FGSQ-001 — Build Method Ledger for FodsDocumentExtendedApis.cs
**Status:** PROPOSED | **Type:** PARENT | **Lane:** A
**REQ:** REQ-FGSQ-001 | **Owner:** Quality Engineer | **Supervisor:** Governance Lead
**Dependencies:** None | **Blocks:** TC-FGSQ-012, TC-FGSQ-013, TC-FGSQ-014
**Scope:** Read-only. All files in `src/net/fods/`. No product source modification.

**Objective:** Produce a complete, disposition-assigned ledger of every public method and dict field in FodsDocumentExtendedApis.cs and all partial-class files it touches.

**Outcome:** `reports/product-quality/fods-missing-methods-origin.yaml` exists with zero unclassified methods.

**Children:**
- TC-FGSQ-001-01: Read and inventory all public methods in ExtendedApis.cs
- TC-FGSQ-001-02: Trace each getter — dict source vs XElement source
- TC-FGSQ-001-03: Trace each setter — dict write vs SetAttributeValue write
- TC-FGSQ-001-04: Assign disposition to each method
- TC-FGSQ-001-05: Write fods-missing-methods-origin.yaml

**Parent acceptance criteria:**
- fods-missing-methods-origin.yaml exists at `reports/product-quality/`
- UNCLASSIFIED_METHODS = 0
- Every method assigned one of: IMPLEMENTED_VERIFY | COLLECTION_STUB_DECIDE | TODO_STUB_DECIDE | HARDCODED_FALSE

**Integration checks:** TC-FGSQ-002 can reference the same files without conflict.

**Evidence required:** fods-missing-methods-origin.yaml (content, not just path)

**Rollback:** Discard the YAML; no code changes occurred.

---

#### TC-FGSQ-001-01 — Read and inventory all public methods in ExtendedApis.cs
**Status:** TODO | **Parent:** TC-FGSQ-001
**Allowed files:** `src/net/fods/FodsDocumentExtendedApis.cs` — read-only
**Preconditions:** ExtendedApis.cs exists in HEAD

**Micro-steps:**
- MS-001-01-01: Read `src/net/fods/FodsDocumentExtendedApis.cs` completely → record total LOC
- MS-001-01-02: Extract all `public` method signatures (name, parameter types, return type, line number) → create raw list
- MS-001-01-03: Count total public methods → compare with known ~194; record discrepancy if any
- MS-001-01-04: Extract all `private.*Dictionary<` field declarations → create separate raw list
- MS-001-01-05: Record findings in working artifact `method-inventory-raw.yaml` under `reports/product-quality/fods-govheal/`

**Evidence:** method-inventory-raw.yaml with method signatures and dict fields
**Completion check:** method-inventory-raw.yaml exists; method count is N > 0; zero fields marked "unknown"
**Next valid task:** TC-FGSQ-001-02

---

#### TC-FGSQ-001-02 — Trace each getter to dict vs XElement
**Status:** TODO | **Parent:** TC-FGSQ-001
**Allowed files:** All `src/net/fods/*.cs` — read-only
**Preconditions:** TC-FGSQ-001-01 CLOSED

**Micro-steps:**
- MS-001-02-01: For each `GetXxx` method in method-inventory-raw.yaml: read method body
- MS-001-02-02: Check if method body contains `_\w+\[` (dict read) → record YES/NO per method
- MS-001-02-03: Check if method body contains `.Attribute(` or `.Element(` or `.Value` (XElement read) → record YES/NO
- MS-001-02-04: Check if method delegates to FodsStyleResolver or FodsStyleEditor → record YES/NO
- MS-001-02-05: Record getter source classification: XML_BACKED | DICT_ONLY | MIXED | HELPER_DELEGATED | CONSTANT | UNKNOWN

**Evidence:** getter-trace-results.yaml appended to working artifact
**Completion check:** Every getter has a source classification; UNKNOWN = 0
**Next valid task:** TC-FGSQ-001-03

---

#### TC-FGSQ-001-03 — Trace each setter to dict vs SetAttributeValue
**Status:** TODO | **Parent:** TC-FGSQ-001
**Allowed files:** All `src/net/fods/*.cs` — read-only
**Preconditions:** TC-FGSQ-001-01 CLOSED

**Micro-steps:**
- MS-001-03-01: For each `SetXxx` method: read method body
- MS-001-03-02: Check if body contains `_\w+\[.*\] =` (dict write) → record YES/NO
- MS-001-03-03: Check if body contains `SetAttributeValue(` or `.Add(new XElement(` → record YES/NO
- MS-001-03-04: Check if body delegates to FodsStyleEditor.SetXxx → record YES/NO
- MS-001-03-05: Record setter write classification: XML_BACKED | DICT_ONLY | MIXED | HELPER_DELEGATED | UNKNOWN

**Evidence:** setter-trace-results.yaml appended to working artifact
**Completion check:** Every setter has a write classification; UNKNOWN = 0
**Next valid task:** TC-FGSQ-001-04

---

#### TC-FGSQ-001-04 — Assign disposition to each method
**Status:** TODO | **Parent:** TC-FGSQ-001
**Preconditions:** TC-FGSQ-001-02 and TC-FGSQ-001-03 both CLOSED

**Disposition rules:**
```
getter=XML_BACKED  + setter=XML_BACKED  → IMPLEMENTED_VERIFY
getter=DICT_ONLY   OR setter=DICT_ONLY  → COLLECTION_STUB_DECIDE (if ODF QName known) or TODO_STUB_DECIDE
getter=CONSTANT    (return false/null/0) → HARDCODED_FALSE
getter=MIXED       or setter=MIXED      → MANUAL_DOMAIN_DECISION_REQUIRED
```

**Micro-steps:**
- MS-001-04-01: Apply disposition rules to each method using getter-trace + setter-trace → record disposition
- MS-001-04-02: For COLLECTION_STUB_DECIDE: record the ODF QName and spec section reference
- MS-001-04-03: For TODO_STUB_DECIDE: record the GI-FODS-NET-NNN tracking comment
- MS-001-04-04: For MANUAL_DOMAIN_DECISION_REQUIRED: record reasoning for human review
- MS-001-04-05: Count methods per disposition → verify sum equals total method count

**Evidence:** disposition-assignment.yaml with per-method disposition
**Completion check:** Sum of all disposition counts = total method count; UNCLASSIFIED = 0
**Next valid task:** TC-FGSQ-001-05

---

#### TC-FGSQ-001-05 — Write fods-missing-methods-origin.yaml
**Status:** TODO | **Parent:** TC-FGSQ-001
**Preconditions:** TC-FGSQ-001-04 CLOSED
**Allowed files:** `reports/product-quality/fods-missing-methods-origin.yaml` — create/write

**Micro-steps:**
- MS-001-05-01: Assemble fods-missing-methods-origin.yaml from working artifacts:
  fields: incident_id, product, language, offending_file, introducing_task_ids, methods[], counters
- MS-001-05-02: For each method entry include: symbol, getter_source, setter_source, disposition, odf_qname_or_na, gap_ids
- MS-001-05-03: Add summary counters: total_methods, by_disposition (IMPLEMENTED_VERIFY, etc.)
- MS-001-05-04: Write file to `reports/product-quality/fods-missing-methods-origin.yaml`
- MS-001-05-05: Verify file parseable as YAML and counters are consistent

**Evidence:** Path and SHA-256 of fods-missing-methods-origin.yaml
**Completion check:** File exists; YAML parses; UNCLASSIFIED_METHODS = 0 per counters
**Next valid task:** TC-FGSQ-002-01

---

### TC-FGSQ-002 — Reconcile Gap Ledger to Current Code Topology
**Status:** PROPOSED | **Type:** PARENT | **Lane:** A
**REQ:** REQ-FGSQ-002 | **Owner:** Quality Engineer | **Supervisor:** Governance Lead
**Dependencies:** None (can run in parallel with TC-FGSQ-001) | **Blocks:** TC-FGSQ-011
**Scope:** Read `reports/product-quality/product-code-gap-ledger.yaml` and update `files:` and metadata only. Do NOT change `status:` fields.

**Objective:** Update all OPEN gap entries so their `files:` lists reference files that currently exist and accurately reflect where the gap manifests in today's code.

**Outcome:** Every OPEN gap's `files:` list contains only paths that exist in the filesystem.

**Children:**
- TC-FGSQ-002-01: Read complete gap ledger and record all OPEN entries
- TC-FGSQ-002-02: For each OPEN entry: verify each listed file exists
- TC-FGSQ-002-03: Update PCG-006/007 files: lists to all current partial-class files
- TC-FGSQ-002-04: Map each GI-FODS-NET-* comment to current file and line number
- TC-FGSQ-002-05: Add reconciled_at timestamp to each updated entry

**Parent acceptance criteria:**
- Zero OPEN gap entries have `files:` referencing non-existent paths
- Each gap entry has `reconciled_at` field
- Gap statuses unchanged (no OPEN → CLOSED transitions in this task)

**Evidence:** Updated product-code-gap-ledger.yaml with diff showing reconciled entries

**Rollback:** `git restore reports/product-quality/product-code-gap-ledger.yaml`

---

#### TC-FGSQ-002-01 — Read complete gap ledger
**Status:** TODO | **Parent:** TC-FGSQ-002
**Allowed files:** `reports/product-quality/product-code-gap-ledger.yaml` — read-only

**Micro-steps:**
- MS-002-01-01: Read product-code-gap-ledger.yaml completely
- MS-002-01-02: Extract all gaps with `status: OPEN` → list gap_ids
- MS-002-01-03: For each OPEN gap: record its `files:` list
- MS-002-01-04: Record total open gap count

**Evidence:** OPEN gap list with file references
**Completion check:** All OPEN gaps listed; file references recorded
**Next valid task:** TC-FGSQ-002-02

---

#### TC-FGSQ-002-02 — Verify file existence for each OPEN gap
**Status:** TODO | **Parent:** TC-FGSQ-002
**Preconditions:** TC-FGSQ-002-01 CLOSED

**Micro-steps:**
- MS-002-02-01: For each file in each OPEN gap's `files:` list: check if path exists in filesystem
- MS-002-02-02: For absent files: record gap_id + absent file path in `file-absence-findings.yaml`
- MS-002-02-03: For present files: confirm the gap symptom still manifests (grep for dict fields / STUB comments)
- MS-002-02-04: Note which files have moved (same gap, different file than recorded)

**Evidence:** file-absence-findings.yaml; file-presence-confirmation.yaml
**Completion check:** Every listed file either confirmed-present or recorded-absent
**Next valid task:** TC-FGSQ-002-03

---

#### TC-FGSQ-002-03 — Update PCG-006/007 files: lists
**Status:** TODO | **Parent:** TC-FGSQ-002
**Allowed files:** `reports/product-quality/product-code-gap-ledger.yaml`
**Preconditions:** TC-FGSQ-002-02 CLOSED

**Micro-steps:**
- MS-002-03-01: For PCG-006 (33 detached dict fields): update `files:` to include all current files containing dict fields: FodsDocumentReadOps.cs, FodsDocumentDataAnnotations.cs, FodsDocumentEditOps.cs, FodsDocumentSheetFeatures.cs, FodsDocumentCellProps.cs, FodsDocumentExtendedApis.cs
- MS-002-03-02: For PCG-007 (35 setters without XML): update `files:` to same list plus FodsDocumentCellStyle.cs
- MS-002-03-03: For PCG-001/002: confirm ExtendedApis.cs exists (it does); update file list if needed
- MS-002-03-04: Verify YAML remains parseable after edits

**Evidence:** Updated ledger diff for PCG-006/007
**Completion check:** PCG-006/007 `files:` contain only existent paths; YAML parses
**Next valid task:** TC-FGSQ-002-04

---

#### TC-FGSQ-002-04 — Map GI-FODS-NET-* comments to current file and line
**Status:** TODO | **Parent:** TC-FGSQ-002
**Allowed files:** `reports/product-quality/product-code-gap-ledger.yaml`
**Preconditions:** TC-FGSQ-002-01 CLOSED

**Micro-steps:**
- MS-002-04-01: Grep `src/net/fods/*.cs` for `TODO(GI-FODS-NET-` → record file:line for each
- MS-002-04-02: For each GI-FODS-NET-NNN in gap ledger: update `files:` and add `stub_locations:` with file:line
- MS-002-04-03: For GI items not found by grep: record as COMMENT_REMOVED (stub may have been restructured)

**Evidence:** grep results; updated gap ledger entries with stub_locations
**Next valid task:** TC-FGSQ-002-05

---

#### TC-FGSQ-002-05 — Add reconciled_at timestamps
**Status:** TODO | **Parent:** TC-FGSQ-002
**Allowed files:** `reports/product-quality/product-code-gap-ledger.yaml`
**Preconditions:** TC-FGSQ-002-03 and TC-FGSQ-002-04 CLOSED

**Micro-steps:**
- MS-002-05-01: Add `reconciled_at: "2026-07-10"` field to every OPEN gap entry
- MS-002-05-02: Add `reconciliation_note: "files list updated to match HEAD topology"` to modified entries
- MS-002-05-03: Verify YAML parses after all additions

**Evidence:** Updated gap ledger; YAML parse confirmation
**Completion check:** Every OPEN gap has `reconciled_at`; file parses
**Next valid task:** TC-FGSQ-003 (Lane B can begin)

---

## Lane B — Governance Structural Repairs

> **Gate B:** All Lane B taskcards must reach VERIFIED before Lane C product-source work begins.
> Lane B changes only governance/tools files. No product source modification.
> Lane B taskcards within are independent and may execute in parallel EXCEPT:
> - TC-FGSQ-003 must precede TC-FGSQ-005 (V90/V91 use same method body extractor)
> - TC-FGSQ-004 must precede TC-FGSQ-006 (whitelist update depends on V87 change scope)

---

### TC-FGSQ-003 — Rewrite V88 with Per-Method Setter Analysis
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-003
**Dependencies:** TC-FGSQ-001 CLOSED (needs known stub list for verification)
**Blocks:** TC-FGSQ-005 (shares method-body extractor)
**Scope:** `tools/supervisor/governance_validators_dotnet_semantic.py` and its test file only

**Objective:** Replace V88's file-wide proximity heuristic with per-method analysis that checks whether the specific setter body writes to dict vs XElement.

**Algorithm:**
```
extract_method_bodies(cs_file_text) → list of (method_name, body_text)
  - Use brace-depth counter: depth=0 at class level; depth=1 at method level
  - Capture text between opening { and matching } at depth=1

For each (name, body) where body contains assignment `_\w+\[`:
  If body does NOT contain SetAttributeValue or new XElement:
    flag as setter_without_xml_write

For each (name, body) where body contains return `_\w+\[` or `_\w+\[.*\]`:
  If body does NOT contain .Attribute( or .Element( or .Value or FodsStyleResolver:
    flag as getter_without_xml_read
```

**Known limitation:** Helper method delegation (e.g., `_WriteProtectionXml(_field)`) appears as
false-positive. Mitigation: allowlist method names starting with `_Write`, `_Set`, `_Save` as
implicit XML-write helpers. Accept ~15% residual false-positive rate.

**Children:**
- TC-FGSQ-003-01: Read current V88 implementation
- TC-FGSQ-003-02: Implement extract_method_bodies() helper
- TC-FGSQ-003-03: Implement check_setter_without_xml_write()
- TC-FGSQ-003-04: Implement check_getter_without_xml_read()
- TC-FGSQ-003-05: Replace old file-proximity logic; set blocks_sprint=True
- TC-FGSQ-003-06: Create synthetic test fixture .cs files
- TC-FGSQ-003-07: Write unit tests for V88
- TC-FGSQ-003-08: Update expected_count in runner

**Parent acceptance criteria:**
- V88 fires on `_rowHeights` setter (FodsDocumentEditOps.cs, known dict-only)
- V88 fires on `_conditionalFormats` setter (FodsDocumentDataAnnotations.cs, known dict-only)
- V88 fires on `_charts` getter (FodsDocumentDataAnnotations.cs, known dict-only)
- V88 does NOT fire on FodsStyleResolver-backed setters (XML-grounded)
- V88 `blocks_sprint=True`
- All existing governance validator tests pass

**Evidence:** Unit test results; V88 fire/no-fire log against known stubs

**Rollback:** `git restore tools/supervisor/governance_validators_dotnet_semantic.py`

---

#### TC-FGSQ-003-01 — Read current V88 implementation
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py` — read-only

**Micro-steps:**
- MS-003-01-01: Read governance_validators_dotnet_semantic.py; find V88 function
- MS-003-01-02: Record V88 function name, line range, current algorithm (proximity check)
- MS-003-01-03: Record current `blocks_sprint` value for V88
- MS-003-01-04: Read associated test file; record test count for V88
- MS-003-01-05: Confirm which other validators share V88's helper functions (if any)

**Evidence:** Notes on current V88 state: function name, line range, blocks_sprint value, test count
**Completion check:** All 5 items recorded; no ambiguity about current state
**Next valid task:** TC-FGSQ-003-02

---

#### TC-FGSQ-003-02 — Implement extract_method_bodies() helper
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-003-01 CLOSED

**Micro-steps:**
- MS-003-02-01: Implement `extract_method_bodies(cs_source: str) -> list[tuple[str, str]]` using brace-depth counter
- MS-003-02-02: Handle edge cases: nested classes (skip depth>2), comments (`//`, `/* */`), string literals
- MS-003-02-03: Test manually: run on FodsDocumentEditOps.cs snippet containing SetRowHeight → verify body extracted correctly
- MS-003-02-04: Test on FodsDocumentDataAnnotations.cs → verify _charts methods extracted

**Evidence:** Manual test output showing SetRowHeight body extracted; dict assignment visible in body
**Completion check:** extract_method_bodies returns list with (name, body) tuples; body contains method code only
**Next valid task:** TC-FGSQ-003-03

---

#### TC-FGSQ-003-03 — Implement check_setter_without_xml_write()
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-003-02 CLOSED

**Micro-steps:**
- MS-003-03-01: Implement `check_setter_without_xml_write(method_name: str, body: str) -> bool`:
  - Returns True (flag) if body contains `_\w+\[` assignment AND does NOT contain `SetAttributeValue(` or `new XElement(` or any name in helper_allowlist
- MS-003-03-02: Define helper_allowlist: method calls starting with `_Write`, `_Set`, `_Save`, `_Update` are treated as implicit XML writes
- MS-003-03-03: Test on known dict-only setter (SetRowHeight) → should return True (flag)
- MS-003-03-04: Test on known XML-backed setter (SetCellValue via FodsStyleEditor) → should return False

**Evidence:** Test output: SetRowHeight → flagged; SetCellValue-FodsStyleEditor → not flagged
**Completion check:** Both test cases pass; function defined
**Next valid task:** TC-FGSQ-003-04

---

#### TC-FGSQ-003-04 — Implement check_getter_without_xml_read()
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-003-02 CLOSED

**Micro-steps:**
- MS-003-04-01: Implement `check_getter_without_xml_read(method_name: str, body: str) -> bool`:
  - Returns True (flag) if body returns from `_\w+\[` AND does NOT contain `.Attribute(` or `.Element(` or `.Value` or `FodsStyleResolver`
- MS-003-04-02: Test on GetChartTitle (reads _charts dict) → should return True (flag)
- MS-003-04-03: Test on GetCellHorizontalAlignment (reads via FodsStyleResolver) → should return False

**Evidence:** Test output: GetChartTitle → flagged; alignment getter → not flagged
**Completion check:** Both test cases pass
**Next valid task:** TC-FGSQ-003-05

---

#### TC-FGSQ-003-05 — Replace old proximity logic; set blocks_sprint=True
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-003-02, -03, -04 all CLOSED

**Micro-steps:**
- MS-003-05-01: Remove old V88 file-proximity logic (the "dict field + any XML pattern in same file" check)
- MS-003-05-02: Replace with: iterate each .cs file → extract_method_bodies → check_setter_without_xml_write + check_getter_without_xml_read per method body
- MS-003-05-03: Collect all flagged (file, method, reason) tuples → emit as findings
- MS-003-05-04: Change V88 `blocks_sprint` from False (or current value) to True
- MS-003-05-05: Ensure V88 findings format matches existing validator output format (check other validators for format example)

**Evidence:** Changed function; blocks_sprint=True confirmed in code
**Completion check:** Old proximity logic absent; new per-method logic present; blocks_sprint=True
**Next valid task:** TC-FGSQ-003-06

---

#### TC-FGSQ-003-06 — Create synthetic test fixture .cs files
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tests/supervisor/fixtures/v88/` — create directory and files

**Micro-steps:**
- MS-003-06-01: Create `tests/supervisor/fixtures/v88/stub_setter_only.cs` — a public class with one setter writing only to a dict (`_foo[key] = value;`), no SetAttributeValue
- MS-003-06-02: Create `tests/supervisor/fixtures/v88/xml_setter_only.cs` — a public class with one setter calling `element.SetAttributeValue("key", value)`, no dict write
- MS-003-06-03: Create `tests/supervisor/fixtures/v88/mixed_setter.cs` — a public class with one setter doing BOTH dict write AND SetAttributeValue
- MS-003-06-04: Create `tests/supervisor/fixtures/v88/helper_delegated_setter.cs` — a setter calling `_WriteFooXml(_fooDict[key])`; should NOT fire (helper allowlist)

**Evidence:** Four fixture files exist at `tests/supervisor/fixtures/v88/`
**Completion check:** All 4 files exist; content matches description
**Next valid task:** TC-FGSQ-003-07

---

#### TC-FGSQ-003-07 — Write unit tests for V88
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tests/supervisor/test_governance_validators_v88.py` (create or extend)
**Preconditions:** TC-FGSQ-003-05 and TC-FGSQ-003-06 CLOSED

**Micro-steps:**
- MS-003-07-01: Write test: `test_v88_flags_stub_setter` — run V88 on stub_setter_only.cs → expect finding
- MS-003-07-02: Write test: `test_v88_passes_xml_setter` — run V88 on xml_setter_only.cs → expect no finding
- MS-003-07-03: Write test: `test_v88_passes_mixed_setter` — run V88 on mixed_setter.cs → expect no finding (mixed is acceptable)
- MS-003-07-04: Write test: `test_v88_passes_helper_delegated` — run V88 on helper_delegated.cs → expect no finding
- MS-003-07-05: Write test: `test_v88_fires_on_known_rowheights_setter` — run V88 on FodsDocumentEditOps.cs → expect finding for SetRowHeight

**Evidence:** All 5 tests pass when run with `.venv/Scripts/pytest tests/supervisor/test_governance_validators_v88.py`
**Completion check:** 5/5 tests pass; 0 failures
**Next valid task:** TC-FGSQ-003-08

---

#### TC-FGSQ-003-08 — Update expected_count in governance runner
**Status:** TODO | **Parent:** TC-FGSQ-003
**Allowed files:** `tools/supervisor/governance_validator_runner.py`
**Preconditions:** TC-FGSQ-003-05 CLOSED

**Micro-steps:**
- MS-003-08-01: Read current `expected_count` in governance_validator_runner.py (currently 167 per investigation)
- MS-003-08-02: Determine if V88 rewrite changes the validator count (it should not — same validator, different algorithm)
- MS-003-08-03: If count unchanged: verify `expected_count` remains correct by running full validator suite
- MS-003-08-04: Run `.venv/Scripts/python tools/supervisor/governance_validator_runner.py` → confirm no "unexpected count" error

**Evidence:** Validator runner output showing expected count matched
**Completion check:** Validator runner exits 0; expected_count assertion passes
**Next valid task:** TC-FGSQ-004 or TC-FGSQ-007 (parallel)

---

### TC-FGSQ-004 — Remove PRODUCT_SOURCE Exemption from V87
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-004
**Dependencies:** TC-FGSQ-001 CLOSED (need list of existing constant-return methods for grandfathering)
**Blocks:** TC-FGSQ-006 (whitelist update depends on scope of new grandfathered entries)

**Objective:** Make V87 block constant-return public methods in PRODUCT_SOURCE declarations, not only RELEASE_GATE, while grandfathering all current violations.

**Children:**
- TC-FGSQ-004-01: Read current V87 logic and identify the PRODUCT_SOURCE branch
- TC-FGSQ-004-02: Enumerate all current constant-return public methods in src/net/fods/
- TC-FGSQ-004-03: Add each existing violation to whitelist with grandfathering fields
- TC-FGSQ-004-04: Change V87 to block PRODUCT_SOURCE
- TC-FGSQ-004-05: Write V87 unit tests
- TC-FGSQ-004-06: Integration run

**Parent acceptance criteria:**
- New `public bool GetXxx() { return false; }` in src/net/fods/ → V87 blocks sprint
- All currently-existing constant-return methods → V87 WARN (not FAIL) because grandfathered
- Expected_count unchanged (V87 exists, only behavior changed)

**Evidence:** Unit test results; validator integration run output
**Rollback:** `git restore tools/supervisor/governance_validators_dotnet_semantic.py registry/dotnet-semantic-stub-whitelist.yaml`

---

#### TC-FGSQ-004-01 — Read current V87 logic
**Status:** TODO | **Parent:** TC-FGSQ-004

**Micro-steps:**
- MS-004-01-01: Read V87 function in governance_validators_dotnet_semantic.py
- MS-004-01-02: Record: where does PRODUCT_SOURCE get WARN vs FAIL? (find the conditional branch)
- MS-004-01-03: Record current whitelist lookup logic — how does V87 check the whitelist?
- MS-004-01-04: Note: does V87 detect only `return false;` or also `return 0;`, `return null;`, `return "";`?

**Evidence:** Notes on V87 current logic with line references
**Next valid task:** TC-FGSQ-004-02

---

#### TC-FGSQ-004-02 — Enumerate existing constant-return public methods
**Status:** TODO | **Parent:** TC-FGSQ-004
**Preconditions:** TC-FGSQ-004-01 CLOSED; TC-FGSQ-001 CLOSED

**Micro-steps:**
- MS-004-02-01: Grep `src/net/fods/*.cs` for pattern `public.*\{[^}]*return false;[^}]*\}` (single-statement public methods returning false)
- MS-004-02-02: Grep for `return 0;` and `return null;` and `return string.Empty;` in public method bodies
- MS-004-02-03: Cross-reference with method-inventory-raw.yaml (from TC-001): add HARDCODED_FALSE methods from ExtendedApis.cs
- MS-004-02-04: Produce `existing-constant-return-methods.yaml` with full list: file, method name, return value

**Evidence:** existing-constant-return-methods.yaml; grep output
**Next valid task:** TC-FGSQ-004-03

---

#### TC-FGSQ-004-03 — Add existing violations to whitelist with grandfathering
**Status:** TODO | **Parent:** TC-FGSQ-004
**Allowed files:** `registry/dotnet-semantic-stub-whitelist.yaml`
**Preconditions:** TC-FGSQ-004-02 CLOSED

**Micro-steps:**
- MS-004-03-01: Read current dotnet-semantic-stub-whitelist.yaml completely
- MS-004-03-02: For each method in existing-constant-return-methods.yaml: add entry with fields:
  `method: <name>`, `file: <path>`, `approved_by: "pre-existing-grandfathered"`,
  `approved_date: "2026-07-10"`, `review_due: "2026-10-01"`,
  `removal_condition: "implement XML path or replace with NotSupportedException"`
- MS-004-03-03: Avoid duplicate entries (check if method already in whitelist before adding)
- MS-004-03-04: Verify YAML parses after additions

**Evidence:** Updated whitelist with diff showing new entries
**Next valid task:** TC-FGSQ-004-04

---

#### TC-FGSQ-004-04 — Change V87 to block PRODUCT_SOURCE
**Status:** TODO | **Parent:** TC-FGSQ-004
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-004-03 CLOSED

**Micro-steps:**
- MS-004-04-01: Find the V87 branch that returns WARN for PRODUCT_SOURCE
- MS-004-04-02: Change that branch: return FAIL + blocks_sprint=True (same as RELEASE_GATE branch)
- MS-004-04-03: Verify whitelisted methods still produce WARN not FAIL (whitelist check must precede PRODUCT_SOURCE check)
- MS-004-04-04: Confirm the ordering: check whitelist first → if whitelisted: WARN + continue; else: FAIL + blocks_sprint

**Evidence:** Changed function; test confirming WARN for whitelisted, FAIL for non-whitelisted
**Next valid task:** TC-FGSQ-004-05

---

#### TC-FGSQ-004-05 — Write V87 unit tests
**Status:** TODO | **Parent:** TC-FGSQ-004
**Preconditions:** TC-FGSQ-004-04 CLOSED

**Micro-steps:**
- MS-004-05-01: Write test: `test_v87_blocks_new_constant_return_product_source` — PRODUCT_SOURCE declaration with new `return false;` method not in whitelist → blocks sprint
- MS-004-05-02: Write test: `test_v87_warns_grandfathered_constant_return` — same method IS in whitelist → WARN not FAIL
- MS-004-05-03: Write test: `test_v87_still_blocks_release_gate` — RELEASE_GATE declaration with constant return → blocks sprint (regression)
- MS-004-05-04: Run all three tests → 3/3 pass

**Evidence:** 3/3 test pass output
**Next valid task:** TC-FGSQ-004-06

---

#### TC-FGSQ-004-06 — Integration run
**Status:** TODO | **Parent:** TC-FGSQ-004
**Preconditions:** TC-FGSQ-004-05 CLOSED

**Micro-steps:**
- MS-004-06-01: Run full governance validator suite: `python tools/supervisor/governance_validator_runner.py`
- MS-004-06-02: Confirm expected_count still matches (no validator added/removed, only behavior changed)
- MS-004-06-03: Confirm no unexpected FAILs introduced on existing compliant code
- MS-004-06-04: Confirm V87 specifically fires on at least one known constant-return in ExtendedApis.cs (if not whitelisted, becomes FAIL; confirm expected)

**Evidence:** Validator runner output; exit code 0
**Completion check:** Runner exits 0; expected_count matches; no new unexpected failures
**Next valid task:** TC-FGSQ-006 (whitelist governance)

---

### TC-FGSQ-005 — Change V90/V91 from Warn to Block
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-005
**Dependencies:** TC-FGSQ-003 CLOSED (shares method-body extractor; reuse extract_method_bodies)
**Note:** V90 = setter_without_xml_write; V91 = getter_without_xml_read (different from V88 which is a file-level check)

**Objective:** Make V90 and V91 block sprint closure (blocks_sprint=True) and grandfather all current violations via the whitelist.

**Children:**
- TC-FGSQ-005-01: Read current V90 and V91; confirm blocks_sprint values
- TC-FGSQ-005-02: Enumerate all current V90/V91 violations to grandfather
- TC-FGSQ-005-03: Add violations to whitelist
- TC-FGSQ-005-04: Change blocks_sprint=True for V90/V91
- TC-FGSQ-005-05: Write unit tests; run validators

**Parent acceptance criteria:**
- New dict-only setter in sprint declaration → V90 blocks sprint
- New dict-only getter in sprint declaration → V91 blocks sprint
- All existing violations → WARN (whitelisted)

---

#### TC-FGSQ-005-01 — Read current V90/V91
**Status:** TODO | **Parent:** TC-FGSQ-005

**Micro-steps:**
- MS-005-01-01: Find V90 function in governance_validators_dotnet_semantic.py; record line range and blocks_sprint
- MS-005-01-02: Find V91 function; record line range and blocks_sprint
- MS-005-01-03: Confirm V90 and V91 are distinct from the new V88 (V88 is the file-level detector; V90/V91 are validator IDs in the sprint declaration context)
- MS-005-01-04: If V90/V91 and V88 implement the same logic: note duplication; proceed anyway

**Evidence:** Confirmed V90/V91 function names, line ranges, current blocks_sprint=False
**Next valid task:** TC-FGSQ-005-02

---

#### TC-FGSQ-005-02 — Enumerate current V90/V91 violations
**Status:** TODO | **Parent:** TC-FGSQ-005
**Preconditions:** TC-FGSQ-005-01 CLOSED

**Micro-steps:**
- MS-005-02-01: Run V90 and V91 in report-mode (blocks_sprint=False) against all src/net/fods/*.cs
- MS-005-02-02: Collect all findings: file, method, violation type (setter-no-xml-write or getter-no-xml-read)
- MS-005-02-03: Write `existing-v90-v91-violations.yaml` with full list

**Evidence:** existing-v90-v91-violations.yaml
**Next valid task:** TC-FGSQ-005-03

---

#### TC-FGSQ-005-03 — Add V90/V91 violations to whitelist
**Status:** TODO | **Parent:** TC-FGSQ-005
**Allowed files:** `registry/dotnet-semantic-stub-whitelist.yaml`
**Preconditions:** TC-FGSQ-005-02 CLOSED

**Micro-steps:**
- MS-005-03-01: For each method in existing-v90-v91-violations.yaml: add whitelist entry (same grandfathering fields as TC-004-03)
- MS-005-03-02: Do not duplicate entries already added by TC-FGSQ-004-03
- MS-005-03-03: Verify YAML parses

**Evidence:** Whitelist diff showing V90/V91 violation entries
**Next valid task:** TC-FGSQ-005-04

---

#### TC-FGSQ-005-04 — Set blocks_sprint=True for V90/V91
**Status:** TODO | **Parent:** TC-FGSQ-005
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`
**Preconditions:** TC-FGSQ-005-03 CLOSED

**Micro-steps:**
- MS-005-04-01: Change V90 `blocks_sprint` from False to True
- MS-005-04-02: Change V91 `blocks_sprint` from False to True
- MS-005-04-03: Verify whitelist check precedes the block — whitelisted violations → WARN

**Next valid task:** TC-FGSQ-005-05

---

#### TC-FGSQ-005-05 — Write unit tests and integration run
**Status:** TODO | **Parent:** TC-FGSQ-005

**Micro-steps:**
- MS-005-05-01: Write test: new dict-only setter (not in whitelist) → V90 blocks
- MS-005-05-02: Write test: whitelisted dict-only setter → V90 WARN not FAIL
- MS-005-05-03: Write test: new dict-only getter → V91 blocks
- MS-005-05-04: Run full validator suite; confirm no new unexpected failures
- MS-005-05-05: Confirm expected_count unchanged (no validators added/removed)

**Evidence:** 3/3 new tests pass; runner exits 0
**Next valid task:** TC-FGSQ-008 (parallel) or TC-FGSQ-006

---

### TC-FGSQ-006 — Add Governance to the V87 Whitelist
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-006
**Dependencies:** TC-FGSQ-004 CLOSED (whitelist now has grandfathered entries; add governance on top)

**Objective:** Add required governance fields (approved_by, review_due, removal_condition) to all whitelist entries and implement a new V_WHITELIST_EXPIRY validator.

**Children:**
- TC-FGSQ-006-01: Verify all whitelist entries have required governance fields (from TC-004-03)
- TC-FGSQ-006-02: Implement V_WHITELIST_EXPIRY validator
- TC-FGSQ-006-03: Register new validator; update expected_count
- TC-FGSQ-006-04: Write unit tests for V_WHITELIST_EXPIRY

**Parent acceptance criteria:**
- Every whitelist entry has approved_by, approved_date, review_due, removal_condition
- V_WHITELIST_EXPIRY fires WARN within 30 days of review_due
- V_WHITELIST_EXPIRY fires FAIL+blocks_sprint past review_due
- expected_count updated; runner exits 0

---

#### TC-FGSQ-006-01 — Verify governance fields in whitelist
**Status:** TODO | **Parent:** TC-FGSQ-006

**Micro-steps:**
- MS-006-01-01: Read current dotnet-semantic-stub-whitelist.yaml
- MS-006-01-02: For each entry: check presence of approved_by, approved_date, review_due, removal_condition
- MS-006-01-03: For any entry missing fields: add them now (same grandfathering values)
- MS-006-01-04: Verify YAML parses after additions

**Evidence:** Whitelist with all entries having required fields; YAML parse confirmation
**Next valid task:** TC-FGSQ-006-02

---

#### TC-FGSQ-006-02 — Implement V_WHITELIST_EXPIRY validator
**Status:** TODO | **Parent:** TC-FGSQ-006
**Allowed files:** `tools/supervisor/governance_validators_dotnet_semantic.py`

**Micro-steps:**
- MS-006-02-01: Implement `validate_whitelist_expiry()` function:
  - Reads registry/dotnet-semantic-stub-whitelist.yaml
  - For each entry: parse review_due date
  - If today >= review_due: FAIL + blocks_sprint=True
  - If today is within 30 days of review_due: WARN
  - If today < review_due - 30 days: PASS
- MS-006-02-02: Assign validator ID (next available ID after last existing validator)
- MS-006-02-03: Register in validator map with category=governance, blocks_sprint=True (for expired)

**Evidence:** Function implemented; blocks_sprint=True for expired entries
**Next valid task:** TC-FGSQ-006-03

---

#### TC-FGSQ-006-03 — Register validator; update expected_count
**Status:** TODO | **Parent:** TC-FGSQ-006
**Allowed files:** `tools/supervisor/governance_validator_runner.py`

**Micro-steps:**
- MS-006-03-01: Add V_WHITELIST_EXPIRY to the runner's validator list
- MS-006-03-02: Increment expected_count by 1
- MS-006-03-03: Run validator runner → confirm expected_count assertion passes

**Evidence:** Runner exits 0; expected_count incremented
**Next valid task:** TC-FGSQ-006-04

---

#### TC-FGSQ-006-04 — Write unit tests for V_WHITELIST_EXPIRY
**Status:** TODO | **Parent:** TC-FGSQ-006

**Micro-steps:**
- MS-006-04-01: Write test: entry with review_due 60 days from now → PASS
- MS-006-04-02: Write test: entry with review_due 15 days from now → WARN
- MS-006-04-03: Write test: entry with review_due yesterday → FAIL + blocks_sprint
- MS-006-04-04: Run 3 tests → 3/3 pass

**Evidence:** 3/3 test pass output
**Next valid task:** TC-FGSQ-007 (parallel-safe with TC-006)

---

### TC-FGSQ-007 — Add Data Provenance to Oracle Depth Scoring
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-007
**Scope:** `tools/oracle/execute_oracle.py` + FODS oracle package YAML files

**Objective:** Extend oracle packages with a `data_source` field per property so D1 depth requires
data_source=parsed and cannot be achieved by a dict-cache return.

**Known limit:** data_source cannot be machine-verified (no runtime dataflow tracing). Requires
declaration + manual reviewer confirmation. Cross-check: if V88 flags a getter, and oracle says
data_source=parsed for the same property, escalate to WARN.

**Children:**
- TC-FGSQ-007-01: Read current make_verdict() and D1 depth logic in execute_oracle.py
- TC-FGSQ-007-02: Add data_source field to oracle package YAML schema
- TC-FGSQ-007-03: Update make_verdict() to use data_source for depth downgrade
- TC-FGSQ-007-04: Update all FODS oracle package YAMLs with data_source declarations
- TC-FGSQ-007-05: Write unit tests; run oracle against FODS samples

**Parent acceptance criteria:**
- oracle package with data_source=unsupported property → D0 for that property
- oracle package with data_source=parsed property → contributes to D1
- All FODS oracle packages have data_source declared for each property
- Existing FODS oracle test pass rate unchanged

---

#### TC-FGSQ-007-01 — Read current make_verdict() and depth logic
**Status:** TODO | **Parent:** TC-FGSQ-007

**Micro-steps:**
- MS-007-01-01: Read execute_oracle.py; find make_verdict() function
- MS-007-01-02: Record current D1 determination logic (which conditions upgrade to D1?)
- MS-007-01-03: List all FODS oracle package YAML files in `oracle/fods/`
- MS-007-01-04: Read one FODS oracle package YAML; record current property format

**Evidence:** Notes on make_verdict logic; list of FODS oracle YAMLs; current property format
**Next valid task:** TC-FGSQ-007-02

---

#### TC-FGSQ-007-02 — Add data_source field to oracle package schema
**Status:** TODO | **Parent:** TC-FGSQ-007

**Micro-steps:**
- MS-007-02-01: Read oracle package JSON schema file (if it exists) or find where schema is defined
- MS-007-02-02: Add `data_source` as optional field on expected_model_properties entries
  Values: `parsed` | `computed` | `unsupported` | `unknown` (default=unknown for backward compat)
- MS-007-02-03: Update schema validation in execute_oracle.py to accept data_source field
- MS-007-02-04: Default behavior for missing data_source: treat as `unknown`; emit WARN for packages claiming D1+

**Evidence:** Schema updated; execute_oracle.py accepts data_source without error
**Next valid task:** TC-FGSQ-007-03

---

#### TC-FGSQ-007-03 — Update make_verdict() to use data_source for depth downgrade
**Status:** TODO | **Parent:** TC-FGSQ-007

**Micro-steps:**
- MS-007-03-01: In make_verdict(): after computing observed properties, check if any expected property has data_source=unsupported AND is being compared as D1
- MS-007-03-02: If data_source=unsupported AND verdict would be D1: downgrade to D0 for that property's contribution; record downgrade in verdict deviations
- MS-007-03-03: If data_source=unknown AND verdict would be D1: emit WARN "property X has unknown data_source; declare parsed or unsupported"
- MS-007-03-04: Final depth_level = min(D1_if_all_parsed_properties_pass, downgraded D0 if any unsupported)

**Evidence:** make_verdict() updated; unit test showing D0 result when data_source=unsupported
**Next valid task:** TC-FGSQ-007-04

---

#### TC-FGSQ-007-04 — Update FODS oracle package YAMLs with data_source
**Status:** TODO | **Parent:** TC-FGSQ-007
**Allowed files:** All `oracle/fods/*.yaml` files

**Micro-steps:**
- MS-007-04-01: For each FODS oracle YAML: read its expected_model_properties
- MS-007-04-02: For chart_title, conditional_format_count, pivot_table_count, sparkline_count: set data_source=unsupported
- MS-007-04-03: For row_count, cell_value, sheet_name, header parsing: set data_source=parsed (these are confirmed XML-backed per FodsParser investigation)
- MS-007-04-04: For any property unclear: set data_source=unknown and add TODO comment
- MS-007-04-05: Verify all FODS oracle YAMLs parse after update

**Evidence:** Updated oracle YAMLs with data_source fields; parse confirmation
**Next valid task:** TC-FGSQ-007-05

---

#### TC-FGSQ-007-05 — Unit tests and oracle run
**Status:** TODO | **Parent:** TC-FGSQ-007

**Micro-steps:**
- MS-007-05-01: Write test: oracle package with data_source=unsupported property → verdict D0
- MS-007-05-02: Write test: oracle package with data_source=parsed and correct value → verdict D1
- MS-007-05-03: Run oracle against known FODS fixture file → verify verdicts consistent with prior run (no regressions on parsed properties)
- MS-007-05-04: Run oracle → confirm FODS properties previously D1 remain D1 (they are truly XML-backed)

**Evidence:** 2/2 unit tests pass; FODS oracle pass rate unchanged for parsed properties
**Next valid task:** TC-FGSQ-008

---

### TC-FGSQ-008 — Add Persistent-Property Roundtrip Requirement to Sprint Validator
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-008
**Scope:** `tools/supervisor/sprint_executor_validate.py` only

**Objective:** Add Phase 13 to the sprint declaration validator requiring `round_trip_test_path` for any PERSISTENT_PROPERTY work item.

**Children:**
- TC-FGSQ-008-01: Read sprint_executor_validate.py phases; find insertion point
- TC-FGSQ-008-02: Define work_type taxonomy
- TC-FGSQ-008-03: Implement Phase 13 check
- TC-FGSQ-008-04: Write test fixtures and unit tests

---

#### TC-FGSQ-008-01 — Read current sprint validator phases
**Status:** TODO | **Parent:** TC-FGSQ-008

**Micro-steps:**
- MS-008-01-01: Read sprint_executor_validate.py completely
- MS-008-01-02: List all existing phases and their line ranges (Phase 1 through N)
- MS-008-01-03: Find last phase; record phase number N (Phase 13 = N+1)
- MS-008-01-04: Record how work items are accessed (field name, data structure)

**Evidence:** Phase list with line numbers; last phase number recorded
**Next valid task:** TC-FGSQ-008-02

---

#### TC-FGSQ-008-02 — Define work_type taxonomy
**Status:** TODO | **Parent:** TC-FGSQ-008

**Work types to add to declaration schema:**
```
PERSISTENT_PROPERTY: setter/getter with ODF XML backing, must survive Save/Load
READ_ONLY_QUERY: reads from parsed document; no save needed; must use real fixture file
UNSUPPORTED_CAPABILITY: throws NotSupportedException; must have exception test
WRITE_ONLY_EXPORT: outputs to different format; must have output-content test
GOVERNANCE_CHANGE: validator/tool change; no product test required
```

**Micro-steps:**
- MS-008-02-01: Check if `work_type` field already exists in evidence-declaration schema
- MS-008-02-02: If absent: add work_type as optional field to evidence-declaration.schema.json
- MS-008-02-03: Document work_type values in a comment in sprint_executor_validate.py
- MS-008-02-04: For missing work_type: default to READ_ONLY_QUERY (lenient) with WARN

**Evidence:** Schema updated with work_type; documentation added
**Next valid task:** TC-FGSQ-008-03

---

#### TC-FGSQ-008-03 — Implement Phase 13 check
**Status:** TODO | **Parent:** TC-FGSQ-008
**Allowed files:** `tools/supervisor/sprint_executor_validate.py`
**Preconditions:** TC-FGSQ-008-01 and TC-FGSQ-008-02 CLOSED

**Micro-steps:**
- MS-008-03-01: Add Phase 13 function `validate_phase13_persistent_property_roundtrip(declaration) -> list[issue]`
- MS-008-03-02: Logic: for each work_item where work_type=PERSISTENT_PROPERTY:
  - If round_trip_test_path absent or empty → WARN (grace period: become FAIL after 2026-09-01)
  - If round_trip_test_path present but file does not exist → FAIL
  - If round_trip_test_path present, file exists, but file does not contain both `Save` and `Load` → WARN "test may not be a true roundtrip"
- MS-008-03-03: Add Phase 13 to the main validation chain
- MS-008-03-04: For UNSUPPORTED_CAPABILITY: check that test file exists containing `NotSupportedException` → WARN if absent

**Evidence:** Phase 13 function added and wired into validation chain
**Next valid task:** TC-FGSQ-008-04

---

#### TC-FGSQ-008-04 — Write test fixtures and unit tests
**Status:** TODO | **Parent:** TC-FGSQ-008
**Preconditions:** TC-FGSQ-008-03 CLOSED

**Micro-steps:**
- MS-008-04-01: Create synthetic declaration: PERSISTENT_PROPERTY with no round_trip_test_path → expect WARN
- MS-008-04-02: Create synthetic declaration: PERSISTENT_PROPERTY with valid roundtrip test path → expect PASS
- MS-008-04-03: Create synthetic declaration: UNSUPPORTED_CAPABILITY with test containing NotSupportedException → expect PASS
- MS-008-04-04: Create synthetic declaration: UNSUPPORTED_CAPABILITY with no exception test → expect WARN
- MS-008-04-05: Run 4 test cases → 4/4 pass
- MS-008-04-06: Run full sprint_executor_validate tests to confirm no regression

**Evidence:** 4/4 unit tests pass; no regressions in existing tests
**Next valid task:** TC-FGSQ-009

---

### TC-FGSQ-009 — Abolish COLLECTION_STUB Comment Marker
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-009
**Scope:** New validator; governance tools only

**Objective:** Add a validator that blocks new `// COLLECTION_STUB` and `// XML write deferred` comment patterns in .cs files, while grandfathering existing ones.

**Children:**
- TC-FGSQ-009-01: Find all current COLLECTION_STUB occurrences (to grandfather)
- TC-FGSQ-009-02: Implement validate_collection_stub_comment() validator
- TC-FGSQ-009-03: Register and write unit tests
- TC-FGSQ-009-04: Add collection_stub_count to self-assessment fields

---

#### TC-FGSQ-009-01 — Find and record all current COLLECTION_STUB occurrences
**Status:** TODO | **Parent:** TC-FGSQ-009

**Micro-steps:**
- MS-009-01-01: Grep `src/net/fods/*.cs` for `COLLECTION_STUB` → list file:line occurrences
- MS-009-01-02: Grep `src/net/fods/*.cs` for `XML write deferred` → list file:line occurrences
- MS-009-01-03: Write `existing-collection-stubs.yaml` with file, line, content per occurrence
- MS-009-01-04: Count total occurrences (expected: ~8 based on investigation)

**Evidence:** existing-collection-stubs.yaml; count confirmed
**Next valid task:** TC-FGSQ-009-02

---

#### TC-FGSQ-009-02 — Implement validate_collection_stub_comment() validator
**Status:** TODO | **Parent:** TC-FGSQ-009
**Preconditions:** TC-FGSQ-009-01 CLOSED

**Micro-steps:**
- MS-009-02-01: Implement function that scans src/net/ .cs files for `COLLECTION_STUB` and `XML write deferred`
- MS-009-02-02: For any occurrence NOT in existing-collection-stubs.yaml: FAIL + blocks_sprint
- MS-009-02-03: For occurrences IN existing-collection-stubs.yaml: WARN "grandfathered COLLECTION_STUB; resolve by TC-FGSQ-012"
- MS-009-02-04: Assign validator ID; add to governance_validators_dotnet.py or _semantic.py

**Evidence:** Validator implemented; fires on new occurrences; warns on existing
**Next valid task:** TC-FGSQ-009-03

---

#### TC-FGSQ-009-03 — Register; update expected_count; write unit tests
**Status:** TODO | **Parent:** TC-FGSQ-009

**Micro-steps:**
- MS-009-03-01: Register new validator in runner; increment expected_count by 1
- MS-009-03-02: Write test: new COLLECTION_STUB comment (not in existing list) → validator fires FAIL
- MS-009-03-03: Write test: existing COLLECTION_STUB comment (in existing list) → validator fires WARN only
- MS-009-03-04: Run 2 unit tests + runner → 2/2 pass; runner exits 0

**Evidence:** 2/2 tests pass; runner exits 0; expected_count incremented
**Next valid task:** TC-FGSQ-009-04

---

#### TC-FGSQ-009-04 — Add collection_stub_count to declaration self-assessment
**Status:** TODO | **Parent:** TC-FGSQ-009
**Allowed files:** `tools/supervisor/sprint_executor_validate.py`

**Micro-steps:**
- MS-009-04-01: Add `collection_stub_count` as optional self-assessment field to evidence declaration schema
- MS-009-04-02: In Phase 13 (or a new phase): warn if collection_stub_count > 0 and no TC-FGSQ-012 work item in declaration
- MS-009-04-03: This is informational — WARN not FAIL

**Evidence:** Schema updated; phase added; field documented
**Next valid task:** TC-FGSQ-010

---

### TC-FGSQ-010 — Add Spec-Grounding Pre-Condition to Task Generation
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-010
**Scope:** `tools/supervisor/autonomous_task_generator.py` only

**Objective:** Before generating an IMPLEMENT_* task, require `spec_fact_id` verifiable in SAL or `odf_qname` verifiable in qname-registry. Otherwise auto-generate as UNSUPPORTED_CAPABILITY.

**Children:**
- TC-FGSQ-010-01: Read autonomous_task_generator.py and _EXPANSION_GOALS structure
- TC-FGSQ-010-02: Locate SAL index and QName registry for lookup
- TC-FGSQ-010-03: Implement validate_expansion_goal_authority()
- TC-FGSQ-010-04: Wire into task generation loop
- TC-FGSQ-010-05: Write unit tests

---

#### TC-FGSQ-010-01 — Read generator and EXPANSION_GOALS structure
**Status:** TODO | **Parent:** TC-FGSQ-010

**Micro-steps:**
- MS-010-01-01: Read autonomous_task_generator.py completely
- MS-010-01-02: Record: where is `_EXPANSION_GOALS` defined? What fields does each goal have?
- MS-010-01-03: Record: which field (if any) represents spec authority? (investigation found `"spec_authority": "schema_authority_available"`)
- MS-010-01-04: Note: what is the action_type field? What action_types exist?

**Evidence:** Notes on generator structure; _EXPANSION_GOALS field list
**Next valid task:** TC-FGSQ-010-02

---

#### TC-FGSQ-010-02 — Locate SAL index and QName registry
**Status:** TODO | **Parent:** TC-FGSQ-010

**Micro-steps:**
- MS-010-02-01: Find where SAL facts are indexed (search for sal_facts or spec_facts in tools/)
- MS-010-02-02: Find qname-registry directory; check what files are in it
- MS-010-02-03: Determine: can a fact_id be looked up programmatically in SAL output?
- MS-010-02-04: Determine: can an odf_qname be looked up in the qname-registry?
- MS-010-02-05: Record lookup method for each: file path, lookup function name if exists

**Evidence:** SAL lookup path and method; QName registry path and method
**Next valid task:** TC-FGSQ-010-03

---

#### TC-FGSQ-010-03 — Implement validate_expansion_goal_authority()
**Status:** TODO | **Parent:** TC-FGSQ-010
**Preconditions:** TC-FGSQ-010-01 and TC-FGSQ-010-02 CLOSED

**Micro-steps:**
- MS-010-03-01: Implement `validate_expansion_goal_authority(goal: dict) -> tuple[bool, str]`:
  - Returns (True, "spec_grounded") if goal has spec_fact_id found in SAL index
  - Returns (True, "qname_grounded") if goal has odf_qname found in qname-registry
  - Returns (True, "unsupported_explicit") if goal.action_type == "UNSUPPORTED_CAPABILITY"
  - Returns (False, "no_spec_authority") otherwise
- MS-010-03-02: Handle case where SAL index or qname-registry file is absent (graceful degradation: WARN, don't crash)
- MS-010-03-03: Log each validation result to task-generation-authority-log.yaml

**Evidence:** Function implemented; handles SAL/QName absence gracefully
**Next valid task:** TC-FGSQ-010-04

---

#### TC-FGSQ-010-04 — Wire into task generation loop
**Status:** TODO | **Parent:** TC-FGSQ-010
**Preconditions:** TC-FGSQ-010-03 CLOSED

**Micro-steps:**
- MS-010-04-01: Find the loop in autonomous_task_generator.py that processes _EXPANSION_GOALS
- MS-010-04-02: Before creating an IMPLEMENT_* task: call validate_expansion_goal_authority(goal)
- MS-010-04-03: If authority returns False: change action_type to UNSUPPORTED_CAPABILITY; keep goal in output but mark as authority_downgraded=true
- MS-010-04-04: Log all authority-downgraded goals with reason

**Evidence:** Wired loop; test showing authority-downgraded goal generates UNSUPPORTED task
**Next valid task:** TC-FGSQ-010-05

---

#### TC-FGSQ-010-05 — Write unit tests
**Status:** TODO | **Parent:** TC-FGSQ-010

**Micro-steps:**
- MS-010-05-01: Write test: goal with valid spec_fact_id → generates IMPLEMENT task
- MS-010-05-02: Write test: goal without spec_fact_id or odf_qname → generates UNSUPPORTED_CAPABILITY task
- MS-010-05-03: Write test: goal with UNSUPPORTED_CAPABILITY action_type explicitly → not downgraded, kept as-is
- MS-010-05-04: Run 3 tests → 3/3 pass

**Evidence:** 3/3 pass
**Next valid task:** TC-FGSQ-011

---

### TC-FGSQ-011 — Add Gap Ledger File-System Reconciliation to Autonomous Cycle
**Status:** PROPOSED | **Type:** PARENT | **Lane:** B
**REQ:** REQ-FGSQ-011
**Scope:** `tools/supervisor/autonomous_cycle.py` only
**Dependencies:** TC-FGSQ-002 CLOSED (gap ledger should be reconciled before wiring cycle check)

**Objective:** After each sprint, report whether OPEN gap entries reference files that still exist in the filesystem. Non-blocking WARN initially; escalate to FAIL after 3 consecutive absent-file cycles.

**Children:**
- TC-FGSQ-011-01: Find insertion point in autonomous_cycle.py
- TC-FGSQ-011-02: Implement reconcile_gap_ledger_files()
- TC-FGSQ-011-03: Write gap-ledger-drift.json output format
- TC-FGSQ-011-04: Wire into cycle; write unit tests

---

#### TC-FGSQ-011-01 — Find insertion point in autonomous_cycle.py
**Status:** TODO | **Parent:** TC-FGSQ-011

**Micro-steps:**
- MS-011-01-01: Read autonomous_cycle.py; identify the declaration-validation step
- MS-011-01-02: Record: what happens after validation? What is the next step?
- MS-011-01-03: Confirm: gap reconciliation should run AFTER validation, BEFORE next-sprint generation

**Evidence:** Confirmed insertion point with line reference
**Next valid task:** TC-FGSQ-011-02

---

#### TC-FGSQ-011-02 — Implement reconcile_gap_ledger_files()
**Status:** TODO | **Parent:** TC-FGSQ-011
**Preconditions:** TC-FGSQ-011-01 CLOSED

**Micro-steps:**
- MS-011-02-01: Implement `reconcile_gap_ledger_files(repo_root: Path, ledger_path: Path) -> dict`:
  - Loads gap ledger YAML
  - For each OPEN gap: checks each file in `files:` list
  - Returns dict: {gap_id: {present: [...], absent: [...], consecutive_absent_cycles: int}}
- MS-011-02-02: Track consecutive_absent_cycles by reading/writing a cycle-state file at `.local/supervisor/gap-drift-state.json`
- MS-011-02-03: If consecutive_absent_cycles >= 3: mark as ESCALATED in output (but do not auto-close)

**Evidence:** Function implemented; handles missing ledger gracefully (returns empty dict)
**Next valid task:** TC-FGSQ-011-03

---

#### TC-FGSQ-011-03 — Write gap-ledger-drift.json output format
**Status:** TODO | **Parent:** TC-FGSQ-011

**Micro-steps:**
- MS-011-03-01: Define output format for `reports/supervisor/gap-ledger-drift.json`:
  ```json
  {"generated_at": "...", "gaps_checked": N, "drifted": [{"gap_id": "...", "absent_files": [...], "consecutive_absent_cycles": N}]}
  ```
- MS-011-03-02: Implement write step in reconcile_gap_ledger_files() to write this JSON
- MS-011-03-03: Confirm output is human-readable and machine-parseable

**Evidence:** gap-ledger-drift.json format defined; write step implemented
**Next valid task:** TC-FGSQ-011-04

---

#### TC-FGSQ-011-04 — Wire into cycle; unit tests
**Status:** TODO | **Parent:** TC-FGSQ-011
**Preconditions:** TC-FGSQ-011-02 and TC-FGSQ-011-03 CLOSED

**Micro-steps:**
- MS-011-04-01: In autonomous_cycle.py: call reconcile_gap_ledger_files() at insertion point
- MS-011-04-02: Log WARN for any drifted gaps; log ESCALATED for 3+ consecutive cycles
- MS-011-04-03: Write test: OPEN gap with absent file → drift report shows it; cycle continues (non-blocking)
- MS-011-04-04: Write test: OPEN gap with present file → drift report clean
- MS-011-04-05: Run 2 tests → 2/2 pass

**Evidence:** 2/2 tests pass; cycle still completes when drift exists
**Next valid task:** TC-FGSQ-012 (Lane C)

---

## Lane C — FODS .NET Architecture Repair

> **Gate C:** Lane B must be CLOSED before Lane C work begins on product source.
> Lane C order: TC-012 and TC-013 and TC-014 in parallel → TC-015 → TC-016 → TC-017.
> Do NOT delete FodsDocumentExtendedApis.cs (TC-016) before TC-012/013/014/015 are CLOSED.

---

### TC-FGSQ-012 — Resolve COLLECTION_STUB Methods in SheetFeatures.cs
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-012
**Dependencies:** All Lane B CLOSED
**Blocks:** TC-FGSQ-016

**Objective:** For each COLLECTION_STUB method: implement XML-backed path or throw NotSupportedException. Remove all associated dict fields. Prove persistence with roundtrip tests.

**Decision table:**
| Stub | ODF target | Decision |
|---|---|---|
| `_filters` | `table:database-range` §9.5.2 | IMPLEMENT |
| `_pageBreaks` | `table:table-row/@fo:break-before` §9.4.4 | IMPLEMENT |
| `_groups` | `table:row-group` §9.4.2 | IMPLEMENT |
| `_sheetProtection` (no-password) | `table:table-protection` | IMPLEMENT |
| `_sheetProtection` (password) | `table:table-protection/@table:password` | UNSUPPORTED (SHA256 out of scope) |

**Children:**
- TC-FGSQ-012-01: Read current COLLECTION_STUB implementations; verify ODF spec sections
- TC-FGSQ-012-02: Implement filters XML read + write + remove dict
- TC-FGSQ-012-03: Implement page breaks XML read + write + remove dict
- TC-FGSQ-012-04: Implement row groups XML read + write + remove dict
- TC-FGSQ-012-05: Implement sheet protection (no-password) XML read + write; UNSUPPORTED for password
- TC-FGSQ-012-06: Run full .NET test suite; confirm 0 failures

**Parent acceptance criteria:**
- No COLLECTION_STUB dict fields remain in SheetFeatures.cs
- Roundtrip tests exist for all 4 IMPLEMENTED capabilities
- NotSupportedException test exists for password-protected protection
- `dotnet test src/net/fods/` → 0 failures

---

#### TC-FGSQ-012-01 — Read current COLLECTION_STUB implementations
**Status:** TODO | **Parent:** TC-FGSQ-012

**Micro-steps:**
- MS-012-01-01: Read FodsDocumentSheetFeatures.cs completely; record all COLLECTION_STUB method signatures
- MS-012-01-02: Record dict field names and their types for each COLLECTION_STUB group
- MS-012-01-03: Read ODF spec references in comments; confirm spec sections are correct
- MS-012-01-04: Check FodsDocumentReadOps.cs for filter-restoration code (RestoreFilterStateFromDocument)

**Evidence:** COLLECTION_STUB method list; confirmed ODF spec sections
**Next valid task:** TC-FGSQ-012-02

---

#### TC-FGSQ-012-02 — Implement filters: XML read + write + remove dict
**Status:** TODO | **Parent:** TC-FGSQ-012
**Allowed files:** `src/net/fods/FodsDocumentSheetFeatures.cs`, `src/net/fods/FodsDocumentReadOps.cs`
**Preconditions:** TC-FGSQ-012-01 CLOSED

**Micro-steps:**
- MS-012-02-01: Add XML read path: in FodsDocumentReadOps.cs RestoreFilterStateFromDocument() or Load(): read `table:database-range` elements from XDocument; store parsed state in XElement (not dict)
- MS-012-02-02: Modify GetFilters() to read from XElement (query `table:database-range` children) instead of _filters dict
- MS-012-02-03: Modify SetFilter() / AddFilter() to write to XElement (`table:database-range` attribute values) instead of _filters dict
- MS-012-02-04: Remove `_filters` and `_allFilterRanges` dict field declarations
- MS-012-02-05: Confirm compilation: `dotnet build src/net/fods/` → 0 errors

**Evidence:** Compilation clean; _filters dict absent from source
**Next valid task:** TC-FGSQ-012-03

---

#### TC-FGSQ-012-03 — Implement page breaks: XML read + write + remove dict
**Status:** TODO | **Parent:** TC-FGSQ-012
**Allowed files:** `src/net/fods/FodsDocumentSheetFeatures.cs`

**Micro-steps:**
- MS-012-03-01: Read GetPageBreaks() and SetPageBreak() current implementation
- MS-012-03-02: Add XML read: read `@fo:break-before` attribute on `table:table-row` elements during parse or lazily on first Get call
- MS-012-03-03: Add XML write: SetPageBreak() calls `row.Element.SetAttributeValue(NsFo + "break-before", "page")` or removes attribute
- MS-012-03-04: Remove `_pageBreaks` dict field
- MS-012-03-05: `dotnet build` → 0 errors

**Evidence:** Compilation clean; _pageBreaks dict absent
**Next valid task:** TC-FGSQ-012-04

---

#### TC-FGSQ-012-04 — Implement row groups: XML read + write + remove dict
**Status:** TODO | **Parent:** TC-FGSQ-012
**Allowed files:** `src/net/fods/FodsDocumentSheetFeatures.cs`

**Micro-steps:**
- MS-012-04-01: Read GetRowGroups() and AddRowGroup() current implementation
- MS-012-04-02: Add XML read: read `table:row-group` child elements of `table:table`
- MS-012-04-03: Add XML write: AddRowGroup() adds `table:row-group` element to table XElement
- MS-012-04-04: Remove `_groups` dict field
- MS-012-04-05: `dotnet build` → 0 errors

**Evidence:** Compilation clean; _groups dict absent
**Next valid task:** TC-FGSQ-012-05

---

#### TC-FGSQ-012-05 — Sheet protection: IMPLEMENT (no-password) + UNSUPPORTED (password)
**Status:** TODO | **Parent:** TC-FGSQ-012
**Allowed files:** `src/net/fods/FodsDocumentSheetFeatures.cs`

**Micro-steps:**
- MS-012-05-01: Read SetSheetProtection() and GetSheetProtected() current implementations
- MS-012-05-02: Implement XML read: read `table:table-protection/@table:protected` boolean attribute
- MS-012-05-03: Implement XML write: SetSheetProtected(sheetName, protected) writes `table:table-protection` element with `table:protected="true/false"`
- MS-012-05-04: For password parameter: throw NotSupportedException("Password-protected sheet protection requires SHA256 hashing per ODF §19.708. This version does not support password protection.")
- MS-012-05-05: Remove `_sheetProtection` and `_sheetProtectionPasswords` dict fields
- MS-012-05-06: `dotnet build` → 0 errors

**Evidence:** Compilation clean; dict fields absent; NotSupportedException path confirmed
**Next valid task:** TC-FGSQ-012-06

---

#### TC-FGSQ-012-06 — Run full test suite
**Status:** TODO | **Parent:** TC-FGSQ-012
**Preconditions:** TC-FGSQ-012-02/03/04/05 all CLOSED

**Micro-steps:**
- MS-012-06-01: Run `dotnet test src/net/fods/FormatFactory.Fods.csproj` → capture output
- MS-012-06-02: If failures: triage each failure; fix in the appropriate TC-012-0N (do not bundle fixes)
- MS-012-06-03: Confirm 0 failures; record pass count

**Evidence:** Test output; 0 failures confirmed
**Next valid task:** TC-FGSQ-020 (add roundtrip tests for TC-012 implementations)

---

### TC-FGSQ-013 — Resolve All TODO(GI-FODS-NET-*) Stubs
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-013
**Dependencies:** All Lane B CLOSED; TC-FGSQ-001 CLOSED (method ledger needed)
**Blocks:** TC-FGSQ-016

**Decision table:**
| GI item | Dict fields | Decision | Rationale |
|---|---|---|---|
| GI-003 (password) | password dict | UNSUPPORTED | SHA256 out of scope |
| GI-006 (charts) | `_charts` | UNSUPPORTED | chart:chart is complex Draw extension |
| GI-007 (condFormats) | `_conditionalFormats` | UNSUPPORTED | complex; no confirmed demand |
| GI-008 (dataValidation) | `_dataValidations` | IMPLEMENT | table:content-validation well-specified |
| GI-009 (hyperlinks) | `_cellHyperlinks`, `_hyperlinks` | IMPLEMENT | text:a straightforward |
| GI-010 (rowHeights) | `_rowHeights` | IMPLEMENT | table:default-row-height trivial attribute |
| GI-011 (namedRanges) | `_namedRanges` | IMPLEMENT | table:named-expressions well-specified |
| GI-012 (pivot/sparklines) | `_sheetPivotTables`, `_pivotTables`, `_sheetSparklines`, `_sparklines` | UNSUPPORTED | not in ODF 1.3 |

**Children:**
- TC-FGSQ-013-01: UNSUPPORTED — charts (GI-006): remove dict; throw NSE; add test
- TC-FGSQ-013-02: UNSUPPORTED — condFormats (GI-007): remove dict; throw NSE; add test
- TC-FGSQ-013-03: UNSUPPORTED — pivot/sparklines (GI-012): remove all 4 dicts; throw NSE; add tests
- TC-FGSQ-013-04: IMPLEMENT — data validation (GI-008): XML read+write+remove dict+roundtrip test
- TC-FGSQ-013-05: IMPLEMENT — hyperlinks (GI-009): XML read+write+remove dicts+roundtrip test (add preservation test first — R1 risk)
- TC-FGSQ-013-06: IMPLEMENT — row heights (GI-010): XML read+write+remove dict+roundtrip test
- TC-FGSQ-013-07: IMPLEMENT — named ranges (GI-011): XML read+write+remove dict+roundtrip test
- TC-FGSQ-013-08: Run full test suite; confirm 0 failures

**Parent acceptance criteria:**
- Zero GI-FODS-NET-* TODO comments remain in src/net/fods/
- All UNSUPPORTED methods throw NotSupportedException with ODF reference
- All IMPLEMENTED methods have roundtrip tests
- All dict fields listed above are absent from src/net/fods/
- `dotnet test` → 0 failures

---

#### TC-FGSQ-013-01 — UNSUPPORTED: charts (remove _charts; NotSupportedException)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentDataAnnotations.cs`

**Micro-steps:**
- MS-013-01-01: Read all GetChartTitle() and related chart methods in DataAnnotations.cs
- MS-013-01-02: Replace GetChartTitle() body with: `throw new NotSupportedException("Chart access is not supported. chart:chart objects require the ODF Draw namespace (§9.8) and are not implemented in this version.");`
- MS-013-01-03: Remove `_charts` private dictionary field and its initialization
- MS-013-01-04: Remove `// STUB: no ODF XML path for chart objects` comment (replaced by NSE)
- MS-013-01-05: Remove TODO(GI-FODS-NET-006) comment
- MS-013-01-06: `dotnet build` → 0 errors

**Evidence:** Build clean; _charts absent; NSE in GetChartTitle body
**Next valid task:** TC-FGSQ-013-02 (parallel-safe)

---

#### TC-FGSQ-013-02 — UNSUPPORTED: conditional formats (remove _conditionalFormats)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentDataAnnotations.cs`

**Micro-steps:**
- MS-013-02-01: Read GetConditionalFormats() and AddConditionalFormat() in DataAnnotations.cs
- MS-013-02-02: Replace both methods with NotSupportedException("Conditional formats are not supported...")
- MS-013-02-03: Remove `_conditionalFormats` dict field
- MS-013-02-04: Remove STUB and TODO(GI-FODS-NET-007) comments
- MS-013-02-05: `dotnet build` → 0 errors

**Evidence:** Build clean; _conditionalFormats absent
**Next valid task:** TC-FGSQ-013-03 (parallel-safe)

---

#### TC-FGSQ-013-03 — UNSUPPORTED: pivot tables and sparklines (remove 4 dicts)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentDataAnnotations.cs`

**Micro-steps:**
- MS-013-03-01: Remove `_sheetPivotTables`, `_pivotTables`, `_sheetSparklines`, `_sparklines` dicts
- MS-013-03-02: Replace all associated Get/Set/Add methods with NotSupportedException("Pivot tables/sparklines are not part of ODF 1.3 and are not supported.")
- MS-013-03-03: Remove all TODO(GI-FODS-NET-012) comments and STUB comments for these features
- MS-013-03-04: `dotnet build` → 0 errors

**Evidence:** Build clean; all 4 dicts absent
**Next valid task:** TC-FGSQ-013-04 (parallel-safe with 01-03)

---

#### TC-FGSQ-013-04 — IMPLEMENT: data validation (GI-008)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentDataAnnotations.cs`
**Risk:** R2 variant — data-validation XML must match ODF §11.4 exactly

**Micro-steps:**
- MS-013-04-01: Read ODF §11.4 table:content-validation specification (element name, attributes, child structure)
- MS-013-04-02: Implement XML read: during FodsDocument Load, parse `table:content-validations/table:content-validation` elements; store as ParsedDataValidation list in a parsed-state field (not dict)
- MS-013-04-03: Implement GetDataValidations(sheetName) to query parsed list by sheet
- MS-013-04-04: Implement AddDataValidation() to add `table:content-validation` XElement to the document
- MS-013-04-05: Remove `_dataValidations` dict field
- MS-013-04-06: `dotnet build` → 0 errors

**Evidence:** Build clean; _dataValidations absent; XML read/write paths implemented
**Next valid task:** TC-FGSQ-013-05

---

#### TC-FGSQ-013-05 — IMPLEMENT: hyperlinks (GI-009) — add preservation test FIRST
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentDataAnnotations.cs`, `tests/net/fods/`
**Risk:** R1 — adding text:a inside text:p may affect cell content parsing. Preservation test required before implementation.

**Micro-steps:**
- MS-013-05-01: **BEFORE IMPLEMENTATION**: write preservation test `test_hyperlink_impl_preserves_plain_cells()` — load a FODS document with plain text cells; confirm no text:a introduced; run test → must PASS before any implementation
- MS-013-05-02: Implement XML read: parse `text:p/text:a` within table:table-cell; extract href and display text
- MS-013-05-03: Implement GetCellHyperlink(sheetName, row, col) to return (url, display) from parsed XElement
- MS-013-05-04: Implement SetCellHyperlink(sheetName, row, col, url, display) to write `text:a` into the cell's text:p XElement
- MS-013-05-05: Remove `_cellHyperlinks` and `_hyperlinks` dict fields
- MS-013-05-06: Run preservation test again → still PASS (confirms no regression)
- MS-013-05-07: `dotnet build` → 0 errors

**Evidence:** Preservation test pass before and after; build clean; dicts absent
**Next valid task:** TC-FGSQ-013-06

---

#### TC-FGSQ-013-06 — IMPLEMENT: row heights (GI-010)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentEditOps.cs`, `src/net/fods/FodsDocumentReadOps.cs`

**Micro-steps:**
- MS-013-06-01: Read current SetRowHeight() in EditOps.cs — note the TODO(GI-FODS-NET-010) comment
- MS-013-06-02: Implement XML write: in SetRowHeight(), call `rowElement.SetAttributeValue(NsTable + "default-row-height", height + "cm")` (or unit as defined by ODF §9.4.4)
- MS-013-06-03: Implement XML read: GetRowHeight(sheetName, rowIndex) reads `table:table-row/@table:default-row-height` attribute from XElement
- MS-013-06-04: Remove `_rowHeights` dict field from FodsDocumentReadOps.cs
- MS-013-06-05: Remove TODO(GI-FODS-NET-010) comment
- MS-013-06-06: `dotnet build` → 0 errors

**Evidence:** Build clean; _rowHeights absent; XML attribute set in SetRowHeight
**Next valid task:** TC-FGSQ-013-07

---

#### TC-FGSQ-013-07 — IMPLEMENT: named ranges (GI-011)
**Status:** TODO | **Parent:** TC-FGSQ-013
**Allowed files:** `src/net/fods/FodsDocumentEditOps.cs`, `src/net/fods/FodsDocumentReadOps.cs`

**Micro-steps:**
- MS-013-07-01: Read current DefineNamedRange() / GetNamedRange() in EditOps.cs
- MS-013-07-02: Implement XML read: parse `table:named-expressions/table:named-range` elements; store as parsed list (not dict)
- MS-013-07-03: Implement GetNamedRange(name) to query parsed list
- MS-013-07-04: Implement DefineNamedRange(name, cellRange) to write `table:named-range` element under `table:named-expressions`
- MS-013-07-05: Remove `_namedRanges` dict field
- MS-013-07-06: Remove TODO(GI-FODS-NET-011) comment
- MS-013-07-07: `dotnet build` → 0 errors

**Evidence:** Build clean; _namedRanges absent; XML read/write paths implemented
**Next valid task:** TC-FGSQ-013-08

---

#### TC-FGSQ-013-08 — Run full test suite
**Status:** TODO | **Parent:** TC-FGSQ-013
**Preconditions:** TC-FGSQ-013-01 through TC-FGSQ-013-07 all CLOSED

**Micro-steps:**
- MS-013-08-01: Run `dotnet test src/net/fods/FormatFactory.Fods.csproj`
- MS-013-08-02: Triage any failures (may be tests that expected dict-backed defaults)
- MS-013-08-03: For failures expecting now-removed behavior: fix tests to expect NSE or correct XML-backed value
- MS-013-08-04: Confirm 0 failures; record pass count

**Evidence:** 0 failures; pass count recorded
**Next valid task:** TC-FGSQ-020 (roundtrip tests)

---

### TC-FGSQ-014 — Verify Category B XML Grounding Is Real
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-014
**Dependencies:** All Lane B CLOSED
**Note:** This may discover additional gaps requiring TC-FGSQ-013 extension.

**Objective:** For each of the 18 Category B cell-styling dict fields, confirm getter reads from FodsStyleResolver/XElement and setter writes via FodsStyleEditor/SetAttributeValue, not from the dict directly.

**Children:**
- TC-FGSQ-014-01: List all _cell* dict fields in CellProps.cs and CellStyle.cs
- TC-FGSQ-014-02: Trace each getter to confirm XML source
- TC-FGSQ-014-03: Trace each setter to confirm XML write path
- TC-FGSQ-014-04: For any failures: create new gap entry and extend TC-FGSQ-013

---

#### TC-FGSQ-014-01 — List all _cell* dict fields
**Status:** TODO | **Parent:** TC-FGSQ-014

**Micro-steps:**
- MS-014-01-01: Read FodsDocumentCellProps.cs completely; extract all `private.*Dictionary<.*_cell.*` field declarations
- MS-014-01-02: Read FodsDocumentCellStyle.cs; extract same
- MS-014-01-03: Build comprehensive list: field name, type, file, line number (expected ~18 fields)

**Evidence:** Comprehensive dict field list with file:line
**Next valid task:** TC-FGSQ-014-02

---

#### TC-FGSQ-014-02 — Trace each getter
**Status:** TODO | **Parent:** TC-FGSQ-014
**Preconditions:** TC-FGSQ-014-01 CLOSED

**Micro-steps:**
- MS-014-02-01: For each `_cell*` field: find its corresponding Get method
- MS-014-02-02: Read Get method body: does it call FodsStyleResolver.GetXxx() or read XElement? → PASS
- MS-014-02-03: Or does it return `_cellXxx[key]` directly? → FAIL (still dict-backed)
- MS-014-02-04: Record PASS/FAIL per field in `category-b-verification.yaml`

**Evidence:** category-b-verification.yaml with PASS/FAIL per field
**Next valid task:** TC-FGSQ-014-03

---

#### TC-FGSQ-014-03 — Trace each setter
**Status:** TODO | **Parent:** TC-FGSQ-014
**Preconditions:** TC-FGSQ-014-01 CLOSED

**Micro-steps:**
- MS-014-03-01: For each `_cell*` field: find its corresponding Set method
- MS-014-03-02: Read Set method body: calls FodsStyleEditor.SetXxx() or SetAttributeValue → PASS
- MS-014-03-03: Or only assigns `_cellXxx[key] = value` → FAIL
- MS-014-03-04: Record PASS/FAIL per field in category-b-verification.yaml

**Evidence:** category-b-verification.yaml updated with setter results
**Next valid task:** TC-FGSQ-014-04

---

#### TC-FGSQ-014-04 — Create gaps for failures; extend TC-013 if needed
**Status:** TODO | **Parent:** TC-FGSQ-014
**Preconditions:** TC-FGSQ-014-02 and TC-FGSQ-014-03 CLOSED

**Micro-steps:**
- MS-014-04-01: Count getter-FAIL and setter-FAIL fields
- MS-014-04-02: If any failures: add each to product-code-gap-ledger.yaml as a new gap (PCG-new-NNN)
- MS-014-04-03: For each new gap: add corresponding implementation taskcard to TC-FGSQ-013 (extend with child TC-FGSQ-013-09, -10, etc.)
- MS-014-04-04: If zero failures: record CATEGORY_B_FULLY_VERIFIED in category-b-verification.yaml

**Evidence:** category-b-verification.yaml showing CATEGORY_B_FULLY_VERIFIED or list of failures with gap IDs
**Next valid task:** TC-FGSQ-015

---

### TC-FGSQ-015 — Resolve GetSheetRightToLeft() Hardcoded False
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-015
**Dependencies:** All Lane B CLOSED
**Scope:** `src/net/fods/FodsDocumentCellProps.cs:~299` only

**Objective:** Replace `return false;` with `throw new NotSupportedException(...)`. Remove related tests; add exception test.

**Children:**
- TC-FGSQ-015-01: Read and confirm current implementation
- TC-FGSQ-015-02: Replace return false with NotSupportedException
- TC-FGSQ-015-03: Update tests

---

#### TC-FGSQ-015-01 — Read and confirm current implementation
**Status:** TODO | **Parent:** TC-FGSQ-015

**Micro-steps:**
- MS-015-01-01: Read FodsDocumentCellProps.cs around line 299
- MS-015-01-02: Confirm method signature: `public bool GetSheetRightToLeft(string sheetName)`
- MS-015-01-03: Confirm body is `return false;` with comment about style:writing-mode
- MS-015-01-04: Find any existing tests for GetSheetRightToLeft in tests/net/fods/

**Evidence:** Method signature confirmed; current behavior confirmed; test file(s) found
**Next valid task:** TC-FGSQ-015-02

---

#### TC-FGSQ-015-02 — Replace with NotSupportedException
**Status:** TODO | **Parent:** TC-FGSQ-015
**Allowed files:** `src/net/fods/FodsDocumentCellProps.cs`

**Micro-steps:**
- MS-015-02-01: Replace `return false;` with:
  `throw new NotSupportedException("Right-to-left writing direction is a style property in ODF (style:writing-mode per ODF §15.5) and cannot be queried at the document configuration level in this version.");`
- MS-015-02-02: Remove `// STUB: writing-mode is a style attribute...` comment
- MS-015-02-03: `dotnet build src/net/fods/` → 0 errors

**Evidence:** Build clean; NotSupportedException in method body
**Next valid task:** TC-FGSQ-015-03

---

#### TC-FGSQ-015-03 — Update tests
**Status:** TODO | **Parent:** TC-FGSQ-015
**Preconditions:** TC-FGSQ-015-02 CLOSED

**Micro-steps:**
- MS-015-03-01: Find existing test asserting `GetSheetRightToLeft()` returns false → remove or replace
- MS-015-03-02: Add new test: `Assert.Throws<NotSupportedException>(() => doc.GetSheetRightToLeft("Sheet1"))`
- MS-015-03-03: Run the new test → must PASS

**Evidence:** New test passes; old test removed
**Next valid task:** TC-FGSQ-016

---

### TC-FGSQ-016 — Remove FodsDocumentExtendedApis.cs
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-016
**Dependencies:** TC-FGSQ-012 CLOSED, TC-FGSQ-013 CLOSED, TC-FGSQ-014 CLOSED, TC-FGSQ-015 CLOSED
**STOP CONDITION:** Do NOT proceed if any of TC-012/013/014/015 have unresolved failures.

**Objective:** Delete FodsDocumentExtendedApis.cs from the repository after confirming all methods are disposed.

**Children:**
- TC-FGSQ-016-01: Verify all methods in ExtendedApis.cs are disposed (from TC-001 method ledger)
- TC-FGSQ-016-02: Confirm test suite passes with file still present
- TC-FGSQ-016-03: Delete file; confirm build and tests still pass
- TC-FGSQ-016-04: Update gap ledger and source-structure-baseline.json

---

#### TC-FGSQ-016-01 — Verify all methods disposed
**Status:** TODO | **Parent:** TC-FGSQ-016

**Micro-steps:**
- MS-016-01-01: Read fods-missing-methods-origin.yaml (from TC-001)
- MS-016-01-02: For each method with disposition COLLECTION_STUB_DECIDE: confirm TC-012 closed it (XML-backed or removed)
- MS-016-01-03: For each method with disposition TODO_STUB_DECIDE: confirm TC-013 closed it (XML-backed or NSE)
- MS-016-01-04: For each method with disposition HARDCODED_FALSE: confirm TC-015 addressed it
- MS-016-01-05: For each method with disposition IMPLEMENTED_VERIFY: confirm TC-014 verified it
- MS-016-01-06: If any method is NOT disposed: STOP — do not proceed to deletion; open a new child taskcard

**Evidence:** Verification against method ledger; zero unresolved methods
**Next valid task:** TC-FGSQ-016-02 (only if zero unresolved)

---

#### TC-FGSQ-016-02 — Full test suite pre-deletion check
**Status:** TODO | **Parent:** TC-FGSQ-016
**Preconditions:** TC-FGSQ-016-01 CLOSED with zero unresolved

**Micro-steps:**
- MS-016-02-01: Run `dotnet test src/net/fods/FormatFactory.Fods.csproj` → must be 0 failures
- MS-016-02-02: Record pass count as pre-deletion baseline

**Evidence:** 0 failures; pass count recorded
**Next valid task:** TC-FGSQ-016-03

---

#### TC-FGSQ-016-03 — Delete file; verify build and tests
**Status:** TODO | **Parent:** TC-FGSQ-016
**Preconditions:** TC-FGSQ-016-02 CLOSED with 0 failures

**Micro-steps:**
- MS-016-03-01: Delete `src/net/fods/FodsDocumentExtendedApis.cs`
- MS-016-03-02: `dotnet build src/net/fods/` → must be 0 errors
- MS-016-03-03: Run `dotnet test src/net/fods/FormatFactory.Fods.csproj` → must be 0 failures
- MS-016-03-04: If failures: restore file (`git restore`), triage, fix root cause in parent TC-012/013/014/015, then retry deletion

**Evidence:** File absent; build 0 errors; test 0 failures
**Next valid task:** TC-FGSQ-016-04

---

#### TC-FGSQ-016-04 — Update gap ledger and baseline
**Status:** TODO | **Parent:** TC-FGSQ-016
**Preconditions:** TC-FGSQ-016-03 CLOSED

**Micro-steps:**
- MS-016-04-01: Update `reports/product-quality/product-code-gap-ledger.yaml` PCG-002 status from OPEN to CLOSED; add `closed_date: "2026-07-10"` and `closed_reason: "file deleted; all methods disposed"`
- MS-016-04-02: Update `registry/source-structure-baseline.json`: remove entry for `src/net/fods/FodsDocumentExtendedApis.cs`
- MS-016-04-03: Verify both YAMLs/JSONs parse after edits

**Evidence:** PCG-002 CLOSED in ledger; file absent from baseline; YAML/JSON parse clean
**Next valid task:** TC-FGSQ-017

---

### TC-FGSQ-017 — Reduce LOC Violations in FodsDocument.cs and FodsDocumentReadOps.cs
**Status:** PROPOSED | **Type:** PARENT | **Lane:** C
**REQ:** REQ-FGSQ-017
**Dependencies:** TC-FGSQ-013 CLOSED (dict-field removals will reduce LOC automatically)
**Note:** Many methods removed in TC-013 will reduce LOC. Measure before deciding if further action needed.

**Children:**
- TC-FGSQ-017-01: Re-measure LOC after TC-013 removals
- TC-FGSQ-017-02: If still above 800: identify and move excess methods
- TC-FGSQ-017-03: Update baseline_loc_cap (downward only)

---

#### TC-FGSQ-017-01 — Re-measure LOC
**Status:** TODO | **Parent:** TC-FGSQ-017
**Preconditions:** TC-FGSQ-013 CLOSED

**Micro-steps:**
- MS-017-01-01: Count LOC in `src/net/fods/FodsDocument.cs` (wc -l or python len(open().readlines()))
- MS-017-01-02: Count LOC in `src/net/fods/FodsDocumentReadOps.cs`
- MS-017-01-03: Record new counts; compare with pre-TC-013 baseline (907 and 892 respectively)
- MS-017-01-04: If FodsDocument.cs ≤800 AND FodsDocumentReadOps.cs ≤800: skip TC-017-02; proceed to TC-017-03

**Evidence:** Post-TC-013 LOC counts recorded
**Next valid task:** TC-FGSQ-017-02 (if either exceeds 800) or TC-FGSQ-017-03 (if both ≤800)

---

#### TC-FGSQ-017-02 — Move excess methods to appropriate partial files
**Status:** TODO | **Parent:** TC-FGSQ-017 | **CONDITION:** Only if TC-017-01 shows either file > 800 LOC
**Allowed files:** Any `src/net/fods/FodsDocument*.cs` EXCEPT creating new files

**Micro-steps:**
- MS-017-02-01: For FodsDocument.cs if >800: identify methods that logically belong in ReadOps/EditOps/CellProps/SheetFeatures
- MS-017-02-02: Move identified methods to appropriate existing partial class files (cut from FodsDocument.cs; paste in target)
- MS-017-02-03: Verify moved methods compile in new location: `dotnet build` → 0 errors
- MS-017-02-04: For FodsDocumentReadOps.cs if >800: same process, moving methods to CellProps/EditOps
- MS-017-02-05: Re-measure LOC; confirm both files ≤800

**Evidence:** Both files ≤800 LOC; build 0 errors
**Next valid task:** TC-FGSQ-017-03

---

#### TC-FGSQ-017-03 — Update baseline_loc_cap downward only
**Status:** TODO | **Parent:** TC-FGSQ-017
**Allowed files:** `registry/source-structure-baseline.json`
**Preconditions:** TC-FGSQ-017-01 or TC-FGSQ-017-02 CLOSED

**Micro-steps:**
- MS-017-03-01: Read current baseline entries for FodsDocument.cs and FodsDocumentReadOps.cs
- MS-017-03-02: For each file: update `loc` field to new measured value; update `baseline_loc_cap` to new value (ONLY if new value is LOWER than current baseline_loc_cap)
- MS-017-03-03: Do NOT increase baseline_loc_cap even if the file grew temporarily
- MS-017-03-04: Verify JSON parses after update

**Evidence:** Updated baseline with lower or equal loc_cap; JSON parse clean
**Next valid task:** TC-FGSQ-018 (Lane D, parallel) or TC-FGSQ-019 (Lane E)

---

## Lane D — Python FODS Architecture Repair

> Parallel with Lane C. No Lane B dependency (Python files; different validators).

---

### TC-FGSQ-018 — Fix Python FODS PCG-003/004/005
**Status:** PROPOSED | **Type:** PARENT | **Lane:** D
**REQ:** REQ-FGSQ-018
**Dependencies:** None (parallel with Lane C)

**Objective:** Close PCG-003/004/005 by renaming three files, removing a module-level spec_qname, replacing wildcard imports with explicit imports, and adding `__all__` to __init__.py.

**Children:**
- TC-FGSQ-018-01: Rename spreadsheet_document.py → fods_analytics.py; remove module-level spec_qname
- TC-FGSQ-018-02: Rename spreadsheet_model_document.py → fods_analytics_extended.py
- TC-FGSQ-018-03: Rename neutral_model.py → model.py; replace wildcard imports; add __all__
- TC-FGSQ-018-04: Update all test imports; sync site-packages; run tests

---

#### TC-FGSQ-018-01 — Rename spreadsheet_document.py; remove spec_qname
**Status:** TODO | **Parent:** TC-FGSQ-018
**Allowed files:** `src/python/fods/spreadsheet_document.py` → `src/python/fods/fods_analytics.py`

**Micro-steps:**
- MS-018-01-01: Read spreadsheet_document.py; locate `spec_qname = 'office:document'` at module scope
- MS-018-01-02: Create fods_analytics.py as copy of spreadsheet_document.py with:
  - Module docstring updated to "fods_analytics.py — Analytics functions for FODS format"
  - Module-level spec_qname line removed
- MS-018-01-03: Verify fods_analytics.py has no module-level spec_qname (grep confirm)
- MS-018-01-04: Delete spreadsheet_document.py

**Evidence:** fods_analytics.py exists; spec_qname line absent; spreadsheet_document.py absent
**Next valid task:** TC-FGSQ-018-02

---

#### TC-FGSQ-018-02 — Rename spreadsheet_model_document.py
**Status:** TODO | **Parent:** TC-FGSQ-018

**Micro-steps:**
- MS-018-02-01: Rename `src/python/fods/spreadsheet_model_document.py` → `src/python/fods/fods_analytics_extended.py`
- MS-018-02-02: Update module docstring to reflect new name
- MS-018-02-03: Delete spreadsheet_model_document.py

**Evidence:** fods_analytics_extended.py exists; spreadsheet_model_document.py absent
**Next valid task:** TC-FGSQ-018-03

---

#### TC-FGSQ-018-03 — Rename neutral_model.py; replace wildcards; add __all__
**Status:** TODO | **Parent:** TC-FGSQ-018

**Micro-steps:**
- MS-018-03-01: Read neutral_model.py; find wildcard imports: `from .spreadsheet_document import *` etc.
- MS-018-03-02: Create `src/python/fods/model.py` with explicit named imports replacing wildcards
- MS-018-03-03: In `src/python/fods/__init__.py`: add explicit `__all__` listing all public names
- MS-018-03-04: Delete neutral_model.py

**Evidence:** model.py exists with explicit imports; __all__ added to __init__.py; wildcards absent
**Next valid task:** TC-FGSQ-018-04

---

#### TC-FGSQ-018-04 — Update test imports; sync site-packages; run tests
**Status:** TODO | **Parent:** TC-FGSQ-018
**Preconditions:** TC-FGSQ-018-01/02/03 all CLOSED

**Micro-steps:**
- MS-018-04-01: Grep all test files for imports from `spreadsheet_document`, `spreadsheet_model_document`, `neutral_model` → list files needing update
- MS-018-04-02: Update each test file: replace old import with new name (fods_analytics, model, etc.)
- MS-018-04-03: If FODS Python is non-editable install: copy new .py files to `.venv/Lib/site-packages/fods/`
- MS-018-04-04: Run `.venv/Scripts/pytest tests/python/fods/` → must be 0 failures
- MS-018-04-05: Run governance validators V65/V77 → both must PASS

**Evidence:** 0 test failures; V65/V77 PASS
**Next valid task:** TC-FGSQ-019

---

## Lane E — Test Reconstruction

> Parallel with Lane F. Depends on Lane C completion.

---

### TC-FGSQ-019 — Classify and Repair Tests for Changed Methods
**Status:** PROPOSED | **Type:** PARENT | **Lane:** E
**REQ:** REQ-FGSQ-019
**Dependencies:** TC-FGSQ-013 CLOSED (know which methods are UNSUPPORTED vs IMPLEMENTED)

**Objective:** Ensure every test in tests/net/fods/ either (a) uses a real FODS fixture file, (b) has a Save/Load cycle, or (c) asserts NotSupportedException. Remove tests that only prove dict-backed defaults.

**Children:**
- TC-FGSQ-019-01: Classify all existing tests (keep / repair / remove)
- TC-FGSQ-019-02: Replace removed tests with NSE assertions for UNSUPPORTED methods
- TC-FGSQ-019-03: Verify remaining tests are real (fixture-based or Save/Load or NSE)
- TC-FGSQ-019-04: Run full test suite

---

#### TC-FGSQ-019-01 — Classify all existing tests
**Status:** TODO | **Parent:** TC-FGSQ-019

**Micro-steps:**
- MS-019-01-01: List all test files in `tests/net/fods/`
- MS-019-01-02: For each test method: determine category:
  - REAL_FIXTURE: loads a .fods file from `tests/fixtures/fods/`
  - REAL_ROUNDTRIP: calls ToFodsXml() or Save() AND LoadFromXml() or Load() in same test
  - NSE_TEST: asserts NotSupportedException on a known-UNSUPPORTED method
  - DICT_DEFAULT: asserts a dict-backed value without Save/Load → REMOVE
  - COMPILATION_ONLY: calls method and asserts nothing meaningful → REMOVE
- MS-019-01-03: Write classification results to `test-classification.yaml`

**Evidence:** test-classification.yaml with all tests classified; DICT_DEFAULT and COMPILATION_ONLY counts recorded
**Next valid task:** TC-FGSQ-019-02

---

#### TC-FGSQ-019-02 — Remove DICT_DEFAULT/COMPILATION_ONLY tests; add NSE assertions
**Status:** TODO | **Parent:** TC-FGSQ-019
**Preconditions:** TC-FGSQ-019-01 CLOSED

**Micro-steps:**
- MS-019-02-01: For each DICT_DEFAULT test for an UNSUPPORTED method: replace with `Assert.Throws<NotSupportedException>(() => ...)`
- MS-019-02-02: For each DICT_DEFAULT test for an IMPLEMENTED method: replace with Save/Load roundtrip pattern OR load from real fixture
- MS-019-02-03: Remove COMPILATION_ONLY tests
- MS-019-02-04: Preserve all FodsGI001CategoryBRoundtripTests.cs tests (these are REAL_ROUNDTRIP)
- MS-019-02-05: `dotnet build` → 0 errors

**Evidence:** Build clean; no DICT_DEFAULT or COMPILATION_ONLY tests remain
**Next valid task:** TC-FGSQ-019-03

---

#### TC-FGSQ-019-03 — Verify remaining tests are real
**Status:** TODO | **Parent:** TC-FGSQ-019
**Preconditions:** TC-FGSQ-019-02 CLOSED

**Micro-steps:**
- MS-019-03-01: Re-classify all remaining tests using same rules as TC-019-01
- MS-019-03-02: Confirm: zero DICT_DEFAULT and zero COMPILATION_ONLY in classification
- MS-019-03-03: Record new totals: REAL_FIXTURE + REAL_ROUNDTRIP + NSE_TEST must account for all tests

**Evidence:** Re-classification showing zero DICT_DEFAULT/COMPILATION_ONLY
**Next valid task:** TC-FGSQ-019-04

---

#### TC-FGSQ-019-04 — Run full test suite
**Status:** TODO | **Parent:** TC-FGSQ-019

**Micro-steps:**
- MS-019-04-01: Run `dotnet test src/net/fods/FormatFactory.Fods.csproj` → 0 failures
- MS-019-04-02: Record new pass count (may be lower than original due to removed tests — expected)
- MS-019-04-03: Confirm test count decreased from removed DICT_DEFAULT tests (sanity check: should not have increased)

**Evidence:** 0 failures; new pass count recorded
**Next valid task:** TC-FGSQ-020

---

### TC-FGSQ-020 — Add Roundtrip Tests for All Newly-Implemented Methods
**Status:** PROPOSED | **Type:** PARENT | **Lane:** E
**REQ:** REQ-FGSQ-020
**Dependencies:** TC-FGSQ-012 CLOSED, TC-FGSQ-013 CLOSED

**Objective:** Add one roundtrip test (Set → ToFodsXml → LoadFromXml → Assert) for each capability newly IMPLEMENTED in TC-012 and TC-013.

**Children:**
- TC-FGSQ-020-01: Filters roundtrip test (TC-012)
- TC-FGSQ-020-02: Page breaks roundtrip test (TC-012)
- TC-FGSQ-020-03: Row groups roundtrip test (TC-012)
- TC-FGSQ-020-04: Sheet protection roundtrip test (TC-012)
- TC-FGSQ-020-05: Data validation roundtrip test (TC-013-04)
- TC-FGSQ-020-06: Hyperlinks roundtrip test (TC-013-05)
- TC-FGSQ-020-07: Row heights roundtrip test (TC-013-06)
- TC-FGSQ-020-08: Named ranges roundtrip test (TC-013-07)
- TC-FGSQ-020-09: Run all new roundtrip tests

Each child micro-step pattern (example for TC-020-07 row heights):
- MS-020-07-01: Add to FodsGI001CategoryCRoundtripTests.cs (or create file):
  ```csharp
  [Fact] public void RT4_RowHeight_Roundtrip() {
    var doc = FodsDocument.CreateNew(); doc.AddSheet("S");
    doc.SetRowHeight("S", 0, 42.5);
    var loaded = FodsDocument.LoadFromXml(doc.ToFodsXml());
    Assert.Equal(42.5, loaded.GetRowHeight("S", 0)); }
  ```
- MS-020-07-02: Run focused test → PASS

**Parent acceptance criteria:** All 8 roundtrip tests pass; 0 failures.

---

## Lane F — Cross-Product Scan

---

### TC-FGSQ-021 — Scan All .NET Products for Semantic-Stub Patterns
**Status:** PROPOSED | **Type:** PARENT | **Lane:** F
**REQ:** REQ-FGSQ-021
**Dependencies:** Lane B CLOSED (validators available for machine-assisted scanning)

**Objective:** Scan all 9 .NET products (csv, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst) for the same patterns found in FODS.

**Scan patterns:** `Dictionary<` private fields + `// STUB` + `return false;` in public methods + `COLLECTION_STUB` comments

**Children:**
- TC-FGSQ-021-01: Scan each product; classify findings
- TC-FGSQ-021-02: Add CONFIRMED findings to gap ledger
- TC-FGSQ-021-03: Write semantic-stub-inventory.yaml

---

#### TC-FGSQ-021-01 — Scan each .NET product
**Status:** TODO | **Parent:** TC-FGSQ-021

**Micro-steps:**
- MS-021-01-01: For each product in [csv, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst]:
  grep `src/net/<product>/*.cs` for dict fields, STUB comments, constant returns
- MS-021-01-02: For each finding: classify CONFIRMED_STUB | LEGITIMATE_CONSTANT | NEEDS_REVIEW
  - CONFIRMED_STUB: dict field with no XML pattern in same class
  - LEGITIMATE_CONSTANT: well-known constant or cache backed by real parsing
  - NEEDS_REVIEW: unclear; requires reading method body
- MS-021-01-03: Record all findings in `semantic-stub-scan-raw.yaml`

**Evidence:** semantic-stub-scan-raw.yaml with findings per product
**Next valid task:** TC-FGSQ-021-02

---

#### TC-FGSQ-021-02 — Add CONFIRMED findings to gap ledger
**Status:** TODO | **Parent:** TC-FGSQ-021
**Preconditions:** TC-FGSQ-021-01 CLOSED

**Micro-steps:**
- MS-021-02-01: For each CONFIRMED_STUB: add new gap entry to product-code-gap-ledger.yaml with gap_id=PCG-NEW-NNN, product, severity, files, symbols, root_cause, status=OPEN
- MS-021-02-02: Do not add LEGITIMATE_CONSTANT findings to gap ledger
- MS-021-02-03: For NEEDS_REVIEW: add with status=NEEDS_REVIEW, not OPEN

**Evidence:** Gap ledger updated with cross-product findings
**Next valid task:** TC-FGSQ-021-03

---

#### TC-FGSQ-021-03 — Write semantic-stub-inventory.yaml
**Status:** TODO | **Parent:** TC-FGSQ-021

**Micro-steps:**
- MS-021-03-01: Write `reports/product-quality/semantic-stub-inventory.yaml` with summary:
  products_scanned, total_findings, confirmed_stubs, legitimate_constants, needs_review
- MS-021-03-02: Add `PRODUCT_LIBRARIES_NOT_SCANNED: 0` counter (9 .NET products = 9/9 scanned)

**Evidence:** semantic-stub-inventory.yaml exists; PRODUCT_LIBRARIES_NOT_SCANNED = 0

---

### TC-FGSQ-022 — Scan All Python Products for Semantic-Stub Patterns
**Status:** PROPOSED | **Type:** PARENT | **Lane:** F
**REQ:** REQ-FGSQ-022
**Dependencies:** TC-FGSQ-018 CLOSED (Python FODS fixed; now scan others)

**Scan patterns:** Module-level `spec_qname` outside class bodies, `from .X import *`, `_analytics` content in domain-named files, missing `__all__`

**Children:**
- TC-FGSQ-022-01: Scan each Python product for patterns
- TC-FGSQ-022-02: Add CONFIRMED findings to gap ledger; write inventory

---

#### TC-FGSQ-022-01 — Scan Python products
**Status:** TODO | **Parent:** TC-FGSQ-022

**Micro-steps:**
- MS-022-01-01: Grep `src/python/` excluding fods (already fixed): `spec_qname\s*=` at module scope → list occurrences
- MS-022-01-02: Grep for `from \.\w+ import \*` → list wildcard imports by file
- MS-022-01-03: For each `_document.py` file: check if it has class definitions (V77 heuristic)
- MS-022-01-04: Record all findings in `python-stub-scan-raw.yaml`

**Evidence:** python-stub-scan-raw.yaml with per-product findings
**Next valid task:** TC-FGSQ-022-02

---

#### TC-FGSQ-022-02 — Add CONFIRMED findings to gap ledger; write inventory
**Status:** TODO | **Parent:** TC-FGSQ-022

**Micro-steps:**
- MS-022-02-01: For each CONFIRMED Python stub: add to gap ledger (PCG-PYTHON-NNN)
- MS-022-02-02: Write Python inventory to semantic-stub-inventory.yaml (append to .NET scan results)
- MS-022-02-03: Record PRODUCT_LIBRARIES_NOT_SCANNED = 0 for Python

**Evidence:** Inventory updated; all Python products documented

---

## Lane G — Certification Repair

---

### TC-FGSQ-023 — Reopen Gate 11 Sub-Criteria Relying on Stub Behavior
**Status:** PROPOSED | **Type:** PARENT | **Lane:** G
**REQ:** REQ-FGSQ-023
**Dependencies:** TC-FGSQ-013 CLOSED (know which capabilities are UNSUPPORTED vs IMPLEMENTED)

**Objective:** Update Gate 11 criteria that referenced chart, conditional format, pivot table, or sparkline capabilities to reflect UNSUPPORTED status. Update coverage denominator.

**Children:**
- TC-FGSQ-023-01: Read Gate 11 criteria for FODS in format-registry.yaml
- TC-FGSQ-023-02: Mark criteria referencing stub-backed capabilities REOPENED
- TC-FGSQ-023-03: Update coverage denominator; write certification notes

---

#### TC-FGSQ-023-01 — Read Gate 11 criteria
**Status:** TODO | **Parent:** TC-FGSQ-023

**Micro-steps:**
- MS-023-01-01: Read `registry/format-registry.yaml` FODS entry; find `release_gates:` section
- MS-023-01-02: List all Gate 11 sub-criteria (G11-C1 through C20 per CLAUDE.md)
- MS-023-01-03: Identify criteria that referenced chart, condformat, pivot, sparkline capabilities

**Evidence:** List of criteria referencing stub-backed capabilities
**Next valid task:** TC-FGSQ-023-02

---

#### TC-FGSQ-023-02 — Mark affected criteria REOPENED
**Status:** TODO | **Parent:** TC-FGSQ-023
**Allowed files:** `registry/format-registry.yaml`

**Micro-steps:**
- MS-023-02-01: For each identified criterion: change status from PASS to REOPENED
- MS-023-02-02: Add note: `reopened_reason: "capability is UNSUPPORTED; criteria counted stub-backed behavior"`
- MS-023-02-03: For IMPLEMENTED capabilities: criteria may remain PASS if roundtrip evidence exists

**Evidence:** Updated format-registry.yaml with REOPENED criteria
**Next valid task:** TC-FGSQ-023-03

---

#### TC-FGSQ-023-03 — Update coverage denominator
**Status:** TODO | **Parent:** TC-FGSQ-023

**Micro-steps:**
- MS-023-03-01: Write to format-registry.yaml FODS certification_notes:
  "4 capabilities IMPLEMENTED with roundtrip evidence: filters, page-breaks, row-heights, named-ranges.
  4 capabilities UNSUPPORTED with explicit NotSupportedException: charts, condFormats, pivots/sparklines, writing-mode.
  N capabilities PASS on roundtrip evidence."
- MS-023-03-02: Verify YAML parses after additions

**Evidence:** Updated certification notes; clear denominator
**Next valid task:** TC-FGSQ-024

---

## Lane H — Pilots and Closure

---

### TC-FGSQ-024 — Run All 10 Required Pilots
**Status:** PROPOSED | **Type:** PARENT | **Lane:** H
**REQ:** REQ-FGSQ-024
**Dependencies:** Lanes C/D/E/F/G all CLOSED

**Children:**
- TC-FGSQ-024-01: Pilot 1 — Existing document inspection (load real FODS, verify values from XML)
- TC-FGSQ-024-02: Pilot 2 — Edit and roundtrip (cell value edit → Save → Load → verify)
- TC-FGSQ-024-03: Pilot 3 — Preservation (edit one property; verify others unchanged)
- TC-FGSQ-024-04: Pilot 4 — Unsupported feature (GetChartTitle() → verify NotSupportedException)
- TC-FGSQ-024-05: Pilot 5 — Invalid domain value (null sheetName → verify ArgumentException)
- TC-FGSQ-024-06: Pilot 6 — Consumer API (use FodsDocument from external consumer test)
- TC-FGSQ-024-07: Pilot 7 — Semantic stub detection (introduce synthetic dict field → V88 fires)
- TC-FGSQ-024-08: Pilot 8 — Suspicious file detection (create temp MissingMethods.cs → V89 fires)
- TC-FGSQ-024-09: Pilot 9 — Certification (run FODS cert suite; verify counts match TC-023)
- TC-FGSQ-024-10: Pilot 10 — Idempotency (re-run validators + tests; verify no changes)

Each pilot child:
**Micro-steps:**
- MS-024-0N-01: Execute the pilot steps as described
- MS-024-0N-02: Record result: PASS | FAIL | BLOCKED_EXTERNAL
- MS-024-0N-03: If FAIL: open issue; do not mark PASS

**Parent acceptance criteria:** All 10 pilots recorded in `reports/product-quality/fods-pilot-results.yaml`; 10/10 PASS or documented BLOCKED_EXTERNAL.

---

### TC-FGSQ-025 — Final Verification and Idempotency
**Status:** PROPOSED | **Type:** PARENT | **Lane:** H
**REQ:** REQ-FGSQ-025
**Dependencies:** TC-FGSQ-024 CLOSED

**Objective:** Confirm all required counters = 0, run everything twice, verify idempotent.

**Children:**
- TC-FGSQ-025-01: Check all required counters from incident completion gate
- TC-FGSQ-025-02: Run .NET tests, Python tests, governance validators
- TC-FGSQ-025-03: Re-run same suite second time; verify identical results (idempotency)
- TC-FGSQ-025-04: Record final verdict

---

#### TC-FGSQ-025-01 — Check all required counters
**Status:** TODO | **Parent:** TC-FGSQ-025

**Micro-steps:**
- MS-025-01-01: Count: methods not reviewed → 0 (from fods-missing-methods-origin.yaml)
- MS-025-01-02: Count: retained APIs without authority → 0 (all IMPLEMENTED have ODF QName; all UNSUPPORTED have NSE)
- MS-025-01-03: Count: retained setters without serialization → 0 (from V88 run: no findings)
- MS-025-01-04: Count: retained getters without parsed state → 0 (from V91 run: no findings)
- MS-025-01-05: Count: fabricated-default-success APIs → 0 (no `return false;` in public methods without whitelist)
- MS-025-01-06: Count: detached product state stores → 0 (no dict fields without XML path)
- MS-025-01-07: Count: MissingMethods-style files → 0 (FodsDocumentExtendedApis.cs absent)
- MS-025-01-08: Count: material findings without gaps → 0 (all findings have PCG-NNN gap entries)
- MS-025-01-09: Count: actionable gaps without tasks → 0 (all OPEN gaps have task_ids)
- MS-025-01-10: Count: product libraries not scanned → 0 (TC-021/022 complete)

**Evidence:** `reports/product-quality/fods-final-verification.yaml` with all counters = 0

---

#### TC-FGSQ-025-02 — Run all test suites and validators (Run 1)
**Status:** TODO | **Parent:** TC-FGSQ-025

**Micro-steps:**
- MS-025-02-01: `dotnet test src/net/fods/` → 0 failures; record count
- MS-025-02-02: `.venv/Scripts/pytest tests/python/fods/` → 0 failures; record count
- MS-025-02-03: `python tools/supervisor/governance_validator_runner.py` → 0 unexpected failures; record output

**Evidence:** Test outputs Run 1; 0 failures each

---

#### TC-FGSQ-025-03 — Re-run (Run 2); verify idempotent
**Status:** TODO | **Parent:** TC-FGSQ-025

**Micro-steps:**
- MS-025-03-01: Re-run `dotnet test` → same pass count as Run 1; 0 failures
- MS-025-03-02: Re-run `.venv/Scripts/pytest` → same pass count; 0 failures
- MS-025-03-03: Re-run governance_validator_runner → same findings as Run 1
- MS-025-03-04: Diff Run 1 and Run 2 outputs → 0 material differences

**Evidence:** Run 2 outputs; diff confirming idempotency

---

#### TC-FGSQ-025-04 — Record final verdict
**Status:** TODO | **Parent:** TC-FGSQ-025

**Micro-steps:**
- MS-025-04-01: Write `reports/product-quality/fods-final-verification.yaml` with:
  verdict, all counters, run1 counts, run2 counts, diff result, date
- MS-025-04-02: Set verdict to PRODUCT_CODE_GOVERNANCE_HEALED_FODS_REBUILT_AND_BACKFILL_VERIFIED if all counters = 0 and idempotency confirmed; otherwise PRODUCT_CODE_GOVERNANCE_OR_FODS_REPAIR_REQUIRES_REWORK

**Evidence:** fods-final-verification.yaml with verdict

---

# PART V — DEPENDENCY DAG

```yaml
execution_dag:
  lane_A:
    TC-001: {depends_on: [], parallel_with: [TC-002]}
    TC-002: {depends_on: [], parallel_with: [TC-001]}

  lane_B_gate: [TC-001, TC-002]  # Both must be CLOSED before Lane B proceeds

  lane_B:
    TC-003: {depends_on: [TC-001], parallel_with: [TC-004, TC-006, TC-007, TC-008, TC-009, TC-010]}
    TC-004: {depends_on: [TC-001], parallel_with: [TC-003, TC-007, TC-008, TC-009, TC-010]}
    TC-005: {depends_on: [TC-003]}  # Reuses method-body extractor from TC-003
    TC-006: {depends_on: [TC-004]}  # Whitelist governance after V87 fix
    TC-007: {depends_on: [], parallel_with: [TC-003, TC-004, TC-008, TC-009, TC-010]}
    TC-008: {depends_on: [], parallel_with: [TC-003, TC-004, TC-007, TC-009, TC-010]}
    TC-009: {depends_on: [], parallel_with: [TC-003, TC-004, TC-007, TC-008, TC-010]}
    TC-010: {depends_on: [], parallel_with: [TC-003, TC-004, TC-007, TC-008, TC-009]}
    TC-011: {depends_on: [TC-002]}  # Gap ledger reconciled before cycle reconciliation wired

  lane_C_gate: [TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-011]

  lane_C:
    TC-012: {depends_on: [lane_C_gate], parallel_with: [TC-013, TC-014, TC-015, TC-018]}
    TC-013: {depends_on: [TC-001, lane_C_gate], parallel_with: [TC-012, TC-014, TC-015, TC-018]}
    TC-014: {depends_on: [lane_C_gate], parallel_with: [TC-012, TC-013, TC-015, TC-018]}
    TC-015: {depends_on: [lane_C_gate], parallel_with: [TC-012, TC-013, TC-014, TC-018]}
    TC-016: {depends_on: [TC-012, TC-013, TC-014, TC-015]}  # Deletion: all must be CLOSED first
    TC-017: {depends_on: [TC-013]}  # LOC reduction after dict-field removals

  lane_D:
    TC-018: {depends_on: [], parallel_with: [TC-012, TC-013, TC-014, TC-015]}

  lane_E:
    TC-019: {depends_on: [TC-013]}  # Test repair after UNSUPPORTED decisions
    TC-020: {depends_on: [TC-012, TC-013]}  # Roundtrip tests after IMPLEMENT decisions

  lane_F:
    TC-021: {depends_on: [lane_C_gate], parallel_with: [TC-022]}  # Validators needed for scanning
    TC-022: {depends_on: [TC-018], parallel_with: [TC-021]}

  lane_G:
    TC-023: {depends_on: [TC-013]}  # Certification after UNSUPPORTED decisions known

  lane_H:
    TC-024: {depends_on: [TC-016, TC-017, TC-018, TC-019, TC-020, TC-021, TC-022, TC-023]}
    TC-025: {depends_on: [TC-024]}

  file_ownership_locks:
    # Only one taskcard may modify each file at a time
    FodsDocumentExtendedApis.cs: [TC-012, TC-013, TC-014, TC-015]  # Shared; coordinate per method
    FodsDocumentDataAnnotations.cs: [TC-013-01, TC-013-02, TC-013-03, TC-013-04, TC-013-05]
    FodsDocumentEditOps.cs: [TC-013-06, TC-013-07]
    FodsDocumentSheetFeatures.cs: [TC-012]
    FodsDocumentCellProps.cs: [TC-014, TC-015]
    governance_validators_dotnet_semantic.py: [TC-003, TC-004, TC-005]  # Serial only
    dotnet-semantic-stub-whitelist.yaml: [TC-004-03, TC-005-03, TC-006-01]  # Serial only
    product-code-gap-ledger.yaml: [TC-002, TC-014, TC-016, TC-021, TC-022]  # Serial only
    sprint_executor_validate.py: [TC-008, TC-009-04]  # Serial only
    autonomous_cycle.py: [TC-011]

  parallel_safe_pairs:
    - [TC-001, TC-002]
    - [TC-003, TC-007]
    - [TC-003, TC-008]
    - [TC-003, TC-009]
    - [TC-003, TC-010]
    - [TC-012, TC-013]
    - [TC-012, TC-014]
    - [TC-012, TC-015]
    - [TC-012, TC-018]
    - [TC-013, TC-018]
    - [TC-021, TC-022]
```

---

# PART VI — STATE MACHINE

```yaml
taskcard_state_machine:
  parent_transitions:
    PROPOSED:
      to: [READY]
      requires: plan section confirmed; no blocking prerequisite taskcards
    READY:
      to: [IN_PROGRESS, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
    IN_PROGRESS:
      to: [CHILDREN_IN_PROGRESS, BLOCKED]
    CHILDREN_IN_PROGRESS:
      to: [INTEGRATION_PENDING, BLOCKED]
      requires: at_least_one_child_in_progress
    INTEGRATION_PENDING:
      to: [VERIFIED, BLOCKED]
      requires: all_mandatory_children_closed
    VERIFIED:
      to: [SCORED]
      requires: parent_acceptance_criteria_met; integration_checks_pass
    SCORED:
      to: [CLOSED, REROUTED]
      requires: all_quality_dimensions_>=_4/5
    CLOSED:
      to: []  # Terminal
      requires: all_mandatory_children_closed; scored_>=4/5; evidence_artifact_exists
    REROUTED:
      to: [IN_PROGRESS]
      requires: reroute_reason_documented; affected_child_reopened
    BLOCKED:
      to: [READY]
      requires: blocker_resolved
    BLOCKED_EXTERNAL:
      to: [READY]
      requires: external_gate_cleared
    DEFERRED_WITH_REASON:
      to: [READY]
      requires: deferral_reason_resolved

  child_transitions:
    TODO:
      to: [READY, DEFERRED_WITH_REASON]
    READY:
      to: [IN_PROGRESS, BLOCKED]
    IN_PROGRESS:
      to: [IMPLEMENTED, BLOCKED]
    IMPLEMENTED:
      to: [VERIFIED]
      requires: evidence_artifact_recorded
    VERIFIED:
      to: [SCORED]
      requires: acceptance_checks_pass
    SCORED:
      to: [CLOSED, REROUTED]
      requires: quality_gates_>=_4/5
    CLOSED:
      to: []  # Terminal
      requires: scored_>=4/5; evidence_artifact_exists
    REROUTED:
      to: [IN_PROGRESS]
    BLOCKED:
      to: [READY]
    BLOCKED_EXTERNAL:
      to: []  # Awaits external gate

  micro_step_transitions:
    PENDING:
      to: [READY, SKIPPED_NOT_APPLICABLE]
    READY:
      to: [ACTIVE]
      requires: parent_child_in_progress; preconditions_met
    ACTIVE:
      to: [COMPLETE, FAILED, BLOCKED]
    COMPLETE:
      to: []  # Terminal
    FAILED:
      to: [READY]
      requires: failure_handled; root_cause_documented
    BLOCKED:
      to: [READY]
    SKIPPED_NOT_APPLICABLE:
      to: []  # Terminal; reason required

  invalid_transitions_hard_blocked:
    - [child_TODO, CLOSED]
    - [child_READY, CLOSED]
    - [child_IMPLEMENTED, CLOSED]  # Must be VERIFIED first
    - [parent_CLOSED, while_any_mandatory_child_not_CLOSED]
    - [parent_SCORED, while_quality_below_4/5]
    - [REROUTED, CLOSED, without_rework_evidence]
    - [BLOCKED_EXTERNAL, CLOSED, without_unblock_evidence]
    - [micro_step_SKIPPED, without_reason]
```

---

# PART VII — VERIFICATION MATRIX

| TC | Check | Command / Method | Expected | Mandatory | Level |
|---|---|---|---|---|---|
| TC-001 | fods-missing-methods-origin.yaml exists | Check file at path | file present; YAML parses | YES | evidence |
| TC-001 | UNCLASSIFIED_METHODS = 0 | Read counters in YAML | 0 | YES | validation |
| TC-002 | All OPEN gaps have existent files | Grep listed paths | All paths exist | YES | integration |
| TC-002 | YAML parses after edits | python -c "import yaml; yaml.safe_load(...)" | No exception | YES | schema |
| TC-003 | V88 fires on SetRowHeight (FodsDocumentEditOps.cs) | Run V88 on file | Finding reported | YES | unit |
| TC-003 | V88 does NOT fire on FodsStyleEditor-backed setter | Run V88 on file | No finding | YES | unit |
| TC-003 | blocks_sprint=True in V88 | Read code | True | YES | source |
| TC-003 | Governance runner exits 0 | python governance_validator_runner.py | Exit 0 | YES | integration |
| TC-004 | New `return false;` in PRODUCT_SOURCE → blocks sprint | Synthetic test | V87 FAIL | YES | unit |
| TC-004 | Whitelisted constant-return → WARN not FAIL | Synthetic test | V87 WARN | YES | unit |
| TC-005 | New dict-only setter → V90 blocks sprint | Synthetic test | V90 FAIL | YES | unit |
| TC-006 | Expired whitelist entry → blocks sprint | Synthetic test (past review_due) | V_WHITELIST_EXPIRY FAIL | YES | unit |
| TC-007 | data_source=unsupported property → oracle D0 | Oracle unit test | depth_level=D0 | YES | unit |
| TC-008 | PERSISTENT_PROPERTY without roundtrip → WARN | Synthetic declaration | Phase 13 WARN | YES | unit |
| TC-009 | New COLLECTION_STUB comment → blocks sprint | Synthetic .cs file | Validator FAIL | YES | unit |
| TC-010 | Goal without spec_fact_id → UNSUPPORTED task | Unit test on generator | Task type=UNSUPPORTED | YES | unit |
| TC-011 | OPEN gap with absent file → drift report | Run cycle mock | gap-ledger-drift.json shows gap | YES | integration |
| TC-012 | No COLLECTION_STUB dict fields in SheetFeatures | Grep _filters,_pageBreaks,_groups,_sheetProtection | 0 occurrences | YES | source |
| TC-012 | dotnet test 0 failures | dotnet test src/net/fods/ | 0 failures | YES | integration |
| TC-013 | No GI-FODS-NET-* TODO comments in src/net/fods/ | Grep TODO(GI-FODS-NET- | 0 occurrences | YES | source |
| TC-013 | All UNSUPPORTED methods throw NSE | Source inspection | NotSupportedException in body | YES | source |
| TC-013 | dotnet test 0 failures | dotnet test src/net/fods/ | 0 failures | YES | integration |
| TC-014 | CATEGORY_B_FULLY_VERIFIED or new gaps created | category-b-verification.yaml | Explicit status | YES | evidence |
| TC-015 | GetSheetRightToLeft throws NSE | dotnet test focused test | Test passes | YES | unit |
| TC-016 | FodsDocumentExtendedApis.cs absent | ls src/net/fods/ | Not in listing | YES | source |
| TC-016 | PCG-002 CLOSED in gap ledger | Read ledger | status=CLOSED | YES | evidence |
| TC-016 | dotnet test 0 failures post-deletion | dotnet test | 0 failures | YES | integration |
| TC-017 | FodsDocument.cs ≤800 LOC | wc -l or python count | ≤800 | YES | source |
| TC-017 | FodsDocumentReadOps.cs ≤800 LOC | wc -l or python count | ≤800 | YES | source |
| TC-018 | V65/V77 PASS for Python FODS | governance_validator_runner.py | V65/V77 PASS | YES | integration |
| TC-018 | pytest tests/python/fods/ 0 failures | pytest | 0 failures | YES | integration |
| TC-019 | Zero DICT_DEFAULT tests remain | Re-run classification | 0 in DICT_DEFAULT category | YES | validation |
| TC-020 | All 8 roundtrip tests pass | dotnet test focused | 8/8 pass | YES | integration |
| TC-021 | PRODUCT_LIBRARIES_NOT_SCANNED = 0 (.NET) | Read inventory YAML | 0 | YES | evidence |
| TC-022 | PRODUCT_LIBRARIES_NOT_SCANNED = 0 (Python) | Read inventory YAML | 0 | YES | evidence |
| TC-023 | No Gate 11 criterion counts UNSUPPORTED as PASS | Read format-registry.yaml | All affected = REOPENED | YES | evidence |
| TC-024 | All 10 pilots recorded | Read fods-pilot-results.yaml | 10 entries | YES | evidence |
| TC-025 | All required counters = 0 (Run 1) | Read fods-final-verification.yaml | All = 0 | YES | validation |
| TC-025 | Idempotency confirmed (Run 2 = Run 1) | Diff outputs | 0 material differences | YES | idempotency |

**Negative control matrix:**

| Scenario | What to introduce | Expected result | Purpose |
|---|---|---|---|
| Semantic stub detection | `private Dictionary<string,string?> _stub = new(); public void SetStub(string k, string v) { _stub[k] = v; }` | V88 fires; V90 fires | Pilot 7 |
| Suspicious filename | Create `src/net/fods/FodsDocumentMissingMethods.cs` (temp) | V89 fires; sprint blocked | Pilot 8 |
| Constant return | `public bool GetXxx() { return false; }` (new, not whitelisted) | V87 fires; sprint blocked | TC-004 regression |
| Expired whitelist | Set review_due to yesterday | V_WHITELIST_EXPIRY fires; sprint blocked | TC-006 regression |
| COLLECTION_STUB comment | `// COLLECTION_STUB: new occurrence` | Validator fires; sprint blocked | TC-009 regression |
| Task without spec ground | Remove spec_fact_id from expansion goal | Goal downgraded to UNSUPPORTED | TC-010 regression |

---

# PART VIII — EVIDENCE CONTRACT

```
evidence_root: reports/product-quality/fods-govheal/

Required evidence artifacts (created during execution):
  run-record.yaml               — generated by TC-025-04
  analysis/
    method-inventory-raw.yaml   — TC-001-01
    getter-trace-results.yaml   — TC-001-02
    setter-trace-results.yaml   — TC-001-03
    disposition-assignment.yaml — TC-001-04
    file-absence-findings.yaml  — TC-002-02
    existing-constant-return-methods.yaml — TC-004-02
    existing-v90-v91-violations.yaml      — TC-005-02
    existing-collection-stubs.yaml        — TC-009-01
    category-b-verification.yaml          — TC-014
    test-classification.yaml              — TC-019-01
    semantic-stub-scan-raw.yaml           — TC-021-01
    python-stub-scan-raw.yaml             — TC-022-01
  decisions/
    collection-stub-decisions.yaml  — TC-012/013 decision tables
    unsupported-capability-list.yaml — all methods → NotSupportedException
  taskcards/
    fods-missing-methods-origin.yaml  — TC-001-05
  validation/
    gap-ledger-drift.json             — TC-011 (generated per cycle)
    task-generation-authority-log.yaml — TC-010
  quality/
    fods-pilot-results.yaml           — TC-024
    fods-final-verification.yaml      — TC-025
  closeout/
    semantic-stub-inventory.yaml      — TC-021/022
    category-b-verification.yaml      — TC-014

Every evidence artifact must include:
  authoritative_plan: plans/.claude/splendid-squishing-orbit.md
  artifact_role: analysis_or_evidence_only
  execution_authority: false
  relevant_taskcard_id: TC-FGSQ-NNN
  relevant_req_id: REQ-FGSQ-NNN
```

---

# PART IX — QUALITY SCORING

```
Required quality dimensions per child taskcard (1–5):
  requirement_correctness:   does this child address the requirement it claims to?
  implementation_correctness: is the implementation semantically correct (not just syntactically)?
  scope_discipline:          did the child touch only allowed files?
  validation_strength:       is the validation command/test adequate to prove the outcome?
  evidence_completeness:     is the evidence artifact present and meaningful?
  regression_safety:         did the child introduce no regressions in existing behavior?
  maintainability:           is the change understandable and maintainable by a future agent?
  production_readiness:      would this change be acceptable in a professional library review?

Acceptance threshold: every mandatory dimension >= 4/5.
Any dimension < 4/5: mark child REROUTED; document weak dimension; create child TC-FGSQ-NNN-RR-01 for rework.

Required quality dimensions per parent taskcard (1–5):
  root_cause_coverage:       does closing this parent address its root cause?
  child_completeness:        are all children present and closed?
  integration_completeness:  do integration checks cover cross-file and cross-component effects?
  dependency_correctness:    are dependencies satisfied before this parent closed?
  preserved_behavior:        did this parent leave all "preserve" items intact?
  evidence_completeness:     are all required evidence artifacts present?
  rerun_consistency:         would a second run produce the same result?
  production_readiness:      would a professional maintainer accept these changes?
```

---

# PART X — EXECUTION HANDOFF

**This section is for the execution agent. Read it before starting any work.**

## Start-of-Session Protocol

1. Read this plan completely. Do not execute from memory.
2. Identify the current state of all 25 parent taskcards (all are PROPOSED at plan creation).
3. Start with Lane A: TC-FGSQ-001 and TC-FGSQ-002 (parallel-safe).
4. After Lane A is CLOSED: start Lane B (all B tasks are parallel-safe within B except TC-003→TC-005 and TC-004→TC-006 sequences).
5. After Lane B is CLOSED: start Lane C (TC-012/013/014/015 parallel-safe; TC-016 depends on all; TC-017 depends on TC-013).
6. TC-018 (Lane D) may run in parallel with Lane C.
7. Lane E (TC-019/020) after TC-013 CLOSED.
8. Lane F (TC-021/022) after TC-018 and Lane B CLOSED.
9. Lane G (TC-023) after TC-013 CLOSED.
10. Lane H (TC-024/025) only after all preceding lanes CLOSED.

## Per-Taskcard Protocol

Before starting any child taskcard:
1. Confirm parent taskcard is IN_PROGRESS or CHILDREN_IN_PROGRESS.
2. Confirm all Preconditions are met.
3. Confirm allowed files only — check `Allowed files:` field.
4. Confirm forbidden scope — do NOT modify product source during Lane B.

During each micro-step:
1. Execute exactly one micro-step.
2. Capture evidence immediately (do not batch evidence).
3. Mark micro-step COMPLETE before starting the next.
4. If micro-step FAILS: stop; document failure; do not proceed to next micro-step; investigate root cause.

After completing all children for a parent:
1. Run parent integration checks.
2. Score all quality dimensions.
3. If any dimension < 4/5: mark parent REROUTED; create rework children.
4. Only after 8/8 quality dimensions ≥ 4/5: mark parent CLOSED.

## Hard Stop Conditions

- STOP if TC-FGSQ-016-01 finds unresolved methods (do not delete ExtendedApis.cs).
- STOP if TC-FGSQ-016-03 `dotnet build` produces errors (restore file; root-cause).
- STOP if any required counter in TC-025-01 is non-zero (find and fix root cause; re-verify).
- STOP at Gate 11 execution (TRUE_EXTERNAL_GATE — Babar Raza sign-off required).

## What Execution Agents Must NOT Do

- Choose work from next-sprint.md while this plan has unclosed taskcards
- Modify product source during Lane B
- Close a parent while mandatory children are non-CLOSED
- Skip micro-steps without documenting SKIPPED_NOT_APPLICABLE + reason
- Treat FodsDocumentExtendedApis.cs deletion as complete before TC-016-01 verifies all methods disposed
- Increase baseline_loc_cap in source-structure-baseline.json
- Mark GetChartTitle or GetConditionalFormats as IMPLEMENTED (these are UNSUPPORTED)
- Treat "test exists" as "test passes" — always run and capture output

## Supporting Artifacts Manifest

The following 46 artifacts are required by the taskcardization protocol. They are created
DURING execution, not before. The content templates are embedded within each taskcard's Evidence fields.

Phase 1 (TC-001 creates these):
  taskcardization-preflight.md → embedded in TC-001 parent acceptance criteria
  active-plan-authority-verdict.md → this plan file IS the authority; no separate artifact needed
  duplicate-plan-risk-check.md → Part I preflight section confirms no duplicates

Phase 2 (TC-001-TC-002 creates these):
  plan-section-inventory.md → this document (Part IV) is the section inventory
  section-processing-ledger.yaml → produced by TC-001-04 disposition-assignment.yaml

Phase 3 (TC-001-TC-013 creates these):
  plan-part-deep-analysis.yaml → each taskcard's Source.Deep-analysis-record field
  actionable-item-extraction-log.yaml → Part III requirements inventory IS this artifact

Phase 4 (TC-003-TC-011 create these):
  solution-options-analysis.md → this plan's "Must Redesign" table + tradeoffs section
  normalized-requirements-inventory.yaml → Part III requirements table

Phase 5 (Execution creates these):
  execution-dag.yaml → Part V (embedded)
  taskcard-state-machine.yaml → Part VI (embedded)
  verification-matrix.md → Part VII (embedded)
  evidence-contract.md → Part VIII (embedded)
  fods-missing-methods-origin.yaml → TC-001-05
  fods-pilot-results.yaml → TC-024
  fods-final-verification.yaml → TC-025
  semantic-stub-inventory.yaml → TC-021/022
  category-b-verification.yaml → TC-014
  gap-ledger-drift.json → TC-011 (per cycle)
  execution-readiness-verdict.md → this execution handoff section

All supporting artifacts must include:
  authoritative_plan: plans/.claude/splendid-squishing-orbit.md
  artifact_role: analysis_or_evidence_only
  execution_authority: false
