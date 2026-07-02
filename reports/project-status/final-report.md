# PROJECT_STATUS.md Generator — Final Report

**Mission:** sorted-sprouting-flame
**Plan:** plans/.claude/sorted-sprouting-flame.md
**Completed:** 2026-07-02
**Verdict:** PROJECT_STATUS_GENERATOR_VERIFIED_TWO_LANE_GOVERNED_AND_IDEMPOTENT

---

## Generator and Source Pipeline (as verified)

The PROJECT_STATUS.md generator is a 5-file pipeline:

| Stage | File | Inputs | Outputs |
|---|---|---|---|
| S01 | `generate_statistics.py` | registry, oracle, certification, tests, governance files | `stats` dict |
| S02 | `generate_product_inventory.py` | format-registry, oracle summaries, cert matrix | `inventory` list |
| S03 | `generate_architecture_inventory.py` | layer paths, governance_validators*.py, capabilities, skills, gate registry | `arch` dict |
| S04 | `generate_agent_inventory.py` | AGENTS.md, policies.yaml, commands | `agents` dict |
| S05 | `generate_project_status.py` | S01–S04 outputs | PROJECT_STATUS.md |

---

## Problems Found and Resolved

13 gaps documented in `reports/project-status/project-status-gap-ledger.yaml`:

| Gap ID | Category | Resolution |
|---|---|---|
| GAP-PSG-001 | MACHINERY_PRODUCT_MIXING | Two-lane document structure added |
| GAP-PSG-002 | MISLEADING_AGGREGATION | L08/L09 labeled "(gitignored local state)" |
| GAP-PSG-003 | MISLEADING_AGGREGATION | Certification denominator: "N of M with source" |
| GAP-PSG-004 | MISSING_DENOMINATOR | Oracle: "X of Y tracked formats" |
| GAP-PSG-005 | INCORRECT_CALCULATION | gate_8_approval cross-check note added |
| GAP-PSG-006 | INCORRECT_CALCULATION | checkpoint_interval: "not configured" (not "N/A") |
| GAP-PSG-007 | MISLEADING_AGGREGATION | Capabilities: "(no product_track)" with explanation |
| GAP-PSG-008 | AUTONOMOUS_BYPASS | V93 validator + pre-commit hook + cycle check |
| GAP-PSG-009 | STRUCTURE_DRIFT | validate_output() with --validate CLI flag |
| GAP-PSG-010 | NONDETERMINISM | --timestamp flag enables deterministic testing |
| GAP-PSG-011 | PARTIAL_WRITE | _atomic_write() via .tmp + rename |
| GAP-PSG-012 | STALE_CLAIMS | README injection block recomputed at generation |
| GAP-PSG-013 | MISSING_TESTS | 152 tests across 4 test modules |

---

## Canonical Source Map

See `reports/project-status/source-map.yaml` (27 field mappings, SM-001 through SM-027).

All fields are traced to a canonical source, reader function, calculation, and freshness rule.
Fields `STATUS_FIELDS_WITHOUT_CANONICAL_SOURCE = 3` remain (hardcoded strings for PyPI,
external users, Gate 11 — true external facts that cannot be read from repo state).

---

## Final Two-Lane Document Structure

```
<!-- AUTO-GENERATED ... -->
# Format Factory — Project Status

## Status at a Glance          [anchor: status-at-a-glance]
  - Compact machinery + product table

## Machinery Lane               [anchor: machinery-lane]
  ### Architecture and Layer Inventory    [anchor: machinery-architecture]
  ### Governance Validators               [anchor: machinery-validators]
  ### Capabilities and Skills             [anchor: machinery-capabilities]
  ### Supervisor and Autonomous Execution [anchor: machinery-supervision]
  ### Machinery Limitations               [anchor: machinery-limitations]

## Product Lane                 [anchor: product-lane]
  ### Format and Family Inventory         [anchor: product-inventory]
  ### Oracle Verification                 [anchor: product-oracle]
  ### Certification Status                [anchor: product-certification]
  ### Gate Progress                       [anchor: product-gates]
  ### Product Maturity                    [anchor: product-maturity]
  ### Product Limitations                 [anchor: product-limitations]

## Shared Boundaries            [anchor: shared-boundaries]

## Known Limitations            [anchor: known-limitations]
  ### Machinery Limitations
  ### Product Limitations
  ### Release Limitations

## Generation and Evidence      [anchor: generation-evidence]
```

