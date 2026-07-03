# Plan: fancy-bubbling-truffle
# Product Library Code-Writing and Architecture Healing — Full 22-Phase Lifecycle

plan_type: product_quality_mission
mission_id: PQLM-001
version: 1.0

## Context

Format Factory's autonomous machinery can produce product code that:
- compiles and satisfies tests
- yet lacks specification grounding, professional API design, and maintainability

The immediate evidence: GI-FODS-NET-001 required a "Category D purge" — code was generated, survived CI, closed taskcards, but was structurally defective. More broadly: 10/20 Python formats lack analytics separation, 19/20 are missing `__all__` declarations, the SAL pipeline's 17+ modules produce artifacts never consumed, `autonomous_task_generator.py` uses hardcoded expansion goals instead of the capability map, and multiple known LOC violations exist in baseline.

**User direction:** Do not anchor on FODS. First triage ALL products to find the worst offender, then use that as the example product for the full investigation and rebuild. Execute all 22 phases.

## Mission Binding Record

```yaml
product_quality_mission:
  mission_id: PQLM-001
  repository: format-factory
  branch: main
  plan_path: plans/.claude/fancy-bubbling-truffle.md
  example_product: fods  # BOUND by TC-PQLM-001 — composite score 172 (runner-up fodt: 86)
  languages: [python, csharp]
  product_roots:
    - src/python/
    - src/net/
  spec_sources:
    - .local/sal-output/
    - acquisition-packs/*/verified-facts.yaml
  qname_sources:
    - shared/qname-registry/
    - registry/odf-ontology/qname-to-code-map.yaml
    - registry/python-qname-architecture.json
  capability_sources:
    - .governance/capabilities/registry.yaml
  code_writing_skills:
    - skills/add-python-api/
    - skills/add-dotnet-api/
    - skills/add-python-object-model-feature/
    - skills/add-dotnet-object-model-feature/
    - skills/implement-spec-stub/
    - skills/spec-shaped-product-architecture-blueprint/
  review_skills:
    - skills/python-qname-code-reviewer/
    - skills/certification-assertion-scorer/
    - skills/certification-stub-detector/
  generation_entry_points:
    - tools/supervisor/autonomous_task_generator.py
    - tools/supervisor/capability_feature_compiler.py
  certification_sources:
    - reports/supervisor/evidence-review.json
    - .governance/certification/
  evidence_roots:
    - .local/evidences/
```

---

## Taskcard Status Table

| TC-ID | Title | Status |
|---|---|---|
| TC-PQLM-001 | Mission Binding + Portfolio Triage | CLOSED |
| TC-PQLM-002 | Incident Baseline Preservation | CLOSED |
| TC-PQLM-003 | Manual File + Symbol Review | CLOSED |
| TC-PQLM-004 | Defect Categorization | CLOSED |
| TC-PQLM-005 | Root Cause Proof | CLOSED |
| TC-PQLM-006 | Target QName Architecture Design | CLOSED |
| TC-PQLM-007 | Code-Writing Skill Audit and Repair | CLOSED |
| TC-PQLM-008 | File/Folder Organization Contract | CLOSED |
| TC-PQLM-009 | Comments, Docs, Tags, Markers Policy | CLOSED |
| TC-PQLM-010 | Public API Governance Contract | CLOSED |
| TC-PQLM-011 | Heal Prompts, Taskcards, Reviewers, Graders | CLOSED |
| TC-PQLM-012 | Add Blocking Governance Validators | CLOSED |
| TC-PQLM-013 | Gap Ledger + Authoritative Plan Update | CLOSED |
| TC-PQLM-014 | System Healing Proof (Controlled Replay) | CLOSED |
| TC-PQLM-015 | Rebuild Example Product | CLOSED |
| TC-PQLM-016 | Rebuild Tests and Certification | CLOSED |
| TC-PQLM-017 | Pilot Tuning (14 Required Pilots) | CLOSED |
| TC-PQLM-018 | Portfolio Scan and Backfill Healing | CLOSED |
| TC-PQLM-019 | Idempotency Proof + Completion Gate | CLOSED |
| TC-PQLM-020 | Final Report | CLOSED |

---

## TC-PQLM-001: Mission Binding + Portfolio Triage
**Corresponds to:** Mission §1 + §19 (triage only)

**Goal:** Bind mission authorities. Scan all product sources to identify the worst-quality format using the full defect taxonomy signals. Commit the example product for TC-PQLM-002+.

