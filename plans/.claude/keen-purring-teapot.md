# Plan: Format Factory README Governance System

authoritative_plan: plans/.claude/keen-purring-teapot.md
plan_type: machinery_hardening
mission_id: README-GOV-001

---

## Context

Format Factory maintains 30 per-format README files (20 Python FOSS, 10 .NET commercial) that are manually authored and have no automated refresh, validation, or staleness detection. The existing README content is valuable and must be preserved — this plan builds a **preservation-first** automated sync system modeled after the existing `tools/capability_sync/` pattern.

**Problem:** READMEs drift from repository truth. No tooling detects staleness, validates claims, or refreshes generated data. Some READMEs are rich (FODS/FODT with frontmatter, 60-90 lines) while others are minimal stubs (CSV/PBM, 32-35 lines). All contain useful maintained content that must not be destroyed.

**Outcome:** A `tools/readme_sync/` module that preserves maintained content, splices verified generated blocks using `<!-- BEGIN/END -->` markers, validates claims against repo truth, detects drift, and is idempotent.

### Root Cause Analysis

1. **No README automation exists.** Unlike `tools/capability_sync/` (which keeps CLAUDE.md and AGENTS.md synced), no equivalent pipeline exists for per-format READMEs.
2. **No staleness detection.** When `pyproject.toml` version bumps, QName registries change, or test files are added, nothing flags the corresponding README as stale.
3. **No generated/maintained boundary.** All README content is manually authored with no markers distinguishing machine-updatable blocks from human prose.
4. **Two distinct README structural families** exist but are undocumented:
   - **ODF-rich** (FODS, FODT, FODG, FODP, ABW, Gnumeric, ZST): YAML frontmatter, spec citations, security notes, requirements coverage, package structure
   - **Short-form FOSS** (CSV, DIF, NDJSON, ODS, ODT, PBM, PGM, PPM, QOI, SYLK, TOML, TSV, XCF): Installation, Quick Start, Features, License
   - **.NET commercial** (FODS, FODT): Gate 11 status, scope, DEC-033, implementation details
   - **.NET minimal** (HTML, Markdown, TXT): Classification, Usage, Gate Status
   - **.NET standard** (CSV, NDJSON, TSV, Netpbm, ZST): Installation, Quick Start, Features, License/Gate

### Existing Repository Patterns to Reuse

The `tools/capability_sync/` module provides a proven 6-module pattern:

| Module | Pattern | README Equivalent |
|---|---|---|
| `inventory_capabilities.py` | Registry compilation from multiple sources | `collector.py` — collect format state |
| `generate_discovery_indexes.py` | Pure content generation (no I/O) | `renderer.py` — generate section content |
| `update_claude_instructions.py` | BEGIN/END marker splicing + backup + idempotent write | `reconciler.py` — splice generated blocks |
| `detect_drift.py` | Timestamp-stripped hash comparison | `drift_detector.py` — staleness check |
| `validate_parity.py` | Multi-check validation with P1/P2 severity | `validator.py` — README contract validation |
| `run_sync.py` | CLI orchestrator with mode dispatch | `run_sync.py` — orchestrator |

**Key conventions from capability_sync:**
- Marker format: `<!-- BEGIN:{ID} generated={ISO8601} source={path} -->`
- Timestamp stripping: `re.sub(r'generated=[^\s>]+', 'generated=STRIPPED', text)`
- Backup path: `.local/archive/{stem}-pre-sync-{ts}.md`
- Idempotency: compare stripped content before writing; skip if unchanged
- Exit codes: 0 = success/no-drift, 1 = drift/error

### Data Sources (all read-only, no format code imports)

| Source | Fields | Parser |
|---|---|---|
| `registry/format-registry.yaml` | display_name, family, extensions, mime_type, spec_body, spec_version, spec_url, gates | `yaml.safe_load` |
| `src/python/{fmt}/pyproject.toml` | name, version, description, license, requires-python, dependencies | `tomllib` (stdlib 3.11+) |
| `src/net/{fmt}/*.csproj` | Version, AssemblyName, TargetFramework, PackageReference | `xml.etree.ElementTree` (stdlib) |
| `shared/qname-registry/{fmt}.yaml` | qname entries, status counts | `yaml.safe_load` |
| `src/python/{fmt}/__init__.py` | `__version__`, `__all__`, `__track__`, `__commercial_ready__` | Text parsing (ast-safe) |
| `src/{track}/{fmt}/` | source file count (.py/.cs) | `pathlib.glob` |
| `tests/{track}/{fmt}/` | test file count | `pathlib.glob` |

---

## Design Decisions

1. **No format code imports.** Collector parses YAML/TOML/XML as text files. Uses `tomllib` (stdlib 3.11+) and `xml.etree.ElementTree` (stdlib). Zero new pip dependencies.
2. **Frontmatter preservation.** Content before first `#` heading is always MAINTAINED (handles YAML frontmatter in FODS/FODT Python READMEs).
3. **Conservative classification.** Unrecognized sections → MAINTAINED. Never delete content the tool doesn't understand.
4. **Marker format matches capability_sync.** `<!-- BEGIN:README-{ID} generated={ts} source={data-source} -->` / `<!-- END:README-{ID} -->`.
5. **Backup before first write.** Each README backed up to `.local/archive/readme-{fmt}-{track}-pre-sync-{ts}.md` before modification.
6. **Dry-run mode.** `--dry-run` prints changes without writing.
7. **Track-aware section schemas.** Python FOSS and .NET commercial have different required/optional section manifests. Export helpers (HTML/Markdown/TXT) use a minimal schema.
8. **Heading alias matching.** Section headings matched case-insensitively with alias map (e.g., "Quick Start" = "Getting Started" = "Usage").

---

## Requirement Inventory