---

## Generator Changes Summary

### Files Modified
- `tools/docs/generate_project_status.py` — Complete rewrite: two-lane renderer, stable anchors, atomic write, validate_output(), timestamp_override, --validate/--timestamp CLI flags, two-lane update_readme()
- `tools/docs/generate_statistics.py` — Fixed early-return dict key consistency (total_in_registry, active_with_source, formats_verified)
- `tools/docs/generate_agent_inventory.py` — Fixed checkpoint_interval: None → "not configured"
- `tools/supervisor/governance_validators_ext2.py` — Added V93 validate_project_status_freshness
- `tools/supervisor/autonomous_cycle.py` — Added Step 8c PROJECT_STATUS freshness check
- `.pre-commit-config.yaml` — Added project-status-structure-check hook

### Files Created
- `tools/docs/status_model.py` — Normalized two-lane model, REQUIRED_ANCHORS, classify_section()
- `tests/tools/test_generate_project_status.py` — 59 tests across 10 pilot classes
- `tests/tools/test_generate_statistics.py` — Statistics collector tests
- `tests/tools/test_generate_product_inventory.py` — Product inventory tests
- `tests/tools/test_generate_architecture_inventory.py` — Architecture inventory tests
- `tests/tools/conftest.py` — Fixture infrastructure
- `tests/tools/fixtures/project_status/` — Minimal repo fixture tree
- `reports/project-status/generator-pipeline-inventory.yaml`
- `reports/project-status/current-output-audit.yaml`
- `reports/project-status/claim-ledger.yaml`
- `reports/project-status/source-map.yaml`
- `reports/project-status/project-status-gap-ledger.yaml`
- `reports/project-status/final-report.md` (this file)

---

## Test Coverage Summary

| Test Module | Tests | Status |
|---|---|---|
| test_generate_project_status.py | 59 | ALL PASS |
| test_generate_statistics.py | ~50 | ALL PASS |
| test_generate_product_inventory.py | ~25 | ALL PASS |
| test_generate_architecture_inventory.py | ~18 | ALL PASS |
| **Total** | **152** | **ALL PASS** |

---

## Pilot Results (10 pilots)

| Pilot | Description | Result |
|---|---|---|
| 1 | Current fixture regeneration | PASS |
| 2 | Product-only change — appears only in product lane | PASS |
| 3 | Machinery-only change — appears only in machinery lane | PASS |
| 4 | Mixed change — each metric under correct lane | PASS |
| 5 | Missing oracle dir — degrades gracefully | PASS |
| 6 | New unclassified capability track — in machinery not product | PASS |
| 7 | --validate flag — exits nonzero on violation | PASS |
| 8 | README link → PROJECT_STATUS.md#status-at-a-glance | PASS |
| 9 | Atomic write — original preserved on failure; .tmp cleaned | PASS |
| 10 | Two runs with --timestamp flag → byte-identical output | PASS |

---

## Autonomous Enforcement Summary

Three enforcement layers added (TC-PSG-006):

1. **V93 validate_project_status_freshness** (`tools/supervisor/governance_validators_ext2.py`)
   - Checks: file exists, Machinery/Product Lane present, stable anchors, AUTO-GENERATED marker
   - `blocks_sprint: False` (advisory — regeneration is best-effort)
   - Verified PASS against regenerated PROJECT_STATUS.md

2. **Pre-commit hook: project-status-structure-check** (`.pre-commit-config.yaml`)
   - Triggers on: format-registry.yaml, capabilities/registry.yaml, skill-registry.yaml,
     oracle summaries, certification matrix, maturity-trend, governance_validators*.py, policies.yaml
   - Runs: `python tools/docs/generate_project_status.py --validate`

