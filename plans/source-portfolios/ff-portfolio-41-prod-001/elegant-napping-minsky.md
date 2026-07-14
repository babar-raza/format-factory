# elegant-napping-minsky
# Format Factory — API Architecture Policy Encoding + Product Audit (v2 — production pass)
# Plan type: policy_encoding + product_audit
# Tracks: B (system policy) then C (product audit)
# Revised: deep inspection pass — root causes identified, prior plan discarded

---

## What the Deep Inspection Found

Three agents examined: validator source code, actual product source trees, and the QName/promotion registries.

### What Already Works — Do Not Touch

- **V111-V127** are SOURCE_STATIC_ANALYSIS validators that read actual AST and file contents: spec_qname
  ClassVar presence, catch-all filenames (V117), root-document-owns-nested-QName (V113), constant-return
  stubs (V124), TODO/FIXME without GAP-*/TC-* ref (V123), Compat/ not behavioral (V129), etc. These are
  well-targeted. Do not duplicate them.

- **3-tier QName registry** is complete and machine-readable:
  - `registry/python-qname-architecture.json` — format-level state (ACCEPTED_VERIFIED for all 20 Python formats)
  - `registry/python-qname-structural-facts.json` — QName↔fact authority for non-ODF formats
  - `shared/qname-registry/{format}.yaml` — per-symbol: qname, canonical_class, spec_fact_ref, facade_names,
    python_file, dotnet_file, namespace_uri, local_name

- **promotion-ledger.yaml** exists with hash-based change detection. `autonomous_cycle.py` already detects
  hash mismatch and auto-sets state=REOPENED. V119 (validate_promoted_code_changed_without_reopening)
  is wired and ready.

- **Python spec/ hierarchy** is production-quality in FODS: 16 classes across 5 namespace dirs, each with
  spec_qname, spec_fact_ref, namespace_uri, local_name, facade_names. This is the pattern to enforce
  elsewhere — not to redesign.

- **no_stub_scan.py** via V149, LOC caps via V78/V79, analytics masquerade via V77, multi-responsibility
  via V66, import direction via V75 — all working.

### The Three Root Causes

**Root Cause 1 — Promotion state machine is armed but never loaded.**
promotion-ledger.yaml has entries (CSV Python, FODT Python at IMPLEMENTATION_VERIFIED). V119 blocks
changes to PROMOTED_STABLE files. But no format has reached PROMOTED_STABLE, so V119 has never fired
and the protection is inert. The missing piece is a tool that executes the IMPLEMENTATION_VERIFIED →
PROMOTED_STABLE transition with prerequisite verification. Without it, the entire protection layer is
technically correct but operationally void.

**Root Cause 2 — No machine-readable public API manifest.**
The spec's Section 3 requires every public symbol to declare: qname, parser_path, writer_path,
roundtrip_test. The existing registry gives QName→facade (shared/qname-registry/{format}.yaml,
facade_names field). The reverse — facade method → QName → parser obligation → writer obligation —
exists nowhere in machine-readable form. V114-V115 check declaration YAML fields for these paths, but
there is no source to validate those claims against, and no per-symbol mapping file for validators
to read. This means the "getters without parser paths / setters without writer paths" counters from
Section 13 cannot be computed and are purely aspirational.

**Root Cause 3 — Architecture audit is manual and one-shot.**
Python has `registry/python-qname-architecture.json` (format-level state per format). .NET has no
equivalent. Without a tool that reads `src/net/` and `src/python/` and emits a per-format
classification (COMPLIANT through FULL_REBUILD), V120 (certify without architecture proof) has nothing
to check against, the 23 completion counters cannot be computed accurately, and the Section 9 pilot
proof requirement cannot be verified mechanically.

### Why the First Plan's Validators Were Wrong

The 6 proposed validators (V150-V155) were mostly DECLARATION_CHECK or duplicated existing coverage:
- V150 (init_reexport_only): overlaps V65 (__all__) and V113 (root nesting)
- V151 (python_model_layer_segregation): overlaps V66 (multi-responsibility) and V111 (spec_qname placement)
- V153 (qname_namespace_per_file): overlaps V126 (file in approved subdirs)
- V154 (aspose_hierarchy_depth): checks declaration fields, no source read
- V155 (promotion_record): checks declaration fields, not ledger state

