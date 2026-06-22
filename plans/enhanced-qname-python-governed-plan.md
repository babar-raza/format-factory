# Governed Plan: QName-Based Class Decomposition, Reviewer Skill, Backfill, and No-Stub Enforcement — All Python Format Packages

## 1. Intent

The current Python format packages must stop growing through codec overflow files and arbitrary `{format}_analytics.py` expansion. Every production feature must be traceable to a spec-backed QName or structural QName, implemented in a governed source hierarchy, exposed through stable public facades, verified by automated reviewers, and backfilled across existing Python products.

This plan converts the existing QName decomposition idea into a mandatory, taskcard-driven, end-to-end execution program. It covers new development, existing product repair, governance enforcement, code-review skill design, backfill, anti-stub policy, evidence, pilots, and final Gate 11 readiness.

The core goal is not to create placeholder spec files. The goal is to make every format package look and behave like a professional library whose code organization, class names, namespaces, tests, and public API are derived from the format specification.

## 2. Non-Negotiable Governance Rules

### 2.1 Mandatory QName Architecture

For every Python format package under `src/python/{format}/`:

1. Codec files are I/O orchestration only.
2. Domain logic belongs in spec-derived modules.
3. Public API objects are exposed through `Compat/` facades.
4. Every production class must declare a canonical QName or structural QName.
5. Every QName must trace to a SAL fact or approved structural fact.
6. Every public facade must map back to one canonical spec class.
7. New functions may not be added to `{format}_analytics.py` or other overflow files.
8. No feature can reach accepted state unless the reviewer skill validates structure, traceability, imports, tests, and no-stub compliance.

### 2.2 No-Stub Policy

The old language “spec stub” is forbidden because a stub means an incomplete or unavailable implementation. Use these terms instead:

- `spec authority class`
- `spec element class`
- `structural element class`
- `canonical spec class`
- `facade class`

A class or file is rejected if it contains or behaves like any of the following:

- `pass` as implementation
- `TODO`, `FIXME`, `stub`, `placeholder`, `not implemented`, `dummy`, `fake`, `mock`, `temporary`, `later`, `future`, `TBD`
- empty methods that claim feature completion
- classes with metadata only when production behavior is required
- generated files without source fact provenance
- facade classes that merely rename incomplete classes
- tests that only assert imports but not behavior when behavior exists

Limited metadata-only classes are allowed only when the spec element has no behavior yet and must be explicitly marked as `authority_only = True`, backed by a SAL fact, and excluded from production readiness claims. These must not be called complete product functionality.

### 2.3 Governance Must Be Unavoidable

The system must make bypassing QName decomposition difficult or impossible:

1. Add governance validators to the supervisor runner.
2. Add pre-merge validation for changed Python format files.
3. Add reviewer-skill gates to taskcard state transitions.
4. Block acceptance if new source files are not registered in the source baseline.
5. Block acceptance if new public APIs are not mapped to a spec or structural QName.
6. Block acceptance if any new code enters analytics overflow files.
7. Block acceptance if any code contains forbidden stub language or incomplete implementation markers.
8. Block acceptance if backfill scope is skipped without an explicit defer record and reason.

## 3. Target Architecture

```text
src/python/{format}/
├── __init__.py
├── {format}_codec.py                 # I/O only: load, save, parse, write orchestration
├── neutral_model.py                  # parse-neutral representation, if needed
├── models.py                         # production behavior shared by facades/spec classes, if needed
├── spec/
│   ├── __init__.py
│   └── {domain}/
│       ├── __init__.py
│       └── {element}.py              # canonical spec/structural element class
└── Compat/
    ├── __init__.py
    └── {format}_{entity}.py          # public facade class
```

### 3.1 Canonical Spec Authority Class

```python
"""
Spec authority: abw:p
Spec ref: AbiWord document format section covering paragraph elements
FACT ref: FACT-ABW-003
Canonical class: Paragraph
Facade: AbwParagraph
"""

class Paragraph:
    spec_qname = "abw:p"
    spec_fact_ref = "FACT-ABW-003"
    namespace_uri = "http://www.abisource.com/awml/"
    local_name = "p"
    facade_names = ["AbwParagraph"]
    authority_only = False
```

