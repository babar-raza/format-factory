# Format-Generic Skill System Audit

**Date:** 2026-05-20
**Sprint:** R33 Lane H -- Skill System Format Genericity Audit
**Scope:** `tools/skills/` (20 .py source files, 3 command files) + `tests/skills/` (21 test files, 2 fixture files)
**Verdict:** LANE_H_PASS_WITH_FOLLOWUP_PLAN

---

## 1. Summary

The skill system was built during the FODS/FODT commercial sprint era (R4-R12) when only two formats were in scope. It contains **66 FODS/FODT references across 20 source files** and **768 references across 21 test files**. However, the core resolver logic (`format_context_resolver.py`) is already format-generic in its data path -- it reads from `generated-requirements/{fmt}/` and `registry/format-registry.yaml` without format-specific branching. The hardcoding is concentrated in three patterns: (a) CLI default/all-expansion lists, (b) FODT-specific constraint injection, and (c) test fixture data.

No file in the skill system claims broad format genericity that it cannot deliver. The `commercial_sprint.py` command explicitly rejects unknown formats with a hardcoded allowlist (`fods`, `fodt`), which is honest but non-extensible.

---

## 2. All FODS/FODT Hardcoded References -- Classification

### 2.1 Category: HARDCODED_ALL_EXPANSION (CLI "all" defaults to `["fods", "fodt"]`)

These are the highest-priority defects. When a user passes `--format all`, the system only iterates FODS and FODT instead of discovering formats from the registry.

| File | Line(s) | Pattern | Classification |
|------|---------|---------|----------------|
| `tools/skills/commands/format_context.py` | 32 | `["fods", "fodt"] if parsed.format == "all"` | FORMAT_GENERIC_DEFECT |
| `tools/skills/commands/lane_select.py` | 32 | `["fods", "fodt"] if parsed.format == "all"` | FORMAT_GENERIC_DEFECT |
| `tools/skills/format_context_resolver.py` | 339, 344 | CLI `--format all` defaults to `["fods", "fodt"]` | FORMAT_GENERIC_DEFECT |
| `tools/skills/lane_selector.py` | 338, 342 | CLI `--format all` defaults to `["fods", "fodt"]` | FORMAT_GENERIC_DEFECT |
| `tools/skills/stale_detection.py` | 339 | `["fods", "fodt"] if args.format == "all"` | FORMAT_GENERIC_DEFECT |
| `tools/skills/replay_fingerprint.py` | 249 | `["fods", "fodt"] if args.format == "all"` | FORMAT_GENERIC_DEFECT |
| `tools/skills/implementation_plan_expander.py` | 402 | `["fods", "fodt"] if args.format == "all"` | FORMAT_GENERIC_DEFECT |
| `tools/skills/stale_propagation.py` | 328, 335 | `["fods", "fodt"]` default | FORMAT_GENERIC_DEFECT |
| `tools/skills/execution_simulator.py` | 379, 392 | `["fods", "fodt"]` default | FORMAT_GENERIC_DEFECT |
| `tools/skills/planning_bundle_runtime.py` | 64, 91 | `["fods", "fodt"]` default | FORMAT_GENERIC_DEFECT |
| `tools/skills/multi_format_planning.py` | 37 | `SUPPORTED_FORMATS = ["fods", "fodt"]` | FORMAT_GENERIC_DEFECT |
| `tools/skills/authority_continuity_registry.py` | 237 | `for fmt in ["fods", "fodt"]` | FORMAT_GENERIC_DEFECT |

**Count: 12 files, ~18 occurrences**

### 2.2 Category: HARDCODED_ALLOWLIST (explicit format rejection)

| File | Line(s) | Pattern | Classification |
|------|---------|---------|----------------|
| `tools/skills/commands/commercial_sprint.py` | 39, 52-53 | `help="Format ID (fods, fodt)"` + `if fmt not in ("fods", "fodt")` | FORMAT_GENERIC_DEFECT |
| `tools/skills/commercial_sprint_dryrun.py` | 267, 274 | `help="Format ID (fods, fodt)"` + `["fods", "fodt"] if ... == "all"` | FORMAT_GENERIC_DEFECT |

**Count: 2 files, ~5 occurrences**

### 2.3 Category: FODT_SPECIFIC_CONSTRAINT_LOGIC (FODT-REQ-040 injection)

These are format-specific business rules that correctly apply only to FODT. They should be refactored to be data-driven (constraints from verifier-review.yaml) but are not incorrect.

| File | Line(s) | Pattern | Classification |
|------|---------|---------|----------------|
| `tools/skills/swarm_prompt_generator.py` | 223-231, 310, 341 | `if fmt == "fodt"` constraint injection, `FODT-REQ-040` text | INTENTIONAL_DEFAULT |
| `tools/skills/implementation_plan_expander.py` | 33-35 | Docstring: `FODT-REQ-040 (iterative traversal, no recursion)` | INTENTIONAL_DEFAULT |

**Count: 2 files, ~10 occurrences**

### 2.4 Category: DOCSTRING_AND_HELP_TEXT (informational, not logic)

