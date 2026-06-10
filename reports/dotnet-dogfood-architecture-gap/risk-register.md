# Risk Register
# Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
# RUN_ID: dotnet-dogfood-architecture-gap
# Generated: 2026-06-05

## Risk Register Table

| Risk ID | Description | Mitigation | Rollback | Severity |
|---------|-------------|------------|----------|----------|
| RISK-001 | select_poc_gaps.py audit (Lane F) inadvertently edits the file, breaking existing gap selection tests | Lane F operates in read-audit mode only. No write tools invoked on this path. All proposed changes go into 08-gap-selector-audit.md as recommendations only. Coordinator confirms file hash before and after Lane F completes. | `git restore tools/supervisor/select_poc_gaps.py` — run `pytest tests/supervisor/` to confirm gap selector tests still pass | MEDIUM |
| RISK-002 | next-sprint.md edit (Lane G) introduces inconsistency with session-resume.md or approval-gates.md | Lane G reads the full current next-sprint.md before proposing any delta. Changes are delta-first: only TASK-009..012 context updated. All non-delta content preserved verbatim. Coordinator reviews Lane G output before accepting. | `git restore reports/supervisor/next-sprint.md` — revert to pre-sprint content | LOW |
| RISK-003 | Declaration overclaims completed status for investigation items before file and test confirmation | Declaration writer (Lane J) only marks items `completed` when the evidence file exists at the declared path AND tests pass (or are not applicable for read-only lanes). Read-only investigation lanes use `partial` or `completed` only with file presence confirmed. | Edit `.local/evidences/dotnet-dogfood-architecture-gap/evidence-declaration.yaml` to downgrade overclaimed items to `partial`. Re-run autonomous-cycle to get corrected grading. | MEDIUM |
| RISK-004 | selected-product-gaps.json is stale relative to current poc-targets.yaml state (generated R98, now R114) | Note the generation timestamp (2026-06-03T02:57:17) in the preflight. Do not re-run select_poc_gaps.py — treat the file as a snapshot for this investigation sprint. Record the freshness gap as a finding in 08-gap-selector-audit.md. | N/A — read-only; no rollback needed. Freshness concern is documented, not actioned. | LOW |
| RISK-005 | Lane I test scaffold (test_validate_dotnet_dogfood_architecture.py) conflicts with existing test files in tests/supervisor/ | Lane I checks existing test files in tests/supervisor/ before creating the scaffold. If a file with the same name exists, Lane I reads it and appends/extends rather than overwrites. | `git restore tests/supervisor/test_validate_dotnet_dogfood_architecture.py` — removes the scaffold if incorrect | LOW |
| RISK-006 | Investigation reports (Lanes A/B/C) make incorrect claims about .NET source structure due to missing files | Lanes A and B use Glob and Read tools on actual src/net/ paths. All claims are grounded in file presence checks. No inference without file read confirmation. | Reports are evidence-only artifacts — no rollback needed. Incorrect findings are corrected in 12-adversarial-challenge.md (Lane K). | LOW |

---

## Severity Definitions

- **HIGH**: Blocks sprint completion or corrupts authoritative files (registry, master-plan, gate records).
- **MEDIUM**: May cause supervisor grading failure (OVERCLAIMED/REJECTED) or require rework before next sprint.
- **LOW**: Minor inconvenience; easy to detect and correct without autonomous continuation impact.

---

## Risk Owner

All risks are owned by the Coordinator (COORD) lane for this investigation sprint.
Risks RISK-001 and RISK-003 require active monitoring before Lane F and Lane J respectively begin execution.
