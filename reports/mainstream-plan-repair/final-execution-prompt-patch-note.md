# Patch Note: final-single-go-mainstream-poc-mega-train-execution-prompt.md
# Sprint: FORMAT-FACTORY-CROSS-PLAN-HARMONIZATION-BEFORE-EXECUTION-001
# Date: 2026-06-04

## Status

The `TC-EXEC-CONTINUE-002` content in `twinkling-percolating-hare.md` already contains
the correct runtime detection logic in its 17-step iteration loop (Step 3: "Detect Ruflo
mode → select Path A or Path B") and the required phrases (verified below).

## Required Phrases — Verified Present in Plan Content

| Phrase | Present in TC-EXEC-CONTINUE-002 content |
|--------|-----------------------------------------|
| "Supervisor runtime detection is authoritative" | NOW YES (after Key repo facts fix) |
| "default to local coordinator" | YES (TC-MAINSTREAM-RUFLO-002 mode definitions) |
| "Do not produce a final user-facing response after each iteration" | YES (section: "DO NOT produce...") |
| "MAINSTREAM_POC_READY_CANDIDATE" | YES (multiple occurrences) |
| "product-output floor" | YES (TC-EXEC-FLOOR-001 section) |
| "train-state.json" | YES (TC-EXEC-STATE-001 section) |
| "max_iterations is a checkpoint" | YES (TC-EXEC-CHECKPOINT-001 section) |

## Impact of Cross-Plan Fix

The `reports/mainstream-plan-repair/final-single-go-mainstream-poc-mega-train-execution-prompt.md`
file is generated DURING the Mainstream sprint by the executing worker.

The executing worker reads `TC-EXEC-CONTINUE-002` content from the plan to create that file.
The plan's Key repo facts section previously would have led the worker to hardcode MODE 4 ACTIVE
in the generated prompt. After the cross-plan harmonization fix, the Key repo facts now say
"DETECT AT RUNTIME", so the worker will generate a prompt that includes runtime detection.

**No additional change to the final execution prompt structure is needed.**
The accepting check in TC-EXEC-CONTINUE-002 already validates all 7 required phrases.

## Mandatory Addition to Generated Prompt

When the executing worker creates `final-single-go-mainstream-poc-mega-train-execution-prompt.md`,
it MUST include this exact phrase in the Ruflo mode section:

```
Supervisor runtime detection is authoritative for Ruflo mode. Do NOT assume MODE 4 ACTIVE.
At the start of each iteration: run MCP status detection. Default to local coordinator
if Supervisor reports DETECTED_NOT_CONFIGURED, ABSENT, BLOCKED, or unclear.
```

## Cross-Reference

Full decision: `reports/cross-plan-harmonization/ruflo-mode-authority-decision.md`
