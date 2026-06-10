# Skills Integration Contract — Product Breadth Handoff Finalization
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001
Contract ID: SKILLS-INTEGRATION-CONTRACT-BREADTH-V1

---

## Overview

This contract provides full governed handoffs for three .NET commercial capabilities:
1. **FODT ExportToMarkdown** (gap: fodt_to_markdown_dotnet)
2. **FODT ExportToTxt** (gap: fodt_to_txt_dotnet)
3. **Netpbm Pipeline** (new R114 capability; replaces stale ai_draft flip_diagonal)

FODS is already READY_FOR_MAINSTREAM from the hardening sprint. This contract covers the remaining two commercial .NET families.

---

## Consumption Guide

### Mainstream

1. Select a target capability from the three packets
2. Read the corresponding handoff YAML (e.g., `fodt-markdown-handoff.yaml`)
3. Execute `add-dotnet-api` skill with `mode: live`
4. Only modify files in `allowed_files` — never touch `forbidden_files`
5. Run focused test command: `dotnet test --filter FullyQualifiedName~<TestClass>`
6. Produce transcript via `validate_skill_transcript.py`
7. Add ledger entry to `reports/r90/product-code-change-ledger.json`
8. If tests fail: use rollback_note to restore and retry
9. Do NOT update poc-targets.yaml — use proposed_capability_delta as a proposal only

### Supervisor

Use `skills-supervisor-field-map.json` for grading rubric. Key grading checks:
- `validate_skill_transcript.py` exits 0 (BLOCKING)
- `new_tests >= 8` (BLOCKING)
- `changed_files subset of allowed_files` (BLOCKING — OVERCLAIMED if violated)
- ledger entry added (NON_BLOCKING — downgrade to ACCEPTED_WITH_LIMITATIONS)

### Acceleration

Skills packets supersede Acceleration ai_draft outputs. See `skills-acceleration-field-map.json`.
- For FODT Markdown: use Skills packet (Accel packet has fixture_error ai_rationale)
- For FODT TXT: use Skills packet only (no Accel packet exists)
- For Netpbm: use Skills packet (Accel chose stale flip_diagonal; Skills selects Pipeline)

---

## Packet Summary

| Capability | Gap ID | Source Files | Test Target | R# |
|-----------|--------|-------------|------------|-----|
| fodt_to_markdown_dotnet | GAP-FODT-DOGFOOD-MD-DOTNET-001 | FodtMarkdownExporter.cs | FodtR114ExportToMarkdownTests.cs | R114 |
| fodt_to_txt_dotnet | GAP-FODT-DOGFOOD-TXT-DOTNET-001 | FodtTxtExporter.cs | FodtR114ExportToTxtTests.cs | R114 |
| netpbm_image_pipeline | GAP-NETPBM-DOGFOOD-PIPELINE-DOTNET-001 | NetpbmImage.cs | NetpbmR114FlipMergePipelineTests.cs | R114 |

---

## Enforcement

All three capabilities use `enforcement_tier: FAIL_CLOSED`.
Any product source change outside allowed_files results in REJECTED grading.
Any test failure results in REJECTED grading.
No capability matrix update may be made until tests pass and Supervisor approves.
