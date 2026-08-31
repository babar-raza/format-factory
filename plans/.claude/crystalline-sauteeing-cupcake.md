# Plan: Extract and Build libxliff — Standalone Professional XLIFF Library

authoritative_plan: C:\Users\prora\.claude\plans\crystalline-sauteeing-cupcake.md
in_repo_path: plans/.claude/crystalline-sauteeing-cupcake.md
plan_status: EXECUTION_READY
plan_version: 5.0
last_enhanced: 2026-08-12
governing_standard: Independent Python Format Library Extraction Standard v1.0
mission_1_status: CLOSED (2026-08-11) — extraction + 8 typed 2.1 modules + v0.1.0 release, 46/46 taskcards, TERMINAL_CLOSED then REOPENED for Mission 2
mission_2_status: ACTIVE — MVP expansion (this revision)

---

## Context (Mission 1 — historical, CLOSED, preserved for continuity)

The Format Factory monorepo contains a production XLIFF 2.0/2.1 implementation at
`src/python/xliff/src/format_factory/xliff/` (25 files, ~4,370 lines) with 53 test files
(~10,166 lines). It depends on `format-factory-core==0.1.0.dev0` for 14 names across 5
core modules (errors, diagnostics, limits, protocols, xml_security — ~350 lines total).

All 8 standard XLIFF 2.1 modules are `PRESERVATION_ONLY` — content round-trips as opaque
`ExtensionNode` objects but has no typed API.

The goal is to create `libxliff` as a fully independent, professionally useful XLIFF library
with typed module support, robust XML security, and clean packaging — following the same
engineering system, API philosophy, repository conventions, test organization, commit
discipline and autonomous execution model as the other standalone format libraries.

The donor implementation is mature and valuable. The migration strategy is
parity-first: prove the extracted code works identically before any redesign.

**Mission 1 result:** all 46 taskcards CLOSED, 15/15 release gate criteria PASS, v0.1.0
published to GitLab, 777 tests passing. Plan was locked TERMINAL_CLOSED on 2026-08-11.
A pilot rerun the same day (fresh venv, wheel-only install) reproduced all 15 gate
criteria and found zero regressions against the donor baseline (591→777 tests, +186).

---

## Context (Mission 2 — ACTIVE, this revision)

A follow-up capability audit against a much larger "professional MVP" bar (see
`docs/reference/xliff-technical-ecosystem-report.md`, copied 2026-08-12 from
`C:\Users\prora\Downloads\XLIFF-technical-ecosystem-product-opportunity-report.md`,
an 831-line OASIS/ISO-sourced XLIFF market and technical analysis dated 2026-08-12)
found that Mission 1 delivered a solid, secure, well-tested **XLIFF 2.0/2.1 Core**
library, but the library is not yet a professionally complete MVP by the standard a
developer would need to confidently embed it in CI, localization tooling, or automated
translation workflows. Concretely: zero XLIFF 1.2 support (deliberately rejected during
Mission 1, not a bug), no general version-conversion, zero PO/JSON/ARB/CSV/TMX
interoperability (the `adapters/` package is an empty docstring stub), no streaming API,
no atomic writes, minimal translation statistics (39-line stub), no CLI stats/diff, and
no fuzz/mutation/benchmark testing despite `hypothesis` being declared as a test
dependency and never used. One specific finding: Mission 1's closed taskcard
`TC-TEST-001` claimed property-based and mutation testing were delivered; verification
this session found neither actually exists in the test suite — this is a
`claimed_but_unproven` finding against a CLOSED taskcard, carried forward as
`TC-PBT-001`/`TC-MUT-001` below rather than silently reopening TC-TEST-001.

**Product charter (governs all Mission 2 scope decisions):**

> A secure, dependable, multi-version XLIFF processing library for developers, focused
> on accurate parsing, safe modification, standards-aware validation, lossless
> preservation, deterministic serialization, useful inspection, and automation-friendly
> tooling. Not a general XML binding. Not a CAT tool or TMS.

Mission 2 does not repeat Mission 1's extraction work and does not modify the 8 typed
2.1 modules, the security boundary, or the semantic validation layer — those are sound,
tested, and stay as-is. Mission 2 adds: XLIFF 1.2 Core (as a genuinely separate model,
never flattened into the 2.x dataclasses), a streaming API, atomic writes, real source
spans, a CRUD/builder API, diff/stats, a real interoperability oracle (OpenXLIFF via
Java — confirmed available: OpenJDK 21.0.11 and 17.0.19 both installed), real
property-based/fuzz/mutation test suites, one PO adapter pilot, ADRs, and a truthful
conformance manifest — then re-certifies and re-releases.

## Repository Authority

- **GitLab:** `https://gitlab.recruitize.ai/sialkot/cantt-smallize/libxliff`
- **Distribution:** `libxliff`
- **Namespace:** `libxliff`
- **Central document type:** `XliffDocument`

Authentication uses the `gitlab_token` environment variable via inline URL with `oauth2`
pseudo-username. Never print, log, commit, or embed the token in the remote URL. Leave `origin`
as the clean HTTPS URL. Never force push. Respect protected branches. Push every accepted
checkpoint. Do not publish externally without separate authorization.

## Known Donor Findings (closure checklist)

Every item below must be explicitly resolved before the `/goal` can end.
Items are tagged with the stage that addresses them.

| # | Finding | Addressed by |
|---|---------|-------------|
| F1 | `format-factory-core==0.1.0.dev0` hard dependency | TC-CORE-001 through TC-CORE-006 |
| F2 | Pre-release/Alpha version metadata (`0.2.0.dev0`) | TC-PKG-001 |
| F3 | Legacy XLIFF implementation (`src/python/xliff/*.py`) and its tests | TC-MIGRATE-003 (assess), not migrated |
| F4 | Oversized public facade (`__init__.py`, 219 lines, 80+ exports) | TC-API-001 |
| F5 | Oversized validator (`validation/validator.py`, 1,154 lines) | TC-VALID-001 |
| F6 | 8/8 standard XLIFF 2.1 modules preservation-only, 0/8 modeled | TC-MOD-* |
| F7 | `is_production_complete()` returns `False` | TC-MOD-* (closes when all 8 modeled) |
| F8 | Tiny synthetic corpus (4 files, all XLIFF 1.2 — wrong version) | TC-CORPUS-001 |
| F9 | Incorrect fixture metadata labeling 1.2 content as 2.x evidence | TC-VERSION-001 |
| F10 | Weak independent interoperability evidence | TC-CORPUS-002 |
| F11 | Undocumented CLI (36 lines, single command) | TC-CLI-001 |
| F12 | XML security weakness: declaration-prefix scanning | TC-SEC-001 |
| F13 | Lazy import of `reject_unsafe_xml` inside `_parse()` | TC-SEC-001-02 |
| F14 | Monorepo-only wrapper functions | TC-API-001-02 |
| F15 | `spec_qname` ClassVar (monorepo convention) | TC-API-002-03 |
| F16 | Resource Data module `namespace=None` despite known URI | TC-MOD-RD-001-01 |
| F17 | Diamond inheritance in error hierarchy via `FormatFactoryError` | TC-CORE-001 |

---

## Core Dependency Map (14 names, 8 import sites)

| File | Imports |
|------|---------|
| `errors.py` | `FormatFactoryError`, `FormatParseError`, `FormatValidationError`, `FormatWriteError` |
| `__init__.py` | `BinarySource` |
| `security/limits.py` | `DEFAULT_LIMITS`, `ResourceLimits` |
| `codec/reader/reader.py` (top) | `BinarySource`, `ProbeResult`, `ResourceLimits` |
| `codec/reader/reader.py` (lazy) | `reject_unsafe_xml` |
| `codec/writer/writer.py` | `ResourceLimits`, `TextDestination` |
| `validation/validator.py` | `BinarySource`, `Diagnostic`, `ResourceLimits`, `Severity`, `ValidationReport` |
| `validation/schema_validator.py` | `Diagnostic`, `SourceLocation`, `ValidationReport` |
| `qa.py` | `Diagnostic`, `Severity`, `ValidationReport` |

---

## Target Repository Structure

```
libxliff/
  pyproject.toml
  README.md
  CHANGELOG.md
  SECURITY.md
  CONTRIBUTING.md
  LICENSE                        # Apache-2.0
  THIRD_PARTY_NOTICES.md         # OASIS schema provenance/notices
  .gitignore
  .gitlab-ci.yml

  src/
    libxliff/
      __init__.py                # small facade, ~30 intentional exports
      py.typed
      errors.py                  # PUBLIC: XliffError hierarchy
      diagnostics.py             # PUBLIC: Diagnostic, DiagnosticSeverity,
                                 #         ValidationResult, SourceLocation

      model/
        __init__.py
        document.py              # XliffDocument, XliffFile, Group, Unit,
                                 #   Segment, Note, DataElement, ExtensionNode
        inline.py                # InlineElement, InlineNode, flatten
        segmentation.py          # split_segment, join_segments, SegmentMapping
        text_editing.py          # text_slots, replace_text_slots

      codec/
        __init__.py
        reader.py                # load, loads, probe
        writer.py                # dump, dumps
        preservation.py          # PreservationMode, LossReport, canonicalize

      validation/
        __init__.py              # validate, schema_validate, full_schema_validate
        core.py                  # validate() entry, structure/ID/language checks
        inline.py                # inline code pairing validation
        references.py            # data-ref, isolated codes, mrk comment-ref
        state.py                 # state constants, target-required states
        schema.py                # XSD-based validation (optional xmlschema)
        modules/                 # per-module validators (domain-rule enforcement)

      security/
        __init__.py
        limits.py                # PUBLIC: XliffResourceLimits, DEFAULT_RESOURCE_LIMITS
        xml.py                   # PUBLIC: secure XML parsing boundary

      modules/                   # typed XLIFF module domain models/parse/edit/write
        __init__.py
        metadata.py
        format_style.py
        glossary.py
        matches.py
        size_restriction.py
        validation_module.py
        resource_data.py
        its.py                   # possibly a sub-package if scope demands

      merge.py
      state_transitions.py
      qa.py
      analytics.py

      cli/
        __init__.py

      _internal/                 # PRIVATE: low-level helpers only
        __init__.py
        io.py                    # BinarySource, TextDestination type aliases
        probe.py                 # ProbeResult

  tests/
    unit/
    integration/
    interoperability/
    security/
    package/
    fixtures/
      valid/
      invalid/
      adversarial/

  docs/
  examples/
```

**NOTE:** This is the FINAL target structure after all normalization (Stage 5).
During Stages 2-3 (extraction/parity), the donor layout is preserved:
`codec/reader/reader.py`, `codec/writer/writer.py`, `analytics/__init__.py`,
`validation/schema_validator.py`. These are restructured in Stage 5.

### Key structural distinctions

- `modules/` = typed XLIFF domain models, parsing, querying, editing, serialization
- `validation/modules/` = validators that enforce domain rules against those models
- `_internal/` = truly private implementation helpers (I/O type aliases, probe result)
- `errors.py`, `diagnostics.py`, `security/limits.py`, `security/xml.py` are PUBLIC

---

## Public API Conventions

### Error hierarchy (public `errors.py`)

```python
class XliffError(Exception):
    message: str
    code: str       # stable XLIFF-prefixed code, e.g. "xliff.parse.namespace"
    context: dict

class XliffParseError(XliffError): ...
class XliffValidationError(XliffError): ...
class XliffWriteError(XliffError): ...
class XliffSecurityError(XliffError): ...
class XliffResourceLimitError(XliffError): ...
```

Self-rooted. No public `FormatFactoryError`. Single clean hierarchy.

### Diagnostic vocabulary (public `diagnostics.py`)

```python
class DiagnosticSeverity(StrEnum): ...   # INFO, WARNING, ERROR, FATAL
class SourceLocation: ...                # frozen dataclass
class Diagnostic: ...                    # code, message, severity, location, details
class ValidationResult: ...              # diagnostics tuple, is_valid, errors
```

During parity (Stages 2-3), the donor names `Severity`/`ValidationReport` may temporarily
exist. They converge to `DiagnosticSeverity`/`ValidationResult` during Stage 5.

### Resource limits (public `security/limits.py`)

```python
class XliffResourceLimits:               # frozen dataclass, XML-relevant fields only
    max_input_bytes: int
    max_output_bytes: int
    max_nesting_depth: int
    max_xml_nodes: int

DEFAULT_RESOURCE_LIMITS = XliffResourceLimits(...)  # values determined by TC-CORE-003-01 investigation
```

**NOTE:** Field set and default values are NOT pre-decided. They must be
justified by TC-CORE-003-01 investigation. The four fields above are candidates
from the donor — the investigation may add, remove, or adjust them.

---

## Taskcard State Machine

### Parent taskcard states

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS →
INTEGRATION_PENDING → VERIFIED → CLOSED
```

Lateral: any non-closed → BLOCKED / BLOCKED_EXTERNAL / DEFERRED_WITH_REASON

### Child taskcard states

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → CLOSED
```

Lateral: any non-closed → BLOCKED / REROUTED / DEFERRED_WITH_REASON

### Rules

- Parent closes ONLY when all mandatory children are CLOSED + integration checks pass
- Child closes ONLY when acceptance checks pass + evidence recorded
- TODO → CLOSED is forbidden (no skip-to-done)
- IMPLEMENTED → CLOSED is forbidden (must verify first)
- REROUTED → CLOSED requires rework evidence

---

# STAGE 1 — DONOR TRUTH CAPTURE

## TC-DONOR-001: Capture Complete Donor State

**Status:** TODO
**Type:** PARENT
**Objective:** Record exact donor state before any migration begins.
**Resolves findings:** Prerequisite for all subsequent work.
**Depends on:** Nothing.
**Gate:** All children CLOSED before Stage 2 begins.

### TC-DONOR-001-01: Pin donor commit

**Action:** Run `git rev-parse HEAD` in format-factory repo. Record SHA.
**Output:** Donor SHA string.
**Verification:** SHA exists and is valid.

### TC-DONOR-001-02: Generate source manifest

**Action:** List all files under `src/python/xliff/src/format_factory/xliff/`
with line counts (`wc -l` or equivalent).
**Output:** Table of 25 files with exact line counts.
**Verification:** Count matches 25 files.

### TC-DONOR-001-03: Record public API manifest

**Action:** Extract `__all__` from donor `__init__.py`. Record every exported name.
**Output:** List of ~80 exported names from donor `__all__`.
**Verification:** Matches line 102-184 of donor `__init__.py`.

### TC-DONOR-001-04: Run test baseline

**Action:** Run `pytest tests/python/xliff/ --tb=short` in format-factory venv.
Record pass/fail/skip counts per file.
**Output:** Test result summary with per-file breakdown.
**Verification:** Results recorded and non-empty.

### TC-DONOR-001-05: Document schema asset provenance

**Action:** List all 20 schema files in `validation/schemas/`. For each,
record filename, size, and whether it traces to an OASIS distribution.
Check `shared/sal-facts/evidence/xliff.yaml` for SHA-256 pinned sources.
**Output:** Schema provenance table.
**Verification:** All 20 files accounted for.

### TC-DONOR-001-06: Record module coverage state

**Action:** Read `modules.py`. Record each module's name, namespace, coverage
status, and `namespace_confirmed` flag.
**Output:** 8-row table matching `STANDARD_MODULES` tuple.
**Verification:** All 8 modules show `PRESERVATION_ONLY`.

### TC-DONOR-001-07: Document core imports map

**Action:** Already documented above (14 names, 8 sites). Verify current accuracy
by grepping `from format_factory.core` in donor source.
**Output:** Confirmed import map.
**Verification:** `grep` output matches the table in this plan.

### TC-DONOR-001-08: Document legacy/shadow paths

**Action:** List all files under `src/python/xliff/` that are NOT under
`src/format_factory/xliff/`. These are the legacy flat-module files.
Record which have overlap with production code.
**Output:** List of ~10 legacy files with overlap assessment.

### TC-DONOR-001-09: Document corpus and security findings

**Action:** List all sample files in `samples/by-format/xliff/`. Record version
(1.2 vs 2.x) for each. Record the known security finding: `reject_unsafe_xml`
is imported lazily at reader.py line 299, and the underlying approach is
byte-level regex scanning after encoding normalization.
**Output:** Corpus inventory + security finding record.

**Stage 1 commit:** `chore(repo): capture donor truth at commit {sha}`

---

# STAGE 2 — MECHANICAL EXTRACTION

## TC-REPO-001: Initialize libxliff Repository

**Status:** TODO
**Type:** PARENT
**Objective:** Create the standalone repo with proper layout.
**Depends on:** TC-DONOR-001 CLOSED.

