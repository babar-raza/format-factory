# Format Factory Generation Archaeology — Enhanced Execution Plan
# Plan ID: fuzzy-conjuring-lobster
# Type: archaeology_audit | plan_authority: AUTHORITATIVE_SINGLE
# Status: IN_PROGRESS
# Authority: SINGLE_PLAN — no competing execution plan exists
# Last enhanced: 2026-07-10 (micro-taskcardization pass)

---

## ═══════════════════════════════════════════════════════════
## PART I — PREFLIGHT ANALYSIS BLOCK
## Embedded deliverables: taskcardization-preflight, authority-verdict,
## duplicate-plan-risk, plan-section-inventory, normalization-profile
## ═══════════════════════════════════════════════════════════

### [DOC-1] Taskcardization Preflight
```yaml
preflight:
  repository_path: "c:/Users/prora/OneDrive/Documents/GitHub/format-factory"
  branch: main
  head_commit: af879e55
  head_message: "feat(vwl): close vast-weaving-lampson machinery hardening plan"
  git_status: dirty_supervisor_artifacts_only
  active_plan_path: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"
  active_plan_title: "Format Factory Generation Archaeology — Execution Plan"
  plan_format: markdown_with_yaml_embedded
  authority_source: user_initiated_plan_mode
  plan_line_count: 543
  major_section_count: 12
  existing_taskcard_sections: 18  # TC-ARCH-001 through TC-ARCH-018
  existing_taskcard_format: high_level_steps_only  # INSUFFICIENT — no children, no micro-steps
  existing_lanes: A_B_C_D_E_F_G_H_I_J_K (11 lanes)
  existing_phases: 6
  existing_gates: none_explicit
  existing_state_vocabulary: PENDING_only
  existing_validation_model: none
  existing_evidence_model: implicit_report_file_only
  existing_normalization_conventions: none
  existing_naming_conventions: TC-ARCH-NNN
  existing_execution_handoff: none
  duplicate_plan_risk: LOW — no competing plans found
  enhancement_required: FULL_MICRO_TASKCARDIZATION
```

### [DOC-2] Active Plan Authority Verdict
```yaml
authority_verdict:
  authoritative_plan: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"
  authority_source: user_initiated_plan_mode_current_session
  duplicate_active_plans_found: false
  competing_execution_plans: none
  plan_in_repo: false  # lives in ~/.claude/plans/, not in repo
  status: AUTHORITATIVE_CONFIRMED
  execution_authority: true
  artifact_role: primary_plan
```

### [DOC-3] Duplicate Plan Risk Check
```yaml
duplicate_risk:
  plans_in_claude_plans_dir: 60+  # historical plans in plans/.claude/
  plans_with_archaeology_scope: 0  # no other archaeology plan found
  spec_to_feature_correction_plan: "plans/strategic/spec-to-feature-radical-correction-plan.md"
    note: "Parent strategic document — NOT a competing execution plan. Different scope."
  risk_level: LOW
  action_required: none
  note: "spec-to-feature-radical-correction-plan.md is strategic authority; this plan is
         its archaeology execution child. They do not compete — this plan produces
         the evidence that feeds corrections into the strategic plan."
```

### [DOC-4] Plan Section Inventory
```yaml
sections:
  - id: S-CTX
    title: "Context"
    type: context_and_rationale
    lines: "8-17"
  - id: S-EV
    title: "Evidence Already Gathered"
    type: recon_and_findings
    lines: "20-83"
  - id: S-VERDICT
    title: "Preliminary Verdict"
    type: analysis_conclusion
    lines: "86-106"
  - id: S-EXEC
    title: "Execution Plan"
    type: execution_definition
    lines: "108-145"
  - id: S-TC001
    title: "TC-ARCH-001 through TC-ARCH-018"
    type: taskcard_high_level
    lines: "148-407"
  - id: S-QMAP
    title: "Investigation Questions Mapped to Taskcards"
    type: traceability
    lines: "410-425"
  - id: S-FILES
    title: "Key Files Referenced"
    type: reference
    lines: "428-464"
  - id: S-SEQ
    title: "Execution Sequence"
    type: phase_ordering
    lines: "467-488"
  - id: S-STRICT
    title: "Strict Mode Constraints"
    type: governance
    lines: "491-501"
  - id: S-VER
    title: "Verification"
    type: closeout_criteria
    lines: "504-513"
  - id: S-QSTD
    title: "QName Translation Standard"
    type: design_standard
    lines: "517-528"
  - id: S-MACH
    title: "Known Existing Machinery to Reuse"
    type: reference
    lines: "531-538"
  - id: S-SELF
    title: "Self-Check"
    type: closeout_criteria
    lines: "541-543"
```

### [DOC-5] Plan Structure and Normalization Profile
```yaml
normalization_profile:
  enhancement_mode: MODE_B_TASKCARD_SECTION_HARDENING
  rationale: "Taskcards already exist but lack children, micro-steps, state, gates, evidence, validation"
  preserved_sections: S-CTX, S-EV, S-VERDICT, S-QSTD, S-FILES, S-MACH, S-STRICT
  normalized_sections: S-TC001, S-EXEC, S-SEQ, S-VER, S-SELF
  added_sections:
    - SECTION-PROCESS-LEDGER
    - REQUIREMENTS-INVENTORY
    - PARENT-CHILD-MICRO-STEP-TASKCARDS
    - MACHINE-STATE-MODEL
    - DEPENDENCY-DAG
    - VALIDATION-MATRIX
    - EVIDENCE-CONTRACT
    - RECONCILIATION-BLOCK
    - EXECUTION-HANDOFF
```

---

## ═══════════════════════════════════════════════════════════
## PART II — ORIGINAL CONTEXT (PRESERVED)
## ═══════════════════════════════════════════════════════════

## Context

This plan executes a **comprehensive Format Factory Generation Archaeology** — a structured audit to answer the core question:

> Is Format Factory currently able to convert specifications into professional, repeatable, qname/spec-hierarchy-aligned, testable, maintainable .NET and Python format libraries? Or is it still generating product-shaped prototypes from weak machinery?

**What triggered this**: The user's prompt identifies that current src/ may contain a mix of generation waves (format-prefixed Gen 1, capability-first Gen 2, partial qname Gen 3, DOM-backed Gen 4) and that machinery may not be deterministic enough to repeatedly produce professional libraries from specs. The archaeology must determine current state with evidence before any further product deepening.

**Intended outcome**: A complete evidence bundle containing per-product capability matrix, gap matrix, backfill facility design, and a go/no-go verdict for product deepening — with 27 required artifacts written to `reports/archaeology-2026-07-10/`.

**Strategic parent**: `plans/strategic/spec-to-feature-radical-correction-plan.md` identifies the same root problems: SAL is "ghost infrastructure — built but dormant", capability layer "generates output nobody consumes", task generation uses "hardcoded goals instead of capability map." This plan produces the forensic evidence to verify and quantify those claims.

---

## Evidence Already Gathered (from preflight investigation)

### Repository State
- **Branch**: main | **HEAD**: af879e55 (feat(vwl): close vast-weaving-lampson machinery hardening plan)
- **Dirty files**: All supervisor/report state files from last sprint (vast-weaving-lampson) — safe sprint artifacts. No product source modified.
- **Untracked**: `.runner_system_id` only
- **Last sprint**: 1169 tests PASS / 0 FAIL | AUTONOMOUS_CONTINUE: YES

### Source Inventory (confirmed by direct inspection)

**Python products (20 formats)**: abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst
- ALL 20 have `spec/` AND `Compat/` subdirectories ✓
- 11/20 have `build/` artifacts inside source (contamination) ✗
- Multiple `format_factory_*.egg-info/` dirs in `src/python/` — 20+ directories contaminating the tree ✗
- `.gitignore` excludes `*.egg-info/` but they ARE present (tracked by git before exclusion or non-normalized)
- **232 Python files** have `spec_qname` set — significant coverage

**Python spec depth** (actual .py file count in spec/ dir):
- FODS: 15 spec files (5 namespaces: number, office, style, table, text) — most mature
- FODT: 9 spec files
- CSV, TOML, ZST, XCF, PBM et al.: 3 spec files each — minimal

**.NET products (10 formats)**: csv, fods, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst
- FODS, FODT: Most mature — have `Spec/`, `Model/`, `Parsing/`, `Writing/`, `Exceptions/`
- CSV: Has `Spec/CsvRecord.cs`
- NDJSON: Has `Spec/` + format-prefixed at root (mixed)
- ZST: NO `Spec/` dir — format-prefixed only (Gen 1)
- All .NET formats have `bin/` and `obj/` inside source dirs (contamination)
- **29 .NET files** have `SpecQName` — lower coverage than Python

### Generation Waves Found (direct evidence)
- **Gen 1** (format-prefixed, monolithic): ZST .NET (`ZstDocument.cs`, `ZstParser.cs`, `ZstWriter.cs`), most Python core files (`fods_analytics.py`, `csv_parser.py` etc.)
- **Gen 2** (capability-first generic): Python `neutral_model.py` in FODS, `models.py` wrapper classes without full spec delegation
- **Gen 3** (partial qname, namespace-aware): Python `Compat/` files that delegate to `spec/`, Python `models.py` (`FodsCell` delegates to `spec.table.table_cell.TableCell`)
- **Gen 4** (DOM-backed, spec identity, qname metadata): Python `spec/table/table_cell.py` with `spec_qname`, `spec_fact_ref`, `namespace_uri`, `facade_names`; .NET `Spec/Table/TableCell.cs` with `SpecQName`, `SpecFactRef`; `FodsDocument.cs` XDocument-backed DOM with ODF namespace constants

### SAL State
- **FODS SAL**: Mature storage structure — actual ODF 1.3 spec PDF at `.local/spec-cache/fods/1.3/`, extracted+normalized+verified
  - Only **10 facts** (FACT-FODS-001 to FACT-FODS-010) — manually seeded from gate artifacts
  - Seeding note: "v1 facts seeded from gate artifacts. Richer extraction planned in TC-0021"
  - TC-0021 NOT done — 10 facts is far below what a comprehensive extraction would produce
- **CSV SAL**: RFC 4180 spec acquired and indexed at `.local/spec-cache/csv/rfc4180/`
- **TOML**: NOT in spec-cache (no spec acquired)
- **Per-format spec-cache**: 19 format dirs exist but quality varies enormously
- **Combined SAL DB**: `.local/spec-cache/sal-facts-20260621.json` — in `.local/`, NOT in repo
- **Critical strategic finding**: spec-to-feature-radical-correction-plan.md says SAL is "ghost infrastructure — built but dormant"

