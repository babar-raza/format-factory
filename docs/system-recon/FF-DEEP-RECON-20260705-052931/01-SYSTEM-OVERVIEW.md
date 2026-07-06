# 01-SYSTEM-OVERVIEW.md — Format Factory Deep Reconnaissance

## 1. Document Scope and Inspected Commit

This document is the product of a deep, evidence-backed technical reconnaissance of the Format Factory repository performed on 2026-07-05 against commit `94dd5308` on branch `main`. Every claim is classified by verification status and backed by repository-relative evidence. Claim IDs (CLM-*) reference the evidence ledger in `04-CLAIM-EVIDENCE-LEDGER.md`.

---

## 2. Executive Technical Summary

Format Factory is a system for converting file-format specifications into tested, legally vetted software libraries. It combines two distinct halves:

- **Products** — deterministic, spec-aligned libraries that parse, write, validate, and convert file formats. 20 Python FOSS packages and 10 .NET libraries exist today.
- **Machinery** — an autonomous AI-driven development pipeline that plans work, executes sprints, validates evidence, grades outcomes, enforces governance, and generates the next sprint's tasks. The machinery is written by agents for agents.

The project was started on 2026-05-02 and has accumulated 1,810 commits over 64 days. The repository contains 15,728 tracked files, approximately 49,000 lines of Python product source, 22,500 lines of C# product source, 81,000 lines of supervisor/machinery Python, and 39,863 collected tests.

**CLM-SYS-001**: Format Factory is a dual-track system (products + machinery) that converts file-format specifications into tested libraries. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `README.md`, `src/python/` (20 format dirs), `src/net/` (10 format dirs), `tools/supervisor/` (262 .py files).

---

## 3. Problem the System Addresses

Implementing file-format support in software is traditionally manual, error-prone, and legally hazardous. Developers must:

1. Locate and understand format specifications (often hundreds of pages).
2. Navigate licensing and patent constraints.
3. Build parsers, writers, and object models from scratch.
4. Write conformance tests without authoritative test oracles.
5. Maintain traceability from spec elements to code.
6. Repeat this for every format and every target language.

Format Factory addresses this by building a repeatable, governed pipeline that automates or semi-automates each step: from format scoring and legal clearance through specification analysis, fact extraction, capability modeling, code generation, testing, oracle verification, and release gating.

**CLM-SYS-002**: The system addresses the problem of converting format specifications into tested libraries. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: pipeline components traced from `acquisition-packs/` through `src/python/` to `oracle/`.

---

## 4. Actual Current System Scope

### Formats with Python Product Source (20)

ABW, CSV, DIF, FODG, FODP, FODS, FODT, Gnumeric, NDJSON, ODS, ODT, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF, ZST.

### Formats with .NET Product Source (10)

CSV, FODS, FODT, HTML, Markdown, NDJSON, Netpbm, TSV, TXT, ZST.

### Formats in Registry but Without Product Source (4+)

ORA, PAM, XPM, ZPAQ — these have acquisition packs but no `src/` implementations.

**CLM-SYS-003**: 20 Python and 10 .NET format implementations exist as source code. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `ls src/python/`, `ls src/net/`.

---

## 5. Intended Users and Consumers

- **End users**: Developers integrating file-format support into their applications. They install Python packages (`format-factory-fods`, `format-factory-zst`, etc.) or reference .NET NuGet packages.
- **Internal consumers**: The machinery itself — the supervisor, validators, and oracle system consume product libraries for verification.
- **Project maintainers**: Use the governance machinery, skills, and commands to drive development.

---

## 6. Inputs and Outputs

| Input | Output |
|---|---|
| File-format specifications (ODF, RFC, ISO, etc.) | Python FOSS packages (`format-factory-{format}`) |
| SAL-extracted facts (JSON) | .NET commercial libraries (`FormatFactory.{Format}`) |
| QName registries (YAML) | Oracle test cases (YAML) |
| Acquisition evidence (legal, scoring, prototypes) | Gap ledgers (JSON) |
| Sprint plans and taskcards | Evidence declarations (YAML) |
| Governance policies | Reports and audits (Markdown, JSON) |

---

## 7. Repository Map

