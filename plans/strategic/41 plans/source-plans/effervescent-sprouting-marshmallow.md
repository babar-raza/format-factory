# Plan: FF-HEAL-QNAME Idempotent Healing Audit
<!-- plan_type: audit_sprint -->
<!-- forensic_audit: 2026-07-10 — 20 critical/high findings healed -->

## Context

The user has requested an **idempotent healing sprint** that audits the full format-factory chain from SPEC → SAL FACTS → QNAME → CAPABILITIES → FEATURES → OBJECT MODEL → SOURCE → APIs → TESTS → EVIDENCE. The audit must produce 23 numbered output files plus `evidence-declaration.yaml` and `evidence-bundle.zip` under `.local/evidences/FF-HEAL-QNAME-<timestamp>/`, run validators, execute safe repairs, and leave the system demonstrably healthier.

**Verified system state (from forensic exploration, 2026-07-10):**
- Last sprint `vast-weaving-lampson` TERMINAL_CLOSED. `active-plan-lock.json` still locked to that plan — **must be overwritten before check_continuation can proceed**.
- `continuation-signal.json`: `iteration=5`, `autonomous_continue=true_with_rework`, `session_id=None`.
- 14,644 SAL facts. **167** governance validators (not 165 — V149 added at governance_validator_runner.py:813). 120 capabilities.
- QName migration maps ALREADY EXIST at `reports/qname-migration/` — 20 per-format maps, **18 needing migration, 2 fully compliant** (fods, fodt).
- `tools/backfill/` ALREADY EXISTS with 7 real tools: `audit_qname_vs_src.py`, `inventory.py`, `plan_generator.py`, `qname_migration_planner.py`, `qname_structure_validator.py`, `validate_migration_safe.py`, `__init__.py`.
- `governance_validator_runner.py` has NO standalone `__main__` block. Function name: `run_all_governance_validators`.
- `autonomous_cycle.py` IS standalone (`def main()` at line 2665, `if __name__` at line 2767). Use it, NOT `supervisor_loop.py` (120s timeout).
- This plan file is at `C:\Users\prora\.claude\plans\effervescent-sprouting-marshmallow.md` — **external to repo; must be copied to `plans/.claude/` per CLAUDE.md Step 0**.
- No prior FF-HEAL-QNAME run exists — this is run #1.

## Run ID

The executing agent MUST compute the run ID using Python (not shell date substitution):

```python
from datetime import datetime
RUN_ID = "FF-HEAL-QNAME-" + datetime.now().strftime("%Y%m%d-%H%M%S")
```

**Immediately write the run ID to `.local/evidences/current-audit-run-id.txt`** so all subsequent taskcards can read it without re-computing. Every subsequent taskcard reads this file to get `RUN_ID`.

---

## Taskcards

### TC-FHQA-000 — Mandatory Session Bootstrap (MUST RUN FIRST)
**Status:** PENDING
**Lane:** A (Repository, Governance, State)
**Prerequisites:** None — this is the precondition for all other work

**Purpose:** Satisfy CLAUDE.md Step 0 mandatory mechanical enforcement. Without this taskcard, `check_continuation.py` will return `ACTIVE_PLAN_INCOMPLETE` hard stop because `active-plan-lock.json` is still TERMINAL_CLOSED for `vast-weaving-lampson`.

**Steps:**
1. Copy this plan file into the repo:
   ```
   cp "C:/Users/prora/.claude/plans/effervescent-sprouting-marshmallow.md" plans/.claude/effervescent-sprouting-marshmallow.md
   ```
2. Write the plan lock (overwrites the stale TERMINAL_CLOSED lock for vast-weaving-lampson):
   ```
   .venv/Scripts/python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/effervescent-sprouting-marshmallow.md
   ```
   (Falls back to `python` if .venv/Scripts/python fails — write_plan_lock.py uses only stdlib)
   Expected: `.local/supervisor/active-plan-lock.json` updated with `status: IN_PROGRESS`, `plan_path: plans/.claude/effervescent-sprouting-marshmallow.md`.
3. Verify lock wrote correctly:
   ```
   python -c "import json; d=json.load(open('.local/supervisor/active-plan-lock.json')); assert d['status']=='IN_PROGRESS', d['status']; print('LOCK_OK:', d['plan_path'])"
   ```
4. Compute and persist run ID:
   ```
   python -c "from datetime import datetime; rid='FF-HEAL-QNAME-'+datetime.now().strftime('%Y%m%d-%H%M%S'); open('.local/evidences/current-audit-run-id.txt','w').write(rid); print('RUN_ID:', rid)"
   ```
   Create `.local/evidences/` if it doesn't exist: `mkdir -p .local/evidences/`
5. Read the run ID back and create run folder:
   ```
   python -c "rid=open('.local/evidences/current-audit-run-id.txt').read().strip(); import os; os.makedirs(f'.local/evidences/{rid}', exist_ok=True); print('RUN_FOLDER:', rid)"
   ```

**Completion criteria:** `active-plan-lock.json` has `status=IN_PROGRESS` for this plan path. `.local/evidences/current-audit-run-id.txt` exists. Run folder exists.

**Rollback:** If write_plan_lock.py fails, manually write the JSON:
```python
import json; from datetime import datetime, timezone
lock={"plan_path":"plans/.claude/effervescent-sprouting-marshmallow.md","status":"IN_PROGRESS","last_taskcard":"TC-FHQA-000","updated_at":datetime.now(timezone.utc).isoformat()}
open('.local/supervisor/active-plan-lock.json','w').write(json.dumps(lock,indent=2))
```

**Post-completion:** Update plan lock last_taskcard:
```
python -c "import json,pathlib; f=pathlib.Path('.local/supervisor/active-plan-lock.json'); d=json.loads(f.read_text()); d['last_taskcard']='TC-FHQA-000'; f.write_text(json.dumps(d,indent=2))"
```

---

