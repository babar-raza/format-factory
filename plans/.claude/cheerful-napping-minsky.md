# Plan: docs/ Root Reorganization — Physical Migration, Reference Repair, and Governance Healing

**plan_type:** docs_reorganization
**mission_id:** DOCS-REORG-001
**created:** 2026-07-01

---

## Context

The `docs/` directory has accumulated **70 files directly at root** alongside 24 topical subdirectories.
A previous execution (per the user's brief) only expanded `docs/README.md` into an index — it did not
physically relocate any document. That left root clutter unaddressed and created false closure.

The actual objective is:
- Physically move safely relocatable documents into existing topical subfolders
- Update ALL active references across the entire repository (YAML, Python, Markdown, JSON, plans,
  registries, evidence contracts, tests, AGENTS.md, CLAUDE.md, skill-registry, commands)
- Preserve historical references correctly (without falsifying evidence)
- Add a `documentation-structure-migration` governed capability, a root-placement policy, and a
  repository-wide path/link validator
- Prove idempotency: a second run produces zero material changes

**Current state (confirmed by exploration):**
- 70 root docs files; 24 subfolders with ~195 docs inside them
- Top-referenced files (by raw count): gates.md (829), specification-cache.md (743),
  acquisition-workflow.md (645), architecture.md (591), release-control.md (569)
- `check_methodology_links.py` **enforces hardcoded paths** for 5 root docs:
  `agent-methodology-index.md`, `planning-methodology.md`, `agent-execution-handoff-standard.md`,
  `plan-hardening-checklist.md`, `fresh-chat-continuity-brief.md`
- `spec-to-feature-correction-plan-summary.md` is a mandatory pre-read in CLAUDE.md (line 160)
- Existing movable-target subfolders: `docs/ai/`, `docs/automation/`, `docs/governance/`,
  `docs/code-quality/`, `docs/python-foss/`, `docs/release/`, `docs/product-factory/`
- Missing expected subfolders: `docs/architecture/`, `docs/security/`, `docs/planning/`,
  `docs/formats/` — some of these may need to be created if semantically correct

**What NOT to move (root retention — pre-confirmed):**
1. `README.md` — docs entry point (canonical root)
2. `agent-methodology-index.md` — cross-cutting agent entry point, enforced by validator
3. `planning-methodology.md` — enforced by `check_methodology_links.py`
4. `agent-execution-handoff-standard.md` — enforced by validator
5. `plan-hardening-checklist.md` — enforced by validator
6. `fresh-chat-continuity-brief.md` — enforced by validator (275 refs)
7. `gates.md` — repository-wide gate authority, genuinely cross-cutting (829 refs)
8. `spec-to-feature-correction-plan-summary.md` — CLAUDE.md mandatory pre-read (line 160)

All other ~62 root files are classified as movable, subject to destination confirmation in TC-DOCS-002.

---

## Critical Files

- `docs/README.md` — current root index (to be rebuilt after moves)
- `AGENTS.md` — 50+ docs/ root references to update
- `CLAUDE.md` — ~15 docs/ root references to update
- `tools/governance/check_methodology_links.py` — hardcoded path enforcement (must update for any moved enforced files; none of the 8 retained files move, so no changes needed here unless destination policy changes)
- `.supervisor/skill-registry.yaml` — capability/skill registration target
- `.governance/capabilities/registry.yaml` — capability registry target
- `reports/documentation/` — output directory for all manifest/audit/policy files

---

## Taskcard Status Table

| TC-ID | Status |
|-------|--------|
| TC-DOCS-001 | CLOSED |
| TC-DOCS-002 | CLOSED |
| TC-DOCS-003 | CLOSED |
| TC-DOCS-004 | CLOSED |
| TC-DOCS-005 | CLOSED |
| TC-DOCS-006 | CLOSED |
| TC-DOCS-007 | CLOSED |
| TC-DOCS-008 | CLOSED |
| TC-DOCS-009 | CLOSED |
| TC-DOCS-010 | CLOSED |
| TC-DOCS-011 | CLOSED |
| TC-DOCS-012 | CLOSED |
| TC-DOCS-013 | CLOSED |
| TC-DOCS-014 | CLOSED |
| TC-DOCS-015 | CLOSED |
| TC-DOCS-016 | CLOSED |
| TC-DOCS-017 | CLOSED |

<!-- lifecycle_audit machine-readable summary (required for parse_plan_taskcards):
TC-DOCS-001 — CLOSED
TC-DOCS-002 — CLOSED
TC-DOCS-003 — CLOSED
TC-DOCS-004 — CLOSED
TC-DOCS-005 — CLOSED
TC-DOCS-006 — CLOSED
TC-DOCS-007 — CLOSED
TC-DOCS-008 — CLOSED
TC-DOCS-009 — CLOSED
TC-DOCS-010 — CLOSED
TC-DOCS-011 — CLOSED
TC-DOCS-012 — CLOSED
TC-DOCS-013 — CLOSED
TC-DOCS-014 — CLOSED
TC-DOCS-015 — CLOSED
TC-DOCS-016 — CLOSED
TC-DOCS-017 — CLOSED
-->

---

## TC-DOCS-001: Baseline Capture + Migration Capability Creation

**Goal:** Capture baseline state; create and register the `documentation-structure-migration` capability so all subsequent work flows through governed routes.

**Actions:**

1. Capture baseline:
   ```
   mkdir -p reports/documentation
   mkdir -p .local/evidences/docs-root-reorganization-001
   ```
   Write `.local/evidences/docs-root-reorganization-001/baseline.yaml` with:
   - mission_id, run_id, branch/HEAD, docs root file count (70), subfolder count (24)
   - List of all docs/ root filenames
   - List of all docs/ subdirectory names

2. Create capability registration in `.governance/capabilities/registry.yaml`:
   - capability_id: `documentation-structure-migration`
   - status: active
   - product_track: layer_governance
   - parity_status: FULL_PARITY
   - claude_code: Y, codex: Y
   - description: Root-document inventory, destination classification, reference graph building,
     safe file migration, active-reference rewriting, compatibility stubs, link validation,
     rollback, idempotency

3. Create skill registration in `.supervisor/skill-registry.yaml`:
   - mission_id: DOCS-REORG-001
   - skill_name: documentation-structure-migration
   - trigger: `/documentation-structure-migration`

4. Create `.claude/commands/documentation-structure-migration.md` — command definition

5. Create `tools/docs/migration_engine.py` — the core migration utility with these subcommands:
   - `inventory` — list all docs/ root files with metadata
   - `scan-refs` — scan entire repo for path references (all file types)
   - `manifest` — generate/validate migration manifest
   - `move` — execute a single migration item (git mv + ref update)
   - `validate` — post-move validation
   - `rollback` — restore from backup

6. Add `tests/tools/test_migration_engine.py` with basic import + subcommand smoke tests

**Evidence:** `.local/evidences/docs-root-reorganization-001/baseline.yaml`, capability/skill registrations, `tools/docs/migration_engine.py`

---

## TC-DOCS-002: Complete Inventory + Classification of All 70 Root Files

**Goal:** Every docs/ root file gets a `docs_root_document` record. Zero unclassified files.

**Actions:**

1. Read each of the 70 docs/ root files (filename at minimum, first lines if needed)
2. Write `reports/documentation/docs-root-inventory.yaml` with a `docs_root_document` entry for each:
   - document_id, current_path, title, purpose, primary_topic, document_type
   - remain_at_root (bool), root_retention_reason (if retained)
   - candidate_destinations (list of existing subfolders)
   - recommended_destination
   - migration_risk: LOW | MEDIUM | HIGH (based on reference count and reference type)
   - active: bool, generated: bool, historical: bool

3. Classification taxonomy to apply:
   - `entry_point` — README.md, agent-methodology-index.md
   - `cross_cutting_policy` — gates.md, security.md
   - `ai_llm_strategy` → docs/ai/
   - `automation_supervision` → docs/automation/
   - `governance_policy` → docs/governance/
   - `planning_execution` → docs/automation/ or docs/governance/
   - `format_acquisition` → docs/python-foss/ (or new docs/formats/ if warranted)
   - `spec_retrieval` → docs/ai/ (RAG-related)
   - `product_architecture` → docs/product-factory/ or docs/code-quality/
   - `code_quality_architecture` → docs/code-quality/
   - `release_compliance` → docs/release/ or docs/governance/

4. For each of the 8 confirmed root-retention files: set `remain_at_root: true` and
   record the validated reason from the retention policy (defined in TC-DOCS-003)

**Expected outcome:** `reports/documentation/docs-root-inventory.yaml` with 70 entries, all classified.

COUNTER CHECK: UNCLASSIFIED_DOCS_ROOT_FILES = 0

---

## TC-DOCS-003: Root Retention Policy YAML + Destination Map YAML

**Goal:** Formal, machine-readable policy documents that govern what stays at root and where everything else goes.

**Actions:**

1. Write `reports/documentation/docs-root-retention-policy.yaml`:
   - Define 5 valid root-retention reasons (from Section 5 of task brief):
     - `canonical_entry_point` — docs/README.md
     - `repository_wide_navigation_index` — (README.md, agent-methodology-index.md)
     - `cross_cutting_policy_root_convention` — gates.md, security.md
     - `validator_enforced_root_location` — 5 methodology files enforced by check_methodology_links.py
     - `mandatory_agent_pre_read` — spec-to-feature-correction-plan-summary.md (CLAUDE.md line 160)
   - List each retained file with its reason
   - Define policy: all other root files MUST have a canonical destination in a subfolder

2. Write `reports/documentation/docs-root-destination-map.yaml`:
   - One entry per movable file with:
     - current_path, destination_path, destination_reason
     - alternatives_rejected (with reasoning)
     - compatibility_strategy: FULL_INTERNAL_REWRITE | TEMPORARY_COMPATIBILITY_STUB | HISTORICAL_PATH_PRESERVATION | DO_NOT_MOVE
     - reference_count_estimate
     - owner (which layer owns this document)
   - Group by destination:
     - docs/ai/ — ~10 files (AI/LLM/RAG strategy docs + their YAML pairs)
     - docs/automation/ — ~7 files (supervision methodology, Conway R9, terminal state machine)
     - docs/governance/ — ~12 files (compliance, legal, release-control, policy docs, execution standards)
     - docs/python-foss/ or docs/product-factory/ — ~8 files (format acquisition, onboarding, tracks)
     - docs/code-quality/ — ~6 files (architecture contract, source hygiene, compiler-related)
     - docs/release/ — ~2 files (release control if not in governance)
     - Possibly new docs/architecture/ — if 3+ architecture docs warrant it

3. Human-reviewable section summarizing the expected move count and any NEW subfolder creation decisions

COUNTER CHECK: ROOT_DOCS_WITHOUT_VALID_RETENTION_REASON = 0

---

## TC-DOCS-004: Build Reference Graph Tool + Full Repository Scan

**Goal:** Complete machine-readable reference graph for every docs/ root file — across ALL file types.

**Actions:**

1. Implement `tools/docs/migration_engine.py scan-refs` subcommand that:
   - Accepts a list of source file paths (or scans all docs/ root files)
   - Searches the entire repository for references using these patterns per file type:
     - Markdown: `[text](docs/filename)`, `](docs/filename`, relative paths
     - YAML: string values containing `docs/filename`
     - JSON: string values containing `docs/filename`
     - Python: string literals, f-strings, Path() calls containing `docs/filename`
     - `.md`, `.yaml`, `.json`, `.py`, `.sh`, `.ps1`, `.txt` files
   - For each match, records: file_path, line_number, match_context, reference_type
   - Reference types (classify per Section 7 of task brief):
     ACTIVE_RUNTIME_REFERENCE, ACTIVE_COMMAND_REFERENCE, ACTIVE_GOVERNANCE_REFERENCE,
     ACTIVE_DOCUMENTATION_LINK, ACTIVE_TEST_REFERENCE, ACTIVE_REGISTRY_REFERENCE,
     ACTIVE_PLAN_OR_TASKCARD, GENERATED_REFERENCE, HISTORICAL_EVIDENCE, OBSOLETE_REFERENCE,
     FALSE_POSITIVE, EXTERNAL_COMPATIBILITY_RISK
   - Excludes: `.git/`, `.local/archive/`, `__pycache__/`, `.venv/`
   - Outputs: `reports/documentation/docs-reference-graph.yaml`

2. Run the scan: `python tools/docs/migration_engine.py scan-refs --output reports/documentation/docs-reference-graph.yaml`

3. Analyze the graph output:
   - For each movable docs/ root file: count ACTIVE_* references vs HISTORICAL_EVIDENCE references
   - Identify which files have 0 ACTIVE_* references (can move with zero reference updates)
   - Identify which files are referenced in `check_methodology_links.py` hardcoded checks
   - Flag GENERATED_REFERENCE files whose producer still emits old paths

4. Write `reports/documentation/docs-historical-reference-disposition.yaml`:
   - For each docs/ root file: list historical references and their disposition
   - Disposition choices: PRESERVE_AS_IS | ANNOTATE_WITH_SUPERSESSION | UPDATE_WITH_NOTE

5. Update `reports/documentation/docs-root-destination-map.yaml` with confirmed reference counts
   (refine estimates from TC-DOCS-003 with actual scan data)

COUNTER CHECK: UNCLASSIFIED_REFERENCES_TO_MOVED_DOCS = 0

---

## TC-DOCS-005: Freeze Migration Manifest

**Goal:** Complete, frozen migration manifest — no file moves until this is complete.

**Actions:**

1. Write `reports/documentation/docs-root-migration-manifest.yaml` with one `docs_migration_item` per movable file:
   ```yaml
   docs_migration_item:
     migration_id: MOVE-001
     source_path: docs/filename.md
     destination_path: docs/subfolder/filename.md
     document_id: <from inventory>
     disposition: FULL_INTERNAL_REWRITE  # or TEMPORARY_COMPATIBILITY_STUB
     compatibility_strategy: <from destination map>
     active_references:  # from reference graph — ACTIVE_* only
       - {file: "...", line: N, type: "ACTIVE_GOVERNANCE_REFERENCE"}
     historical_references:  # HISTORICAL_EVIDENCE entries
       - {file: "...", line: N, disposition: "PRESERVE_AS_IS"}
     generated_references:  # GENERATED_REFERENCE entries
       - {file: "...", producer: "...", action: "UPDATE_PRODUCER"}
     content_hash_before: <sha256>
     rollback_path: .local/archive/docs-reorg-backup/
     move_status: PENDING
     reference_update_status: PENDING
     validation_status: PENDING
     exact_next_action: "git mv docs/source.md docs/dest/source.md"
   ```

2. Number all migration_ids sequentially (MOVE-001 through MOVE-N)
3. Group items by migration wave (Wave 1-6) matching TC-DOCS-007 through TC-DOCS-012
4. Create backup directory: `.local/archive/docs-reorg-backup/`
5. Copy all files-to-be-moved to backup directory before any moves
6. Verify manifest is complete (count == total movable files from inventory)

---

## TC-DOCS-006: Pilot Classes 1-5 — Prove Methodology Before Bulk

**Goal:** Execute and validate 5 pilot migration classes. Bulk work begins only after all 5 pass.

**Pilot 1 — Low-reference move:**
- Select a docs/ root file with 0-5 ACTIVE_* references
- Move it to its destination subfolder using `git mv`
- Update all active references
- Validate: destination exists, old path gone from active refs, no broken links
- Prove rollback: restore, verify original state

**Pilot 2 — Heavily-referenced governance document:**
- Select a file with 50+ ACTIVE_* references spanning YAML, Markdown, Python
- Move it, update ALL reference types (not just Markdown)
- Validate: run `tools/docs/migration_engine.py validate --source <old> --dest <new>`
- Prove: registry references updated, plan references updated, test references updated

**Pilot 3 — Historical-reference handling:**
- Select a file referenced in old evidence bundles / sprint reports
- Move it, preserve historical references as-is
- Validate: historical docs still contain original path (as expected), annotation added if warranted
- Prove: no historical falsification

**Pilot 4 — Compatibility stub case:**
- Select a file where `TEMPORARY_COMPATIBILITY_STUB` is the correct strategy
  (has EXTERNAL_COMPATIBILITY_RISK references or unknown consumers)
- Move canonical copy, leave thin stub at old path containing:
  - Deprecation notice with canonical new path
  - No authoritative content duplication
  - Deprecation metadata block
- Validate: stub is thin, canonical has all content, no active refs still using old path

**Pilot 5 — Generated-reference producer repair:**
- Identify a file whose old path appears in a generated artifact (output of a tool/script)
- Update the producing script/tool to emit the new path
- Re-run the generator to confirm new output uses new path
- Validate: no generator recreates old path reference

**After all 5 pilots pass:** Record results in `.local/evidences/docs-root-reorganization-001/pilot-results.yaml`

---

## TC-DOCS-007: Wave 1 — AI/LLM Docs (→ docs/ai/)

**Scope:** ~10 files + YAML pairs related to AI, LLM, retrieval, oracle strategy

**Candidate files:**
- `docs/ai/ai-assisted-commercial-development.md` + `.yaml` → `docs/ai/`
- `docs/ai/ai-generated-format-requirements-pipeline.md` + `.yaml` → `docs/ai/`
- `docs/ai/ai-usage-operating-model.md` + `.yaml` → `docs/ai/`
- `docs/ai/llm-and-embedding-strategy.md` → `docs/ai/`
- `docs/ai/llm-endpoint-strategy.md` → `docs/ai/`
- `docs/ai/agent-swarm-ai-orchestration.md` → `docs/ai/`
- `docs/ai/oracle-provider-strategy.md` → `docs/ai/`
- `docs/ai/spec-retrieval-and-rag-policy.md` + `.yaml` → `docs/ai/`
- `docs/ai/spec-retrieval-strategy.md` → `docs/ai/`
- `docs/ai/spec-retrieval-tier3-evaluation.md` → `docs/ai/`

**Per-file actions:**
1. `git mv docs/<file> docs/ai/<file>`
2. Update all ACTIVE_* references in the reference graph for this file
3. Create compatibility stub if TEMPORARY_COMPATIBILITY_STUB strategy applies
4. Run `python tools/docs/migration_engine.py validate` for each moved file
5. Update manifest item: move_status → COMPLETE

**Key references to update:**
- AGENTS.md references to `docs/ai/llm-endpoint-strategy.md`, `docs/ai/ai-usage-operating-model.md`
  (lines ~880-884), `docs/ai/spec-retrieval-strategy.md` (line ~603), `docs/ai/llm-and-embedding-strategy.md`
- `tools/llm/run_record.py` and `tools/llm/artifact_index.py` — contain Python string refs to
  `docs/ai/llm-endpoint-strategy.md`
- `.supervisor/skill-registry.yaml` if it references any of these files

---

## TC-DOCS-008: Wave 2 — Automation/Supervision Docs (→ docs/automation/)

**Scope:** ~7 files related to supervision methodology and state machines

**Candidate files:**
- `docs/automation/assistant-supervision-methodology.md` + `.yaml` → `docs/automation/`
- `docs/automation/terminal-closure-state-machine.md` → `docs/automation/`
- `docs/automation/conway-r9-authority-continuity.md` → `docs/automation/`
- `docs/automation/conway-r9-governed-simulation.md` → `docs/automation/`
- `docs/automation/conway-r9-swarm-governance.md` → `docs/automation/`
- `docs/automation/fresh-chat-project-bootstrap.md` + `.yaml` → `docs/automation/`
  (Note: bootstrap is NOT enforced by check_methodology_links.py — safe to move)

**Per-file actions:** Same pattern as Wave 1 (git mv, ref update, validate, checkpoint)

**Key references to update:**
- AGENTS.md line ~911 reference to `docs/automation/assistant-supervision-methodology.md`
- AGENTS.md line ~904 reference to `docs/automation/fresh-chat-project-bootstrap.md`
- Any plans or evidence referencing `docs/conway-r9-*.md`

---

## TC-DOCS-009: Wave 3 — Governance/Policy Docs (→ docs/governance/)

**Scope:** ~12 files covering governance policy, release control, legal, compliance, execution standards

**Candidate files:**
- `docs/governance/compliance-posture.md` → `docs/governance/`
- `docs/governance/legal-and-licensing.md` → `docs/governance/`
- `docs/governance/release-control.md` → `docs/governance/`
- `docs/governance/security.md` → `docs/governance/`
- `docs/governance/source-track-maturity-policy.md` → `docs/governance/`
- `docs/governance/sprint-depth-policy.md` → `docs/governance/`
- `docs/governance/prototype-quarantine-policy.md` → `docs/governance/`
- `docs/taskcard-layer-states.md` → `docs/governance/`
- `docs/governance/project-execution-standards.md` + `.yaml` → `docs/governance/`
- `docs/governance/current-state-and-evidence-authority.md` → `docs/governance/`
- `docs/governance/playbook-layer.md` → `docs/governance/`

**Key references to update:**
- AGENTS.md line ~402 (`docs/governance/security.md`), line ~415 (`docs/governance/legal-and-licensing.md`),
  line ~204 and ~286 (`docs/governance/release-control.md`), line ~637 (`docs/governance/current-state-and-evidence-authority.md`)
- `tools/ai/validators/risk_controls.py` (may reference security.md)
- `tools/governance/ci_skill_attribution_check.py`
- Plans and registries referencing `docs/governance/release-control.md`

**COMPATIBILITY NOTE:** `docs/governance/security.md`, `docs/governance/legal-and-licensing.md`, and
`docs/governance/release-control.md` have very high reference counts (375/523/569). Use
`TEMPORARY_COMPATIBILITY_STUB` strategy for these if any EXTERNAL_COMPATIBILITY_RISK refs exist.

---

## TC-DOCS-010: Wave 4 — Format/Acquisition/Spec Docs (→ docs/python-foss/ or appropriate)

**Scope:** ~14 files related to format understanding, spec handling, acquisition

**Candidate files:**
- `docs/python-foss/format-completion-matrix.md` → `docs/python-foss/` (or `docs/product-factory/`)
- `docs/python-foss/format-expansion-roadmap.md` + `.yaml` → `docs/python-foss/`
- `docs/python-foss/format-feature-matrix-template.md` → `docs/python-foss/`
- `docs/python-foss/format-onboarding-guide.md` → `docs/python-foss/`
- `docs/python-foss/format-representation-model.md` → `docs/python-foss/`
- `docs/python-foss/format-understanding-layer.md` → `docs/python-foss/`
- `docs/python-foss/odf-flat-family-reuse-strategy.md` → `docs/python-foss/`
- `docs/python-foss/non-aspose-format-candidate-registry-plan.md` → `docs/python-foss/`
- `docs/python-foss/acquisition-workflow.md` → `docs/python-foss/` (645 refs — MEDIUM RISK)
- `docs/python-foss/specification-cache.md` → `docs/python-foss/` (743 refs — HIGH RISK, confirm strategy)
- `docs/python-foss/specification-normalization.md` → `docs/python-foss/`
- `docs/python-foss/spec-consumption-workbench.md` → `docs/python-foss/`
- `docs/python-foss/spec-to-source-chain-contract.md` → `docs/python-foss/`

**HIGH RISK files (`specification-cache.md`, `acquisition-workflow.md`):** Given the very high reference
counts, build compatibility stubs AND update all ACTIVE_* (non-historical) references.

**Key references to update:**
- AGENTS.md line ~192 (`docs/python-foss/acquisition-workflow.md`), lines ~570, 603 (spec docs)
- Various plan files and evidence bundles

---

## TC-DOCS-011: Wave 5 — Architecture/Product/Code-Quality Docs

**Scope:** ~10 files covering architecture, code quality, product tracks, commercial model

**Candidate files:**
- `docs/code-quality/architecture-contract.md` → `docs/code-quality/` (or new `docs/architecture/`)
- `docs/code-quality/architecture.md` — REVIEW: may warrant root retention (591 refs, cross-cutting)
  → If not retained: `docs/code-quality/` or create `docs/architecture/`
- `docs/code-quality/source-package-hygiene.md` → `docs/code-quality/`
- `docs/code-quality/capability-feature-compiler-spec.md` → `docs/code-quality/`
- `docs/code-quality/capability-layer-design.md` → `docs/code-quality/`
- `docs/code-quality/compiler-relationship.md` → `docs/code-quality/`
- `docs/code-quality/test-layering.md` → `docs/code-quality/`
- `docs/product-factory/commercial-dotnet-architecture.md` + `.yaml` → `docs/product-factory/`
- `docs/product-factory/commercial-product-capability-model.md` + `.yaml` → `docs/product-factory/`
- `docs/product-factory/product-object-model-edit-save-export-strategy.md` → `docs/product-factory/`
- `docs/product-factory/product-tracks.md` → `docs/product-factory/`

**Decision gate for `docs/code-quality/architecture.md`:** Read the retention policy from TC-DOCS-003.
If it qualifies as `repository_wide_navigation_index`, retain it. Otherwise, move to
`docs/code-quality/` with TEMPORARY_COMPATIBILITY_STUB.

---

## TC-DOCS-012: Wave 6 — Remaining/Ambiguous Docs

**Scope:** Any docs/ root files not covered by Waves 1-5. This includes:
- Files discovered during inventory (TC-DOCS-002) that don't fit the Wave 1-5 categories
- Ambiguous files requiring deeper classification
- `docs/governance/gate-quality-criteria.md` (may belong in docs/governance/)

**Actions:**
1. Review inventory for any unprocessed root files
2. Apply retention policy: move if no valid retention reason
3. Create stubs or update references per established pattern
4. Ensure MISPLACED_MOVABLE_DOCS_REMAINING_AT_ROOT = 0 after this wave

---

## TC-DOCS-013: Rebuild docs/README.md from Final Structure

**Goal:** docs/README.md accurately reflects what remains at root and maps all subfolders.

**Actions:**
1. Read the final docs/ directory state (what's at root, what's in each subfolder)
2. Rewrite `docs/README.md` to:
   - Show only documents that actually remain at root (the ~8 retained files)
   - Concise "Start Here" section for agents and contributors
   - Map of all existing subdirectories with one-line descriptions
   - Links to subfolder README/index files where they exist
   - Distinguish active, generated, historical, deprecated material
   - Add document placement policy note: "New docs should go in a subfolder unless approved"
3. Update/add subfolder README files in any subfolders that now have a significantly different set
   of documents (e.g., docs/ai/ if it received 10 new files)
4. Validate that `check_methodology_links.py` still passes after README update
   (it checks README.md links to methodology files — those files are retained at root)

---

## TC-DOCS-014: Placement/Link Governance Validator + Gap/Taskcard Integration

**Goal:** Add permanent governance so root clutter cannot recur.

**Actions:**

1. Write `docs/governance/documentation-placement-policy.yaml`:
   - `documentation_placement` records per document type (entry_point, governance_policy, etc.)
   - `allowed_at_docs_root`: true only for the 8 retained categories
   - `validation_rules`: patterns to enforce
   - `naming_pattern` per category
   - `removal_plan` for any compatibility stubs

2. Extend or create `tools/governance/check_docs_placement.py`:
   - Check 1: No new files at docs/ root unless in the root-allowlist
   - Check 2: All active references to moved files point to canonical destinations (not stubs)
   - Check 3: Compatibility stubs have deprecation metadata
   - Check 4: Subfolder README files are current
   - Machine-readable output (JSON), nonzero exit on failure
   - Supports: `--changed-scope <files>` mode for CI, `--full` mode for audits

3. Register `check_docs_placement.py` in:
   - `tools/governance/governance_validators.py` or equivalent runner
   - CI: `.github/workflows/ci.yml` (if appropriate)

4. Create required gap entries (GAP-DOCS-*) for any material findings:
   - DOCS_ROOT_MISPLACEMENT gaps for any files that couldn't be moved (need future resolution)
   - LINK_VALIDATOR_GAP if the validator is incomplete
   - GENERATED_REFERENCE_PRODUCER_GAP for any producers not yet repaired

5. Verify: MATERIAL_DOCS_REORGANIZATION_FINDINGS_WITHOUT_GAPS = 0

---

## TC-DOCS-015: Full Verification + Post-Migration Audit

**Goal:** Prove every required counter is zero; produce the post-migration audit YAML.

**Actions:**

1. Run `python tools/docs/migration_engine.py validate --full`:
   - Every destination exists
   - Every active reference resolves to canonical location
   - No old active paths remain (except intentional stubs)
   - Stubs are thin (no duplicated authority)

2. Run `python tools/governance/check_docs_placement.py --full`:
   - Exit 0 required

3. Run `python tools/governance/check_methodology_links.py`:
   - Exit 0 required (retained methodology files are at root, so no changes needed here)

4. Run existing test suite: `.venv/Scripts/pytest tests/tools/test_readme_sync.py -v`
   - All tests pass

5. Run `python tools/docs/migration_engine.py scan-refs --check-stale` to find any remaining
   old-path references that should have been updated

6. Write `reports/documentation/docs-root-post-migration-audit.yaml`:
   - files_originally_at_root: 70
   - files_retained_with_reasons: ~8
   - files_moved: ~62
   - destinations: {docs/ai/: N, docs/automation/: N, ...}
   - references_updated_by_type: {ACTIVE_GOVERNANCE_REFERENCE: N, ...}
   - compatibility_stubs: [{old_path: ..., canonical_path: ..., removal_criteria: ...}]
   - historical_references_preserved: N
   - broken_references: 0
   - stale_references: 0
   - validation_results: {check_methodology_links: PASS, check_docs_placement: PASS, ...}

7. Required counters — all must be 0:
   - MISPLACED_MOVABLE_DOCS_REMAINING_AT_ROOT = 0
   - BROKEN_ACTIVE_REFERENCES = 0
   - UNEXPLAINED_OLD_PATH_REFERENCES = 0
   - ACTIVE_INTERNAL_REFERENCES_USING_DEPRECATED_STUBS = 0
   - DUPLICATE_AUTHORITATIVE_DOCS = 0
   - GENERATED_PRODUCERS_EMITTING_OLD_PATHS = 0

---

## TC-DOCS-016: Idempotency Proof (Second Pass — Zero Material Changes)

**Goal:** Run the full migration process a second time and confirm no material changes occur.

**Actions:**

1. Re-run inventory: `python tools/docs/migration_engine.py inventory`
   - Confirm: same ~8 files at root, all others in subfolders
   - No new unclassified files

2. Re-run reference scan: `python tools/docs/migration_engine.py scan-refs`
   - Confirm: 0 ACTIVE_* references to old paths

3. Re-run governance validator: `python tools/governance/check_docs_placement.py --full`
   - Confirm: PASS, exit 0

4. Re-run methodology link checker: `python tools/governance/check_methodology_links.py`
   - Confirm: PASS, exit 0

5. Re-run `tools/readme_sync/run_sync.py --mode validate`
   - Confirm: no README drift

6. Record second-pass results in `.local/evidences/docs-root-reorganization-001/idempotency-proof.yaml`
   - material_second_run_changes: 0

COUNTER CHECK: MATERIAL_SECOND_RUN_CHANGES = 0

---

## TC-DOCS-017: Evidence Closeout + Final Report

**Goal:** Complete evidence bundle and final narrative report.

**Actions:**

1. Write `reports/documentation/docs-root-reorganization-report.md` covering:
   - Why the previous index-only execution was insufficient
   - Original root count (70) → final root count (~8)
   - Per-wave summary: what moved where
   - Reference updates by type (total counts)
   - Compatibility stubs created (with removal criteria)
   - Historical references preserved
   - Generated producers repaired
   - Governance/skill repairs (new capability, new validator)
   - Test and pilot results
   - Final all-counters-zero verification
   - Final verdict: DOCS_ROOT_REORGANIZED_REFERENCES_PRESERVED_GOVERNANCE_HEALED_AND_IDEMPOTENT

2. Write `.local/evidences/docs-root-reorganization-001/terminal-closeout.yaml`

3. Update CLAUDE.md capability index if needed (run `/sync-capabilities`)

4. Update `docs/README.md` canonical location in MEMORY.md if the structure changes significantly

---

## Verification Plan

**Immediate after each wave:**
- `python tools/docs/migration_engine.py validate --wave N`
- `git diff --check` (no whitespace errors)
- Confirm destination file exists, source file gone (or stub present)

**After TC-DOCS-014:**
- `python tools/governance/check_docs_placement.py --full`
- `python tools/governance/check_methodology_links.py`

**After TC-DOCS-015:**
- `.venv/Scripts/pytest tests/tools/ -v` — all pass
- All required counters = 0

**After TC-DOCS-016:**
- Second-pass confirms idempotency (MATERIAL_SECOND_RUN_CHANGES = 0)

---

## Reuse Notes

- `tools/governance/check_methodology_links.py` — extend, don't replace, for broader link checking
- `tools/readme_sync/validator.py` — relative link validation already exists; reuse pattern
- `.governance/capabilities/registry.yaml` + `.supervisor/skill-registry.yaml` — follow existing registration patterns
- `git mv` for all physical moves (preserves git history)
- `.local/archive/docs-reorg-backup/` for rollback backups before any move

---

## Completion Gate

Close when:
- All 17 taskcards CLOSED
- All 14 required counters = 0
- Final verdict = DOCS_ROOT_REORGANIZED_REFERENCES_PRESERVED_GOVERNANCE_HEALED_AND_IDEMPOTENT


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-01T13:43:12.489966+00:00"
  hardened_at: "2026-07-01T14:00:00.000000+00:00"
  locked_by: "34c4217ef0bd"
  hardening_note: "ITERATION_REQUIRED was a false positive — 3-column table prevented lifecycle_audit from parsing 17 CLOSED taskcards. Fixed to 2-column format. All 17 taskcards confirmed CLOSED."
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
