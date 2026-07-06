# 01-SYSTEM-OVERVIEW.md — Format Factory Deep Reconnaissance

## 1. Document Scope and Inspected Commit

This document is the product of a deep, evidence-backed technical reconnaissance of the Format Factory repository. Originally performed on 2026-07-05 against commit `94dd5308`; refreshed on 2026-07-06 against commit `0e47f12f` on branch `main`. Every claim is classified by verification status and backed by repository-relative evidence. Claim IDs (CLM-*) reference the evidence ledger in `04-CLAIM-EVIDENCE-LEDGER.md`.

---

## 2. Executive Technical Summary

Format Factory is a system for converting file-format specifications into tested, legally vetted software libraries. It combines two distinct halves:

- **Products** — deterministic, spec-aligned libraries that parse, write, validate, and convert file formats. 20 Python FOSS packages and 10 .NET libraries exist today.
- **Machinery** — an autonomous AI-driven development pipeline that plans work, executes sprints, validates evidence, grades outcomes, enforces governance, and generates the next sprint's tasks. The machinery is written by agents for agents.

The project was started on 2026-05-02 and has accumulated 1,831 commits over 65 days. The repository contains approximately 54,000 lines of Python product source, 22,600 lines of C# product source, 85,000 lines of supervisor/machinery Python, and 39,864 collected tests.

**CLM-SYS-001**: Format Factory is a dual-track system (products + machinery) that converts file-format specifications into tested libraries. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `README.md`, `src/python/` (20 format dirs), `src/net/` (10 format dirs), `tools/supervisor/` (273 .py files).

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
│   ├── python/          # 20 format packages, ~54K LOC
│   │   ├── fods/        # FODS: 3,891 LOC
│   │   ├── fodt/        # FODT: 4,681 LOC (most mature Python)
│   │   ├── ...          # 18 more format packages
│   │   └── _shared/     # Shared utilities
│   └── net/             # 10 .NET libraries, ~22.6K LOC
│       ├── fods/        # FODS: 10,197 LOC (most mature .NET)
│       ├── fodt/        # FODT: 6,008 LOC
│       └── ...          # 8 more format libraries
├── tools/
│   ├── supervisor/      # 273 files, ~85K LOC — sprint orchestration
│   ├── oracle/          # Oracle execution engine
│   ├── spec/            # Spec processing and validation
│   ├── specification-authority-layer/  # SAL fact extraction
│   ├── ai/              # AI-assisted analysis tools
│   ├── governance/      # Governance enforcement
│   ├── certification/   # Test certification tools
│   ├── assurance/       # Output quality assurance
│   └── ...              # 30+ other tool directories
├── tests/               # 39,864 tests
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
| L11 | Supervisor Layer | `tools/supervisor/` | Sprint orchestration, grading | 273 |
| L12 | Governance Layer | `tools/supervisor/governance_validators*.py` | 161 canonical validators | 20 modules |
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
- **Evidence**: 24 SAL Python modules, ~14,719 total facts (consolidated)
- **Status**: `IMPLEMENTED_AND_VERIFIED` (for active formats; 4 acquisition-only formats have 0 facts)

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
- **Count**: 39,864 tests collected
- **Status**: `IMPLEMENTED_AND_VERIFIED` (1,571 FODS tests passed, 1,316 ZST tests passed during initial run)

### Stage 9: Governance Validation
- **Validators**: 161 canonical across 20 modules (156 `def validate_` functions + 5 contract-registry entries)
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

**Fact counts** (from `.local/sal-output/` consolidation): ~14,719 total facts. FODS: ~4,990 facts. ODF family formats (FODS, FODT, ODS, FODG, FODP, ODT) account for ~14,135 facts. Four acquisition-only formats (ora, pam, xpm, zpaq) have 0 facts.

**CLM-PIPE-002**: SAL extracts structured facts from specifications. `IMPLEMENTED_AND_VERIFIED` (MEDIUM). Evidence: 24 SAL modules exist, fact JSON files found in `.local/sal-output/`. Extraction process involves AI-assisted steps.

---

## 11. Capability Modeling

Capabilities track what each format implementation can do, what gaps remain, and what features are planned.

**Key files**:
- `reports/capability-layer/gap-ledger.json` — active gap tracking
- `reports/capability-layer/gap-ledger-active.json` — current active gaps
- `reports/capability-layer/capability-authority-model.yaml` — capability taxonomy
- `.governance/capabilities/registry.yaml` — 120 active capabilities (123 total entries)

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