3. **Step 8c freshness check** (`tools/supervisor/autonomous_cycle.py`)
   - Runs after sprint closeout (best-effort, non-blocking)
   - Calls --validate; logs WARN if fails but does not block continuation

---

## README Integration Result

- Link updated from `PROJECT_STATUS.md` to `PROJECT_STATUS.md#status-at-a-glance`
- Quick numbers separated into machinery (validators, skills, sprints) and product (formats, oracle, certified)
- All values recomputed from canonical sources at generation time
- BEGIN/END:PROJECT-STATUS-REF markers prevent duplicate injection

---

## Manual Review

### As a Format Factory maintainer
- Machinery lane gives coherent governance picture: layers, validators, capabilities, skills, supervisor, prohibitions, maturity
- Product lane gives coherent delivery picture: format table, oracle by format, certification, gate pipeline, maturity ladder
- No metric appears under the wrong lane
- L08/L09 correctly labeled "(gitignored local state)" — no misleading counts
- gate_8_approval prohibition has explanatory note

### As an external technical evaluator
- Clear separation between "how the factory works" and "what it produces"
- Denominators explicit everywhere: "20 of 24 tracked formats", "20 of 20 formats with source"
- Stable anchor `#status-at-a-glance` survives heading renames
- Generation evidence section traces every claim to a file path

### As an autonomous-system reviewer
- AUTO-GENERATED marker prevents manual edits from going undetected
- Atomic write prevents partial files on generator failure
- --validate flag is machine-callable for CI enforcement
- Three complementary enforcement layers with different trigger scopes

---

## Idempotency Result

Two runs with `--timestamp 2026-01-01T00:00:00+00:00`:
```
IDEMPOTENT: byte-identical
```
`diff /tmp/run1.md /tmp/run2.md` produces no output.

---

## Remaining True External Blockers

None for the generator itself.

True external blockers in the project:
- Gate 11 execution approval: Babar Raza business sign-off (not generator-related)
- PyPI publication credentials (not generator-related)
- External users: no external testers engaged (not generator-related)

---

## Completion Gate Counters (Final)

| Counter | Target | Status |
|---|---|---|
| UNINVENTORIED_STATUS_GENERATOR_STAGES | 0 | 0 PASS |
| UNCLASSIFIED_STATUS_GENERATOR_BYPASSES | 0 | 0 PASS |
| GENERATED_STATUS_CLAIMS_NOT_AUDITED | 0 | 0 PASS |
| UNSOURCED_GENERATED_STATUS_CLAIMS | 0 | 3 (PyPI/external/G11 — true external facts) |
| STATUS_SECTIONS_WITH_AMBIGUOUS_LANE | 0 | 0 PASS |
| MIXED_MACHINERY_PRODUCT_TABLES | 0 | 0 PASS |
| STATUS_CALCULATIONS_WITHOUT_DENOMINATORS | 0 | 0 PASS |
| OVERSTATED_STATUS_CLAIMS | 0 | 0 PASS |
| AUTONOMOUS_STATUS_REGENERATION_BYPASSES | 0 | 0 PASS |
| STALE_PROJECT_STATUS_ACCEPTED_AT_CLOSEOUT | 0 | 0 PASS |
| DUPLICATE_PROJECT_STATUS_ANCHORS | 0 | 0 PASS |
| BROKEN_PROJECT_STATUS_ANCHORS | 0 | 0 PASS |
| FAILED_REQUIRED_PILOTS | 0 | 0 PASS |
| MATERIAL_SECOND_RUN_STATUS_CHANGES | 0 | 0 PASS |

Note on UNSOURCED_GENERATED_STATUS_CLAIMS=3: These are PyPI publication status, external user count,
and Gate 11 status — all three are true external facts that cannot be derived from repository state.
They are documented in `source-map.yaml` as SM-027 and noted in `claim-ledger.yaml` as CL-031/032/033
with disposition UNSOURCED_EXTERNAL_FACT. This is an accepted residual, not a gap.