### TC-REPO-001-01: Clone GitLab repository

**Action:** `git clone https://gitlab.recruitize.ai/sialkot/cantt-smallize/libxliff`
using `gitlab_token` via inline URL with `oauth2` pseudo-username. If repo is empty, that's expected.
**Verification:** Local clone exists with `.git/`.
**Failure handling:** If clone fails due to demonstrated network/auth failure,
`git init libxliff` locally, configure remote, and record the blocker as
`EXTERNAL_BLOCKER: gitlab_clone_failed_[reason]`. Local-only is a fallback
for demonstrated failure, NOT an alternative execution mode.
**GitLab push rule:** Push every accepted checkpoint commit. Never close the
product goal with unpublished local commits unless GitLab is genuinely
externally unavailable and the blocker is explicitly recorded.

### TC-REPO-001-02: Create directory structure

**Action:** Create all directories per target structure above. Create empty
`__init__.py` files where needed.
**Allowed files:** All directories/files in the target structure.
**Verification:** `find src/libxliff -name "*.py" | wc -l` shows expected count.

### TC-REPO-001-03: Create pyproject.toml

**Action:** Write `pyproject.toml` with:
- `name = "libxliff"`, `version = "0.1.0.dev0"`
- `requires-python = ">=3.11"`
- `license = "Apache-2.0"`
- Zero runtime dependencies initially (TC-SEC-001-01 may justify adding a
  security dependency like `defusedxml` — update pyproject.toml at that point)
- Optional: `schema = ["xmlschema>=4.1"]`, `test = ["pytest>=8.3", "hypothesis>=6.100"]`
- Entry point: `libxliff = "libxliff.cli:main"`
- Package data: `py.typed`, `validation/schemas/*.xsd`, `*.sch`, `*.nvdl`
- Ruff: `target-version = "py311"`, `line-length = 100`
- Mypy: `strict = true`
**Verification:** `pip install -e .` succeeds, `python -c "import libxliff"` works.

### TC-REPO-001-04: Create metadata files

**Action:** Create README.md, LICENSE (Apache-2.0), CHANGELOG.md, SECURITY.md,
CONTRIBUTING.md, .gitignore. Minimal stubs — expanded in Stage 14.
**Verification:** All files exist and are non-empty.

**Commit:** `chore(repo): initialize libxliff standalone repo layout`

---

## TC-MIGRATE-001: Copy Production Source

**Status:** TODO
**Type:** PARENT
**Objective:** Copy all 25 production source files with namespace adaptation.
**Depends on:** TC-REPO-001 CLOSED.
**Critical rule:** DO NOT remove any existing public behavior during this stage.

### TC-MIGRATE-001-01: Copy model files

**Action:** Copy from donor `model/` to `src/libxliff/model/`:
- `document.py`, `inline.py`, `segmentation.py`, `text_editing.py`, `__init__.py`
Translate: `from format_factory.xliff.` → relative imports.
Leave `from format_factory.core` imports as-is (compatibility shim handles them).
**Files:** 5 files.

### TC-MIGRATE-001-02: Copy codec files (preserve donor layout)

**Action:** Preserve the donor directory structure exactly:
Copy donor `codec/reader/reader.py` → `src/libxliff/codec/reader/reader.py`.
Copy donor `codec/reader/__init__.py` → `src/libxliff/codec/reader/__init__.py`.
Copy donor `codec/writer/writer.py` → `src/libxliff/codec/writer/writer.py`.
Copy donor `codec/writer/__init__.py` → `src/libxliff/codec/writer/__init__.py`.
Copy donor `codec/preservation.py` → `src/libxliff/codec/preservation.py`.
Copy donor `codec/__init__.py` → `src/libxliff/codec/__init__.py`.
Translate internal imports only (format_factory.xliff → relative).
**Files:** 6 files.
**PARITY RULE:** Do NOT flatten `codec/reader/` and `codec/writer/` here.
Flattening is deferred to TC-CODEC-001 in Stage 5 after parity is proven.

### TC-MIGRATE-001-03: Copy validation files (preserve donor names)

**Action:** Copy donor `validation/validator.py`, `validation/schema_validator.py`,
`validation/__init__.py` to corresponding locations under `src/libxliff/validation/`.
**PARITY RULE:** Do NOT rename `schema_validator.py` → `schema.py` here.
Renaming is deferred to Stage 5 after parity is proven.
Translate internal imports only.
**Files:** 3 files.

### TC-MIGRATE-001-04: Copy security files

**Action:** Copy donor `security/__init__.py` and `security/limits.py`.
**Files:** 2 files.

### TC-MIGRATE-001-05: Copy top-level modules (preserve donor layout)

**Action:** Copy donor `errors.py`, `modules.py`, `merge.py`,
`state_transitions.py`, `qa.py` to `src/libxliff/`.
Copy donor `analytics/__init__.py` → `src/libxliff/analytics/__init__.py`
(preserve as package, not flattened to module).
**PARITY RULE:** Do NOT flatten `analytics/` here. Flattening is deferred
to Stage 5 after parity is proven.
**Files:** 6 files.

### TC-MIGRATE-001-06: Copy cli

**Action:** Copy donor `cli/__init__.py` to `src/libxliff/cli/__init__.py`.
**Files:** 1 file.

### TC-MIGRATE-001-07: Copy root __init__.py (PRESERVE ALL EXPORTS)

**Action:** Copy donor `__init__.py` to `src/libxliff/__init__.py`.
Translate `from format_factory.xliff.` → relative imports.
**PRESERVE:** All aliases (`probe_xliff`, `load_xliff`, `write_xliff`),
all helper functions (`iter_file_units`, `get_file_count`, `get_unit_count`,
`roundtrip`, `xliff_installed_workflow`), the full `__all__` list.
These are removed ONLY in Stage 5 after parity proves what's actually used.
**Files:** 1 file.

### TC-MIGRATE-001-08: Create local migration bridge (NO donor dependency)

**Action:** Create `src/libxliff/_migration_bridge.py` containing LOCAL copies
of the exact 14 donor-core behaviors needed for parity. This file is a
self-contained temporary bridge — it does NOT import from `format_factory.core`.
Contents (copied from donor core source, adapted minimally):
- Error base classes: `FormatFactoryError`, `FormatParseError`,
  `FormatValidationError`, `FormatWriteError`, `ResourceLimitError`
- Diagnostics: `Severity(StrEnum)`, `SourceLocation`, `Diagnostic`,
  `ValidationReport`
- Limits: `ResourceLimits`, `DEFAULT_LIMITS`
- I/O types: `BinarySource` TypeAlias, `TextDestination` TypeAlias
- Probe: `ProbeResult` frozen dataclass
- XML security: `reject_unsafe_xml`, `safe_fromstring` (and helpers)

All production files that import `from format_factory.core import X` get
rewritten to `from libxliff._migration_bridge import X`.
**CRITICAL:** This bridge must NOT require `format-factory-core` to be installed.
It preserves behavioral compatibility by containing the exact donor behaviors
locally, not by importing them.
**Verification:** `pip install -e .[test]` succeeds WITHOUT `format-factory-core`.
All 14 names resolve from the local bridge.

### TC-MIGRATE-001-09: Translate all import paths

**Action:** Global search-replace across all copied source files:
- `from format_factory.xliff.` → relative imports (`.model.`, `.codec.`, etc.)
- `from format_factory.core import` → `from libxliff._migration_bridge import`
- `import format_factory.xliff` → `import libxliff`
**Verification:** `grep -r "format_factory.xliff" src/` returns zero hits.
`grep -r "format_factory.core" src/` returns zero hits (all routed through `_migration_bridge`).

**Commit:** `feat(migration): copy production source with namespace adaptation`

---

## TC-MIGRATE-002: Copy Schemas and Fixtures

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-REPO-001 CLOSED.

### TC-MIGRATE-002-01: Copy schema files

**Action:** Copy all 20 XSD/SCH/NVDL files from donor
`validation/schemas/` to `src/libxliff/validation/schemas/`.
**Verification:** `ls src/libxliff/validation/schemas/ | wc -l` = 20.

### TC-MIGRATE-002-02: Copy sample fixtures