### 3.2 Public Compat Facade

```python
from ..spec.document.paragraph import Paragraph as _SpecParagraph

class AbwParagraph(_SpecParagraph):
    """Production public facade for AbiWord paragraph elements."""
```

The facade must not duplicate metadata unless needed to preserve public API behavior. The canonical source of spec metadata is the spec authority class.

## 4. Format Archetypes and Required Coverage

### 4.1 XML Document Formats

| Format | Required domains | Required first-pass QNames |
|---|---|---|
| FODS | office, table, text, style, number | office:document, table:table, table:table-cell, text:p |
| FODT | office, text, table, style | office:document, text:p, text:h, table:table-cell |
| FODG | office, draw, presentation, style | office:document, draw:page, draw:frame, draw:g |
| FODP | office, draw, presentation, style | office:document, draw:page, presentation:show |
| ODS | office, table, text, style, number | office:document, table:table, table:table-row, table:table-cell |
| ODT | office, text, table, style | office:document, text:p, text:h, table:table |
| GNUMERIC | workbook, sheet, cells, style | gnm:Workbook, gnm:Sheet, gnm:Cells, gnm:Row |
| ABW | document | abw:abiword, abw:section, abw:p, abw:c, abw:field |

### 4.2 Text and Tabular Formats

| Format | Required domains | Required first-pass structural QNames |
|---|---|---|
| CSV | record | csv:record, csv:field |
| TSV | record | tsv:record, tsv:field |
| DIF | header, table | dif:header, dif:table, dif:vector, dif:datum |
| NDJSON | record | ndjson:record, ndjson:field |
| TOML | table | toml:table, toml:key, toml:array |
| SYLK | header, row | sylk:header, sylk:row, sylk:cell |

### 4.3 Binary and Image/Archive Formats

| Format | Required domains | Required first-pass structural QNames |
|---|---|---|
| PBM | header, bitmap | pbm:header, pbm:bitmap |
| PGM | header, graymap | pgm:header, pgm:graymap |
| PPM | header, pixmap | ppm:header, ppm:pixmap |
| QOI | header, chunk | qoi:header, qoi:chunk, qoi:index |
| XCF | header, layer, channel, property | xcf:header, xcf:layer, xcf:channel, xcf:property |
| ZST | frame, block | zst:frame, zst:block, zst:magic |

## 5. Reviewer Skill Design

Create a governed code reviewer skill before broad implementation.

### 5.1 Skill Name

`skills/python_qname_code_reviewer/`

### 5.2 Skill Responsibilities

The skill must review every changed Python format package and produce a machine-readable verdict.

It must check:

1. Directory structure follows the canonical template.
2. Codec file remains I/O-only.
3. No new functions were added to analytics overflow files.
4. Every class has a QName or structural QName where applicable.
5. Every QName has a fact reference.
6. Every fact reference exists in SAL fact cache or approved structural fact registry.
7. Every facade inherits from exactly one canonical spec authority class.
8. `__init__.py` exports are stable and backwards compatible.
9. Source files stay below governance LOC caps.
10. Tests cover imports, metadata, behavior, and regression.
11. No forbidden stub/incomplete terms exist in source, tests, docs, or generated reports.
12. Backfill queue is updated for remaining legacy code.
13. Evidence exists for every accepted transition.

### 5.3 Reviewer Verdicts

The skill may return only:

- `ACCEPTED_VERIFIED`
- `REWORK_REQUIRED`
- `BLOCKED_EXTERNAL_AUTHORITY`
- `DEFERRED_WITH_APPROVED_REASON`

No soft-pass is allowed for production code.

### 5.4 Reviewer Evidence Output

Each review run must write:

```text
.local/evidences/{run_id}/python-qname-review/{format}/
├── verdict.json
├── qname-map.json
├── facade-map.json
├── sal-fact-trace.json
├── no-stub-scan.txt
├── import-check.log
├── test-run.log
├── source-baseline-diff.json
└── reviewer-notes.md
```