| Req ID | Description | Source |
|---|---|---|
| REQ-RS-001 | Parse existing README into sections preserving all content | User spec §2, §6 |
| REQ-RS-002 | Classify sections as MAINTAINED/GENERATED/HYBRID/UNKNOWN | User spec §2, §27 |
| REQ-RS-003 | Collect verified format state from registries without format code imports | User spec §4, §29 |
| REQ-RS-004 | Generate package info, installation, license, and API sections from repo truth | User spec §10-14 |
| REQ-RS-005 | Reconcile generated data into existing README preserving maintained content | User spec §9, §30 |
| REQ-RS-006 | Render final README with BEGIN/END markers around generated blocks | User spec §27 |
| REQ-RS-007 | Validate README claims against repo truth (package name, version, links) | User spec §36 |
| REQ-RS-008 | Detect staleness via timestamp-stripped hash comparison | User spec §32 |
| REQ-RS-009 | Orchestrate full/single/validate/drift-only modes via CLI | User spec §33 |
| REQ-RS-010 | Backup README before first modification | User spec §28 |
| REQ-RS-011 | Idempotent: second run on unchanged repo produces zero diff | User spec §47 |
| REQ-RS-012 | Preservation validation: detect maintained content loss | User spec §37 |
| REQ-RS-013 | Governance validator for stale README detection | User spec §46 |
| REQ-RS-014 | Skill registration for `/sync-readmes` command | User spec §38 |
| REQ-RS-015 | Pilot on 3 representative README categories before portfolio backfill | User spec §43 |
| REQ-RS-016 | Full portfolio backfill across all 30 READMEs | User spec §44 |

---

## Wave 0: Core Tooling

### TC-README-W0-001: Section Schema and Heading Alias Map

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Create section schema definitions and heading alias map that support both Python FOSS and .NET commercial README structures.
**Requirements:** REQ-RS-001, REQ-RS-002

**Scope:**
- Allowed files: `tools/readme_sync/__init__.py`, `tools/readme_sync/section_schema.py`
- Allowed folders: `tools/readme_sync/`
- Forbidden: Any file outside `tools/readme_sync/`

**Preserved behavior:** No existing files are modified.

**Child Taskcards:**

#### TC-README-W0-001-01: Create package marker
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-001
**Purpose:** Initialize `tools/readme_sync/` as a Python package.

**Micro-steps:**
- MS-W0-001-01-01: Create `tools/readme_sync/__init__.py` with docstring and empty body. **Target:** `tools/readme_sync/__init__.py`. **Expected output:** File exists, importable. **Completion check:** `python -c "import sys; sys.path.insert(0,'tools'); import readme_sync"` exits 0.

#### TC-README-W0-001-02: Define SectionDef dataclass and section manifests
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-001
**Depends on:** TC-README-W0-001-01
**Purpose:** Define the data model for section classification.

**Micro-steps:**
- MS-W0-001-02-01: Create `tools/readme_sync/section_schema.py`. Define `SectionDef` dataclass with fields: `heading: str`, `section_id: str`, `classification: str` (MAINTAINED|GENERATED|HYBRID), `required: bool`, `order: int`, `generator_name: str | None`, `heading_aliases: list[str]`. **Target:** `tools/readme_sync/section_schema.py`.
- MS-W0-001-02-02: Define `PYTHON_FOSS_SECTIONS` list with entries for: title (MAINTAINED, order=0), installation (GENERATED, order=10, aliases=["Installation"]), quick_start (MAINTAINED, order=20, aliases=["Quick Start", "Getting Started", "Usage"]), public_api (GENERATED, order=30, aliases=["Public API"]), features (MAINTAINED, order=40, aliases=["Features", "Supported Features", "Capabilities"]), security_notes (MAINTAINED, order=50, aliases=["Security Notes", "Security"]), requirements_coverage (MAINTAINED, order=60, aliases=["Requirements Coverage"]), package_info (GENERATED, order=70, required=True), package_structure (MAINTAINED, order=80, aliases=["Package Structure", "Source Layout", "Folder Contents"]), running_tests (MAINTAINED, order=90, aliases=["Running Tests", "Tests"]), license (GENERATED, order=100, required=True, aliases=["License"]). **Target:** same file.
- MS-W0-001-02-03: Define `DOTNET_COMMERCIAL_SECTIONS` list covering: title (MAINTAINED), status (MAINTAINED, aliases=["Status", "Status: Gate 11*"]), scope (MAINTAINED), dec_033 (MAINTAINED, aliases=["DEC-033*"]), current_implementation (MAINTAINED, aliases=["Current Implementation*"]), what_remains (MAINTAINED, aliases=["What Remains*"]), installation (GENERATED, order=60), package_info (GENERATED, order=70, required=True), commercial_licensing (MAINTAINED), references (MAINTAINED), license (GENERATED, order=100). **Target:** same file.
- MS-W0-001-02-04: Define `DOTNET_MINIMAL_SECTIONS` list for export helpers (HTML/Markdown/TXT): title (MAINTAINED), classification (MAINTAINED), usage (MAINTAINED), gate_status (MAINTAINED), package_info (GENERATED, required=True). **Target:** same file.
- MS-W0-001-02-05: Define `DOTNET_STANDARD_SECTIONS` for CSV/NDJSON/TSV/Netpbm/ZST .NET: same as PYTHON_FOSS_SECTIONS but with gate_status (MAINTAINED) added. **Target:** same file.
- MS-W0-001-02-06: Define `get_schema_for_format(format_id: str, track: str) -> list[SectionDef]` that returns the appropriate schema. Logic: if track=dotnet and format_id in (html, markdown, txt) → DOTNET_MINIMAL; if track=dotnet and format_id in (fods, fodt) → DOTNET_COMMERCIAL; if track=dotnet → DOTNET_STANDARD; else → PYTHON_FOSS. **Target:** same file.
- MS-W0-001-02-07: Define `match_heading(heading: str, schema: list[SectionDef]) -> SectionDef | None` that matches a README heading against schema entries using case-insensitive alias matching with glob-style wildcards (e.g., "Status: Gate 11*" matches "Status: Gate 11 commercial_readiness_in_progress — NOT Release-Ready"). **Target:** same file.

**Acceptance checks:**
- `get_schema_for_format("fods", "python")` returns PYTHON_FOSS_SECTIONS
- `get_schema_for_format("html", "dotnet")` returns DOTNET_MINIMAL_SECTIONS
- `get_schema_for_format("fods", "dotnet")` returns DOTNET_COMMERCIAL_SECTIONS
- `match_heading("## Quick Start", PYTHON_FOSS_SECTIONS)` returns the quick_start SectionDef
- `match_heading("## Status: Gate 11 commercial_readiness_in_progress — NOT Release-Ready", DOTNET_COMMERCIAL_SECTIONS)` returns the status SectionDef

**Evidence:** Unit test in `tests/tools/test_readme_sync.py` with assertions for all schema lookups and heading matches.