**Actions:**
1. Read `registry/format-registry.yaml` for active format list (Python FOSS + .NET commercial tracks)
2. Read `registry/source-structure-baseline.json` for known_violations by format
3. Read `.governance/capabilities/registry.yaml` for capability/test counts per format
4. For each format in `src/python/` and `src/net/`, collect signals:
   - known_violation count (from baseline)
   - file count with LOC > 800
   - presence of `*_misc.py`, `*_helpers.py`, `*_extra.py`, `*_utils.py`, `*ExtendedApis*`, `*MissingMethods*`
   - `__all__` presence in `__init__.py`
   - analytics separation status
   - test count vs 65-test threshold
   - sprint/task/wave/gate/run identifiers in source (grep for `IR-`, `R\d{2,}`, `TC-`, `wave`, `train`, `sprint`)
   - README or certification claims not backed by evidence
5. Score each format on taxonomy match (architecture, QName, state/persistence, API design, files/folders, code writing, comments/docs, tests, governance)
6. Select the format with the highest combined defect signal score as the **example product**
7. Write `reports/product-quality/portfolio-triage.yaml` with all scores and selection rationale

**Output:**
- `reports/product-quality/portfolio-triage.yaml`
- `EXAMPLE_PRODUCT` and `EXAMPLE_LANGUAGE` bound for all subsequent taskcards

**Counters updated:** PRODUCT_LIBRARIES_NOT_SCANNED (initial triage pass)

---

## TC-PQLM-002: Incident Baseline Preservation
**Corresponds to:** Mission §2

**Goal:** Capture the complete before-state of the example product so every future change is measured against a known baseline.

**Actions:**
1. List all source files for the example product with: path, LOC, modification time
2. For Python: list all modules, public types, exported names, docstrings, TODO/FIXME/HACK markers
3. For .NET: list all classes, interfaces, methods, XML doc coverage, partial class splits
4. Record: all tests, their pass/fail state, what they actually assert
5. Record: any README, maturity, or certification claims
6. Record: commits, taskcards, and evidence that produced current code (git log --follow for key files)
7. Write `reports/product-quality/incident-baseline.yaml`

**Output:** `reports/product-quality/incident-baseline.yaml`

**Prerequisite:** TC-PQLM-001 CLOSED

---

## TC-PQLM-003: Manual File + Symbol Review
**Corresponds to:** Mission §3 + §4

**Goal:** Read every file completely. Document every public symbol. No proxy reading — full file content required.

**Actions (per file):**
- Record `file_review`: intended vs actual responsibilities, public/internal types, state owned, qnames, parser/model/writer/export roles, comment quality, documentation quality, tags/markers, architecture findings, code writing findings, governance findings, disposition
- Dispositions: KEEP | REWRITE | SPLIT_BY_DOMAIN | MOVE | MERGE_DUPLICATE | REPLACE_WITH_CANONICAL_MODEL | REMOVE_TEST_SHAPED_CODE | REMOVE_SPECULATIVE_API | QUARANTINE | INVESTIGATION_REQUIRED

**Actions (per public symbol):**
- Record `symbol_review`: symbol, file, owning type, intended user need, specification authority, qname, capability IDs, current behavior, state source, parser/model/writer connection, roundtrip behavior, validation, comments/docs, tests, consumer usage, disposition, gap IDs

**Required counters after completion:**
- PRODUCT_FILES_NOT_MANUALLY_REVIEWED = 0
- PUBLIC_SYMBOLS_NOT_REVIEWED = 0

**Output:** `reports/product-quality/file-reviews.yaml`, `reports/product-quality/symbol-reviews.yaml`

**Prerequisite:** TC-PQLM-002 CLOSED

---

## TC-PQLM-004: Defect Categorization
**Corresponds to:** Mission §5

**Goal:** Map every finding from §3/§4 to a defect category. Every material finding must have a category.

**Taxonomy to apply:**
- Architecture: monolithic facade, giant partial class, wrong ownership, missing domain types, duplicate models, parser/model/writer coupling, export logic inside domain objects
- QName/spec: no QName authority, decorative QName, incorrect hierarchy, generic facade replacing format semantics, speculative API
- State/persistence: detached dictionaries, in-memory-only properties, getter without parsed source, setter without writer path, fabricated defaults, state lost after reload
- API design: stringly typed domain, aliases for tests, inconsistent naming, inflated public surface, root document owning nested behavior
- Files/folders: `MissingMethods`, `ExtendedApis`, `Misc`, `Helpers`, `Stubs` filenames; sprint/task/run identifiers in filenames; multiple unrelated types per file
- Code writing: constant returns, empty success, semantic stubs, excessive method length, magic strings, mutable state without invariants
- Comments/docs: history-describing comments, sprint IDs in product source, stale comments, false XML docs/docstrings, missing public API documentation
- Tests/certification: presence-only tests, getter/setter symmetry tests, default-only assertions, no real input, no writer proof, no round-trip
- Governance: missing code-writing skill, weak skill contract, no architecture gate, no file-content review, task closure based on tests only