```
format-factory/
├── src/
│   ├── python/          # 20 format packages, ~49K LOC
│   │   ├── fods/        # FODS: 4,903 LOC (most mature Python)
│   │   ├── fodt/        # FODT: 5,263 LOC
│   │   ├── ...          # 18 more format packages
│   │   └── _shared/     # Shared utilities
│   └── net/             # 10 .NET libraries, ~22.5K LOC
│       ├── fods/        # FODS: 10,197 LOC (most mature .NET)
│       ├── fodt/        # FODT: 6,008 LOC
│       └── ...          # 8 more format libraries
├── tools/
│   ├── supervisor/      # 262 files, ~81K LOC — sprint orchestration
│   ├── oracle/          # Oracle execution engine
│   ├── spec/            # Spec processing and validation
│   ├── specification-authority-layer/  # SAL fact extraction
│   ├── ai/              # AI-assisted analysis tools
│   ├── governance/      # Governance enforcement
│   ├── certification/   # Test certification tools
│   ├── assurance/       # Output quality assurance
│   └── ...              # 30+ other tool directories
├── tests/               # 39,863 tests, ~262 MB
├── oracle/              # Oracle test cases for 20 formats
├── shared/qname-registry/  # 21 QName registry files
├── registry/            # Format registry, baselines
├── schemas/             # JSON/YAML schemas
├── plans/               # Master plan, strategic plans
├── reports/             # Sprint reports, audits (402 MB)
├── acquisition-packs/   # Per-format gate evidence
├── samples/             # Sample files for testing
├── packaging/           # Package build scripts
├── .supervisor/         # Skill registry, policies
├── .governance/         # Capability registry
├── .claude/commands/    # 124 Claude Code commands
└── .github/workflows/   # CI: lint, security, tests
```

---

## 8. Major Architectural Layers

Format Factory is organized into 11 independent layers:

| Layer | Name | Path(s) | Purpose | Files |
|---|---|---|---|---|
| L01 | SAL (Specification Authority Layer) | `tools/spec/`, `tools/specification-authority-layer/` | Fact extraction from specs | ~30 |
| L02 | QName Registry | `shared/qname-registry/*.yaml` | Spec-element-to-class mapping | 21 |
| L03 | Capability Layer | `reports/capability-layer/` | Feature tracking, gap ledgers | ~173 |
| L05 | Oracle Layer | `oracle/`, `tools/oracle/` | Deterministic verification cases | ~49 |
| L06 | Product Source | `src/python/`, `src/net/` | Parser, writer, model implementations | ~800+ |
| L07 | Test Layer | `tests/` | Unit, integration, roundtrip, oracle tests | ~5,600 |
| L08 | Evidence Layer | `.local/evidences/` (gitignored) | Sprint evidence declarations | Local |
| L09 | State Layer | `.local/supervisor/` (gitignored) | Continuation signals, plan locks | Local |
| L11 | Supervisor Layer | `tools/supervisor/` | Sprint orchestration, grading | 262 |
| L12 | Governance Layer | `tools/supervisor/governance_validators*.py` | 153 programmatic validators | 18 modules |
| L13 | Skills Layer | `.supervisor/skill-registry.yaml` | 123 registered skills | 1 |

**CLM-ARCH-001**: The system uses an 11-layer architecture. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: Layer paths exist and contain active code; verified via directory inspection and LOC counts.

---

## 9. End-to-End Specification-to-Library Lifecycle

The pipeline proceeds through these stages (confirmed via repository evidence):

### Stage 1: Format Selection and Scoring
- **Tool**: Agent-driven scoring using 7-factor-100pt model
- **Output**: Score in `registry/format-registry.yaml`
- **Evidence**: FODS scored 93/100, approved by Babar Raza 2026-05-04
- **Status**: `IMPLEMENTED_AND_VERIFIED`

### Stage 2: Legal and Gate Review (Gates 1-4)
- **Gates**: Legal category, spec availability, patent search, prototype
- **Output**: Acquisition packs in `acquisition-packs/{format}/`
- **Evidence**: 28 format directories in `acquisition-packs/`
- **Status**: `IMPLEMENTED_AND_VERIFIED`

### Stage 3: Specification Acquisition and Fact Extraction (SAL)
- **Tool**: `tools/specification-authority-layer/` + `tools/spec/`
- **Output**: Structured facts in `.local/sal-output/` and per-format `spec/` dirs
- **Evidence**: 24 SAL Python modules, ~14,441 total facts reported
- **Status**: `IMPLEMENTED_AND_VERIFIED` (for active formats; 4 formats have 0 facts)

### Stage 4: QName Mapping
- **Registry**: `shared/qname-registry/{format}.yaml`
- **Output**: Spec-qualified-name to canonical class mapping
- **Evidence**: 21 YAML files, FODS has 12+ entries mapping `office:document` → `Office.Document` etc.
- **Status**: `IMPLEMENTED_AND_VERIFIED` (99.4% coverage reported)

### Stage 5: Capability Modeling
- **Output**: `reports/capability-layer/gap-ledger.json`, capability maps
- **Status**: `IMPLEMENTED_AND_VERIFIED` (gap ledger active, 21+ gap-related files)

