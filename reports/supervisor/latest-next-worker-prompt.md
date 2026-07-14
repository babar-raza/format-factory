# FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
# Generated: 2026-07-13T18:11:56.170299
# Source: Supervisor autonomous-cycle review of CERT-LAYER-HEAL-20260710
# Stream: mainstream
# ADVISORY ONLY -- not a Format Factory authority document

---

## Preflight (read before any code change)

Read these files before writing any code:

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `plans/master-plan.md`
4. `registry/format-registry.yaml`
5. `reports/supervisor/session-resume.md`
6. `reports/supervisor/latest-review.md`
7. `.supervisor/policies.yaml`
8. `.supervisor/skill-registry.yaml`
9. `.local/supervisor/selected-product-gaps.json`
10. `product-capability-matrix/poc-targets.yaml`
11. `CLAUDE.md`

---

## Sprint Identity

- Sprint ID: FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
- Prior sprint: CERT-LAYER-HEAL-20260710
- Prior verdict: ACCEPTED_WITH_REWORK
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: False

---

## Sprint Goal

**Goal:** Advance product POC: FODS .NET Product Deepening; FODT .NET Product Deepening; Netpbm .NET Product Deepening; ZST Python Improvement. Build evidence declaration and run supervisor autonomous-cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.
2. Last instruction MUST be:
   ```
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
3. The declaration must list ALL work items with status, evidence paths, and test references.
4. Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.
5. Evidence is support infrastructure -- the goal is product POC progress.

---

## Governed Product Acceleration Rules

1. Load `.local/supervisor/selected-product-gaps.json` before choosing product work.
2. Resolve each selected product gap through `.supervisor/skill-registry.yaml`.
3. No direct ad-hoc `src/` edits are permitted. Use a governed skill or generated execution handoff.
4. Every `src/` edit MUST be recorded in `reports/r90/product-code-change-ledger.json`.
5. Run `python tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json` after product-code changes.
6. Include at least one dogfood export lane and one package/install proof lane.

---

## Train Manifest

| Train | Group | Title |
|-------|-------|-------|
| A | G1 | Governance Preflight |
| B | G3 | FODS .NET Product Deepening |
| C | G3 | FODT .NET Product Deepening |
| D | G3 | Netpbm .NET Product Deepening |
| E | G4 | ZST Python Improvement |
| F | G4 | Netpbm Python Improvement |
| G | G4 | SYLK Python Improvement |
| H | G4 | TOML Python Improvement |
| I | G4 | NDJSON Python Improvement |
| J | G4 | FODG Python Improvement |
| K | G4 | TSV Python Improvement |
| L | G4 | ABW Python Improvement |
| M | G4 | Gnumeric Python Improvement |
| N | G4 | FODP Python Improvement |
| O | G4 | CSV Python Improvement |
| P | G4 | ODT Python Improvement |
| Q | G4 | QOI Python Improvement |
| R | G4 | DIF Python Improvement |
| S | G4 | XCF Python Improvement |
| T | G4 | ODS Python Improvement |
| U | G5 | Dogfood: fodt -> txt |
| V | G5 | Dogfood: fodt -> html |
| W | G6 | Package Build + Install Proof |
| X | G7 | State + Memory + POC Matrix Sync |
| Y | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before selecting product work.

**Acceptance Criteria:**
- All preflight files read
- No policy violations detected
- Gate states documented

**Files:**
- `reports/<run_id>/00-preflight.md`

## Group G3: Commercial .NET Product

### Train B: FODS .NET Product Deepening

Continue FODS commercial .NET product advancement. Prepare commit-ready packet only. Do not commit or push. External gate: classify specific blocker per AGENTS.md §AG.

**Acceptance Criteria:**
- FODS .NET test count increased or new API proven
- dotnet_status in poc-targets.yaml updated

**Files:**
- `src/net/fods/`
- `tests/net/fods/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
dotnet test tests/net/fods/ --verbosity quiet
```

### Train C: FODT .NET Product Deepening

Continue FODT commercial .NET product advancement. Prepare commit-ready packet only. Do not commit or push. External gate: classify specific blocker per AGENTS.md §AG.

**Acceptance Criteria:**
- FODT .NET test count increased or new API proven
- dotnet_status in poc-targets.yaml updated

**Files:**
- `src/net/fodt/`
- `tests/net/fodt/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
dotnet test tests/net/fodt/ --verbosity quiet
```

### Train D: Netpbm .NET Product Deepening

Continue Netpbm commercial .NET product advancement. Prepare commit-ready packet only. Do not commit or push. External gate: classify specific blocker per AGENTS.md §AG.

**Acceptance Criteria:**
- Netpbm .NET test count increased or new API proven
- dotnet_status in poc-targets.yaml updated

**Files:**
- `src/net/netpbm/`
- `tests/net/netpbm/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
dotnet test tests/net/netpbm/ --verbosity quiet
```

## Group G4: FOSS / Reduced Product

### Train E: ZST Python Improvement

Continue ZST FOSS product. Continue FOSS product deepening and additional compression API coverage

**Acceptance Criteria:**
- ZST Python test count maintained or increased

**Files:**
- `src/python/zst/`
- `tests/python/zst/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/zst/ -x -q
```

### Train F: Netpbm Python Improvement

Continue Netpbm FOSS product. Continue FOSS product deepening and additional Python API coverage

**Acceptance Criteria:**
- Netpbm Python test count maintained or increased

**Files:**
- `src/python/pbm/`
- `src/python/pgm/`
- `src/python/ppm/`
- `tests/python/pbm/`
- `tests/python/pgm/`
- `tests/python/ppm/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/pbm/ tests/python/pgm/ tests/python/ppm/ -x -q
```

### Train G: SYLK Python Improvement

Continue SYLK FOSS product. Continue FOSS product deepening — cell iteration, set_cell_value; package install proof

**Acceptance Criteria:**
- SYLK Python test count maintained or increased

**Files:**
- `src/python/sylk/`
- `tests/python/sylk/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/sylk/ -x -q
```

### Train H: TOML Python Improvement

Continue TOML FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- TOML Python test count maintained or increased

**Files:**
- `src/python/toml/`
- `tests/python/toml/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/toml/ -x -q
```

### Train I: NDJSON Python Improvement

Continue NDJSON FOSS product. Dogfood pipeline integration

**Acceptance Criteria:**
- NDJSON Python test count maintained or increased

**Files:**
- `src/python/ndjson/`
- `tests/python/ndjson/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/ndjson/ -x -q
```

### Train J: FODG Python Improvement

Continue FODG FOSS product. SVG export investigation

**Acceptance Criteria:**
- FODG Python test count maintained or increased

**Files:**
- `src/python/fodg/`
- `tests/python/fodg/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/fodg/ -x -q
```

### Train K: TSV Python Improvement

Continue TSV FOSS product. Dogfood pipeline integration

**Acceptance Criteria:**
- TSV Python test count maintained or increased

**Files:**
- `src/python/tsv/`
- `tests/python/tsv/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/tsv/ -x -q
```

### Train L: ABW Python Improvement

Continue ABW FOSS product. Dogfood pipeline integration

**Acceptance Criteria:**
- ABW Python test count maintained or increased

**Files:**
- `src/python/abw/`
- `tests/python/abw/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/abw/ -x -q
```

### Train M: Gnumeric Python Improvement

Continue Gnumeric FOSS product. Dogfood pipeline integration

**Acceptance Criteria:**
- Gnumeric Python test count maintained or increased

**Files:**
- `src/python/gnumeric/`
- `tests/python/gnumeric/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/gnumeric/ -x -q
```

### Train N: FODP Python Improvement

Continue FODP FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- FODP Python test count maintained or increased

**Files:**
- `src/python/fodp/`
- `tests/python/fodp/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/fodp/ -x -q
```

### Train O: CSV Python Improvement

Continue CSV FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- CSV Python test count maintained or increased

**Files:**
- `src/python/csv/`
- `tests/python/csv/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/csv/ -x -q
```

### Train P: ODT Python Improvement

Continue ODT FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- ODT Python test count maintained or increased

**Files:**
- `src/python/odt/`
- `tests/python/odt/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/odt/ -x -q
```

### Train Q: QOI Python Improvement

Continue QOI FOSS product. Write capability and package install proof

**Acceptance Criteria:**
- QOI Python test count maintained or increased

**Files:**
- `src/python/qoi/`
- `tests/python/qoi/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/qoi/ -x -q
```

### Train R: DIF Python Improvement

Continue DIF FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- DIF Python test count maintained or increased

**Files:**
- `src/python/dif/`
- `tests/python/dif/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/dif/ -x -q
```

### Train S: XCF Python Improvement

Continue XCF FOSS product. Continue FOSS product deepening

**Acceptance Criteria:**
- XCF Python test count maintained or increased

**Files:**
- `src/python/xcf/`
- `tests/python/xcf/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/xcf/ -x -q
```

### Train T: ODS Python Improvement

Continue ODS FOSS product. Continue FOSS product deepening — gates 8-10

**Acceptance Criteria:**
- ODS Python test count maintained or increased

**Files:**
- `src/python/ods/`
- `tests/python/ods/`
- `reports/r90/product-code-change-ledger.json`

**Verification:**
```bash
python -m pytest tests/python/ods/ -x -q
```

## Group G5: Dogfood Exports

### Train U: Dogfood: fodt -> txt

No FF .NET text write library. Prerequisite: Build FormatFactory.Text .NET library with write_text().

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml

### Train V: Dogfood: fodt -> html

No FF .NET HTML write library. Prerequisite: Build FormatFactory.Html .NET library.

**Acceptance Criteria:**
- Export test passes using FF library
- Dogfood status updated in poc-targets.yaml

## Group G6: Package / Install Proof

### Train W: Package Build + Install Proof

Rebuild wheels/sdists for any changed packages. Run installed-workflow smoke test from extracted wheel. Treat missing artifacts as failures, not skips.

**Acceptance Criteria:**
- All changed packages rebuilt
- Installed import test passes
- Package artifacts present in evidence directory

**Files:**
- `packaging/`

**Verification:**
```bash
python -m pytest tests/evidence/ -x -q
```

## Group G7: State / Memory / POC Matrix

### Train X: State + Memory + POC Matrix Sync

Update state/current-state.md, .supervisor/project-memory.md, and product-capability-matrix/poc-targets.yaml with sprint results.

**Acceptance Criteria:**
- poc-targets.yaml reflects actual status (no overclaiming)
- state/current-state.md updated
- project-memory.md entry appended

**Files:**
- `state/current-state.md`
- `.supervisor/project-memory.md`
- `product-capability-matrix/poc-targets.yaml`

## Group G8: Evidence + Supervisor Loop

### Train Y: Evidence Declaration + Supervisor Autonomous-Cycle

Write evidence-declaration.yaml listing ALL work items. Run autonomous-cycle. Verify session-resume.md is regenerated. Validate `reports/r90/product-code-change-ledger.json` for any governed product source edit.

**Acceptance Criteria:**
- evidence-declaration.yaml written with all work items
- autonomous-cycle exits 0 or 3
- session-resume.md regenerated with current data
- approval-gates.md shows correct AUTONOMOUS_CONTINUE

**Files:**
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `reports/supervisor/session-resume.md`

**Verification:**
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```


