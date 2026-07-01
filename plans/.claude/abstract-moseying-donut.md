# Plan: Drivers Subsystem — Reconcile Governance, Define Language Scope, Harden Templates, Build Format-Test Promotion, Prove Pilots, and Enforce Idempotency

plan_type: machinery_hardening
mission_id: DRIVERS-SUBSYSTEM-HEALING-001
created: 2026-07-01

---

## Context

The `drivers/` subsystem provides 5 `.py.tmpl` test scaffold templates consumed by `test_drivers.py` and `product_feature_factory.py`. Despite active consumers and 30 passing tests, the subsystem suffers from:

1. A **stale governance plan** (`idempotent-snuggling-wombat.md`) that incorrectly claims "zero tool references" and proposes deleting `drivers/` — contradicted by two proven direct consumers.
2. A **registry consumer list** that omits `product_feature_factory.py` (direct consumer).
3. **Implicit Python-only scope** with no machine-readable policy.
4. **Weak template assertions** (`result is not None`, `isinstance(result, object)`) with no placeholder enforcement.
5. **No format-test promotion lifecycle** — scaffolds are generated but never governed from SCAFFOLD → MAINTAINED.
6. **No machine-readable template/renderer contracts** or drift validators.
7. **No consumer graph report** or formal classification of reference types.

The mission is to correct all contradictions, define the language model, harden contracts, implement the promotion lifecycle, run 8 required pilots, and prove idempotency.

---

## Critical Files