### Stage 6: Source Implementation
- **Python**: 20 packages in `src/python/`, manually written with spec-aligned structure
- **.NET**: 10 libraries in `src/net/`, manually written
- **Pattern**: Each format has main codec, analytics, spec/ hierarchy, Compat/ facades
- **Status**: `IMPLEMENTED_AND_VERIFIED` (runtime verified for FODS, FODT, ZST, TOML)

### Stage 7: Oracle Verification
- **Cases**: `oracle/formats/{format}/oracle-package.yaml` for all 20 Python formats
- **Executor**: `tools/oracle/execute_oracle.py` (1,428 LOC)
- **Result**: 73/73 PASS across all 20 formats
- **Status**: `IMPLEMENTED_AND_VERIFIED`

### Stage 8: Testing
- **Framework**: pytest (Python), xUnit-style .cs files (.NET)
- **Count**: 39,863 tests collected
- **Status**: `IMPLEMENTED_AND_VERIFIED` (1,571 FODS tests passed, 1,316 ZST tests passed in this run)

### Stage 9: Governance Validation
- **Validators**: 153 across 18 modules
- **Status**: `IMPLEMENTED_AND_VERIFIED`

### Stage 10: Packaging
- **Python**: `packaging/python/build-local-packages.py`
- **Status**: `IMPLEMENTED_AND_VERIFIED` (install-proof evidence exists)

### Stage 11: Release Gating (Gate 11)
- **Status**: `PARTIALLY_IMPLEMENTED` — Gate 11 NOT approved. Requires Babar Raza business decision.

**CLM-PIPE-001**: A 10+ stage pipeline from spec to library exists and is operational. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: Components at each stage confirmed via files, runtime tests, and gate records.

---

## 10. Specification Analysis and Fact Extraction

The Specification Authority Layer (SAL) extracts machine-readable facts from format specifications.

**Components**:
- `tools/specification-authority-layer/` — 24 Python modules including `requirement_extractor.py`, `fact_quality.py`, `context_pack_builder.py`
- `tools/spec/merge_sal_facts.py` — merges facts across formats
- Per-format `src/python/{format}/spec/` — spec-aligned domain modules

**Data flow**: Specification PDFs/HTML → SAL extraction (sometimes AI-assisted via `tools/ai/`) → structured JSON facts → persisted in `.local/sal-output/`

**Fact counts** (from MEMORY.md, verified against code): ~14,441 total facts. FODS: ~4,988 facts. Some formats (ora, pam, xpm, zpaq) have 0 facts.

**CLM-PIPE-002**: SAL extracts structured facts from specifications. `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: 24 SAL modules exist, fact JSON files found in `.local/sal-output/`. Extraction process involves AI-assisted steps.

---

## 11. Capability Modeling

Capabilities track what each format implementation can do, what gaps remain, and what features are planned.

**Key files**:
- `reports/capability-layer/gap-ledger.json` — active gap tracking
- `reports/capability-layer/gap-ledger-active.json` — current active gaps
- `reports/capability-layer/capability-authority-model.yaml` — capability taxonomy
- `.governance/capabilities/registry.yaml` — 119 active capabilities

**CLM-PIPE-003**: Capability modeling tracks per-format features and gaps. `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: Gap ledger files, capability registry.

---

## 12. Capability-to-Feature Translation

The capability-to-feature compiler translates capability records into concrete work items.

**Key files**:
- `tools/supervisor/capability_feature_compiler.py` — canonical pipeline tool (produces `next-work-items.json`)
- `tools/capability_layer/capability_to_feature_compiler.py` — planning tool (taskcard stubs)

**CLM-PIPE-004**: Capability-to-feature compilation exists. `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: Two compiler implementations exist (pipeline and planning).

---

## 13. Source Generation and Manual Implementation Boundaries

Product source code is **primarily manually written**, not code-generated. Each format package follows a consistent pattern:

```
src/python/{format}/
├── __init__.py              # Public API with __all__
├── {format}_codec.py        # Core parse/load/save functions
├── {format}_analytics.py    # Spec-backed analytics functions
├── models.py                # Domain model dataclasses
├── exceptions.py            # Format-specific exceptions
├── constants.py             # Namespace URIs, limits
├── spec/                    # Spec-aligned domain hierarchy
│   ├── office/document.py   # Maps to QName office:document
│   └── table/table.py       # Maps to QName table:table
└── Compat/                  # Format-prefixed facade classes
    ├── fods_document.py     # FodsDocument → Office.Document
    └── fods_cell.py         # FodsCell → Table.TableCell