**Output:** `reports/product-quality/problem-taxonomy.yaml`

**Required counter:** MATERIAL_FINDINGS_WITHOUT_GAPS (tracked but closed in TC-PQLM-013)

**Prerequisite:** TC-PQLM-003 CLOSED

---

## TC-PQLM-005: Root Cause Proof
**Corresponds to:** Mission §6

**Goal:** For each defect category, trace to the originating system component. Test competing hypotheses.

**Components to inspect for each defect:**
- `tools/supervisor/autonomous_task_generator.py` — does it use hardcoded goals instead of capability map?
- `.supervisor/skill-registry.yaml` + `skills/` — do skill contracts require architecture-first design?
- `tools/supervisor/capability_feature_compiler.py` — does the gap ledger flow into task generation?
- Reviewer rubrics in skills — do they inspect full files or just summaries?
- Grader scoring in `tools/supervisor/supervisor_loop.py` — does it reward semantic quality or volume?
- Evidence declaration schema — does it require spec_fact_refs, parser/writer path, roundtrip proof?
- Certification rules — does certification require semantic proof or just test count?

**Record per cause:**
```yaml
system_cause:
  cause_id: SC-NNN
  defect_categories: []
  originating_component: <file:line>
  exact_instruction_or_behavior: <quote>
  incentive_created: <what the agent optimizes for>
  resulting_code_pattern: <what bad code results>
  first_failed_control_boundary: <which validator/gate missed it>
  why_existing_controls_failed: <exact reason>
  evidence: []
  prevention: <what to add>
  detection: <what validator to add>
  recovery: <how to heal existing code>
```

**Required counter:** DEFECT_CATEGORIES_WITHOUT_PROVEN_SYSTEMIC_CAUSE = 0

**Output:** `reports/product-quality/system-causes.yaml`

**Key hypothesis to test:** `autonomous_task_generator.py` uses `_EXPANSION_GOALS` hardcoded catalog → tasks generated without spec grounding → agents produce code without SAL fact backing → code passes tests but lacks professional design.

**Prerequisite:** TC-PQLM-004 CLOSED

---

## TC-PQLM-006: Target QName Architecture Design
**Corresponds to:** Mission §7 + §8

**Goal:** Design the target state for the example product — QName type map, file layout, domain types, parser/model/writer/export components — BEFORE any source changes.

**Produce for each language:**
```yaml
target_product_architecture:
  product: <example_product>
  language: python | csharp
  root_document_type: <canonical class>
  namespace_or_module_hierarchy: []
  qname_type_map: []  # spec_qname → canonical class → file
  domain_types: []
  value_types: []
  parser_components: []
  writer_components: []
  validation_components: []
  export_components: []
  public_facades: []
  mutability_policy: <immutable read model | mutable DOM>
  nullability_policy: <explicit nulls | never null>
  unsupported_feature_policy: <raise | warn | skip>
  compatibility_policy: <no breaking | shim in Compat/>
  file_layout: []  # approved file → responsibility mapping
  migration_map: []  # current file → target file
```

**File layout rules to enforce:**
- No `MissingMethods`, `ExtendedApis`, `Misc`, `Helpers`, `Stubs` in product filenames
- No sprint/task/requirement/wave/train/gate identifiers in product source filenames
- Parser / Model / Writer / Export / Validation concerns separated into distinct files
- One primary public type per file unless tightly coupled (document + factory method ok)
- Namespaces/modules mirror domain hierarchy (Model/Table/, Model/Style/, etc.)

**Output:** `reports/product-quality/target-architecture.yaml`

**Prerequisite:** TC-PQLM-005 CLOSED

---

## TC-PQLM-007: Code-Writing Skill Audit and Repair
**Corresponds to:** Mission §9

**Goal:** Audit all 6 code-writing skills. Repair any that allow bad patterns through without rejection.

**Skills to audit:**
- `skills/add-python-api/` → enforce architecture-first, QName authority, file-content plan, parser/model/writer obligations, comment plan, self-review
- `skills/add-dotnet-api/` → same + XML doc requirement, no `ExtendedApis.cs` targets
- `skills/add-python-object-model-feature/` → spec_qname ClassVar enforcement
- `skills/add-dotnet-object-model-feature/` → spec QName in XML doc, canonical naming
- `skills/implement-spec-stub/` → one stub at a time, architecture_only marker required
- `skills/spec-shaped-product-architecture-blueprint/` → no flat class violations