| File | Role |
|---|---|
| [drivers/_readme.md](drivers/_readme.md) | Subsystem README — needs consumer/language/promotion update |
| [drivers/python/*.py.tmpl](drivers/python/) | 5 template files — need placeholder hardening |
| [tools/supervisor/test_drivers.py](tools/supervisor/test_drivers.py) | Primary template loader — needs contracts + language policy |
| [tools/supervisor/product_feature_factory.py](tools/supervisor/product_feature_factory.py) | Secondary consumer — needs provenance emission + promotion task creation |
| [tools/supervisor/libforge_pattern_registry.py](tools/supervisor/libforge_pattern_registry.py) | Metadata reference — needs consumer classification update |
| [tests/supervisor/test_test_drivers.py](tests/supervisor/test_test_drivers.py) | Test suite — needs contract/policy/drift coverage added |
| [plans/.claude/idempotent-snuggling-wombat.md](plans/.claude/idempotent-snuggling-wombat.md) | Stale plan — delete claim must be corrected |
| [registry/repository-root-folders.yaml](registry/repository-root-folders.yaml) | Registry — consumer list incomplete |
| [plans/layers/test-infrastructure-layer.md](plans/layers/test-infrastructure-layer.md) | Layer L07 — driver ownership must be recorded |

---

## Taskcard Status Table

| TC-ID | Title | Status |
|---|---|---|
| TC-DRV-001 | Phase 1: Status inventory + finding verification | CLOSED |
| TC-DRV-002 | Phase 2: Governance contradiction reconciliation | CLOSED |
| TC-DRV-003 | Phase 3: Real consumer graph | CLOSED |
| TC-DRV-004 | Phase 4: Language scope decision (PYTHON_ONLY_BY_DESIGN) | CLOSED |
| TC-DRV-005 | Phase 5: Driver/template/renderer contracts + drift validators | CLOSED |
| TC-DRV-006 | Phase 6: Placeholder + test-quality hardening | CLOSED |
| TC-DRV-007 | Phase 7: Pattern-to-format-test promotion lifecycle | CLOSED |
| TC-DRV-008 | Phase 8: FeatureFactory + test_drivers integration repair | CLOSED |
| TC-DRV-009 | Phase 9+10: Fixture/assertion contracts + governance/README repair | CLOSED |
| TC-DRV-010 | Phase 11: Existing generated-test audit | CLOSED |
| TC-DRV-011 | Phase 12: Eight required pilots | CLOSED |
| TC-DRV-012 | Final validation, idempotency proof, closeout | CLOSED |

---

## TC-DRV-001 — Phase 1: Status Inventory + Finding Verification

**Goal:** Verify each supplied finding against current code. Produce `reports/drivers/drivers-finding-validation.yaml`.

**Findings to verify:**

| Finding ID | Claim | Expected Verdict |
|---|---|---|
| F-001 | Stale plan says drivers/ has no consumers and should be deleted | REFUTED — 2 direct consumers proven |
| F-002 | Root-folder registry places drivers/ under misleading deleted/consolidated section | VERIFY exact heading |
| F-003 | test_drivers.py hardcodes `drivers/python` | CONFIRMED (line 14) |
| F-004 | Language scope is implicit; no Python-only policy exists | CONFIRMED |
| F-005 | No governed lifecycle promotes templates into tests/{language}/{format} | CONFIRMED |
| F-006 | Templates contain weak placeholders (None, b"", TODO, compile-only assertions) | CONFIRM per template |
| F-007 | Consumer docs may incorrectly describe indirect refs as direct consumers | VERIFY registry vs actual |
| F-008 | No broad renderer/template argument drift guard exists | CONFIRM |

**Actions:**
- Run `cat` / Read each critical file to confirm each finding
- Produce `reports/drivers/drivers-finding-validation.yaml` with per-finding verdict, evidence, severity, systemic flag, required_action
- Create `reports/drivers/` directory

**Completion gate:** File exists with all 8 findings classified.

---

## TC-DRV-002 — Phase 2: Governance Contradiction Reconciliation

**Goal:** Correct all governance contradictions. UNRESOLVED_DRIVERS_GOVERNANCE_CONTRADICTIONS = 0.

**Actions:**
1. **Fix `plans/.claude/idempotent-snuggling-wombat.md`**: Add a correction note to TC-ROOT-002 that the "zero consumers → DELETE" finding was incorrect. Document both proven direct consumers. Do NOT delete the historical context — mark it as `superseded_by_evidence`.
2. **Fix `registry/repository-root-folders.yaml`**: Add `tools/supervisor/product_feature_factory.py` to the consumers list for `drivers/`. Verify the retention heading is RETAIN (not deleted/consolidated).
3. **Fix `drivers/_readme.md`**: Update consumer list to include all 3 consumers with classification (DIRECT/METADATA). Update purpose statement to match actual role.
4. **Update `plans/layers/test-infrastructure-layer.md`**: Add `drivers/` as owned subsystem under L07 scope.

**Produce:** `reports/drivers/drivers-governance-contradictions.yaml` listing each contradiction, what was wrong, what was corrected, evidence path.

**Completion gate:** All 4 corrections applied. YAML report exists.

---

## TC-DRV-003 — Phase 3: Real Consumer Graph

**Goal:** Prove every consumer classification with code evidence. FALSE_DIRECT_CONSUMER_CLAIMS = 0.

**Consumer classifications:**

| File | Classification | Evidence |
|---|---|---|
| `tools/supervisor/test_drivers.py` | DIRECT_RUNTIME_CONSUMER | `_DRIVERS_DIR / "python"` + `_load_template()` reads `.tmpl` files |
| `tools/supervisor/product_feature_factory.py` | DIRECT_RUNTIME_CONSUMER | Imports all 5 `render_*` functions, calls them at runtime |
| `tests/supervisor/test_test_drivers.py` | TEST_ONLY_CONSUMER | Imports render functions; only executed in test context |
| `tests/supervisor/test_product_feature_factory.py` | TEST_ONLY_CONSUMER | Tests FeatureFactory which uses drivers indirectly |
| `tools/supervisor/libforge_pattern_registry.py` | DECLARATIVE_REFERENCE | PatternRecord documents test_drivers.py but no runtime coupling |
| `registry/repository-root-folders.yaml` | DECLARATIVE_REFERENCE | Lists consumers as metadata only |
| `compose_verify_loop.py` | DOCUMENTATION_REFERENCE | Docstring mention, no import or runtime call |

**Actions:**
- For each consumer: paste exact code evidence (line numbers, import/call statements)
- Verify no files claim direct access to `drivers/python/*.py.tmpl` except `test_drivers.py`
- Produce `reports/drivers/drivers-consumer-graph.yaml`

**Completion gate:** YAML report with all consumers classified. Zero false claims.

---

## TC-DRV-004 — Phase 4: Language Scope Decision

**Goal:** Eliminate implicit language scope. IMPLICIT_LANGUAGE_SCOPE = 0.

**Selected model: PYTHON_ONLY_BY_DESIGN**

Rationale: Only Python templates exist. Only Python consumers exist. No .NET driver infrastructure. No plan to add other languages in current sprints. Explicit rejection is cleaner than an extension registry for a currently single-language system.

**Actions:**
1. Add module-level docstring to `test_drivers.py`: "Language: Python only. This driver explicitly supports Python test generation. For other languages, a new driver module must be registered."
2. Add `_SUPPORTED_LANGUAGE = "python"` constant to `test_drivers.py`.
3. Add `_validate_language(lang: str)` helper that raises `ValueError` with clear message if lang != "python".
4. Add 2 tests in `test_test_drivers.py`: unsupported language rejection, and Python accepted.
5. Update `drivers/_readme.md` §Language with explicit PYTHON_ONLY_BY_DESIGN declaration.
6. Produce `reports/drivers/driver-language-decision.yaml` with decision, rationale, enforcement evidence.

**Completion gate:** YAML decision file. Tests pass. No implicit scope remains.

---

## TC-DRV-005 — Phase 5: Driver, Template, and Renderer Contracts

**Goal:** Machine-readable contracts for all templates and renderers. ACTIVE_TEMPLATE_RENDERER_MISMATCHES = 0.

**Actions:**
1. Create `drivers/python/driver-contracts.yaml` with the following structure:

```yaml
driver_language:
  language_id: python
  status: active
  driver_root: drivers/python/
  renderer: tools/supervisor/test_drivers.py
  file_extension: .py
  test_framework: pytest
  syntax_validator: ast.parse
  test_runner: .venv/Scripts/pytest
  supported_patterns: [getter, export_csv, roundtrip, append, probe]

driver_templates:
  - template_id: getter_test
    pattern_id: A
    source_path: drivers/python/getter_test.py.tmpl
    renderer_id: render_getter_test
    required_arguments: [function_name, module, class_name, return_type_safe]
    placeholder_policy: scaffold_markers_required
    assertion_requirements: [meaningful_behavioral_assertion]
    status: active

  - template_id: export_csv_test
    pattern_id: B
    source_path: drivers/python/export_csv_test.py.tmpl
    renderer_id: render_export_csv_test
    required_arguments: [function_name, module, format_cap]
    placeholder_policy: scaffold_markers_required
    assertion_requirements: [meaningful_behavioral_assertion]
    status: active

  - template_id: roundtrip_test
    pattern_id: C
    source_path: drivers/python/roundtrip_test.py.tmpl
    renderer_id: render_roundtrip_test
    required_arguments: [format_upper, format_cap, format_name, test_import, load_function, write_function, compare_field]
    placeholder_policy: scaffold_markers_required
    assertion_requirements: [field_preservation_assertion, real_fixture_bytes]
    status: active

  - template_id: append_test
    pattern_id: D
    source_path: drivers/python/append_test.py.tmpl
    renderer_id: render_append_test
    required_arguments: [function_name, module, format_cap, collection_key]
    placeholder_policy: scaffold_markers_required
    assertion_requirements: [meaningful_behavioral_assertion]
    status: active

  - template_id: probe_test
    pattern_id: E
    source_path: drivers/python/probe_test.py.tmpl
    renderer_id: render_probe_test
    required_arguments: [function_name, module, format_cap, format_lower]
    placeholder_policy: scaffold_markers_required
    assertion_requirements: [meaningful_behavioral_assertion]
    status: active

driver_renderers:
  - renderer_id: render_getter_test
    provided_arguments: [function_name, module, class_name, return_type_safe]
  - renderer_id: render_export_csv_test
    provided_arguments: [function_name, module, format_cap]
  - renderer_id: render_roundtrip_test
    provided_arguments: [format_upper, format_cap, format_name, test_import, load_function, write_function, compare_field]
  - renderer_id: render_append_test
    provided_arguments: [function_name, module, format_cap, collection_key]
  - renderer_id: render_probe_test
    provided_arguments: [function_name, module, format_cap, format_lower]
```

2. Add `validate_template_renderer_compatibility()` function to `test_drivers.py` that:
   - Loads `drivers/python/driver-contracts.yaml`
   - For each template, checks `required_arguments == renderer_provided_arguments`
   - Raises `ContractViolationError` on mismatch

3. Add test in `test_test_drivers.py`: `TestContractValidation` — verifies compatibility passes, and fails on deliberate mismatch.

4. Produce `reports/drivers/template-renderer-compatibility.yaml`.

**Completion gate:** Contract YAML exists. Validator function works. Tests pass.

---

## TC-DRV-006 — Phase 6: Placeholder and Test-Quality Hardening

**Goal:** Replace ambiguous placeholders with machine-readable incomplete markers. FORBIDDEN_PLACEHOLDERS_IN_MAINTAINED_TESTS = 0.

**Placeholder inventory per template:**

| Template | Placeholder | Classification | Action |
|---|---|---|---|
| roundtrip_test.py.tmpl | `# TODO: provide minimal valid bytes` | FORBIDDEN_COMPLETION_PLACEHOLDER | Replace with `TEST_SCAFFOLD_INCOMPLETE` marker |
| roundtrip_test.py.tmpl | `b""` for fixture bytes | PRODUCT_FIXTURE_REQUIRED | Replace with `# FIXTURE_REQUIRED: provide real {format} bytes` |
| append_test.py.tmpl | `b""` for source bytes | PRODUCT_FIXTURE_REQUIRED | Replace with `# FIXTURE_REQUIRED: provide real {format} bytes` |
| probe_test.py.tmpl | `b""` for probe input | PRODUCT_FIXTURE_REQUIRED | Replace with `# FIXTURE_REQUIRED: provide real {format} bytes` |
| All templates | `assert result is not None` | FORBIDDEN_COMPLETION_PLACEHOLDER | Replace with `# EXPECTED_VALUE_REQUIRED: assert meaningful behavior` |
| All templates | `isinstance(result, object)` | FORBIDDEN_COMPLETION_PLACEHOLDER | Replace with `# ORACLE_REQUIRED: verify spec-derived expected value` |

**Actions:**
1. Update each `.py.tmpl` file to replace forbidden placeholders with machine-readable markers.
2. Add `scan_for_forbidden_placeholders(rendered_code: str) -> list[str]` function to `test_drivers.py` that detects: `assert result is not None`, `isinstance(result, object)`, bare `b""` as fixture, bare `None` as expected value, `pass` as test body.
3. Add `SCAFFOLD_INCOMPLETE` comment block to rendered output header: `# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED`.
4. Add `is_maintained_test(rendered_code: str) -> bool` that returns False while any forbidden marker remains.
5. Produce `reports/drivers/template-placeholder-inventory.yaml`.

**Completion gate:** No forbidden placeholders in template source. Scanner function blocks false-complete. Report exists.

---

## TC-DRV-007 — Phase 7: Pattern-to-Format-Test Promotion Lifecycle

**Goal:** Implement the SCAFFOLD → MAINTAINED lifecycle with task creation. FALSELY_COMPLETE_GENERATED_SCAFFOLDS = 0.

**Actions:**
1. Create `tools/supervisor/drivers_promotion.py` with:
   - `GeneratedTestPromotionTask` dataclass matching the contract schema (task_id, product_id, format_id, language, pattern_id, template_id, renderer_id, generated_path, target_path, incomplete_markers, required_fixtures, required_expected_values, capability_refs, gap_ids, required_assertions, required_negative_cases, status)
   - `create_promotion_task(render_result, format_id, pattern_id, ...) -> GeneratedTestPromotionTask`
   - `write_promotion_task(task: GeneratedTestPromotionTask, output_dir: Path)` — writes YAML task file
   - `scan_incomplete_markers(code: str) -> list[str]` — detects `FIXTURE_REQUIRED`, `EXPECTED_VALUE_REQUIRED`, `ORACLE_REQUIRED`, `FORMAT_ADAPTATION_REQUIRED`, `TEST_SCAFFOLD_INCOMPLETE`
   - `get_promotion_status(task: GeneratedTestPromotionTask) -> str` — returns one of the 7 allowed states
   - `validate_maintained_gate(code: str) -> bool` — returns False while any marker remains

2. Create `reports/drivers/promotion-tasks/` directory for promotion task output.

3. Modify `product_feature_factory.py` render calls to:
   - Call `create_promotion_task()` after each scaffold render
   - Write task YAML to `reports/drivers/promotion-tasks/`
   - Emit provenance header in rendered scaffold: `# PROVENANCE: template={template_id}, renderer={renderer_id}, format={format_id}, generated_at={iso_timestamp}`

4. Add tests in a new `tests/supervisor/test_drivers_promotion.py`:
   - `test_promotion_task_created_on_render`
   - `test_scaffold_status_is_not_maintained_while_markers_remain`
   - `test_maintained_gate_passes_only_when_all_markers_removed`
   - `test_promotion_task_yaml_is_valid`

**Completion gate:** `drivers_promotion.py` exists and tested. FeatureFactory emits promotion tasks. Tests pass.

---

## TC-DRV-008 — Phase 8: FeatureFactory and test_drivers Integration Repair

**Goal:** Full pipeline correctness: pattern → driver → template → renderer → scaffold → promotion task → format test.

**Actions:**
1. Refactor `test_drivers.py`:
   - Add `render_with_provenance(template_id, args) -> RenderResult` dataclass that includes: rendered_code, template_id, renderer_id, provided_args, timestamp, scaffold_status="FORMAT_ADAPTATION_REQUIRED"
   - Existing `render_*` functions call `render_with_provenance` internally
   - Add `validate_language_before_render(language: str)` gate

2. Refactor `test_test_drivers.py` to add:
   - `TestLanguagePolicy` — Python accepted, unsupported rejected
   - `TestContractValidation` — compatibility check passes/fails correctly
   - `TestPlaceholderScanner` — detects all 6 forbidden placeholder types
   - `TestPromotionTaskGeneration` — scaffold creates a promotion task
   - `TestMaintainedGate` — gate fails with markers, passes without
   - `TestProvenance` — rendered output contains PROVENANCE header
   - `TestRendererDrift` — removing an argument causes pre-generation failure

3. Verify `test_drivers.py` does NOT hardcode `drivers/python` in any public API — only in `_DRIVERS_DIR` private constant (acceptable for PYTHON_ONLY_BY_DESIGN).

**Completion gate:** All new tests pass. Pipeline produces provenance + promotion tasks. Drift is detected pre-render.

---

## TC-DRV-009 — Phase 9+10: Fixture/Assertion Contracts + Governance/README Repair

**Goal:** Complete contract definitions. All governance artifacts current and accurate.

**Actions:**
1. Add fixture contract constants to `test_drivers.py`:
   - `VALID_FIXTURE_SOURCES = ["repository_golden_sample", "deterministic_builder", "spec_example", "minimal_valid_bytes", "intentionally_malformed", "verified_roundtrip"]`
   - `WEAK_ASSERTION_PATTERNS` list of banned assertion strings
   - `MEANINGFUL_ASSERTION_KINDS` list of accepted assertion patterns

2. Add `validate_fixture_contract(fixture_bytes: bytes, fixture_source: str)` that rejects `b""` unless `fixture_source == "empty_input_contract"`.

3. Update `drivers/_readme.md` to document (per mission spec):
   - Purpose and current relevance (verified RETAIN)
   - Direct vs indirect consumers (classified)
   - Non-consumers (explicit list)
   - Supported language policy (PYTHON_ONLY_BY_DESIGN)
   - Template/renderer contracts (reference `driver-contracts.yaml`)
   - Placeholder policy (FORBIDDEN markers)
   - Format-promotion lifecycle (SCAFFOLD → MAINTAINED states)
   - Fixture and assertion requirements
   - Validation commands (`python -m pytest tests/supervisor/test_test_drivers.py -v`)
   - How to add a driver/template
   - Known gaps and next action

4. Add drift check to `test_test_drivers.py`: `TestDocumentationDrift` — reads `_readme.md` and asserts key sections exist. Fails if consumer list, language policy, or promotion lifecycle sections are removed.

5. Verify `idempotent-snuggling-wombat.md` TC-ROOT-002 correction is applied (from TC-DRV-002).

**Completion gate:** README fully updated. Drift test added. Contract helpers in test_drivers.py.

---

## TC-DRV-010 — Phase 11: Existing Generated-Test Audit

**Goal:** Inventory all driver-generated or FeatureFactory-produced test outputs. UNTRACKED_FORMAT_PROMOTION_OBLIGATIONS = 0.

**Actions:**
1. Search `tests/python/` for files containing `# Generated by` or `# AUTO-GENERATED` or `SCAFFOLD_STATUS`.
2. Scan `tests/python/` for tests with forbidden placeholder patterns (weak assertions).
3. For each weak test found: create a gap entry and promotion taskcard.
4. Produce `reports/drivers/generated-test-portfolio-audit.yaml` with classifications: SCAFFOLD, PARTIALLY_PROMOTED, MAINTAINED, WEAK_ASSERTION, PLACEHOLDER_REMAINS, MISSING_PROVENANCE, FALSELY_COMPLETE, UNKNOWN.
5. For any FALSELY_COMPLETE or PLACEHOLDER_REMAINS: create canonical gap (GAP-DRV-PROMO-NNN) and promotion taskcard.

**Completion gate:** Audit YAML exists. All material findings have gaps. All ready gaps have taskcards.

---

## TC-DRV-011 — Phase 12: Eight Required Pilots

**Goal:** Prove every system component through direct execution. FAILED_REQUIRED_PILOTS = 0.

**Pilot 1 — Current Python path (consumer + rendering flow):**
- Import `test_drivers.py` directly
- Call `render_getter_test("src/python/csv/models.py", "get_cell", ["row", "col"], "str")`
- Verify output is valid Python (ast.parse)
- Record console output as evidence

**Pilot 2 — Placeholder rejection:**
- Call a render function, get scaffold
- Confirm `is_maintained_test()` returns False
- Confirm `scan_incomplete_markers()` returns >0 items
- Confirm scaffold header contains `SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED`
- Confirm promotion task is created

**Pilot 3 — Simple format promotion (CSV):**
- Take the getter scaffold for CSV `get_cell`
- Replace `EXPECTED_VALUE_REQUIRED` with real assertion: `assert result == "value"`
- Replace `FIXTURE_REQUIRED` with real CSV bytes
- Confirm `is_maintained_test()` returns True
- Run the test file with `.venv/Scripts/pytest`
- Record promotion receipt YAML: `reports/drivers/promotion-receipts/csv-getter-pilot3.yaml`

**Pilot 4 — Structured/binary format promotion (ZST or FODS):**
- Use ZST (compress/decompress) or FODS (spreadsheet cell getter)
- Add real fixture from `samples/by-format/{format}/`
- Prove nontrivial fixture/assertion (byte comparison or model field equality)
- Record promotion receipt

**Pilot 5 — Renderer drift:**
- Temporarily remove one required argument from a render function signature
- Prove `validate_template_renderer_compatibility()` raises `ContractViolationError`
- Restore and prove it passes again
- Record before/after output

**Pilot 6 — Consumer classification:**
- Prove DIRECT: call `_load_template("getter_test.py.tmpl")` via test_drivers.py import
- Prove INDIRECT: show FeatureFactory chain to template
- Prove DECLARATIVE: show libforge_pattern_registry has no runtime coupling
- Record classifications in consumer-graph YAML

**Pilot 7 — Language policy (PYTHON_ONLY_BY_DESIGN):**
- Call `_validate_language("csharp")` → confirm `ValueError` raised
- Call `_validate_language("python")` → confirm no error
- Record both outcomes

**Pilot 8 — Idempotency:**
- Run full validation suite + rendering + compatibility check twice
- Compare: promotion task YAML content, consumer graph YAML, compatibility report
- Confirm zero material second-run changes (md5sum comparison or diff)
- Record `MATERIAL_SECOND_RUN_CHANGES = 0`

**Evidence:** Collect all pilot outputs in `.local/evidences/drivers-subsystem-healing-<run-id>/pilots/`.

**Completion gate:** All 8 pilots documented with console output or file evidence. Zero failures.

---

## TC-DRV-012 — Final Validation, Idempotency Proof, and Closeout

**Goal:** Prove all required counters = 0. Produce final report and terminal closeout.

**Actions:**
1. Run full test suite for affected modules:
   ```
   .venv/Scripts/pytest tests/supervisor/test_test_drivers.py tests/supervisor/test_product_feature_factory.py tests/supervisor/test_drivers_promotion.py -v
   ```
2. Run governance validators on modified source files.
3. Confirm required counters:
   - `UNRESOLVED_DRIVERS_GOVERNANCE_CONTRADICTIONS = 0`
   - `FALSE_DIRECT_CONSUMER_CLAIMS = 0`
   - `IMPLICIT_LANGUAGE_SCOPE = 0`
   - `ACTIVE_TEMPLATE_RENDERER_MISMATCHES = 0`
   - `FORBIDDEN_PLACEHOLDERS_IN_MAINTAINED_TESTS = 0`
   - `FALSELY_COMPLETE_GENERATED_SCAFFOLDS = 0`
   - `UNTRACKED_FORMAT_PROMOTION_OBLIGATIONS = 0`
   - `MATERIAL_DRIVERS_FINDINGS_WITHOUT_GAPS = 0`
   - `READY_DRIVERS_GAPS_WITHOUT_TASKCARDS = 0`
   - `FAILED_REQUIRED_PILOTS = 0`
   - `MATERIAL_SECOND_RUN_CHANGES = 0`
4. Run second pass of idempotency (all validators, renderers, reconciliation) — diff against first run.
5. Write `reports/drivers/drivers-subsystem-healing-report.md` with final verdict.
6. Write `.local/evidences/drivers-subsystem-healing-<run-id>/terminal-closeout.yaml`.
7. Write evidence declaration at `.local/evidences/drivers-subsystem-healing-<run-id>/evidence-declaration.yaml`.
8. Run `python tools/supervisor/autonomous_cycle.py` with declaration.

**Final verdict target:** `DRIVERS_SUBSYSTEM_RECONCILED_HARDENED_AND_IDEMPOTENT`

---

## Required Outputs

```
reports/drivers/
  drivers-finding-validation.yaml          (TC-DRV-001)
  drivers-governance-contradictions.yaml   (TC-DRV-002)
  drivers-consumer-graph.yaml              (TC-DRV-003)
  driver-language-decision.yaml            (TC-DRV-004)
  template-renderer-compatibility.yaml     (TC-DRV-005)
  template-placeholder-inventory.yaml      (TC-DRV-006)
  generated-test-portfolio-audit.yaml      (TC-DRV-010)
  promotion-tasks/                         (TC-DRV-007)
  promotion-receipts/                      (TC-DRV-011)
  drivers-subsystem-healing-report.md      (TC-DRV-012)

drivers/python/
  driver-contracts.yaml                    (TC-DRV-005)
  [updated *.py.tmpl files]                (TC-DRV-006)

tools/supervisor/
  test_drivers.py                          (modified TC-DRV-004,005,006,008)
  product_feature_factory.py               (modified TC-DRV-007,008)
  drivers_promotion.py                     (new TC-DRV-007)

tests/supervisor/
  test_test_drivers.py                     (extended TC-DRV-008,009)
  test_drivers_promotion.py               (new TC-DRV-007)

.local/evidences/drivers-subsystem-healing-<run-id>/
  evidence-declaration.yaml
  terminal-closeout.yaml
  pilots/
```

---

## Verification

After TC-DRV-012:
```bash
# Run test suite
.venv/Scripts/pytest tests/supervisor/test_test_drivers.py tests/supervisor/test_product_feature_factory.py tests/supervisor/test_drivers_promotion.py -v

# Verify counter report
cat reports/drivers/drivers-subsystem-healing-report.md | grep -E "= 0$"

# Second-run idempotency
# Run reconciliation suite again, compare output files with diff
```

All counters must equal 0. Final verdict must be `DRIVERS_SUBSYSTEM_RECONCILED_HARDENED_AND_IDEMPOTENT`.


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T11:38:59.728617+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