Adding redundant validators increases expected_count noise, creates false PASS signals, and doesn't
close any real gap. They were dropped.

---

## Production-Grade Solution

Four concrete infrastructure components, in dependency order.

---

### TC-B01: Architecture Audit Tool
**Status:** OPEN
**Lane:** machinery_governance
**File created:** `tools/review/architecture_audit.py`
**File created:** `reports/architecture-audit/` (directory, with .gitkeep)
**Files modified:** none (tool is standalone, called manually and from TC-B03 validation)

**What it does:**
Scans `src/python/{format}/` and `src/net/{format}/` for all formats in format-registry.yaml.
For each format×language, emits `reports/architecture-audit/{format}_{lang}.json`.

**Python audit criteria (all objective, automatable):**
```
spec_dir_present:        src/python/{f}/spec/ exists
spec_namespaced:         at least one subdir under spec/ (not flat)
models_spec_qname:       all classes in models.py have spec_qname attribute (AST scan)
init_logic_free:         __init__.py has no class/function definitions (AST scan)
compat_delegates:        Compat/ classes have methods that call spec types (not empty shells)
parser_produces_typed:   parser.py/codec.py contains import from spec/ (not just dict returns)
```

**Classification mapping:**
```
COMPLIANT                  all 6 criteria pass
MINOR_REALIGNMENT          4-5 pass; failures are naming/minor gaps only
PUBLIC_FACADE_REPAIR       spec/ present but Compat/ missing or empty; init has logic
QNAME_MODEL_DECOMPOSITION  spec_qname classes found in wrong files (parser, codec)
PARSER_WRITER_REALIGNMENT  parser.py has no spec/ import (produces raw dicts only)
FULL_REBUILD               spec_dir_present = false; no spec_qname anywhere
```

**.NET audit criteria:**
```
model_dir_present:       src/net/{f}/Model/ exists
spec_dir_present:        src/net/{f}/Spec/ exists
no_dumping_ground:       no files named *ExtendedApis.cs, *MissingMethods.cs, *Misc.cs
loc_within_cap:          all files ≤ baseline_loc_cap from source-structure-baseline.json
spec_qname_constants:    at least one .cs file has const string SpecQName (grep)
model_depth:             at least 2 levels in Model/ (root type + child types)
```

**Output JSON schema per format:**
```json
{
  "format_id": "fods",
  "language": "python",
  "audit_timestamp": "2026-07-10T...",
  "classification": "COMPLIANT",
  "criteria": {
    "spec_dir_present": true,
    "spec_namespaced": true,
    "models_spec_qname": true,
    "init_logic_free": true,
    "compat_delegates": true,
    "parser_produces_typed": true
  },
  "violations": [],
  "files_scanned": 15
}
```

**Cap:** 300 LOC. Uses `registry/source-structure-baseline.json` for LOC data (already computed).
Uses `ast.parse` for Python; grep for .NET. No new dependencies.

**Idempotency:** Second run overwrites output with identical content (audit is deterministic).

---

### TC-B02: Public API Manifest (Schema + FODS Pilot)
**Status:** OPEN (depends on TC-B01 classification of FODS as COMPLIANT)
**Lane:** lane-qname-mapping (new lane, added in TC-B04)
**Files created:**
- `.supervisor/schemas/public-api-manifest.schema.json`
- `registry/public-api-manifest/fods_python.yaml` (FODS pilot manifest)
- `registry/public-api-manifest/fods_dotnet.yaml`

**What it does:**
Defines the machine-readable per-symbol mapping that the spec's Section 3 requires.
Starts with FODS as the pilot format (most complete in both languages).

**Schema fields (per symbol entry):**
```yaml
- public_symbol: "FodsDocument.get_sheet"
  owning_type: "FodsDocument"
  qname: "table:table"                        # from shared/qname-registry/fods.yaml
  canonical_model_type: "spec.table.table.Table"
  parser_path: "src/python/fods/fods_codec.py::parse_fods"
  writer_path: "src/python/fods/fods_writer.py::write_fods"
  roundtrip_test: "tests/python/fods/test_fods_roundtrip.py::test_sheet_roundtrip"
  spec_fact_ids: ["FACT-FODS-042"]
  capability_ids: ["add-python-api"]
  compatibility_status: "COMPLIANT"
```