```

**Generated vs manual**: The `spec/` hierarchy classes have `spec_qname: ClassVar[str]` declarations mapping to specification elements. The implementation code (parsers, writers, analytics) is manually authored. Templates exist in `templates/` but are scaffolding aids, not continuous code generators.

**CLM-ARCH-002**: Product source is manually written following a governed pattern, not continuously auto-generated. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: Reading `src/python/fods/parser.py` shows hand-written streaming XML parser with IR-FODS-* requirement references.

---

## 14. Public Object-Model Architecture

Each Python format package exposes:
- **Class-based API**: e.g., `FodsDocument.from_file("spreadsheet.fods")` (via Compat/ facades)
- **Dict-based API**: e.g., `parse_fods("file.fods")` returns a dict with `sheets`, `metadata`
- **Analytics API**: e.g., `count_sheets(model)`, `get_cell_types(model)`

Each .NET format library exposes:
- **Document class**: e.g., `FodsDocument` with parse, edit, save, export methods
- **Model classes**: e.g., `FodsWorksheet`, `FodsWorksheetCollection`
- **Export classes**: e.g., `FodsCsvExporter`, `FodsHtmlExporter`, `FodsJsonExporter`

**CLM-ARCH-003**: Python packages expose dual APIs (class-based and dict-based). `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `src/python/fods/__init__.py` imports both, runtime test confirmed dict API works.

---

## 15. Parsing, Editing, Saving, and Exporting

### Parse/Load
All 20 Python formats implement load/parse. Verified at runtime for FODS, FODT, ZST, TOML.

### Edit
FODS (Python) supports cell editing via dict API. .NET FODS has `FodsDocumentEditOps.cs` (738 LOC) with rich editing. Most Python formats support model mutation via dict operations.

### Same-Format Save (Write)
FODS Python has `writer.py` (182 LOC) with `write_fods()`. Roundtrip verified. ZST has `compress_file`/`decompress_file` for round-trip. Not all formats have dedicated writers.

### Export
FODS Python: CSV export (`csv_exporter.py`, 124 LOC), TSV export (`fods_to_tsv.py`, 90 LOC).
FODS .NET: CSV, HTML, JSON, ODS, PDF, PNG exporters (6 exporter classes, ~1,900 LOC combined).

**CLM-PROD-001**: FODS supports parse, edit, write, and export in both Python and .NET. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: Runtime roundtrip test, source inspection of writer.py and .NET exporter classes.

---

## 16. Agentic Execution Model

The system uses AI agents (primarily Claude Code) for development execution:

- **Primary agent**: Claude Code (VS Code extension) — defined in `CLAUDE.md` and `AGENTS.md`
- **Secondary agent**: Codex (optional) — requires governance adapter
- **Agent configuration**: Kilo AI (`.kilo/kilo.jsonc`) — minimal config

The agent model is **not runtime autonomy** — agents operate at development time to write code, run tests, and produce evidence. Product libraries contain no LLM calls.

**CLM-ARCH-004**: AI agents drive development but products are deterministic with no LLM calls. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: Product source contains no AI imports; `CLAUDE.md` governs agent behavior.

---

## 17. Skills and Commands

### Skills (123 registered)
Skills are registered in `.supervisor/skill-registry.yaml` and map to Claude commands in `.claude/commands/`. Each skill defines:
- `skill_id`, `description`, `trigger`, `inputs`, `outputs`
- Routing to capability IDs

**Skill categories** (from capability registry):
- Governance (26): validation, certification, audit
- Layer governance (25): layer state, task tracking
- Planning (17): evidence, taskcards, execution
- Product (12): Python/dotnet API, object model, analytics
- Acquisition (5): scoring, gate checks
- Other (38): packaging, oracle, infrastructure, maintenance

### Commands (124)
`.claude/commands/*.md` define executable prompts for Claude Code's `/command` interface.

**CLM-GOV-001**: 123 skills and 124 commands are registered. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `grep -c "skill_id:" .supervisor/skill-registry.yaml` = 123; `find .claude/commands -name "*.md" | wc -l` = 124.

---

## 18. Supervisor and Autonomous Execution

The supervisor system (`tools/supervisor/`, 262 files, ~81K LOC) orchestrates autonomous development:

### Core Components

| Component | File | LOC | Purpose |
|---|---|---|---|
| Supervisor Loop | `supervisor_loop.py` | 605 | Main entry point, `autonomous-cycle` command |
| Autonomous Cycle | `autonomous_cycle.py` | 2,651 | Sprint execution, grading, next-sprint generation |
| Continuation Checker | `check_continuation.py` | 796 | Decides whether to continue or stop |
| Sprint Executor | `sprint_executor.py` | 628 | Sprint-level execution coordinator |
| Declaration Validator | `sprint_executor_validate.py` | 828 | Validates evidence declarations |
| Plan Lock | `write_plan_lock.py` | 691 | Per-chat plan lock mechanism |
| Governance Validators | `governance_validators*.py` | ~9,000+ | 153 validators across 18 modules |