## 6. Backfill Program for Existing Python Products

The original plan deferred analytics migration. That is no longer acceptable. Existing products must be backfilled through a controlled, iterative program.

### 6.1 Backfill Inventory

Create a full inventory before modifying products:

```text
docs/audits/python-qname-backfill-inventory.csv
```

Required columns:

- format
- file_path
- symbol_name
- current_location
- inferred_domain
- inferred_qname
- source_fact_ref
- public_api_impact
- tests_existing
- tests_needed
- migration_status
- reviewer_verdict
- notes

### 6.2 Backfill Classification

Every existing function/class must be classified as one of:

1. `codec_io` — remains in codec.
2. `spec_element_behavior` — moves to `spec/{domain}/{element}.py` or supporting model.
3. `facade_behavior` — moves to `Compat/` facade.
4. `neutral_model_behavior` — moves to `neutral_model.py`.
5. `utility_private` — moves to internal utility module with no public claim.
6. `dead_or_duplicate` — removed only after test-backed proof.
7. `blocked_by_missing_spec_fact` — queued for SAL fact generation.

### 6.3 Backfill Migration Rules

1. Do not migrate blindly by file size.
2. Do not break public imports.
3. Add compatibility re-exports when moving public symbols.
4. Each migrated behavior must retain or improve test coverage.
5. Each moved symbol must have a before/after location in evidence.
6. Large analytics files must shrink over time; freezing them forever is not acceptable.
7. If a full shrink is too large for one sprint, create a measurable burn-down queue.

### 6.4 Backfill Acceptance Criteria

A format is accepted only when:

1. Inventory exists.
2. All public symbols are classified.
3. At least one real behavior has moved from legacy/analytics location into QName architecture, unless the format had no misplaced behavior.
4. Tests pass.
5. Reviewer skill returns `ACCEPTED_VERIFIED`.
6. Remaining work is recorded as taskcards, not prose.

## 7. SAL and Fact Governance

### 7.1 Fact Source Rules

1. XML formats must use real namespace/local-name facts.
2. Non-XML formats must use approved structural facts.
3. Facts must be generated deterministically, not hand-seeded manually.
4. A class may not claim a fact reference that does not exist.
5. Missing facts block implementation unless the task is explicitly fact-discovery only.

### 7.2 Required Registries

```text
.local/spec-cache/sal-facts-{format}.json
registry/python-qname-architecture.json
registry/python-qname-structural-facts.json
registry/source-structure-baseline.json
```

### 7.3 QName Map Output

Every format must produce:

```text
docs/audits/python-qname/{format}-qname-map.csv
```

Required columns:

- qname
- class_name
- file_path
- facade_name
- sal_fact_ref
- source_spec
- behavior_methods
- tests
- reviewer_status

## 8. Taskcard-Driven State Machine

Every format must move through the same state machine. No format may skip states.

```text
DISCOVERED
  -> INVENTORIED
  -> FACTS_READY
  -> ARCHITECTURE_PLANNED
  -> PILOT_IMPLEMENTED
  -> BACKFILL_STARTED
  -> REVIEWER_VERIFIED
  -> TEST_VERIFIED
  -> GOVERNANCE_VERIFIED
  -> EVIDENCE_PACKAGED
  -> ACCEPTED_VERIFIED
```

### 8.1 Rework States

```text
REWORK_QNAME_TRACE
REWORK_STUB_REMOVAL
REWORK_PUBLIC_API_COMPAT
REWORK_TEST_COVERAGE
REWORK_SOURCE_BASELINE
REWORK_BACKFILL_CLASSIFICATION
BLOCKED_EXTERNAL_SPEC_AUTHORITY
```

### 8.2 Required Taskcard Fields

```yaml
id: PY-QNAME-{FORMAT}-{NNN}
title:
format:
archetype:
state:
owner_lane:
inputs:
outputs:
files_to_change:
files_forbidden_to_change:
sal_facts_required:
qnames_required:
public_api_contract:
backfill_scope:
reviewer_skill_required: true
no_stub_scan_required: true
tests_required:
governance_validators_required:
evidence_path:
acceptance_criteria:
rework_history:
final_verdict:
```