**Action:** Copy all 4 sample files from `samples/by-format/xliff/` to
`tests/fixtures/`. Place valid/*.xliff under `tests/fixtures/valid/` for now
(they will be reclassified in Stage 5 since they are actually XLIFF 1.2).
Place `invalid/missing-namespace.xliff` under `tests/fixtures/invalid/`.
**Verification:** All 4 files present in `tests/fixtures/`.

### TC-MIGRATE-002-03: Create THIRD_PARTY_NOTICES.md

**Action:** Document OASIS schema provenance using data from TC-DONOR-001-05.
Record license terms for each schema file.
**Verification:** File exists and references all 20 schema files.

**Commit:** `feat(migration): copy schemas, fixtures, and provenance notices`

---

## TC-MIGRATE-003: Copy and Assess Tests

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-MIGRATE-001 CLOSED.

### TC-MIGRATE-003-01: Assess 7 legacy tests

**Action:** Read each of the 7 legacy `xliff.*` test files. For each, determine:
(a) Does it test behavior that the production namespace also covers? → skip.
(b) Does it test behavior NOT covered by production tests? → port the test
    to use `libxliff` imports.
(c) Is it testing obsolete implementation details? → discard with reason.
Record the decision for each file.
**Output:** Assessment table with file, decision, reason.

### TC-MIGRATE-003-02: Copy 46 production-API test files

**Action:** Copy all test files that import from `format_factory.xliff` to
`tests/unit/`. Translate imports: `from format_factory.xliff` → `from libxliff`,
`from format_factory.core` → `from libxliff._migration_bridge`.
**Files:** 46 files.
**Note:** Tests remain in flat structure during parity. Reorganization into
`unit/integration/security/` happens in Stage 5.

### TC-MIGRATE-003-03: Port useful legacy test behavior

**Action:** For each legacy test marked "port" in TC-MIGRATE-003-01, rewrite
the test to use `libxliff` imports and add to `tests/unit/`.
**Depends on:** TC-MIGRATE-003-01 CLOSED.

**Commit:** `feat(migration): copy tests and fixtures with import translation`

---

# STAGE 3 — EXTRACTION PARITY

## TC-PARITY-001: Prove Extraction Parity (GATE 1 of 2)

**Status:** TODO
**Type:** PARENT
**Objective:** All donor tests pass in standalone libxliff using the local
migration bridge — WITHOUT requiring `format-factory-core` to be installed.
**Depends on:** TC-MIGRATE-001, TC-MIGRATE-002, TC-MIGRATE-003 all CLOSED.
**Gate:** This MUST pass before ANY Stage 4+ work begins.

### TC-PARITY-001-01: Install and run tests (donor-free)

**Action:**
1. `pip install -e .[test]` — do NOT install `format-factory-core`
2. `pytest tests/ -v --tb=short`
3. Compare pass/fail/skip counts with TC-DONOR-001-04 baseline.
**Expected:** Same pass/fail profile as donor.
**CRITICAL:** The migration bridge must provide all needed behaviors locally.
If any test fails because `format_factory.core` is missing, that is a bridge
defect — fix the bridge, do not install the donor package.

### TC-PARITY-001-02: Fix parity regressions

**Action:** For each test that fails in libxliff but passed in donor:
diagnose the import/path issue, fix it, re-run. Do NOT change test logic
or implementation behavior — only fix namespace/import issues.
**Depends on:** TC-PARITY-001-01 shows failures.

### TC-PARITY-001-03: Verify core imports work

**Action:** `python -c "from libxliff import XliffDocument, load, validate, probe"`
must succeed. Verify the migration bridge resolves all 14 core names locally.
**Verification:** Exit code 0 with `format-factory-core` NOT installed.

### TC-PARITY-001-04: Record extraction parity evidence

**Action:** Save full pytest output. Record: total tests, passed, failed, skipped.
Compare with donor baseline side-by-side.
**Output:** Extraction parity evidence document.
**Evidence must prove:** standalone location + local migration bridge = donor behavior.

**Commit:** `test(parity): extraction parity — all donor tests pass standalone`
**Push to GitLab after this commit.**

---

# STAGE 4 — ELIMINATE MIGRATION BRIDGE (final XLIFF-owned replacements)

## TC-CORE-001: Implement XLIFF-Specific Errors

**Status:** TODO
**Type:** PARENT
**Objective:** Replace `FormatFactoryError` with self-rooted `XliffError`.
**Resolves findings:** F1, F17.
**Depends on:** TC-PARITY-001 CLOSED.

### TC-CORE-001-01: Create public errors.py

**Action:** Write `src/libxliff/errors.py` with:
```python
class XliffError(Exception):
    code = "xliff_error"
    def __init__(self, message, *, code=None, context=None): ...

class XliffParseError(XliffError): code = "xliff.parse"
class XliffValidationError(XliffError): code = "xliff.validation"
class XliffWriteError(XliffError): code = "xliff.write"
class XliffSecurityError(XliffError): code = "xliff.security"
class XliffResourceLimitError(XliffError): code = "xliff.resource_limit"
class SchemaValidationUnavailable(XliffError): code = "xliff.schema_unavailable"
```
Preserve `message`, `code`, `context` interface from donor.
**File:** `src/libxliff/errors.py`
**Verification:** All error classes instantiate correctly.

### TC-CORE-001-02: Test error hierarchy

**Action:** Add `tests/unit/test_errors.py`: verify MRO, `isinstance` chains,
`code`/`context`/`message` attributes, `str()` output.
**Verification:** Tests pass.

---

## TC-CORE-002: Implement Diagnostics

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-PARITY-001 CLOSED.

### TC-CORE-002-01: Create public diagnostics.py

**Action:** Write `src/libxliff/diagnostics.py` with:
- `DiagnosticSeverity(StrEnum)` — INFO, WARNING, ERROR, FATAL
- `SourceLocation` — frozen dataclass (byte_offset, line, column, path)
- `Diagnostic` — frozen dataclass (code, message, severity, location, details)
- `ValidationResult` — frozen dataclass wrapping diagnostics tuple, `is_valid`, `errors`, `extend()`
- Temporary aliases: `Severity = DiagnosticSeverity`, `ValidationReport = ValidationResult`
  (removed in Stage 5)
**File:** `src/libxliff/diagnostics.py`
**Verification:** All classes instantiate. `ValidationResult([]).is_valid` is `True`.

### TC-CORE-002-02: Test diagnostics

**Action:** Add `tests/unit/test_diagnostics.py`: severity ordering, location validation,
diagnostic construction, report `is_valid` logic, `extend()` immutability.
**Verification:** Tests pass.

---

## TC-CORE-003: Implement Resource Limits

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-CORE-001 CLOSED (needs `XliffResourceLimitError`).

### TC-CORE-003-01: Investigate and create security/limits.py

**Action:** BEFORE implementing, investigate appropriate limits:
- Realistic CAT/localization file sizes (typical and large)
- Multi-file XLIFF package sizes
- Large module-heavy documents (ITS, Resource Data with embedded content)
- Limits enforced by the XML parser selected in TC-SEC-001-01
- Memory amplification from the object model (bytes on disk → memory)
- Malicious workload thresholds (what input sizes enable DoS?)
- Donor `ResourceLimits` values as parity candidates (verify they reflect
  actual donor behavior, not arbitrary numbers)

Based on investigation, write `src/libxliff/security/limits.py` with:
- `XliffResourceLimits` — frozen dataclass with justified XML-relevant fields
- `with_overrides(**values)` method
- `enforce(name, actual)` method raising `XliffResourceLimitError`
- `DEFAULT_RESOURCE_LIMITS` singleton with evidence-backed defaults
- `effective_limits(limits: XliffResourceLimits | None)` helper
- Temporary aliases: `ResourceLimits = XliffResourceLimits`,
  `DEFAULT_LIMITS = DEFAULT_RESOURCE_LIMITS` (removed in Stage 5)
**Output:** Limits justification record (why each field, why each default).
**File:** `src/libxliff/security/limits.py`

### TC-CORE-003-02: Test limits

**Action:** Add `tests/unit/test_resource_limits.py`: construction, enforcement,
overrides, validation errors for bad values.
**Verification:** Tests pass.

---

## TC-CORE-004: Implement XML Security Module

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-CORE-001, TC-CORE-003 CLOSED.

### TC-CORE-004-01: Create security/xml.py (bridge replacement)

**Action:** Write `src/libxliff/security/xml.py` as the final XLIFF-owned
replacement for the bridge's XML security functions. At this stage, preserve
the SAME security approach as the migration bridge (encoding normalization +
full-payload scanning + post-parse tree limits). The parser-level hardening
in TC-SEC-001 (Stage 5) will upgrade this to use parser-level protection.
Contents:
- `PERMITTED_ENCODINGS` frozenset
- `_detect_encoding(data)` — BOM-based detection
- `_normalize_to_utf8(data)` — proper codec transcode (not null-byte stripping)
- `reject_unsafe_xml(data, *, error_class)` — full-payload scan after transcode
- `safe_fromstring(data, *, limits, error_class)` — full pipeline
**File:** `src/libxliff/security/xml.py`
**Note:** Uses `XliffSecurityError` as default error class (not `FormatParseError`).
**Note:** This is a behavioral-parity replacement of the bridge, NOT the final
security architecture. TC-SEC-001 upgrades this to parser-level protection.

### TC-CORE-004-02: Update security/__init__.py

**Action:** Re-export `DEFAULT_RESOURCE_LIMITS`, `XliffResourceLimits`,
`effective_limits`, `reject_unsafe_xml`, `safe_fromstring`, `PERMITTED_ENCODINGS`.

---

## TC-CORE-005: Implement I/O Protocols

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-PARITY-001 CLOSED.

### TC-CORE-005-01: Create _internal/io.py

**Action:** Write type aliases:
```python
BinarySource: TypeAlias = str | PathLike[str] | bytes | bytearray | memoryview | BinaryIO
TextDestination: TypeAlias = str | PathLike[str] | TextIO
```
**File:** `src/libxliff/_internal/io.py`

### TC-CORE-005-02: Create _internal/probe.py

**Action:** Copy `ProbeResult` frozen dataclass from donor core.
**File:** `src/libxliff/_internal/probe.py`

---

## TC-CORE-006: Rewire All Imports and Remove Migration Bridge

**Status:** TODO
**Type:** PARENT
**Objective:** Replace `_migration_bridge` with final XLIFF-owned implementations.
**Depends on:** TC-CORE-001 through TC-CORE-005 all CLOSED.
**Gate:** Zero `format_factory` AND zero `_migration_bridge` references after this.

### TC-CORE-006-01: Update production source imports

**Action:** Replace every `from libxliff._migration_bridge import X` with the
correct final import:
- Error bases → `from libxliff.errors import ...`
- Diagnostics → `from libxliff.diagnostics import ...`
- Limits → `from libxliff.security.limits import ...`
- XML security → `from libxliff.security.xml import ...`
- I/O types → `from libxliff._internal.io import ...`
- ProbeResult → `from libxliff._internal.probe import ...`
**Files:** 8 production source files.

### TC-CORE-006-02: Update test imports

**Action:** Replace `from libxliff._migration_bridge import` in test files.
3 test files have direct bridge imports.
**Files:** 3 test files.

### TC-CORE-006-03: Delete migration bridge

**Action:** Remove `src/libxliff/_migration_bridge.py`.
**Verification:** File no longer exists.

### TC-CORE-006-04: Verify zero format_factory and zero bridge references

**Action:** `grep -r "format_factory" src/ tests/` — must return zero hits.
`grep -r "_migration_bridge" src/ tests/` — must return zero hits.
**Verification:** Both greps empty.

### TC-CORE-006-05: Prove independence parity (GATE 2 of 2)

**Action:** `pip install -e .[test]` (without `format-factory-core`).
`pytest tests/ -v --tb=short`.
Compare results with TC-PARITY-001-04 extraction parity evidence.
**Verification:** All tests pass. Same pass/fail profile as extraction parity.
**Evidence must prove:** same behavior after bridge removal + final XLIFF-owned replacements.
**Output:** Independence parity evidence document.

**Commits:**
- `refactor(core): implement XLIFF-specific error/diagnostic/limits/security`
- `refactor(core): remove migration bridge, prove independence parity`

**Push to GitLab after these commits.**

---

# STAGE 5 — ARCHITECTURE/API NORMALIZATION

## TC-SEC-001: XML Security Hardening

**Status:** TODO
**Type:** PARENT
**Objective:** Parser-level secure boundary. String scanning alone is NOT
acceptable as the DTD/entity protection mechanism.
**Resolves findings:** F12, F13.
**Depends on:** TC-CORE-006 CLOSED.

### TC-SEC-001-01: Investigate XML parser options

**Action:** Investigate available standard-library and third-party XML parsers
that can enforce security constraints BEFORE or DURING parsing (not after):
- DTD disabled at parser level
- Entity expansion disabled at parser level
- External entity/network resolution disabled at parser level
- Safe encoding handling
- Resource limits enforceable as early as technically possible

Candidates to evaluate:
- `xml.etree.ElementTree` (stdlib) — what security guarantees does Python 3.11+
  provide? Can DTD processing be disabled at the parser level?
- `defusedxml` — mature third-party, specifically designed for safe XML parsing
- `lxml` with `XMLParser(resolve_entities=False, no_network=True, dtd_validation=False)`

Evaluate each on: security guarantees, XLIFF fidelity (namespace handling,
preservation requirements), dependency maintenance status, performance.

**Output:** Parser selection decision record with justification.
**RULE:** A mature, maintained XML security dependency IS acceptable if it
materially improves security. "Zero runtime dependencies" does NOT override
security correctness.

### TC-SEC-001-02: Implement parser-level secure boundary

**Action:** Based on TC-SEC-001-01 decision, implement `security/xml.py`:
- The selected parser/configuration must enforce DTD/entity/external-entity
  rejection at the PARSER LEVEL, not via string scanning
- `reject_unsafe_xml` is a top-level import in reader (not lazy — fixes F13)
- `safe_fromstring` or equivalent is the single parse entry point
- `XliffSecurityError` raised for all security violations
- Encoding normalization retained for multi-byte support
- Tree/resource limits enforced as early as technically possible
- If a third-party parser is selected, add it to `pyproject.toml` dependencies
**Files:** `src/libxliff/security/xml.py`, `src/libxliff/codec/reader.py`

### TC-SEC-001-03: Define encoding policy

**Action:** Document which XML encodings are accepted and which are rejected.
The `PERMITTED_ENCODINGS` frozenset already exists. Verify it matches the
actual XML/XLIFF requirements (UTF-8, UTF-16, UTF-32, ISO-8859-1, ASCII).
**Output:** Encoding policy in SECURITY.md.

### TC-SEC-001-04: Create adversarial security test suite

**Action:** Create `tests/security/` with adversarial test files:
- `test_encoding.py` — UTF-8, UTF-16LE/BE, UTF-32, BOM/no-BOM valid documents
- `test_doctype.py` — DOCTYPE at start, after large comment, mid-document
- `test_entity.py` — internal entity, external entity (file:// / http://),
  exponential expansion (Billion Laughs)
- `test_resource_limits.py` — input bytes, node count, nesting depth, text bytes,
  huge attributes
- `test_null_byte.py` — null-byte interleaving bypass attempts
- `test_deep_structure.py` — deeply nested elements exceeding depth limits
**Fixtures:** Create `tests/fixtures/adversarial/` with crafted payloads.
**Verification:** All security tests pass. All attack payloads are rejected.
Tests must prove that protection comes from the parser configuration, not
from pre-parse string scanning.

**Commit:** `fix(security): parser-level XML security with adversarial test suite`

---

## TC-VALID-001: Validator Decomposition

**Status:** TODO
**Type:** PARENT
**Objective:** Split 1,154-line validator.py into cohesive modules.
**Resolves findings:** F5.
**Depends on:** TC-CORE-006 CLOSED.

### TC-VALID-001-01: Extract validation/core.py

**Action:** Move `validate()` entry point and document/file/unit/segment
structure checks, ID uniqueness, language compatibility into `validation/core.py`.
**Verification:** `from libxliff.validation import validate` still works.

### TC-VALID-001-02: Extract validation/inline.py

**Action:** Move `_validate_inline()`, `_inline_elements()` into `validation/inline.py`.

### TC-VALID-001-03: Extract validation/references.py

**Action:** Move isolated-code pairing, data-ref, mrk comment-ref checks into
`validation/references.py`.

### TC-VALID-001-04: Extract validation/state.py

**Action:** Move state constants (`_STATES`, `_TARGET_REQUIRED_STATES`) and
helpers into `validation/state.py`.

### TC-VALID-001-05: Extract per-module validators

**Action:** Move each module's validation logic into `validation/modules/{name}.py`.
Create `validation/modules/__init__.py` that aggregates them.
8 files: metadata.py, format_style.py, glossary.py, matches.py,
size_restriction.py, validation.py, resource_data.py, its.py (stubs
that will be expanded in Stage 8).

### TC-VALID-001-06: Verify all validation tests pass

**Action:** `pytest tests/ -k "valid" -v`. All existing validation tests must pass.
**Verification:** Zero regressions.

**Commits:** `refactor(validation): decompose validator into core/inline/references/state/modules`

---

## TC-CODEC-001: Flatten Codec Structure

**Status:** TODO
**Type:** PARENT (of Stage 5 normalization)
**Depends on:** TC-CORE-006 CLOSED.

**Action:** NOW flatten the codec layout (deferred from Stage 2 per parity rule):
- `codec/reader/reader.py` → `codec/reader.py`
- `codec/writer/writer.py` → `codec/writer.py`
- Remove intermediate `codec/reader/__init__.py` and `codec/writer/__init__.py`
- Update `codec/__init__.py` to re-export from flat locations
- Update all internal imports referencing the old nested paths
**Verification:** No `codec/reader/` or `codec/writer/` subdirectories exist.
All tests pass after flattening.

## TC-RENAME-001: Rename schema_validator and Flatten Analytics

**Status:** TODO
**Type:** CHILD (of Stage 5 normalization)
**Depends on:** TC-CORE-006 CLOSED.

**Action:** NOW apply structural cleanup deferred from Stage 2:
- Rename `validation/schema_validator.py` → `validation/schema.py`
- Update `validation/__init__.py` imports accordingly
- Flatten `analytics/__init__.py` → `analytics.py` (single module)
- Update all internal imports
**Verification:** All tests pass after restructuring.

---

## TC-API-001: Narrow Root Facade

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F4, F14.
**Depends on:** TC-PARITY-001, TC-VALID-001 CLOSED.

### TC-API-001-01: Classify all donor exports by semantic role

**Action:** For each name in the current `__all__` (80+ names), classify by
semantic role using ALL available evidence (source role, documentation,
existing examples, tests, product semantics — not test grep alone):

- **central_public** — core user-facing API (load, dump, XliffDocument, etc.)
- **useful_advanced** — useful capability to expose via submodule import
  (e.g., `from libxliff.merge import ...`)
- **obsolete_alias** — donor-framework alias with no standalone value
  (probe_xliff, load_xliff, write_xliff)
- **monorepo_hook** — monorepo integration function with no standalone value
  (xliff_installed_workflow)
- **implementation_detail** — internal helper leaked to public surface
- **compatibility_candidate** — potentially useful for users migrating
  from donor; document deprecation path if removed

**Output:** Full classification table with role + justification per name.
**RULE:** Do NOT remove useful capabilities merely because no current test
imports them. Removal decisions must be based on semantic role analysis.

### TC-API-001-02: Remove exports classified as removable

**Action:** Remove from `__init__.py` ONLY exports classified as
`obsolete_alias`, `monorepo_hook`, or `implementation_detail`:
- `probe_xliff = probe` alias (obsolete_alias)
- `load_xliff = load` alias (obsolete_alias)
- `write_xliff = dumps` alias (obsolete_alias)
- `xliff_installed_workflow()` (monorepo_hook)
- Others classified as removable in TC-API-001-01
For `compatibility_candidate` items: decide retain-with-deprecation or remove.
For `useful_advanced` items: move to submodule access, not root `__all__`.
Update `__all__`. Fix tests that imported removed names.
**Depends on:** TC-API-001-01 CLOSED.

### TC-API-001-03: Reduce to ~30 intentional exports

**Action:** Organize `__init__.py` to export only the public API:
- Document types: `XliffDocument`, `XliffFile`, `Group`, `Unit`, `Segment`, `Note`
- Inline: `InlineElement`, `InlineNode`
- Codec: `load`, `loads`, `dump`, `dumps`, `probe`
- Validation: `validate`, `schema_validate`
- Errors: `XliffError`, `XliffParseError`, `XliffValidationError`, `XliffWriteError`
- Preservation: `PreservationMode`
- Constants: `SUPPORTED_VERSIONS`, `XLIFF_NAMESPACE`
- Advanced types available via `libxliff.modules`, `libxliff.merge`, etc.

**Commit:** `refactor(api): narrow root facade to ~30 intentional exports`

---

## TC-API-002: Converge Naming

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-CORE-002 CLOSED, TC-API-001 CLOSED.

### TC-API-002-01: Severity → DiagnosticSeverity

**Action:** Remove the `Severity = DiagnosticSeverity` alias from diagnostics.py.
Update all internal usage sites to use `DiagnosticSeverity`.
**Verification:** `grep -r "Severity" src/ | grep -v DiagnosticSeverity` returns zero.

### TC-API-002-02: ValidationReport → ValidationResult

**Action:** Remove the `ValidationReport = ValidationResult` alias.
Update all internal usage sites.
**Verification:** `grep -r "ValidationReport" src/` returns zero.

### TC-API-002-03: Remove spec_qname ClassVar

**Action:** Remove `spec_qname: ClassVar[str]` from model classes if present.
**Verification:** `grep -r "spec_qname" src/` returns zero.

### TC-API-002-04: Remove ResourceLimits/DEFAULT_LIMITS aliases

**Action:** Remove temporary aliases. Update all usage to
`XliffResourceLimits`/`DEFAULT_RESOURCE_LIMITS`.
**Verification:** `grep -r "ResourceLimits" src/ | grep -v XliffResourceLimits` returns zero.

**Commit:** `refactor(api): converge to final naming (DiagnosticSeverity, ValidationResult, XliffResourceLimits)`

---

## TC-API-003: Document-Centric API

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-API-001, TC-API-002 CLOSED.

### TC-API-003-01: Verify load/save/validate pattern

**Action:** Ensure `XliffDocument` supports:
```python
doc = XliffDocument.load("messages.xlf")  # or load() module function
result = doc.validate()                    # returns ValidationResult
doc.save("updated.xlf")                    # or dump() module function
```
If `XliffDocument` lacks `.load()` and `.save()` class/instance methods,
add them as thin wrappers around `load()` and `dump()`.
**Verification:** The three-line example works.

### TC-API-003-02: Add options classes only where warranted

**Action:** Review `load()`, `dump()`, `validate()` parameter surfaces.
Create `XliffLoadOptions`, `XliffSaveOptions`, `XliffValidationOptions`,
`XliffMergeOptions` ONLY if they have >2 meaningful configuration fields.
Do not create empty option objects.
**Output:** Decision record per options class.

**Commit:** `feat(api): document-centric XliffDocument.load/validate/save API`

---

## TC-VERSION-001: Explicit Support Matrix

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F8, F9.
**Depends on:** TC-CORE-006 CLOSED.

### TC-VERSION-001-01: Verify SUPPORTED_VERSIONS

**Action:** Read `codec/reader.py`. Confirm
`SUPPORTED_VERSIONS = frozenset({"2.0", "2.1"})`.
**Verification:** Constant exists and is correct.

### TC-VERSION-001-02: Create XLIFF 2.0 test fixtures

**Action:** Create `tests/fixtures/valid/minimal-2.0.xliff` — minimal valid
XLIFF 2.0 document with `urn:oasis:names:tc:xliff:document:2.0` namespace,
one file, one unit, one segment.
**Verification:** `load()` parses it successfully.

### TC-VERSION-001-03: Create XLIFF 2.1 test fixtures

**Action:** Create `tests/fixtures/valid/minimal-2.1.xliff` — minimal valid
XLIFF 2.1 document. Also create `tests/fixtures/valid/with-modules-2.1.xliff`
containing at least one standard module extension.
**Verification:** `load()` parses both successfully.

### TC-VERSION-001-04: Reclassify 1.2 fixtures

**Action:** Move existing XLIFF 1.2 fixtures from `tests/fixtures/valid/` to
`tests/fixtures/invalid/unsupported-version/`. Add a test that verifies
`load()` raises `XliffParseError` for XLIFF 1.2 input.
**Verification:** Test passes.

### TC-VERSION-001-05: Document version support (capability-based)

**Action:** Add version support section to README.md with a capability-based
matrix. Do NOT claim "fully supported" for any version until the
corresponding module and interoperability gates genuinely pass.
Example during development:
```
XLIFF 2.0 core: supported
XLIFF 2.1 core: supported
Metadata module: [status]
Glossary module: [status]
Format Style module: [status]
Translation Candidates module: [status]
Size/Length Restriction module: [status]
Validation module: [status]
Resource Data module: [status]
ITS module: [status]
```
Say "fully supported" ONLY when all module capability gates for that
version genuinely pass (TC-GATE-001 criterion).
- XLIFF 1.2: not supported (raises `XliffParseError`)

**Commit:** `feat(version): explicit 2.0/2.1 support matrix with correct fixtures`

---

## TC-TEST-REORG-001: Reorganize Test Structure

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-SEC-001, TC-VALID-001 CLOSED.

### TC-TEST-REORG-001-01: Categorize existing tests

**Action:** For each test file in `tests/unit/`, classify as:
- `unit` — single-component tests
- `integration` — multi-component workflow tests
- `security` — already in `tests/security/` from TC-SEC-001
Move files to appropriate subdirectories.

### TC-TEST-REORG-001-02: Create conftest.py files

**Action:** Create `tests/conftest.py` with shared fixtures (fixture paths, etc.).
Create per-directory conftest if needed.

### TC-TEST-REORG-001-03: Verify all tests still pass

**Action:** `pytest tests/ -v`. Zero regressions from reorganization.

**Commit:** `refactor(tests): reorganize into unit/integration/security/package taxonomy`

---

## TC-WHEEL-001: Early Installed-Wheel Smoke (before module expansion)

**Status:** TODO
**Type:** PARENT
**Objective:** Catch monorepo assumptions before 8 module implementations build on them.
**Depends on:** TC-API-003, TC-SEC-001, TC-VALID-001, TC-TEST-REORG-001 all CLOSED.

### TC-WHEEL-001-01: Build and install wheel

**Action:**
1. `python -m build --wheel`
2. Create clean venv (no format-factory, no source checkout on PYTHONPATH)
3. `pip install dist/libxliff-*.whl`
**Verification:** Install succeeds.

### TC-WHEEL-001-02: Smoke test installed package

**Action:** In the clean venv (NOT from the source tree):
```python
from libxliff import XliffDocument, load, validate, dump
# load a fixture, validate, save
```
Verify imports originate in site-packages, not source checkout.
**Verification:** `import libxliff; print(libxliff.__file__)` shows site-packages path.

### TC-WHEEL-001-03: Verify no donor dependency

**Action:** `pip list | grep format-factory` — must show nothing.
`python -c "import format_factory"` — must raise ImportError.
**Verification:** Both checks pass.

**Commit:** `test(package): early installed-wheel smoke before module expansion`

**Push to GitLab after Stage 5 commits.**

---

## PRODUCT-FIRST ENFORCEMENT (applies from Stage 6 onward)

After parity, independence, XML security, validator decomposition, and API
normalization are complete: do NOT spend more time improving extraction
machinery. Almost all remaining work goes to product value:
- Eight standard modules
- Inline/content semantics
- Segmentation
- States
- QA
- Merge
- Corpus
- Interoperability evidence
- Documentation and examples

No generic framework is permitted in this repository. No governance machinery.
No supervisor infrastructure. This is a standalone library.

---

# STAGE 6 — STANDARD MODULES (8 vertical slices)

Each module follows the same vertical pattern. Each is a separate parent taskcard
with children covering spec analysis through evidence.

Module capability dimensions tracked independently:

| Dimension | Meaning |
|-----------|---------|
| `PARSED` | Module content parsed into typed objects (not `ExtensionNode`) |
| `MODELED` | Domain model with typed dataclasses exists |
| `QUERYABLE` | Consumers can inspect module data through typed accessors |
| `EDITABLE` | Safe mutations where the standard permits |
| `WRITABLE` | Changes serialize correctly |
| `VALIDATED` | Constraints beyond schema are enforced |
| `PRESERVATION_SAFE` | Unknown content within/around module survives lossless mode |
| `INTEROP_EVIDENCE` | Independent/official evidence exists |

Element/class sketches below are planning hypotheses. Each TC-MOD-*-01 spec analysis
MUST verify against the actual OASIS specification and bundled XSD/SCH assets before
implementation proceeds. **This is a HARD GATE — no module implementation child
(TC-MOD-*-02 through TC-MOD-*-10) may begin until TC-MOD-*-01 is CLOSED.**

No class hierarchy or XML structure from this plan may override specification evidence.
The first module (TC-MOD-MD-001) establishes the implementation ENGINEERING pattern.
Later modules reuse the engineering pattern (parse → model → query → edit → serialize →
validate → preserve → test), but derive their SEMANTIC model from their own spec analysis.

Spec analysis must inspect for each module:
- Relevant OASIS specification section
- Bundled XSD
- Schematron constraints (where present)
- Namespace URI
- Element cardinalities and attachment points
- Cross-references to core and other modules
- Inheritance/processing rules

---

## TC-MOD-MD-001: Metadata Module (1 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Small
**Namespace:** `urn:oasis:names:tc:xliff:metadata:2.0`
**Depends on:** TC-VALID-001 CLOSED, TC-API-003 CLOSED.

### TC-MOD-MD-001-01: Spec analysis

**Action:** Read OASIS XLIFF 2.1 spec Section 5.3 (Metadata Module). Read
bundled `metadata.xsd` and `metadata.sch`. Record: elements, attributes,
cardinalities, attachment points, constraints, interactions with core.
**Output:** Spec analysis record for Metadata module.

### TC-MOD-MD-001-02: Domain model

**Action:** Create `src/libxliff/modules/metadata.py` with typed dataclasses
based on spec analysis. Expected types (verify against spec):
`Metadata`, `MetaGroup`, `Meta`.
**File:** `src/libxliff/modules/metadata.py`

### TC-MOD-MD-001-03: Parse integration

**Action:** Extend `codec/reader.py` to detect `mda:` namespace elements and
parse into typed `Metadata` objects instead of `ExtensionNode`.
**File:** `src/libxliff/codec/reader.py`

### TC-MOD-MD-001-04: Query accessors

**Action:** Add typed accessors on `Unit`, `XliffFile`, `Group` to access
metadata content (e.g., `unit.metadata -> Metadata | None`).
**File:** `src/libxliff/model/document.py`

### TC-MOD-MD-001-05: Edit methods

**Action:** Add safe mutation methods where the standard permits (e.g.,
adding/removing meta groups, modifying meta values).

### TC-MOD-MD-001-06: Serialize

**Action:** Extend `codec/writer.py` to serialize typed `Metadata` objects
back to XML with correct namespace.
**File:** `src/libxliff/codec/writer.py`

### TC-MOD-MD-001-07: Validate

**Action:** Upgrade `validation/modules/metadata.py` to validate against
typed objects. Add constraint checks beyond schema.
**File:** `src/libxliff/validation/modules/metadata.py`

### TC-MOD-MD-001-08: Preservation test

**Action:** Verify that unknown content around/within metadata elements
survives lossless mode. Add roundtrip test with extra attributes/elements.

### TC-MOD-MD-001-09: Tests

**Action:** Create `tests/unit/test_module_metadata.py`:
- Parse positive fixture → verify typed model
- Parse negative fixture → verify error
- Roundtrip test (parse → serialize → parse → compare)
- Edit test (add/modify/remove metadata → verify serialization)
- Validation test (valid and invalid metadata structures)
**File:** `tests/unit/test_module_metadata.py`

### TC-MOD-MD-001-10: Update module coverage (evidence-based)

**Action:** Update `modules.py` based on PROVEN capability dimensions only.
Do NOT blindly set coverage to `MODELED` — set the actual capability-state
representation based on which dimensions were proven by tests:
PARSED, MODELED, QUERYABLE, EDITABLE, WRITABLE, VALIDATED,
PRESERVATION_SAFE, INTEROP_EVIDENCE.
Record each dimension's status with evidence reference.

**Commit:** `feat(modules): typed Metadata module support`
**Push to GitLab.**

---

## TC-MOD-FS-001: Format Style Module (2 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Small
**Namespace:** `urn:oasis:names:tc:xliff:fs:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

**Commit:** `feat(modules): typed Format Style module support`

---

## TC-MOD-GL-001: Glossary Module (3 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Medium
**Namespace:** `urn:oasis:names:tc:xliff:glossary:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

**Commit:** `feat(modules): typed Glossary module support`

---

## TC-MOD-MT-001: Translation Candidates Module (4 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Medium
**Namespace:** `urn:oasis:names:tc:xliff:matches:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

**Commit:** `feat(modules): typed Translation Candidates (Matches) module support`

---

## TC-MOD-SL-001: Size and Length Restriction Module (5 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Medium
**Namespace:** `urn:oasis:names:tc:xliff:sizerestriction:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

**Commit:** `feat(modules): typed Size and Length Restriction module support`

---

## TC-MOD-VL-001: Validation Module (6 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Medium
**Namespace:** `urn:oasis:names:tc:xliff:validation:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

**Commit:** `feat(modules): typed Validation module support`

---

## TC-MOD-RD-001: Resource Data Module (7 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Large
**Namespace:** `urn:oasis:names:tc:xliff:resourcedata:2.0`
**Depends on:** TC-VALID-001 CLOSED.
**Same 10-child pattern as TC-MOD-MD-001.**

### TC-MOD-RD-001-01 (spec analysis) MUST FIX:
The donor `modules.py` has `namespace=None, namespace_confirmed=False` for
Resource Data despite the validator already knowing the URI
(`urn:oasis:names:tc:xliff:resourcedata:2.0`). Fix this during spec analysis.
**Resolves finding:** F16.

**Commit:** `feat(modules): typed Resource Data module support`

---

## TC-MOD-ITS-001: ITS Module (8 of 8)

**Status:** TODO
**Type:** PARENT
**Complexity:** Very Large
**Namespaces:** `http://www.w3.org/2005/11/its` + `urn:oasis:names:tc:xliff:itsm:2.1`
**Depends on:** TC-MOD-MD-001 through TC-MOD-RD-001 patterns established.
**Note:** XLIFF 2.1 only. May require sub-package if 20+ data categories justify it.
**Same 10-child pattern as TC-MOD-MD-001, but children may be larger.**

**Commit:** `feat(modules): typed ITS module support`

**Push to GitLab after each module commit.**

---

# STAGE 7 — DEEP CORE WORKFLOWS

Enhance existing implementations. Each is a standalone parent taskcard.
Only work on demonstrated requirements — no speculative features.

## TC-WF-001: Hierarchy Enhancement

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify and enhance: files → groups → units → segments/ignorables.
Preserve order, IDs, scopes, references. Add tests for deep nesting, ordering.
**Commit:** `feat(workflow): enhanced hierarchy traversal and ordering`

## TC-WF-002: Inline Codes Enhancement

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify safe typed inline model. Test: paired codes (pc), isolated
codes (sc/ec), nesting, data references, invalid pairings, target-side
movement, unknown inline extensions.
**Commit:** `feat(workflow): comprehensive inline code model and tests`

## TC-WF-003: Source/Target Editing

**Status:** TODO
**Depends on:** TC-WF-002 CLOSED.
**Action:** Verify text replacement does not destroy inline codes. Test
token-aware replacement via `replace_text_slots`.
**Commit:** `feat(workflow): safe source/target text editing`

## TC-WF-004: Segmentation

**Status:** TODO
**Depends on:** TC-WF-002 CLOSED.
**Action:** Verify `split_segment`/`join_segments` preserve IDs, states,
inline validity, references, annotations. Test mapping/report output.
**Commit:** `feat(workflow): segmentation with integrity preservation`

## TC-WF-005: Translation States

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify standard state/substate exposure. Verify optional
transition-policy validation. No proprietary workflow semantics.
**Commit:** `feat(workflow): translation state management`

## TC-WF-006: Notes and Annotations

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify standardized note behavior and span/marker structures.
**Commit:** `feat(workflow): notes and annotation support`

## TC-WF-007: Merge

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify template merge and source-drift detection. Verify no
silent merge when correspondence cannot be proven.
**Commit:** `feat(workflow): template merge with drift detection`

## TC-WF-008: QA

**Status:** TODO
**Depends on:** Stage 5 CLOSED.
**Action:** Verify QA checks: missing targets, unchanged targets, placeholder
mismatches, inline mismatches, length constraints, consistency, invalid references.
Verify QA is separate from conformance validation.
**Commit:** `feat(workflow): localization QA checks`

---

# STAGE 8 — EVIDENCE AND QUALITY

## TC-SCHEMA-001: Schema Validation

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-MIGRATE-002 CLOSED.

### TC-SCHEMA-001-01: Verify schema provenance

**Action:** Compare all 20 bundled schema files against OASIS distribution
(using SHA-256 from `shared/sal-facts/evidence/xliff.yaml`).
Record provenance status for each.

### TC-SCHEMA-001-02: Test schema validation

**Action:** Verify `schema_validate()` and `full_schema_validate()` work
with `xmlschema` installed. Test valid and invalid documents.
**Verification:** `pip install .[schema] && pytest -k schema`.

### TC-SCHEMA-001-03: Document Schematron limitation

**Action:** Record that `.sch` files use `queryBinding="xslt2"` which
lxml's isoschematron cannot process. Document in README.
**Output:** Documentation note.

**Commit:** `test(schema): verify OASIS schema provenance and validation`

---

## TC-CORPUS-001: Build Real Corpus

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F8.
**Depends on:** Stage 6 module work substantially complete.

### TC-CORPUS-001-01: Create synthetic 2.x fixtures

**Action:** Create `tests/fixtures/valid/` documents covering:
- Groups, multiple files, inline codes, notes
- Each standard module (metadata, glossary, matches, etc.)
- Large documents (stress test)
- Different namespace layouts

### TC-CORPUS-001-02: Source official OASIS examples

**Action:** Search for legally reusable OASIS XLIFF 2.x test suite material.
If available, copy with provenance record to `tests/interoperability/`.

### TC-CORPUS-001-03: Source open-source XLIFF documents

**Action:** Search for permissively-licensed XLIFF 2.x documents from
localization tools (Okapi Framework, other open-source producers).
Record provenance.

**Commit:** `test(corpus): real XLIFF 2.x corpus with provenance`

---

## TC-CORPUS-002: Independent Interoperability Evidence

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F10.
**Depends on:** TC-CORPUS-001 CLOSED.

### TC-CORPUS-002-01: Schema validation of libxliff output

**Action:** Validate libxliff-serialized documents against OASIS XSD schemas.
**Verification:** All valid documents pass schema validation.

### TC-CORPUS-002-02: External tool roundtrip

**Action:** Where feasible, verify that documents produced by libxliff
can be re-read by independent XLIFF tools/validators.
Self-roundtrip does NOT count as interoperability.
**Output:** Interoperability evidence record.

**Commit:** `test(interop): independent interoperability evidence`

---

## TC-CLI-001: CLI Enhancement or Removal

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F11.
**Depends on:** TC-API-003 CLOSED, major workflow taskcards CLOSED.

### TC-CLI-001-01: Decide retain vs remove

**Action:** If the API surface justifies CLI commands, enhance.
Otherwise remove. Decision criteria: does each subcommand expose
a mature, tested API capability?

### TC-CLI-001-02: Implement subcommands (if retained)

**Action:** If retained:
- `libxliff inspect FILE` — version, files, units, module coverage
- `libxliff validate FILE` — structural + optional schema validation
- `libxliff qa FILE` — localization QA check summary
- `libxliff canonicalize FILE` — canonical output
**File:** `src/libxliff/cli/__init__.py`

### TC-CLI-001-03: Test installed CLI

**Action:** Build wheel, install in fresh venv, test `libxliff --help`,
test each subcommand. Test exit codes.
**Verification:** Installed entry point works.

**Commit:** `feat(cli): useful CLI subcommands (inspect/validate/qa/canonicalize)`

---

## TC-TEST-001: Testing Strategy Completion

**Status:** TODO
**Type:** PARENT
**Depends on:** Stages 5-7 substantially complete.

### TC-TEST-001-01: Property-based tests (core)

**Action:** Add hypothesis strategies for core workflows:
- Document construction/roundtrip
- Inline element generation/pairing
- Segmentation split/join
- Language/space inheritance
**Timing:** Run after Stage 5 normalization, before deep module work.

### TC-TEST-001-02: Property-based tests (modules)

**Action:** Add hypothesis strategies for module roundtrip invariants.
Run after each major module family (e.g., after small modules MD+FS,
after medium modules GL+MT+SL+VL, after large modules RD+ITS).
**Timing:** Incremental — not deferred to end.

### TC-TEST-001-03: Mutation tests (security + validation)

**Action:** Run mutation testing on critical paths AFTER Stage 5:
- Security boundary (xml.py) — prioritize
- ID/reference validation
- Inline pairing
- State transitions
**Timing:** After TC-SEC-001 and TC-VALID-001.

### TC-TEST-001-04: Mutation tests (modules + merge)

**Action:** Run focused mutation testing after each module family:
- Module cardinalities
- Merge/drift logic
**Timing:** Incremental — after each module family, not only at end.

### TC-TEST-001-05: Installed package tests (full)

**Action:** Create `tests/package/test_installed.py`:
- Build wheel → install in fresh venv → import libxliff → smoke test
- Build sdist → install → smoke test
- Verify schema package data included
- Verify CLI entry point works (if retained)
This is the FULL version of TC-WHEEL-001 (which was the early smoke).
**File:** `tests/package/test_installed.py`

**Commit:** `test(quality): property-based, mutation, and installed-package tests`

---

# STAGE 9 — PACKAGING AND RELEASE READINESS

## TC-CI-001: GitLab CI

**Status:** TODO
**Type:** PARENT
**Depends on:** TC-TEST-001 CLOSED.

### TC-CI-001-01: Create .gitlab-ci.yml

**Action:** Create CI config with stages:

**quality:**
- Ruff format check (`ruff format --check`)
- Ruff lint check (`ruff check`)
- Mypy strict (`mypy --strict src/`)

**test** (Python 3.11, 3.12, 3.13):
- Unit tests (`pytest tests/unit/`)
- Integration tests (`pytest tests/integration/`)
- Security tests (`pytest tests/security/`)

**interop** (REQUIRED — no `allow_failure`):
- Official schema validation environment (`pip install .[schema]`)
- Real/official XLIFF corpus tests (`pytest tests/interoperability/`)
- Independent validator/tool evidence where available

**package:**
- Wheel build (`python -m build --wheel`)
- Sdist build (`python -m build --sdist`)
- Clean wheel install in fresh venv + import smoke
- Clean sdist install in fresh venv + import smoke
- Import outside checkout verification
- Document API smoke test
- Installed CLI test (if retained)
- Schema package-data verification (XSD/SCH/NVDL files present in wheel)

**File:** `.gitlab-ci.yml`

**Commit:** `chore(ci): GitLab CI pipeline (quality/test/interop/package)`

---

## TC-PKG-001: Final Packaging

**Status:** TODO
**Type:** PARENT
**Resolves findings:** F2.
**Depends on:** All Stages 1-8 substantially complete.

### TC-PKG-001-01: Finalize metadata

**Action:** Update `pyproject.toml`:
- Version: `0.1.0` (remove `.dev0` — only when final gate passes)
- All classifiers, project URLs, description finalized
- Verify no stale metadata

### TC-PKG-001-02: Write documentation

**Action:** Comprehensive README.md covering:
- Installation
- Quick start (load/validate/edit/save)
- Module support matrix
- Version support (2.0/2.1)
- CLI usage
- Security posture
- API reference overview
**File:** `README.md`

### TC-PKG-001-03: Write CHANGELOG

**Action:** Document 0.1.0 release notes.
**File:** `CHANGELOG.md`

### TC-PKG-001-04: Create examples

**Action:** Create `examples/` with runnable scripts:
- `load_and_inspect.py`
- `validate_document.py`
- `translate_units.py`
- `access_modules.py`
**Verification:** Each example runs without error.

### TC-PKG-001-05: Build verification

**Action:** `python -m build` → verify wheel and sdist contents.
Check `py.typed` included, schemas included, no stray files.
**Verification:** `pip install dist/*.whl && python -c "import libxliff"` works.

### TC-PKG-001-06: Clean-clone test

**Action:** Clone from GitLab in fresh directory. `pip install .`. Run tests.
Verify NO format-factory dependency needed.
**Verification:** All tests pass in clean environment.

**Commit:** `chore(release): finalize packaging, docs, and examples`

---

# EXECUTION DAG

```
TC-DONOR-001
  └→ TC-REPO-001
       ├→ TC-MIGRATE-001 (preserve donor layout)
       │    └→ TC-MIGRATE-003
       └→ TC-MIGRATE-002
            └→ TC-PARITY-001 (GATE 1: extraction parity, donor-free)
                 ← TC-MIGRATE-001, TC-MIGRATE-002, TC-MIGRATE-003
                 ├→ TC-CORE-001
                 ├→ TC-CORE-002
                 ├→ TC-CORE-003 ← TC-CORE-001
                 ├→ TC-CORE-004 ← TC-CORE-001, TC-CORE-003
                 ├→ TC-CORE-005
                 └→ TC-CORE-006 (GATE 2: independence parity)
                      ← TC-CORE-001..005
                      ├→ TC-SEC-001 (parser investigation → hardening)
                      ├→ TC-VALID-001
                      ├→ TC-CODEC-001 (flatten, deferred from Stage 2)
                      ├→ TC-RENAME-001 (schema_validator rename + analytics flatten)
                      ├→ TC-VERSION-001
                      ├→ TC-API-001 ← TC-VALID-001
                      │    └→ TC-API-002
                      │         └→ TC-API-003
                      ├→ TC-TEST-REORG-001 ← TC-SEC-001, TC-VALID-001
                      └→ TC-WHEEL-001 (early installed-wheel smoke)
                           ← TC-API-003, TC-SEC-001, TC-VALID-001, TC-TEST-REORG-001
                           └→ TC-TEST-001-01, TC-TEST-001-03 (core property/mutation)
                                └→ [Stage 6: Modules — sequential]
                                     TC-MOD-MD-001 (establishes pattern)
                                     TC-MOD-FS-001
                                     TC-MOD-GL-001
                                     TC-MOD-MT-001
                                       └→ TC-TEST-001-02, TC-TEST-001-04 (module quality)
                                     TC-MOD-SL-001
                                     TC-MOD-VL-001
                                     TC-MOD-RD-001
                                     TC-MOD-ITS-001
                                     └→ [Stage 7: Workflows — parallel-safe]
                                          TC-WF-001..008
                                          └→ [Stage 8: Evidence]
                                               TC-SCHEMA-001, TC-CORPUS-001
                                               TC-CORPUS-002, TC-CLI-001
                                               TC-TEST-001-05 (full package)
                                               └→ [Stage 9: Release]
                                                    TC-CI-001, TC-PKG-001
                                                    └→ TC-GATE-001
```

Parallel-safe within a stage:
- TC-CORE-001, TC-CORE-002, TC-CORE-005 can run in parallel
- TC-SEC-001, TC-VALID-001, TC-CODEC-001, TC-RENAME-001, TC-VERSION-001 can run in parallel
- TC-WF-001..008 can mostly run in parallel (except TC-WF-003 depends on TC-WF-002)

Sequential requirements:
- All Stage 6 modules are sequential (first establishes pattern)
- TC-CORE-006 must wait for all TC-CORE-001..005
- TC-API-001 must wait for TC-VALID-001
- TC-WHEEL-001 must complete before module expansion begins
- TC-PKG-001 must wait for substantially all prior work
- Quality testing (property/mutation) runs incrementally, not only at end

---

# EVIDENCE CONTRACT

Every child taskcard MUST produce evidence before closing:

| Evidence type | Required for |
|---------------|-------------|
| Test output (pytest log) | All implementation taskcards |
| Grep verification | Import/reference removal taskcards |
| Diff review | All code changes |
| Extraction parity comparison | TC-PARITY-001 (GATE 1) |
| Independence parity comparison | TC-CORE-006-05 (GATE 2) |
| Parser selection justification | TC-SEC-001-01 |
| Adversarial security test results | TC-SEC-001-04 |
| Resource limit justification | TC-CORE-003-01 |
| API export semantic classification | TC-API-001-01 |
| Schema validation output | TC-SCHEMA-001 |
| Early installed-wheel smoke | TC-WHEEL-001 |
| Full installed package test | TC-TEST-001-05, TC-PKG-001 |
| Module capability dimensions (per dimension) | All TC-MOD-* |
| Spec analysis record | All TC-MOD-*-01 (hard gate) |
| Version support matrix (capability-based) | TC-VERSION-001-05 |

Evidence is captured inline (commit messages, test output) — not in separate
report infrastructure. This repository does not build governance machinery.

---

# FINAL COMPLETION GATE

## TC-GATE-001: Final Release-Ready Verification

**Status:** TODO
**Type:** PARENT
**Depends on:** All prior parent taskcards CLOSED.

The `/goal` ends only when ALL of the following are verified:

- [ ] `libxliff` on GitLab with complete pushed history
- [ ] Zero `format_factory` references in source or tests
- [ ] Zero runtime dependencies (OR only justified security dependency per TC-SEC-001-01)
- [ ] No legacy shadow implementation
- [ ] Extraction parity proven (TC-PARITY-001 GATE 1 evidence)
- [ ] Independence parity proven (TC-CORE-006-05 GATE 2 evidence)
- [ ] XML security: parser-level boundary (not scanning-only), adversarial suite passes
- [ ] XML parser selection justified with decision record
- [ ] Public API: document-centric, ~30 exports, proper naming
- [ ] Diagnostics/errors follow convention (DiagnosticSeverity, ValidationResult)
- [ ] Validator decomposed (no file >800 LOC)
- [ ] Resource limits fields and defaults justified with investigation evidence
- [ ] XLIFF 2.0 + 2.1 explicitly tested with version-correct fixtures
- [ ] Version support matrix is capability-based (no premature "fully supported")
- [ ] All 8 standard modules satisfy capability dimensions:
  - [ ] PARSED — module content parsed into typed objects
  - [ ] MODELED — domain model with typed dataclasses exists
  - [ ] QUERYABLE — typed accessors available
  - [ ] EDITABLE — safe mutations where the standard permits
  - [ ] WRITABLE — changes serialize correctly
  - [ ] VALIDATED — constraints beyond schema enforced
  - [ ] PRESERVATION_SAFE — unknown content survives lossless mode
  - [ ] INTEROP_EVIDENCE — independent/official evidence exists (where feasible)
- [ ] `is_production_complete()` returns `True` (product helper — NOT the release authority; the gate above is stronger)
- [ ] Official schema validation works
- [ ] Real corpus exists with recorded provenance
- [ ] Independent interoperability evidence exists
- [ ] Wheel + sdist build cleanly
- [ ] Installed-wheel tests pass outside source tree
- [ ] Security suite passes
- [ ] Property/mutation tests satisfactory
- [ ] CLI useful+documented or removed
- [ ] Examples run in CI
- [ ] GitLab CI passes all stages
- [ ] Version is `0.1.0` (no `.dev0`)
- [ ] Early installed-wheel smoke passed (TC-WHEEL-001)
- [ ] API export classification is semantic-role-based (not test-grep-only)
- [ ] All module spec analyses completed as hard gate before implementation
- [ ] All commits pushed to GitLab (not local-only)
- [ ] Clean clone → install → test passes without donor repo

---

---

# MISSION 2 — VERIFIED BASELINE (recorded 2026-08-12, before Stage 10 work begins)

Environment: Java available (OpenJDK 21.0.11 and 17.0.19, `java -version` confirmed) —
OpenXLIFF/Okapi-based oracle work is achievable, not blocked. `.venv/Scripts/pytest
tests/` → 777 passed, 3 skipped (Schematron/NVDL, documented XSLT2-tooling limitation).
Wheel builds clean (`libxliff-0.1.0-py3-none-any.whl`). `git log origin/master..HEAD`
empty — all Mission 1 commits pushed. Working tree clean.

## Corrected Capability Matrix

Status taxonomy: `complete_and_verified` / `implemented_but_insufficiently_tested` /
`partially_implemented` / `present_but_defective` / `missing` / `intentionally_deferred`
/ `blocked_by_external_evidence_or_infrastructure`.

| Capability | Status | Evidence |
|---|---|---|
| Secure XML parsing | complete_and_verified | `security/xml.py` — defusedxml parser-level DTD/entity rejection; 37 security tests |
| XLIFF 2.0/2.1 Core read/write | complete_and_verified | `codec/reader.py`/`writer.py`; 777 tests; `SUPPORTED_VERSIONS={"2.0","2.1"}` at reader.py:63 |
| XLIFF 1.2 Core read/write | missing | Zero code anywhere; deliberately rejected in Mission 1 (donor's 1.2 fixtures were mislabeled, not real support) |
| XLIFF 2.2 Core read/preserve | missing | Not previously assessed; 2.2 is an OASIS Committee Specification (2025-03-13), not yet a Standard |
| 8 standard 2.1 modules | complete_and_verified | `is_production_complete()==True`; all MODELED; 42 spec-traced "obligation" tests |
| Inline-code model (2.x) | complete_and_verified | pc/sc/ec pairing validated; `inline-codes-complex.xliff` fixture |
| Unknown-extension preservation (2.x) | complete_and_verified | `ExtensionNode`/`PreservationMode`; byte-identical repeated-write test |
| Deterministic canonical serialization | complete_and_verified | `dumps()`; version-downgrade loss detection raises `XliffWriteError` |
| Source-preserving serialization | missing | No attribute-order/prefix/comment/PI capture anywhere |
| Schema validation (XSD) | complete_and_verified | `schema_validate`/`full_schema_validate`; 10 bundled OASIS XSDs; 43 interop tests |
| Schematron validation | intentionally_deferred | 9 `.sch` files bundled but not executable — lxml isoschematron can't run XSLT2; documented in README |
| Semantic validation (ID/inline/state/references) | complete_and_verified | `validation/core.py` + per-module validators, max 286 LOC |
| Fragment/cross-reference validation (`#f1/u1/s1`) | missing | `validation/references.py` covers inline data-ref/isolated-pairing only, zero fragment-identifier logic |
| CRUD (create/update/delete) | partially_implemented | Works via raw `list.append()` on mutable dataclasses; no guided API, no id-uniqueness check on mutation |
| Querying | partially_implemented | `iter_units()` + 2 module-scoped `find_*`; no document-wide search/filter |
| Translation statistics | partially_implemented | `analytics.py` — 3 functions, 39 lines; no word counts, no per-file/module breakdown |
| Structural/content diff | missing | No `diff.py` or equivalent anywhere |
| Streaming/lazy parsing | missing | `_parse()` is whole-document DOM only; zero iterparse/lazy code |
| Atomic writes | missing | `dump()` calls `Path.write_text()` directly, no temp-file+rename |
| Structured diagnostics with real source spans | present_but_defective | `SourceLocation` dataclass exists but is populated with real line/column in exactly zero call sites; `ET.ParseError.position` is available but discarded |
| CLI | partially_implemented | `inspect`/`validate`/`qa`/`canonicalize` work; no `stats`/`diff` |
| Version/dialect detection | partially_implemented | Version read from `@version` attribute; no dialect (SDLXLIFF/MXLIFF/etc.) sniffing, not required for MVP |
| PO/JSON/ARB/CSV/TMX interoperability | missing | `adapters/__init__.py` is a one-line docstring; zero adapter code |
| 1.2↔2.x conversion with loss report | missing | Only a narrow `dumps(profile="2.0")` write-time guard exists (blocks silent 2.1-content loss); no general converter |
| Interoperability oracle (external tool) | missing | FF's `oracle/formats/xliff/oracle-package.yaml` is self-referential (targets the donor module, marks INTEROPERABILITY not-applicable, reason "Python stdlib xml.etree is the reference parser") |
| Property-based tests | claimed_but_unproven → missing | Mission 1's TC-TEST-001 claimed this CLOSED; `hypothesis` is a declared dependency, zero `@given`/`strategies` usage found in `tests/` |
| Fuzz tests | claimed_but_unproven → missing | Same taskcard, same finding |
| Mutation tests | claimed_but_unproven → missing | Same taskcard, same finding; no mutmut/cosmic-ray config anywhere |
| Benchmarks | missing | No `pytest-benchmark`, no `perf_counter` usage, no benchmark file |
| ADRs | missing | No `docs/adr/` or `DECISIONS.md` in libxliff |
| License / third-party notices | complete_and_verified | Full Apache-2.0 `LICENSE`; substantive `THIRD_PARTY_NOTICES.md` with real OASIS provenance table |
| CI (quality/test/interop/package) | complete_and_verified | `.gitlab-ci.yml`, 4 stages, Python 3.11-3.13; Linux-only (no OS matrix — not MVP-blocking per research §14.2, deferred) |
| Conformance manifest / limitations doc | missing | README has version/module tables but no dedicated "Conformance Manifest" or "Limitations" section |

---

# MISSION 2 — MVP SCOPE

Source: `docs/reference/xliff-technical-ecosystem-report.md` §11.1-11.2, reconciled
against the verified baseline above and the product charter. Full detail in the report;
this table is the binding scope contract for Stage 10-15 taskcards.

## Must-have (Stage 10-12 target; blocks TC-GATE-002)

Version/dialect-hint detection · XLIFF 1.2 Core read/write (narrower "v1" scope, see
Stage 10 note) · 2.0/2.1 Core (done) · 2.2 Core read/opaque-preserve (write only if
justified — low priority, 2.2 is not yet an OASIS Standard) · version-specific models
(no false equivalence) · language/namespace handling · notes/states/metadata basics ·
lossless mixed-content/inline token model (done 2.x, needed 1.2) · unknown-extension
preservation (done 2.x, needed 1.2) · structural validation (done) · streaming
inspection · deterministic canonical output (done) · structured errors with real
location · secure parser defaults (done).

## Should-have (Stage 11-14 target; blocks TC-GATE-002 unless explicitly deferred below)

Builders/edit transactions · inline pair/reference integrity (done 2.x) · duplicate-ID/
fragment checks · offline XSD validation (done) · semantic validation levels (done) ·
module-aware parse/write (done, 2.x) · vendor-extension round-trip (done, 2.x) ·
1.2↔2.x conversion WITH explicit loss report (never silent) · structural/content diff ·
statistics (real expansion) · atomic writes · CLI JSON output (SARIF explicitly
optional, not required) · **one** pilot adapter — PO, chosen because OASIS publishes an
official PO-profile guide (cited in the report) and PO has the cleanest 1:1 key/value
mapping in the interoperability matrix; this satisfies "at most one conversion or
profile pilot... necessary to demonstrate the adapter architecture" without committing
to RESX/JSON/ARB/CSV/TMX/Android/Apple/dialect packs.

## Explicitly excluded from Mission 2 (do not taskcard; record as intentionally_deferred)

TM/MT/LLM translation · terminology engine beyond existing Glossary module · any
converter beyond the one PO pilot · vendor-dialect normalization packs (Apple, Angular,
SDLXLIFF, MQXLIFF, MXLIFF, TXLF, WPML) · desktop editor · cloud service · TMS
connectors · guessing-based auto-repair · multi-language bindings · Rust rewrite ·
DOCX/HTML/Markdown extraction · universal lossless 1.2↔2.x conversion claims ·
unqualified "fully XLIFF compliant" claims · OS matrix expansion in CI (Linux-only
stays acceptable for this MVP) · SARIF CLI output.

---

# MISSION 2 — ARCHITECTURE DECISIONS

Full design rationale recorded as ADRs under `docs/adr/` during Stage 14 (`TC-ADR-001`).
Binding decisions for Stage 10-11 implementation:

1. **XLIFF 1.2 lives in a new sibling package `src/libxliff/v12/`** (`model.py`,
   `reader.py`, `writer.py`, `validation.py`), never inside `model/document.py`. 1.2's
   `TransUnit` has no `Segment` list — segmentation is expressed via `seg_source:
   list[InlineNode]` walked by a thin `iter_seg_marks()` helper, reusing
   `model/inline.py::InlineElement`/`InlineNode` as-is (that module has no 2.x-specific
   fields). `security/xml.py::safe_fromstring`, `security/limits.py`, and the whole
   `errors.py` hierarchy are reused unmodified — they are already namespace-agnostic.
   `reader.py`'s `_local()` helper (reader.py:99-100) is copied verbatim into `v12/`.
2. **Version-neutral query facade**: new `src/libxliff/view.py` — `XliffView` wraps
   either `XliffDocument` (2.x) or the new `Xliff12Document`, dispatching on
   `isinstance`, exposing `iter_segments()`/`iter_notes()`/`.version` uniformly. This is
   what `stats`/`diff`/CLI get built against — not a shared mutable base class.
3. **Lossless/source-preserving layer extends the existing dataclasses; no parallel XML
   tree.** Add `attribute_order`/`declared_prefixes` fields to the dataclasses that
   already carry `attributes: dict[str, str]` (document.py:97-193), captured from
   `element.attrib` insertion order (already preserved by dict) plus a
   `start-ns`-event iterparse pass. One `DocumentEnvelope`-style record (`encoding`,
   `has_bom`, `newline`) attaches once per document. Comments/PIs become small
   `ExtensionNode`-like siblings using the existing extension machinery. This reuses the
   proven `PreservationMode`/`ExtensionNode` pattern rather than building a second
   parallel tree (which the research proposes but which duplicates work the codebase
   already does a different, working way).
4. **Streaming**: new `codec/streaming.py`, `stream_units(source) -> Iterator[Unit]`
   using `ET.iterparse(events=("end",))` matching `{ns}unit`, tracking `file`/`group`
   ancestry for context, calling `.clear()` after each unit. Must re-implement the
   security guard incrementally (the existing `safe_fromstring` post-parse tree walk
   assumes one full tree — `iterparse` bypasses it) — this is real new work, not free
   reuse; verify at implementation time whether `defusedxml` exposes an iterparse-safe
   path or whether a hardened `XMLParser` must be built by hand.
5. **CRUD**: new `src/libxliff/builder.py` (`DocumentBuilder`) with validated
   `add_unit`/`remove_unit`/`add_segment`/`update_target`/`set_state` methods —
   additive only. Raw list mutation stays available; the builder is a safety layer, not
   a gate.
6. **Diff/stats**: expand `analytics.py` (`DocumentStats`, `compute_stats()`, built on
   `XliffView`); new `diff.py` (`DiffReport`, id-keyed `diff_documents()`).
7. **Atomic writes**: `writer.py::dump()` — temp file in the same directory +
   `os.replace()`, ~15 lines, mechanical.
8. **Real source spans**: `ET.ParseError.position` (line, column) already exists on the
   exception raised at `security/xml.py:112-113` and is currently discarded — capture it
   into `SourceLocation` on the parse-error path (small). Per-node validation spans
   require threading position tracking through the parse traversal — fold this into
   item 3's combined attribute-order/prefix pass rather than doing it twice (larger).
9. **What does not change**: the 8 typed modules, the 2.0/2.1 dataclass model, the
   security boundary, and the existing semantic validation layer are not touched except
   for the additive error-path change in item 8.

---

# MISSION 2 — INDEPENDENCE BOUNDARY (binding, re-verified at TC-GATE-002)

`libxliff` is being *certified using* Format Factory, not *built from* it. The published
package must not: import any `format_factory`/`format-factory-core` package; depend on
any FF path, environment variable, state file, registry, or runtime service; mention
Format Factory anywhere in its public identity, package metadata, API, docs, examples,
generated artifacts, or diagnostics; require the monorepo to build/install/test/use;
contain unrelated code from other format libraries; depend on non-public FF
infrastructure. Verified in a clean environment outside the FF import path (already
proven once for Mission 1's scope — TC-WHEEL-001/TC-GATE-001 — must be reproven for
every Mission 2 addition at TC-GATE-002).

# MISSION 2 — FORMAT FACTORY MACHINERY REUSE CLASSIFICATION

Correction from the planning session (binding): "reuse Format Factory machinery" means
invoke FF's **skills, commands, supervisor governance, certification scripts, and
oracle framework** — as external tooling run *from* the format-factory repo, *targeting*
the external libxliff checkout by absolute path — never port, copy, or adapt product
code from `src/` (including the Mission-1-superseded donor at
`src/python/xliff/src/format_factory/xliff/`, which is legacy and stays untouched) into
libxliff. Two of the items below were verified this session by reading the actual
tool source, not assumed from the skill's description alone.

| Component | What it is | Classification | Verified detail |
|---|---|---|---|
| `/property-based-testing` skill | Prompt-only checklist, zero bundled code | Direct reuse (methodology) | Guides authoring TC-PBT-001/002 and TC-FUZZ-001/002; the resulting test *code* still lives natively in `libxliff/tests/` — a standalone repo must be able to `pytest tests/` with zero FF present, so the tests themselves are libxliff-only even though the methodology is FF-governed |
| `/run-oracle` + `tools/oracle/execute_oracle.py` | Executes `oracle/formats/<fmt>/oracle-package.yaml` against a format library that must be "importable from `src/python/` **or installed**" | Format Factory extension | Verified: the existing `oracle/formats/xliff/oracle-package.yaml` is stale — `executor_config` targets the donor module `format_factory.xliff.load_xliff`, and `INTEROPERABILITY` is explicitly `not_applicable`. TC-ORACLE-002/003 below fix `executor_config` to target the **installed `libxliff` package** (pip-installed from the GitLab wheel into a throwaway FF-side venv, not from a monorepo path) and add a genuine `INTEROPERABILITY` profile — this requires registering a new external-tool provider, which is real, justified extension work in `tools/oracle/provider_registry.yaml`, not a copy-paste |
| `/certification-mutation-tester` (`tools/certification/mutation_tester.py`) | `--target <file>`, `--tests <dir>`, `--output <json>` | Direct reuse | Verified: genuinely path-parametric (no monorepo path hardcoding in the argument-handling code) — TC-MUT-001 points `--target`/`--tests` directly at the libxliff checkout |
| `/certification-performance-benchmark` (`tools/certification/performance_benchmark.py`) | Benchmark harness | Adaptation required | Verified: hardcodes `sys.path.insert(0, REPO_ROOT / "src" / "python")` and formats-specific subpaths — **not** portable to an external repo as-is. TC-BENCH-001 adapts this FF-side script to accept an external `--src-root`, rather than reimplementing benchmarking logic inside libxliff |
| Other `certification-*` skills (stub-detector, assertion-scorer, exception-checker, generate-security-tests) | Various `tools/certification/*.py` | Adaptation required (verify per-script before use) | Not yet individually verified for path-parametrization — TC-CERT-000 checks each one actually used before Stage 12 relies on it; do not assume portability |
| `/plan-hardening`, `/post-sprint-audit`, `write_plan_lock.py`, `check_continuation.py` | FF's supervisor/governance loop | Direct reuse (process, not code) | Governs Mission 2 execution the same way it governed Mission 1 — taskcard state transitions, sprint audits, plan-lock lifecycle. This is process discipline applied *by the executing agent*, not a libxliff dependency |
| Gap-ledger / taskcard YAML schema (`.supervisor/schemas/stage2-taskcard-contract.schema.json`) | Taskcard field conventions | libxliff-only naming convention, monorepo-only machinery | The `TC-<AREA>-<NNN>` ID scheme and field vocabulary are reused as *convention* in this plan file; the actual schema-validation tooling stays in FF and is never referenced by libxliff |
| Evidence-bundle format (`evidence-declaration.yaml`) | FF's per-sprint evidence contract | Reject for libxliff-internal evidence | Too deeply coupled to FF's supervisor/grader/registry machinery to reuse even as convention; Mission 2 evidence lives in `docs/certification/CONFORMANCE.md` + `docs/certification/evidence/*.json` inside libxliff, a much lighter libxliff-only format, populated *from* FF-tooling output but not shaped like FF's own contract |
| `oracle/formats/xliff/oracle-package.yaml` itself | FF's existing (stale) xliff oracle package | Format Factory extension (repair + extend, do not fork) | Lives in FF permanently — it's the format-registry entry for XLIFF, not a libxliff artifact; Mission 2 fixes and extends it in place |

---

# STAGE 10 — XLIFF 1.2 CORE (critical path)

**Scope boundary for "1.2 Core v1"** (binding — this is what closes as
`complete_and_verified`, not a partial claim): `<xliff>`/`<file>`/`<header>`/`<body>`/
`<group>`/`<trans-unit>`/`<source>`/`<target>`/`<note>`(s), `<seg-source>`+`<mrk
mtype="seg">` segmentation, non-overlapping `<bpt>/<ept>`/`<ph>`/`<it>`/`<sub>` inline
pairs, and 1.2's own target `state`/`state-qualifier`/`approved` values (kept fully
distinct from the 2.x `state`/`subState` machine — no shared enum, no silent mapping).
**Explicitly deferred** to `TC-V12-101` (fast-follow, outside Mission 2 gate, tracked
honestly as `intentionally_deferred` not `partially_implemented`): `<alt-trans>`,
`<bin-unit>`/`<bin-source>`/`<bin-target>`, `<context-group>`/`<count-group>` modules,
and complex inline crossing/overlap/subflow edge cases. This boundary exists so Stage 10
can close truthfully rather than carry a permanently-partial flagship item.

## TC-V12-001: 1.2 Core Document Model

**Status:** TODO **Type:** PARENT **Size:** L **Depends on:** Stage 5 CLOSED (Mission 1).
**Objective:** Typed dataclasses for the 1.2 Core scope above, in `src/libxliff/v12/model.py`.
**Public API impact:** New public module `libxliff.v12`; no changes to existing exports.
**Backward-compat risk:** None — purely additive.
**Non-goals:** No alt-trans, no bin-unit, no context-group (see scope boundary).

### TC-V12-001-01: Spec analysis
**Action:** Read OASIS XLIFF 1.2 (docs.oasis-open.org/xliff/v1.2/os/xliff-core.html)
sections for file/header/body/group/trans-unit/note/source/target. Record element
cardinalities, required attributes (`original`, `source-language`, `datatype` on
`<file>`; `id` on `<trans-unit>`), and the Strict vs Transitional XSD distinction (bundle
both; note in the model which one a document validates against).
**Output:** Spec analysis record, same format as Mission 1's `TC-MOD-*-01` cards.

### TC-V12-001-02: Core dataclasses
**Action:** `Xliff12Document`, `TransUnitFile`, `Group12`, `TransUnit`, `Note12` per the
architecture decision above — mutable `@dataclass(slots=True)`, matching the existing
2.x model's shape/conventions (`attributes: dict[str,str]` for unknowns, etc.) but as an
entirely separate type hierarchy.
**Verification:** mypy --strict clean; no import from `model/document.py`.

## TC-V12-002: 1.2 Inline + Segmentation Model

**Status:** TODO **Type:** PARENT **Size:** L **Depends on:** TC-V12-001 CLOSED.
**Objective:** `bpt`/`ept`/`ph`/`it`/`sub` inline tokens (non-overlapping pairs only,
per scope boundary) and `seg-source`/`mrk[mtype=seg]` segmentation, reusing
`model/inline.py::InlineElement`/`InlineNode` unmodified.
**Security implications:** None beyond the shared parsing boundary (item 10 below).

### TC-V12-002-01: Inline token mapping
**Action:** Map 1.2's inline vocabulary onto the existing `InlineElement`/`InlineNode`
shape (tag/attributes/content/tail) — confirm no 1.2-specific fields are needed on that
shared type; if any are, add them as optional fields (never break 2.x usage).
**Verification:** Existing 2.x inline tests still pass unmodified after any shared-type change.

### TC-V12-002-02: Segmentation via seg-source/mrk
**Action:** `iter_seg_marks(trans_unit) -> Iterator[SegMark]` walking `seg-source`'s
`mrk[mtype="seg"]` children, exposing `mid`, source tokens, and the corresponding target
span (matched by `mid` in `<target>`'s own `mrk` markers where present).
**Output:** Working segmentation reader against real 1.2 fixtures.

## TC-V12-003: 1.2 Parser

**Status:** TODO **Type:** PARENT **Size:** L **Depends on:** TC-V12-002 CLOSED.
**Objective:** `src/libxliff/v12/reader.py` — `load12`/`loads12`, reusing
`security/xml.py::safe_fromstring` and `security/limits.py::XliffResourceLimits`
unmodified (both are namespace-agnostic, verified during architecture review).
**Security implications:** Inherits the existing parser-level DTD/entity protection —
no new security surface, but must be proven by a dedicated adversarial test (see
TC-V12-006).

### TC-V12-003-01: Root/file/header/body/group/trans-unit parse functions
**Action:** Mirror `codec/reader.py`'s dispatch-by-`_local(tag)` pattern for the 1.2
element set. Tolerant/strict mode via a `_ParseContext`-analog copied and adapted (not
shared — the 1.2 recovery messages are distinct).
**Verification:** Parses all official OASIS 1.2 spec examples without error.

### TC-V12-003-02: Unknown-extension preservation for 1.2
**Action:** Same `ExtensionNode` pattern as 2.x — unknown elements/attributes at 1.2
extension points round-trip losslessly.
**Verification:** Roundtrip test with a synthetic vendor extension survives byte-for-byte
(within the 1.2 canonical serialization contract).

## TC-V12-004: 1.2 Writer

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-V12-003 CLOSED.
**Objective:** `src/libxliff/v12/writer.py` — `dump12`/`dumps12`, deterministic
canonical output matching the rigor `codec/writer.py` already gives 2.x (repeated-call
byte-identical test required).

### TC-V12-004-01: Canonical serializer
**Action:** Deterministic attribute ordering, namespace prefix policy, indentation
outside mixed content (never pretty-print inside `<source>`/`<target>` — this is a hard
rule carried from the research and from the existing 2.x writer's own discipline).
**Verification:** `test_repeated_dumps12_calls_are_byte_identical` passes.

## TC-V12-005: 1.2 Validation

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-V12-004 CLOSED.
**Objective:** `src/libxliff/v12/validation.py` — duplicate-ID checks (1.2 scoping
rules differ from 2.x — verify against spec, do not assume identical), 1.2's own
state/state-qualifier value validation (distinct enum from 2.x, no shared code), and
Strict-vs-Transitional XSD selection.
**Depends on:** Also bundle the 1.2 Strict + Transitional XSDs into
`v12/schemas/` (new files, licensed/provenance-documented same as the existing 20
2.x/module schemas in `THIRD_PARTY_NOTICES.md`).

## TC-V12-006: 1.2 Test Suite + Fixtures

**Status:** TODO **Type:** PARENT **Size:** L **Depends on:** TC-V12-005 CLOSED.
**Gate:** Stage 10 does not close until this reaches parity in rigor with the 2.x suite.
**Required tests:** parser/writer/roundtrip/validation/security(adversarial) for the
full 1.2 Core v1 scope boundary — target ≥100 tests, matching the density of the
existing per-module 2.x suites (15-34 tests each). Fixtures under
`tests/fixtures/valid/xliff-1.2/` and `tests/fixtures/invalid/xliff-1.2/`, sourced from
official OASIS 1.2 spec examples first, synthetic second.
**Evidence:** Full pytest output; fixture provenance table (spec-derived vs synthetic).

## TC-V12-101: alt-trans + Complex Inline (fast-follow, OUTSIDE Mission 2 gate)

**Status:** DEFERRED_WITH_REASON **Reason:** Scope boundary — see Stage 10 preamble.
**Depends on:** TC-V12-006 CLOSED. **Does not block TC-GATE-002.**

## TC-DETECT-001: Version/Dialect Detection + load() Dispatch

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** TC-V12-003 CLOSED (for full
dispatch; sniff-only logic may start once TC-V12-001 is CLOSED).
**Objective:** Top-level `libxliff.load()` inspects root `xliff/@version` and namespace,
routes to 1.2 (`v12.load12`) or 2.x (`codec.reader.load`), raises a structured
`XliffUnsupportedVersionError` for 1.0/1.1/2.2/unknown rather than a generic parse error.
**Public API impact:** `load()`'s dispatch logic changes; its signature does not.
**Backward-compat risk:** None if 2.x routing is unchanged for 2.x input — add a
regression test proving existing 2.x callers see identical behavior post-dispatch.

## TC-CONV12-001: 1.2↔2.x Conversion with Loss Report

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-V12-006 CLOSED,
TC-DETECT-001 CLOSED.
**Objective:** `convert(document, to="2.1") -> ConversionResult` (document + explicit
machine-readable `ConversionReport` listing preserved/transformed/approximated/dropped
items per the research's fidelity model). Never silent. Never claim "lossless" without a
named source profile, target profile, and a passing round-trip test for that pair.
**Non-goals:** No universal lossless claim; no 1.0/1.1/2.2 conversion.

---

# STAGE 11 — CORE INFRASTRUCTURE (parallel to Stage 10 — touches existing 2.x files, not v12/)

## TC-STREAM-001: Streaming Inspection API

**Status:** TODO **Type:** PARENT **Size:** L **Depends on:** Stage 5 CLOSED (Mission 1).
**Objective:** `codec/streaming.py::stream_units(source, *, limits=None) ->
Iterator[Unit]` via `ET.iterparse(events=("end",))`, bounded memory (`.clear()` after
each unit), tracking `file`/`group` ancestry for context attachment.
**Security implications:** Must reimplement resource-limit enforcement incrementally
(node/depth/text-byte counting) since `iterparse` bypasses `safe_fromstring`'s
post-parse tree walk — this is genuinely new security-relevant code, requires its own
adversarial tests, not inherited "for free" from the existing boundary.
**Required tests:** Memory-bound proof on a large synthetic fixture (e.g. 50K units);
adversarial DTD/entity rejection proven independently of the DOM-parse path.

## TC-IO-001: Atomic Writes

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** Stage 5 CLOSED.
**Objective:** `writer.py::dump()` — temp file in destination's directory + `os.replace()`.
**Required tests:** Simulated interrupted write leaves the original file (or nothing),
never a truncated/corrupt file at the destination path.

## TC-IO-002: Real Source Spans

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Stage 5 CLOSED. **Coordinate
with TC-STREAM-001** (both touch `codec/reader.py` — same owner/sequence to avoid
merge conflicts).
**Objective:** Parse-error path captures `ET.ParseError.position` into `SourceLocation`
(small, mechanical). Per-node validation spans require position tracking threaded
through the parse traversal — implement as part of the attribute-order/prefix capture
pass from Architecture Decision 3, not as a second traversal.

## TC-BUILD-001: CRUD/Builder API (2.x)

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Stage 5 CLOSED.
**Objective:** `src/libxliff/builder.py::DocumentBuilder` — validated
`add_unit`/`remove_unit`/`add_segment`/`update_target`/`set_state`, each checking
id-uniqueness before mutating (a check that does not exist today on raw `.append()`).
**Backward-compat risk:** None — additive; raw list mutation remains fully supported.

## TC-BUILD-002: Extend Builder to 1.2 (fast-follow)

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-BUILD-001, TC-V12-006 CLOSED.

## TC-DIFF-001: Structural + Content Diff

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-BUILD-001 CLOSED.
**Objective:** `diff.py::DiffReport`/`diff_documents(a: XliffView, b: XliffView)` —
id-keyed (not positional) added/removed/changed segment diff, JSON-serializable.

## TC-STATS-001: Real Statistics Module

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Stage 5 CLOSED.
**Objective:** Replace the 39-line `analytics.py` stub with `DocumentStats`
(unit/segment/word counts, translated %, per-file/per-module rollups) built on
`XliffView`, so it works uniformly for 1.2 and 2.x once both exist.
**Required tests:** Word/segment counts verified against fixtures with hand-computed
expected values (not just "runs without error").

## TC-CLI-002: CLI stats/diff Subcommands

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** TC-STATS-001, TC-DIFF-001 CLOSED.
**Objective:** `cli/__init__.py` gains `stats`/`diff` subcommands, JSON output matching
the existing `inspect`/`validate`/`qa`/`canonicalize` conventions, stable exit codes.

---

# STAGE 12 — INTEROPERABILITY ORACLE & TEST INFRASTRUCTURE

All taskcards in this stage invoke FF's actual skill/tooling layer (see Machinery Reuse
Classification above) run *from* format-factory *against* the external libxliff path.
None of this tooling is ported into libxliff; only its output evidence is copied in.

## TC-CERT-000: Verify Certification Tooling Portability Per-Script

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** Nothing.
**Objective:** For every `certification-*` skill this stage plans to invoke
(mutation-tester, performance-benchmark, stub-detector, generate-security-tests,
exception-checker), read its underlying script in `tools/certification/*.py` and
classify it Direct-reuse or Adaptation-required per actual argument handling — do not
assume portability from the skill description alone. Already verified this session:
`mutation_tester.py` is genuinely path-parametric (`--target`/`--tests`/`--output`,
no monorepo-path hardcoding) → Direct reuse. `performance_benchmark.py` hardcodes
`sys.path.insert(0, REPO_ROOT / "src" / "python")` → Adaptation required (see
TC-BENCH-001). Verify the remaining scripts before Stage 12 relies on them.
**Non-goals:** Do not fix format-factory's scripts under this taskcard beyond what a
specific downstream taskcard (e.g. TC-BENCH-001) explicitly needs.
**Evidence:** Per-script classification table with source citations.

## TC-ORACLE-001: Acquire + License-Vet OpenXLIFF

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** Nothing.
**Objective:** Pin an OpenXLIFF (EPL-1.0, github.com/maxprograms-com/OpenXLIFF) release
by version + SHA-256, download the JAR/distribution into format-factory's test-tooling
area (not libxliff), record provenance. **Test-only tooling — never a runtime or
install-time dependency of libxliff itself.**
**Verification:** `java -jar <openxliff>.jar -version` runs successfully using the
confirmed-available OpenJDK 21.0.11.

## TC-ORACLE-002: Extend FF's Oracle Framework — OpenXLIFF Provider + Fixed executor_config

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-ORACLE-001 CLOSED.
**Objective:** This is genuine, justified extension of FF's oracle machinery (see
classification table) — not a libxliff-side reimplementation:
1. `pip install` the libxliff wheel (from GitLab, or a locally built wheel) into a
   throwaway venv reachable by `tools/oracle/execute_oracle.py`.
2. Fix `oracle/formats/xliff/oracle-package.yaml`'s `executor_config` — currently
   `module: format_factory.xliff, callable: load_xliff` (the superseded donor) — to
   target the **installed `libxliff` package** (`module: libxliff, callable: load`).
3. Register a new OpenXLIFF provider in `tools/oracle/provider_registry.yaml` following
   the existing LibreOffice/FODS provider pattern (binary discovery via the OpenJDK
   install, version pin, invocation flags) — this generalizes the provider framework to
   a second external tool, benefiting any future format oracle that needs a
   non-LibreOffice/non-stdlib reference.
4. Change `profiles_not_applicable` — remove the `INTEROPERABILITY: not_applicable`
   entry (its stated reason, "Python stdlib xml.etree is the reference parser," is
   exactly the self-referential gap this taskcard closes) and add real
   `INTEROPERABILITY` cases backed by the OpenXLIFF provider.
**Public API impact on libxliff:** None — libxliff is only ever installed/imported, never
modified by this taskcard.

## TC-ORACLE-003: Run Oracle — 2.x Interoperability Corpus + Comparison

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-ORACLE-002 CLOSED.
**Objective:** Invoke `/run-oracle` (`python tools/oracle/execute_oracle.py --format
xliff --profile INTEROPERABILITY`) round-tripping libxliff-authored 2.x documents
through OpenXLIFF; compare semantic equivalence per the research's fidelity model (text/
IDs/context/notes/states/inline-codes/candidates/metadata/extensions each get an
independent result, not one boolean).
**Evidence:** `oracle-run-summary.json` (FF-side, permanent record in
`oracle/formats/xliff/reports/`) copied into libxliff's own
`docs/certification/evidence/oracle-interop-2x.json` with a provenance header
(`generated_by`, `ff_commit`, `libxliff_commit`, `date`) — copied, never referenced by
path back into format-factory.

## TC-ORACLE-004: Extend Oracle to 1.2 (fast-follow within Mission 2)

**Status:** TODO **Type:** CHILD **Size:** M **Depends on:** TC-ORACLE-003, TC-V12-004 CLOSED.
**Objective:** Add 1.2 corpus cases to the same oracle package/provider from
TC-ORACLE-002 — no new machinery, just new cases and an `executor_config` variant
targeting `libxliff.v12.load12`.

## TC-PBT-001: Property-Based Test Suite (2.x Roundtrip)

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Nothing.
**Objective:** Invoke the `/property-based-testing` skill as the methodology/checklist
for authoring real `@given`/`hypothesis.strategies` tests — generating valid 2.x
documents, asserting parse↔write roundtrip equivalence — activating the currently-
unused `hypothesis` dependency already in `pyproject.toml`. The test *code* is authored
natively inside `libxliff/tests/` (a standalone repo must be fully self-testing with
zero FF present); the skill governs methodology only, contributes no code.
**Corrects:** The `claimed_but_unproven` finding against Mission 1's TC-TEST-001.

## TC-PBT-002: Extend to 1.2

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-PBT-001, TC-V12-006 CLOSED.

## TC-FUZZ-001: Fuzz Test Suite (2.x Parser)

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Nothing.
**Objective:** Via the same `/property-based-testing` skill's fuzz-oriented guidance,
author hypothesis-driven malformed/adversarial-input tests targeting parser crash/hang
resistance, feeding new cases into libxliff's own `tests/security/` and
`tests/fixtures/adversarial/`. Native libxliff test code, FF-governed methodology only.
**Corrects:** The same `claimed_but_unproven` TC-TEST-001 finding, fuzz half.

## TC-FUZZ-002: Extend to 1.2 Parser

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-FUZZ-001, TC-V12-003 CLOSED.

## TC-BENCH-001: Benchmark Suite (Baseline, 2.x) via /certification-performance-benchmark

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-CERT-000 CLOSED (needs
the portability verdict first — sized M, not S, because adaptation is required, not
optional, per TC-CERT-000's finding).
**Objective:** Adapt `tools/certification/performance_benchmark.py` (FF-side) to accept
an external `--src-root`/`--package` argument instead of its hardcoded
`REPO_ROOT/src/python` assumption, then invoke `/certification-performance-benchmark`
against the libxliff checkout for parse/write/validate throughput on representative
small/medium/large fixtures and peak-memory measurement. This is a small, justified
generalization of FF's own script (benefits any future externally-benchmarked library),
not a libxliff-side reimplementation. Baseline numbers are measured, never invented.
**Evidence:** Benchmark JSON copied into `docs/certification/evidence/`.

## TC-BENCH-002: Extend to Streaming + 1.2

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-BENCH-001, TC-STREAM-001,
TC-V12-006 CLOSED.

## TC-MUT-001: Mutation Testing Pass via /certification-mutation-tester

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** TC-V12-006, TC-PBT-001,
TC-CERT-000 CLOSED.
**Objective:** Invoke `/certification-mutation-tester`
(`tools/certification/mutation_tester.py --target <libxliff>/src/libxliff/... --tests
<libxliff>/tests/... --output <report>.json`) — confirmed genuinely path-parametric, no
adaptation needed — over `model/`, `codec/`, `validation/` (including the new `v12/`
modules). Fix weak-assertion gaps the mutation score surfaces; re-run until score is
acceptable.
**Corrects:** The same `claimed_but_unproven` TC-TEST-001 finding, mutation half.
**Evidence:** Mutation score JSON copied into `docs/certification/evidence/`.

---

# STAGE 13 — PO ADAPTER PILOT

## TC-ADAPT-PO-001: PO↔XLIFF 2.x Mapping Model

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Nothing (targets existing 2.x only).
**Objective:** `adapters/po.py` implementing the OASIS PO-profile-guided key/value
mapping (msgid/msgstr, context, comments, references, fuzzy/flags where the profile
defines them). Replaces the `adapters/__init__.py` stub with real content.
**Non-goals:** No plural-array handling beyond what the profile defines; no obsolete-
entry support; this is a pilot demonstrating the adapter architecture, not a complete
gettext toolkit.

## TC-ADAPT-PO-002: PO Adapter Loss Report

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-ADAPT-PO-001 CLOSED.
**Objective:** Mirrors TC-CONV12-001's explicit-loss-report pattern — no silent lossy
conversion claims for the PO pilot either.

## TC-ADAPT-PO-003: PO Adapter Test Suite

**Status:** TODO **Type:** CHILD **Size:** S **Depends on:** TC-ADAPT-PO-002 CLOSED.
**Objective:** Roundtrip + loss-report tests. Demonstrates the adapter boundary is
extensible without committing Mission 2 to further format adapters.

---

# STAGE 14 — DOCUMENTATION & GOVERNANCE (rolling, low conflict, can start immediately)

## TC-ADR-001: Architecture Decision Records

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Nothing — one ADR per
closed work package, written as that package closes, not batched at the end.
**Objective:** `docs/adr/` — minimum 6 ADRs by TC-GATE-002: version-model separation
(1.2 as sibling package, never flattened), streaming design, builder-API transaction
model, lossless-layer-extends-not-parallel-tree decision, oracle provider choice,
conversion loss-report format.

## TC-DOCS-001: Conformance Manifest + Docs Overhaul

**Status:** TODO **Type:** PARENT **Size:** M **Depends on:** Near-completion of Stage
10-13 (this is the last content-dependent card in Stage 14).
**Objective:** README/new `CONFORMANCE.md` states exactly: which versions are
Read/Write/Modify/Validate roles apply to, which modules are typed vs opaque, which
validation levels are implemented, which profiles/tool versions were tested, source-
preservation guarantees, known fidelity limitations. **Never** an unqualified "fully
XLIFF compliant" claim anywhere in the repo (README, docstrings, CLI help text,
package metadata description).
**Verification:** `grep -ri "fully.*compliant\|fully xliff"` across the repo returns
zero hits outside this explicit-prohibition note itself.

---

# STAGE 15 — CI & FINAL GATE

## TC-CI-002: CI Expansion

**Status:** TODO **Type:** PARENT **Size:** S **Depends on:** TC-PBT-001, TC-FUZZ-001,
TC-MUT-001, TC-BENCH-001, TC-ORACLE-003 (each needs a runnable entry point first).
**Objective:** `.gitlab-ci.yml` gains fuzz/mutation/benchmark/oracle jobs. Java/JAR
availability handled as an explicit, reportable condition — per the research, "a
skipped interoperability suite is not a passing release gate," so a skip must be logged
with a reason, never silently green.

## TC-GATE-002: Final MVP Re-Certification and Packaging

**Status:** ITERATION_REQUIRED (all agent-achievable items verified CLOSED;
one TRUE_EXTERNAL_GATE remains — see below) **Type:** PARENT **Depends on:**
All Stage 10-14 must-have and should-have taskcards CLOSED. `TC-V12-101` is
explicitly excluded from this gate (deferred, not blocking).

The Mission 2 scope ends only when ALL of the following are verified:

- [x] XLIFF 1.2 Core v1 (scope boundary above) reads/writes/validates, ≥100 dedicated tests (124)
- [x] 1.2 and 2.x remain genuinely separate models — zero shared mutable dataclass forces false equivalence
- [x] Version/dialect detection routes correctly; unsupported versions raise a structured error
- [x] 1.2↔2.x conversion exists with an explicit, non-silent loss report
- [x] Streaming API proven memory-bounded on a large fixture, with its own adversarial security tests
- [x] Atomic writes proven (interrupted-write test)
- [x] Real source spans populated on the parse-error path at minimum
- [x] CRUD builder API exists for both 1.2 and 2.x, additive to raw mutation (TC-BUILD-002 implemented for real this session — see its taskcard row)
- [x] Diff and real statistics modules exist, tested against hand-computed expected values (verified: `test_word_and_char_counts_hand_computed` etc.)
- [x] CLI has `inspect`/`validate`/`qa`/`canonicalize`/`stats`/`diff`, all JSON-capable, stable exit codes (canonicalize writes XML by design, not JSON — its job is producing output, not a report; verified all 6 subcommands exist and the other 5 emit JSON with 0/1 exit codes)
- [x] One PO adapter pilot works end-to-end with a loss report
- [x] Interoperability oracle proven against an independent external tool, not self-referential — **Okapi Framework Tikal 1.48.0**, not OpenXLIFF (OpenXLIFF rejected: no prebuilt release JAR, requires Java 25 vs 21/17 available; see ADR-007). 8/8 FF-side oracle cases + 4/4 native libxliff-side cases PASS.
- [x] Real property-based test suite exists and passes (corrects TC-TEST-001's false closure)
- [x] Real fuzz test suite exists and passes (corrects TC-TEST-001's false closure)
- [x] Real mutation test suite run with a reported score (corrects TC-TEST-001's false closure)
- [x] Benchmark baseline recorded (not invented) for parse/write/validate at 3+ file sizes
- [x] Minimum 6 ADRs recorded for the Mission 2 architecture decisions (7: ADR-001..007)
- [x] Conformance manifest published; zero unqualified "fully compliant" claims anywhere (grep-verified: only hit is the prohibition statement itself)
- [x] Wheel + sdist build cleanly; installed-wheel smoke test passes outside the source tree (verified this session in two fresh venvs under the scratchpad, zero format-factory packages present, CLI entry point works, all 20 schema files + v12 present in the wheel)
- [x] Version bumped from 0.1.0 (e.g. 0.2.0) reflecting the MVP scope increase (0.2.0)
- [ ] All Mission 2 commits pushed to GitLab — **TRUE_EXTERNAL_GATE:
      `EXTERNAL_BLOCKER: git_push_credentials_unavailable`.** The `gitlab_token`
      (formerly `gl_pat`) was invalid/expired/improperly-scoped — verified via 4
      distinct checks across this session: (1) direct `git push` → GCM dialog
      cancelled; (2) `credential.helper=` override with askpass → server
      rejection; (3) `git ls-remote` (read-only diagnostic) → identical
      "HTTP Basic: Access denied" error; (4) re-checked `git ls-remote`
      again after several more hours of session work (in case the token
      was rotated externally mid-session) → identical error. 52 commits
      exist locally on `master`, none pushed. This is recorded here per
      the plan's own rule: "Never close the product goal with unpublished
      local commits unless GitLab is genuinely externally unavailable and
      the blocker is explicitly recorded." A human with a valid `gitlab_token`
      (or corrected credential) must run `git push origin master` from
      `c:\Users\prora\OneDrive\Documents\GitHub\libxliff` to complete this
      item — no other lane in this plan can resolve it.
- [ ] `docs/certification/CONFORMANCE.md` + `docs/certification/evidence/*.json` populated,
      each MVP requirement mapped to its taskcard ID and evidence file (evidence
      generated via FF tooling run externally per TC-CERT-000, then copied — never
      referenced by path back into format-factory, never imported at runtime)

---

# MISSION 2 — EXECUTION DAG (extends the Mission 1 DAG; TC-GATE-001 is CLOSED and stays closed)

```
[Mission 1: TC-GATE-001 CLOSED]
  └→ TC-V12-001 → TC-V12-002 → TC-V12-003 → TC-V12-004 → TC-V12-005 → TC-V12-006
       ├→ TC-V12-101 (deferred, non-blocking)
       ├→ TC-DETECT-001 (sniff-only can start after TC-V12-001; full dispatch after TC-V12-003)
       │    └→ TC-CONV12-001 ← TC-V12-006
       │         └→ TC-ORACLE-004 ← TC-ORACLE-003
       ├→ TC-BUILD-002 ← TC-BUILD-001
       ├→ TC-PBT-002 ← TC-PBT-001
       ├→ TC-FUZZ-002 ← TC-FUZZ-001
       └→ TC-BENCH-002 ← TC-BENCH-001, TC-STREAM-001

[Parallel, no dependency on Stage 10]
  TC-STREAM-001 (own lane: codec/reader.py + writer.py, coordinate with TC-IO-002)
  TC-IO-001 (own file region: writer.py::dump)
  TC-IO-002 (coordinate with TC-STREAM-001: codec/reader.py)
  TC-BUILD-001 → TC-DIFF-001, TC-STATS-001 → TC-CLI-002
  TC-CERT-000, TC-ORACLE-001 → TC-ORACLE-002 → TC-ORACLE-003
  TC-PBT-001, TC-FUZZ-001, TC-BENCH-001 (fully independent of each other)
  TC-ADAPT-PO-001 → TC-ADAPT-PO-002 → TC-ADAPT-PO-003 (fully isolated lane: adapters/)
  TC-ADR-001 (rolling, near-zero conflict, throughout)

[Join points]
  TC-MUT-001 ← TC-V12-006, TC-PBT-001, TC-CERT-000
  TC-CI-002 ← TC-PBT-001, TC-FUZZ-001, TC-MUT-001, TC-BENCH-001, TC-ORACLE-003
  TC-DOCS-001 ← near-completion of Stage 10-13
  TC-GATE-002 ← all Stage 10-14 must-have/should-have CLOSED (TC-V12-101 excluded)
```

**Critical path:** `TC-V12-001→002→003→004→005→006→DETECT-001→CONV12-001→
ORACLE-004→DOCS-001→GATE-002` — 11 sequential nodes, mostly L/M sized. XLIFF 1.2 Core
dominates schedule length; the PO-adapter and 2.x-oracle lanes are shorter and finish
well before Stage 10 does.

**Parallel-safe lanes (file-conflict-free):**
- Lane A — `v12/`, `validation/` (new v12 submodule only): all of Stage 10.
- Lane B — existing `codec/reader.py`/`writer.py`: TC-STREAM-001, TC-IO-001, TC-IO-002
  (same owner/sequence within the lane to avoid conflicts with each other).
- Lane C1 — libxliff `tests/` only, native test code: TC-PBT-001/002, TC-FUZZ-001/002 —
  fully parallel to A/B/D.
- Lane C2 — format-factory-side tooling extension (`oracle/formats/xliff/`,
  `tools/oracle/provider_registry.yaml`, `tools/certification/*.py`), touches
  format-factory not libxliff: TC-CERT-000, TC-ORACLE-001..004, TC-BENCH-001/002,
  TC-MUT-001 — parallel to A/B/C1/D, but sequenced internally against each other since
  they share `oracle/formats/xliff/oracle-package.yaml` and `tools/certification/`.
- Lane D — new `builder.py`/`diff.py`/`analytics.py` expansion: TC-BUILD-001,
  TC-DIFF-001, TC-STATS-001, then TC-CLI-002.
- Lane E — `adapters/po.py`: Stage 13, fully isolated.
- Lane F — `docs/adr/`: TC-ADR-001, rolling throughout.

---

# MISSION 2 — EVIDENCE CONTRACT (extends Mission 1's)

Same discipline as Mission 1 (evidence inline via commit messages + test output — no
separate report-generation machinery built inside libxliff). Additional evidence types:

| Evidence type | Required for |
|---|---|
| 1.2 spec analysis record | TC-V12-001-01 (hard gate before TC-V12-002 begins) |
| ≥100-test 1.2 suite output | TC-V12-006 |
| Conversion loss-report sample (real output, not description) | TC-CONV12-001, TC-ADAPT-PO-002 |
| Streaming memory-bound proof | TC-STREAM-001 |
| Interrupted-write test output | TC-IO-001 |
| Oracle comparison report (checked into `docs/certification/evidence/`) | TC-ORACLE-003, TC-ORACLE-004 |
| Property-based/fuzz test run output | TC-PBT-001/002, TC-FUZZ-001/002 |
| Mutation score report | TC-MUT-001 |
| Benchmark baseline numbers (measured, not invented) | TC-BENCH-001/002 |
| ADR files (minimum 6) | TC-ADR-001 |
| Conformance-manifest-vs-evidence cross-check | TC-DOCS-001, TC-GATE-002 |

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-DONOR-001 | CLOSED |
| TC-REPO-001 | CLOSED |
| TC-MIGRATE-001 | CLOSED |
| TC-MIGRATE-002 | CLOSED |
| TC-MIGRATE-003 | CLOSED |
| TC-PARITY-001 | CLOSED |
| TC-CORE-001 | CLOSED |
| TC-CORE-002 | CLOSED |
| TC-CORE-003 | CLOSED |
| TC-CORE-004 | CLOSED |
| TC-CORE-005 | CLOSED |
| TC-CORE-006 | CLOSED |
| TC-SEC-001 | CLOSED |
| TC-VALID-001 | CLOSED |
| TC-CODEC-001 | CLOSED |
| TC-RENAME-001 | CLOSED |
| TC-VERSION-001 | CLOSED |
| TC-API-001 | CLOSED |
| TC-API-002 | CLOSED |
| TC-API-003 | CLOSED |
| TC-TEST-REORG-001 | CLOSED |
| TC-WHEEL-001 | CLOSED |
| TC-MOD-MD-001 | CLOSED |
| TC-MOD-FS-001 | CLOSED |
| TC-MOD-GL-001 | CLOSED |
| TC-MOD-MT-001 | CLOSED |
| TC-MOD-SL-001 | CLOSED |
| TC-MOD-VL-001 | CLOSED |
| TC-MOD-RD-001 | CLOSED |
| TC-MOD-ITS-001 | CLOSED |
| TC-WF-001 | CLOSED |
| TC-WF-002 | CLOSED |
| TC-WF-003 | CLOSED |
| TC-WF-004 | CLOSED |
| TC-WF-005 | CLOSED |
| TC-WF-006 | CLOSED |
| TC-WF-007 | CLOSED |
| TC-WF-008 | CLOSED |
| TC-SCHEMA-001 | CLOSED |
| TC-CORPUS-001 | CLOSED |
| TC-CORPUS-002 | CLOSED |
| TC-CLI-001 | CLOSED |
| TC-TEST-001 | CLOSED (see Mission 2 baseline: property/mutation sub-claims found `claimed_but_unproven`, corrected by TC-PBT-001/TC-FUZZ-001/TC-MUT-001 — not reopened) |
| TC-CI-001 | CLOSED |
| TC-PKG-001 | CLOSED |
| TC-GATE-001 | CLOSED |
| TC-V12-001 | CLOSED |
| TC-V12-002 | CLOSED |
| TC-V12-003 | CLOSED |
| TC-V12-004 | CLOSED |
| TC-V12-005 | CLOSED |
| TC-V12-006 | CLOSED |
| TC-V12-101 | DEFERRED_WITH_REASON |
| TC-DETECT-001 | CLOSED |
| TC-CONV12-001 | CLOSED |
| TC-STREAM-001 | CLOSED |
| TC-IO-001 | CLOSED |
| TC-IO-002 | CLOSED |
| TC-BUILD-001 | CLOSED |
| TC-BUILD-002 | CLOSED (implemented for real -- TC-GATE-002's own checklist required "CRUD builder API exists for both 1.2 and 2.x"; the DEFERRED_WITH_REASON label conflicted with that and was resolved by building it, not by weakening the gate) |
| TC-DIFF-001 | CLOSED |
| TC-STATS-001 | CLOSED |
| TC-CLI-002 | CLOSED |
| TC-CERT-000 | CLOSED |
| TC-ORACLE-001 | CLOSED |
| TC-ORACLE-002 | CLOSED |
| TC-ORACLE-003 | CLOSED |
| TC-ORACLE-004 | CLOSED |
| TC-PBT-001 | CLOSED |
| TC-PBT-002 | DEFERRED_WITH_REASON |
| TC-FUZZ-001 | CLOSED |
| TC-FUZZ-002 | DEFERRED_WITH_REASON |
| TC-BENCH-001 | CLOSED |
| TC-BENCH-002 | DEFERRED_WITH_REASON |
| TC-MUT-001 | CLOSED |
| TC-ADAPT-PO-001 | CLOSED |
| TC-ADAPT-PO-002 | CLOSED |
| TC-ADAPT-PO-003 | CLOSED |
| TC-ADR-001 | CLOSED |
| TC-DOCS-001 | CLOSED |
| TC-CI-002 | CLOSED |
| TC-GATE-002 | BLOCKED_EXTERNAL (20/21 checklist items verified; GitLab push blocked on invalid `gitlab_token` credential — `EXTERNAL_BLOCKER: git_push_credentials_unavailable`, verified 4x this session, see TC-GATE-002's own checklist entry above for full detail) |

---

# EXECUTION HANDOFF

**Authoritative plan:** This file (external seed). On execution start, copy to
`plans/.claude/crystalline-sauteeing-cupcake.md` in the format-factory repo per
CLAUDE.md Step 0, then run
`python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/crystalline-sauteeing-cupcake.md`
to reopen the plan lock (it is currently `TERMINAL_CLOSED` from Mission 1 — Mission 2
requires a fresh, non-terminal lock).

**Mission 1 (Stages 1-9):** CLOSED. Do not re-execute. Do not reopen TC-GATE-001.

**Mission 2 first parent taskcard:** TC-V12-001 (1.2 Core Document Model).
**Mission 2 first child taskcard:** TC-V12-001-01 (Spec analysis).
**Working directory:** `c:\Users\prora\OneDrive\Documents\GitHub\libxliff`.

**Execution rules (same discipline as Mission 1):**
1. Read this plan (Mission 2 section).
2. Select the next eligible TODO taskcard by dependency order — Lane A (Stage 10) is
   the critical path; Lanes B-F may run concurrently with it and with each other.
3. Confirm prerequisites are CLOSED.
4. Execute the taskcard's action; implement the smallest durable, correct change.
5. Add/update tests before claiming success; run focused tests, then the full suite.
6. Capture evidence per the Evidence Contract above.
7. Mark taskcard VERIFIED → CLOSED; update this plan's Taskcard Status Summary table.
8. Continue to the next eligible taskcard — do not stop between taskcards for approval.
9. Commit and push at each parent-taskcard completion (GitLab, per Mission 1's verified
   push mechanism — `gitlab_token` env var via inline URL with `oauth2` pseudo-username,
   never printed/logged/embedded in the remote URL, never force-pushed).
10. When all Stage 10-14 must-have/should-have taskcards are CLOSED → verify TC-GATE-002.
11. Only a genuine external blocker (unavailable credentials, a legally restricted
    fixture, an inaccessible external system, a mandatory publication-approval gate)
    stops execution — record it precisely and continue every other safe lane.

**The execution agent must NOT:**
- Skip taskcards without marking DEFERRED_WITH_REASON
- Close a parent before its children
- Treat code existence as verification
- Treat test existence as passing proof
- Build governance/reporting machinery
- Add speculative features not in this plan
- Force XLIFF 1.2 into the 2.x mutable model
- Reduce tests, weaken validators, or narrow scope to manufacture a green gate
- Claim "fully XLIFF compliant" anywhere
- Reopen TC-GATE-001 / Mission 1 taskcards (Mission 1 is CLOSED history; corrections to
  Mission 1's false TC-TEST-001 closure are handled by Mission 2's TC-PBT-001/
  TC-FUZZ-001/TC-MUT-001, not by reopening the old taskcard)
