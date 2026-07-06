# 05-GAPS-CONTRADICTIONS-AND-OPEN-QUESTIONS.md

Issues, contradictions, and open questions discovered during the deep reconnaissance. This is an observation document, not an implementation plan.

---

## Documentation Drift

### ISSUE-DOC-001: Validator Count Discrepancy

> **VERIFICATION (FF-XPLAN-001, 2026-07-06; refreshed 2026-07-06):** The canonical
> count is now **161**, as asserted by `governance_validator_runner.py expected_count=161`
> (134 explicit + 27 from contract registry). `grep -c "def validate_"` across 20 modules
> returns 156. README's "101" remains stale. The count has grown from 129→161 between
> the initial recon and this refresh due to convergence work (FF-XPLAN-001).

| Field | Value |
|---|---|
| Description | Multiple documents report different governance validator counts |
| Affected | `README.md`, `PROJECT_STATUS.md`, `CLAUDE.md`, MEMORY.md, actual code |
| Evidence | README: "101 governance validators". PROJECT_STATUS.md: "101 validators across 11 modules". MEMORY.md: "127 total". `governance_validator_runner.py`: **161 canonical** (134 explicit + 27 contract). `grep -c "def validate_"`: **156 across 20 modules**. |
| Impact | Moderate — readers get wrong impression of governance depth |
| Confidence | HIGH — independently counted from runner and grep |
| Blocks | Blog claim must use verified count (**161** canonical) |
| Likely Interpretation | Count grew rapidly (101 → 127 → 129 → 161) and documentation wasn't updated at each step. Grep returns 156 but canonical runner count is 161 including contract-registry validators. |

### ISSUE-DOC-002: Skill Count Discrepancy

| Field | Value |
|---|---|
| Description | README says "120 skills", actual count is 123 |
| Affected | `README.md` vs `.supervisor/skill-registry.yaml` |
| Evidence | `grep -c "skill_id:" .supervisor/skill-registry.yaml` = 123 |
| Impact | Low — minor count drift |
| Confidence | HIGH |

### ISSUE-DOC-003: Sprint Count Unverified

| Field | Value |
|---|---|
| Description | README claims "840 autonomous sprint cycles" but this was not independently verified |
| Affected | `README.md` |
| Evidence | Report directories exist (r23-r133 + many skills-r*, mainstream-*, acceleration-*) but total was not precisely counted |
| Impact | Low — directionally plausible but exact number unverified |
| Confidence | MEDIUM |
| Likely Interpretation | The numbered reports (r23-r133 = ~110) plus the many skill/mainstream/acceleration series could plausibly reach 840 |

### ISSUE-DOC-004: PROJECT_STATUS.md Generation Date

| Field | Value |
|---|---|
| Description | PROJECT_STATUS.md was auto-generated on 2026-07-02 but some counts are already stale |
| Affected | `PROJECT_STATUS.md` |
| Evidence | Header: "Generated: 2026-07-02T16:07:14+00:00". Reports "101 validators" but actual is 161 canonical. Reports "100 of 103 capabilities" but registry shows 120 active |
| Impact | Moderate — auto-generated status is not re-generated frequently enough |
| Confidence | HIGH |

---

## Missing Implementation Links

### ISSUE-IMPL-001: CSV Module Name Shadows stdlib

| Field | Value |
|---|---|
| Description | Python format package `csv` conflicts with Python's built-in `csv` module |
| Affected | `src/python/csv/` |
| Evidence | `from csv import parse_csv` fails at runtime — Python resolves to stdlib `csv` |
| Impact | HIGH — consumers cannot import the Format Factory CSV package using natural `from csv import ...` |
| Confidence | HIGH — runtime failure observed |
| Likely Interpretation | Package is installed as `format-factory-csv` (pip name) but the import path conflicts. Works only via `sys.path` manipulation or explicit path imports |

### ISSUE-IMPL-002: Write Support Gaps

> **REFRESH (2026-07-06):** Write coverage has improved significantly. Only 3 of 20
> Python formats now lack write/save: QOI, XCF, ZST. The previous count of "~8" was
> based on incomplete directory inspection. ODS, ODT, ABW, Gnumeric, FODG, and FODP
> all now have write/save functions.

| Field | Value |
|---|---|
| Description | 3 of 20 Python formats lack same-format save/write |
| Affected | QOI, XCF, ZST |
| Evidence | `grep -r "def write_\|def save_"` found no write functions in these 3 format dirs |
| Impact | LOW — only 3 formats cannot round-trip; 17 of 20 have write support |
| Confidence | HIGH — exhaustive source search during refresh |