**Required cross-references (two consistency constraints):**
1. `qname` must appear as a key in `shared/qname-registry/fods.yaml`
2. `owning_type` must appear in `facade_names` of the matched qname-registry entry

These constraints are checked by new validator V150 (see TC-B03).

**FODS Python manifest scope:** All public symbols in `src/python/fods/__init__.py.__all__`
(approximately 20-30 methods). Derive from existing facade_names and spec/ classes.

**FODS .NET manifest scope:** All public methods on `FodsDocument` and `FodsCell` (the two
primary public types). Approximately 40-50 symbols based on known file structure.

**Other formats:** Manifests are created incrementally — one per pilot proof (Section 9).
Not all 30 formats need manifests before promotion; only the format being promoted.

---

### TC-B03: Three Focused Validators (replacing the prior six)
**Status:** OPEN (depends on TC-B01 and TC-B02)
**Lane:** machinery_governance
**File created:** `tools/supervisor/governance_validators_arch_api.py`
**Files modified:** `tools/supervisor/governance_validator_runner.py` (expected_count 167→170)

Only 3 validators — each closes a real gap not covered by existing validators.

**V150 `validate_public_api_manifest_consistency`** (SOURCE_STATIC_ANALYSIS)
- Reads `registry/public-api-manifest/{format}_{lang}.yaml` for any format mentioned in the
  declaration's `planned_work_items`
- Verifies: parser_path file exists on disk; writer_path file exists on disk; roundtrip_test
  file exists on disk; qname appears in `shared/qname-registry/{format}.yaml`
- Severity: FAIL for missing files; WARN for missing qname cross-reference
- Does NOT fire if no manifest file exists for the format (opt-in, not universal gate yet)
- Rule-ref: ARCH-API-001 (Section 3 public_api_mapping requirement)

**V151 `validate_architecture_audit_regression`** (SOURCE_STATIC_ANALYSIS + REGISTRY_CHECK)
- Reads `reports/architecture-audit/{format}_{lang}.json` for each format in changed_files
- If classification was COMPLIANT or MINOR_REALIGNMENT in last audit, and current changed_files
  introduce a file that violates the audit criteria (e.g., adds a class with spec_qname to
  parser.py, or adds *ExtendedApis.cs), severity is FAIL
- If no prior audit JSON exists: WARN only (not a FAIL — audit-first policy, not retroactive block)
- Forces: architecture audit must be run before promotion work begins
- Rule-ref: ARCH-API-002 (Section 7 audit requirement)

**V152 `validate_promotion_prerequisite`** (REGISTRY_CHECK)
- Fires only for RELEASE_GATE declaration items
- Reads promotion-ledger.yaml for the declared format+language
- FAIL if a RELEASE_GATE item claims promotion_level > IMPLEMENTATION_VERIFIED without a
  corresponding promotion-ledger.yaml entry at PROMOTED_STABLE or CERTIFIED
- Severity: FAIL (hard gate — a release gate claim without ledger backing is a false certification)
- Does not fire for PRODUCT_SOURCE or PRODUCT_TEST items (only RELEASE_GATE)
- Rule-ref: ARCH-API-003 (Section 11 promotion controls)

**Runner update:**
- Import governance_validators_arch_api
- Add V150, V151, V152 to the per-changed-file loop (V151) and work-item loop (V150, V152)
- Update expected_count: 167 → 170
- Update test assertion in `tests/supervisor/test_governance_validators.py`

**Why only 3 (not 6):**
167 validators is already dense. Every additional validator that fires on the same condition as an
existing one creates double-reporting (two WARN/FAILs for one root cause) and raises the expected_count
baseline without increasing enforcement signal. V150-V152 close the three real gaps. Any further
validators should wait until these have been exercised in at least 2 sprint cycles to detect false positives.

---

### TC-B04: Lane Registry Expansion + Promotion Tool
**Status:** OPEN
**Lane:** layer_governance
**Files modified:** `registry/lane-scope-registry.yaml`
**Files created:** `tools/supervisor/promote_product.py`
**Files created:** `.supervisor/schemas/public-api-manifest.schema.json`
**Files created:** `.supervisor/schemas/promotion-record.schema.json`
**Files created:** `registry/public-api-manifest/` (directory, .gitkeep)