### TC-FHQA-001 — Preflight + Run Folder Setup
**Status:** PENDING
**Lane:** A (Repository, Governance, State, Evidence)
**Prerequisites:** TC-FHQA-000 complete. Run ID file exists.

**Steps:**
1. Read run ID: `RID=$(cat .local/evidences/current-audit-run-id.txt)` — all writes go to `.local/evidences/$RID/`
2. Run: `git status`, `git log --oneline -5`, `git diff --stat HEAD` — capture output
3. Inventory dirty files by category (sprint artifact / product source / machinery / docs / unknown / risky)
4. List existing evidence runs: `ls .local/evidences/ | grep FF-HEAL-QNAME` — prior runs of this audit type
5. Write **`00-run-index.md`** — run ID, timestamp, branch, HEAD commit, list of all 25 expected output artifacts with PENDING status:
   - 00-run-index.md, 01-preflight-state.md, 02-previous-run-review.md, 03-system-chain-audit.md, 04-qname-audit.md, 05-src-product-compliance.yaml, 06-src-source-quality-review.md, 07-sal-audit.md, 08-capability-layer-audit.md, 09-skill-inventory-and-gaps.md, 10-downstream-layer-audit.md, 11-autonomous-supervisor-audit.md, 12-lane-separation-risk.md, 13-backfill-facility-audit.md, 14-product-maturity-matrix.yaml, 15-traceability-matrix.yaml, 16-gap-matrix.yaml, 17-taskcards.yaml, 18-repair-plan.md, 19-execution-log.md, 20-validation-log.md, 21-idempotency-report.md, 22-next-run-prompt.md, 23-final-verdict.md, evidence-declaration.yaml, evidence-bundle.zip
6. Write **`01-preflight-state.md`** — git state, dirty file inventory by category, untracked files, risky files flagged, continuation-signal.json state (iteration=5, autonomous_continue=true_with_rework)
7. Write **`02-previous-run-review.md`** — result: "FIRST_RUN of FF-HEAL-QNAME — no prior FF-HEAL-QNAME runs found"; note related prior runs (backfill/, qname migration maps already at reports/qname-migration/ from Phase F audit); list what is verified-stable vs what needs audit

**Output files:** 00-run-index.md, 01-preflight-state.md, 02-previous-run-review.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-001`

---

### TC-FHQA-002 — System Chain Audit (Full SPEC → EVIDENCE Chain)
**Status:** PENDING
**Lane:** A + B (Repository + QName)
**Prerequisites:** TC-FHQA-001 complete

**Steps:**
1. Read `plans/strategic/spec-to-feature-radical-correction-plan.md` lines 1–200 (chain definition + lane manifest)
2. Read `registry/odf-ontology/qname-to-code-map.yaml` (first 100 lines — QName authority structure)
3. Read `registry/python-qname-architecture.json` (full file — per-format class inventory)
4. Read `.governance/capabilities/registry.yaml` lines 1–300 — assess whether `source_fact_ids` and `obligation_ids` fields are present in capability entries
5. Read `tools/capability_layer/capability_compiler.py` lines 1–100 (SAL→capability chain)
6. Read `tools/supervisor/capability_feature_compiler.py` lines 1–100 (capability→feature chain / gap→work-item)
7. Assess each chain link with Green/Yellow/Orange/Red/Gray + file-path evidence:
   - **SPEC**: ODF 1.3 + format-specific specs (authority: registry/format-registry.yaml)
   - **SAL**: .local/spec-cache/sal-facts-latest.json (14,644 facts — is ingestion deterministic and reproducible?)
   - **QNAME**: registry/odf-ontology/ + reports/qname-migration/summary.json (18/20 formats need migration)
   - **CAPABILITY**: .governance/capabilities/registry.yaml (do capabilities cite `source_fact_ids` → FACT-* ?)
   - **FEATURE**: tools/supervisor/capability_feature_compiler.py → .local/supervisor/next-work-items.json
   - **CLASS/PROPERTY/METHOD**: src/python/{format}/spec/ (do spec classes have spec_qname + spec_fact_ref?)
   - **TEST**: tests/python/{format}/test_*_spec_qname*.py (do tests verify chain?)
   - **EVIDENCE**: .local/evidences/*/evidence-declaration.yaml (do declarations cite provenance_chain?)
8. Write **`03-system-chain-audit.md`** — chain status table, per-link assessment, what breaks and where, file-path evidence for each verdict

**Output files:** 03-system-chain-audit.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-002`

---

### TC-FHQA-003 — QName Audit + Per-Product Compliance Matrix
**Status:** PENDING
**Lane:** B (QName Schema and Source Organization)
**Prerequisites:** TC-FHQA-002 complete

**Steps:**
1. Read `registry/odf-ontology/qname-to-code-map.yaml` (full file — QName → canonical class → facade mapping)
2. Read `registry/odf-ontology/namespace-tree.yaml` and `prefix-namespace-registry.yaml`
3. Read `reports/qname-migration/summary.json` — note: 18 formats needing migration, 2 fully compliant
4. For the 2 compliant formats: read their migration map to understand what "compliant" means
5. Grep for `spec_qname` in `src/python/`: `grep -r "spec_qname" src/python/ --include="*.py" -l` — list files
6. Grep for `ClassVar` + `spec_qname` together: `grep -r "ClassVar.*spec_qname\|spec_qname.*ClassVar" src/python/ --include="*.py" -l`
7. Read migration maps for 5 pilot formats: `reports/qname-migration/fods-migration-map.json`, `csv-migration-map.json`, `zst-migration-map.json`, `dif-migration-map.json`, `toml-migration-map.json` — note MATCH vs MISSING_CLASS vs WRONG_PATH vs MISSING_SPEC_QNAME counts
8. For 5 pilot formats, sample one spec/ class file each to verify compliance pattern
9. Check validators V111/V112 (spec_qname enforcement) — read governance_validators_spec.py lines 1–100
10. Write **`04-qname-audit.md`** — QName authority source, naming rules (namespace:localname → NamespaceClass → FacadeClass in Compat/), gap summary from migration maps, validator coverage
11. Write **`05-src-product-compliance.yaml`** — per-product compliance matrix for all 20 FOSS Python + 4 .NET formats:
    - Populate from `reports/qname-migration/` data for Python formats; .NET: from direct sampling of `src/net/` spec files
    - Fields: product, language, format, current_source_root, expected_qname_root, spec_qname_status (MATCH/MISSING/PARTIAL), namespace_status, folder_structure_status, validator_proof, backfill_status, source_quality_rating (Green/Yellow/Orange/Red/Gray), maturity_level (P0-P8), required_fix
    - Do NOT claim "inspected directly" for formats not sampled — mark source as "migration-map-derived"