### QName/Ontology State
- **`registry/odf-ontology/`**: Has `qname-to-code-map.yaml`, `canonical-class-inventory.yaml`, `containment-graph.yaml`, `prefix-namespace-registry.yaml`
- **canonical-class-inventory.yaml**: Generated 2026-06-15, shows most classes as "not_implemented" or "facade_exists_no_canonical" — **STALE** (actual `Spec/Table/TableCell.cs` exists and isn't reflected)
- **qname-to-code-map.yaml**: References `src/FormatFactory/Office/Document.cs` — a **shared .NET namespace that does NOT exist** (paths are aspirational design targets, not actual locations)

### Governance/Skills State
- **165 governance validators** across 18+ validator files
- **V111-V127** in `governance_validators_ext4.py` directly enforce qname compliance, spec authority, traceability
- **Skills enforce qname**: `add-python-api.md` requires qname-to-code-map lookup, rejects format-prefixed names outside Compat/
- **`/qname-backfill` skill** exists in `.claude/commands/`
- **`/spec-parity-verification`** skill exists

### Capability Layer State
- `capability_feature_compiler.py` translates `gap-ledger.json` → `next-work-items.json`
- `CompiledCapability` schema has `specification_facts`, `qnames`, `parser_obligations`, `writer_obligations`
- SAL → Capability connection is indirect/manual (not a deterministic automated pipeline)
- `reports/capability-layer/` has per-format matrices
- **Critical strategic finding**: spec-to-feature-radical-correction-plan.md says capability layer "generates output nobody consumes"

### Gate Status
- FODS, FODT, NetPBM: G11-G sub-gate approved by Babar Raza 2026-06-05
- All formats: `commercial_product_ready: false` — NOT release-ready
- Full Gate 11 requires Babar Raza final commercial authorization

---

## Preliminary Verdict (to be confirmed by full audit)

**READY_AFTER_TARGETED_MACHINERY_REPAIRS**

Strengths:
- Architecture concept is sound (spec/ → models → Compat/ → consumers)
- FODS Python and .NET are the most advanced (Gen 4 in spec/ dirs)
- 165 governance validators enforce the architecture mechanically
- Skills enforce qname naming for new additions
- SAL pipeline concept exists and works for FODS (10 verified facts)
- 232 Python files and 29 .NET files carry spec_qname/SpecQName — real coverage

Blockers:
1. SAL only has 10 manually-seeded FODS facts; TC-0021 (richer extraction) pending — SAL is ghost infrastructure
2. canonical-class-inventory.yaml is stale — doesn't reflect current code reality
3. Build artifacts inside source dirs (11/20 Python, all .NET formats)
4. Shared .NET canonical namespace doesn't exist (qname-to-code-map paths aspirational)
5. Most formats (CSV, TOML, ZST, etc.) have minimal spec/ coverage (3 files vs FODS's 15)
6. SAL → Capability connection is indirect/manual — capability output not consumed
7. Non-ODF formats (ZST, CSV, etc.) have no formal qname namespace system

---

## ═══════════════════════════════════════════════════════════
## PART III — SECTION PROCESSING LEDGER
## [DOC-6] section-processing-ledger.yaml
## ═══════════════════════════════════════════════════════════

```yaml
section_processing_ledger:
  generated_by: "taskcardization-pass-2026-07-10"
  authoritative_plan: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"

  sections:
    - section_id: S-CTX
      title: "Context"
      type: context_and_rationale
      analysis_completed: true
      actionable_items_found: 0
      existing_taskcards: none
      missing_taskcards: none
      ambiguities: none
      contradictions: none
      enhancement_required: none
      change_status: PRESERVED

    - section_id: S-EV
      title: "Evidence Already Gathered"
      type: recon_and_findings
      analysis_completed: true
      actionable_items_found: 0  # findings only, not actions
      existing_taskcards: none
      missing_taskcards: none
      ambiguities:
        - "egg-info directories listed in .gitignore but present — are they committed or generated on install?"
        - "232 spec_qname files vs 20 formats × avg 11 files = good coverage but need per-format breakdown"
      contradictions: none
      enhancement_required: "Clarify egg-info tracking status in TC-ARCH-003"
      change_status: PRESERVED_WITH_NOTE

    - section_id: S-VERDICT
      title: "Preliminary Verdict"
      type: analysis_conclusion
      analysis_completed: true
      actionable_items_found: 0
      existing_taskcards: none
      missing_taskcards: none
      enhancement_required: none
      change_status: PRESERVED

    - section_id: S-TC001-through-018
      title: "TC-ARCH-001 through TC-ARCH-018"
      type: taskcard_high_level
      analysis_completed: true
      actionable_items_found: 18  # one per parent taskcard
      existing_taskcards: 18  # parents only
      missing_taskcards:
        - "72 child taskcards (avg 4 per parent)"
        - "360 micro-steps (avg 5 per child)"
      ambiguities:
        - "TC-ARCH-016 says 'synthesize gaps from TC-ARCH-001 to TC-ARCH-015' — must be SEQUENTIAL not parallel"
        - "TC-ARCH-017 'convert all gaps into taskcards' — scope unclear, needs child decomposition"
        - "TC-ARCH-018 'score all 36 questions' — no template provided for scoring"
      contradictions:
        - "TC-ARCH-007 says write per-product-capability-matrix.yaml but TC-ARCH-016/017 also write gap/taskcard files — overlap in output directory"
      enhancement_required: FULL_CHILD_MICRO_STEP_DECOMPOSITION
      change_status: ENHANCED

    - section_id: S-SEQ
      title: "Execution Sequence"
      type: phase_ordering
      analysis_completed: true
      actionable_items_found: 6  # phases
      existing_taskcards: none
      missing_taskcards: "No dependency DAG — only phase groupings"
      enhancement_required: "Add dependency DAG with parallel-safe flags"
      change_status: ENHANCED

    - section_id: S-VER
      title: "Verification"
      type: closeout_criteria
      analysis_completed: true
      actionable_items_found: 6  # verification checks
      missing_taskcards: "Not linked to specific child taskcards"
      enhancement_required: "Link each check to its responsible taskcard"
      change_status: ENHANCED
```

---

## ═══════════════════════════════════════════════════════════
## PART IV — REQUIREMENTS INVENTORY
## [DOC-7] normalized-requirements-inventory.yaml
## ═══════════════════════════════════════════════════════════

```yaml
requirements:
  # Lane A — Repository/State/Evidence
  - id: REQ-REPO-001
    description: "Capture and classify current repository state (branch, HEAD, dirty files, plans, evidence dirs)"
    plan_section: S-TC001 (TC-ARCH-001)
    investigation_required: false
    parent_taskcard: TC-ARCH-001

  # Lane B — Source Inventory
  - id: REQ-SRC-001
    description: "Inventory all 20 Python format source trees including spec/, Compat/, build artifacts"
    plan_section: S-TC001 (TC-ARCH-002)
    parent_taskcard: TC-ARCH-002

  - id: REQ-SRC-002
    description: "Inventory all 10 .NET format source trees including Spec/, Model/, build artifacts"
    plan_section: S-TC001 (TC-ARCH-002)
    parent_taskcard: TC-ARCH-002

  - id: REQ-SRC-003
    description: "Find and report all build artifacts (build/, bin/, obj/, egg-info/) inside src/"
    plan_section: S-TC001 (TC-ARCH-003)
    parent_taskcard: TC-ARCH-003

  - id: REQ-SRC-004
    description: "Classify all source files by generation wave (Gen 1-4) with per-file evidence"
    plan_section: S-TC001 (TC-ARCH-004)
    parent_taskcard: TC-ARCH-004

  # Lane C — QName
  - id: REQ-QNAME-001
    description: "Audit qname-to-code-map.yaml and verify each claimed path exists"
    plan_section: S-TC001 (TC-ARCH-005)
    parent_taskcard: TC-ARCH-005

  - id: REQ-QNAME-002
    description: "Measure canonical-class-inventory staleness against actual code"
    plan_section: S-TC001 (TC-ARCH-005)
    parent_taskcard: TC-ARCH-005

  - id: REQ-QNAME-003
    description: "Per-product: score spec_qname/SpecQName presence and delegation correctness"
    plan_section: S-TC001 (TC-ARCH-006)
    parent_taskcard: TC-ARCH-006

  # Lane D — Source Quality
  - id: REQ-QUAL-001
    description: "Score each Python product on 7 quality dimensions (Green/Yellow/Orange/Red/Gray)"
    plan_section: S-TC001 (TC-ARCH-007)
    parent_taskcard: TC-ARCH-007

  - id: REQ-QUAL-002
    description: "Score each .NET product on 7 quality dimensions"
    plan_section: S-TC001 (TC-ARCH-007)
    parent_taskcard: TC-ARCH-007

  # Lane E — SAL
  - id: REQ-SAL-001
    description: "Audit FODS SAL facts (10 manually seeded) and pipeline determinism"
    plan_section: S-TC001 (TC-ARCH-008)
    parent_taskcard: TC-ARCH-008

  - id: REQ-SAL-002
    description: "Survey per-format spec-cache coverage and classify as real/stub/missing"
    plan_section: S-TC001 (TC-ARCH-008)
    parent_taskcard: TC-ARCH-008

  # Lane F — Capability
  - id: REQ-CAP-001
    description: "Trace SAL → capability → feature compiler → next-work-items.json pipeline"
    plan_section: S-TC001 (TC-ARCH-009)
    parent_taskcard: TC-ARCH-009

  # Lane G — Downstream Generation
  - id: REQ-GEN-001
    description: "Identify where malformed source code enters the system"
    plan_section: S-TC001 (TC-ARCH-010)
    parent_taskcard: TC-ARCH-010

  # Lane H — Skills
  - id: REQ-SKILL-001
    description: "Inventory product-touching skills and score their qname/SAL/capability enforcement"
    plan_section: S-TC001 (TC-ARCH-011)
    parent_taskcard: TC-ARCH-011

  # Lane I — Supervisor
  - id: REQ-SUP-001
    description: "Audit check_continuation.py and GOV_BLOCK enforcement"
    plan_section: S-TC001 (TC-ARCH-012)
    parent_taskcard: TC-ARCH-012

  - id: REQ-SUP-002
    description: "Audit lane separation enforcement (code vs prompt-only)"
    plan_section: S-TC001 (TC-ARCH-013)
    parent_taskcard: TC-ARCH-013

  # Lane J — Backfill
  - id: REQ-BACK-001
    description: "Assess /qname-backfill skill capability and design systematic backfill plan"
    plan_section: S-TC001 (TC-ARCH-014)
    parent_taskcard: TC-ARCH-014

  # Lane K — Gate 11 / Readiness
  - id: REQ-GATE-001
    description: "Score FODS/FODT/NetPBM against Gate 11 C1-C20 and P1-P11 criteria"
    plan_section: S-TC001 (TC-ARCH-015)
    parent_taskcard: TC-ARCH-015

  # All Lanes — Synthesis
  - id: REQ-GAP-001
    description: "Build complete system-gap-matrix.yaml from all lane findings"
    plan_section: S-TC001 (TC-ARCH-016)
    parent_taskcard: TC-ARCH-016

  - id: REQ-TC-001
    description: "Convert all gaps into governed taskcards in 16 required groups"
    plan_section: S-TC001 (TC-ARCH-017)
    parent_taskcard: TC-ARCH-017

  - id: REQ-VERD-001
    description: "Answer 36 investigation questions and 21 self-check items; deliver verdict"
    plan_section: S-TC001 (TC-ARCH-018)
    parent_taskcard: TC-ARCH-018
```

---

## ═══════════════════════════════════════════════════════════
## PART V — HIERARCHICAL TASKCARDS
## Parent → Child → Micro-Steps for each of TC-ARCH-001 to TC-ARCH-018
## ═══════════════════════════════════════════════════════════

### Machine State Vocabulary
```
Parent states:  PROPOSED | READY | IN_PROGRESS | CHILDREN_IN_PROGRESS |
                INTEGRATION_PENDING | VERIFIED | SCORED | CLOSED |
                BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

Child states:   TODO | READY | IN_PROGRESS | IMPLEMENTED | VERIFIED |
                SCORED | CLOSED | REROUTED | BLOCKED | BLOCKED_EXTERNAL |
                DEFERRED_WITH_REASON

Micro-step:     PENDING | READY | ACTIVE | COMPLETE | FAILED |
                BLOCKED | SKIPPED_NOT_APPLICABLE
```

---

### TC-ARCH-001: Preflight State Report
```yaml
parent_taskcard:
  id: TC-ARCH-001
  title: "Capture repository preflight state and write preflight-state.md"
  type: PARENT
  status: PROPOSED
  lane: A
  requirement_ids: [REQ-REPO-001]
  plan_section: S-TC001

  objective: "Produce verified ground-truth snapshot of repo state before any audit work begins"
  outcome: "reports/archaeology-2026-07-10/preflight-state.md exists with complete, verified data"

  scope:
    allowed_read: ["git commands", ".local/supervisor/", "reports/supervisor/", "plans/"]
    allowed_write: ["reports/archaeology-2026-07-10/preflight-state.md"]
    forbidden_write: ["src/", "registry/", "tools/"]

  children:
    - TC-ARCH-001-01  # git state
    - TC-ARCH-001-02  # classify dirty files
    - TC-ARCH-001-03  # enumerate directories
    - TC-ARCH-001-04  # write report

  parent_acceptance_criteria:
    - "preflight-state.md exists and is non-empty"
    - "Every dirty file is classified"
    - "Branch, HEAD, and last sprint recorded"
    - "All plan directories listed"

  closeout_criteria:
    - "All 4 children CLOSED"
    - "preflight-state.md written to reports/archaeology-2026-07-10/"
    - "No unclassified dirty files"

  evidence_required:
    - "reports/archaeology-2026-07-10/preflight-state.md (path + file size > 0)"
```

```yaml
child_taskcard:
  id: TC-ARCH-001-01
  parent_id: TC-ARCH-001
  title: "Capture git state (log, status, branch, HEAD)"
  type: CHILD
  status: TODO
  requirement_ids: [REQ-REPO-001]

  purpose: "Establish exact repo state before any file reads or analysis"
  scope:
    allowed: ["git log --oneline -20", "git status", "git branch", "git rev-parse HEAD"]
    forbidden: ["git add", "git commit", "git push"]

  micro_steps:
    - id: MS-001-01-01
      action: "Run: git log --oneline -20"
      target_artifact: "preflight notes (in memory)"
      expected_output: "20 commit lines showing recent sprint history"
      completion_check: "Output contains commit hash af879e55 at position 0-1"
      status: PENDING

    - id: MS-001-01-02
      action: "Run: git status --short and record all dirty/untracked files"
      target_artifact: "preflight notes"
      expected_output: "List of modified and untracked files"
      completion_check: "Every file on the list is recorded with its change type (M, ??, D)"
      status: PENDING

    - id: MS-001-01-03
      action: "Run: git branch and git rev-parse HEAD; record branch name and full commit hash"
      target_artifact: "preflight notes"
      expected_output: "branch=main, HEAD=af879e55 (or current value)"
      completion_check: "Branch and HEAD recorded"
      status: PENDING

  acceptance_checks:
    - "All 3 micro-steps COMPLETE"
    - "Git state captured in memory for report writing"

  next_valid_task: TC-ARCH-001-02
```

```yaml
child_taskcard:
  id: TC-ARCH-001-02
  parent_id: TC-ARCH-001
  title: "Classify each dirty file by category"
  type: CHILD
  status: TODO
  requirement_ids: [REQ-REPO-001]

  purpose: "Distinguish sprint artifacts from product source changes, machinery changes, or risks"
  categories:
    - "sprint_artifact: supervisor state files, reports, plan files from last sprint"
    - "product_source: changes to src/python/ or src/net/"
    - "machinery_source: changes to tools/, governance files"
    - "generated_evidence: .local/evidences/ files"
    - "risky_conflicting: uncommitted changes that could affect audit results"
    - "unknown: cannot classify without deeper inspection"

  micro_steps:
    - id: MS-001-02-01
      action: "For each M (modified) file in git status, assign category using the category definitions above"
      expected_output: "Classification table: file → category"
      completion_check: "Zero files with category=unknown after inspection"
      status: PENDING

    - id: MS-001-02-02
      action: "For each ?? (untracked) file, assign category or mark as out-of-scope"
      expected_output: ".runner_system_id classified as system artifact (out of scope)"
      completion_check: "All untracked files classified"
      status: PENDING

    - id: MS-001-02-03
      action: "Record: are any product source files (src/python, src/net) dirty? If yes, note as audit risk"
      expected_output: "Audit-risk flag = false (expected based on preflight)"
      completion_check: "Risk flag recorded"
      status: PENDING

  acceptance_checks:
    - "Every file in git status output has an assigned category"
    - "No unclassified files"

  next_valid_task: TC-ARCH-001-03
```

```yaml
child_taskcard:
  id: TC-ARCH-001-03
  parent_id: TC-ARCH-001
  title: "Enumerate plans, evidence dirs, ledgers, supervisor files"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-001-03-01
      action: "List plans/ directory recursively; record: master-plan.md, strategic/, .claude/ count"
      target: "plans/ directory"
      expected_output: "plans/master-plan.md + plans/strategic/4 files + plans/.claude/60+ files"
      status: PENDING

    - id: MS-001-03-02
      action: "List .local/evidences/ run IDs and .local/supervisor/ state files"
      target: ".local/"
      expected_output: "List of run IDs, active-plan-lock.json, continuation-signal.json"
      status: PENDING

    - id: MS-001-03-03
      action: "Record last sprint ID, last test count, AUTONOMOUS_CONTINUE status from session-resume.md"
      target: "reports/supervisor/session-resume.md"
      expected_output: "sprint=vast-weaving-lampson, tests=1169, continue=YES"
      status: PENDING

  next_valid_task: TC-ARCH-001-04
```

```yaml
child_taskcard:
  id: TC-ARCH-001-04
  parent_id: TC-ARCH-001
  title: "Write reports/archaeology-2026-07-10/preflight-state.md"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-001-04-01
      action: "Create directory: reports/archaeology-2026-07-10/ if it does not exist"
      expected_output: "Directory exists"
      completion_check: "ls reports/archaeology-2026-07-10/ succeeds"
      status: PENDING

    - id: MS-001-04-02
      action: "Write preflight-state.md with: git state, file classifications, plan/evidence dirs, sprint state"
      target_file: "reports/archaeology-2026-07-10/preflight-state.md"
      expected_output: "File exists with all sections non-empty"
      status: PENDING

    - id: MS-001-04-03
      action: "Verify preflight-state.md is complete: contains git section, dirty-file table, plan list, sprint state"
      expected_output: "All 4 sections present in file"
      completion_check: "grep -c '##' reports/archaeology-2026-07-10/preflight-state.md >= 4"
      status: PENDING

  next_valid_task: TC-ARCH-002
  closes_parent: true  # when CLOSED, TC-ARCH-001 is INTEGRATION_PENDING
```

---

### TC-ARCH-002: Source Inventory
```yaml
parent_taskcard:
  id: TC-ARCH-002
  title: "Full inventory of all Python and .NET source trees"
  type: PARENT
  status: PROPOSED
  lane: B
  requirement_ids: [REQ-SRC-001, REQ-SRC-002]
  dependencies: [TC-ARCH-001]

  objective: "Produce verified enumeration of all 30 products (20 Python + 10 .NET) with file counts"
  outcome: "reports/archaeology-2026-07-10/source-inventory.md with complete per-product tables"

  children:
    - TC-ARCH-002-01  # Python format inventory
    - TC-ARCH-002-02  # .NET format inventory
    - TC-ARCH-002-03  # test/fixture directory inventory
    - TC-ARCH-002-04  # write report

  closeout_criteria:
    - "All 4 children CLOSED"
    - "source-inventory.md covers all 30 products"
    - "Each product row has: spec_depth, compat_exists, build_artifact, test_count"
```

```yaml
child_taskcard:
  id: TC-ARCH-002-01
  parent_id: TC-ARCH-002
  title: "Inventory each of 20 Python format source trees"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-002-01-01
      action: "For each Python format dir in src/python/, list all .py files (excluding __pycache__ and build/)"
      expected_output: "Per-format file list with counts"
      completion_check: "All 20 formats processed"
      status: PENDING

    - id: MS-002-01-02
      action: "For each format, count .py files in spec/ subdir (depth indicates spec maturity)"
      expected_output: "Per-format spec depth: fods=15, fodt=9, others=3"
      completion_check: "All 20 formats have spec depth recorded"
      status: PENDING

    - id: MS-002-01-03
      action: "For each format, verify Compat/ exists and count files in it"
      expected_output: "All 20 formats have Compat/, with varying file counts"
      status: PENDING

    - id: MS-002-01-04
      action: "For each format, check whether build/, dist/, or format_factory_*.egg-info/ exists inside the format dir"
      expected_output: "11/20 have build/; list which ones"
      status: PENDING

    - id: MS-002-01-05
      action: "Record Python _shared/ package contents (what's in src/python/_shared/)"
      expected_output: "List of shared base classes"
      status: PENDING

  next_valid_task: TC-ARCH-002-02
```

```yaml
child_taskcard:
  id: TC-ARCH-002-02
  parent_id: TC-ARCH-002
  title: "Inventory each of 10 .NET format source trees"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-002-02-01
      action: "For each .NET format in src/net/, list all .cs files (excluding bin/ and obj/)"
      expected_output: "Per-format .cs file list with counts"
      completion_check: "All 10 formats processed"
      status: PENDING

    - id: MS-002-02-02
      action: "For each format, check whether Spec/ subdir exists and list files inside it"
      expected_output: "FODS has Spec/Office/ and Spec/Table/; ZST has NO Spec/"
      status: PENDING

    - id: MS-002-02-03
      action: "For each format, check whether Model/ subdir exists and list files"
      expected_output: "FODS has FodsCell.cs, FodsRow.cs, FodsSheet.cs; others vary"
      status: PENDING

    - id: MS-002-02-04
      action: "Record which .NET formats have bin/ and obj/ inside source (all should)"
      expected_output: "All 10 formats have bin/ and obj/"
      status: PENDING

  next_valid_task: TC-ARCH-002-03
```

```yaml
child_taskcard:
  id: TC-ARCH-002-03
  parent_id: TC-ARCH-002
  title: "Inventory test directories and fixture samples per format"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-002-03-01
      action: "List tests/ directory — which formats have dedicated test dirs?"
      expected_output: "Per-format test directory presence"
      status: PENDING

    - id: MS-002-03-02
      action: "For each format test dir, count test files and note test coverage areas"
      expected_output: "Per-format: test file count, coverage type (unit/roundtrip/integration)"
      status: PENDING

    - id: MS-002-03-03
      action: "List samples/by-format/ and record which formats have fixture files"
      expected_output: "Per-format fixture file presence"
      status: PENDING

  next_valid_task: TC-ARCH-002-04
```

```yaml
child_taskcard:
  id: TC-ARCH-002-04
  parent_id: TC-ARCH-002
  title: "Write reports/archaeology-2026-07-10/source-inventory.md"
  type: CHILD
  status: TODO

  micro_steps:
    - id: MS-002-04-01
      action: "Write Python product table: format | spec_depth | compat | build_artifact | test_count | fixture"
      target_file: "reports/archaeology-2026-07-10/source-inventory.md"
      expected_output: "Table with 20 rows"
      status: PENDING

    - id: MS-002-04-02
      action: "Write .NET product table: format | spec_dir | model_dir | cs_count | bin_obj | test_count"
      target_file: "reports/archaeology-2026-07-10/source-inventory.md"
      expected_output: "Table with 10 rows"
      status: PENDING

    - id: MS-002-04-03
      action: "Write summary: total products, total files, % with spec/, % with Compat/, contamination count"
      expected_output: "Summary section with aggregate stats"
      status: PENDING

  next_valid_task: TC-ARCH-003
  closes_parent: true
```

---

### TC-ARCH-003: Source Hygiene Audit
```yaml
parent_taskcard:
  id: TC-ARCH-003
  title: "Find and categorize all build artifacts inside src/"
  type: PARENT
  status: PROPOSED
  lane: B
  requirement_ids: [REQ-SRC-003]
  dependencies: [TC-ARCH-002]

  objective: "Identify all build contamination in src/ and confirm .gitignore alignment"
  outcome: "reports/archaeology-2026-07-10/source-hygiene-audit.md"

  children:
    - TC-ARCH-003-01  # Python artifact scan
    - TC-ARCH-003-02  # .NET artifact scan
    - TC-ARCH-003-03  # gitignore check
    - TC-ARCH-003-04  # write report

  closeout_criteria:
    - "All 4 children CLOSED"
    - "source-hygiene-audit.md written"
    - "Complete list of artifact paths recorded"
```

```yaml
child_taskcard:
  id: TC-ARCH-003-01
  parent_id: TC-ARCH-003
  title: "Find all Python build artifacts inside src/python/"
  status: TODO

  micro_steps:
    - id: MS-003-01-01
      action: "Find all *.egg-info/ directories inside src/python/ (at any depth)"
      expected_output: "20+ egg-info dirs (one per format + root)"
      completion_check: "Count > 0"
      status: PENDING

    - id: MS-003-01-02
      action: "Find all build/ directories inside src/python/ format dirs"
      expected_output: "11 format dirs have build/ inside them"
      status: PENDING

    - id: MS-003-01-03
      action: "Find all __pycache__/ directories inside src/python/"
      expected_output: "Many __pycache__/ dirs (expected but note presence)"
      status: PENDING

    - id: MS-003-01-04
      action: "Check: are egg-info dirs tracked by git? Run: git ls-files src/python/*.egg-info"
      expected_output: "Determine if tracked (committed) or just present locally"
      completion_check: "tracking status recorded for each egg-info dir"
      status: PENDING

  next_valid_task: TC-ARCH-003-02
```

```yaml
child_taskcard:
  id: TC-ARCH-003-02
  parent_id: TC-ARCH-003
  title: "Find all .NET build artifacts inside src/net/"
  status: TODO

  micro_steps:
    - id: MS-003-02-01
      action: "Find all bin/ directories inside src/net/ format dirs"
      expected_output: "10 format dirs have bin/"
      status: PENDING

    - id: MS-003-02-02
      action: "Find all obj/ directories inside src/net/ format dirs"
      expected_output: "10 format dirs have obj/"
      status: PENDING

    - id: MS-003-02-03
      action: "Check: are bin/ and obj/ tracked by git? Run: git ls-files src/net/fods/bin/"
      expected_output: "Determine tracking status — if tracked, this is committed contamination"
      status: PENDING

  next_valid_task: TC-ARCH-003-03
```

```yaml
child_taskcard:
  id: TC-ARCH-003-03
  parent_id: TC-ARCH-003
  title: "Verify .gitignore coverage for all identified artifact patterns"
  status: TODO

  micro_steps:
    - id: MS-003-03-01
      action: "Read root .gitignore and check for: *.egg-info/, build/, bin/, obj/, __pycache__/, dist/"
      expected_output: "All patterns present in .gitignore"
      status: PENDING

    - id: MS-003-03-02
      action: "If any artifact dirs ARE tracked by git: record as GAP-HYGIENE finding requiring .gitignore cleanup"
      expected_output: "Gap entry if tracked artifacts found"
      status: PENDING

  next_valid_task: TC-ARCH-003-04
```

```yaml
child_taskcard:
  id: TC-ARCH-003-04
  parent_id: TC-ARCH-003
  title: "Write reports/archaeology-2026-07-10/source-hygiene-audit.md"
  status: TODO

  micro_steps:
    - id: MS-003-04-01
      action: "Write: Python artifact table (format, egg-info count, build dir, tracked?)"
      target_file: "reports/archaeology-2026-07-10/source-hygiene-audit.md"
      status: PENDING

    - id: MS-003-04-02
      action: "Write: .NET artifact table (format, bin tracked?, obj tracked?)"
      status: PENDING

    - id: MS-003-04-03
      action: "Write: hygiene verdict — are source audits polluted? recommended cleanup actions"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-004
```

---

### TC-ARCH-004: Generation Archaeology
```yaml
parent_taskcard:
  id: TC-ARCH-004
  title: "Classify all source files by generation wave (Gen 1-4) with evidence"
  type: PARENT
  status: PROPOSED
  lane: B
  requirement_ids: [REQ-SRC-004]
  dependencies: [TC-ARCH-002]

  objective: "Produce a per-product, per-file generation wave classification with evidence"
  outcome: "reports/archaeology-2026-07-10/generation-archaeology.md"

  gen_wave_definitions:
    gen1: "format-prefixed monolithic: FodsParser, ZstDocument, csv_parser.py — no spec delegation"
    gen2: "capability-first generic: neutral_model.py, Workbook/Sheet/Cell patterns"
    gen3: "partial qname: FodsCell delegates to spec.table.table_cell.TableCell via Compat/"
    gen4: "DOM-backed spec identity: spec_qname ClassVar, spec_fact_ref, SpecQName const"

  children:
    - TC-ARCH-004-01  # Python classification
    - TC-ARCH-004-02  # .NET classification
    - TC-ARCH-004-03  # survival analysis
    - TC-ARCH-004-04  # write report

  closeout_criteria:
    - "All 4 children CLOSED"
    - "generation-archaeology.md written"
    - "Every format has assigned primary generation wave"
```

```yaml
child_taskcard:
  id: TC-ARCH-004-01
  parent_id: TC-ARCH-004
  title: "Classify Python formats by generation wave"
  status: TODO

  micro_steps:
    - id: MS-004-01-01
      action: "For FODS: read spec/table/table_cell.py — confirm spec_qname, spec_fact_ref → Gen 4"
      target_file: "src/python/fods/spec/table/table_cell.py"
      expected_output: "class TableCell with spec_qname='table:table-cell' and spec_fact_ref"
      status: PENDING

    - id: MS-004-01-02
      action: "For FODS: read models.py — confirm FodsCell delegates to spec TableCell → Gen 3"
      target_file: "src/python/fods/models.py"
      expected_output: "FodsCell delegates to _SpecTableCell"
      status: PENDING

    - id: MS-004-01-03
      action: "For ZST: list src/python/zst/ files and check if spec/ is populated — expected minimal"
      target_dir: "src/python/zst/"
      expected_output: "3 spec files only; zst_parser.py, zst_workflow.py — format-prefixed (Gen 1/2)"
      status: PENDING

    - id: MS-004-01-04
      action: "For CSV: read src/python/csv/spec/ and check record.py — is there a spec class?"
      target_dir: "src/python/csv/spec/"
      expected_output: "3 spec files; check class names and spec_qname"
      status: PENDING

    - id: MS-004-01-05
      action: "For each remaining format (toml, xcf, pbm, pgm, ppm, qoi, abw, dif, etc.): run grep for spec_qname in spec/*.py and record whether canonical pattern exists"
      expected_output: "Per-format: gen wave assignment (Gen 1-4) with evidence file"
      completion_check: "All 20 formats have wave assignment"
      status: PENDING

  next_valid_task: TC-ARCH-004-02
```

```yaml
child_taskcard:
  id: TC-ARCH-004-02
  parent_id: TC-ARCH-004
  title: "Classify .NET formats by generation wave"
  status: TODO

  micro_steps:
    - id: MS-004-02-01
      action: "For FODS: read Spec/Table/TableCell.cs — confirm SpecQName constant → Gen 4"
      target_file: "src/net/fods/Spec/Table/TableCell.cs"
      expected_output: "public const string SpecQName = 'table:table-cell'"
      status: PENDING

    - id: MS-004-02-02
      action: "For FODS: read FodsDocument.cs — confirm XDocument DOM backing, namespace constants → Gen 4"
      target_file: "src/net/fods/FodsDocument.cs"
      expected_output: "XDocument _doc field; NsOffice, NsTable namespace constants"
      status: PENDING

    - id: MS-004-02-03
      action: "For ZST: read src/net/zst/ root files — check if SpecQName appears anywhere"
      target_dir: "src/net/zst/"
      expected_output: "No SpecQName — Gen 1 only"
      status: PENDING

    - id: MS-004-02-04
      action: "For CSV, NDJSON, TSV, HTML, Markdown, TXT, NetPBM: run grep for SpecQName in each"
      expected_output: "Per-format wave assignment"
      completion_check: "All 10 formats have wave assignment"
      status: PENDING

  next_valid_task: TC-ARCH-004-03
```

```yaml
child_taskcard:
  id: TC-ARCH-004-03
  parent_id: TC-ARCH-004
  title: "Assess survival vs replacement for each generation of code"
  status: TODO

  micro_steps:
    - id: MS-004-03-01
      action: "For Gen 1 code: determine which files are called from public API. If not called, mark as replaceable."
      expected_output: "Gen 1 files that are called (keep) vs orphaned (replaceable)"
      status: PENDING

    - id: MS-004-03-02
      action: "For Gen 2 code: check if neutral_model.py or similar is still referenced. If replaced by spec/, mark obsolete."
      expected_output: "Gen 2 survival assessment per format"
      status: PENDING

    - id: MS-004-03-03
      action: "For Gen 3 (Compat/ facades): confirm they delegate to Gen 4 spec/ classes. If yes, mark as valuable transitional layer."
      expected_output: "Compat/ files should be kept as backward-compat layer"
      status: PENDING

    - id: MS-004-03-04
      action: "For Gen 4 spec/ classes: confirm they are the canonical implementation. Mark as KEEP/EXPAND."
      expected_output: "Gen 4 code = keep; needs expansion to cover more spec elements"
      status: PENDING

  next_valid_task: TC-ARCH-004-04
```

```yaml
child_taskcard:
  id: TC-ARCH-004-04
  parent_id: TC-ARCH-004
  title: "Write reports/archaeology-2026-07-10/generation-archaeology.md"
  status: TODO

  micro_steps:
    - id: MS-004-04-01
      action: "Write generation wave definitions section with code examples from actual source"
      target_file: "reports/archaeology-2026-07-10/generation-archaeology.md"
      status: PENDING

    - id: MS-004-04-02
      action: "Write per-product generation wave table: format | language | primary_wave | evidence_file"
      expected_output: "Table with 30 rows (20 Python + 10 .NET)"
      status: PENDING

    - id: MS-004-04-03
      action: "Write survival analysis: what should be kept, replaced, or expanded in each wave"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-005
```

---

### TC-ARCH-005: QName Schema Audit
```yaml
parent_taskcard:
  id: TC-ARCH-005
  title: "Audit qname-to-code-map.yaml and canonical-class-inventory.yaml vs actual code"
  type: PARENT
  status: PROPOSED
  lane: C
  requirement_ids: [REQ-QNAME-001, REQ-QNAME-002]
  dependencies: [TC-ARCH-002, TC-ARCH-004]

  objective: "Measure staleness of qname registry vs actual source; identify aspirational vs real paths"
  outcome: "reports/archaeology-2026-07-10/qname-schema-audit.md"

  known_findings:
    - "canonical-class-inventory.yaml generated 2026-06-15 — STALE"
    - "qname-to-code-map.yaml references src/FormatFactory/ which does NOT exist"

  children:
    - TC-ARCH-005-01  # audit qname-to-code-map
    - TC-ARCH-005-02  # verify canonical paths exist
    - TC-ARCH-005-03  # audit canonical-class-inventory staleness
    - TC-ARCH-005-04  # write report

  closeout_criteria:
    - "All 4 children CLOSED"
    - "qname-schema-audit.md written"
    - "Stale/aspirational entries counted"
```

```yaml
child_taskcard:
  id: TC-ARCH-005-01
  parent_id: TC-ARCH-005
  title: "Read qname-to-code-map.yaml and record all mappings"
  status: TODO

  micro_steps:
    - id: MS-005-01-01
      action: "Read registry/odf-ontology/qname-to-code-map.yaml fully"
      target_file: "registry/odf-ontology/qname-to-code-map.yaml"
      expected_output: "Full mapping list: office:document → Office.Document, table:table-cell → Table.TableCell, etc."
      status: PENDING

    - id: MS-005-01-02
      action: "Count total qname mappings; identify which ones have dotnet_path vs python_path"
      expected_output: "N mappings total; M have dotnet_path; K have python_path"
      status: PENDING

    - id: MS-005-01-03
      action: "Identify all dotnet_paths referencing src/FormatFactory/ (aspirational, non-existent)"
      expected_output: "List of aspirational paths that do not exist"
      status: PENDING

  next_valid_task: TC-ARCH-005-02
```

```yaml
child_taskcard:
  id: TC-ARCH-005-02
  parent_id: TC-ARCH-005
  title: "For each mapping, verify whether the claimed source paths actually exist"
  status: TODO

  micro_steps:
    - id: MS-005-02-01
      action: "For each python_path in qname-to-code-map: check if the file exists in actual repo"
      expected_output: "Per-path: EXISTS / MISSING / ASPIRATIONAL"
      status: PENDING

    - id: MS-005-02-02
      action: "For each dotnet_path: check if the file exists (src/FormatFactory/ paths will be MISSING)"
      expected_output: "Most dotnet_paths will be MISSING (pointing to non-existent shared namespace)"
      status: PENDING

    - id: MS-005-02-03
      action: "For FODS specifically: verify src/net/fods/Spec/Table/TableCell.cs exists despite map saying src/FormatFactory/Table/TableCell.cs"
      target_file: "src/net/fods/Spec/Table/TableCell.cs"
      expected_output: "File EXISTS at per-format path, not at shared path"
      completion_check: "Confirms qname map uses aspirational shared path, actual code uses per-format path"
      status: PENDING

    - id: MS-005-02-04
      action: "Calculate: what % of python_paths exist? what % of dotnet_paths exist?"
      expected_output: "Python: ~70-80% exist; .NET: ~20% exist (all at wrong shared path)"
      status: PENDING

  next_valid_task: TC-ARCH-005-03
```

```yaml
child_taskcard:
  id: TC-ARCH-005-03
  parent_id: TC-ARCH-005
  title: "Audit canonical-class-inventory.yaml for staleness"
  status: TODO

  micro_steps:
    - id: MS-005-03-01
      action: "Read registry/odf-ontology/canonical-class-inventory.yaml fully"
      expected_output: "Full class list with status field per entry"
      status: PENDING

    - id: MS-005-03-02
      action: "Count entries by status: not_implemented / facade_exists_no_canonical / implemented"
      expected_output: "~5 facade_exists; ~15 not_implemented; ~0 implemented (based on 2026-06-15 snapshot)"
      status: PENDING

    - id: MS-005-03-03
      action: "For each 'facade_exists_no_canonical' entry: verify that the canonical class NOW EXISTS in Spec/"
      expected_output: "TC-ARCH-005-03 finding: TableCell exists in Spec/ but inventory says facade_exists_no_canonical → STALE"
      status: PENDING

  next_valid_task: TC-ARCH-005-04
```

```yaml
child_taskcard:
  id: TC-ARCH-005-04
  parent_id: TC-ARCH-005
  title: "Write reports/archaeology-2026-07-10/qname-schema-audit.md"
  status: TODO

  micro_steps:
    - id: MS-005-04-01
      action: "Write: qname-to-code-map.yaml audit table (qname, canonical, python_path_status, dotnet_path_status)"
      target_file: "reports/archaeology-2026-07-10/qname-schema-audit.md"
      status: PENDING

    - id: MS-005-04-02
      action: "Write: canonical-class-inventory staleness analysis — how stale, what changed since 2026-06-15"
      status: PENDING

    - id: MS-005-04-03
      action: "Write: gap findings: aspirational shared .NET namespace, stale inventory, path mismatches"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-006
```

---

### TC-ARCH-006: Per-Product QName Compliance
```yaml
parent_taskcard:
  id: TC-ARCH-006
  title: "Score each product for qname compliance (spec_qname/SpecQName presence and delegation)"
  type: PARENT
  status: PROPOSED
  lane: C
  requirement_ids: [REQ-QNAME-003]
  dependencies: [TC-ARCH-004, TC-ARCH-005]

  objective: "Produce a per-product qname compliance score for all 30 products"
  outcome: "reports/archaeology-2026-07-10/per-product-qname-compliance.yaml"

  compliance_dimensions:
    - "spec_dir_exists: does spec/ (Python) or Spec/ (.NET) exist?"
    - "classes_have_spec_qname: do classes in spec/ have spec_qname ClassVar?"
    - "facade_delegates_to_spec: do Compat/ or Model/ files delegate to spec classes?"
    - "models_not_detached: no anonymous dict as primary state"
    - "traceability_chain: spec_fact_ref present linking to SAL"

  children:
    - TC-ARCH-006-01  # Python spec_qname grep
    - TC-ARCH-006-02  # .NET SpecQName grep
    - TC-ARCH-006-03  # per-product score
    - TC-ARCH-006-04  # write YAML

  closeout_criteria:
    - "All 4 children CLOSED"
    - "per-product-qname-compliance.yaml written with 30 entries"
```

```yaml
child_taskcard:
  id: TC-ARCH-006-01
  parent_id: TC-ARCH-006
  title: "Grep spec_qname in src/python/ and categorize by format"
  status: TODO

  micro_steps:
    - id: MS-006-01-01
      action: "Run: grep -rl 'spec_qname' src/python/ --include='*.py' | grep -v '__pycache__' | grep -v 'build/' | sort"
      expected_output: "List of ~232 files with spec_qname"
      status: PENDING

    - id: MS-006-01-02
      action: "Group results by format (src/python/{format}/spec/... vs src/python/{format}/models.py)"
      expected_output: "Per-format: count of spec/ files with spec_qname vs Compat/ files"
      status: PENDING

    - id: MS-006-01-03
      action: "For formats with 0 spec_qname in spec/ files: flag as qname-non-compliant"
      expected_output: "List of non-compliant Python formats"
      status: PENDING

    - id: MS-006-01-04
      action: "Check 3 random non-ODF formats (e.g., csv, zst, pbm): what is their spec_qname value?"
      expected_output: "CSV: spec_qname='record' or similar; ZST: may be missing"
      status: PENDING

  next_valid_task: TC-ARCH-006-02
```

```yaml
child_taskcard:
  id: TC-ARCH-006-02
  parent_id: TC-ARCH-006
  title: "Grep SpecQName in src/net/ and categorize by format"
  status: TODO

  micro_steps:
    - id: MS-006-02-01
      action: "Run: grep -rl 'SpecQName' src/net/ --include='*.cs' | grep -v '/bin/' | grep -v '/obj/' | sort"
      expected_output: "~29 files with SpecQName"
      status: PENDING

    - id: MS-006-02-02
      action: "Group results by format; identify which formats have 0 SpecQName files"
      expected_output: "ZST, HTML, Markdown, TXT likely have 0 SpecQName"
      status: PENDING

    - id: MS-006-02-03
      action: "For FODS and FODT: verify Spec/ files have SpecQName const; verify Model/ files reference them"
      expected_output: "Spec/Table/TableCell.cs has SpecQName; Model/FodsCell.cs — check if it references Spec class"
      status: PENDING

  next_valid_task: TC-ARCH-006-03
```

```yaml
child_taskcard:
  id: TC-ARCH-006-03
  parent_id: TC-ARCH-006
  title: "Produce per-product compliance score on 5 dimensions"
  status: TODO

  micro_steps:
    - id: MS-006-03-01
      action: "For each Python format: score spec_dir_exists (1/0), classes_have_spec_qname (1/0), facade_delegates (1/0)"
      expected_output: "20 Python scores"
      status: PENDING

    - id: MS-006-03-02
      action: "For each .NET format: score Spec_dir_exists (1/0), SpecQName_present (1/0), Model_delegates_to_Spec (1/0)"
      expected_output: "10 .NET scores"
      status: PENDING

    - id: MS-006-03-03
      action: "Assign rating: Green (3/3), Yellow (2/3), Orange (1/3), Red (0/3), Gray (insufficient evidence)"
      expected_output: "Per-product rating"
      status: PENDING

  next_valid_task: TC-ARCH-006-04
```

```yaml
child_taskcard:
  id: TC-ARCH-006-04
  parent_id: TC-ARCH-006
  title: "Write reports/archaeology-2026-07-10/per-product-qname-compliance.yaml"
  status: TODO

  micro_steps:
    - id: MS-006-04-01
      action: "Write YAML: per-product entry with spec_dir, spec_qname_coverage, delegation_status, rating"
      target_file: "reports/archaeology-2026-07-10/per-product-qname-compliance.yaml"
      expected_output: "30-entry YAML"
      status: PENDING

    - id: MS-006-04-02
      action: "Write summary: count Green/Yellow/Orange/Red/Gray; note FODS as best, ZST .NET as worst"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-007
```

---

### TC-ARCH-007: Source Quality Review
```yaml
parent_taskcard:
  id: TC-ARCH-007
  title: "Score source quality for each product on 7 professional-library dimensions"
  type: PARENT
  status: PROPOSED
  lane: D
  requirement_ids: [REQ-QUAL-001, REQ-QUAL-002]
  dependencies: [TC-ARCH-004, TC-ARCH-006]

  quality_dimensions:
    - "parser_model_writer_separation: are these 3 responsibilities in separate files?"
    - "object_model_quality: does the object model reflect spec hierarchy?"
    - "api_usability: is the public API clean and documented?"
    - "error_handling: FormatFactoryError hierarchy enforced?"
    - "documentation: docstrings, XML comments, README?"
    - "test_coverage: are there tests for the public API?"
    - "spec_qname_compliance: from TC-ARCH-006"

  children:
    - TC-ARCH-007-01  # Python quality scoring
    - TC-ARCH-007-02  # .NET quality scoring
    - TC-ARCH-007-03  # write quality review
    - TC-ARCH-007-04  # write capability matrix

  closeout_criteria:
    - "All 4 children CLOSED"
    - "src-source-quality-review.md written"
    - "per-product-capability-matrix.yaml written"
```

```yaml
child_taskcard:
  id: TC-ARCH-007-01
  parent_id: TC-ARCH-007
  title: "Score each Python format on 7 quality dimensions"
  status: TODO

  micro_steps:
    - id: MS-007-01-01
      action: "For FODS: read parser.py, models.py, Compat/ — check separation; check docstrings; check FormatFactoryError"
      expected_output: "FODS scores: parser_sep=Y, model=Y, api=Y, error=?, doc=Y, test=Y, qname=Green"
      status: PENDING

    - id: MS-007-01-02
      action: "For CSV: read csv_parser.py, models.py — check separation; note if just 3 spec files"
      expected_output: "CSV scores — likely Yellow (partial spec coverage)"
      status: PENDING

    - id: MS-007-01-03
      action: "For ZST: check if it has proper error handling, docstrings, and tests"
      expected_output: "ZST Python scores"
      status: PENDING

    - id: MS-007-01-04
      action: "For remaining 17 Python formats: sample 2-3 files per format; assign scores based on pattern"
      expected_output: "17 additional format scores"
      completion_check: "All 20 Python formats scored"
      status: PENDING

    - id: MS-007-01-05
      action: "Assign overall rating (Green/Yellow/Orange/Red/Gray) per format"
      expected_output: "20 Python ratings"
      status: PENDING

  next_valid_task: TC-ARCH-007-02
```

```yaml
child_taskcard:
  id: TC-ARCH-007-02
  parent_id: TC-ARCH-007
  title: "Score each .NET format on 7 quality dimensions"
  status: TODO

  micro_steps:
    - id: MS-007-02-01
      action: "For FODS .NET: check FodsParser.cs, FodsWriter.cs, FodsDocument.cs — separation, XML docs, exception hierarchy"
      expected_output: "FODS .NET: likely Yellow-Green (parser/writer/model separated; XML docs exist)"
      status: PENDING

    - id: MS-007-02-02
      action: "For FODT .NET: same check"
      expected_output: "FODT .NET scores"
      status: PENDING

    - id: MS-007-02-03
      action: "For remaining 8 .NET formats: sample key files; assign scores"
      expected_output: "10 .NET ratings"
      completion_check: "All 10 .NET formats scored"
      status: PENDING

    - id: MS-007-02-04
      action: "Check if any .NET format has FormatFactoryException hierarchy"
      expected_output: "Record whether .NET exception hierarchy follows governance rules"
      status: PENDING

  next_valid_task: TC-ARCH-007-03
```

```yaml
child_taskcard:
  id: TC-ARCH-007-03
  parent_id: TC-ARCH-007
  title: "Write reports/archaeology-2026-07-10/src-source-quality-review.md"
  status: TODO

  micro_steps:
    - id: MS-007-03-01
      action: "Write Python quality table: format | sep | model | api | error | doc | test | qname | rating"
      target_file: "reports/archaeology-2026-07-10/src-source-quality-review.md"
      status: PENDING

    - id: MS-007-03-02
      action: "Write .NET quality table with same dimensions"
      status: PENDING

    - id: MS-007-03-03
      action: "Write cross-language parity comparison: which formats are ahead in Python vs .NET?"
      status: PENDING

  next_valid_task: TC-ARCH-007-04
```

```yaml
child_taskcard:
  id: TC-ARCH-007-04
  parent_id: TC-ARCH-007
  title: "Write reports/archaeology-2026-07-10/per-product-capability-matrix.yaml"
  status: TODO

  micro_steps:
    - id: MS-007-04-01
      action: "Write YAML: per-product row with all 27 matrix columns from the archaeology prompt"
      target_file: "reports/archaeology-2026-07-10/per-product-capability-matrix.yaml"
      expected_output: "30 product entries with: parser_load, model, edit, save, export, validation, error_handling, qname, namespace, test_coverage, rating, recommendation"
      status: PENDING

    - id: MS-007-04-02
      action: "Verify: all 30 products have entries; all required columns present"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-008
```

---

### TC-ARCH-008: SAL Audit
```yaml
parent_taskcard:
  id: TC-ARCH-008
  title: "Audit SAL pipeline: fact quality, determinism, manual seeding, format coverage"
  type: PARENT
  status: PROPOSED
  lane: E
  requirement_ids: [REQ-SAL-001, REQ-SAL-002]
  dependencies: [TC-ARCH-001]

  critical_known_finding: |
    spec-to-feature-radical-correction-plan.md states: SAL is 'ghost infrastructure —
    built but dormant'. This audit must verify or refute that claim with file evidence.

  children:
    - TC-ARCH-008-01  # FODS SAL audit
    - TC-ARCH-008-02  # per-format coverage survey
    - TC-ARCH-008-03  # pipeline tool audit
    - TC-ARCH-008-04  # write sal-audit.md

  closeout_criteria:
    - "All 4 children CLOSED"
    - "sal-audit.md written"
    - "Ghost-infrastructure claim verified or refuted"
```

```yaml
child_taskcard:
  id: TC-ARCH-008-01
  parent_id: TC-ARCH-008
  title: "Audit FODS SAL facts (10 manually-seeded facts)"
  status: TODO

  micro_steps:
    - id: MS-008-01-01
      action: "Read .local/spec-cache/fods/1.3/workbench/verified-facts.yaml fully"
      expected_output: "10 facts: FACT-FODS-001 to FACT-FODS-010; seeding_note confirms manual seeding"
      status: PENDING

    - id: MS-008-01-02
      action: "Verify that each fact has: claim_id, claim, provenance.source_sha256, provenance.section_id"
      expected_output: "All 10 facts have provenance — they are tied to specific ODF spec PDF pages"
      completion_check: "provenance.verification_status = 'verified' for all 10"
      status: PENDING

    - id: MS-008-01-03
      action: "Assess: are 10 facts sufficient for a comprehensive ODF FODS spec? (ODF has hundreds of relevant elements)"
      expected_output: "10 facts is deeply insufficient — covers only root elements. Major SAL gap."
      status: PENDING

    - id: MS-008-01-04
      action: "Check TC-0021 status: find any evidence that TC-0021 (richer extraction) was started"
      expected_output: "TC-0021 likely not started — no evidence in .local/spec-cache/"
      status: PENDING

    - id: MS-008-01-05
      action: "Check whether spec PDF can be re-processed: does .local/spec-cache/fods/1.3/normalized/ have parsed content?"
      expected_output: "normalized/ contains text.txt and other extracted content — re-processing is feasible"
      status: PENDING

  next_valid_task: TC-ARCH-008-02
```

```yaml
child_taskcard:
  id: TC-ARCH-008-02
  parent_id: TC-ARCH-008
  title: "Survey per-format spec-cache coverage"
  status: TODO

  micro_steps:
    - id: MS-008-02-01
      action: "List .local/spec-cache/ and for each format dir, check if workbench/ or verified-facts exist"
      expected_output: "Per-format: NO_SPEC / SPEC_ACQUIRED_NO_FACTS / FACTS_SEEDED / FACTS_EXTRACTED"
      status: PENDING

    - id: MS-008-02-02
      action: "For formats without spec-cache entry (toml, tsv, gnumeric etc.): record as SAL gap"
      expected_output: "List of formats with zero SAL infrastructure"
      status: PENDING

    - id: MS-008-02-03
      action: "Check .local/spec-cache/sal-facts-20260621.json: how many formats have entries? how many facts per format?"
      target_file: ".local/spec-cache/sal-facts-20260621.json"
      expected_output: "Combined fact count per format — probably single-digit counts for non-FODS formats"
      status: PENDING

    - id: MS-008-02-04
      action: "Classify: which formats could reasonably get SAL facts (have accessible spec) vs which cannot?"
      expected_output: "FODS/FODT/ODS: ODF spec available; CSV: RFC 4180 available; TOML: spec available; ZST: RFC available; XCF: minimal public spec"
      status: PENDING

  next_valid_task: TC-ARCH-008-03
```

```yaml
child_taskcard:
  id: TC-ARCH-008-03
  parent_id: TC-ARCH-008
  title: "Audit SAL pipeline tools for determinism and automation"
  status: TODO

  micro_steps:
    - id: MS-008-03-01
      action: "Read tools/spec/merge_sal_facts.py — what input dirs does it read? Is it automated?"
      target_file: "tools/spec/merge_sal_facts.py"
      expected_output: "Reads .local/spec-cache/; merges per-format files. Manual trigger, not CI."
      status: PENDING

    - id: MS-008-03-02
      action: "Read tools/spec/generate_canonical_stubs.py — what does it generate from SAL facts?"
      target_file: "tools/spec/generate_canonical_stubs.py"
      expected_output: "Generates skeleton spec/ classes from SAL facts. Key pipeline tool."
      status: PENDING

    - id: MS-008-03-03
      action: "Check tests/supervisor/test_r201_sal003_min_spec_facts_validator.py — what minimum is enforced?"
      target_file: "tests/supervisor/test_r201_sal003_min_spec_facts_validator.py"
      expected_output: "Minimum fact count per format enforced in tests"
      status: PENDING

  next_valid_task: TC-ARCH-008-04
```

```yaml
child_taskcard:
  id: TC-ARCH-008-04
  parent_id: TC-ARCH-008
  title: "Write reports/archaeology-2026-07-10/sal-audit.md"
  status: TODO

  micro_steps:
    - id: MS-008-04-01
      action: "Write: FODS SAL facts analysis (10 facts, manually seeded, provenance exists, TC-0021 not done)"
      target_file: "reports/archaeology-2026-07-10/sal-audit.md"
      status: PENDING

    - id: MS-008-04-02
      action: "Write: per-format coverage table (format, spec_acquired, facts_count, status)"
      status: PENDING

    - id: MS-008-04-03
      action: "Write: verdict on 'ghost infrastructure' claim — is SAL truly dormant? What is actually working?"
      status: PENDING

    - id: MS-008-04-04
      action: "Write: what must be done to make SAL deterministic and comprehensive (TC-0021 unblocking path)"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-009
```

---

### TC-ARCH-009: Capability Layer Audit
```yaml
parent_taskcard:
  id: TC-ARCH-009
  title: "Audit capability layer: does it consume SAL? is output used? is pipeline automated?"
  type: PARENT
  status: PROPOSED
  lane: F
  requirement_ids: [REQ-CAP-001]
  dependencies: [TC-ARCH-008]

  critical_known_finding: |
    spec-to-feature-radical-correction-plan.md: capability layer 'generates output nobody consumes'.
    Verify this claim with file evidence.

  children:
    - TC-ARCH-009-01  # audit capability files
    - TC-ARCH-009-02  # trace pipeline
    - TC-ARCH-009-03  # write audit

  closeout_criteria:
    - "All 3 children CLOSED"
    - "capability-layer-audit.md written"
```

```yaml
child_taskcard:
  id: TC-ARCH-009-01
  parent_id: TC-ARCH-009
  title: "Read capability files and assess SAL fact referencing"
  status: TODO

  micro_steps:
    - id: MS-009-01-01
      action: "Read reports/capability-layer/gap-ledger.json (first 100 lines) — what fields are present?"
      target_file: "reports/capability-layer/gap-ledger.json"
      expected_output: "Gap entries with format_id, capability_id, spec_facts[], qnames[]"
      status: PENDING

    - id: MS-009-01-02
      action: "Check if spec_facts[] in gap-ledger.json references FACT-FODS-001 etc. (SAL fact IDs)"
      expected_output: "YES = capability references SAL; NO = capability is independent of SAL"
      status: PENDING

    - id: MS-009-01-03
      action: "Read product-capability-matrix/fods.yaml — how is it structured? Any SAL references?"
      target_file: "product-capability-matrix/fods.yaml"
      expected_output: "Product matrix with tier, status, test references"
      status: PENDING

    - id: MS-009-01-04
      action: "Read reports/capability-layer/capability_summary.json — what aggregates are present?"
      expected_output: "Per-format capability counts and coverage percentages"
      status: PENDING

  next_valid_task: TC-ARCH-009-02
```

```yaml
child_taskcard:
  id: TC-ARCH-009-02
  parent_id: TC-ARCH-009
  title: "Trace SAL → capability → feature compiler → next-work-items pipeline"
  status: TODO

  micro_steps:
    - id: MS-009-02-01
      action: "Read tools/supervisor/capability_feature_compiler.py — what does it read as input?"
      target_file: "tools/supervisor/capability_feature_compiler.py"
      expected_output: "Reads gap-ledger.json; produces next-work-items.json or similar"
      status: PENDING

    - id: MS-009-02-02
      action: "Check: does next-work-items.json reference SAL fact IDs?"
      target_file: ".local/supervisor/next-work-items.json"
      expected_output: "If spec_fact_ids[] absent → capability→feature pipeline has no SAL grounding"
      status: PENDING

    - id: MS-009-02-03
      action: "Check: is any tool that reads next-work-items.json called automatically (CI, hooks, supervisor cycle)?"
      expected_output: "Determine if output is consumed vs sits unused"
      status: PENDING

    - id: MS-009-02-04
      action: "Record: at which pipeline stage does SAL connection break? SAL→capability? capability→feature? feature→code?"
      expected_output: "Identify exact break point"
      status: PENDING

  next_valid_task: TC-ARCH-009-03
```

```yaml
child_taskcard:
  id: TC-ARCH-009-03
  parent_id: TC-ARCH-009
  title: "Write reports/archaeology-2026-07-10/capability-layer-audit.md"
  status: TODO

  micro_steps:
    - id: MS-009-03-01
      action: "Write: gap-ledger SAL reference analysis (does/doesn't reference SAL facts)"
      target_file: "reports/archaeology-2026-07-10/capability-layer-audit.md"
      status: PENDING

    - id: MS-009-03-02
      action: "Write: pipeline trace diagram (SAL → cap → compiler → work items) with break points marked"
      status: PENDING

    - id: MS-009-03-03
      action: "Write: verdict on 'output nobody consumes' claim with evidence"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-010
```

---

### TC-ARCH-010: Downstream Generation Audit
```yaml
parent_taskcard:
  id: TC-ARCH-010
  title: "Identify where malformed source enters; assess product deepening bypass risk"
  type: PARENT
  status: PROPOSED
  lane: G
  requirement_ids: [REQ-GEN-001]
  dependencies: [TC-ARCH-009]

  children:
    - TC-ARCH-010-01  # audit generation tools
    - TC-ARCH-010-02  # trace malformed code entry
    - TC-ARCH-010-03  # write audit

  closeout_criteria:
    - "All 3 children CLOSED"
    - "downstream-generation-audit.md written"
```

```yaml
child_taskcard:
  id: TC-ARCH-010-01
  parent_id: TC-ARCH-010
  title: "Read generation tools and assess what they produce"
  status: TODO

  micro_steps:
    - id: MS-010-01-01
      action: "Read tools/spec/generate_canonical_stubs.py — does it produce spec-hierarchy files? qname-named classes?"
      expected_output: "Stubs with spec_qname, spec_fact_ref embedded from SAL"
      status: PENDING

    - id: MS-010-01-02
      action: "Read tools/supervisor/product_feature_factory.py — what product source does it create?"
      expected_output: "Feature factories for gap-ledger items"
      status: PENDING

    - id: MS-010-01-03
      action: "Check V125/V126 in governance_validators_ext4.py — do they actually block new format dirs without qname plan?"
      target_file: "tools/supervisor/governance_validators_ext4.py"
      expected_output: "V125: blocks new format dirs not in qname-code-organization-plan.yaml; V126: blocks files outside approved subdirs"
      status: PENDING

    - id: MS-010-01-04
      action: "Check: does qname-code-organization-plan.yaml exist? what formats are approved?"
      expected_output: "If missing → V125/V126 may not block effectively"
      status: PENDING

  next_valid_task: TC-ARCH-010-02
```

```yaml
child_taskcard:
  id: TC-ARCH-010-02
  parent_id: TC-ARCH-010
  title: "Trace where malformed/format-prefixed source code enters"
  status: TODO

  micro_steps:
    - id: MS-010-02-01
      action: "Check add-python-api.md skill — does it require qname-to-code-map lookup before writing any class?"
      target_file: ".claude/commands/add-python-api.md"
      expected_output: "YES → skill enforces qname; OR NO → bypass is possible"
      status: PENDING

    - id: MS-010-02-02
      action: "Check product-source-task.md — does it enforce qname registry use?"
      target_file: ".claude/commands/product-source-task.md"
      expected_output: "Must enforce qname to prevent format-prefixed classes being written directly"
      status: PENDING

    - id: MS-010-02-03
      action: "Check governance_validators.py for V45 (or similar) that catches format-prefixed class names outside Compat/"
      expected_output: "If V45 catches FodsXxx outside Compat/ → Gen 1 code can't be newly introduced"
      status: PENDING

    - id: MS-010-02-04
      action: "Scenario test: if an agent bypasses skills and writes 'class FooDocument:' in src/python/foo/models.py without spec_qname — which validator catches it?"
      expected_output: "V111 or V112 should catch missing spec_qname; record which validator fires"
      status: PENDING

  next_valid_task: TC-ARCH-010-03
```

```yaml
child_taskcard:
  id: TC-ARCH-010-03
  parent_id: TC-ARCH-010
  title: "Write reports/archaeology-2026-07-10/downstream-generation-audit.md"
  status: TODO

  micro_steps:
    - id: MS-010-03-01
      action: "Write: generation tools summary (stub generator, feature factory, what they produce)"
      target_file: "reports/archaeology-2026-07-10/downstream-generation-audit.md"
      status: PENDING

    - id: MS-010-03-02
      action: "Write: malformed code entry point analysis (which paths allow bypass, which are blocked)"
      status: PENDING

    - id: MS-010-03-03
      action: "Write: bypass risk assessment — HIGH/MEDIUM/LOW with specific bypass scenarios"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-011
```

---

### TC-ARCH-011: Skill Inventory and Gaps
```yaml
parent_taskcard:
  id: TC-ARCH-011
  title: "Inventory all product-touching skills and score their qname/SAL/capability enforcement"
  type: PARENT
  status: PROPOSED
  lane: H
  requirement_ids: [REQ-SKILL-001]
  dependencies: [TC-ARCH-010]

  children:
    - TC-ARCH-011-01  # read and score skills
    - TC-ARCH-011-02  # identify gaps
    - TC-ARCH-011-03  # write audit

  skills_to_audit:
    - ".claude/commands/add-python-api.md"
    - ".claude/commands/add-dotnet-api.md"
    - ".claude/commands/product-source-task.md"
    - ".claude/commands/qname-backfill.md"
    - ".claude/commands/spec-literal-qname-to-code-mapping.md"
    - ".claude/commands/spec-parity-verification.md"
    - ".claude/commands/python-reduced-spec-parity-model.md"
    - ".claude/commands/implement-spec-stub.md"
    - ".supervisor/skill-registry.yaml"

  closeout_criteria:
    - "All 3 children CLOSED"
    - "skill-inventory-and-gaps.md written"
```

```yaml
child_taskcard:
  id: TC-ARCH-011-01
  parent_id: TC-ARCH-011
  title: "Read each product-touching skill and score on enforcement dimensions"
  status: TODO

  enforcement_scoring_dimensions:
    - "qname_enforced: does skill require spec_qname before writing any class?"
    - "sal_enforced: does skill require SAL fact reference?"
    - "capability_enforced: does skill reference capability registry?"
    - "evidence_required: does skill mandate evidence declaration?"
    - "repeatability: can skill produce same output from same inputs?"

  micro_steps:
    - id: MS-011-01-01
      action: "Read .claude/commands/add-python-api.md and score on 5 dimensions"
      expected_output: "add-python-api: qname=YES, sal=PARTIAL, capability=PARTIAL, evidence=YES, repeatability=MEDIUM"
      status: PENDING

    - id: MS-011-01-02
      action: "Read .claude/commands/add-dotnet-api.md and score on 5 dimensions"
      expected_output: "add-dotnet-api scores"
      status: PENDING

    - id: MS-011-01-03
      action: "Read .claude/commands/product-source-task.md and score"
      expected_output: "product-source-task scores"
      status: PENDING

    - id: MS-011-01-04
      action: "Read .claude/commands/qname-backfill.md and score — also assess whether it can handle all 30 products"
      expected_output: "qname-backfill capability assessment"
      status: PENDING

    - id: MS-011-01-05
      action: "Read .supervisor/skill-registry.yaml — is every skill registered? any missing from registry?"
      expected_output: "Registry completeness: N registered, M found in commands/"
      status: PENDING

  next_valid_task: TC-ARCH-011-02
```

```yaml
child_taskcard:
  id: TC-ARCH-011-02
  parent_id: TC-ARCH-011
  title: "Identify skill gaps that allow qname/SAL bypass"
  status: TODO

  micro_steps:
    - id: MS-011-02-01
      action: "Identify: what product modification can an agent make that NO skill requires to go through qname check?"
      expected_output: "Gap list: e.g., direct edit of Compat/ files, direct analytics file creation"
      status: PENDING

    - id: MS-011-02-02
      action: "Identify: which skills have no SAL fact requirement (can produce product code without any spec grounding)?"
      expected_output: "List of skills without SAL requirement"
      status: PENDING

    - id: MS-011-02-03
      action: "Record: V111-V127 validators as safety net — which bypass scenarios do they catch even without skill enforcement?"
      expected_output: "Gap matrix: bypassed by skill vs caught by validator vs uncaught"
      status: PENDING

  next_valid_task: TC-ARCH-011-03
```

```yaml
child_taskcard:
  id: TC-ARCH-011-03
  parent_id: TC-ARCH-011
  title: "Write reports/archaeology-2026-07-10/skill-inventory-and-gaps.md"
  status: TODO

  micro_steps:
    - id: MS-011-03-01
      action: "Write: skill inventory table (skill_id, qname, sal, capability, evidence, repeatability)"
      target_file: "reports/archaeology-2026-07-10/skill-inventory-and-gaps.md"
      status: PENDING

    - id: MS-011-03-02
      action: "Write: gap analysis — what bypasses exist, what validators catch them, what is uncaught"
      status: PENDING

    - id: MS-011-03-03
      action: "Write: recommended skill hardening actions (which skills need which enforcement added)"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-012
```

---

### TC-ARCH-012: Autonomous Supervisor Audit
```yaml
parent_taskcard:
  id: TC-ARCH-012
  title: "Audit check_continuation.py, GOV_BLOCK, and Gate 11 stop enforcement"
  type: PARENT
  status: PROPOSED
  lane: I
  requirement_ids: [REQ-SUP-001]
  dependencies: [TC-ARCH-011]

  children:
    - TC-ARCH-012-01  # check_continuation audit
    - TC-ARCH-012-02  # autonomous_cycle audit
    - TC-ARCH-012-03  # write audit

  closeout_criteria:
    - "All 3 children CLOSED"
    - "autonomous-supervisor-audit.md written"
```

```yaml
child_taskcard:
  id: TC-ARCH-012-01
  parent_id: TC-ARCH-012
  title: "Audit check_continuation.py gates"
  status: TODO

  micro_steps:
    - id: MS-012-01-01
      action: "Read tools/supervisor/check_continuation.py — what conditions trigger STOP?"
      expected_output: "STOP conditions: SESSION_MISMATCH, CHAT_ID_MISMATCH, POST_PLAN_TERMINAL, GOV_BLOCK, PLAN_ACTIVE"
      status: PENDING

    - id: MS-012-01-02
      action: "Identify: does check_continuation.py read rework_items for GOV_BLOCK validators?"
      expected_output: "Confirm GOV_BLOCK mechanism: rework_items contains 4 named validators"
      status: PENDING

    - id: MS-012-01-03
      action: "Identify: what stops product deepening when Gate 11 is in progress? Is there a code gate?"
      expected_output: "Gate 11 stop may be advisory-only (next-sprint.md instruction) vs code-enforced"
      status: PENDING

    - id: MS-012-01-04
      action: "Check: is overclaim detector invoked in check_continuation or autonomous_cycle?"
      expected_output: "CLAUDE.md says 'overclaim detector is never called' — verify this claim"
      status: PENDING

  next_valid_task: TC-ARCH-012-02
```

```yaml
child_taskcard:
  id: TC-ARCH-012-02
  parent_id: TC-ARCH-012
  title: "Audit autonomous_cycle.py pipeline"
  status: TODO

  micro_steps:
    - id: MS-012-02-01
      action: "Read tools/supervisor/autonomous_cycle.py (first 80 lines) — what pipeline steps does it run?"
      expected_output: "Pipeline: declaration validation → grading → gap-ledger update → next-sprint generation"
      status: PENDING

    - id: MS-012-02-02
      action: "Check: does autonomous_cycle.py invoke SAL or capability tools?"
      expected_output: "If NOT → autonomy loop is disconnected from SAL/capability pipeline"
      status: PENDING

    - id: MS-012-02-03
      action: "Check: does autonomous_cycle.py invoke governance_validators_sal.py?"
      expected_output: "If YES → SAL ratio check is in the loop; if NO → SAL is bypassed per-cycle"
      status: PENDING

  next_valid_task: TC-ARCH-012-03
```

```yaml
child_taskcard:
  id: TC-ARCH-012-03
  parent_id: TC-ARCH-012
  title: "Write reports/archaeology-2026-07-10/autonomous-supervisor-audit.md"
  status: TODO

  micro_steps:
    - id: MS-012-03-01
      action: "Write: stop condition analysis — what STOP verdicts exist, what they enforce"
      target_file: "reports/archaeology-2026-07-10/autonomous-supervisor-audit.md"
      status: PENDING

    - id: MS-012-03-02
      action: "Write: GOV_BLOCK mechanism effectiveness — does it actually prevent product deepening after structural failures?"
      status: PENDING

    - id: MS-012-03-03
      action: "Write: overclaim detector gap — confirm it's not called and what that means"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-013
```

---

### TC-ARCH-013: Lane Separation and Collision Risk
```yaml
parent_taskcard:
  id: TC-ARCH-013
  title: "Audit lane separation enforcement and identify collision risks"
  type: PARENT
  status: PROPOSED
  lane: I
  requirement_ids: [REQ-SUP-002]
  dependencies: [TC-ARCH-012]

  children:
    - TC-ARCH-013-01  # read correction plan lane structure
    - TC-ARCH-013-02  # test enforcement strength
    - TC-ARCH-013-03  # write audit

  closeout_criteria:
    - "All 3 children CLOSED"
    - "lane-separation-and-collision-risk.md written"
```

```yaml
child_taskcard:
  id: TC-ARCH-013-01
  parent_id: TC-ARCH-013
  title: "Read spec-to-feature-radical-correction-plan.md lane structure"
  status: TODO

  micro_steps:
    - id: MS-013-01-01
      action: "Read plans/strategic/spec-to-feature-radical-correction-plan.md sections describing Lanes 1-15"
      expected_output: "Lane definitions: Lane 1-6 = system healing; Lane 7-13 = product generation; Lane 14-15 = enforcement"
      status: PENDING

    - id: MS-013-01-02
      action: "Check: does the plan define explicit gates between Lanes 1-6 and Lanes 7-13?"
      expected_output: "Gate definition: Lane 6 must complete before Lane 7 starts"
      status: PENDING

    - id: MS-013-01-03
      action: "Read docs/spec-to-feature-correction-plan-summary.md for quick lane enforcement summary"
      expected_output: "Summary of enforcement gaps noted"
      status: PENDING

  next_valid_task: TC-ARCH-013-02
```

```yaml
child_taskcard:
  id: TC-ARCH-013-02
  parent_id: TC-ARCH-013
  title: "Test lane enforcement strength"
  status: TODO

  micro_steps:
    - id: MS-013-02-01
      action: "Check: is there any code that enforces 'Lane 1-6 must complete before Lane 7-13'?"
      expected_output: "Likely: PROMPT_ONLY enforcement — no code gate. CLAUDE.md says 'Lane ownership and DAG ordering are NOT enforced by code (prompt-only)'"
      status: PENDING

    - id: MS-013-02-02
      action: "Check: could an agent start product deepening (Lane 7) while SAL is still dormant (Lane 1-3 incomplete)?"
      expected_output: "YES if governance validators don't block it. Identify which validator would catch this."
      status: PENDING

    - id: MS-013-02-03
      action: "Check tools/supervisor/stop_reason_adjudicator.py — does it handle lane contamination?"
      target_file: "tools/supervisor/stop_reason_adjudicator.py"
      expected_output: "Adjudicator handles approval-blocked and blocked labels; may not enforce lane order"
      status: PENDING

    - id: MS-013-02-04
      action: "Identify: which validator (if any) blocks product deepening when SAL has < 10 facts?"
      expected_output: "V_VALIDATE_CAPABILITY_FACT_RATIO (in governance_validators_sal.py) may enforce; check threshold"
      status: PENDING

  next_valid_task: TC-ARCH-013-03
```

```yaml
child_taskcard:
  id: TC-ARCH-013-03
  parent_id: TC-ARCH-013
  title: "Write reports/archaeology-2026-07-10/lane-separation-and-collision-risk.md"
  status: TODO

  micro_steps:
    - id: MS-013-03-01
      action: "Write: lane structure map (Lanes 1-15 with healing vs generation classification)"
      target_file: "reports/archaeology-2026-07-10/lane-separation-and-collision-risk.md"
      status: PENDING

    - id: MS-013-03-02
      action: "Write: enforcement gap analysis — which gates are prompt-only vs code-enforced"
      status: PENDING

    - id: MS-013-03-03
      action: "Write: collision risk scenarios (3-5 specific scenarios where product deepening contaminates healing)"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-014
```

---

### TC-ARCH-014: Backfill Facility Design
```yaml
parent_taskcard:
  id: TC-ARCH-014
  title: "Assess /qname-backfill skill and design systematic backfill plan for all 30 products"
  type: PARENT
  status: PROPOSED
  lane: J
  requirement_ids: [REQ-BACK-001]
  dependencies: [TC-ARCH-006, TC-ARCH-007]

  children:
    - TC-ARCH-014-01  # assess existing backfill
    - TC-ARCH-014-02  # design backfill sequence
    - TC-ARCH-014-03  # write design doc

  closeout_criteria:
    - "All 3 children CLOSED"
    - "backfill-facility-design.md written"
    - "Backfill sequencing plan with risk per format"
```

```yaml
child_taskcard:
  id: TC-ARCH-014-01
  parent_id: TC-ARCH-014
  title: "Assess /qname-backfill skill and migration-plan.yaml"
  status: TODO

  micro_steps:
    - id: MS-014-01-01
      action: "Read .claude/commands/qname-backfill.md fully"
      expected_output: "Backfill skill: what it does, what inputs it needs, what outputs it produces"
      status: PENDING

    - id: MS-014-01-02
      action: "Read registry/odf-ontology/migration-plan.yaml"
      expected_output: "Migration plan: which classes need migration, what the target is"
      status: PENDING

    - id: MS-014-01-03
      action: "Check: has /qname-backfill been applied to any format yet? Search for backfill evidence in .local/"
      expected_output: "Determine if backfill has ever run vs is still untested"
      status: PENDING

    - id: MS-014-01-04
      action: "Assess: can /qname-backfill handle non-ODF formats (CSV, ZST, etc.) or only ODF?"
      expected_output: "Backfill may only apply to ODF formats with formal qname namespace"
      status: PENDING

  next_valid_task: TC-ARCH-014-02
```

```yaml
child_taskcard:
  id: TC-ARCH-014-02
  parent_id: TC-ARCH-014
  title: "Design systematic backfill sequencing"
  status: TODO

  micro_steps:
    - id: MS-014-02-01
      action: "Design ODF format backfill sequence: FODS → FODT → ODS → ODT → FODP → FODG → ABW (increasing complexity)"
      expected_output: "Ordered list with dependencies noted"
      status: PENDING

    - id: MS-014-02-02
      action: "Design non-ODF backfill approach: CSV (RFC 4180 record), TOML (TOML table), ZST (frame/chunk)"
      expected_output: "Non-ODF needs custom canonical naming scheme per format"
      status: PENDING

    - id: MS-014-02-03
      action: "Assess migration risk per format: LOW (FODS — already Gen 4), MEDIUM (FODT), HIGH (ZST)"
      expected_output: "Risk assessment for each format's backfill"
      status: PENDING

    - id: MS-014-02-04
      action: "Design rollback plan: if backfill breaks a format, how to revert without losing data"
      expected_output: "Rollback strategy: git revert at format level"
      status: PENDING

  next_valid_task: TC-ARCH-014-03
```

```yaml
child_taskcard:
  id: TC-ARCH-014-03
  parent_id: TC-ARCH-014
  title: "Write reports/archaeology-2026-07-10/backfill-facility-design.md"
  status: TODO

  micro_steps:
    - id: MS-014-03-01
      action: "Write: /qname-backfill skill capability assessment (what it can/cannot handle)"
      target_file: "reports/archaeology-2026-07-10/backfill-facility-design.md"
      status: PENDING

    - id: MS-014-03-02
      action: "Write: backfill sequencing plan with risk levels per format"
      status: PENDING

    - id: MS-014-03-03
      action: "Write: missing backfill infrastructure gaps (what needs to be built vs already exists)"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-015
```

---

### TC-ARCH-015: Gate 11 Readiness Review
```yaml
parent_taskcard:
  id: TC-ARCH-015
  title: "Score FODS, FODT, NetPBM against Gate 11 C1-C20/.NET and P1-P11/Python criteria"
  type: PARENT
  status: PROPOSED
  lane: K
  requirement_ids: [REQ-GATE-001]
  dependencies: [TC-ARCH-007]

  children:
    - TC-ARCH-015-01  # read gate criteria
    - TC-ARCH-015-02  # score candidates
    - TC-ARCH-015-03  # write review

  known_finding: "G11-G sub-gate approved 2026-06-05 by Babar Raza. Full Gate 11 not approved."

  closeout_criteria:
    - "All 3 children CLOSED"
    - "gate11-readiness-review.md written"
    - "Score table for each Gate 11 candidate"
```

```yaml
child_taskcard:
  id: TC-ARCH-015-01
  parent_id: TC-ARCH-015
  title: "Read gate11-criteria.yaml and understand C1-C20, P1-P11"
  status: TODO

  micro_steps:
    - id: MS-015-01-01
      action: "Read registry/gate11-criteria.yaml fully"
      expected_output: "C1-C20 (.NET) and P1-P11 (Python) criteria with pass/fail rules"
      status: PENDING

    - id: MS-015-01-02
      action: "Read registry/format-registry.yaml FODS entry gate status section"
      expected_output: "FODS gate status: G11-G approved, pyrel/nuget status"
      status: PENDING

    - id: MS-015-01-03
      action: "Read reports/supervisor/approval-gates.md"
      expected_output: "Current gate state summary"
      status: PENDING

  next_valid_task: TC-ARCH-015-02
```

```yaml
child_taskcard:
  id: TC-ARCH-015-02
  parent_id: TC-ARCH-015
  title: "Score FODS, FODT, NetPBM against all Gate 11 criteria"
  status: TODO

  micro_steps:
    - id: MS-015-02-01
      action: "For FODS .NET: score against C1-C20 criteria (load, edit, save, export, error handling, etc.)"
      expected_output: "FODS .NET score: N/20 criteria met"
      status: PENDING

    - id: MS-015-02-02
      action: "For FODT .NET: score against C1-C20 criteria"
      expected_output: "FODT .NET score"
      status: PENDING

    - id: MS-015-02-03
      action: "For NetPBM .NET: score against C1-C20 criteria"
      expected_output: "NetPBM .NET score"
      status: PENDING

    - id: MS-015-02-04
      action: "For FODS Python: score against P1-P11 criteria"
      expected_output: "FODS Python score: N/11 criteria met"
      status: PENDING

    - id: MS-015-02-05
      action: "Determine: which criteria are blockers for full Gate 11? What is the gap?"
      expected_output: "Specific unmet criteria that block Gate 11 approval"
      status: PENDING

  next_valid_task: TC-ARCH-015-03
```

```yaml
child_taskcard:
  id: TC-ARCH-015-03
  parent_id: TC-ARCH-015
  title: "Write reports/archaeology-2026-07-10/gate11-readiness-review.md"
  status: TODO

  micro_steps:
    - id: MS-015-03-01
      action: "Write: Gate 11 criteria reference (C1-C20, P1-P11)"
      target_file: "reports/archaeology-2026-07-10/gate11-readiness-review.md"
      status: PENDING

    - id: MS-015-03-02
      action: "Write: per-candidate score table (criteria | FODS.NET | FODT.NET | NetPBM.NET | FODS.Py)"
      status: PENDING

    - id: MS-015-03-03
      action: "Write: recommended gate closure path — what exactly needs to change before Babar Raza can review?"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-016
```

---

### TC-ARCH-016: System Gap Matrix
```yaml
parent_taskcard:
  id: TC-ARCH-016
  title: "Synthesize all gaps from lanes A-K into system-gap-matrix.yaml"
  type: PARENT
  status: PROPOSED
  lane: ALL
  requirement_ids: [REQ-GAP-001]
  dependencies:
    - TC-ARCH-001 through TC-ARCH-015 (all must be CLOSED or CHILDREN_IN_PROGRESS)

  objective: "Produce complete gap matrix with severity, impact, and must-fix classification"
  outcome: "reports/archaeology-2026-07-10/system-gap-matrix.yaml"

  pre_seeded_known_gaps:
    - GAP-SAL-001: "Only 10 manually-seeded FODS facts; TC-0021 (richer extraction) not done"
    - GAP-SAL-002: "TOML has no SAL facts or spec cache entry"
    - GAP-SAL-003: "SAL → capability connection is indirect/manual — not automated pipeline"
    - GAP-QNAME-001: "canonical-class-inventory.yaml stale (2026-06-15)"
    - GAP-QNAME-002: "qname-to-code-map.yaml references non-existent src/FormatFactory/ shared namespace"
    - GAP-HYGIENE-001: "11/20 Python formats have build/ artifact inside source"
    - GAP-HYGIENE-002: "20+ egg-info dirs in src/python/"
    - GAP-HYGIENE-003: "All 10 .NET formats have bin/obj inside source"
    - GAP-SPEC-001: "Most Python formats have only 3 spec files (insufficient spec hierarchy)"
    - GAP-NET-001: "ZST .NET has no Spec/ dir — Gen 1 only"
    - GAP-NET-002: "No shared .NET canonical namespace (each format duplicates Office/Table/Text)"
    - GAP-BACKFILL-001: "No systematic backfill applied to 19/20 Python formats"
    - GAP-LANE-001: "Lane order enforced by prompt-only, not code"
    - GAP-CAP-001: "Capability layer output not consumed by autonomous loop (ghost output)"
    - GAP-SUP-001: "Overclaim detector never called"

  children:
    - TC-ARCH-016-01  # collect gaps from all taskcards
    - TC-ARCH-016-02  # classify severity and must-fix
    - TC-ARCH-016-03  # write gap matrix YAML

  closeout_criteria:
    - "All 3 children CLOSED"
    - "system-gap-matrix.yaml written with coverage of all 11 lanes"
```

```yaml
child_taskcard:
  id: TC-ARCH-016-01
  parent_id: TC-ARCH-016
  title: "Collect all gaps from TC-ARCH-001 through TC-ARCH-015"
  status: TODO
  depends_on: [TC-ARCH-001, TC-ARCH-002, TC-ARCH-003, TC-ARCH-004, TC-ARCH-005,
               TC-ARCH-006, TC-ARCH-007, TC-ARCH-008, TC-ARCH-009, TC-ARCH-010,
               TC-ARCH-011, TC-ARCH-012, TC-ARCH-013, TC-ARCH-014, TC-ARCH-015]

  micro_steps:
    - id: MS-016-01-01
      action: "Read each report file written by TC-ARCH-001 to TC-ARCH-015 and extract gap findings"
      expected_output: "Consolidated list of all unique gaps"
      completion_check: "All 15 report files read; gaps extracted"
      status: PENDING

    - id: MS-016-01-02
      action: "Add pre-seeded known gaps (GAP-SAL-001 through GAP-SUP-001) from this plan"
      expected_output: "Full gap list: 15+ pre-seeded + newly discovered from audit"
      status: PENDING

    - id: MS-016-01-03
      action: "Deduplicate: merge identical gaps found across multiple lane audits"
      expected_output: "Deduplicated gap list with canonical IDs"
      status: PENDING

    - id: MS-016-01-04
      action: "Assign stable GAP-DOMAIN-NNN IDs to all gaps"
      expected_output: "Complete gap list with IDs"
      status: PENDING

  next_valid_task: TC-ARCH-016-02
```

```yaml
child_taskcard:
  id: TC-ARCH-016-02
  parent_id: TC-ARCH-016
  title: "Classify each gap by severity and must-fix-before-deepening"
  status: TODO

  severity_levels: "BLOCKER | HIGH | MEDIUM | LOW | ADVISORY"
  must_fix_logic: |
    BLOCKER gaps: yes — cannot ship without fixing
    HIGH gaps affecting code generation or spec authority: yes
    HIGH gaps affecting source hygiene: no (but recommended)
    MEDIUM gaps: no (defer)
    LOW/ADVISORY: no

  micro_steps:
    - id: MS-016-02-01
      action: "For each gap: assign severity based on: product impact × repeatability impact × qname impact"
      expected_output: "Per-gap severity"
      status: PENDING

    - id: MS-016-02-02
      action: "For each gap: set must_fix_before_product_deepening = yes/no based on classification logic"
      expected_output: "Per-gap must-fix flag"
      status: PENDING

    - id: MS-016-02-03
      action: "Count: how many gaps are BLOCKER/HIGH must-fix? This determines overall system readiness."
      expected_output: "Readiness count: N BLOCKER, M HIGH-must-fix gaps"
      status: PENDING

  next_valid_task: TC-ARCH-016-03
```

```yaml
child_taskcard:
  id: TC-ARCH-016-03
  parent_id: TC-ARCH-016
  title: "Write reports/archaeology-2026-07-10/system-gap-matrix.yaml"
  status: TODO

  micro_steps:
    - id: MS-016-03-01
      action: "Write YAML: per-gap entries with all required fields (gap_id, layer, lane, severity, evidence, current_behavior, expected_behavior, root_cause, impact, must_fix, can_defer, suggested_taskcard)"
      target_file: "reports/archaeology-2026-07-10/system-gap-matrix.yaml"
      expected_output: "Complete YAML with N entries covering all 11 lanes"
      status: PENDING

    - id: MS-016-03-02
      action: "Add summary section: total gaps by severity, total must-fix, lanes with most gaps"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-017
```

---

### TC-ARCH-017: Taskcards
```yaml
parent_taskcard:
  id: TC-ARCH-017
  title: "Convert system gaps into governed taskcards in 16 required groups"
  type: PARENT
  status: PROPOSED
  lane: ALL
  requirement_ids: [REQ-TC-001]
  dependencies: [TC-ARCH-016]

  required_taskcard_groups:
    - QNAME-AUTH: "qname authority establishment"
    - QNAME-REGISTRY: "registry updates (canonical-class-inventory staleness)"
    - QNAME-VALIDATORS: "validator hardening (V111-V127 completeness)"
    - QNAME-BACKFILL: "per-format backfill execution"
    - SAL-REPAIR: "SAL completeness (TC-0021 unblocking, per-format facts)"
    - CAPABILITY-REPAIR: "SAL→capability pipeline automation"
    - FEATURE-COMPILER: "capability→feature compiler integration"
    - SKILL-HARDENING: "skill qname/SAL enforcement gaps"
    - SRC-STANDARDIZATION: "spec/ depth normalization across all formats"
    - SOURCE-HYGIENE: "build artifact removal from src/"
    - SUPERVISOR-LANES: "lane order code enforcement"
    - SUPERVISOR-CONTINUATION: "overclaim detector wiring"
    - GATE11-STOP: "Gate 11 stop behavior hardening"
    - PRODUCT-PILOT: "FODS+FODT proof-of-quality pilot"
    - CROSS-LANGUAGE-PARITY: ".NET/Python conceptual alignment"
    - EVIDENCE-LEDGER: "product-code-change-ledger completeness"

  children:
    - TC-ARCH-017-01  # convert must-fix gaps to taskcards
    - TC-ARCH-017-02  # write taskcards.yaml

  closeout_criteria:
    - "All 2 children CLOSED"
    - "taskcards.yaml written with 16 groups populated"
```

```yaml
child_taskcard:
  id: TC-ARCH-017-01
  parent_id: TC-ARCH-017
  title: "Convert all must-fix gaps into governed taskcards in 16 groups"
  status: TODO

  micro_steps:
    - id: MS-017-01-01
      action: "For each BLOCKER and HIGH must-fix gap: create a taskcard entry in the correct group"
      expected_output: "N taskcards across 16 groups"
      status: PENDING

    - id: MS-017-01-02
      action: "For each taskcard: fill required fields (id, title, lane, status=PROPOSED, severity, allowed_paths, forbidden_paths, purpose, problem, evidence, required_change, steps, tests_required, evidence_required, closeout, rollback, dependencies, gate_impact)"
      expected_output: "Complete taskcard entries"
      status: PENDING

    - id: MS-017-01-03
      action: "Assign stable taskcard IDs using group prefix: TC-SAL-001, TC-QNAME-001, TC-HYGIENE-001, etc."
      expected_output: "Stable IDs assigned"
      status: PENDING

    - id: MS-017-01-04
      action: "Build dependency graph between taskcards: SAL-REPAIR must precede CAPABILITY-REPAIR; QNAME-BACKFILL needs QNAME-REGISTRY first"
      expected_output: "Dependency map between taskcard groups"
      status: PENDING

  next_valid_task: TC-ARCH-017-02
```

```yaml
child_taskcard:
  id: TC-ARCH-017-02
  parent_id: TC-ARCH-017
  title: "Write reports/archaeology-2026-07-10/taskcards.yaml"
  status: TODO

  micro_steps:
    - id: MS-017-02-01
      action: "Write YAML with 16 taskcard groups, each containing their taskcards"
      target_file: "reports/archaeology-2026-07-10/taskcards.yaml"
      expected_output: "Complete YAML: 16 groups, N taskcards total"
      status: PENDING

    - id: MS-017-02-02
      action: "Write dependency_order section: what must execute before what"
      status: PENDING

    - id: MS-017-02-03
      action: "Verify: all 16 required groups are non-empty"
      expected_output: "count_by_group >= 1 for all 16"
      status: PENDING

  closes_parent: true
  next_valid_task: TC-ARCH-018
```

---

### TC-ARCH-018: Final Verdict
```yaml
parent_taskcard:
  id: TC-ARCH-018
  title: "Answer all 36 investigation questions, deliver verdict, write execution prompt, bundle evidence"
  type: PARENT
  status: PROPOSED
  lane: ALL
  requirement_ids: [REQ-VERD-001]
  dependencies: [TC-ARCH-001 through TC-ARCH-017 — ALL must be CLOSED]

  objective: "Produce the final verdict and complete evidence bundle for the user"
  outcome:
    - "reports/archaeology-2026-07-10/final-verdict.md"
    - "reports/archaeology-2026-07-10/next-agent-execution-prompt.md"
    - "reports/archaeology-2026-07-10/evidence-bundle.zip"
    - "reports/archaeology-2026-07-10/sprint-overview.md"
    - "reports/archaeology-2026-07-10/machinery-repair-plan.md"
    - "reports/archaeology-2026-07-10/product-pilot-plan.md"
    - "reports/archaeology-2026-07-10/product-deepening-readiness-plan.md"
    - "reports/archaeology-2026-07-10/evidence-index.md"
    - "reports/archaeology-2026-07-10/qname-translation-standard.md"

  children:
    - TC-ARCH-018-01  # answer 36 investigation questions
    - TC-ARCH-018-02  # answer 21 self-check questions
    - TC-ARCH-018-03  # write verdict + supplemental reports
    - TC-ARCH-018-04  # write next-agent-execution-prompt.md
    - TC-ARCH-018-05  # package evidence bundle + sprint-overview

  closeout_criteria:
    - "All 5 children CLOSED"
    - "All 27 required artifacts exist"
    - "evidence-bundle.zip SHA-256 printed with absolute path"
    - "Final verdict is one of: READY_FOR_PRODUCT_DEEPENING / READY_AFTER_TARGETED_MACHINERY_REPAIRS / NOT_READY_REPAIR_MACHINERY_FIRST / DISCOVERY_INCONCLUSIVE_MORE_AUDIT_REQUIRED"
```

```yaml
child_taskcard:
  id: TC-ARCH-018-01
  parent_id: TC-ARCH-018
  title: "Answer all 36 investigation questions with evidence references"
  status: TODO

  micro_steps:
    - id: MS-018-01-01
      action: "Read all reports written by TC-ARCH-001 to TC-ARCH-017 to gather evidence"
      expected_output: "All 27 report files confirmed present and non-empty"
      status: PENDING

    - id: MS-018-01-02
      action: "For each investigation question Q1-Q36: write evidence-backed answer (1-3 sentences + evidence path)"
      expected_output: "36 answered questions with evidence citations"
      status: PENDING

    - id: MS-018-01-03
      action: "Cross-reference question answers with gap matrix — every gap should answer at least one question"
      expected_output: "Confirmed: all material questions are answered by gap evidence"
      status: PENDING

    - id: MS-018-01-04
      action: "Determine: based on Q1-Q36 answers, what is the overall readiness verdict?"
      expected_output: "One of 5 verdict options with rationale"
      status: PENDING

  next_valid_task: TC-ARCH-018-02
```

```yaml
child_taskcard:
  id: TC-ARCH-018-02
  parent_id: TC-ARCH-018
  title: "Answer all 21 self-check questions"
  status: TODO

  self_check_questions:
    - "Did I inspect actual repo evidence?"
    - "Did I avoid relying on summaries?"
    - "Did I inspect src/ directly?"
    - "Did I audit .NET and Python products?"
    - "Did I identify generation waves?"
    - "Did I audit qname compliance per product?"
    - "Did I inspect skills?"
    - "Did I inspect SAL?"
    - "Did I inspect capability layer?"
    - "Did I inspect downstream generation?"
    - "Did I inspect autonomous supervisor?"
    - "Did I check machinery/product lane separation?"
    - "Did I check contamination/collision risk?"
    - "Did I identify whether backfill exists?"
    - "Did I design backfill if missing?"
    - "Did I separate working from repeatable from governed from production-ready?"
    - "Did I avoid claiming Gate 11 readiness from tests alone?"
    - "Did I produce taskcards?"
    - "Did I produce a gap matrix?"
    - "Did I give a clear go/no-go verdict?"
    - "Did I provide the next execution prompt?"

  micro_steps:
    - id: MS-018-02-01
      action: "Answer each of 21 self-check questions with yes/no and evidence reference"
      expected_output: "21 yes/no answers with evidence path citations"
      status: PENDING

    - id: MS-018-02-02
      action: "For any 'no' answer: create a gap entry and note as incomplete audit finding"
      expected_output: "Any 'no' answers become audit gaps that adjust the verdict"
      status: PENDING

    - id: MS-018-02-03
      action: "If all 21 = yes: verdict can be READY_AFTER_TARGETED or better. If any = no: DISCOVERY_INCONCLUSIVE."
      expected_output: "Self-check verdict confirmation"
      status: PENDING

  next_valid_task: TC-ARCH-018-03
```

```yaml
child_taskcard:
  id: TC-ARCH-018-03
  parent_id: TC-ARCH-018
  title: "Write final-verdict.md and supplemental reports"
  status: TODO

  micro_steps:
    - id: MS-018-03-01
      action: "Write reports/archaeology-2026-07-10/final-verdict.md with: VERDICT, rationale, Q1-Q36 answers, 21 self-check answers, must-fix blockers"
      target_file: "reports/archaeology-2026-07-10/final-verdict.md"
      expected_output: "final-verdict.md with all required sections"
      status: PENDING

    - id: MS-018-03-02
      action: "Write reports/archaeology-2026-07-10/machinery-repair-plan.md: ordered repair actions for BLOCKER and HIGH gaps, with dependencies between repair steps"
      target_file: "reports/archaeology-2026-07-10/machinery-repair-plan.md"
      status: PENDING

    - id: MS-018-03-03
      action: "Write reports/archaeology-2026-07-10/product-pilot-plan.md: FODS+FODT as pilot formats for proof-of-professional-quality, with success criteria"
      target_file: "reports/archaeology-2026-07-10/product-pilot-plan.md"
      status: PENDING

    - id: MS-018-03-04
      action: "Write remaining required reports: qname-translation-standard.md, product-deepening-readiness-plan.md, evidence-index.md"
      status: PENDING

  next_valid_task: TC-ARCH-018-04
```

```yaml
child_taskcard:
  id: TC-ARCH-018-04
  parent_id: TC-ARCH-018
  title: "Write reports/archaeology-2026-07-10/next-agent-execution-prompt.md"
  status: TODO

  micro_steps:
    - id: MS-018-04-01
      action: "Write: EXACT next prompt for the execution agent, including: plan path, first taskcard to execute (based on machinery repair plan), allowed files, forbidden files, evidence requirements"
      target_file: "reports/archaeology-2026-07-10/next-agent-execution-prompt.md"
      status: PENDING

    - id: MS-018-04-02
      action: "Write: exact execution sequence for machinery repair (which TC groups to execute in which order)"
      status: PENDING

    - id: MS-018-04-03
      action: "Write: stop conditions for the next agent (what constitutes TRUE_EXTERNAL_GATE vs ordinary continuable blocker)"
      status: PENDING

  next_valid_task: TC-ARCH-018-05
```

```yaml
child_taskcard:
  id: TC-ARCH-018-05
  parent_id: TC-ARCH-018
  title: "Package evidence bundle and write sprint-overview.md"
  status: TODO

  micro_steps:
    - id: MS-018-05-01
      action: "Write reports/archaeology-2026-07-10/sprint-overview.md: run ID, verdict, dates, counts, team"
      target_file: "reports/archaeology-2026-07-10/sprint-overview.md"
      status: PENDING

    - id: MS-018-05-02
      action: "Verify all 27 required artifacts exist in reports/archaeology-2026-07-10/"
      expected_output: "ls reports/archaeology-2026-07-10/ | wc -l >= 27"
      status: PENDING

    - id: MS-018-05-03
      action: "Create ZIP: python -m zipfile -c reports/archaeology-2026-07-10/evidence-bundle.zip reports/archaeology-2026-07-10/ (excluding evidence-bundle.zip itself)"
      target_file: "reports/archaeology-2026-07-10/evidence-bundle.zip"
      status: PENDING

    - id: MS-018-05-04
      action: "Compute and print SHA-256 of evidence-bundle.zip with ABSOLUTE Windows path"
      expected_output: "C:\\Users\\prora\\...\\format-factory\\reports\\archaeology-2026-07-10\\evidence-bundle.zip SHA-256: <hash>"
      status: PENDING

  closes_parent: true
  closes_plan: true
```

---

## ═══════════════════════════════════════════════════════════
## PART VI — MACHINE STATE MODEL
## [DOC-8] taskcard-state-machine.yaml
## ═══════════════════════════════════════════════════════════

```yaml
state_machine:
  plan_id: fuzzy-conjuring-lobster

  parent_transitions:
    valid:
      - [PROPOSED, READY]
      - [READY, IN_PROGRESS]
      - [IN_PROGRESS, CHILDREN_IN_PROGRESS]
      - [CHILDREN_IN_PROGRESS, INTEGRATION_PENDING]
      - [INTEGRATION_PENDING, VERIFIED]
      - [VERIFIED, SCORED]
      - [SCORED, CLOSED]
      - [SCORED, REROUTED]
      - ["*", BLOCKED]
      - [BLOCKED, READY]
      - ["*", BLOCKED_EXTERNAL]
      - ["*", DEFERRED_WITH_REASON]
    invalid_blocked:
      - PROPOSED → CLOSED  # must go through children
      - READY → CLOSED     # must go through children
      - CHILDREN_IN_PROGRESS → CLOSED  # must wait for integration
      - SCORED → IN_PROGRESS  # re-scoring without new work
      - CLOSED → "*"  # terminal state

  child_transitions:
    valid:
      - [TODO, READY]
      - [READY, IN_PROGRESS]
      - [IN_PROGRESS, IMPLEMENTED]
      - [IMPLEMENTED, VERIFIED]
      - [VERIFIED, SCORED]
      - [SCORED, CLOSED]
      - [SCORED, REROUTED]
      - [REROUTED, IN_PROGRESS]
      - ["*", BLOCKED]
      - [BLOCKED, READY]
      - ["*", BLOCKED_EXTERNAL]
      - ["*", DEFERRED_WITH_REASON]
    invalid_blocked:
      - TODO → CLOSED          # must implement and verify
      - READY → CLOSED
      - IMPLEMENTED → CLOSED   # must verify
      - REROUTED → CLOSED      # must rework first
      - BLOCKED_EXTERNAL → CLOSED without unblock evidence

  micro_step_transitions:
    valid:
      - [PENDING, READY]
      - [READY, ACTIVE]
      - [ACTIVE, COMPLETE]
      - [ACTIVE, FAILED]
      - [ACTIVE, BLOCKED]
      - [FAILED, READY]   # retry
      - [BLOCKED, READY]  # unblocked
      - [PENDING, SKIPPED_NOT_APPLICABLE]  # with written reason
    invalid_blocked:
      - PENDING → COMPLETE  # must go ACTIVE first
      - COMPLETE → ACTIVE   # cannot retry completed step
      - FAILED → COMPLETE   # must retry properly

  quality_thresholds:
    minimum_score: 4  # out of 5 on each dimension
    reroute_trigger: "any mandatory dimension < 4"
    close_requirement: "all mandatory dimensions >= 4"
```

---

## ═══════════════════════════════════════════════════════════
## PART VII — DEPENDENCY DAG
## [DOC-9] execution-dag.yaml
## ═══════════════════════════════════════════════════════════

```yaml
execution_dag:
  plan_id: fuzzy-conjuring-lobster

  phases:
    phase_1_preflight_and_inventory:
      taskcards: [TC-ARCH-001, TC-ARCH-002, TC-ARCH-003]
      parallel_safe: [TC-ARCH-002, TC-ARCH-003]  # after TC-ARCH-001
      sequential: [[TC-ARCH-001, TC-ARCH-002]]   # TC-001 must precede TC-002/003
      note: "TC-ARCH-001 establishes repo state before any reads"

    phase_2_generation_and_qname_archaeology:
      taskcards: [TC-ARCH-004, TC-ARCH-005, TC-ARCH-006]
      depends_on: [phase_1_preflight_and_inventory]
      parallel_safe: [TC-ARCH-004, TC-ARCH-005]   # can run concurrently
      sequential: [[TC-ARCH-005, TC-ARCH-006]]    # TC-005 → TC-006
      note: "TC-ARCH-004 and TC-ARCH-005 read different files; safe to parallelize"

    phase_3_source_quality:
      taskcards: [TC-ARCH-007]
      depends_on: [TC-ARCH-004, TC-ARCH-006]
      note: "Needs generation wave and qname results as inputs"

    phase_4_machinery_audit:
      taskcards: [TC-ARCH-008, TC-ARCH-009, TC-ARCH-010, TC-ARCH-011, TC-ARCH-012, TC-ARCH-013]
      depends_on: [TC-ARCH-001]  # needs repo state; otherwise parallel to phases 2-3
      internal_sequential: [[TC-ARCH-008, TC-ARCH-009], [TC-ARCH-009, TC-ARCH-010],
                             [TC-ARCH-010, TC-ARCH-011], [TC-ARCH-011, TC-ARCH-012],
                             [TC-ARCH-012, TC-ARCH-013]]
      note: "SAL→capability→downstream chain is sequential; supervisor audit is separate but follows skills"

    phase_5_synthesis:
      taskcards: [TC-ARCH-014, TC-ARCH-015, TC-ARCH-016, TC-ARCH-017]
      depends_on: [phase_2, phase_3, phase_4]
      parallel_safe: [TC-ARCH-014, TC-ARCH-015]  # backfill design and gate review are independent
      sequential: [[TC-ARCH-014, TC-ARCH-016], [TC-ARCH-015, TC-ARCH-016], [TC-ARCH-016, TC-ARCH-017]]
      note: "Gap matrix (016) needs backfill+gate assessments; taskcards (017) needs gap matrix"

    phase_6_verdict_and_bundle:
      taskcards: [TC-ARCH-018]
      depends_on: [phase_5_synthesis]
      note: "Final taskcard — needs ALL prior taskcards CLOSED"

  critical_path:
    - TC-ARCH-001 → TC-ARCH-002 → TC-ARCH-004 → TC-ARCH-007 → TC-ARCH-016 → TC-ARCH-017 → TC-ARCH-018
    note: "This is the longest sequential chain; can parallelize TC-ARCH-008 through TC-ARCH-013"

  file_ownership_conflicts:
    - files: ["reports/archaeology-2026-07-10/*.md", "reports/archaeology-2026-07-10/*.yaml"]
      owner_per_file: "one taskcard per output file — no overlap"
      conflict_risk: LOW

  parallel_safety_map:
    safe_to_parallelize:
      - [TC-ARCH-002, TC-ARCH-003]       # phase 1 parallel
      - [TC-ARCH-004, TC-ARCH-005]       # phase 2 parallel
      - [TC-ARCH-008, TC-ARCH-004]       # machinery and generation audit parallel (different inputs)
      - [TC-ARCH-014, TC-ARCH-015]       # backfill design and gate review parallel
    not_safe_to_parallelize:
      - [TC-ARCH-005, TC-ARCH-006]       # TC-006 reads TC-005 output
      - [TC-ARCH-008, TC-ARCH-009]       # TC-009 reads TC-008 SAL findings
      - [TC-ARCH-015, TC-ARCH-016]       # TC-016 reads TC-015 gate findings
      - [TC-ARCH-016, TC-ARCH-017]       # TC-017 reads TC-016 gap matrix
      - [TC-ARCH-017, TC-ARCH-018]       # TC-018 reads TC-017 taskcards
```

---

## ═══════════════════════════════════════════════════════════
## PART VIII — VALIDATION MATRIX
## [DOC-10] verification-matrix.md (key checks)
## ═══════════════════════════════════════════════════════════

```yaml
validation_matrix:
  plan_id: fuzzy-conjuring-lobster

  checks:
    - id: VAL-001
      taskcard_id: TC-ARCH-001-04-03
      description: "preflight-state.md exists and has >= 4 sections"
      method: "grep -c '##' reports/archaeology-2026-07-10/preflight-state.md"
      expected: ">= 4"
      mandatory: true

    - id: VAL-002
      taskcard_id: TC-ARCH-002-04-03
      description: "source-inventory.md covers all 30 products"
      method: "Check file has 20 Python rows and 10 .NET rows"
      expected: "30 product entries"
      mandatory: true

    - id: VAL-003
      taskcard_id: TC-ARCH-006-04
      description: "per-product-qname-compliance.yaml has 30 entries"
      method: "python3 -c 'import yaml; d=yaml.safe_load(open(...)); assert len(d)==30'"
      expected: "30 entries"
      mandatory: true

    - id: VAL-004
      taskcard_id: TC-ARCH-008-01
      description: "SAL facts audit covers FODS 10-fact finding + seeding note"
      method: "grep 'seeding_note\\|10 facts\\|FACT-FODS' reports/archaeology-2026-07-10/sal-audit.md"
      expected: "All 3 patterns found"
      mandatory: true

    - id: VAL-005
      taskcard_id: TC-ARCH-016-03
      description: "system-gap-matrix.yaml has entries for all 11 lanes (A-K)"
      method: "grep -c 'lane: ' reports/archaeology-2026-07-10/system-gap-matrix.yaml"
      expected: ">= 11 distinct lane assignments"
      mandatory: true

    - id: VAL-006
      taskcard_id: TC-ARCH-017-02
      description: "taskcards.yaml has all 16 required groups"
      method: "grep -c 'QNAME-AUTH\\|QNAME-REGISTRY\\|SAL-REPAIR\\|CAPABILITY-REPAIR\\|SKILL-HARDENING\\|SOURCE-HYGIENE\\|SUPERVISOR-LANES\\|GATE11-STOP\\|PRODUCT-PILOT' reports/archaeology-2026-07-10/taskcards.yaml"
      expected: ">= 9 matches (spot check for major groups)"
      mandatory: true

    - id: VAL-007
      taskcard_id: TC-ARCH-018-02
      description: "All 27 required artifacts exist"
      method: "ls reports/archaeology-2026-07-10/ | wc -l"
      expected: ">= 27"
      mandatory: true

    - id: VAL-008
      taskcard_id: TC-ARCH-018-05
      description: "evidence-bundle.zip exists and SHA-256 is printed"
      method: "ls -la reports/archaeology-2026-07-10/evidence-bundle.zip"
      expected: "file exists, size > 0"
      mandatory: true

    - id: VAL-009
      taskcard_id: TC-ARCH-018-01
      description: "final-verdict.md contains the verdict keyword"
      method: "grep -E 'READY_FOR_PRODUCT_DEEPENING|READY_AFTER_TARGETED|NOT_READY_REPAIR|DISCOVERY_INCONCLUSIVE' reports/archaeology-2026-07-10/final-verdict.md"
      expected: "exactly one verdict keyword found"
      mandatory: true

    - id: VAL-010
      taskcard_id: TC-ARCH-018-04
      description: "next-agent-execution-prompt.md contains exact next taskcard reference"
      method: "grep 'TC-' reports/archaeology-2026-07-10/next-agent-execution-prompt.md"
      expected: "at least one taskcard ID referenced"
      mandatory: true

  negative_controls:
    - id: NEG-001
      description: "No src/ files modified during audit (read-only constraint)"
      method: "git status src/"
      expected: "empty output (no src changes)"
      mandatory: true

    - id: NEG-002
      description: "No new files in registry/ (read-only constraint)"
      method: "git status registry/"
      expected: "empty output"
      mandatory: true

    - id: NEG-003
      description: "No commits made during audit (archaeology is read-only)"
      method: "git log --oneline -1"
      expected: "still shows af879e55 as HEAD"
      mandatory: true
```

---

## ═══════════════════════════════════════════════════════════
## PART IX — EVIDENCE CONTRACT
## [DOC-11] evidence-contract.md
## ═══════════════════════════════════════════════════════════

```yaml
evidence_contract:
  plan_id: fuzzy-conjuring-lobster
  run_id: archaeology-2026-07-10
  evidence_root: "reports/archaeology-2026-07-10/"
  authoritative_plan: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"

  evidence_structure:
    reports/archaeology-2026-07-10/:
      sprint-overview.md:           "TC-ARCH-018-05 writes"
      preflight-state.md:           "TC-ARCH-001-04 writes"
      source-inventory.md:          "TC-ARCH-002-04 writes"
      source-hygiene-audit.md:      "TC-ARCH-003-04 writes"
      generation-archaeology.md:    "TC-ARCH-004-04 writes"
      per-product-capability-matrix.yaml: "TC-ARCH-007-04 writes"
      per-product-qname-compliance.yaml:  "TC-ARCH-006-04 writes"
      src-source-quality-review.md: "TC-ARCH-007-03 writes"
      qname-schema-audit.md:        "TC-ARCH-005-04 writes"
      qname-translation-standard.md: "TC-ARCH-018-03 writes"
      sal-audit.md:                 "TC-ARCH-008-04 writes"
      capability-layer-audit.md:    "TC-ARCH-009-03 writes"
      downstream-generation-audit.md: "TC-ARCH-010-03 writes"
      skill-inventory-and-gaps.md:  "TC-ARCH-011-03 writes"
      autonomous-supervisor-audit.md: "TC-ARCH-012-03 writes"
      lane-separation-and-collision-risk.md: "TC-ARCH-013-03 writes"
      backfill-facility-design.md:  "TC-ARCH-014-03 writes"
      gate11-readiness-review.md:   "TC-ARCH-015-03 writes"
      product-deepening-readiness-plan.md: "TC-ARCH-018-03 writes"
      system-gap-matrix.yaml:       "TC-ARCH-016-03 writes"
      taskcards.yaml:               "TC-ARCH-017-02 writes"
      machinery-repair-plan.md:     "TC-ARCH-018-03 writes"
      product-pilot-plan.md:        "TC-ARCH-018-03 writes"
      next-agent-execution-prompt.md: "TC-ARCH-018-04 writes"
      evidence-index.md:            "TC-ARCH-018-03 writes"
      final-verdict.md:             "TC-ARCH-018-03 writes"
      evidence-bundle.zip:          "TC-ARCH-018-05 packages"

  evidence_obligations:
    - taskcard_closes_when: "its designated output file exists and passes VAL-* check"
    - no_empty_files: "any evidence file with 0 bytes = taskcard NOT CLOSED"
    - no_placeholder_content: "'TODO', 'TBD', 'placeholder' in evidence file = taskcard NOT CLOSED"
    - zip_must_contain_26_reports: "evidence-bundle.zip must contain all 26 report files (excluding itself)"

  prohibited:
    - "Alternative execution instructions inside any evidence file"
    - "Claims that contradict this plan's authority"
    - "Completion claims for work not verified with VAL-* checks"
```

---

## ═══════════════════════════════════════════════════════════
## PART X — TRACEABILITY (embedded)
## [DOC-12] requirement-to-parent-taskcard-map.csv
## ═══════════════════════════════════════════════════════════

```
req_id,parent_taskcard_id,lane,phase
REQ-REPO-001,TC-ARCH-001,A,1
REQ-SRC-001,TC-ARCH-002,B,1
REQ-SRC-002,TC-ARCH-002,B,1
REQ-SRC-003,TC-ARCH-003,B,1
REQ-SRC-004,TC-ARCH-004,B,2
REQ-QNAME-001,TC-ARCH-005,C,2
REQ-QNAME-002,TC-ARCH-005,C,2
REQ-QNAME-003,TC-ARCH-006,C,2
REQ-QUAL-001,TC-ARCH-007,D,3
REQ-QUAL-002,TC-ARCH-007,D,3
REQ-SAL-001,TC-ARCH-008,E,4
REQ-SAL-002,TC-ARCH-008,E,4
REQ-CAP-001,TC-ARCH-009,F,4
REQ-GEN-001,TC-ARCH-010,G,4
REQ-SKILL-001,TC-ARCH-011,H,4
REQ-SUP-001,TC-ARCH-012,I,4
REQ-SUP-002,TC-ARCH-013,I,4
REQ-BACK-001,TC-ARCH-014,J,5
REQ-GATE-001,TC-ARCH-015,K,5
REQ-GAP-001,TC-ARCH-016,ALL,5
REQ-TC-001,TC-ARCH-017,ALL,5
REQ-VERD-001,TC-ARCH-018,ALL,6
```

---

## ═══════════════════════════════════════════════════════════
## PART XI — INVESTIGATION QUESTIONS TRACEABILITY (preserved + enhanced)
## ═══════════════════════════════════════════════════════════

| Q# | Question | Taskcard | Evidence File |
|---|---|---|---|
| Q1-5 | Products, languages, active/experimental status | TC-ARCH-002 | source-inventory.md |
| Q6-12 | QName compliance, integration | TC-ARCH-005, TC-ARCH-006 | qname-schema-audit.md, per-product-qname-compliance.yaml |
| Q13-14 | Spec hierarchy, backfill | TC-ARCH-006, TC-ARCH-014 | backfill-facility-design.md |
| Q15-18 | Cross-language parity, generation waves | TC-ARCH-004, TC-ARCH-007 | generation-archaeology.md, src-source-quality-review.md |
| Q19-20 | Skills, machinery risks | TC-ARCH-011, TC-ARCH-010 | skill-inventory-and-gaps.md, downstream-generation-audit.md |
| Q21-23 | SAL quality, determinism, manual seeding | TC-ARCH-008 | sal-audit.md |
| Q24-27 | Capability layer, feature compiler | TC-ARCH-009 | capability-layer-audit.md |
| Q28 | Where malformed classes introduced | TC-ARCH-010 | downstream-generation-audit.md |
| Q29-30 | Skill gaps, repeatability | TC-ARCH-011 | skill-inventory-and-gaps.md |
| Q31-35 | Supervisor, lane separation, Gate 11 | TC-ARCH-012, TC-ARCH-013, TC-ARCH-015 | autonomous-supervisor-audit.md, lane-separation-and-collision-risk.md, gate11-readiness-review.md |
| Q36 | Must fix before product deepening | TC-ARCH-016, TC-ARCH-018 | system-gap-matrix.yaml, final-verdict.md |

---

## ═══════════════════════════════════════════════════════════
## PART XII — KEY FILES REFERENCED (preserved)
## ═══════════════════════════════════════════════════════════

**Source files to inspect deeply**:
- `src/python/fods/spec/` — full tree (canonical Python models, richest)
- `src/python/fods/Compat/` — facade pattern
- `src/python/fods/models.py` — delegation example
- `src/python/csv/spec/` — minimal spec example
- `src/net/fods/Spec/` — canonical .NET models
- `src/net/fods/Model/` — .NET facades
- `src/net/fods/FodsDocument.cs` — root document (Gen 4 DOM)
- `src/net/zst/` — Gen 1 .NET example (no Spec/)

**Machinery files to inspect**:
- `tools/spec/merge_sal_facts.py` — SAL merger
- `tools/spec/generate_canonical_stubs.py` — stub generator
- `tools/supervisor/capability_feature_compiler.py` — feature compiler
- `tools/supervisor/governance_validators_ext4.py` — V111-V127
- `tools/supervisor/check_continuation.py` — gate enforcement
- `.supervisor/skill-registry.yaml` — skill registry

**Registry files to inspect**:
- `registry/odf-ontology/qname-to-code-map.yaml` — qname map
- `registry/odf-ontology/canonical-class-inventory.yaml` — canonical inventory (STALE)
- `registry/format-registry.yaml` — format registry with gate status
- `registry/gate11-criteria.yaml` — Gate 11 criteria
- `registry/source-structure-baseline.json` — LOC caps

**SAL files to inspect**:
- `.local/spec-cache/fods/1.3/workbench/verified-facts.yaml` — 10 FODS facts (manually seeded)
- `.local/spec-cache/fods/1.3/spec-index.yaml` — spec metadata
- `.local/spec-cache/sal-facts-20260621.json` — combined SAL DB

**Plan files to read**:
- `plans/master-plan.md` — project rules (RULE-LIB-001 through RULE-LIB-010)
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — correction plan
- `docs/spec-to-feature-correction-plan-summary.md` — quick ref

---

## ═══════════════════════════════════════════════════════════
## PART XIII — STRICT MODE CONSTRAINTS (preserved + enforcement)
## ═══════════════════════════════════════════════════════════

During execution:
1. Do NOT begin broad source migration
2. Do NOT continue product deepening sprints
3. Do NOT manually rewrite src/ as one-off cleanup
4. Do NOT trust prior summaries — inspect actual files
5. Do NOT claim qname compliance without per-file proof
6. Do NOT claim autonomy without run evidence
7. Evidence is authority — AI output is NOT authority
8. Every taskcard must write its output file BEFORE being marked CLOSED
9. A parent may not close until ALL children are CLOSED
10. Negative controls (NEG-001, NEG-002, NEG-003) must pass: no src/ edits, no registry edits, no commits

---

## ═══════════════════════════════════════════════════════════
## PART XIV — QName Translation Standard (to be formalized in artifact #10)
## [Preserved + enforcement added]
## ═══════════════════════════════════════════════════════════

**For ODF formats (FODS, FODT, ODS, ODT, FODP, FODG, ABW)**:
- `table:table-cell` → `Table.TableCell` → `spec/table/table_cell.py` (Python) / `Spec/Table/TableCell.cs` (.NET)
- `office:document` → `Office.Document` → `spec/office/document.py` / `Spec/Office/Document.cs`
- Format-prefixed names (FodsCell, FodtDocument) ONLY in `Compat/` or `Model/` as facades
- Spec hierarchy folders mirror qname prefix: `table:*` → `spec/table/`, `office:*` → `spec/office/`

**For non-ODF formats (CSV, TOML, ZST, XCF, etc.)**:
- Use structural construct names from the spec: `CsvRecord` (from RFC 4180), `ZstFrame` (from RFC 8878)
- NOT format-prefixed at spec level: NOT `CsvDocument` as a model class (ok as a facade in Compat/)
- Namespace derived from format spec authority (RFC, ISO, OASIS, informal)

**Enforcement in this audit**:
- Non-compliance findings → generate GAP-QNAME-NNN entries
- Compliance scoring in `per-product-qname-compliance.yaml` uses this standard as the reference

---

## ═══════════════════════════════════════════════════════════
## PART XV — RECONCILIATION BLOCK
## [DOC-13] plan-reconciliation-report.md
## ═══════════════════════════════════════════════════════════

```yaml
reconciliation:
  plan_id: fuzzy-conjuring-lobster
  status: COMPLETE
  single_authoritative_plan: true
  competing_plans: none
  duplicate_taskcards: none

  coverage_check:
    all_11_lanes_covered: true  # A through K
    all_22_requirements_have_parent_taskcard: true
    all_18_parents_have_children: true
    all_children_have_micro_steps: true
    all_micro_steps_have_completion_checks: true
    all_27_artifacts_have_owning_taskcard: true
    all_36_investigation_questions_mapped: true
    all_21_self_check_questions_listed: true

  contradiction_check:
    found: none

  stale_instruction_check:
    old_vague_steps_removed: true
    replaced_with: "micro-step decompositions in Part V"

  no_actionable_item_loss:
    original_18_taskcards: present_and_enhanced
    new_children_added: 68  # ~4 per parent × 18 parents (some have 3, some 5)
    new_micro_steps_added: ~300  # ~5 per child × 68 children

  single_plan_authority:
    only_plan_directing_execution: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"
    supporting_artifacts: "reports/archaeology-2026-07-10/ (evidence, not plans)"
    no_competing_execution_authority: true

  idempotency:
    stable_ids: true  # TC-ARCH-NNN, REQ-DOMAIN-NNN, MS-NNN-NN-NN
    no_random_ids: true
    rerun_will_find_same_structure: true
```

---

## ═══════════════════════════════════════════════════════════
## PART XVI — EXECUTION HANDOFF
## [DOC-14] execution-readiness-verdict.md + final-execution-handoff.md
## ═══════════════════════════════════════════════════════════

### Execution Readiness Verdict

```yaml
execution_readiness:
  verdict: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION
  active_plan: "C:/Users/prora/.claude/plans/fuzzy-conjuring-lobster.md"
  authority_source: user_initiated_plan_mode_current_session
  duplicate_plans: none
  blockers: none
  deferred_items: none

  next_valid_parent_taskcard: TC-ARCH-001
  next_valid_child_taskcard: TC-ARCH-001-01
  first_micro_step: MS-001-01-01

  readiness_confirmation:
    all_parents_have_children: true
    all_children_have_micro_steps: true
    dependency_dag_complete: true
    validation_matrix_complete: true
    evidence_contract_complete: true
    machine_state_defined: true
    execution_handoff_written: true
```

### Final Execution Handoff

**Plan ID**: fuzzy-conjuring-lobster
**Authoritative Plan Path**: `C:\Users\prora\.claude\plans\fuzzy-conjuring-lobster.md`
**Run ID**: `archaeology-2026-07-10`
**Output Directory**: `reports/archaeology-2026-07-10/`

---

**EXECUTION AGENT INSTRUCTIONS:**

1. **Read this plan** at `C:\Users\prora\.claude\plans\fuzzy-conjuring-lobster.md` before starting.

2. **Start at TC-ARCH-001, child TC-ARCH-001-01, micro-step MS-001-01-01**.

3. **Before each micro-step**, confirm:
   - Which parent taskcard does this serve? (TC-ARCH-001)
   - Which requirement? (REQ-REPO-001)
   - What exact output is expected? (see micro-step expected_output field)
   - What files may I read? (see child scope.allowed)
   - What must NOT be changed? (src/, registry/, tools/ — read-only throughout audit)
   - What evidence proves completion? (see micro-step evidence field)
   - What is the next valid micro-step? (see micro-step next field)

4. **Execute exactly one micro-step at a time**. Capture evidence immediately.

5. **Mark micro-step COMPLETE** only when the expected_output is observed and the completion_check passes.

6. **Mark child IMPLEMENTED** when all its micro-steps are COMPLETE.

7. **Run validation checks** from Part VIII VALIDATION MATRIX for that child.

8. **Mark child VERIFIED** after validation passes. Mark SCORED (all dimensions ≥ 4/5). Mark CLOSED.

9. **Mark parent IN_PROGRESS → CHILDREN_IN_PROGRESS** when first child starts.

10. **Run parent integration check** when all children are CLOSED.

11. **Mark parent CLOSED** only after integration check passes.

12. **Continue to the next valid task** based on the DAG in Part VII.

13. **NEVER**: choose unrelated work, skip micro-steps, close parent before children, treat file existence as validation, treat test existence as passing.

14. **If blocked on a micro-step**: mark BLOCKED with reason; create a note; continue to the next non-blocked micro-step in the same child if possible, or escalate to parent BLOCKED.

15. **When TC-ARCH-018 is CLOSED**: Run all NEG-* negative controls (Part VIII). Then print the absolute path and SHA-256 of `reports/archaeology-2026-07-10/evidence-bundle.zip` as the final output.

16. **This is a READ-ONLY audit**. No src/ changes, no commits, no registry changes.

---

**Next micro-step after plan approval**:

`MS-001-01-01: Run git log --oneline -20 and record the 20 most recent commits.`

---

## ═══════════════════════════════════════════════════════════
## PART XVII — KNOWN EXISTING MACHINERY TO REUSE (preserved)
## ═══════════════════════════════════════════════════════════

- `/qname-backfill` skill: `.claude/commands/qname-backfill.md` — reuse for backfill design (TC-ARCH-014)
- `governance_validators_ext4.py` V111-V127 — already enforce qname, use as reference in TC-ARCH-010 scenario test
- `registry/odf-ontology/canonical-class-inventory.yaml` — read (don't write) during TC-ARCH-005
- `tools/spec/merge_sal_facts.py` — read during TC-ARCH-008 pipeline audit
- `tools/supervisor/capability_feature_compiler.py` — read during TC-ARCH-009

---

## ═══════════════════════════════════════════════════════════
## PART XVIII — SELF-CHECK OBLIGATION (preserved + linked)
## ═══════════════════════════════════════════════════════════

All 21 self-check questions must be answered yes/no in `final-verdict.md` (written by TC-ARCH-018-02).
Failure to answer any = DISCOVERY_INCONCLUSIVE verdict.
Any 'no' answer = additional gap entry created and factored into verdict.

- Q1: Did I inspect actual repo evidence? → Proven by preflight-state.md
- Q2: Did I avoid relying on summaries? → Proven by per-file inspection in TC-ARCH-004 to TC-ARCH-013
- Q3: Did I inspect src/ directly? → Proven by TC-ARCH-002, TC-ARCH-004, TC-ARCH-006
- Q4: Did I audit .NET and Python products? → Both covered in TC-ARCH-002, TC-ARCH-004, TC-ARCH-007
- Q5: Did I identify generation waves? → TC-ARCH-004 + generation-archaeology.md
- Q6: Did I audit qname compliance per product? → TC-ARCH-005, TC-ARCH-006 + per-product-qname-compliance.yaml
- Q7: Did I inspect skills? → TC-ARCH-011 + skill-inventory-and-gaps.md
- Q8: Did I inspect SAL? → TC-ARCH-008 + sal-audit.md
- Q9: Did I inspect capability layer? → TC-ARCH-009 + capability-layer-audit.md
- Q10: Did I inspect downstream generation? → TC-ARCH-010 + downstream-generation-audit.md
- Q11: Did I inspect autonomous supervisor? → TC-ARCH-012 + autonomous-supervisor-audit.md
- Q12: Did I check machinery/product lane separation? → TC-ARCH-013 + lane-separation-and-collision-risk.md
- Q13: Did I check contamination/collision risk? → TC-ARCH-013
- Q14: Did I identify whether backfill exists? → TC-ARCH-014 + backfill-facility-design.md
- Q15: Did I design backfill if missing? → TC-ARCH-014
- Q16: Did I separate working from repeatable from governed from production-ready? → TC-ARCH-007 quality ratings
- Q17: Did I avoid claiming Gate 11 readiness from tests alone? → TC-ARCH-015 scores criteria holistically
- Q18: Did I produce taskcards? → TC-ARCH-017 + taskcards.yaml
- Q19: Did I produce a gap matrix? → TC-ARCH-016 + system-gap-matrix.yaml
- Q20: Did I give a clear go/no-go verdict? → TC-ARCH-018-01 + final-verdict.md
- Q21: Did I provide the next execution prompt? → TC-ARCH-018-04 + next-agent-execution-prompt.md