**Part A — 7 new lanes in lane-scope-registry.yaml:**

The spec (Section 8) requires 14 lanes. Current registry has 5. Add the 7 below (which map to the
spec's 14 lanes after deduplication with existing ones):

```yaml
- lane_id: lane-qname-mapping
  name: QName Mapping
  purpose: Map spec QNames to canonical types, namespaces, folders, files; write qname-registry entries
  permitted_writes: [registry/**, docs/architecture/**, .local/evidences/**]
  forbidden_writes: [src/**]
  required_skill: spec-literal-qname-to-code-mapping

- lane_id: lane-canonical-model
  name: Canonical Model
  purpose: Implement spec-shaped internal model types (Model/ subdirs, spec/ packages)
  permitted_writes: [src/net/*/Model/**, src/python/**/spec/**, src/python/**/models.py,
                     tests/**, .local/evidences/**]
  required_skill: add-dotnet-object-model-feature

- lane_id: lane-parser-realignment
  name: Parser Realignment
  purpose: Align parsers to populate canonical model types, not raw dicts or live DOM mutations
  permitted_writes: [src/net/*/Parsing/**, src/python/**/*_parser.py,
                     src/python/**/*_codec.py, tests/**, .local/evidences/**]

- lane_id: lane-writer-realignment
  name: Writer Realignment
  purpose: Align writers to serialize from canonical model, not raw dicts
  permitted_writes: [src/net/*/Writing/**, src/python/**/*_writer.py,
                     src/python/**/*_codec.py, tests/**, .local/evidences/**]

- lane_id: lane-public-api-facade
  name: Public API Facade
  purpose: Build Aspose-style facade over QName model; implement collection/child hierarchy
  permitted_writes: [src/net/**, src/python/**/Compat/**, src/python/**/__init__.py,
                     registry/public-api-manifest/**, tests/**, .local/evidences/**]
  required_skill: add-dotnet-api

- lane_id: lane-promotion
  name: Promotion and Protection
  purpose: Run promote_product.py; write promotion records; track reopening; certify products
  permitted_writes: [registry/promotion-ledger.yaml, registry/public-api-manifest/**,
                     reports/architecture-audit/**, .local/evidences/**]
  forbidden_writes: [src/**]

- lane_id: lane-independent-review
  name: Independent Review
  purpose: Supervisor-level product review; architecture audit; second-run idempotency check
  permitted_writes: [reports/architecture-audit/**, .local/evidences/**]
  forbidden_writes: [src/**, registry/promotion-ledger.yaml]
```

**Part B — promote_product.py:**

A CLI tool that executes the IMPLEMENTATION_VERIFIED → PROMOTED_STABLE transition.

```
python tools/supervisor/promote_product.py \
  --format fods \
  --language python \
  --proof-bundle <path-to-zip>
```

**Steps the tool executes:**
1. Read format-registry.yaml — verify format exists and human_gate1_approved=true
2. Read promotion-ledger.yaml — verify current state=IMPLEMENTATION_VERIFIED (not DRAFT or REOPENED)
3. Read `reports/architecture-audit/{format}_{lang}.json` — verify classification is COMPLIANT or
   MINOR_REALIGNMENT (FAIL if file doesn't exist — must run architecture_audit.py first)
4. Read `registry/public-api-manifest/{format}_{lang}.yaml` — verify it exists and has ≥1 entry
5. Run oracle: `python tools/supervisor/execute_oracle.py {format}` — verify all cases PASS
6. Compute api_baseline_hash: SHA-256 of JSON-sorted `__all__` from `src/python/{f}/__init__.py`
   (or for .NET: sorted list of public method names from the root document class)
7. Write promotion-ledger.yaml entry:
   ```yaml
   - format_id: fods
     language: python
     state: PROMOTED_STABLE
     api_baseline_hash: "<sha256>"
     api_symbol_count: <n>
     promoted_files: [<list from __init__.py imports>]
     proof_bundle: <path>
     last_verified_date: "<today>"
   ```
8. Print: "PROMOTED_STABLE: fods/python. Protected files: [N files listed]"
9. Print: "V119 is now active for these files. Any change will trigger REOPENED state."

**Error conditions (all FAIL fast, no partial writes):**
- Architecture audit JSON missing → "Run: python tools/review/architecture_audit.py first"
- Classification is FULL_REBUILD or PUBLIC_FACADE_REPAIR → "Promote blocked: {classification}. Resolve before promoting."
- Oracle has failing cases → "Oracle FAIL: promote blocked"
- No public-api-manifest entry → "Manifest missing: create registry/public-api-manifest/{f}_{l}.yaml first"
- State is REOPENED → "Format is REOPENED. Resolve the hash mismatch (run: git diff {promoted_files}) before re-promoting."

**Atomicity:** Write to a temp file, then rename. Never leave promotion-ledger.yaml in a partial state.

**Tradeoff acknowledged:** Running promote_product.py for FODS/Python activates V119. This means any
subsequent change to `src/python/fods/__init__.py` (or any promoted_file) will auto-trigger REOPENED
in the next `autonomous_cycle.py` run. This is correct behavior but requires developers to be aware
that FODS promoted files cannot be silently modified. The tool explicitly prints the list of now-protected
files to prevent confusion.

---

### TC-B05: Architecture Counters (Live, Derived, Not Static)
**Status:** OPEN (depends on TC-B01)
**Lane:** layer_governance
**File created:** `tools/supervisor/architecture_counters.py`

**Core insight:** Static JSON goes stale after the next commit. The 23 counters from Section 13 must
be computed from live registry state, not written once.

**How each counter is computed:**

| Counter | Source | Method |
|---------|--------|--------|
| EXISTING_PRODUCTS_NOT_AUDITED | format-registry.yaml + reports/architecture-audit/ | count formats with no audit JSON, or audit JSON >7 days old |
| SUPPORTED_QNAMES_WITHOUT_MODEL_TYPES | shared/qname-registry/*.yaml | count entries where python_file is null or file doesn't exist |
| MODEL_TYPES_WITHOUT_SPEC_AUTHORITY | Same registry | count entries where spec_fact_ref is null or not in SAL facts |
| PUBLIC_APIS_WITHOUT_QNAME_MAPPING | registry/public-api-manifest/*.yaml | count symbols with no matching qname entry |
| PUBLIC_APIS_WITHOUT_MODEL_DELEGATION | Same manifest | count symbols where canonical_model_type is null |
| GETTERS_WITHOUT_PARSER_PATH | Same manifest | count symbols where parser_path is null |
| SETTERS_WITHOUT_WRITER_PATH | Same manifest | count symbols where writer_path is null |
| PERSISTENT_FEATURES_WITHOUT_ROUNDTRIP | Same manifest | count symbols where roundtrip_test is null |
| DETACHED_PERSISTENT_STATE_STORES | Last governance_validator_runner output | count V108/V116 violations |
| WRONG_ROOT_TYPE_OWNERSHIP | Last governance_validator_runner output | count V113/V74 violations |
| FILES_OUTSIDE_QNAME_LAYOUT | Last governance_validator_runner output | count V109/V126 violations |
| TYPES_OUTSIDE_QNAME_HIERARCHY | Last governance_validator_runner output | count V127 violations |
| DUMPING_GROUND_FILES | architecture_audit JSONs | count violations of no_dumping_ground criterion |
| TEST_ONLY_OR_SPECULATIVE_APIS | Last governance_validator_runner output | count V107 violations |
| PUBLIC_APIS_WITHOUT_TRACEABILITY | registry/public-api-manifest/*.yaml | count symbols with no spec_fact_ids |
| PUBLIC_APIS_WITH_FALSE_OR_MISSING_DOCS | Last governance_validator_runner output | count V121 violations |
| UNGOVERNED_CODE_MARKERS | Last governance_validator_runner output | count V123 violations |
| CODE_CHANGES_WITHOUT_FILE_OWNERSHIP | governance_validator_runner output | count V88 violations |
| CODE_CHANGES_WITHOUT_FINAL_DIFF_REVIEW | (advisory — always 0 until enforcement added) | 0 |
| PROMOTED_CODE_CHANGED_WITHOUT_REOPENING | promotion-ledger.yaml | count entries with state=REOPENED |
| NEW_PRODUCTS_BYPASSING_ARCHITECTURE_GATE | format-registry.yaml | count formats with human_gate1_approved=true but no audit JSON |
| FAILED_REQUIRED_PILOTS | architecture_audit JSONs | count pilot formats where classification ≠ COMPLIANT after two runs |
| MATERIAL_SECOND_RUN_CHANGES | architecture_audit JSONs | count formats where run N vs run N-1 differ materially (different classification) |

**Output:** `reports/architecture-audit/completion-counters.json`
Called from sprint closeout as a best-effort step (like build_declaration_review_package.py).
If it fails, log and continue.

**Staleness warning:** If any governance_validator_runner output is >7 days old, WARN in output.

---

## Track C — Product Audit (runs after TC-B01 tool is built)

---

### TC-C01: Run Architecture Audit on All 30 Formats
**Status:** OPEN (depends on TC-B01)
**Lane:** lane-independent-review

Execute:
```
python tools/review/architecture_audit.py --all
```

This produces 30 JSON files (20 Python + 10 .NET) in `reports/architecture-audit/`.

**Expected classifications (pre-confirmed by exploration):**

| Format | Language | Expected Classification | Key Evidence |
|--------|----------|------------------------|--------------|
| fods | python | COMPLIANT | Full spec/, facade_names, models.py correct |
| fodt | python | COMPLIANT or MINOR_REALIGNMENT | Has spec/, models.py (verify Compat/ delegates) |
| ods | python | MINOR_REALIGNMENT | Has spec/, verify parser imports |
| csv | python | MINOR_REALIGNMENT | models.py has spec_qname; verify Compat/ |
| tsv | python | MINOR_REALIGNMENT | Same as csv |
| sylk | python | MINOR_REALIGNMENT | Has spec/ (verify) |
| dif | python | MINOR_REALIGNMENT | Has spec/ (verify) |
| abw | python | PUBLIC_FACADE_REPAIR or MINOR_REALIGNMENT | Needs verification |
| gnumeric | python | MINOR_REALIGNMENT | Has spec/ (verify) |
| ndjson | python | MINOR_REALIGNMENT | Has spec/ |
| toml | python | MINOR_REALIGNMENT | Has spec/ |
| fodg | python | MINOR_REALIGNMENT | Has spec/ |
| fodp | python | MINOR_REALIGNMENT | Has spec/ |
| odt | python | MINOR_REALIGNMENT | Has spec/ |
| xcf | python | MINOR_REALIGNMENT | Has spec/ (verify) |
| zst | python | MINOR_REALIGNMENT | Has spec/ |
| pbm/pgm/ppm | python | MINOR_REALIGNMENT | Has spec/ |
| qoi | python | MINOR_REALIGNMENT | Has spec/ |
| fods | dotnet | MINOR_REALIGNMENT | Model/ + Spec/ present; FodsDocument.cs 907 LOC (over cap) |
| fodt | dotnet | MINOR_REALIGNMENT | Model/ + Spec/ present; no *ExtendedApis.cs found |
| csv | dotnet | PUBLIC_FACADE_REPAIR | No Model/ dir; minimal Spec/ |
| ndjson | dotnet | PUBLIC_FACADE_REPAIR (verify) | Needs inspection |
| netpbm | dotnet | MINOR_REALIGNMENT | Has Model/ (verify) |
| tsv | dotnet | PUBLIC_FACADE_REPAIR (verify) | Has Spec/ only |
| html | dotnet | FULL_REBUILD | Single file |
| markdown | dotnet | FULL_REBUILD | Single file |
| txt | dotnet | FULL_REBUILD | Single file |
| zst | dotnet | PUBLIC_FACADE_REPAIR | Has Exceptions/ only |

**If actual classification differs from expected:** The audit tool is correct; the expectation is wrong.
Update the table in this plan — do not modify the tool to produce expected results.

---

### TC-C02: Produce Architecture Gap Register
**Status:** OPEN (depends on TC-C01)
**Lane:** lane-independent-review
**File created:** `reports/architecture-audit/architecture-gap-register.json`

After the 30 audit JSONs exist, call `architecture_counters.py` to compute all 23 counters.
Then produce the gap register: one entry per format×violation (not per-counter — per actual violation
found in the audit criteria).

Each gap entry:
```json
{
  "gap_id": "ARCH-GAP-NET-HTML-001",
  "product": "html",
  "language": "dotnet",
  "classification": "FULL_REBUILD",
  "violation": "FILES_OUTSIDE_QNAME_LAYOUT",
  "file": "src/net/html/HtmlDocument.cs",
  "description": "Single-file format with no QName model, no Model/ dir, no Spec/ dir",
  "counter": "FILES_OUTSIDE_QNAME_LAYOUT",
  "governed_lane": "lane-canonical-model",
  "priority": "MEDIUM",
  "remediation": "New format kickstart with /new-format-kickstart after pilot completes"
}
```

**Priority assignment:**
- CRITICAL: FULL_REBUILD formats with active product work in next-sprint.md
- HIGH: QNAME_MODEL_DECOMPOSITION or PARSER_WRITER_REALIGNMENT
- MEDIUM: PUBLIC_FACADE_REPAIR
- LOW: MINOR_REALIGNMENT (already on a healing path)

---

## Files Summary

### Created
- `tools/review/architecture_audit.py` (≤300 LOC, Python, standalone)
- `tools/supervisor/promote_product.py` (≤200 LOC, Python, CLI)
- `tools/supervisor/architecture_counters.py` (≤200 LOC, Python, derives 23 counters)
- `tools/supervisor/governance_validators_arch_api.py` (V150, V151, V152)
- `registry/public-api-manifest/fods_python.yaml` (FODS pilot — ~30 symbol entries)
- `registry/public-api-manifest/fods_dotnet.yaml` (FODS pilot — ~40 symbol entries)
- `.supervisor/schemas/public-api-manifest.schema.json`
- `.supervisor/schemas/promotion-record.schema.json`
- `registry/public-api-manifest/.gitkeep`
- `reports/architecture-audit/.gitkeep`
- `reports/architecture-audit/architecture-gap-register.json` (after TC-C02)
- `reports/architecture-audit/completion-counters.json` (after TC-C02)

### Modified
- `registry/lane-scope-registry.yaml` — 7 new lanes (total 12)
- `tools/supervisor/governance_validator_runner.py` — import V150-V152, expected_count 167 → 170
- `tests/supervisor/test_governance_validators.py` — update assertion to 170

### Not modified (intentional)
- `registry/promotion-ledger.yaml` — will be written by `promote_product.py` at TC-B04 pilot time,
  not by this plan directly
- Any existing validator files — V150-V152 are additive only

---

## Execution Order

```
TC-B01 (architecture_audit.py)         — no dependencies
  └─ TC-C01 (run audit --all)          — needs TC-B01 tool
TC-B02 (FODS manifests)                — no code dependencies; reads existing source
TC-B03 (3 validators V150-V152)        — needs TC-B01 and TC-B02 to exist (manifests + audit JSONs)
TC-B04 (lanes + promote_product.py)    — no dependencies; pure new files
TC-B05 (architecture_counters.py)      — needs TC-B01 (audit JSONs as input)
  └─ TC-C02 (gap register + counters)  — needs TC-C01 (all 30 JSONs exist) + TC-B05 (tool built)
```

---

## Verification

**After TC-B01 (architecture_audit.py):**
```bash
python tools/review/architecture_audit.py --format fods --language python
# Must produce reports/architecture-audit/fods_python.json
# Must classify COMPLIANT
# Second run: diff output — must be identical (idempotency)
python tools/review/architecture_audit.py --all
# Must produce 30 JSON files without errors
```

**After TC-B02 (FODS manifest):**
```bash
python -c "import yaml; m=yaml.safe_load(open('registry/public-api-manifest/fods_python.yaml')); print(len(m),'entries')"
# Count must be ≥ 20 (one per __all__ export)
# Each entry must have public_symbol, qname, parser_path, writer_path
```

**After TC-B03 (validators):**
```bash
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -x
# Must pass with updated assertion: assert len(validators) == 170
python tools/supervisor/governance_validator_runner.py --dry-run
# Must print expected_count=170, no import errors
```

**After TC-B04 (promote_product.py):**
```bash
python tools/supervisor/promote_product.py --format fods --language python --proof-bundle test
# Before audit + manifest exist: must FAIL with clear error message
# After audit + manifest exist: must succeed, write promotion-ledger.yaml entry
python tools/supervisor/promote_product.py --format fods --language python --proof-bundle test
# Second run: must detect state=PROMOTED_STABLE and print "already promoted"
```

**After TC-B05 (architecture_counters.py):**
```bash
python tools/supervisor/architecture_counters.py
# Must produce reports/architecture-audit/completion-counters.json
# EXISTING_PRODUCTS_NOT_AUDITED must equal 0 after TC-C01
# PROMOTED_CODE_CHANGED_WITHOUT_REOPENING must equal 0 initially
```

**After TC-C02 (gap register):**
```bash
python -c "import json; g=json.load(open('reports/architecture-audit/architecture-gap-register.json')); print(len(g['gaps']),'gaps')"
# Must have at least 1 gap (html FULL_REBUILD is guaranteed)
# Must have no gaps for COMPLIANT formats (fods/python should have 0 gaps)
```

---

## Tradeoffs and Risks

**1. promote_product.py activates V119 for FODS files.**
When promote_product.py is first run for fods/python, every file in promoted_files becomes
protected. Any subsequent modification to `src/python/fods/__init__.py` will auto-trigger REOPENED
in autonomous_cycle.py. This is correct per the spec — but it means the FODS sprint work that
touches __init__.py (API additions) will cycle through REOPENED→re-promote on each significant change.
Mitigation: Only run promote_product.py at explicit format stabilization points, not after every sprint.

**2. Architecture audit tool at 300 LOC cap.**
Python audit criteria require AST parse (ast.parse) + file existence checks. .NET criteria require
grep + path traversal. The tool can stay under 300 LOC if criteria are implemented as a flat function
per criterion (no classes). If it exceeds 300 LOC, split into `architecture_audit_python.py` and
`architecture_audit_dotnet.py` with a thin dispatch script.

**3. FODS manifest will have ~30-40 entries — all must be hand-authored.**
There is no tool to auto-generate the manifest from source. Derive entries from:
- `src/python/fods/__init__.py` `__all__` list (method names)
- `shared/qname-registry/fods.yaml` (qname + facade_names cross-reference)
- `src/python/fods/fods_codec.py` and `fods_writer.py` (parser_path, writer_path)
This takes effort but is a one-time cost per format. The manifest is then maintained alongside source.

**4. Counters derived from governance_validator_runner last-run output are stale by definition.**
The runner output is not persisted between sprints unless autonomous_cycle.py writes it. Some counters
(DETACHED_PERSISTENT_STATE_STORES, WRONG_ROOT_TYPE_OWNERSHIP, etc.) depend on the runner's last
violation report. If the runner hasn't run recently, these counters show 0 (optimistic, not accurate).
Mitigation: architecture_counters.py emits a staleness warning if runner output is >7 days old.
WARN does not block the sprint.

**5. V151 (architecture_audit_regression) requires audit JSON to exist before it can fire.**
For formats that haven't been audited yet, V151 is silent (WARN only). This means the validator
doesn't protect formats that were never audited. Mitigation: V152 separately blocks RELEASE_GATE
claims. The combination ensures that formats cannot claim release-gate status without an audit,
even if V151 hasn't fired yet.

**6. Lane enforcement remains prompt-only.**
Adding 7 lanes to lane-scope-registry.yaml does not add write-time code enforcement — the existing
on_out_of_scope_discovery pattern is agent-prompt-based. Runtime enforcement (file-system hooks or
CI-level scope guards) is a deeper infrastructure change outside this plan's scope. The lanes define
the correct ownership structure; enforcement escalates to CI in a future lane.

---

## What This Plan Does NOT Do (Explicitly Out of Scope)

- Does not implement the Section 9 pilot beyond FODS manifests (the full 12-proof pilot is a
  separate plan that depends on this one being complete)
- Does not migrate any format to FULL_REBUILD or QNAME_MODEL_DECOMPOSITION classification
  (audit identifies; migration is a separate sprint per format)
- Does not add runtime write-time lane enforcement (prompt-only remains for now)
- Does not add the PRODUCT_ARCHITECTURE_READY gate to format-registry.yaml as a blocking field
  (added as informational field only; blocking enforcement is the next plan after pilot completes)
- Does not increase expected_count beyond 170 (V150-V152 only; future validators wait for these
  to be exercised first)