**Output files:** 04-qname-audit.md, 05-src-product-compliance.yaml
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-003`

---

### TC-FHQA-004 — Source Quality Review
**Status:** PENDING
**Lane:** C (Product Source Quality)
**Prerequisites:** TC-FHQA-003 complete

**Steps:**
1. Read `docs/code-quality/production-library-standard-v2.md` lines 1–120 (scoring rubric, RULE-LIB-001 through RULE-LIB-010)
2. Sample these exact Python files (use absolute paths from repo root):
   - `src/python/fods/fods/fods_parser.py` (first 80 lines)
   - `src/python/fodt/fodt/fodt_parser.py` (first 80 lines) — verify path with `ls src/python/fodt/fodt/` first
   - `src/python/csv/csv/models.py` (first 80 lines) — verify path with `ls src/python/csv/csv/` first
   - `src/python/dif/dif/dif_parser.py` (first 80 lines) — verify path with `ls src/python/dif/dif/` first
   - `src/python/zst/zst/zst_codec.py` (first 80 lines) — verify path with `ls src/python/zst/zst/` first
   - **Path verification rule:** For each format, first run `ls src/python/{format}/{format}/` to confirm the nested package path exists; if different, find the correct path.
3. Sample .NET files:
   - `src/net/fods/FodsDocument.cs` (first 60 lines)
   - `src/net/csv/` — list directory then read main .cs file
4. Score each sampled file 0-10 on: modularity, object model quality, spec alignment, qname alignment, parser/model/writer separation, API usability, error handling, documentation, maintainability, export readiness
5. Flag GOV_BLOCK risks: cross-reference any file > 800 LOC against `registry/source-structure-baseline.json` to determine if it's a known violation (exempt) or new violation (BLOCK)
6. Write **`06-src-source-quality-review.md`** — per-format scores, GOV_BLOCK risks with file paths, quality ratings

**Output files:** 06-src-source-quality-review.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-004`

---

### TC-FHQA-005 — SAL Audit
**Status:** PENDING
**Lane:** E (SAL / Spec Authority Layer)
**Prerequisites:** TC-FHQA-004 complete

**Steps:**
1. Read `tools/spec/merge_sal_facts.py` lines 1–80 (determinism, versioning, merge logic)
2. Read `.local/spec-cache/sal-facts-latest.json` lines 1–60 (schema: generated_at, generator, formats_processed, spec_facts_total, results[])
3. For 5 formats (fods, csv, zst, toml, dif): read `reports/qname-migration/{format}-migration-map.json` — check whether SAL fact IDs (FACT-*) are referenced in migration map entries
4. Read `tools/supervisor/governance_validators_sal.py` (full, 296 lines — what SAL validators enforce)
5. Read `tools/supervisor/governance_validators_spec.py` lines 1–80 (spec validators)
6. Grep `.governance/capabilities/registry.yaml` for `source_fact_ids`: `grep -c "source_fact_ids" .governance/capabilities/registry.yaml` — count capabilities with SAL traceability
7. Grep `.governance/capabilities/registry.yaml` for `obligation_ids`: `grep -c "obligation_ids" .governance/capabilities/registry.yaml`
8. Check `/ingest-spec-sal` skill: `grep -A 20 "command: /ingest-spec-sal" .supervisor/skill-registry.yaml`
9. Assess: deterministic (same input → same output)? versioned (generated_at field)? stable? validated? consumed downstream?
10. Write **`07-sal-audit.md`** — SAL readiness verdict, fact counts by format, downstream consumption (capability traceability percentage), gaps, ingestion repeatability status

**Output files:** 07-sal-audit.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-005`

---

### TC-FHQA-006 — Capability Layer Audit
**Status:** PENDING
**Lane:** F (Capability Layer)
**Prerequisites:** TC-FHQA-005 complete

**Steps:**
1. Read `.governance/capabilities/registry.yaml` lines 1–300 (first capability entries — assess field structure)
2. Grep for required traceability fields: `grep -c "source_fact_ids\|obligation_ids\|spec_fact_ref" .governance/capabilities/registry.yaml`
3. Read `tools/capability_layer/capability_compiler.py` (first 120 lines — SAL→obligation→capability chain)
4. Read `tools/capability_layer/capability_pipeline.py` (first 80 lines — pipeline structure)
5. Read `tools/supervisor/capability_feature_compiler.py` lines 1–120 (gap→work-item chain; from MEMORY.md this is the canonical PIPELINE tool)
6. Read `reports/capability-layer/gap-ledger-active.json` lines 1–40 (gap structure: capability_id, format_id, gap_type, status, spec_fact_refs)
7. Assess: do capabilities derive from SAL (source_fact_ids → FACT-* ?)? Is capability-to-feature compilation automated (via next-work-items.json)? Are capabilities used in product work selection?
8. Write **`08-capability-layer-audit.md`** — verdict (production-ready/usable-but-incomplete/partially-wired/mostly-aspirational/broken), derivation chain status, SAL→capability traceability percentage, automated vs manual compilation status

**Output files:** 08-capability-layer-audit.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-006`

---

### TC-FHQA-007 — Skill Inventory and Gaps
**Status:** PENDING
**Lane:** D (Skills and Repeatability)
**Prerequisites:** TC-FHQA-006 complete