**Closeout criteria:** All acceptance checks pass. Schema covers all 5 README categories observed in repo.

---

### TC-README-W0-002: Format State Collector

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Collect verified format metadata from repository data sources without importing format code.
**Requirements:** REQ-RS-003

**Scope:**
- Allowed files: `tools/readme_sync/collector.py`
- Allowed folders: `tools/readme_sync/`
- Forbidden: Any `src/python/{fmt}/` or `src/net/{fmt}/` source file modification

**Dependencies:** TC-README-W0-001 (needs `__init__.py`)

**Child Taskcards:**

#### TC-README-W0-002-01: Implement collector module
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-002
**Depends on:** TC-README-W0-001-01

**Micro-steps:**
- MS-W0-002-01-01: Create `tools/readme_sync/collector.py`. Import `tomllib` (Python 3.11+), `xml.etree.ElementTree`, `yaml`, `pathlib`, `ast`, `re`. Define `REPO_ROOT = Path(__file__).resolve().parents[2]`. **Target:** `tools/readme_sync/collector.py`.
- MS-W0-002-01-02: Implement `_read_format_registry(format_id: str) -> dict | None`. Opens `registry/format-registry.yaml`, finds the entry where `format_id` matches, returns dict with keys: display_name, family, extensions, mime_type, spec_body, spec_version, spec_url, gate_1_status, gate_11_status. Returns None if format not found. **Target:** same file.
- MS-W0-002-01-03: Implement `_read_pyproject(format_id: str) -> dict | None`. Opens `src/python/{format_id}/pyproject.toml` with `tomllib.load()`. Extracts: name, version, description, license (from `project.license.text`), requires_python, dependencies (list). Returns None if file not found. **Target:** same file.
- MS-W0-002-01-04: Implement `_read_csproj(format_id: str) -> dict | None`. Globs `src/net/{format_id}/*.csproj`, parses first match with ElementTree. Extracts from `<PropertyGroup>`: Version, AssemblyName, TargetFramework, Description. Extracts `<PackageReference>` Include+Version as dependencies list. Returns None if no csproj found. **Target:** same file.
- MS-W0-002-01-05: Implement `_read_qname_registry(format_id: str) -> dict`. Opens `shared/qname-registry/{format_id}.yaml`. Counts total entries and entries with `status: implemented`. Returns `{"qname_count": N, "qname_implemented_count": M}`. Returns `{"qname_count": 0, "qname_implemented_count": 0}` if file not found. **Target:** same file.
- MS-W0-002-01-06: Implement `_count_source_files(format_id: str, track: str) -> int`. Counts `.py` files (excluding `__pycache__`, `build/`, `*.egg-info/`) for Python track, or `.cs` files (excluding `bin/`, `obj/`) for dotnet track, under `src/{track}/{format_id}/`. **Target:** same file.
- MS-W0-002-01-07: Implement `_count_test_files(format_id: str, track: str) -> int`. Counts `test_*.py` files for Python, `*Tests.cs` files for dotnet, under `tests/{track}/{format_id}/`. **Target:** same file.
- MS-W0-002-01-08: Implement `_read_python_exports(format_id: str) -> list[str]`. Opens `src/python/{format_id}/__init__.py`, extracts `__version__`, `__track__`, `__commercial_ready__`, `__capability_level__` via regex. For `__all__`: if statically defined (list literal), parse with `ast.literal_eval`; if dynamically computed (list comprehension), return `["(dynamic)"]`. Returns list of export names. **Target:** same file.
- MS-W0-002-01-09: Implement `collect_format_state(format_id: str, track: str) -> dict`. Calls all sub-collectors, merges results into single dict. Keys: `format_id`, `track`, `display_name`, `family`, `extensions`, `mime_type`, `spec_body`, `spec_version`, `spec_url`, `gate_1_status`, `gate_11_status`, `package_name`, `version`, `description`, `license`, `requires_python`, `target_framework`, `dependencies`, `qname_count`, `qname_implemented_count`, `source_file_count`, `test_file_count`, `public_api_exports`, `python_version_meta`, `python_track_meta`, `python_commercial_ready`. **Target:** same file.
- MS-W0-002-01-10: Implement `collect_all_formats() -> list[dict]`. Discovers all format directories from `src/python/*/` and `src/net/*/` (excluding `__pycache__`, `build`). Calls `collect_format_state` for each. Returns list of state dicts. **Target:** same file.

**Acceptance checks:**
- `collect_format_state("fods", "python")` returns dict with `display_name="Flat OpenDocument Spreadsheet"`, `package_name="format-factory-fods"`, `version="0.1.0"`, `qname_count>=8`, `source_file_count>=6`, `test_file_count>=50`
- `collect_format_state("fods", "dotnet")` returns dict with `target_framework="net10.0"`, `gate_11_status` present
- `collect_format_state("csv", "python")` returns dict with `package_name` containing "csv"
- `collect_all_formats()` returns list with >=30 entries

**Evidence:** Test assertions in `tests/tools/test_readme_sync.py::test_collector_*`.

**Rollback:** Delete `tools/readme_sync/collector.py`. No other files touched.

**Closeout criteria:** All acceptance checks pass. No format code imported. All 30 format+track combos return non-None state dicts.

---

### TC-README-W0-003: README Parser and Reconciler

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Parse existing READMEs into classified sections and reconcile with generated data, preserving maintained content.
**Requirements:** REQ-RS-001, REQ-RS-002, REQ-RS-005, REQ-RS-010, REQ-RS-012

**Scope:**
- Allowed files: `tools/readme_sync/reconciler.py`
- Forbidden: Modification of any README.md file (this module is pure logic)

**Dependencies:** TC-README-W0-001 (section_schema.py)

**Child Taskcards:**

#### TC-README-W0-003-01: Implement Section and ClassifiedSection dataclasses
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-003

**Micro-steps:**
- MS-W0-003-01-01: Create `tools/readme_sync/reconciler.py`. Define `Section` dataclass: `heading: str` (the `##` line, empty for preamble), `body: str` (content between headings), `line_start: int`, `line_end: int`. **Target:** `tools/readme_sync/reconciler.py`.
- MS-W0-003-01-02: Define `ClassifiedSection` dataclass extending Section: `section_id: str`, `classification: str` (MAINTAINED|GENERATED|HYBRID|UNKNOWN), `matched_def: SectionDef | None`, `has_markers: bool` (True if BEGIN/END markers present in body). **Target:** same file.