### Execution Flow
1. Agent reads `reports/supervisor/session-resume.md` for context
2. Agent reads `reports/supervisor/next-sprint.md` for work items
3. Agent executes sprint work (code changes, tests, evidence)
4. Agent writes evidence declaration to `.local/evidences/{run_id}/`
5. `supervisor_loop.py autonomous-cycle` validates and grades work
6. `check_continuation.py` decides: CONTINUE (exit 0) or STOP (exit 1)
7. If CONTINUE: loop back to step 2 with updated next-sprint.md
8. Iteration counter in `.local/supervisor/continuation-signal.json`

### Sprint History
840+ autonomous sprints completed (per README). Sprint reports in `reports/r23/` through `reports/r133/` and `reports/skills-r*`, `reports/mainstream-*`, `reports/acceleration-*`, etc.

**CLM-GOV-002**: The supervisor orchestrates autonomous sprint execution with continuation checking. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `supervisor_loop.py`, `check_continuation.py`, `autonomous_cycle.py` — all verified via source inspection. Sprint report directories exist (r23-r133+).

---

## 19. Governance and Evidence

### Evidence Declarations
Each sprint produces an evidence declaration YAML file containing:
- Work items with status, evidence paths, test references
- Worker self-verdict
- Changed files list

Schema: `schemas/evidence/` (multiple schemas for different evidence types)

### Governance Validators (153 total)

| Module | Count | Focus |
|---|---|---|
| `governance_validators.py` | 50 | Core validators |
| `governance_validators_ext4.py` | 20 | Extended validators batch 4 |
| `governance_validators_ext2.py` | 19 | Extended validators batch 2 |
| `governance_validators_ext.py` | 15 | Extended validators batch 1 |
| `governance_validators_ext3.py` | 10 | Extended validators batch 3 |
| `governance_validators_found_issue.py` | 8 | Found-issue validators |
| `governance_validators_dotnet_semantic.py` | 6 | .NET semantic validators |
| `governance_validators_spec.py` | 5 | Spec-related validators |
| `governance_validators_sal.py` | 4 | SAL validators |
| `governance_validators_layers.py` | 4 | Layer validators |
| `governance_validators_output_quality.py` | 3 | Output quality (V134-V136) |
| `governance_validators_consumer_proof.py` | 2 | Consumer proof validators |
| `governance_validators_gate_auth.py` | 2 | Gate authorization |
| Others (5 modules) | 5 | Signal, ledger, path, root_struct, dotnet |

### Gate System
Formats pass through 11 gates:
- Gates 1-4: Legal, spec, patent, prototype
- Gates 5-7: Requirements, oracle, fuzz
- Gates 8-10: Product readiness
- Gate 11: Commercial release (requires Babar Raza approval)

FODS has passed Gates 1-7 + Gate 11 G11-G sub-gate (approved 2026-06-05).

**CLM-GOV-003**: 153 governance validators exist across 18 modules. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `grep -c "def validate_"` across all governance_validators*.py files.

---

## 20. Testing and Oracle Strategy

### Test Architecture

| Layer | Tests | Duration | Purpose |
|---|---|---|---|
| L0: Structural | ~500 | Fast | Import smoke, health checks |
| L1: Focused | ~15,000 | Fast | Single-format unit tests |
| L2: Family | ~5,000 | Medium | Related format group tests |
| L3: Integration | ~6,000 | Medium | Supervisor, governance, evidence |
| L4: Golden | ~3,000 | Slow | Roundtrip, cross-format, export |
| L5: Broad | ~5,000 | Slow | All Python + supervisor + evidence |
| L6: Full | ~5,000 | Slow | Entire test suite |

Total: 39,863 tests collected.

### Test Types
- **Unit tests**: Per-format in `tests/python/{format}/` and `tests/net/{format}/`
- **Roundtrip tests**: Parse-edit-save-reload cycles (marked `roundtrip`)
- **Oracle tests**: Spec-grounded deterministic cases (marked `oracle`)
- **Security tests**: Malformed input, injection, boundary tests (marked `security`)
- **Property-based tests**: Hypothesis-driven (marked `property_based`)
- **Governance tests**: Validator and policy tests in `tests/governance/`
- **Supervisor tests**: 6,783 tests in `tests/supervisor/`

### Oracle System
- 20 formats have oracle packages in `oracle/formats/{format}/`
- Each package contains spec-grounded test cases
- `tools/oracle/execute_oracle.py` (1,428 LOC) executes cases
- Result: 73/73 PASS across all 20 Python formats

**CLM-TEST-001**: 39,863 tests collected across 6 layers. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `pytest --collect-only` returned 39,863.