### ISSUE-IMPL-003: SAL Extraction is AI-Assisted, Not Deterministic

| Field | Value |
|---|---|
| Description | The SAL pipeline involves AI-assisted analysis steps, making fact extraction non-deterministic |
| Affected | `tools/specification-authority-layer/`, `tools/ai/` |
| Evidence | `tools/ai/` directory contains pipeline, synthesis, retrieval modules. SAL tools reference AI processing |
| Impact | MEDIUM — reproducibility of fact extraction is uncertain |
| Confidence | MEDIUM |
| Likely Interpretation | SAL facts are validated and cached, so the non-determinism affects extraction runs but not downstream consumers |

### ISSUE-IMPL-004: Four Formats Have Zero SAL Facts

| Field | Value |
|---|---|
| Description | ORA, PAM, XPM, ZPAQ have acquisition packs but no SAL facts and no product source |
| Affected | `acquisition-packs/ora/`, `acquisition-packs/pam/`, etc. |
| Evidence | MEMORY.md states "SAL still 0 for: ora, pam, xpm, zpaq" |
| Impact | LOW — these formats have not progressed past initial acquisition |
| Confidence | HIGH |

---

## Duplicated or Potentially Redundant Components

### ISSUE-DUP-001: Two Capability-to-Feature Compilers

| Field | Value |
|---|---|
| Description | Two separate implementations exist for compiling capabilities into features |
| Affected | `tools/supervisor/capability_feature_compiler.py` (pipeline), `tools/capability_layer/capability_to_feature_compiler.py` (planning) |
| Evidence | Both files exist and serve different purposes per MEMORY.md |
| Impact | LOW — intentional separation (pipeline vs planning) but creates confusion |
| Confidence | MEDIUM |
| Likely Interpretation | Canonical routing notice exists to prevent confusion |

### ISSUE-DUP-002: Machinery LOC Exceeds Product LOC

| Field | Value |
|---|---|
| Description | Supervisor/machinery code (~85K LOC) is larger than all product code (~77K LOC) |
| Affected | `tools/supervisor/` vs `src/python/` + `src/net/` |
| Evidence | `wc -l tools/supervisor/**/*.py` = 85,280; sum of product LOC (Python 54,202 + .NET 22,643) = ~76,845 |
| Impact | MEDIUM — unusual ratio; machinery maintenance cost is significant |
| Confidence | HIGH |
| Likely Interpretation | The "factory is bigger than the product" is intentional but carries scaling risk |

---

## Disconnected or Potentially Unused Components

### ISSUE-DISC-001: Kilo Agent Configuration is Minimal

| Field | Value |
|---|---|
| Description | `.kilo/kilo.jsonc` contains only `{"$schema": "...", "snapshot": false}` — effectively unused |
| Affected | `.kilo/` |
| Evidence | File content inspection |
| Impact | LOW — placeholder configuration |
| Confidence | HIGH |

### ISSUE-DISC-002: Templates Directory Purpose Unclear

> **VERIFICATION (FF-XPLAN-001, 2026-07-06):** INCORRECT. `lane-library.yaml`
> in `templates/` is actively referenced by `tools/skills/lane_selector.py`,
> `prompt_quality_gate.py`, and `swarm_prompt_generator.py`. The templates
> directory is well-integrated into the skill execution pipeline.

| Field | Value |
|---|---|
| Description | `templates/` directory exists but its relationship to active code generation is unclear |
| Affected | `templates/` |
| Evidence | Directory exists; not deeply inspected |
| Impact | LOW |
| Confidence | ~~LOW~~ **REFUTED** — templates are actively used |

### ISSUE-DISC-003: Report Directory Growth (402 MB)

| Field | Value |
|---|---|
| Description | The `reports/` directory is 402 MB and contains hundreds of sprint report directories with no automated archival |
| Affected | `reports/` |
| Evidence | `du -sh reports/` = 402M |
| Impact | MEDIUM — repository size will continue growing |
| Confidence | HIGH |

---

## Cross-Language Inconsistencies

### ISSUE-LANG-001: Python Has 20 Formats, .NET Has 10