### 8.3 State Transition Rule

A state transition is valid only when:

1. Required files exist.
2. Required evidence exists.
3. Reviewer skill verdict allows transition.
4. Tests pass for the affected package.
5. Governance runner passes or records a blocking failure.
6. No forbidden stub/incomplete markers are present.

## 9. Execution Lanes

### 9.1 Coordinator Lane

Responsibilities:

- Maintain master taskcard board.
- Prevent duplicate or conflicting migrations.
- Assign formats to lanes.
- Merge reviewer evidence.
- Stop unsafe changes.
- Produce final status matrix.

### 9.2 Skill Lane

Responsibilities:

- Build reviewer skill.
- Build no-stub scanner.
- Build QName/facade/fact validators.
- Add tests for reviewer skill itself.

### 9.3 SAL Lane

Responsibilities:

- Generate or validate facts.
- Maintain SAL fact cache.
- Reject manual/fabricated facts.
- Provide missing-fact queues.

### 9.4 Product Pilot Lane

Responsibilities:

- Complete FODT Compat.
- Implement ABW pilot.
- Prove architecture end-to-end.

### 9.5 Backfill Lane

Responsibilities:

- Inventory existing Python packages.
- Classify current symbols.
- Migrate misplaced behavior incrementally.
- Burn down analytics overflow usage.

### 9.6 Verification Lane

Responsibilities:

- Run tests.
- Run governance runner.
- Run reviewer skill.
- Verify evidence completeness.
- Produce adversarial review.

## 10. Implementation Sequence

### Phase 0 — Readiness and Baseline

Deliverables:

1. Current source structure inventory.
2. Current public API inventory.
3. Current analytics overflow inventory.
4. Current SAL fact inventory.
5. Current test coverage map.
6. Current no-stub scan report.
7. Taskcard board initialized.

Acceptance:

- No code changes accepted yet.
- Baseline evidence exists.
- Formats are assigned to archetypes.

### Phase 1 — Governance and Reviewer Skill

Deliverables:

1. `skills/python_qname_code_reviewer/` implemented.
2. No-stub scanner implemented.
3. QName validator implemented.
4. Facade inheritance validator implemented.
5. SAL fact existence validator implemented.
6. Analytics-change blocker implemented.
7. Source-baseline registration validator implemented.
8. Unit tests and pilot fixtures for all validators.

Acceptance:

- Reviewer skill can reject bad fixtures.
- Reviewer skill can accept known-good FODS pattern.
- Governance runner invokes reviewer skill.

### Phase 2 — FODT Completion

Deliverables:

1. Add missing `Compat/` layer for FODT.
2. Re-export stable public API.
3. Confirm existing FODT spec classes are complete and not stubs.
4. Add/repair tests.
5. Reviewer skill accepts FODT.

Acceptance:

- FODT reaches `ACCEPTED_VERIFIED` for architecture completion.

### Phase 3 — ABW Pilot

Deliverables:

1. Generate or validate ABW SAL facts.
2. Add ABW spec authority classes.
3. Add ABW Compat facades.
4. Move at least one real ABW behavior into the QName architecture if currently misplaced.
5. Preserve public API.
6. Add import, metadata, behavior, and regression tests.
7. Reviewer skill accepts ABW.

Acceptance:

- ABW proves the pattern for a currently incomplete XML package.

### Phase 4 — ODF Drawing and Presentation

Formats:

- FODG
- FODP

Deliverables:

1. Spec domains: office, draw, presentation, style.
2. Compat facades.
3. Backfill inventory.
4. Migration of at least one real misplaced behavior per format.
5. Tests and reviewer evidence.

### Phase 5 — Spreadsheet XML

Formats:

- ODS
- GNUMERIC

Deliverables:

1. Spec domains and facts.
2. Facades for workbook/sheet/cell entities.
3. Existing public API compatibility.
4. Backfill classification and first migration.
5. Tests and reviewer evidence.

### Phase 6 — Text/Tabular Formats

