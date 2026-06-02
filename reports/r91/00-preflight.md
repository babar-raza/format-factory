---
sprint: R91
generated_by: r91-worker
---

# R91 Preflight

**Sprint ID:** FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001

## Environment Check

- Python interpreter: `.local/venv/Scripts/python` — confirmed exists
- .NET SDK: available via `dotnet` CLI
- Supervisor pipeline: `tools/supervisor/supervisor_loop.py` — available

## Prior Sprint Outcome

- R90 verdict: `R90_MAINSTREAM_PRODUCT_ACCELERATION_ACTIVE_GOVERNED_POC_PROGRESS_PASS`
- R90 autonomous-cycle exit: 0
- R90 work items accepted: 6/6
- R90 inherited failures: 12 (pre-existing, not introduced by R90)

## Blocking Issues

- 12 inherited test failures block `autonomous_continue` flag
- `session-resume.md` shows `BLOCKED_MISSING_FINAL_VERDICT` (legacy pipeline echo — D91-01)
- Supervisor grades globally, not item-by-item (D91-04)

## Decision

**CONTINUE with R91.**

The 12 inherited failures are pre-existing and classified. A repair lane is added. R91 goal is to heal the autonomous supervisor flow toward the declaration→grading→rework/new-work loop while continuing product advancement.

## Sprint Goal

1. Heal autonomous supervisor flow: declaration→grading→rework/new-work→continuation
2. Repair 12 inherited test failures (pre-existing, non-R91-introduced)
3. Advance product work: FODS .NET SetCellValue, FODT .NET SaveToFile, Netpbm .NET SetPixelColor, PPM installed example, SYLK CSV hardening, FODT dogfood bridge
4. Implement per-item supervisor grading (Trains D + V)
5. Update next-sprint generator to produce rework + new-product-work sections (Train E)