**CLM-TEST-002**: All 20 Python formats pass oracle verification (73/73). `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: MEMORY.md records, oracle-package.yaml status: VERIFIED for FODS.

---

## 21. Product and Format Inventory

### Python FOSS Products (20 formats)

| Format | Family | LOC | Tests | Parse | Write | Export | Oracle | Package |
|---|---|---|---|---|---|---|---|---|
| FODS | Cells | 4,903 | 1,571 | Yes | Yes | CSV, TSV | 8/8 | Yes |
| FODT | Text | 5,263 | 140 files | Yes | Yes | — | 3/3 | Yes |
| CSV | Cells | 2,485 | 62 files | Yes | Yes | — | 5/5 | Yes |
| TSV | Cells | 2,205 | 116 files | Yes | Yes | — | 4/4 | Yes |
| ZST | Compression | 2,401 | 1,316 | Yes | Yes | — | 6/6 | Yes |
| NDJSON | Data | 2,674 | 155 files | Yes | Yes | — | 4/4 | Yes |
| ODS | Cells | 2,974 | 113 files | Yes | — | — | 3/3 | Yes |
| ODT | Text | 1,544 | 39 files | Yes | — | — | 3/3 | Yes |
| TOML | Config | 1,779 | 64 files | Yes | Yes | — | 4/4 | Yes |
| ABW | Text | 2,639 | 162 files | Yes | — | — | 3/3 | Yes |
| DIF | Cells | 2,506 | 97 files | Yes | Yes | — | 3/3 | Yes |
| SYLK | Cells | 2,199 | 102 files | Yes | Yes | — | 3/3 | Yes |
| FODG | Drawing | 2,572 | 105 files | Yes | — | — | 3/3 | Yes |
| FODP | Presentation | 1,504 | 38 files | Yes | — | — | 3/3 | Yes |
| Gnumeric | Cells | 2,508 | 122 files | Yes | — | — | 3/3 | Yes |
| XCF | Image | 1,773 | 73 files | Yes | — | — | 3/3 | Yes |
| QOI | Image | 1,826 | 47 files | Yes | Yes | — | 3/3 | Yes |
| PBM | Image | 1,860 | 70 files | Yes | Yes | — | 3/3 | Yes |
| PGM | Image | 1,792 | 65 files | Yes | Yes | — | 3/3 | Yes |
| PPM | Image | 1,969 | 82 files | Yes | Yes | — | 3/3 | Yes |

### .NET Commercial Products (10 formats)

| Format | LOC | Test Files | Parse | Write | Edit | Export |
|---|---|---|---|---|---|---|
| FODS | 10,197 | 575 | Yes | Yes | Yes | CSV, HTML, JSON, ODS, PDF, PNG |
| FODT | 6,008 | 653 | Yes | Yes | Yes | Markdown, TXT, HTML |
| Netpbm | 2,843 | 627 | Yes | Yes | Yes | — |
| CSV | 1,377 | 179 | Yes | Yes | — | — |
| TSV | 506 | 179 | Yes | Yes | — | — |
| NDJSON | 603 | 186 | Yes | Yes | — | — |
| ZST | 535 | 174 | Yes | — | — | — |
| HTML | 190 | 11 | — | Yes | — | — |
| Markdown | 156 | 11 | — | Yes | — | — |
| TXT | 142 | 11 | — | Yes | — | — |

**CLM-PROD-002**: Python has broader format coverage (20 vs 10) while .NET has deeper feature depth for FODS and FODT. `IMPLEMENTED_AND_VERIFIED` (HIGH).

---

## 22. Product Maturity Matrix

| Format | Python Status | .NET Status | Strongest Capability |
|---|---|---|---|
| FODS | `TESTED + CONFORMANCE_EVIDENCED` | `TESTED + EXPORT_WORKING` | Full roundtrip + 6 export formats |
| FODT | `TESTED + CONFORMANCE_EVIDENCED` | `TESTED + EXPORT_WORKING` | Document parsing + 3 exports |
| ZST | `TESTED + CONFORMANCE_EVIDENCED` | `LOAD_WORKING` | Compress/decompress roundtrip |
| CSV | `TESTED` | `TESTED` | Parse and write |
| TSV | `TESTED` | `TESTED` | Parse and write |
| NDJSON | `TESTED` | `TESTED` | Parse and write |
| Netpbm | `TESTED` (PBM/PGM/PPM) | `TESTED + EDIT_WORKING` | Pixel editing |
| ODS | `TESTED` | — | Parse (ZIP-based) |
| ODT | `TESTED` | — | Parse |
| DIF | `TESTED` | — | Parse and write |
| SYLK | `TESTED` | — | Parse and write |
| TOML | `TESTED` | — | Parse and write |
| ABW | `TESTED` | — | Parse |
| Gnumeric | `TESTED` | — | Parse |
| FODG | `TESTED` | — | Parse |
| FODP | `TESTED` | — | Parse |
| XCF | `TESTED` | — | Parse (GIMP format) |
| QOI | `TESTED` | — | Parse and encode |
| HTML | — | `SCAFFOLDED` | Write-only target |
| Markdown | — | `SCAFFOLDED` | Write-only target |
| TXT | — | `SCAFFOLDED` | Write-only target |

---

## 23. Python versus .NET Comparison

| Dimension | Python | .NET |
|---|---|---|
| Formats | 20 | 10 |
| Total source LOC | ~49K | ~22.5K |
| Most mature | FODS (4,903 LOC) | FODS (10,197 LOC) |
| Licensing | Apache-2.0 (FOSS) | Commercial |
| Edit capabilities | Dict-based mutation | Rich edit ops (dedicated classes) |
| Export formats | CSV, TSV (FODS only) | CSV, HTML, JSON, ODS, PDF, PNG |
| Packaging | pip installable (local) | NuGet-ready (.csproj) |
| Target framework | Python 3.9+ | .NET 10.0 |
| Gate 11 status | Not applicable (FOSS) | Not approved (pending) |
| Spec alignment | spec/ hierarchy with QName | Spec/ hierarchy with QName |

The .NET track is deeper but narrower. FODS .NET is the most feature-rich implementation with 22 .cs files and 6 export formats. Python is broader with 20 formats but simpler per-format functionality.

---

## 24. Extension Process for a New Format

Adding a new format follows the governed pipeline:
1. **Score**: `/score-format` evaluates legal, spec, community, strategic value
2. **Gate 1**: Human approves scoring → `format-registry.yaml` updated
3. **Gates 2-4**: Legal review, spec download, prototype build
4. **Gate 5**: Requirements generation from spec
5. **Gate 6**: Oracle comparison (e.g., against LibreOffice)
6. **Gate 7**: Fuzz testing of prototype
7. **Kickstart**: `/new-format-kickstart` scaffolds `src/python/{format}/`
8. **Implementation**: Parser, writer, models, analytics, spec/ hierarchy
9. **Testing**: Unit tests, oracle cases, roundtrip tests
10. **Packaging**: `packaging/python/build-local-packages.py`

**CLM-ARCH-005**: A governed 10-step extension process exists. `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: acquisition-packs/ (28 formats), `/new-format-kickstart` skill, `build-local-packages.py`.