| Field | Value |
|---|---|
| Description | .NET product track covers half the formats that Python covers |
| Affected | `src/net/` vs `src/python/` |
| Evidence | Python: 20 format dirs, .NET: 10 format dirs |
| Impact | LOW — by design (Python FOSS is broader, .NET commercial is deeper) |
| Confidence | HIGH |
| Likely Interpretation | Intentional dual-track strategy |

### ISSUE-LANG-002: .NET Has No CI Test Automation

> **VERIFICATION (FF-XPLAN-001, 2026-07-06):** INCORRECT. CI has a full
> `dotnet-build` job (ci.yml) that runs `dotnet restore`, `dotnet build`,
> and `dotnet test` for all .NET projects. The recon missed this job during
> single-pass inspection.

| Field | Value |
|---|---|
| Description | `.github/workflows/ci.yml` runs Python lint and tests but no .NET build or test |
| Affected | .NET test suite |
| Evidence | ~~CI file inspected — no `dotnet test` or `dotnet build` steps~~ **REFUTED**: ci.yml `dotnet-build` job includes restore, build, and test |
| Impact | ~~MEDIUM~~ **NONE** — .NET CI automation exists |
| Confidence | ~~HIGH~~ **REFUTED** |

### ISSUE-LANG-003: .NET Export-Only Formats (HTML, Markdown, TXT)

| Field | Value |
|---|---|
| Description | Three .NET formats (HTML, Markdown, TXT) are write/export-only targets with no parse capability |
| Affected | `src/net/html/` (190 LOC), `src/net/markdown/` (156 LOC), `src/net/txt/` (142 LOC) |
| Evidence | LOC counts and file inspection — these are target writer libraries for FODS/FODT export |
| Impact | LOW — by design (export targets, not standalone format libraries) |
| Confidence | HIGH |

---

## Governance and Process Gaps

### ISSUE-GOV-001: Prompt-Only Governance Rules

| Field | Value |
|---|---|
| Description | Many governance rules exist only in CLAUDE.md and AGENTS.md — enforced by AI compliance, not by code |
| Affected | CLAUDE.md (plan lock rules, supreme directive, post-plan terminal), AGENTS.md (agent contract) |
| Evidence | CLAUDE.md is ~500+ lines of governance instructions; some rules have code enforcement (check_continuation.py) but many rely on agent compliance |
| Impact | MEDIUM — governance is as reliable as the agent's adherence to instructions |
| Confidence | HIGH |
| Likely Interpretation | Known gap; Lane 14 of the correction plan addresses supervision gap enforcement |

### ISSUE-GOV-002: generate_supervisor_packet.py Known Bug

| Field | Value |
|---|---|
| Description | `load_selected_product_gaps` receives list not dict — causes `AttributeError: 'list' object has no attribute 'get'` |
| Affected | `tools/supervisor/generate_supervisor_packet.py` |
| Evidence | MEMORY.md records this as a "pre-existing bug" |
| Impact | LOW — classified as "non-blocking per Supreme Directive" |
| Confidence | MEDIUM |

---

## Open Questions

### OQ-001: How Reproducible is SAL Fact Extraction?

Given that SAL involves AI-assisted steps, can two separate runs produce identical fact sets from the same specification? This affects traceability claims.

### OQ-002: What is the Actual Sprint Count?

README claims 840+. The report directories suggest hundreds of sprints but the exact total was not independently verified. A precise count would require enumerating all report directories and evidence declarations.

### OQ-003: Are All 39,864 Tests Green?

Only 2,887 tests (FODS + ZST) were executed during the initial recon. The full suite may contain failures, skips, or environmental dependencies not visible in collection.

### OQ-004: What is the Publication Timeline?

Gate 11 is the only blocker for publication. No evidence of a target date or decision criteria was found beyond "requires Babar Raza business approval."

### OQ-005: How Do Stale Plan Locks Affect New Contributors?

MEMORY.md documents recurring issues with stale plan locks blocking continuation. A new contributor checking out the repo would need to understand the `.local/supervisor/` state management to work with the autonomous loop.

### OQ-006: Is the Machinery-to-Product LOC Ratio Sustainable?

At 85K:77K (1.11:1), the machinery is already larger than the products. As more formats are added, will the machinery grow proportionally? Or does it reach a steady state?

### OQ-007: What Percentage of Tests Are Generated vs Hand-Written?

The 39,864 test count is large. Some tests appear to be generated (e.g., test files with systematic naming patterns in `tests/python/deepening/`). The ratio of generated to hand-written tests affects the interpretation of test coverage claims.