**NOTE:** Do NOT read `.supervisor/skill-registry.yaml` in full (3,047 lines — context exhaustion risk). Use targeted grep extraction.

**Steps:**
1. Extract skill commands: `grep -n "^  command:\|^    command:" .supervisor/skill-registry.yaml | head -150` — list all skill command names
2. Extract key fields for skills relevant to this audit: `grep -A 5 "qname\|sal_aware\|spec_qname" .supervisor/skill-registry.yaml | head -100`
3. Check for `/qname-backfill` skill: `grep -n "qname-backfill\|qname_backfill" .supervisor/skill-registry.yaml`
4. Check for `/spec-ingestion`, `/sal-ingest`, `/qname-compiler` skills: `grep -n "ingest-spec-sal\|qname-compiler\|backfill\|spec-ingestion" .supervisor/skill-registry.yaml`
5. Read `.supervisor/skill-quality-matrix.yaml` lines 1–80 (quality assessment structure)
6. Cross-reference the required 15 skill types against what was found:
   - spec_ingestion_skill → `/ingest-spec-sal` (exists per MEMORY.md)
   - sal_fact_extraction_skill → `/ingest-spec-sal` (same)
   - qname_compiler_skill → check above grep
   - capability_compiler_skill → check above grep
   - feature_compiler_skill → check above grep
   - object_model_generator_skill → `/add-python-object-model-feature` (exists per CLAUDE.md)
   - parser_generator_skill → not confirmed — grep for it
   - writer_generator_skill → not confirmed — grep for it
   - qname_validator_skill → check if V111/V112 have a skill wrapper
   - src_backfill_skill → `tools/backfill/` exists but no skill; this is a CONFIRMED GAP
   - compatibility_shim_skill → check for Compat/ shim generator
   - test_generation_skill → check above grep
   - evidence_bundle_skill → `/build-evidence-bundle` (exists per CLAUDE.md)
   - regression_audit_skill → check above grep
   - supervisor_lane_skill → `/autonomous-loop` (exists per CLAUDE.md)