Formats:

- CSV
- TSV
- DIF
- NDJSON
- TOML
- SYLK

Deliverables:

1. Structural QName registry.
2. Canonical classes for record/field/table/header/cell concepts.
3. Facades only where public API classes are needed.
4. Backfill and tests.

### Phase 7 — Binary/Image/Archive Formats

Formats:

- PBM
- PGM
- PPM
- QOI
- XCF
- ZST

Deliverables:

1. Structural QName registry.
2. Binary element classes for headers, chunks, frames, layers, blocks.
3. Backfill of misplaced parsing/inspection behavior.
4. Tests and reviewer evidence.

### Phase 8 — Full Backfill Burn-Down

Deliverables:

1. Backfill inventory updated for every Python product.
2. Analytics files reduced or marked with remaining burn-down taskcards.
3. All migrated symbols mapped to QName architecture.
4. No new analytics growth.
5. Public API compatibility verified.

Acceptance:

- Remaining legacy debt is explicit, measurable, and governed.
- No hidden overflow pattern remains for new work.

### Phase 9 — Gate 11 Readiness

Deliverables:

1. Final matrix for all formats.
2. Final reviewer verdicts.
3. Final no-stub report.
4. Final source baseline.
5. Final test logs.
6. Final governance runner logs.
7. Final evidence bundle.

Acceptance:

- Formats that pass are labeled `ACCEPTED_VERIFIED`.
- Formats with remaining work are not called production-ready.
- Gate 11 candidates have complete evidence.

## 11. Verification Commands

Use Windows-compatible commands where applicable.

```powershell
python tools/supervisor/governance_validator_runner.py
python tools/review/python_qname_reviewer.py --format abw
python tools/review/no_stub_scan.py --paths src/python tests docs registry
python -m pytest tests/python/abw
python -m pytest tests/python/fodt
python -m pytest tests/review/test_python_qname_reviewer.py
```

For each format:

```powershell
python -c "from src.python.{format}.Compat import *; print('compat import ok')"
python -c "import src.python.{format} as pkg; print(pkg.__name__)"
```

## 12. Final Status Matrix

The final report must include:

| Format | Archetype | Facts ready | Spec classes | Compat | Backfill | No-stub | Tests | Reviewer | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|

Rules:

- Do not mark a format green unless evidence exists.
- Do not call metadata-only classes production features.
- Do not bury blocked work in prose.
- Every red/yellow item must have a taskcard.

## 13. Final Handoff Prompt for Execution Agent

```text
You are executing the governed Python QName decomposition and backfill plan in the real repository.

Mission:
Implement mandatory QName-based architecture across Python format packages, create and enforce the Python QName code reviewer skill, backfill existing Python products, eliminate stub/incomplete patterns, and drive every format through the taskcard state machine until accepted or explicitly blocked with evidence.

Non-negotiables:
- Do not create stubs, placeholders, TODOs, fake implementations, dummy classes, or incomplete production claims.
- Do not add new behavior to analytics overflow files.
- Do not skip reviewer-skill validation.
- Do not skip SAL/structural fact traceability.
- Do not break public API imports.
- Do not mark any format accepted without tests, governance, evidence, and reviewer verdict.

Execution order:
1. Build baseline inventories.
2. Create taskcards for all formats.
3. Implement reviewer skill and no-stub scanner first.
4. Complete FODT Compat.
5. Implement ABW as the pilot.
6. Run reviewer, tests, governance, and no-stub scan.
7. Backfill existing misplaced behavior.
8. Continue format groups by archetype.
9. Produce final evidence bundle and status matrix.

Required state machine:
DISCOVERED -> INVENTORIED -> FACTS_READY -> ARCHITECTURE_PLANNED -> PILOT_IMPLEMENTED -> BACKFILL_STARTED -> REVIEWER_VERIFIED -> TEST_VERIFIED -> GOVERNANCE_VERIFIED -> EVIDENCE_PACKAGED -> ACCEPTED_VERIFIED

If a state fails, move to the appropriate REWORK state and continue after repair. Do not stop at prose recommendations.
```