#### TC-README-W0-003-02: Implement parse_readme
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-003
**Depends on:** TC-README-W0-003-01

**Micro-steps:**
- MS-W0-003-02-01: Implement `parse_readme(content: str) -> list[Section]`. Split content by lines matching `^#{1,3} ` (heading regex). Content before first heading is Section with `heading=""` (preamble — holds frontmatter). Each subsequent heading starts a new Section. Track line_start/line_end. Handle edge cases: empty file → single empty preamble section; file with no headings → single preamble section. **Target:** `tools/readme_sync/reconciler.py`.
- MS-W0-003-02-02: Add special handling for YAML frontmatter: if content starts with `---\n`, treat everything up to and including the closing `---\n` as part of the preamble section (even if it contains `#` characters). **Target:** same file.

**Acceptance checks:**
- `parse_readme(fods_python_readme)` returns 6 sections (preamble + 5 headings: Quick Start, Security Notes, Requirements Coverage, Package Structure + title)
- `parse_readme(csv_python_readme)` returns 5 sections (preamble + Installation, Quick Start, Features, License + title)
- `parse_readme("")` returns 1 section (empty preamble)
- Preamble section for FODS Python contains all 13 frontmatter lines

#### TC-README-W0-003-03: Implement classify_sections
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-003
**Depends on:** TC-README-W0-003-02, TC-README-W0-001-02

**Micro-steps:**
- MS-W0-003-03-01: Implement `classify_sections(sections: list[Section], format_id: str, track: str) -> list[ClassifiedSection]`. For each section: call `match_heading(section.heading, schema)`. If matched → use SectionDef's classification and section_id. If unmatched → classification=MAINTAINED, section_id derived from heading slug. Check body for `<!-- BEGIN:README-` markers → set has_markers=True. Preamble (heading="") always MAINTAINED. **Target:** `tools/readme_sync/reconciler.py`.

**Acceptance checks:**
- FODS Python: "Quick Start" classified MAINTAINED, "Security Notes" classified MAINTAINED
- CSV Python: "Installation" classified GENERATED, "Features" classified MAINTAINED
- FODS .NET: "DEC-033 Option B" classified MAINTAINED, "Status: Gate 11..." classified MAINTAINED

#### TC-README-W0-003-04: Implement reconcile
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-003
**Depends on:** TC-README-W0-003-03

**Micro-steps:**
- MS-W0-003-04-01: Implement `reconcile(sections: list[ClassifiedSection], state: dict, schema: list[SectionDef]) -> list[ClassifiedSection]`. Rules: (1) MAINTAINED sections → preserved exactly. (2) GENERATED sections with existing markers → body between markers replaced. (3) GENERATED sections without markers → body wrapped in new markers. (4) Missing required GENERATED sections → new ClassifiedSection created with generated body and markers, inserted at canonical order position relative to existing sections. (5) UNKNOWN sections → treated as MAINTAINED. **Target:** `tools/readme_sync/reconciler.py`.
- MS-W0-003-04-02: Implement `_find_insertion_point(sections: list[ClassifiedSection], order: int) -> int`. Finds the index where a new section with the given order should be inserted, respecting the canonical ordering of already-present sections. **Target:** same file.

**Acceptance checks:**
- Reconciling FODS Python with its own state produces sections list where all MAINTAINED sections have identical body content
- Reconciling CSV Python adds PACKAGE_INFO section (missing) and wraps INSTALLATION in markers
- Reconciling FODS .NET preserves all 7 existing sections and adds PACKAGE_INFO

**Closeout criteria:** Round-trip test: `parse_readme → classify → reconcile → render` on FODS Python README produces content where every MAINTAINED line matches original.

---

### TC-README-W0-004: Content Generators (Renderer)

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Generate verified content blocks for GENERATED sections.
**Requirements:** REQ-RS-004, REQ-RS-006

**Scope:**
- Allowed files: `tools/readme_sync/renderer.py`
- Forbidden: Any README.md modification

**Dependencies:** TC-README-W0-001 (section_schema), TC-README-W0-002 (collector)

**Child Taskcards:**

#### TC-README-W0-004-01: Implement renderer module with markers and generators
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-004
**Depends on:** TC-README-W0-001-02, TC-README-W0-002-01

**Micro-steps:**
- MS-W0-004-01-01: Create `tools/readme_sync/renderer.py`. Define `BEGIN_TMPL = "<!-- BEGIN:README-{section_id} generated={ts} source=tools/readme_sync -->"`, `END_TMPL = "<!-- END:README-{section_id} -->"`. Define `_strip_timestamps(text: str) -> str` using `re.sub(r'generated=[^\s>]+', 'generated=STRIPPED', text)`. **Target:** `tools/readme_sync/renderer.py`.
- MS-W0-004-01-02: Implement `gen_installation(state: dict) -> str`. If track=python: `pip install {package_name}`. If track=dotnet: `dotnet add package {package_name}`. Wrap in code block. **Target:** same file.
- MS-W0-004-01-03: Implement `gen_package_info(state: dict) -> str`. Render a Markdown table with rows: Format, Package, Version, License, Spec (if available), QNames (mapped/total), Source files, Test files. Only include rows where data is available. **Target:** same file.
- MS-W0-004-01-04: Implement `gen_public_api(state: dict) -> str`. If public_api_exports is not empty and not `["(dynamic)"]`, render as bullet list. If dynamic, render note: "Public API is dynamically exported — see `__init__.py`." Only for Python track. **Target:** same file.
- MS-W0-004-01-05: Implement `gen_license(state: dict) -> str`. Render license identifier (e.g., "Apache-2.0"). **Target:** same file.
- MS-W0-004-01-06: Implement `gen_dotnet_status(state: dict) -> str`. Render Gate 11 status from `gate_11_status` field. **Target:** same file.
- MS-W0-004-01-07: Implement `render_readme(sections: list[ClassifiedSection], state: dict) -> str`. Iterate sections. For MAINTAINED: emit heading + body verbatim. For GENERATED: emit heading, then `BEGIN_TMPL`, then call appropriate `gen_*` function by `matched_def.generator_name`, then `END_TMPL`. For preamble (no heading): emit body verbatim. Join with consistent newlines. Ensure file ends with single newline. **Target:** same file.
- MS-W0-004-01-08: Implement `write_with_backup(readme_path: Path, new_content: str, original_content: str) -> bool`. Compare `_strip_timestamps(new_content)` vs `_strip_timestamps(original_content)`. If equal, return False (no change). Otherwise: create backup at `.local/archive/readme-{fmt}-{track}-pre-sync-{ts}.md`, write new_content to readme_path, return True. **Target:** same file.