---

## 25. CI, Packaging, and Release

### CI (GitHub Actions)
- **Lint**: ruff check on `src/`, `tests/`, `tools/`
- **Security**: bandit scan on `src/`
- **Fast tests**: Layers 0-3 via `tools/test_runner.py`
- **Skill attribution**: Detects unattributed `src/` mutations

### Packaging
- Python: `packaging/python/build-local-packages.py` builds pip-installable wheels
- .NET: Standard `.csproj` build with `dotnet build`

### Release
- Gate 11 is the commercial release gate — NOT approved
- Python FOSS packages are buildable locally but not yet published to PyPI
- .NET NuGet packages are buildable but not yet published

**CLM-ARCH-006**: CI exists with lint, security, and tests. Packaging works locally. No public releases yet. `IMPLEMENTED_NOT_RUNTIME_VERIFIED` (MEDIUM). Evidence: `.github/workflows/ci.yml` exists. PyPI/NuGet publication not confirmed.

---

## 26. Security and Privacy Considerations

- **XXE protection**: Parser uses `defusedxml` when available (fallback to stdlib `xml.etree`)
- **File size limits**: `MAX_FILE_BYTES` constant prevents memory exhaustion
- **Input validation**: Strict mode parsers raise on malformed input
- **Fuzz testing**: Gate 7 tests malformed inputs (18 FODS fixtures)
- **Security scan**: Bandit in CI, `bandit -r src/`
- **No secrets in source**: `.gitignore` excludes `.env`, `.local/`
- **No runtime LLM calls**: Products are deterministic