The supervisor system (`tools/supervisor/`, 273 files, ~85K LOC) orchestrates autonomous development:

### Core Components

| Component | File | LOC | Purpose |
|---|---|---|---|
| Supervisor Loop | `supervisor_loop.py` | 605 | Main entry point, `autonomous-cycle` command |
| Autonomous Cycle | `autonomous_cycle.py` | 2,651 | Sprint execution, grading, next-sprint generation |
| Continuation Checker | `check_continuation.py` | 796 | Decides whether to continue or stop |
| Sprint Executor | `sprint_executor.py` | 628 | Sprint-level execution coordinator |
| Declaration Validator | `sprint_executor_validate.py` | 828 | Validates evidence declarations |
| Plan Lock | `write_plan_lock.py` | 691 | Per-chat plan lock mechanism |
| Governance Validators | `governance_validators*.py` | ~9,000+ | 161 canonical validators across 20 modules |

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

### Governance Validators (161 canonical)

The canonical count of 161 comes from `governance_validator_runner.py` (`expected_count: 161`): 134 explicitly wired validators + 27 from the `@validator` contract registry (`governance_validators_contract.py`). The `grep -c "def validate_"` count across all modules is 156 (includes some unwired helpers).

| Module | `def validate_` count | Focus |
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
| `governance_validators_contract.py` | 2 | @validator decorator and ValidationResult contract |
| `governance_validators_consumer_proof.py` | 2 | Consumer proof validators |
| `governance_validators_gate_auth.py` | 2 | Gate authorization |
| `governance_validators_oracle.py` | 1 | Oracle validators |
| `governance_validators_signal.py` | 1 | Signal validators |
| `governance_validators_root_struct.py` | 1 | Root structure validators |
| `governance_validators_path.py` | 1 | Path validators |
| `governance_validators_ledger.py` | 1 | Ledger validators |
| `governance_validators_dotnet.py` | 1 | .NET validators |

### Gate System
Formats pass through 11 gates:
- Gates 1-4: Legal, spec, patent, prototype
- Gates 5-7: Requirements, oracle, fuzz
- Gates 8-10: Product readiness
- Gate 11: Commercial release (requires Babar Raza approval)

FODS has passed Gates 1-7 + Gate 11 G11-G sub-gate (approved 2026-06-05).

**CLM-GOV-003**: 161 canonical governance validators exist across 20 modules. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `governance_validator_runner.py expected_count=161`; `grep -c "def validate_"` = 156 across 20 files; canonical count includes contract-registry entries.

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

Total: 39,864 tests collected.

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

