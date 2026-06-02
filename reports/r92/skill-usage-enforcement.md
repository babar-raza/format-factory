---
sprint: R92
generated_by: r92-worker
---

# Skill Usage Enforcement (Train I)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Rule

All `src/*` changes must be backed by:
1. A governed `.claude/commands/` skill (executed via sprint prompt naming exact paths), OR
2. A generated execution handoff (`/execution-handoff`), OR
3. A backfill exception report for pre-governance changes

## R91 Audit Result

| Changed File | Skill/Handoff | Ledger Entry | Classification |
|-------------|---------------|-------------|---------------|
| src/net/fods/FodsDocument.cs | R91 sprint prompt (add-dotnet-api) | R91-GOVERNED-DOTNET-FODS-SETCELLVALUE-001 | GOVERNED |
| src/net/fodt/FodtDocument.cs | R91 sprint prompt (add-dotnet-api) | R91-GOVERNED-DOTNET-FODT-SAVETOFILE-001 | GOVERNED |

All R91 src/* changes: GOVERNED

## Validator

`tools/supervisor/validate_product_code_ledger.py` — PRESENT
Reports missing ledger entries for any changed src/* file.

## R92 Rule

Every R92 src/* change will:
1. Name the skill/handoff in the sprint execution report
2. Add a ledger entry before the change
3. Run the validator after the change
4. Be listed in the R92 evidence declaration with ledger_refs