**Each skill must explicitly REJECT:**
- "implement all missing methods"
- "make tests pass" without authority
- "add stubs / return defaults"
- "store values in dictionaries"
- "split the file" without design
- Dumping-ground filenames
- Sprint/task/requirement markers in production source

**Output:** Updated skill files; `reports/product-quality/skill-audit.yaml`

**Prerequisite:** TC-PQLM-006 CLOSED (need target architecture to know what skills should produce)

---

## TC-PQLM-008: File/Folder Organization Contract
**Corresponds to:** Mission §8 (implementation)

**Goal:** Produce an enforceable product-specific file layout contract and validate it can detect violations.

**Actions:**
1. Write `docs/code-quality/product-file-layout-contract.yaml` with approved layout per format
2. Write a validator (or extend V50/V66) that checks filenames against approved layouts
3. Confirm the validator runs in pre-commit, supervisor review, and certification
4. Test the validator rejects: `FodsDocumentExtendedApis.cs`, `fods_misc.py`, `fods_helpers.py`, `Sprint5Additions.cs`

**Output:** `docs/code-quality/product-file-layout-contract.yaml`, validator extension

**Prerequisite:** TC-PQLM-006 CLOSED

---

## TC-PQLM-009: Comments, Docs, Tags, Markers Policy
**Corresponds to:** Mission §10

**Goal:** Define and enforce a single comment/docstring/tag contract.

**Policy to define (Python):**
- Public API: docstrings required; describe intent, spec grounding, persistence guarantees; no sprint/run/wave IDs
- TODO/FIXME/HACK: must reference governed GAP-* or TC-* ID; expiration required
- Forbidden: "production-grade stub", history descriptions, stale behavior claims, commented-out code
- `__all__`: explicit or dynamic pattern required in all `__init__.py`

**Policy to define (.NET):**
- XML doc on all public types and members (GenerateDocumentationFile enforced)
- `<summary>` must describe spec QName and user intent; not sprint history
- `<exception cref>` required when method throws
- TODO with `// TODO(GI-NNN):` format only; no free-form sprint IDs