7. Write **`09-skill-inventory-and-gaps.md`** — skill inventory table (name, status, qname/SAL/capability integration), confirmed gaps (skills that don't exist), required repairs

**Output files:** 09-skill-inventory-and-gaps.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-007`

---

### TC-FHQA-008 — Downstream + Supervisor + Lane Separation + Backfill Audits
**Status:** PENDING
**Lane:** G, H, I, J
**Prerequisites:** TC-FHQA-007 complete

**Steps:**

**Downstream (Lane G):**
1. Read `plans/strategic/spec-to-feature-radical-correction-plan.md` lines 200–400 (lane definitions §7–§15)
2. Assess: feature→class→property→method chain. Is there a code generator? Is it triggered via skills? Is output validated?

**Supervisor (Lane H):**
3. Read `tools/supervisor/autonomous_cycle.py` lines 1–80 (lane routing, declaration intake)
4. Read `reports/supervisor/approval-gates.md` (current gate status)
5. Read `.local/supervisor/continuation-signal.json` (iteration=5, autonomous_continue=true_with_rework)
6. Assess Gate 11 stop behavior: what triggers it? Is it properly gated?

**Lane Separation (Lane I):**
7. Identify machinery files (tools/supervisor/, .supervisor/, tools/spec/, tools/backfill/) vs product files (src/python/, src/net/)
8. Identify shared files that both lanes touch (registry/, reports/qname-migration/, .local/supervisor/)
9. Assess collision risk: can machinery hardening corrupt src/ ? Can product work corrupt machinery state?

**Backfill (Lane J) — AUDIT existing tools, do NOT design from scratch:**
10. Read `tools/backfill/audit_qname_vs_src.py` lines 1–50 (dry-run mode, READ-ONLY)
11. Read `tools/backfill/qname_structure_validator.py` lines 1–50 (structure validation)
12. Read `tools/backfill/qname_migration_planner.py` lines 1–50 (migration map generation)
13. Read `tools/backfill/validate_migration_safe.py` lines 1–40 (safety validation)
14. Check if any reports/qname-migration/ maps are from previous backfill tool runs: `cat reports/qname-migration/summary.json | python -c "import sys,json; d=json.load(sys.stdin); print('tool:', d.get('tool'), 'date:', d.get('date'))"`
15. Assess: which phases are implemented? Which are missing? Is rollback supported?

**Write outputs:**
16. Write **`10-downstream-layer-audit.md`** — generation chain status, code generator existence, skill trigger status
17. Write **`11-autonomous-supervisor-audit.md`** — supervisor health, lane routing, Gate 11 behavior, continuation state (note: iteration=5 is NOT a stop; `true_with_rework` means address rework items first)
18. Write **`12-lane-separation-risk.md`** — lane boundary map, shared file risk registry, collision matrix, required guardrails
19. Write **`13-backfill-facility-audit.md`** — existing 7 tools audit, phases implemented vs missing, safety assessment, recommendations for completing the facility

**Output files:** 10-downstream-layer-audit.md, 11-autonomous-supervisor-audit.md, 12-lane-separation-risk.md, 13-backfill-facility-audit.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-008`

---

### TC-FHQA-009 — Product Maturity + Traceability Matrix
**Status:** PENDING
**Lane:** K, L, M, N
**Prerequisites:** TC-FHQA-008 complete

**Steps:**
1. Read `registry/python-qname-architecture.json` (full — maturity indicators, spec_classes count per format, SAL fact counts)
2. Check `reports/capability-layer/gap-ledger-stats.txt` — run `ls reports/capability-layer/ | grep stats` first; if missing, use `wc -l reports/capability-layer/gap-ledger-active.json` as proxy
3. Read `registry/format-completion-matrix.yaml` lines 1–100 (completion stages per format)
4. Assign P0-P8 maturity level to all 20 Python FOSS + 4 .NET formats using evidence:
   - P0: skeleton only; P1: loads format; P2: meaningful object model; P3: edit/manipulate; P4: save same format; P5: round-trip; P6: export/convert; P7: meaningful spec coverage; P8: professional production-quality
5. For 3 pilot formats (fods, csv, zst), build spec-to-source-to-test traceability chain:
   - For each: spec source → spec element → SAL fact ID → qname → capability ID → source class → test file → evidence path
   - Use `reports/qname-migration/{format}-migration-map.json` as the bridge
   - Use `.local/spec-cache/sal-facts-{format}.json` for SAL facts
6. Assess .NET/.Python convergence: shared SAL facts? shared qnames in registry/odf-ontology/? shared object model concepts?
7. Assess 500-format scalability — categorize 10 format types (trivial tabular/text, simple binary, container-based, XML spec-heavy, office document, image, archive/compression, database/spreadsheet, multimedia, unknown/proprietary)
8. Write **`14-product-maturity-matrix.yaml`** — format, language, maturity_level (P0-P8), evidence, confidence (high/medium/low), missing_next_level_requirements, qname_blocks_progress (bool), sal_blocks_progress (bool)
9. Write **`15-traceability-matrix.yaml`** — per pilot format: each chain link with status (complete/partial/broken/missing), file_path, evidence
10. Write **`16-gap-matrix.yaml`** — gap_id, layer, lane, severity (Blocker/High/Medium/Low/Advisory), symptom, evidence_path, current_behavior, expected_behavior, root_cause, product_impact, machinery_impact, required_fix, must_fix_before_product_deepening (bool), deferrable (bool), taskcard_id, current_status

**Output files:** 14-product-maturity-matrix.yaml, 15-traceability-matrix.yaml, 16-gap-matrix.yaml
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-009`

---

### TC-FHQA-010 — Taskcards + Repair Plan
**Status:** PENDING
**Lane:** All lanes
**Prerequisites:** TC-FHQA-009 complete (16-gap-matrix.yaml must exist)

**Steps:**
1. Read `16-gap-matrix.yaml` from the run folder
2. Convert every actionable gap into a taskcard following the required structure:
   - objective, ownership, prerequisites, dependencies, execution_steps, validation, evidence, rollback, completion_criteria, status (backlog/ready/active/blocked/validation/complete)
3. Deduplicate against existing taskcards:
   - `ls taskcards/` (root-level taskcards directory — 195 existing .md files)
   - `ls .supervisor/taskcards/` if it exists
   - Do NOT create taskcards that duplicate existing TC-NNN or S-F2F-NN taskcards
   - For overlapping items, reference the existing taskcard ID instead of creating a new one
4. Group new taskcards by required groups: QNAME-AUTH, QNAME-VALIDATORS, QNAME-BACKFILL, SAL-REPAIR, CAPABILITY-REPAIR, FEATURE-COMPILER, SKILL-HARDENING, SRC-STANDARDIZATION, DOTNET-CONVERGENCE, PYTHON-CONVERGENCE, SUPERVISOR-LANES, SUPERVISOR-CONTINUATION, GATE11-STOP, PRODUCT-PILOT, EVIDENCE-LEDGER, TRACEABILITY, MATURITY-MODEL, SCALABILITY
5. Write **`17-taskcards.yaml`** — only NEW taskcards (with duplicate-avoidance notes for any overlapping existing taskcards)
6. Write **`18-repair-plan.md`** — ordered repair plan: highest-impact safe repairs first, scope estimate, rollback notes, governance constraints

**Output files:** 17-taskcards.yaml, 18-repair-plan.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-010`

---

### TC-FHQA-011 — Safe Execution (Minimum Viable Repairs)
**Status:** PENDING
**Lane:** B, D (QName + Skills)
**Prerequisites:** TC-FHQA-010 complete
**Governance:** NO ad-hoc src/ edits. All repairs target tools/, .local/, or reports/ only.

Execute ONLY these safe, high-leverage repairs:

**Repair R1 — Run existing QName structure validator and capture output:**
```
.venv/Scripts/python tools/backfill/qname_structure_validator.py --format fods --out .local/evidences/$RID/qname-fods-structure-report.json
.venv/Scripts/python tools/backfill/qname_structure_validator.py --format csv --out .local/evidences/$RID/qname-csv-structure-report.json
```
(Use `.venv/Scripts/python`, not `python` — system Python lacks required packages.)
If `--all` flag exists: `python tools/backfill/qname_structure_validator.py --all --out .local/evidences/$RID/qname-all-structure-report.json`

**Repair R2 — Run existing QName migration planner for pilot formats:**
```
.venv/Scripts/python tools/backfill/qname_migration_planner.py --format fods --out-dir .local/evidences/$RID/migration-plans/
.venv/Scripts/python tools/backfill/qname_migration_planner.py --format csv --out-dir .local/evidences/$RID/migration-plans/
```
Write `.local/evidences/$RID/qname-compliance-report.txt` summarizing the combined output.
**Do NOT create a new generate_qname_compliance_report.py script** — use existing tools.

**Repair R3 — Assess QName inventory validator gap:**
- Check V111 and V112: `grep -n "V111\|V112\|validate_spec_qname\|spec_qname" tools/supervisor/governance_validators_spec.py | head -20`
- Check V53: `grep -n "V53\|validate.*facade.*spec_qname\|spec_qname.*facade" tools/supervisor/governance_validators.py | head -10`
- If existing validators already cover ClassVar enforcement, document "COVERED BY V111/V112/V53 — no new validator needed"
- If genuine gap: write `tools/supervisor/governance_validators_qname_inventory.py` with `validate_qname_inventory(repo_root)` — add to runner only if this adds real coverage not already in V111-V113
- **CRITICAL: if adding a new validator, the new expected_count = 167 + 1 = 168; update governance_validator_runner.py line 813**

**Repair R4 — Skill gap documentation:**
- Confirm `/qname-backfill` skill is absent from `.supervisor/skill-registry.yaml` (from TC-FHQA-007 findings)
- If absent: add gap entry to `17-taskcards.yaml` group SKILL-HARDENING — do NOT touch skill-registry.yaml directly (requires `/sync-capabilities`)

**Repair R5 — Pilot plan files (read-only documentation):**
- Write `.local/evidences/$RID/fods-qname-backfill-pilot.md` — concrete plan: which files need ClassVar→plain spec_qname fix, which need spec_fact_ref added, which files need namespace_uri
- Write `.local/evidences/$RID/csv-qname-backfill-pilot.md` — same for CSV (simpler format)
- Source data: use R1 and R2 outputs, not guesswork

**Execution log:** Write **`19-execution-log.md`** recording: command, cwd, before-state, after-state, pass/fail for each repair

**Output files:** 19-execution-log.md, .local/evidences/$RID/qname-fods-structure-report.json, .local/evidences/$RID/qname-csv-structure-report.json, .local/evidences/$RID/migration-plans/*, optionally governance_validators_qname_inventory.py
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-011`

---

### TC-FHQA-012 — Validation + Idempotency
**Status:** PENDING
**Lane:** All lanes
**Prerequisites:** TC-FHQA-011 complete

**Steps:**
1. Run new validator tests if R3 created a new validator:
   ```
   .venv/Scripts/pytest tests/supervisor/test_governance_validators_qname_inventory.py -v 2>&1 | tee .local/evidences/$RID/test-new-validator.txt
   ```
2. Run existing governance test suite:
   ```
   .venv/Scripts/pytest tests/governance/ -v --tb=short -q 2>&1 | tee .local/evidences/$RID/test-governance.txt
   ```
3. Run ALL governance validators using the correct invocation (requires a declaration dict as first arg):
   ```python
   python -c "
   import sys, json; sys.path.insert(0, 'tools/supervisor')
   from governance_validator_runner import run_all_governance_validators
   from pathlib import Path
   from datetime import datetime, timezone
   # Minimal health-check declaration — does not claim any real work items
   minimal_decl = {
       'worker_id': 'FF-HEAL-QNAME-health-check',
       'run_id': 'health-check',
       'sprint_id': 'health-check',
       'declared_at': datetime.now(timezone.utc).isoformat(),
       'format_id_scope': 'all',
       'planned_work_items': []
   }
   result = run_all_governance_validators(minimal_decl, Path('.').resolve())
   print('SUMMARY:', result['summary'])
   print('expected_count:', result['expected_count'])
   print('ran_count:', result.get('ran_count', 'N/A'))
   " 2>&1 | tee .local/evidences/$RID/governance-validator-run.txt
   ```
   **Note:** Many validators will WARN/FAIL on an empty declaration — this is expected for a health-check run. What matters is that `ran_count >= expected_count (167)` and no CRITICAL import errors occur.
4. Idempotency check — run qname_structure_validator twice, compare outputs:
   (Use `.local/tmp/` not `/tmp/` — Windows compatibility)
   ```
   mkdir -p .local/tmp
   .venv/Scripts/python tools/backfill/qname_structure_validator.py --format fods --out .local/tmp/qname-idempotency-1.json
   .venv/Scripts/python tools/backfill/qname_structure_validator.py --format fods --out .local/tmp/qname-idempotency-2.json
   python -c "
   import json
   r1=json.load(open('.local/tmp/qname-idempotency-1.json'))
   r2=json.load(open('.local/tmp/qname-idempotency-2.json'))
   assert r1==r2, 'IDEMPOTENCY FAILURE: outputs differ'
   print('IDEMPOTENCY_PASS: outputs are identical')
   "
   ```
5. Verify all 25 expected output artifacts exist in run folder:
   ```python
   import os; rid=open('.local/evidences/current-audit-run-id.txt').read().strip()
   expected=[
       '00-run-index.md','01-preflight-state.md','02-previous-run-review.md',
       '03-system-chain-audit.md','04-qname-audit.md','05-src-product-compliance.yaml',
       '06-src-source-quality-review.md','07-sal-audit.md','08-capability-layer-audit.md',
       '09-skill-inventory-and-gaps.md','10-downstream-layer-audit.md',
       '11-autonomous-supervisor-audit.md','12-lane-separation-risk.md',
       '13-backfill-facility-audit.md','14-product-maturity-matrix.yaml',
       '15-traceability-matrix.yaml','16-gap-matrix.yaml','17-taskcards.yaml',
       '18-repair-plan.md','19-execution-log.md','20-validation-log.md',
       '21-idempotency-report.md','22-next-run-prompt.md','23-final-verdict.md',
       'evidence-declaration.yaml'
   ]
   missing=[f for f in expected if not os.path.exists(f'.local/evidences/{rid}/{f}')]
   print('MISSING:', missing or 'NONE — all 25 artifacts present')
   ```
6. Record: command, cwd, result, pass/fail, output path for every command
7. Write **`20-validation-log.md`** — all commands run with full results
8. Write **`21-idempotency-report.md`** — idempotent operations, non-idempotent operations, what must be fixed to achieve full idempotency

**Failure handling:** If governance validator run fails (non-zero exit), log error and continue — this is best-effort closeout per Supreme Directive.

**Output files:** 20-validation-log.md, 21-idempotency-report.md
**Post-completion:** Update plan lock `last_taskcard: TC-FHQA-012`

---

### TC-FHQA-013 — Final Verdict + Evidence Bundle
**Status:** PENDING
**Lane:** A (Evidence)
**Prerequisites:** TC-FHQA-012 complete

**Steps:**
1. Write **`22-next-run-prompt.md`** — updated audit prompt for run #2 with:
   - Prior run ID and verdict incorporated at top
   - Verified-stable fixes (backfill tools ran, migration maps read, validators passed) noted with VERIFIED_STABLE tag
   - Open taskcard IDs for next run
   - Idempotency instructions: "Skip TC-FHQA-002 through TC-FHQA-009 if run folder from prior run has all files marked complete"

2. Write **`23-final-verdict.md`** — full verdict:
   - Final verdict: `ACCEPTED_WITH_REMAINING_TASKCARDS` or `PARTIAL_REPAIR_WITH_EVIDENCE`
   - Execution-readiness: `READY_AFTER_TARGETED_MACHINERY_REPAIRS` (18/20 Python formats need QName migration before Gate 11)
   - Qname readiness, SAL readiness, Capability readiness, Skill readiness, Backfill readiness, Source quality readiness, .NET/Python convergence status, Supervisor status, Lane separation status
   - Product maturity summary (all 24 formats)
   - All 26 self-check yes/no answers

3. Write **`evidence-declaration.yaml`** per schema at `.supervisor/schemas/evidence-declaration.schema.json`:
   ```yaml
   worker_id: "FF-HEAL-QNAME-AUDIT"
   run_id: "<RUN_ID from current-audit-run-id.txt>"
   sprint_id: "<RUN_ID>"
   declared_at: "<ISO 8601 timestamp>"
   format_id_scope: "all"
   planned_work_items:
     - item_id: "TC-FHQA-000"
       status: "CLOSED"
       evidence_paths:
         - ".local/supervisor/active-plan-lock.json"
         - ".local/evidences/current-audit-run-id.txt"
       worker_self_verdict: "VERIFIED"
     # ... repeat for TC-FHQA-001 through TC-FHQA-013
   test_results:
     passed: <count from test runs>
     failed: <count>
     skipped: <count>
   worker_self_verdict: "ACCEPTED_WITH_REMAINING_TASKCARDS"
   ```
   **Required fields per schema:** worker_id, run_id, sprint_id, declared_at, format_id_scope, planned_work_items[].item_id, .status, .evidence_paths, .worker_self_verdict, test_results.passed, test_results.failed

4. Validate declaration before submitting:
   ```
   .venv/Scripts/python tools/supervisor/sprint_executor_validate.py .local/evidences/$RID/evidence-declaration.yaml --repair
   ```
   Fix any FAIL errors. If validator itself fails, log and proceed.

5. Bundle all run files:
   ```python
   import zipfile, os, hashlib
   rid = open('.local/evidences/current-audit-run-id.txt').read().strip()
   bundle_path = f'.local/evidences/{rid}/evidence-bundle.zip'
   with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
       for fn in os.listdir(f'.local/evidences/{rid}'):
           fp = f'.local/evidences/{rid}/{fn}'
           if os.path.isfile(fp): zf.write(fp, fn)
   sha = hashlib.sha256(open(bundle_path,'rb').read()).hexdigest()
   abs_path = os.path.abspath(bundle_path)
   print(f'BUNDLE: {abs_path}')
   print(f'SHA256: {sha}')
   ```

6. Run sprint closeout (use autonomous_cycle.py, NOT supervisor_loop.py):
   ```
   .venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/$RID/evidence-declaration.yaml
   ```

7. Write plan terminal lock — ALL 14 taskcards closed:
   ```
   python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/effervescent-sprouting-marshmallow.md --terminal
   ```

8. Print absolute bundle path and SHA-256 (already computed in step 5)

**Output files:** 22-next-run-prompt.md, 23-final-verdict.md, evidence-declaration.yaml, evidence-bundle.zip

---

## Critical Files to Read During Execution

| File | Purpose | Verified Exists |
|------|---------|----------------|
| `registry/odf-ontology/qname-to-code-map.yaml` | QName authority | YES |
| `registry/python-qname-architecture.json` | Per-format class inventory | YES |
| `reports/qname-migration/summary.json` | 18/20 formats need migration | YES |
| `reports/qname-migration/{format}-migration-map.json` | Per-format gaps | YES (20 files) |
| `.governance/capabilities/registry.yaml` | Capability derivation | YES |
| `tools/spec/merge_sal_facts.py` | SAL determinism | YES |
| `.local/spec-cache/sal-facts-latest.json` | SAL facts (sample) | YES |
| `.local/spec-cache/sal-facts-{format}.json` | Per-format SAL facts | YES (20 files) |
| `tools/supervisor/governance_validators_sal.py` | SAL validators (296 lines) | YES |
| `tools/supervisor/governance_validators_spec.py` | Spec validators | YES |
| `.supervisor/skill-registry.yaml` | Skills (use grep, not full read) | YES |
| `registry/source-structure-baseline.json` | LOC caps | YES |
| `docs/code-quality/production-library-standard-v2.md` | Quality rubric | YES |
| `registry/format-completion-matrix.yaml` | Per-format completion stages | YES |
| `plans/strategic/spec-to-feature-radical-correction-plan.md` | Chain authority | YES |
| `tools/supervisor/capability_feature_compiler.py` | Gap→work-item chain | YES |
| `.local/supervisor/continuation-signal.json` | Current supervisor state | YES |
| `tools/backfill/qname_migration_planner.py` | Migration planner tool | YES |
| `tools/backfill/qname_structure_validator.py` | Structure validator tool | YES |
| `tools/backfill/audit_qname_vs_src.py` | Dry-run audit tool | YES |

## Existing Utilities to REUSE (not recreate)

| Tool | Correct Invocation | Notes |
|------|--------------------|-------|
| `tools/backfill/qname_structure_validator.py` | `.venv/Scripts/python tools/backfill/qname_structure_validator.py --format {fmt}` | READ-ONLY dry-run |
| `tools/backfill/qname_migration_planner.py` | `.venv/Scripts/python tools/backfill/qname_migration_planner.py --format {fmt} --out-dir {dir}` | Produces per-format migration map |
| `tools/backfill/audit_qname_vs_src.py` | `.venv/Scripts/python tools/backfill/audit_qname_vs_src.py --all` | Full audit |
| `governance_validator_runner` | `python -c "from tools.supervisor.governance_validator_runner import run_all_governance_validators; ..."` | Library function, NOT standalone script |
| `tools/supervisor/autonomous_cycle.py` | `.venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration ...` | Use this, NOT supervisor_loop.py |
| `tools/supervisor/sprint_executor_validate.py` | `.venv/Scripts/python tools/supervisor/sprint_executor_validate.py {decl} --repair` | Validate before autonomous-cycle |
| `tools/supervisor/build_declaration_review_package.py` | `.venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration ...` | Optional ZIP package |

## Governance Constraints

1. **No ad-hoc `src/` edits** — all repairs target `tools/`, `.local/`, or `reports/` only
2. **Expected validator count is 167** (not 165) at `governance_validator_runner.py:813` — if R3 adds a new validator: new count = 168; update that line
3. **No product deepening rotation** (SUSPENDED per MEMORY.md)
4. **Write plan lock after each taskcard** — use `write_plan_lock.py` update or manual JSON edit
5. **Plan terminal** — use `write_plan_lock.py --plan-path plans/.claude/effervescent-sprouting-marshmallow.md --terminal` only when ALL 14 taskcards (TC-FHQA-000 through TC-FHQA-013) are CLOSED
6. **Sprint closeout is best-effort** — if autonomous_cycle.py fails, log and continue to next taskcard
7. **`tools/backfill/` exists** — do NOT create `qname_backfill_planner.py`; real tools are already there; read and run them
8. **`reports/qname-migration/` exists** — do NOT create a new compliance report script; use existing migration maps and tools

## Verification Checklist

Before claiming completion:
- [ ] `.local/supervisor/active-plan-lock.json` has `status: TERMINAL_CLOSED` for this plan path
- [ ] `.local/evidences/current-audit-run-id.txt` exists and matches run folder name
- [ ] All 23 numbered files (00-run-index.md through 23-final-verdict.md) exist in run folder
- [ ] `evidence-declaration.yaml` exists and passed `sprint_executor_validate.py`
- [ ] `evidence-bundle.zip` exists; absolute path + SHA-256 printed
- [ ] `governance_validator_runner` ran with `ran_count >= expected_count (167)`
- [ ] Idempotency: `qname_structure_validator.py` run twice → identical output
- [ ] `18/20 Python FOSS formats needing QName migration` documented in gap matrix

## Execution Order

TC-FHQA-000 → TC-FHQA-001 → TC-FHQA-002 → TC-FHQA-003 → TC-FHQA-004 → TC-FHQA-005 → TC-FHQA-006 → TC-FHQA-007 → TC-FHQA-008 → TC-FHQA-009 → TC-FHQA-010 → TC-FHQA-011 → TC-FHQA-012 → TC-FHQA-013

**TC-FHQA-000 is mandatory first.** All others are sequential. Update plan lock `last_taskcard` after each. Do NOT proceed past any taskcard until its output files exist.

---

## Forensic Audit Log (2026-07-10 — 20 findings healed)

| Finding | Severity | Fix Applied |
|---------|----------|-------------|
| expected_count was 165, actual is 167 | CRITICAL | Updated everywhere to 167; line ref added (governance_validator_runner.py:813) |
| tools/backfill/ has 7 real tools — R3 "create stub" was wrong | CRITICAL | R3 rewritten to RUN existing qname_structure_validator.py + qname_migration_planner.py |
| reports/qname-migration/ has 20 maps (18 needing migration) — R2 "create script" duplicated work | CRITICAL | R2 rewritten to READ existing migration maps; 18/20 gap noted in context |
| governance_validator_runner.py has no __main__ block — `python governance_validator_runner.py` silently fails | CRITICAL | Fixed to correct invocation: `python -c "from tools.supervisor.governance_validator_runner import run_all_governance_validators; ..."` |
| active-plan-lock.json is TERMINAL_CLOSED for old plan — will hard-stop execution | CRITICAL | TC-FHQA-000 added with mandatory lock override |
| Plan file is external to repo — CLAUDE.md mandates copy to plans/.claude/ | CRITICAL | TC-FHQA-000 step 1 is copy + lock |
| supervisor_loop.py used in TC-FHQA-013 (120s timeout) | CRITICAL | Changed to autonomous_cycle.py |
| Run ID via `$(date)` bash sub cannot persist across Write tool calls | CRITICAL | Changed to Python datetime; persisted to current-audit-run-id.txt |
| continuation-signal.json iteration=0 was wrong; actual is 5 with true_with_rework | CRITICAL | Corrected in context |
| No TC-FHQA-000 session bootstrap — CLAUDE.md Step 0 mandatory | CRITICAL | TC-FHQA-000 added as first taskcard |
| evidence-declaration.yaml had no schema reference or required fields | HIGH | Added schema path + required field list with YAML example |
| No declaration validation step before autonomous-cycle | HIGH | TC-FHQA-013 step 4 added sprint_executor_validate.py --repair |
| skill-registry.yaml full read (3,047 lines) risked context exhaustion | HIGH | TC-FHQA-007 changed to targeted grep extraction |
| TC-FHQA-003 claimed "All 20 Python + 4 .NET inspected" but only 5 sampled | HIGH | Added "migration-map-derived" source label; scope disclaimer added |
| TC-FHQA-004 file paths wrong (missing nested `fods/fods/` structure) | HIGH | Corrected to `src/python/fods/fods/fods_parser.py` with ls-verify step |
| No per-taskcard plan lock update | HIGH | Post-completion step added to all 14 taskcards |
| TC-FHQA-008 "design phases 1-16" was wrong — backfill already partly implemented | MEDIUM | Changed to "audit existing tools" not "design from scratch"; renamed file to 13-backfill-facility-audit.md |
| TC-FHQA-010 deduplication target was docs/taskcards/ — should be taskcards/ at root | MEDIUM | Fixed to `taskcards/` (root level, 195 existing files) |
| TC-FHQA-012 idempotency test was vague | MEDIUM | Added specific command: qname_structure_validator.py run twice + diff |
| Output count inconsistency (23 numbered + 2 unnumbered) | LOW | Clarified as "23 numbered files + evidence-declaration.yaml + evidence-bundle.zip = 25 total artifacts" |