---

## Hard Prohibitions

- No `git push` without explicit user authorization.
- No `git commit` without explicit user authorization.
- No Gate 8 or Gate 11 approval (requires Babar Raza).
- No `commercial_product_ready: true` in any file.
- No PyPI / NuGet / GitHub release publication.
- No paid external AI API or web automation.
- No MCP activation unless MODE 4 already authorized.
- No destructive git operations (`git reset --hard`, `git clean -fd`, force-push).
- No deletion of existing test files.
- No PENDING markers in final state files.
- No overclaiming: if evidence is missing, declare status honestly.
- No direct ad-hoc `src/` edits outside the governed skill registry or generated handoff.
- No product-code change without a product-code ledger entry.

---

## Final Validation Sequence

After all trains complete, run this exact sequence:

```bash
# 1. Python tests
.local/venv/Scripts/python -m pytest tests/ -x -q --tb=short

# 2. Compile check on supervisor tools
.local/venv/Scripts/python -m py_compile tools/supervisor/autonomous_cycle.py
.local/venv/Scripts/python -m py_compile tools/supervisor/supervisor_loop.py
.local/venv/Scripts/python -m py_compile tools/supervisor/generate_supervisor_packet.py

# 3. .NET tests (if .NET work was done)
dotnet test tests/net/ --verbosity quiet

# 4. Write evidence declaration
# (create .local/evidences/<run_id>/evidence-declaration.yaml)

# 5. Run supervisor autonomous-cycle
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Allowed Verdicts

The sprint MUST end with one of these verdicts in the evidence declaration:

| Verdict | Meaning |
|---------|---------|
| ALL_TRAINS_COMPLETE | All trains passed acceptance criteria |
| PARTIAL_TRAINS_COMPLETE_PUBLICATION_BLOCKED | Some trains done, publication gate blocks remaining |
| REWORK_REQUIRED | Supervisor review found issues requiring repair |
| BLOCKED_EXTERNAL_GATE | Cannot proceed without external gate approval |

---

## Final Artifact Specification

At sprint end, these files MUST exist:

- `.local/evidences/<run_id>/evidence-declaration.yaml` -- declaration of all work items
- `reports/supervisor/session-resume.md` -- regenerated by autonomous-cycle
- `reports/supervisor/approval-gates.md` -- regenerated by autonomous-cycle
- `product-capability-matrix/poc-targets.yaml` -- updated if any product status changed
- `state/current-state.md` -- updated with sprint outcome

---

END OF SUPERVISOR-GENERATED MEGA-TRAIN EXECUTION PROMPT


## Durable Failure Memory Warnings

The following failures have been recorded in durable failure memory.
Address escalated failures with priority.

- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_execution_method_required_validator_failed (seen 164x, last: ff-r570-model-deepening-daf8d8b4)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_source_diff_required_validator_failed (seen 129x, last: r556-zst-skippable)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_idempotency_key_required_validator_failed (seen 96x, last: ff-r570-model-deepening-daf8d8b4)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_claim_classification_validator_failed (seen 7x, last: IDEMPOTENT-SWARM-EXECUTION-20260615-E31FA98)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_route_decision_required_validator_failed (seen 132x, last: ff-r570-model-deepening-daf8d8b4)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_spec_fact_refs_validator_failed (seen 219x, last: cert-integration-healing)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_governed_direct_execution_validator_failed (seen 6x, last: r556-zst-skippable)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_monolith_detection_validator_failed (seen 354x, last: CERT-LAYER-HEAL-20260710)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): exit_code_3_rework_required (seen 394x, last: layer-heal-010)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_source_architecture_failed (seen 19x, last: capability-convergence-iteration-3-20260624)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_skill_transcript_present_failed (seen 27x, last: ff-r570-model-deepening-daf8d8b4)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_qname_class_names_failed (seen 5x, last: r561-csv-tsv-ndjson-odt)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_error_fallback_safety_failed (seen 7x, last: convergence-test-repair-20260624-999bb7)
- ESCALATED FAILURE (GRADING_FALSE_POSITIVE): Item declared completed but no evidence found. Provide evidence at declared paths. (seen 110x, last: FORMAT-FACTORY-LAYER-AUDIT-20260626)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_forbidden_module_names_failed (seen 3x, last: PROD-GOVERNANCE-001)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_spec_fact_refs_in_sal_output_failed (seen 14x, last: cert-integration-healing)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_ledger_continuation_gate_failed (seen 9x, last: r561-csv-tsv-ndjson-odt)
- ESCALATED FAILURE (OVERCLAIM_FAILURE):  (seen 56x, last: TC-ACP-016)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_dotnet_loc_cap_failed (seen 5x, last: ff-sprint-s450-dotnet-fodt-deepening-20260701)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_readme_freshness_failed (seen 87x, last: stateless-juggling-robin-sprint2)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_dependency_direction_failed (seen 5x, last: r560-xcf-gnumeric-abw-dif)
- ESCALATED FAILURE (OVERCLAIM_FAILURE): Stub evidence detected (was ACCEPTED_WITH_LIMITATIONS): ['Evidence consists only of a planning markdown document; no actual execution artifacts (e.g., git commit logs, diff outputs, or build reports) are provided.', 'No concrete proof that the dirty working tree was audited, changes were committed, or that product gaps were selected and validated.', 'Missing the required product‑gap selection file (e.g., selected-product-gaps.json) or any verification that it was created/used.', 'No build or installation evidence to satisfy mandatory outcomes such as package artifacts built or dogfood export path advanced.', 'Claims are listed with dispositions but lack supporting data (e.g., test results, command output, screenshots) to verify those dispositions.'] (seen 3x, last: ff-gates-advancement-20260702)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_V102_failed (seen 9x, last: SYLK-TOML-FOSS-ANALYTICS-BATCH-001)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_analytics_naming_enforced_failed (seen 4x, last: honey-heal-20260704)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_V121_failed (seen 3x, last: FODG-DIF-PYTHON-MUTATION-001)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_root_structure_validator_failed (seen 6x, last: GNUMERIC-TO-NDJSON-DOGFOOD-001)
- WARNING: 36 unresolved failures in failure memory



## Learning-Based Governance Advisories

- **SPRINT_CLOSEOUT_PATTERN** (seen 573x): Sprint declaration validated PASS with sprint_executor_validate.py — *Action:* Continue using sprint_executor_validate.py --repair before closeout
- **TEST_FAILURE** (seen 340x): Sprint ended with 1 test failures (0 new) — *Action:* Fix test failures before closing sprint; never carry forward new failures
- **TEST_FAILURE** (seen 4x): Sprint ended with 2 test failures (0 new) — *Action:* Fix test failures before closing sprint; never carry forward new failures

## Spec-Parity Requirements (from skill registry)

The following skills require `spec_qname` mapping when invoked for product model work.
Any product model task using these skills MUST declare which spec QNames are addressed
and MUST NOT invent arbitrary flat class names without spec authority.

- **add-analytics-function**: spec_qname_required=true
- **add-dotnet-api**: spec_qname_required=true
- **add-dotnet-object-model-feature**: spec_qname_required=true
- **add-python-api**: spec_qname_required=true
- **add-python-object-model-feature**: spec_qname_required=true
- **add-same-format-writer-feature**: spec_qname_required=true
- **implement-spec-stub**: spec_qname_required=true
- **python-qname-code-reviewer**: spec_qname_required=true
- **python-reduced-spec-parity-model**: spec_qname_required=true
- **spec-literal-qname-to-code-mapping**: spec_qname_required=true
- **spec-parity-source-regeneration-and-migration**: spec_qname_required=true
- **spec-shaped-product-architecture-blueprint**: spec_qname_required=true

**Enforcement:** If a product model change is made without citing spec_fact_refs,
governance validator V8 (spec_fact_references) will FAIL the item.
Use SAL output at `.local/sal-output/sal-facts-latest.json` for valid FACT-* refs.

## Lane Selection (Derived from ledger state)

Format ABW: selected_lane=feature | Lane B gaps: 1
Format CSV: selected_lane=feature
Format DIF: selected_lane=feature | Lane B gaps: 1
Format FODG: selected_lane=feature | Lane B gaps: 1
Format FODP: selected_lane=feature | Lane B gaps: 1
Format FODS: selected_lane=feature | Lane B gaps: 1
Format FODT: selected_lane=feature | Lane B gaps: 1
Format GNUMERIC: selected_lane=feature | Lane B gaps: 1
Format NDJSON: selected_lane=feature
Format ODS: selected_lane=feature | Lane B gaps: 1
Format ODT: selected_lane=dom | Lane B gaps: 1
  → Include `deepening_lane: dom` in evidence declaration.
  → Select DOM advancement gap as primary task: GAP-ODT-DOM-D2-MUTATION-AND-ROUNDTRIP-001
Format PBM: selected_lane=feature
Format PGM: selected_lane=feature
Format PPM: selected_lane=feature
Format QOI: selected_lane=feature
Format SYLK: selected_lane=feature | Lane B gaps: 1
Format TOML: selected_lane=feature | Lane B gaps: 1
Format TSV: selected_lane=feature
Format XCF: selected_lane=feature | Lane B gaps: 1
Format ZST: selected_lane=feature

Lane B starvation: ODT require DOM advancement this sprint.