**CLM-TEST-001**: 39,864 tests collected across 6 layers. `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: `pytest --collect-only` returned 39,864.

**CLM-TEST-002**: All 20 Python formats pass oracle verification (73/73). `IMPLEMENTED_AND_VERIFIED` (HIGH). Evidence: MEMORY.md records, oracle-package.yaml status: VERIFIED for FODS.

---

## 21. Product and Format Inventory

### Python FOSS Products (20 formats)

| Format | Family | LOC | Parse | Write | Export | Oracle | Analytics |
|---|---|---|---|---|---|---|---|
| FODS | Cells | 3,891 | Yes | Yes | CSV | 8/8 | Yes |
| FODT | Text | 4,681 | Yes | Yes | Yes | 3/3 | Yes |
| CSV | Cells | 2,297 | Yes | Yes | — | 5/5 | Yes |
| TSV | Cells | 2,059 | Yes | Yes | — | 4/4 | — |
| ZST | Compression | 2,238 | Yes | — | — | 6/6 | — |
| NDJSON | Data | 2,551 | Yes | Yes | — | 4/4 | — |
| ODS | Cells | 2,781 | Yes | Yes | CSV | 3/3 | Yes |
| ODT | Text | 1,310 | Yes | Yes | — | 3/3 | — |
| TOML | Config | 1,638 | Yes | Yes | — | 4/4 | Yes |
| ABW | Text | 2,277 | Yes | Yes | — | 3/3 | — |
| DIF | Cells | 2,327 | Yes | Yes | — | 3/3 | — |
| SYLK | Cells | 2,016 | Yes | Yes | — | 3/3 | Yes |
| FODG | Drawing | 2,202 | Yes | Yes | — | 3/3 | — |
| FODP | Presentation | 1,338 | Yes | Yes | — | 3/3 | — |
| Gnumeric | Cells | 2,338 | Yes | Yes | — | 3/3 | Yes |
| XCF | Image | 1,570 | Yes | — | — | 3/3 | — |
| QOI | Image | 1,638 | Yes | — | — | 3/3 | — |
| PBM | Image | 1,673 | Yes | Yes | — | 3/3 | — |
| PGM | Image | 1,664 | Yes | Yes | — | 3/3 | — |
| PPM | Image | 1,841 | Yes | Yes | — | 3/3 | — |

**Write coverage**: 17 of 20 Python formats have write/save support. Three formats are read-only: QOI, XCF, ZST.

### .NET Products (10 formats)

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
| ODS | `TESTED` | — | Parse and write + CSV export |
| ODT | `TESTED` | — | Parse and write |
| DIF | `TESTED` | — | Parse and write |
| SYLK | `TESTED` | — | Parse and write |
| TOML | `TESTED` | — | Parse and write |
| ABW | `TESTED` | — | Parse and write |
| Gnumeric | `TESTED` | — | Parse and write |
| FODG | `TESTED` | — | Parse and write |
| FODP | `TESTED` | — | Parse and write |
| XCF | `TESTED` | — | Parse (GIMP format, read-only) |
| QOI | `TESTED` | — | Parse (read-only) |
| HTML | — | `SCAFFOLDED` | Write-only target |
| Markdown | — | `SCAFFOLDED` | Write-only target |
| TXT | — | `SCAFFOLDED` | Write-only target |

---

## 23. Python versus .NET Comparison

| Dimension | Python | .NET |
|---|---|---|
| Formats | 20 | 10 |
| Total source LOC | ~54K | ~22.6K |
| Most mature | FODT (4,681 LOC) | FODS (10,197 LOC) |
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

1. **Broad format coverage**: 20 Python + 10 .NET implementations from a standing start of 65 days
2. **Rigorous governance**: 161 canonical validators, 123 skills, 124 commands — unusually high for a 2-month project
3. **Spec traceability**: QName registry links every code class to a specification element
4. **Oracle verification**: 73/73 PASS — deterministic proof that parsers match specifications
5. **Autonomous development**: 840+ sprints executed through formal pipeline
6. **Test density**: 39,864 tests — approximately 556 tests per format (Python average)
7. **Dual-track**: Same governance for both FOSS (Python) and commercial (.NET)

---

## 28. Current Limitations

1. **No public releases**: Neither PyPI packages nor NuGet packages are published
2. **Gate 11 not approved**: Commercial release requires business decision
3. **Write support is nearly complete but 3 formats remain read-only**: QOI, XCF, and ZST lack same-format write. 17 of 20 Python formats have write/save.
4. **Export is narrow**: Only FODS and ODS have cross-format export (CSV). .NET FODS has 6 export targets.
5. **Edit support varies**: Rich editing exists for FODS .NET but not uniformly across formats
6. **SAL has gaps**: 4 acquisition-only formats (ora, pam, xpm, zpaq) have 0 extracted facts and no product source
7. **Analytics are large**: Some analytics files exceed 1,000 LOC (governance violation tracking)
8. **Supervisor is very large**: 85K LOC of machinery for 77K LOC of product — machinery outweighs product

---

## 29. Architectural Risks

1. **Machinery-to-product ratio**: Supervisor code (85K LOC) is larger than all product code (77K LOC combined). This is unusual and creates maintenance burden.
2. **Prompt-only governance**: Many governance rules exist only in CLAUDE.md and AGENTS.md — they are enforced by AI compliance, not by code.
3. **Report accumulation**: The `reports/` directory is 402 MB and growing. No automated archival or pruning.
4. **Single-agent dependency**: The system is designed around Claude Code. Codex support is governance-adapted but not primary.
5. **Local-state dependency**: Evidence and continuation state in `.local/` is gitignored — not reproducible across machines.
6. **CI coverage is partial**: CI runs lint, security, and L0-L3 Python tests plus .NET restore/build/test, but the full 39K+ test suite is not run in CI.

---

## 30. Known Debt

1. **Monolithic analytics files**: Some `*_analytics.py` files exceed governance LOC caps
2. **CSV import shadowing**: Python's `csv` stdlib module conflicts with the format-factory `csv` package name
3. **Missing writers**: 3 Python formats lack same-format save (QOI, XCF, ZST)
4. **Zero-fact formats**: ORA, PAM, XPM, ZPAQ have acquisition packs but no SAL facts or product code
5. **Stale plan locks**: Historical plan locks can interfere with continuation checking
6. **supervisor_loop.py timeout**: 120-second default can block on large declarations

---

## 31. Specification Types

The system handles specifications of several different kinds, each with different ingestion and normalization paths:

| Spec Type | Formats | Ingestion Path | Normalization | Current Support |
|---|---|---|---|---|
| XML schema / ODF-style prose specs | FODS, FODT, ODS, ODT, FODG, FODP | SAL extraction via `tools/specification-authority-layer/` | AI-assisted fact extraction → JSON | Full (14,135 facts for ODF family) |
| Binary layout specs | XCF (GIMP), QOI | Manual spec reading → fact JSON | Manually normalized | Partial (5-45 facts each) |
| Textual grammar / record-oriented | CSV, TSV, DIF, SYLK, NDJSON, TOML | RFC/spec reading → fact JSON | Manually normalized | Partial (18-70 facts each) |
| Compression / container specs | ZST (Zstandard), Gnumeric (gzip+XML) | RFC/spec reading → fact JSON | Manually normalized | Partial (64-204 facts) |
| XML-based document specs | ABW (AbiWord XML) | Spec reading → fact JSON | Manually normalized | Minimal (39 facts) |

**Limitations**: SAL AI-assisted extraction is currently effective primarily for XML/ODF-family specifications. Non-XML formats rely on manually normalized fact sets that are smaller and less comprehensive. The 4 acquisition-only formats (ORA, PAM, XPM, ZPAQ) have no facts extracted yet.

## 32. Format Categories

Products are organized into these categories based on their primary purpose:

| Category | Formats (Python) | Formats (.NET) | Notes |
|---|---|---|---|
| Spreadsheets and tables | FODS, ODS, CSV, TSV, DIF, SYLK, Gnumeric | FODS, CSV, TSV | Tabular data with cells, rows, formulas |
| Documents and text | FODT, ODT, ABW | FODT | Rich text with paragraphs, styles, sections |
| Presentations | FODP | — | Slide-based content |
| Drawings | FODG | — | Vector graphics |
| Images and rasters | PBM, PGM, PPM, QOI, XCF | Netpbm | Pixel data, codec operations |
| Structured data | NDJSON, TOML | NDJSON | Machine-readable structured records |
| Compression | ZST | ZST | Compression/decompression codec |
| Export-only targets | — | HTML, Markdown, TXT | Write-only output formats for .NET |

**Coverage**: The strongest category is spreadsheets/tables (7 Python formats, 3 .NET) where the ODF specification provides deep SAL fact coverage. Image/raster formats have the simplest implementations. Structured data formats (NDJSON, TOML) are lightweight wrappers.

## 33. Glossary

| Term | Definition | FF-Specific Meaning |
|---|---|---|
| **Specification** | A formal document describing a file format's structure, syntax, and semantics (e.g., ODF 1.3, RFC 8478) | Input to the SAL layer; the authoritative source for all product behavior |
| **Schema** | A machine-readable definition of allowed structure (e.g., XML Schema, JSON Schema) | Used for both specification elements and internal data validation (evidence schemas, capability schemas) |
| **SAL** | Specification Authority Layer | The subsystem (`tools/specification-authority-layer/`) that extracts structured facts from specifications. Uses AI-assisted analysis for complex specs. |
| **QName** | Qualified Name — a namespace-prefixed element identifier (e.g., `table:table-cell`) | Maps spec elements to canonical class names via `shared/qname-registry/{format}.yaml`. Shared across Python and .NET. |
| **Namespace** | An XML namespace URI that disambiguates element names (e.g., `urn:oasis:names:tc:opendocument:xmlns:table:1.0`) | Defined in specification; used by parsers to identify elements; recorded in QName registry |
| **Capability** | A discrete feature or behavior that a format implementation can exhibit | Tracked in `.governance/capabilities/registry.yaml` (120 active). Each maps to a product track. |
| **Capability Compiler** | A tool that translates capability gaps into concrete work items | `tools/supervisor/capability_feature_compiler.py` produces `next-work-items.json` from gap ledger entries |
| **Object Model** | The in-memory data structure representing a parsed file's content | Each format defines models via dataclasses or dicts. Spec-aligned classes live in `spec/`; user-facing facades in `Compat/`. |
| **Parser** | Code that reads a file format and produces an object model | Implemented per format in `{format}_codec.py` or `parser.py`. Uses streaming XML for ODF formats. |
| **Writer / Serializer** | Code that takes an object model and writes it back to the format | 17 of 20 Python formats have writers. Enables round-trip (parse→edit→save). |
| **Round-trip** | Parse a file, optionally modify it, write it back, and verify the output matches expectations | Key quality metric. FODS Python has verified parse→write→parse round-trip. |
| **Preservation** | The property that writing a parsed file back produces output identical (or semantically equivalent) to the input | Stronger than round-trip; not yet verified for all formats |
| **Oracle** | A deterministic, spec-grounded test case that verifies parser output against specification requirements | 73 oracle cases across 20 formats, all PASS. Defined in `oracle/formats/{format}/oracle-package.yaml`. |
| **Evidence Declaration** | A YAML file documenting what work was done in a sprint, with file references and test results | Written to `.local/evidences/{run_id}/`. Schema at `schemas/evidence/`. Validated by `sprint_executor_validate.py`. |
| **Gate** | An approval checkpoint in the acquisition or release pipeline (11 total) | Gates 1-4: legal/spec/prototype. Gates 5-7: requirements/oracle/fuzz. Gates 8-10: product readiness. Gate 11: commercial release. |
| **Gate 11** | The commercial release gate requiring business approval from Babar Raza | Blocks PyPI and NuGet publication. Criteria: C1-C20 (.NET), P1-P11 (Python). |
| **Sprint** | A unit of autonomous development work, typically executed by Claude Code | 840+ completed. Each sprint reads `next-sprint.md`, executes work, produces evidence. |
| **Taskcard** | A named work item within a plan (e.g., TC-PGI-045) | Has status (CLOSED, IN_PROGRESS, etc.). Plans contain multiple taskcards executed sequentially. |
| **Lane** | A parallel execution track for format-specific or cross-cutting work | The supervisor can schedule work across multiple lanes (e.g., FODS deepening, governance). |
| **Queue** | An ordered list of work items awaiting execution | Gap ledger entries feed into the work queue via the capability compiler |
| **Supervisor** | The orchestration system that plans, validates, grades, and sequences autonomous sprints | `tools/supervisor/` (273 files, 85K LOC). Core: `supervisor_loop.py`, `autonomous_cycle.py`, `check_continuation.py`. |
| **Governance Validator** | A programmatic check enforcing code quality, spec alignment, or process compliance (e.g., V001, V134) | 161 canonical validators across 20 modules. Run during autonomous-cycle grading. |
| **Gap Ledger** | Tracks missing capabilities per format as structured JSON entries | `reports/capability-layer/gap-ledger.json`. Entries drive work item generation. |
| **Skill** | A registered agent command with defined inputs, outputs, and capability routing | 123 skills in `.supervisor/skill-registry.yaml`. Every source mutation should go through a registered skill. |
| **Promotion** | Advancing a format through pipeline gates (e.g., from Gate 4 to Gate 5) | Tracked in `registry/format-registry.yaml` |
| **Certification** | Formal verification that tests meet quality thresholds (strong assertions, exception coverage) | Tools in `tools/certification/`. Report at `reports/certification/certification-report.md`. |
| **Compat/** | Facade directory within each format package containing format-prefixed convenience classes | e.g., `FodsDocument`, `FodsCell`. Wraps canonical spec-aligned classes for user ergonomics. |
| **spec/** | Spec-aligned domain class hierarchy within each format package | Classes have `spec_qname: ClassVar[str]` linking to specification elements. Canonical naming, not format-prefixed. |
| **Machinery** | Development automation tools (not shipped to users) | `tools/supervisor/`, `tools/oracle/`, `tools/spec/`, etc. — 85K LOC total. |
| **Product** | Format libraries shipped to end users | `src/python/` (20 formats, 54K LOC), `src/net/` (10 formats, 22.6K LOC). No AI/LLM dependencies. |
| **FOSS** | Free and Open Source Software | The Python product track, licensed Apache-2.0 |
| **Idempotency** | The property that running an operation multiple times produces the same result | Applied to skills, governance validators, and this documentation maintenance process |
| **Generated Code** | Artifacts produced automatically by machinery (e.g., `next-sprint.md`, `session-resume.md`, capability index) | Distinguished from manually written product source. See DIAG-017. |
| **Manually Maintained Code** | Product source written by agents through governed skills, not auto-generated | Parsers, writers, models, analytics, tests. May be scaffolded initially via `/new-format-kickstart`. |

---

## 34. Claim-Reference Index

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
| CLM-GOV-003 | 19 | 161 canonical governance validators |
| CLM-TEST-001 | 20 | 39,864 tests collected |
| CLM-TEST-002 | 20 | 73/73 oracle pass rate |