**Acceptance checks:**
- `gen_installation({"track": "python", "package_name": "format-factory-fods"})` produces string containing `pip install format-factory-fods`
- `gen_package_info(fods_state)` produces Markdown table with Version row showing "0.1.0"
- `render_readme(reconciled_sections, fods_state)` produces string with `<!-- BEGIN:README-PACKAGE_INFO` marker
- `write_with_backup` returns False when called twice with same content (idempotency)

**Closeout criteria:** All generators produce valid Markdown. Rendered output for FODS Python contains markers around generated blocks and byte-identical maintained content.

---

### TC-README-W0-005: Orchestrator, Validator, and Drift Detector

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** CLI orchestrator with mode dispatch, README validation, and drift detection.
**Requirements:** REQ-RS-007, REQ-RS-008, REQ-RS-009, REQ-RS-011

**Scope:**
- Allowed files: `tools/readme_sync/run_sync.py`, `tools/readme_sync/validator.py`, `tools/readme_sync/drift_detector.py`
- Forbidden: Modification of any non-`tools/readme_sync/` file

**Dependencies:** TC-README-W0-002, TC-README-W0-003, TC-README-W0-004

**Child Taskcards:**

#### TC-README-W0-005-01: Implement validator
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-005

**Micro-steps:**
- MS-W0-005-01-01: Create `tools/readme_sync/validator.py`. Define `ValidationResult` dataclass: `readme_path: str`, `format_id: str`, `track: str`, `issues: list[str]` (warnings), `errors: list[str]` (blockers), `stale_sections: list[str]`. **Target:** `tools/readme_sync/validator.py`.
- MS-W0-005-01-02: Implement `validate_readme(readme_path: Path, format_id: str, track: str) -> ValidationResult`. Checks: (1) Required sections from schema are present. (2) GENERATED sections have BEGIN/END markers (warning if missing — means sync hasn't run yet). (3) Package name in README matches pyproject.toml/csproj (error if mismatch). (4) Version in README matches (error if mismatch). (5) Repository-relative links in README resolve to existing paths (warning per broken link). **Target:** same file.
- MS-W0-005-01-03: Implement `validate_all() -> list[ValidationResult]`. Discovers all format READMEs, calls `validate_readme` for each, returns list. **Target:** same file.

#### TC-README-W0-005-02: Implement drift detector
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-005

**Micro-steps:**
- MS-W0-005-02-01: Create `tools/readme_sync/drift_detector.py`. Implement `check_readme_drift(format_id: str, track: str) -> dict`. Reads existing README, runs full collect→reconcile→render pipeline in memory, compares `_strip_timestamps(rendered)` vs `_strip_timestamps(existing)`. Returns `{"drifted": bool, "format_id": str, "track": str, "reason": str}`. **Target:** `tools/readme_sync/drift_detector.py`.
- MS-W0-005-02-02: Implement `check_all_drift() -> dict`. Runs `check_readme_drift` for all formats. Returns `{"overall": "NO_DRIFT"|"DRIFT", "results": [...]}`. **Target:** same file.
- MS-W0-005-02-03: Implement `main() -> int`. CLI: `--output path` for JSON report. Exit 0 = no drift, exit 1 = drift detected. **Target:** same file.

#### TC-README-W0-005-03: Implement orchestrator
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-005
**Depends on:** TC-README-W0-005-01, TC-README-W0-005-02

**Micro-steps:**
- MS-W0-005-03-01: Create `tools/readme_sync/run_sync.py`. Define argparse CLI: `--mode {full,single,validate,drift-only}`, `--format FMT`, `--track {python,dotnet}`, `--dry-run`. **Target:** `tools/readme_sync/run_sync.py`.
- MS-W0-005-03-02: Implement `sync_single(format_id, track, dry_run) -> bool`. Full pipeline: collect_format_state → parse_readme → classify_sections → reconcile → render_readme → write_with_backup (or print diff if dry_run). Returns True if file changed. **Target:** same file.
- MS-W0-005-03-03: Implement `sync_all(dry_run) -> dict`. Calls `sync_single` for all discovered format+track combos. Returns summary `{"processed": N, "changed": M, "errors": [...]}`. **Target:** same file.
- MS-W0-005-03-04: Implement `main() -> int`. Mode dispatch: `full` → sync_all; `single` → sync_single (requires --format and --track); `validate` → validate_all; `drift-only` → check_all_drift. Exit codes: 0 = success/no-drift, 1 = drift/errors. Print summary. **Target:** same file.

**Acceptance checks:**
- `python tools/readme_sync/run_sync.py --mode drift-only` runs without error (detects drift on un-synced READMEs)
- `python tools/readme_sync/run_sync.py --mode validate` reports missing markers as warnings
- `python tools/readme_sync/run_sync.py --mode single --format fods --track python --dry-run` prints diff without modifying file

**Closeout criteria:** All CLI modes work. `--dry-run` never writes. Exit codes match spec.

---

### TC-README-W0-006: Unit Test Suite

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Comprehensive unit tests for all readme_sync modules.
**Requirements:** REQ-RS-011

**Scope:**
- Allowed files: `tests/tools/test_readme_sync.py`
- Forbidden: Modification of any non-test file

**Dependencies:** TC-README-W0-001 through TC-README-W0-005

**Child Taskcards:**

#### TC-README-W0-006-01: Write unit tests
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W0-006

**Micro-steps:**
- MS-W0-006-01-01: Create `tests/tools/test_readme_sync.py`. Test `section_schema`: schema lookups, heading matching (case-insensitive, alias, wildcard). **Target:** `tests/tools/test_readme_sync.py`.
- MS-W0-006-01-02: Test `collector`: `collect_format_state("fods", "python")` returns expected fields; `collect_format_state("fods", "dotnet")` returns expected fields; `collect_format_state("csv", "python")` returns expected fields. Assert no format code imports (collector uses only stdlib + yaml). **Target:** same file.
- MS-W0-006-01-03: Test `reconciler`: parse FODS Python README → correct section count; parse CSV Python README → correct section count; classify → correct classifications; reconcile → maintained sections unchanged. **Target:** same file.
- MS-W0-006-01-04: Test `renderer`: gen_installation produces correct output; gen_package_info produces valid Markdown table; render_readme produces markers around generated blocks. **Target:** same file.
- MS-W0-006-01-05: Test idempotency: run full pipeline twice on FODS Python, assert second render equals first render (after timestamp stripping). **Target:** same file.
- MS-W0-006-01-06: Test preservation: parse → classify → reconcile → render FODS Python README. Extract all MAINTAINED section bodies from original. Assert each appears byte-identical in rendered output. **Target:** same file.
- MS-W0-006-01-07: Test negative control: remove a MAINTAINED section from rendered output, run validator, assert it detects the missing section. **Target:** same file.

**Acceptance checks:**
- `python -m pytest tests/tools/test_readme_sync.py -v` — all tests pass
- At least 15 test functions covering schema, collector, reconciler, renderer, idempotency, preservation

**Closeout criteria:** All tests pass. Coverage includes all 3 README categories (ODF-rich, short-form, .NET commercial).

---

## Wave 1: Pilots

### TC-README-W1-001: Pilot — FODS Python (ODF-rich)

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Prove preservation-first sync on the most complex Python README.
**Requirements:** REQ-RS-011, REQ-RS-012, REQ-RS-015

**Dependencies:** TC-README-W0-005 (orchestrator complete)

**Child Taskcards:**

#### TC-README-W1-001-01: Execute sync and verify preservation
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W1-001

**Micro-steps:**
- MS-W1-001-01-01: Record SHA-256 of `src/python/fods/README.md` before sync. **Completion check:** hash captured.
- MS-W1-001-01-02: Run `python tools/readme_sync/run_sync.py --mode single --format fods --track python`. **Expected output:** File updated with generated markers.
- MS-W1-001-01-03: Verify YAML frontmatter (lines 1-13) preserved verbatim via diff. **Completion check:** `diff` shows no changes to lines 1-13.
- MS-W1-001-01-04: Verify "Quick Start" section body unchanged via diff. **Completion check:** code block preserved byte-for-byte.
- MS-W1-001-01-05: Verify "Security Notes" section body unchanged. **Completion check:** all 4 bullet points present and unchanged.
- MS-W1-001-01-06: Verify "Requirements Coverage" section body unchanged.
- MS-W1-001-01-07: Verify "Package Structure" code block unchanged.
- MS-W1-001-01-08: Verify new `<!-- BEGIN:README-PACKAGE_INFO -->` block present with correct version, spec, QName data.
- MS-W1-001-01-09: Run sync again. Verify zero diff (idempotency). **Completion check:** `git diff src/python/fods/README.md` returns empty.
- MS-W1-001-01-10: Run `python tools/readme_sync/run_sync.py --mode drift-only --format fods --track python`. Verify exit 0. **Completion check:** exit code is 0.

**Acceptance checks:** All 10 micro-steps complete. Backup file exists in `.local/archive/`.

---

### TC-README-W1-002: Pilot — CSV Python (short-form)

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Prove sync on a minimal README without frontmatter.
**Requirements:** REQ-RS-011, REQ-RS-012, REQ-RS-015

**Dependencies:** TC-README-W0-005

**Child Taskcards:**

#### TC-README-W1-002-01: Execute sync and verify preservation
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W1-002

**Micro-steps:**
- MS-W1-002-01-01: Record SHA-256 of `src/python/csv/README.md` before sync.
- MS-W1-002-01-02: Run `python tools/readme_sync/run_sync.py --mode single --format csv --track python`.
- MS-W1-002-01-03: Verify "Quick Start" code example preserved byte-for-byte (both class-based and function API examples).
- MS-W1-002-01-04: Verify "Features" bullet list preserved.
- MS-W1-002-01-05: Verify "Installation" section has markers wrapping `pip install` command, command text unchanged.
- MS-W1-002-01-06: Verify new `<!-- BEGIN:README-PACKAGE_INFO -->` block added.
- MS-W1-002-01-07: Run sync again. Verify zero diff (idempotency).

---

### TC-README-W1-003: Pilot — FODS .NET (commercial)

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Prove sync on a .NET commercial README with Gate 11 content.
**Requirements:** REQ-RS-011, REQ-RS-012, REQ-RS-015

**Dependencies:** TC-README-W0-005

**Child Taskcards:**

#### TC-README-W1-003-01: Execute sync and verify preservation
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W1-003

**Micro-steps:**
- MS-W1-003-01-01: Record SHA-256 of `src/net/fods/README.md` before sync.
- MS-W1-003-01-02: Run `python tools/readme_sync/run_sync.py --mode single --format fods --track dotnet`.
- MS-W1-003-01-03: Verify "Status: Gate 11..." section prose preserved (entire paragraph about NOT Release-Ready).
- MS-W1-003-01-04: Verify "DEC-033 Option B" section preserved verbatim (all 3 bullet points).
- MS-W1-003-01-05: Verify "Current Implementation" section with subsections preserved.
- MS-W1-003-01-06: Verify "What Remains for Gate 11" numbered list preserved.
- MS-W1-003-01-07: Verify "Commercial Licensing" and "References" sections preserved.
- MS-W1-003-01-08: Verify new `<!-- BEGIN:README-PACKAGE_INFO -->` block added with .csproj data.
- MS-W1-003-01-09: Run sync again. Verify zero diff (idempotency).

---

## Wave 2: Portfolio Backfill

### TC-README-W2-001: Full Portfolio Sync

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Sync all 30 READMEs with verified generated data while preserving all maintained content.
**Requirements:** REQ-RS-016

**Dependencies:** TC-README-W1-001, TC-README-W1-002, TC-README-W1-003 (all pilots pass)

**Child Taskcards:**

#### TC-README-W2-001-01: Execute full sync
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W2-001

**Micro-steps:**
- MS-W2-001-01-01: Run `python tools/readme_sync/run_sync.py --mode full --dry-run`. Review output for any unexpected deletions or errors. **Completion check:** no errors, no maintained content flagged for deletion.
- MS-W2-001-01-02: Run `python tools/readme_sync/run_sync.py --mode full`. **Expected output:** 30 READMEs processed.
- MS-W2-001-01-03: Run `git diff --stat` to verify scope of changes. Only files under `src/python/*/README.md` and `src/net/*/README.md` should be modified. **Completion check:** no unexpected files.
- MS-W2-001-01-04: Run `git diff` and manually inspect that no maintained lines were deleted (only additions and marker insertions). **Completion check:** diff shows no `-` lines for maintained content.
- MS-W2-001-01-05: Run `python tools/readme_sync/run_sync.py --mode drift-only`. Verify exit 0. **Completion check:** exit code is 0.
- MS-W2-001-01-06: Run `python tools/readme_sync/run_sync.py --mode validate`. Verify exit 0 (no errors). **Completion check:** exit code is 0.
- MS-W2-001-01-07: Run `python tools/readme_sync/run_sync.py --mode full` again. Verify zero files changed (idempotency). **Completion check:** output shows "0 files changed".

**Acceptance checks:** All 30 READMEs have PACKAGE_INFO generated blocks. All maintained content preserved. Idempotent.

**Rollback:** `git checkout -- src/python/*/README.md src/net/*/README.md`. Backup files in `.local/archive/`.

---

## Wave 3: Governance Integration

### TC-README-W3-001: Governance Validator

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Add README freshness validation to governance validators.
**Requirements:** REQ-RS-013

**Dependencies:** TC-README-W2-001 (portfolio sync complete)

**Scope:**
- Allowed files: `tools/governance/governance_validators_ext2.py` (or ext3 if ext2 is full), `tests/tools/test_governance_validators.py`
- Forbidden: Modification of any README.md

**Child Taskcards:**

#### TC-README-W3-001-01: Add validate_readme_freshness validator
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W3-001

**Micro-steps:**
- MS-W3-001-01-01: Read `tools/governance/governance_validators_ext2.py` to understand V82 pattern (latest validator). Identify insertion point and naming convention.
- MS-W3-001-01-02: Add `validate_readme_freshness()` function (V83 or next available number). Calls `drift_detector.check_all_drift()`. Returns PASS if no drift, FAIL with list of stale READMEs if drift. **Target:** governance validators file.
- MS-W3-001-01-03: Add test for V83 in governance validator tests. **Target:** `tests/tools/test_governance_validators.py`.
- MS-W3-001-01-04: Run governance validator tests. Verify new test passes. **Completion check:** test exits 0.

---

### TC-README-W3-002: Skill Registration

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Register `/sync-readmes` as a discoverable skill.
**Requirements:** REQ-RS-014

**Dependencies:** TC-README-W0-005

**Child Taskcards:**

#### TC-README-W3-002-01: Create command file and register skill
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W3-002

**Micro-steps:**
- MS-W3-002-01-01: Create `.claude/commands/sync-readmes.md` with skill prompt that calls `python tools/readme_sync/run_sync.py --mode full`. Follow pattern of `.claude/commands/sync-capabilities.md`. **Target:** `.claude/commands/sync-readmes.md`.
- MS-W3-002-01-02: Add skill entry to `.supervisor/skill-registry.yaml` with `skill_id: sync-readmes`, `status: active`, `product_track: layer_governance`. **Target:** `.supervisor/skill-registry.yaml`.
- MS-W3-002-01-03: Add command entry to `.claude/commands/command-registry.yaml`. **Target:** `.claude/commands/command-registry.yaml`.
- MS-W3-002-01-04: Run `/sync-capabilities` to verify the new skill appears in the capability index. **Completion check:** `sync-readmes` appears in `.governance/capabilities/registry.yaml`.

---

### TC-README-W3-003: Trigger Documentation

**Type:** PARENT
**Status:** CLOSED
**Owner:** Worker Agent
**Objective:** Document when README sync should be triggered.
**Requirements:** REQ-RS-008

**Child Taskcards:**

#### TC-README-W3-003-01: Create trigger documentation
**Type:** CHILD | **Status:** CLOSED | **Parent:** TC-README-W3-003

**Micro-steps:**
- MS-W3-003-01-01: Create `docs/automation/readme-sync-triggers.md`. Document: (1) After `pyproject.toml` or `.csproj` version bumps, (2) After QName registry changes, (3) After new test files added to `tests/{track}/{fmt}/`, (4) During sprint closeout (best-effort, non-blocking — same pattern as capability_sync), (5) Before release/package preparation. Include `python tools/readme_sync/run_sync.py --mode drift-only` as the CI check command. **Target:** `docs/automation/readme-sync-triggers.md`.

---

## Execution DAG

```
TC-README-W0-001 (schema)
    ↓
TC-README-W0-002 (collector) ──────┐
    ↓                               ↓
TC-README-W0-003 (reconciler) ── TC-README-W0-004 (renderer)
    ↓                               ↓
    └───────────┬───────────────────┘
                ↓
TC-README-W0-005 (orchestrator+validator+drift)
                ↓
TC-README-W0-006 (unit tests)
                ↓
    ┌───────────┼───────────────────┐
    ↓           ↓                   ↓
TC-README-W1-001  TC-README-W1-002  TC-README-W1-003  (pilots, parallel-safe)
    └───────────┼───────────────────┘
                ↓
TC-README-W2-001 (portfolio backfill)
                ↓
    ┌───────────┼───────────────────┐
    ↓           ↓                   ↓
TC-README-W3-001  TC-README-W3-002  TC-README-W3-003  (governance, parallel-safe)
```

## File Ownership

| File | Owner Taskcard | Operation |
|---|---|---|
| `tools/readme_sync/__init__.py` | TC-README-W0-001-01 | CREATE |
| `tools/readme_sync/section_schema.py` | TC-README-W0-001-02 | CREATE |
| `tools/readme_sync/collector.py` | TC-README-W0-002-01 | CREATE |
| `tools/readme_sync/reconciler.py` | TC-README-W0-003 children | CREATE |
| `tools/readme_sync/renderer.py` | TC-README-W0-004-01 | CREATE |
| `tools/readme_sync/validator.py` | TC-README-W0-005-01 | CREATE |
| `tools/readme_sync/drift_detector.py` | TC-README-W0-005-02 | CREATE |
| `tools/readme_sync/run_sync.py` | TC-README-W0-005-03 | CREATE |
| `tests/tools/test_readme_sync.py` | TC-README-W0-006-01 | CREATE |
| `src/python/*/README.md` | TC-README-W1/W2 | MODIFY (preserving) |
| `src/net/*/README.md` | TC-README-W1/W2 | MODIFY (preserving) |
| Governance validator file | TC-README-W3-001-01 | MODIFY (append) |
| `.claude/commands/sync-readmes.md` | TC-README-W3-002-01 | CREATE |
| `.supervisor/skill-registry.yaml` | TC-README-W3-002-01 | MODIFY (append) |
| `.claude/commands/command-registry.yaml` | TC-README-W3-002-01 | MODIFY (append) |
| `docs/automation/readme-sync-triggers.md` | TC-README-W3-003-01 | CREATE |

---

## Verification Matrix

| Check | Type | Command | Expected | Taskcard |
|---|---|---|---|---|
| Schema lookup correctness | Unit | `pytest tests/tools/test_readme_sync.py -k test_schema` | PASS | W0-006 |
| Collector returns valid data | Unit | `pytest tests/tools/test_readme_sync.py -k test_collector` | PASS | W0-006 |
| Parser preserves frontmatter | Unit | `pytest tests/tools/test_readme_sync.py -k test_parse_frontmatter` | PASS | W0-006 |
| Classification correctness | Unit | `pytest tests/tools/test_readme_sync.py -k test_classify` | PASS | W0-006 |
| Maintained content unchanged | Unit | `pytest tests/tools/test_readme_sync.py -k test_preservation` | PASS | W0-006 |
| Idempotency (second run = no diff) | Integration | `run_sync.py --mode full` twice | 0 changes on 2nd | W1/W2 |
| Drift detection works | Integration | Modify pyproject.toml, run `--mode drift-only` | Exit 1 | W0-006 |
| Negative: missing section detected | Negative | Remove maintained section, run validate | Warning emitted | W0-006 |
| FODS Python pilot preservation | Pilot | `git diff src/python/fods/README.md` | No maintained deletions | W1-001 |
| CSV Python pilot preservation | Pilot | `git diff src/python/csv/README.md` | No maintained deletions | W1-002 |
| FODS .NET pilot preservation | Pilot | `git diff src/net/fods/README.md` | No maintained deletions | W1-003 |
| Full portfolio no-loss | Portfolio | `git diff --stat` after full sync | Only README.md files | W2-001 |
| Governance validator | Governance | `pytest test_governance_validators.py -k test_readme_freshness` | PASS | W3-001 |
| Skill discoverable | Integration | `/sync-capabilities` shows sync-readmes | Entry present | W3-002 |

---

## Quality Scoring Dimensions

Each child taskcard scored 1-5 on:
1. **Requirement correctness** — does it satisfy its mapped REQ-RS-* requirement?
2. **Implementation correctness** — does the code work as specified?
3. **Scope discipline** — no files outside allowed scope modified?
4. **Validation strength** — are tests present and passing?
5. **Evidence completeness** — are test logs and diffs captured?
6. **Regression safety** — no existing functionality broken?
7. **Preservation fidelity** — no maintained README content lost?

Acceptance threshold: all dimensions ≥ 4/5. Score < 4 → REROUTED.

---

## Rollback Strategy

- **Wave 0:** Delete `tools/readme_sync/` and `tests/tools/test_readme_sync.py`. No other files affected.
- **Wave 1-2:** `git checkout -- src/python/*/README.md src/net/*/README.md`. Backup files in `.local/archive/`.
- **Wave 3:** Revert governance validator addition, remove skill registry entries, delete command file.

---

## Critical Files Reference

| File | Role |
|---|---|
| [tools/capability_sync/run_sync.py](tools/capability_sync/run_sync.py) | Pattern: orchestrator |
| [tools/capability_sync/detect_drift.py](tools/capability_sync/detect_drift.py) | Pattern: drift detection |
| [tools/capability_sync/update_claude_instructions.py](tools/capability_sync/update_claude_instructions.py) | Pattern: BEGIN/END marker splicing |
| [tools/capability_sync/generate_discovery_indexes.py](tools/capability_sync/generate_discovery_indexes.py) | Pattern: pure content generation |
| [tools/capability_sync/validate_parity.py](tools/capability_sync/validate_parity.py) | Pattern: multi-check validation |
| [registry/format-registry.yaml](registry/format-registry.yaml) | Data: format metadata |
| [src/python/fods/README.md](src/python/fods/README.md) | Pilot: ODF-rich README (62 lines, YAML frontmatter) |
| [src/python/csv/README.md](src/python/csv/README.md) | Pilot: short-form README (34 lines, no frontmatter) |
| [src/net/fods/README.md](src/net/fods/README.md) | Pilot: .NET commercial README (64 lines, Gate 11 content) |
| [src/python/fods/pyproject.toml](src/python/fods/pyproject.toml) | Data: Python package metadata |
| [src/net/fods/FormatFactory.Fods.csproj](src/net/fods/FormatFactory.Fods.csproj) | Data: .NET package metadata |
| [shared/qname-registry/fods.yaml](shared/qname-registry/fods.yaml) | Data: QName mapping |

---

## Execution Handoff

**First taskcard to execute:** TC-README-W0-001-01 (create `__init__.py`)
**Execution order:** Follow DAG top-down. Within a wave, child taskcards execute sequentially per parent. Parents in the same wave may run in parallel only if they have no file ownership overlap (W1 pilots are parallel-safe; W3 governance tasks are parallel-safe).
**Evidence root:** `.local/evidences/readme-gov-001/`


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01T15:36:22+00:00"
  locked_by: "22efecc290b9"
  audit_gate: AUDIT_PASS
  mission_id: README-GOV-001
  all_taskcards_closed: true
  total_taskcards: 14
  completed_at: "2026-07-01"
  completion_summary: |
    All 14 taskcards CLOSED. tools/readme_sync/ module built (8 files).
    30 READMEs synced with generated markers (INSTALLATION, PACKAGE_INFO, PUBLIC_API, LICENSE).
    23/23 unit tests PASS (tests/tools/test_readme_sync.py).
    163/163 governance validator tests PASS (V87 validate_readme_freshness in ext2).
    /sync-readmes skill registered. Trigger docs written.
    Drift detector: NO_DRIFT verified after full sync 2026-07-01.
  mutation_policy: "TERMINAL — no further writes"
-->
