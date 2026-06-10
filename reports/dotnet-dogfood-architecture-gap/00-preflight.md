# Phase 0 Preflight Report
# Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
# RUN_ID: dotnet-dogfood-architecture-gap
# Generated: 2026-06-05

## Python Interpreter

- Path: `.local/venv/Scripts/python` (C:/Users/prora/OneDrive/Documents/GitHub/format-factory/.local/venv/Scripts/python)
- Version: Python 3.13.2
- Status: CONFIRMED (primary interpreter)
- Fallback: Not needed

---

## Preflight File Status

| File | Path | Status | Key Finding |
|------|------|--------|-------------|
| CLAUDE.md | CLAUDE.md | READ | Sprint closeout requires evidence-declaration.yaml + autonomous-cycle run. Hard stops: push, commit, gate 8/11, MCP activation. |
| AGENTS.md | AGENTS.md | READ | Non-negotiable operating contract. No push/commit/gate approval without human authorization. DEC-034 independent verification required before human review. |
| GOVERNANCE.md | GOVERNANCE.md | READ | All 11 gates require human approval. Commercial source (`src/net/`) may not be created until Gate 10 passed and DD3 resolved. 7-level authority hierarchy. |
| session-resume.md | reports/supervisor/session-resume.md | READ | Last sprint: SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001, ACCEPTED, 45 tests, 0 failures. Autonomous continue: True. MODE 4. MCP ACTIVE. |
| next-sprint.md | reports/supervisor/next-sprint.md | READ | TASK-009..012 are pending product deepening tasks for 4 dogfood gaps. See exact wording below. |
| policies.yaml | .supervisor/policies.yaml | READ | max_iterations: 12. supervisor_canonical_loop_command uses autonomous-cycle. selected_product_gaps_file: .local/supervisor/selected-product-gaps.json. |
| skill-registry.yaml | .supervisor/skill-registry.yaml | READ | 18 active skills registered. add-dogfood-export skill: status=active, requires target_ff_library and dogfood_backend_is_format_factory_library validation. |
| add-dogfood-export.md | .claude/commands/add-dogfood-export.md | READ | Step-3 stop condition cited verbatim below. |
| selected-product-gaps.json | .local/supervisor/selected-product-gaps.json | READ | 14 selected gaps. First 4 all priority_score=125. See gap details below. |
| poc-targets.yaml | product-capability-matrix/poc-targets.yaml | READ | FODS/FODT/Netpbm sections read. FODS+FODT dogfood_status shows GAP_DOGFOOD_EXTERNAL for .NET CSV/HTML/Markdown/TXT. No FF target writer library for these formats in .NET. |
| supervisor-worker-contract.md | docs/automation/supervisor-worker-contract.md | READ | 17 required declaration fields identified. See table below. |

---

## Verbatim Step-3 Stop Condition from add-dogfood-export.md

> "Confirm the product-code ledger and validator exist and pass before touching source. If either is missing, stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED`."

(Full stop conditions section from the command file):

```
## Stop Conditions

- The ledger or validator is missing.
- A Format Factory target writer does not exist.
- Paths exceed the explicit handoff.
- External or direct writing remains in the claimed dogfood path.
- Reload or focused tests fail.
```

---

## TASK-009..012 Exact Wording from next-sprint.md

```
- [pending] TASK-009: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet — dogfood_status.fods_to_csv_dotnet
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet — dogfood_status.fods_to_html_dotnet
- [pending] TASK-011: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — dogfood_status.fodt_to_markdown_dotnet
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — dogfood_status.fodt_to_txt_dotnet
```

---

## First 4 Selected Gaps (from selected-product-gaps.json)

| Rank | Gap ID | Format | Capability Path | Current Status | Priority Score |
|------|--------|--------|-----------------|----------------|----------------|
| 1 | commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS | dogfood_status.fods_to_csv_dotnet | GAP_DOGFOOD_EXTERNAL | 125 |
| 2 | commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS | dogfood_status.fods_to_html_dotnet | GAP_DOGFOOD_EXTERNAL | 125 |
| 3 | commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT | dogfood_status.fodt_to_markdown_dotnet | GAP_DOGFOOD_EXTERNAL | 125 |
| 4 | commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT | dogfood_status.fodt_to_txt_dotnet | GAP_DOGFOOD_EXTERNAL | 125 |

---

## All 17 Required Declaration Fields (from supervisor-worker-contract.md)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | run_id | string | Unique run identifier |
| 2 | sprint_id | string | Sprint identifier |
| 3 | evidence_root | string | Path to evidence directory |
| 4 | start_time / end_time | string | ISO timestamps |
| 5 | git_head_start / git_head_end | string | Commit SHAs |
| 6 | git_status_final | string | Git status at end |
| 7 | declared_scope | string | What the sprint intended |
| 8 | planned_work_items | array | All work items with evidence |
| 9 | completed_work_items | array | Item IDs completed |
| 10 | incomplete_work_items | array | Item IDs not completed |
| 11 | changed_files | array | Files created or modified |
| 12 | tests_run | integer | Total tests executed |
| 13 | test_results | object | passed/failed/skipped/errors |
| 14 | evidence_artifacts | array | Paths to evidence files |
| 15 | reports_created | array | Report file paths |
| 16 | worker_self_verdict | string | Worker's assessment |
| 17 | worker_self_grade | string | PASS/PARTIAL/FAIL/BLOCKED |
| 18 | next_recommended_work | array | Suggested next tasks |

Note: The contract table lists 17 rows but field 4 covers two fields (start_time AND end_time) and field 5 covers two fields (git_head_start AND git_head_end), making the effective count 18 named fields in 17 logical groupings as presented in the contract document.

---

## POC-Targets Key Findings (FODS/FODT/Netpbm)

**FODS dogfood_status:**
- fods_to_csv_dotnet: GAP_DOGFOOD_EXTERNAL
- fods_to_html_dotnet: GAP_DOGFOOD_EXTERNAL
- target_ff_library_for_csv_dotnet: "format-factory-csv (when .NET CSV library exists)" — DOES NOT EXIST

**FODT dogfood_status:**
- fodt_to_txt_dotnet: GAP_DOGFOOD_EXTERNAL
- fodt_to_markdown_dotnet: GAP_DOGFOOD_EXTERNAL
- target_ff_library_for_txt: "format-factory-fodt document_to_text (Python)" — Python only, no .NET equivalent

**Netpbm dogfood_status:**
- dotnet_family_export: IMPLEMENTED (cross-format within Netpbm family)
- All Python dogfood paths: IMPLEMENTED

---

## Not Found Files

| File | Status |
|------|--------|
| GOVERNANCE.md | READ (found at repo root) |
| All other preflight files | READ |

No files were NOT_FOUND during preflight.

---

## Preflight Verdict

**PASS**

- Python interpreter: CONFIRMED (.local/venv/Scripts/python, v3.13.2)
- All 11 preflight files: READ
- Session state: AUTONOMOUS_CONTINUE=True, MODE 4, 0 critical contradictions
- Key architectural gap confirmed: No standalone FF target writer libraries for CSV/HTML/Markdown/TXT in .NET
- TASK-009..012 wording captured verbatim
- All 17 declaration fields identified
- Stop condition verbatim captured