| File | Line(s) | Pattern | Classification |
|------|---------|---------|----------------|
| `tools/skills/acquisition_lifecycle_simulator.py` | 8, 150 | Docstring: `active formats (FODS, FODT)` and `e.g. 'fods'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/authority_continuity_registry.py` | 78 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/commercial_sprint_dryrun.py` | 70 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/execution_simulator.py` | 209 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/implementation_plan_expander.py` | 253 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/lane_selector.py` | 319 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/multi_format_planning.py` | 12 | `FODS, FODT (current)` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/replay_fingerprint.py` | 119 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/replay_lineage.py` | 89, 332 | `e.g. 'fods', 'fodt'`, default `fods` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/stale_detection.py` | 184 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/stale_propagation.py` | 195 | `e.g. 'fods', 'fodt'` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/swarm_prompt_generator.py` | 155, 157, 453-454 | `e.g. 'fods', 'fodt'`, help text | GOLDEN_REFERENCE_ALLOWED |

**Count: 12 files, ~15 occurrences**

### 2.5 Category: DATA_REGISTRY_ENTRIES (backlog/group definitions with FODS/FODT as data)

| File | Line(s) | Pattern | Classification |
|------|---------|---------|----------------|
| `tools/skills/acquisition_lifecycle_simulator.py` | 387-397 | `"fods": { ... }`, `"fodt": { ... }` in hardcoded data table | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/candidate_format_backlog.py` | 242-254 | FODS/FODT entries in candidate backlog data | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/multi_format_acquisition_planner.py` | 54-55, 111-112 | `GROUP_ACTIVE_FORMATS` with `["fods", "fodt"]` | GOLDEN_REFERENCE_ALLOWED |
| `tools/skills/implementation_simulation_v2.py` | 562, 565-566 | FODS/FODT in standard simulation format set | GOLDEN_REFERENCE_ALLOWED |

**Count: 4 files, ~10 occurrences**

### 2.6 Category: TEST_FIXTURES (FODS/FODT used as test data)

| File | Count | Classification |
|------|-------|----------------|
| `tests/skills/fixtures/fods-sprint-prompt.md` | ~50 | TEST_FIXTURE_ALLOWED |
| `tests/skills/fixtures/fodt-sprint-prompt.md` | ~80 | TEST_FIXTURE_ALLOWED |
| `tests/skills/test_format_context_resolver.py` | 54 | TEST_FIXTURE_ALLOWED |
| `tests/skills/test_authority_continuity_registry.py` | 117 | TEST_FIXTURE_ALLOWED |
| `tests/skills/test_execution_simulator.py` | 73 | TEST_FIXTURE_ALLOWED |
| `tests/skills/test_implementation_simulation_v2.py` | 73 | TEST_FIXTURE_ALLOWED |
| All other 17 test files | ~321 | TEST_FIXTURE_ALLOWED |

**Count: 21 test files + 2 fixture files, ~768 occurrences total**

---

## 3. Genericity Claims vs Reality

### 3.1 What the Skill System Claims

- `multi_format_planning.py` docstring: "Designed for extensibility: HWP/HWPX, ALZ/EGG, public-spec formats" -- **accurate but not yet delivered**
- `acquisition_lifecycle_simulator.py` docstring: "Simulate the complete format acquisition lifecycle for any format" -- **partially true**: the function signature accepts any format string, but the embedded data table only has FODS/FODT entries
- `commercial_sprint.py` command: `help="Format ID (fods, fodt)"` -- **honest limitation**
- `format_context_resolver.py` core logic: **genuinely format-generic** (reads `generated-requirements/{fmt}/` for any `fmt`)

### 3.2 Honest Limitation Reporting

The skill system **does NOT overclaim genericity**. The `commercial_sprint.py` command explicitly rejects non-FODS/FODT formats. The `multi_format_planning.py` sets `SUPPORTED_FORMATS = ["fods", "fodt"]` as a constant. These are honest about the current scope.

### 3.3 Latent Genericity (Already Present)

The following components accept arbitrary format strings and would work for any format that has the expected file structure:

- `format_context_resolver.resolve_format_context(fmt)` -- reads from `generated-requirements/{fmt}/` and registry
- `_resolve_gate_state(fmt)` -- reads from `registry/format-registry.yaml` by `format_id`
- `_collect_known_constraints(fmt)` -- reads from `generated-requirements/{fmt}/verifier-review.yaml`
- `lane_selector.select_lanes_for_format(fmt)` -- delegates to resolver
- `stale_detection.detect_stale_state(fmt)` -- delegates to resolver
- `implementation_plan_expander.expand_implementation_plan(fmt)` -- reads from `generated-requirements/{fmt}/`

---

## 4. Risk Assessment

| Risk | Severity | Description |
|------|----------|-------------|
| Silent omission | MEDIUM | When `--format all` is used, new formats (ODS, ODT, QOI, etc.) are silently excluded |
| Allowlist gate | LOW | `commercial_sprint.py` rejects non-FODS/FODT formats; prevents accidental misuse but blocks expansion |
| FODT constraint coupling | LOW | FODT-REQ-040 is hardcoded in prompt generator; new format-specific constraints would need code changes |
| Test coverage gap | LOW | No tests verify the system works for non-FODS/FODT formats passed as arguments |

---

## 5. Verdict

**LANE_H_PASS_WITH_FOLLOWUP_PLAN**

Rationale:
1. The skill system does not overclaim genericity -- it honestly limits itself to FODS/FODT
2. The core resolver layer is already format-generic by design
3. The hardcoding is concentrated in CLI defaults and expansion lists, which are straightforward to refactor
4. The FODT-specific constraint logic is intentional and correct for its purpose
5. Test fixtures using FODS/FODT as data are appropriate and do not need removal
6. A concrete hardening plan is provided in the companion document

The system is **guarded** (it does not silently produce wrong results for new formats) but **not yet generic** (it cannot serve the 20+ formats now in the pipeline without code changes).