**Add validators for:**
- Undocumented public Python APIs (missing docstring on public def)
- False XML doc (`<summary>` is whitespace or "TODO")
- Untracked TODO/FIXME/HACK (no recognized ID pattern)
- Comments containing `sprint`, `wave`, `train`, `TC-` (outside of governed references)
- Commented-out code blocks (lines starting with `#` that are valid Python/C#)

**Output:** `docs/code-quality/comment-and-docs-contract.md`, validator extensions

**Prerequisite:** TC-PQLM-005 CLOSED (need root causes to know what to block)

---

## TC-PQLM-010: Public API Governance Contract
**Corresponds to:** Mission §11

**Goal:** Define authority requirements for every public API and add enforcement.

**Contract:**
- Every public class/method/property requires: specification authority (QName or spec fact ref), capability ID, owning type, documented persistence behavior
- No API added solely because: tests reference it, compilation requires it, another language exposes it, a requirement ID exists, it increases capability counts
- Root document must not own methods for nested domain concepts
- No stringly-typed closed vocabularies — use typed enums/value types

**Enforcement additions:**
- Pre-implementation check: "does a GAP-* or FACT-* entry authorize this API?" — block if missing
- Post-implementation check: "is this API referenced only by tests?" — flag for review
- Documentation check: persistence claims must be tested (getter without parser proof = fail)

**Output:** `docs/code-quality/public-api-contract.md`, validator extensions

**Prerequisite:** TC-PQLM-009 CLOSED

---

## TC-PQLM-011: Heal Prompts, Taskcards, Reviewers, Graders
**Corresponds to:** Mission §12

**Goal:** Update all components that shape agent behavior during task execution.

**Prompts to heal:**
- Sprint generation prompt (next-sprint.md template): require architecture plan before implementation section
- Task decomposition prompt: require QName authority and file-content plan for each work item
- Code-generation sub-prompts: add mandatory pre-implementation checklist

**Taskcard schema to extend** (`docs/automation/supervisor-worker-contract.md`):
- Add required fields: `qnames`, `owning_types`, `target_files`, `file_responsibilities`, `parser_obligations`, `model_obligations`, `writer_obligations`, `public_api_obligations`, `comment_and_docs_obligations`, `proof_target`, `closeout_rules`

**Reviewer rubrics to update:**
- Must inspect full file content (not just diff)
- Must score: folder/namespace correctness, public API shape, comments/docs, naming, parser/model/writer path, round-trip behavior
- Must reject: presence-only assertions, test-shaped APIs, undocumented symbols

**Grader scoring to update:**
- Reward semantic completeness, architectural conformance, roundtrip proof
- Penalize: volume-only increases, test-count padding, capability count inflation without spec grounding

**Output:** Updated schema files, reviewer rubrics, grader config

**Prerequisite:** TC-PQLM-007, TC-PQLM-010 CLOSED

---

## TC-PQLM-012: Add Blocking Governance Validators
**Corresponds to:** Mission §13

**Goal:** Add precise, bounded checks for patterns identified in defect taxonomy. Wire into all enforcement points.

**New validators to add** (extend `tools/supervisor/governance_validators_ext2.py`):
- V86: `validate_suspicious_filenames` — block `*ExtendedApis*`, `*MissingMethods*`, `*Misc*`, `*Stubs*` in product src
- V87: `validate_history_identifiers_in_source` — scan product .py/.cs for free-form sprint/wave/train/run IDs
- V88: `validate_undocumented_public_python_apis` — block public `def` without docstring
- V89: `validate_ungoverned_todo_markers` — block TODO/FIXME/HACK without recognized GAP-*/TC-* ref
- V90: `validate_constant_return_public_methods` — detect public methods that always return literal
- V91: `validate_getter_without_parser_source` — detect public properties with no parser/model backing
- V92: `validate_setter_without_writer_path` — detect public setters with no writer path
- V93: `validate_test_only_public_apis` — detect public APIs referenced only in test files
- V94: `validate_detached_persistent_state` — detect `dict` used as primary backing store for persistent features
- V95: `validate_files_outside_approved_layout` — check source file paths against product-file-layout-contract.yaml

**Wire into:**
- `tools/supervisor/governance_validator_runner.py` (register new validators)
- Sprint closeout (autonomous_cycle.py)
- Pre-commit (if hook exists)
- Certification requirements

**Output:** Extended validator files, updated runner, test coverage for each new validator

**Prerequisite:** TC-PQLM-009, TC-PQLM-010 CLOSED

---

## TC-PQLM-013: Gap Ledger + Authoritative Plan Update
**Corresponds to:** Mission §14

**Goal:** Convert every finding into a tracked gap. Update the authoritative plan with healing lanes.

**Produce:** `reports/product-quality/product-code-gap-ledger.yaml`

**Each gap entry:**
```yaml
gap:
  gap_id: PCG-NNN
  product: <format>
  language: python | csharp | both
  category: <taxonomy category>
  severity: blocking | major | minor
  files: []
  symbols: []
  qnames: []
  capability_ids: []
  evidence: []
  first_failed_boundary: <validator or gate>
  root_cause: <SC-NNN ref>
  system_repair: <machinery change>
  architecture_repair: <type/file design change>
  code_repair: <source change>
  documentation_repair: <comment/doc change>
  test_repair: <test change>
  certification_repair: <cert status change>
  backfill_scope: example_only | portfolio
  verification: []
  pilots: []
  task_ids: []
  status: OPEN
  next_action: <first concrete step>
```

**Also update** `plans/master-plan.md` with lanes for all gap categories.

**Required counters:**
- MATERIAL_FINDINGS_WITHOUT_GAPS = 0
- ACTIONABLE_GAPS_WITHOUT_TASKS = 0

**Prerequisite:** TC-PQLM-005, TC-PQLM-012 CLOSED

---

## TC-PQLM-014: System Healing Proof (Controlled Replay)
**Corresponds to:** Mission §15

**Goal:** Prove the healed system rejects bad task shapes BEFORE touching product source.

**Controlled fixtures to create** in `tests/product-quality/fixtures/`:
- `reject_missing_method_task.yaml` — task asking to "implement all missing methods"
- `reject_test_shaped_api.yaml` — task asking to "add method X because test Y needs it"
- `reject_dumping_ground.yaml` — task targeting `*_misc.py` or `*Helpers.cs`
- `reject_detached_state.yaml` — task adding `dict` backing store for persistent feature
- `reject_history_comment.yaml` — task adding sprint/wave ID to product source
- `reject_undocumented_api.yaml` — task adding public method with no docstring

**Replay workflow:**
1. Run each fixture through the healed skill (simulate what agent would receive)
2. Verify the skill explicitly rejects or reframes the instruction before producing code
3. Verify validators catch any fixture that slips through to source

**Proof threshold:** All 6 fixture types must be rejected or reframed. Zero may produce defective code.

**Output:** `reports/product-quality/system-healing-proof.yaml`

**Prerequisite:** TC-PQLM-011, TC-PQLM-012, TC-PQLM-013 CLOSED

---

## TC-PQLM-015: Rebuild Example Product
**Corresponds to:** Mission §16

**Goal:** Using healed system, rebuild the example product through the official healed path.

**Steps (in order, no skipping):**
1. Classify every current file against target architecture (TC-PQLM-006)
2. Remove test-only and speculative APIs (with migration shims where needed for compatibility)
3. Design QName-aligned domain types per target_product_architecture
4. Replace detached dict state with proper parser-backed model
5. Connect parser → model → writer path end-to-end
6. Add typed values for closed vocabularies (enums, value objects)
7. Reorganize files/folders per approved layout (TC-PQLM-008)
8. Rewrite comments and documentation per policy (TC-PQLM-009)
9. Remove all implementation-history residue from source
10. Preserve justified compatibility through thin Compat/ shims only
11. Remove dumping-ground files after complete symbol migration

**Do NOT:** Split files mechanically by line count. Reorganize without redesign.

**Output:** Rebuilt source under `src/python/{example}/` and/or `src/net/{example}/`

**Prerequisite:** TC-PQLM-014 CLOSED

---

## TC-PQLM-016: Rebuild Tests and Certification
**Corresponds to:** Mission §17

**Goal:** Replace weak tests. Reopen and rebuild certification.

**Tests to add (replace presence-only tests):**
- Authority tests: verify QName mapping
- Parser tests: real file input → correct domain model
- Model tests: typed properties, factory methods
- Writer tests: domain model → format bytes
- Round-trip tests: parse(write(doc)) ≈ doc
- Preservation tests: unknown elements survive round-trip
- Validation tests: malformed input raises typed exceptions
- Documentation accuracy tests: docstrings match behavior
- Public consumer tests: external-consumer-style usage
- Architecture/layout checks: file names match approved layout
- Code-writing governance regression: bad patterns detected by validators
- Semantic-stub detection tests

**Certification to reopen:** Any certification closed based on volume or test count alone must be reopened and require new proof across all certification dimensions (parse, model, edit, write, round-trip, preservation, public API quality, source organization, documentation, unsupported behavior, interoperability, governance).

**Output:** Updated test files; reopened certification records

**Prerequisite:** TC-PQLM-015 CLOSED

---

## TC-PQLM-017: Pilot Tuning (14 Required Pilots)
**Corresponds to:** Mission §18

**14 required pilots:**
1. Architecture-first generation — agent produces architecture plan before code
2. Rejection of test-shaped missing-method work
3. QName-constrained persistent feature — spec fact → QName → model → parser → writer → test
4. Correct nested-domain ownership — nested concept owned by nested type, not root document
5. Professional folder/file generation — no dumping-ground files produced
6. Typed API and validation — no stringly-typed closed vocabularies
7. Accurate docstrings/XML docs — documentation matches actual behavior
8. Rejection of sprint/task markers and stale comments
9. Round-trip and preservation — unknown elements survive
10. External consumer usability — third-party consumer example compiles and runs
11. Semantic-stub and detached-state detection — new validators catch these
12. Agent replay from original defective task shape — healed system reframes it
13. Cross-language conceptual parity — Python and .NET expose equivalent domain model
14. Idempotent rerun — second skill execution on already-correct code produces no diff

**After each pilot:**
- Manually review ALL generated files
- Inspect comments and documentation
- Inspect folder and namespace layout
- Record weaknesses → update gaps → tune skills/validators → rerun until PASS
- Do NOT broaden rollout after weak pass

**Required counter:** FAILED_REQUIRED_PILOTS = 0 before proceeding to TC-PQLM-018

**Prerequisite:** TC-PQLM-016 CLOSED

---

## TC-PQLM-018: Portfolio Scan and Backfill Healing
**Corresponds to:** Mission §19

**Goal:** Apply full defect taxonomy to all remaining products. Heal confirmed cases through official healed path.

**Scan order prioritization:**
1. Certified or mature products (highest risk of false claims)
2. Commercial candidates (Gate 10/11 track)
3. Large root types (high API/test ratios)
4. Products with partial classes
5. Products with sprint/task identifiers in source
6. Minimal domain models with many default-return methods
7. Products generated by the same skills that produced defects in example product

**For each confirmed defective product:**
- Open gap entries in `reports/product-quality/product-code-gap-ledger.yaml`
- Heal shared machinery FIRST if the defect is systemic
- Repair product through official healed path (not ad-hoc)
- Add tests
- Reopen false certification

**Required counters:**
- PRODUCT_LIBRARIES_NOT_SCANNED = 0
- CONFIRMED_SIMILAR_CASES_NOT_HEALED = 0
- FALSE_CERTIFICATIONS_NOT_REOPENED = 0

**Prerequisite:** TC-PQLM-017 CLOSED

---

## TC-PQLM-019: Idempotency Proof + Completion Gate
**Corresponds to:** Mission §20 + §21

**Goal:** Second run produces no material changes. All 24 completion counters reach 0.

**Idempotency test:**
1. Run all healed skills on already-rebuilt example product — verify zero diff
2. Run all new validators on healed source — verify zero violations
3. Run all new tests on healed source — verify same pass counts
4. Run pilots 1 and 14 (architecture-first + idempotent rerun) — verify zero diff

**Completion gate checklist** (all 24 counters must = 0):
- PRODUCT_FILES_NOT_MANUALLY_REVIEWED
- PUBLIC_SYMBOLS_NOT_REVIEWED
- RETAINED_PUBLIC_APIS_WITHOUT_AUTHORITY
- DEFECT_CATEGORIES_WITHOUT_PROVEN_SYSTEMIC_CAUSE
- RETAINED_GETTERS_WITHOUT_PARSER_OR_MODEL_SOURCE
- RETAINED_SETTERS_WITHOUT_WRITER_PATH
- PERSISTENT_FEATURES_WITHOUT_ROUNDTRIP
- DETACHED_PERSISTENT_STATE_STORES
- TEST_ONLY_PUBLIC_APIS
- FABRICATED_DEFAULT_SUCCESS_APIS
- SUSPICIOUS_DUMPING_GROUND_FILES
- PRODUCT_SOURCE_FILES_WITH_HISTORY_IDENTIFIERS
- UNGOVERNED_TODO_FIXME_HACK_MARKERS
- PUBLIC_APIS_WITH_MISSING_OR_FALSE_DOCUMENTATION
- STALE_OR_MISLEADING_COMMENTS
- FILES_OUTSIDE_APPROVED_PRODUCT_LAYOUT
- MATERIAL_FINDINGS_WITHOUT_GAPS
- ACTIONABLE_GAPS_WITHOUT_TASKS
- FAILED_REQUIRED_PILOTS
- PRODUCT_LIBRARIES_NOT_SCANNED
- CONFIRMED_SIMILAR_CASES_NOT_HEALED
- FALSE_CERTIFICATIONS_NOT_REOPENED
- MATERIAL_SECOND_RUN_CHANGES

**Required counter:** MATERIAL_SECOND_RUN_CHANGES = 0

**Prerequisite:** TC-PQLM-018 CLOSED

---

## TC-PQLM-020: Final Report
**Corresponds to:** Mission §22

**Output:** `reports/product-quality/final-report.yaml` + human-readable summary

**Report must include:**
- Files and symbols reviewed (total counts)
- Defect categories found (by taxonomy bucket)
- Proven systemic causes (SC-NNN list)
- Target QName architecture (summary)
- File/folder/namespace contract (summary)
- Code-writing skills added or repaired (list)
- Comments/docstrings/tags governance (new rules)
- Prompt/task/reviewer/grader repairs (summary)
- Example product migration (before/after)
- Files and types removed, moved, redesigned (list)
- Parser/model/writer and round-trip proof (evidence paths)
- Tests and certification rebuilt (counts)
- Pilot tuning iterations (count per pilot)
- Products scanned and healed (list)
- Idempotency result
- Remaining true external blockers
- Exact evidence paths

**Verdict (exactly one):**
- `PRODUCT_CODE_SYSTEM_HEALED_AND_LIBRARIES_PRODUCTION_READY`
- `PRODUCT_CODE_SYSTEM_OR_PRODUCT_REPAIR_REQUIRES_REWORK`
- `BLOCKED_BY_TRUE_EXTERNAL_DEPENDENCY`

**Prerequisite:** TC-PQLM-019 CLOSED

---

## Key Files

**Investigation inputs:**
- [registry/source-structure-baseline.json](registry/source-structure-baseline.json) — LOC violations by format
- [.governance/capabilities/registry.yaml](.governance/capabilities/registry.yaml) — capability/test counts
- [registry/format-registry.yaml](registry/format-registry.yaml) — active format list
- [tools/supervisor/autonomous_task_generator.py](tools/supervisor/autonomous_task_generator.py) — hardcoded expansion goals (root cause hypothesis)
- [tools/supervisor/capability_feature_compiler.py](tools/supervisor/capability_feature_compiler.py) — canonical pipeline tool

**Skills to audit:**
- `skills/add-python-api/`, `skills/add-dotnet-api/`
- `skills/add-python-object-model-feature/`, `skills/add-dotnet-object-model-feature/`
- `skills/implement-spec-stub/`, `skills/spec-shaped-product-architecture-blueprint/`

**Standards to enforce:**
- [docs/code-quality/production-library-standard-v2.md](docs/code-quality/production-library-standard-v2.md)
- `.supervisor/skill-registry.yaml`

**Governance to extend:**
- [tools/supervisor/governance_validators_ext2.py](tools/supervisor/governance_validators_ext2.py) — add V86-V95
- [tools/supervisor/governance_validator_runner.py](tools/supervisor/governance_validator_runner.py) — register new validators

**Reports to produce:**
- `reports/product-quality/portfolio-triage.yaml`
- `reports/product-quality/incident-baseline.yaml`
- `reports/product-quality/file-reviews.yaml`
- `reports/product-quality/symbol-reviews.yaml`
- `reports/product-quality/problem-taxonomy.yaml`
- `reports/product-quality/system-causes.yaml`
- `reports/product-quality/target-architecture.yaml`
- `reports/product-quality/skill-audit.yaml`
- `reports/product-quality/system-healing-proof.yaml`
- `reports/product-quality/product-code-gap-ledger.yaml`
- `reports/product-quality/final-report.yaml`

---

## Verification (End-to-End Test)

1. **Portfolio triage** — `reports/product-quality/portfolio-triage.yaml` exists with scores for all active formats; example product is selected
2. **Incident baseline** — `reports/product-quality/incident-baseline.yaml` captures full before-state including commit hash, file sizes, LOC, public APIs
3. **All 24 completion counters = 0** — verified at TC-PQLM-019
4. **Pilot 14 passes** — `python -m pytest tests/product-quality/` with zero diff on second run
5. **New validators pass** — V86-V95 trigger on known-bad fixtures, pass on healed source
6. **Round-trip proof** — `parse(write(doc)) ≈ doc` for all retained persistent features in example product
7. **Final verdict** = `PRODUCT_CODE_SYSTEM_HEALED_AND_LIBRARIES_PRODUCTION_READY` (or explicit rework/blocked verdict with evidence)

---

## Taskcard Closure Summary (machine-parseable — 2-column format for lifecycle_audit.py)

| TC-ID | Status |
|---|---|
| TC-PQLM-001 | CLOSED |
| TC-PQLM-002 | CLOSED |
| TC-PQLM-003 | CLOSED |
| TC-PQLM-004 | CLOSED |
| TC-PQLM-005 | CLOSED |
| TC-PQLM-006 | CLOSED |
| TC-PQLM-007 | CLOSED |
| TC-PQLM-008 | CLOSED |
| TC-PQLM-009 | CLOSED |
| TC-PQLM-010 | CLOSED |
| TC-PQLM-011 | CLOSED |
| TC-PQLM-012 | CLOSED |
| TC-PQLM-013 | CLOSED |
| TC-PQLM-014 | CLOSED |
| TC-PQLM-015 | CLOSED |
| TC-PQLM-016 | CLOSED |
| TC-PQLM-017 | CLOSED |
| TC-PQLM-018 | CLOSED |
| TC-PQLM-019 | CLOSED |
| TC-PQLM-020 | CLOSED |

---

## Execution Notes

- **Do NOT commit or push** without explicit authorization
- **Do NOT perform irreversible external actions** (package publication, Gate 11 execution) without Babar Raza authority
- **Worst-case ordering:** If portfolio triage identifies a format other than FODS, all subsequent taskcards anchor on that format. FODS is a secondary example only.
- **Failure handling:** On any failure → PRESERVE RAW EVIDENCE → find first failed boundary → update gap → heal machinery → rerun pilot → rerun through healed path → manually review → reaudit
- **Plan lock:** Use `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/fancy-bubbling-truffle.md` immediately at session start


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-03T00:00:00.000000+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
  closure_note: "All 20 TC-PQLM taskcards CLOSED. Final verdict: PRODUCT_CODE_SYSTEM_HEALED_AND_LIBRARIES_PRODUCTION_READY. Convergence controller updated ITERATION_REQUIRED to TERMINAL_CLOSED after all-green validation."
-->