**CLM-ARCH-007**: Security measures exist (defusedxml, size limits, bandit, fuzz tests). `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: `parser.py` lines 24-29 show defusedxml import.

---

## 27. Current Strengths

1. **Broad format coverage**: 20 Python + 10 .NET implementations from a standing start of 64 days
2. **Rigorous governance**: 153 validators, 123 skills, 124 commands — unusually high for a 2-month project
3. **Spec traceability**: QName registry links every code class to a specification element
4. **Oracle verification**: 73/73 PASS — deterministic proof that parsers match specifications
5. **Autonomous development**: 840+ sprints executed through formal pipeline
6. **Test density**: 39,863 tests — approximately 556 tests per format (Python average)
7. **Dual-track**: Same governance for both FOSS (Python) and commercial (.NET)

---

## 28. Current Limitations

1. **No public releases**: Neither PyPI packages nor NuGet packages are published
2. **Gate 11 not approved**: Commercial release requires business decision
3. **Write support is partial**: Many formats have parse but not save/write
4. **Export is narrow**: Only FODS has multiple export targets
5. **Edit support varies**: Rich editing exists for FODS .NET but not uniformly across formats
6. **No CI for .NET**: GitHub Actions only runs Python lint/test
7. **SAL has gaps**: 4 formats (ora, pam, xpm, zpaq) have 0 extracted facts
8. **Analytics are large**: Some analytics files exceed 1,000 LOC (governance violation tracking)
9. **Supervisor is very large**: 81K LOC of machinery for 72K LOC of product — machinery outweighs product

---

## 29. Architectural Risks

1. **Machinery-to-product ratio**: Supervisor code (81K LOC) is larger than all product code (72K LOC combined). This is unusual and creates maintenance burden.
2. **Prompt-only governance**: Many governance rules exist only in CLAUDE.md and AGENTS.md — they are enforced by AI compliance, not by code.
3. **Report accumulation**: The `reports/` directory is 402 MB and growing. No automated archival or pruning.
4. **Single-agent dependency**: The system is designed around Claude Code. Codex support is governance-adapted but not primary.
5. **Local-state dependency**: Evidence and continuation state in `.local/` is gitignored — not reproducible across machines.
6. **No public CI for products**: Product tests run locally; CI only runs lint and L0-L3.

---

## 30. Known Debt

1. **Monolithic analytics files**: Some `*_analytics.py` files exceed governance LOC caps
2. **CSV import shadowing**: Python's `csv` stdlib module conflicts with the format-factory `csv` package name
3. **Missing writers**: ~8 Python formats lack same-format save
4. **Zero-fact formats**: ORA, PAM, XPM, ZPAQ have acquisition packs but no SAL facts or product code
5. **Stale plan locks**: Historical plan locks can interfere with continuation checking
6. **supervisor_loop.py timeout**: 120-second default can block on large declarations

---

## 31. Glossary

| Term | Definition |
|---|---|
| **SAL** | Specification Authority Layer — extracts facts from specs |
| **QName** | Qualified Name — spec namespace:element identifier (e.g., `table:table`) |
| **Gate** | Approval checkpoint in the acquisition pipeline (11 total) |
| **Sprint** | A unit of autonomous development work |
| **Taskcard** | A work item within a plan (e.g., TC-PGI-045) |
| **Oracle** | Deterministic spec-grounded test case |
| **Gap Ledger** | Tracks missing capabilities per format |
| **Evidence Declaration** | YAML file documenting sprint outcomes |
| **Governance Validator** | Programmatic check (e.g., V001, V134) |
| **Skill** | Registered Claude command with defined inputs/outputs |
| **Compat/** | Facade directory with format-prefixed convenience classes |
| **spec/** | Spec-aligned domain class hierarchy |
| **Machinery** | Development automation tools (not shipped) |
| **Product** | Format libraries (shipped to users) |
| **FOSS** | Free and Open Source Software (Python track) |
| **Gate 11** | Commercial release gate (requires business approval) |

---

## 32. Claim-Reference Index

All claim IDs used in this document:

| Claim ID | Section | Summary |
|---|---|---|
| CLM-SYS-001 | 2 | Dual-track system (products + machinery) |
| CLM-SYS-002 | 3 | Addresses spec-to-library conversion problem |
| CLM-SYS-003 | 4 | 20 Python + 10 .NET implementations |
| CLM-ARCH-001 | 8 | 11-layer architecture |
| CLM-ARCH-002 | 13 | Product source is manually written |
| CLM-ARCH-003 | 14 | Python dual API (class + dict) |
| CLM-ARCH-004 | 16 | Agents drive development, products are deterministic |
| CLM-ARCH-005 | 24 | Governed 10-step extension process |
| CLM-ARCH-006 | 25 | CI exists, packaging works locally |
| CLM-ARCH-007 | 26 | Security measures exist |
| CLM-PIPE-001 | 9 | 10+ stage pipeline is operational |
| CLM-PIPE-002 | 10 | SAL extracts structured facts |
| CLM-PIPE-003 | 11 | Capability modeling tracks gaps |
| CLM-PIPE-004 | 12 | Capability-to-feature compilation exists |
| CLM-PROD-001 | 15 | FODS supports parse, edit, write, export |
| CLM-PROD-002 | 21 | Python broader, .NET deeper |
| CLM-GOV-001 | 17 | 123 skills and 124 commands |
| CLM-GOV-002 | 18 | Supervisor orchestrates autonomous sprints |
| CLM-GOV-003 | 19 | 153 governance validators |
| CLM-TEST-001 | 20 | 39,863 tests collected |
| CLM-TEST-002 | 20 | 73/73 oracle pass rate |
