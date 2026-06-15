---
version: "1.0"
last-updated: "2026-06-15"
phase-available: "all"
gate-required: null
created-by: post-sprint-autonomy-loop sprint
---

# /post-sprint-loop

Run the full Post-Sprint Autonomy Loop: Audit -> Harden -> Execute -> Classify -> Loop until all-green.

## Steps

1. Initialize loop state:
   ```
   python tools/supervisor/post_sprint_loop_controller.py --repo-root . --run-id <run_id> --init
   ```

2. Execute Stage 1 (Audit) per `.supervisor/prompts/prompt1-post-sprint-audit.md`.
   Write outputs to evidence root as `stage1-*` files.

3. Execute Stage 2 (Plan Hardening) per `.supervisor/prompts/prompt2-plan-hardening.md`.
   Read Stage 1 outputs. Write outputs as `stage2-*` files.

4. Execute Stage 3 (Controlled Execution) per `.supervisor/prompts/prompt3-controlled-execution.md`.
   Read Stage 2 taskcards. Execute, score, verify. Write outputs as `stage3-*` files.

5. Classify Stage 3 output:
   ```
   python tools/supervisor/post_sprint_loop_controller.py --repo-root . --classify --stage3-output <stage3_output_path>
   ```

6. Read the classification decision:
   - `ACCEPTED_ALL_GREEN` -> Run adversarial review, then accept
   - `REROUTE_TO_HARDEN` -> Go back to Step 3
   - `REROUTE_TO_AUDIT` -> Go back to Step 2
   - `REROUTE_REWORK` -> Fix failing items, go back to Step 4
   - `MAX_LOOPS_EXCEEDED` -> Stop, report remaining issues
   - `BLOCKED_EXTERNAL` / `HARD_STOP` -> Stop with evidence

7. After acceptance, package evidence:
   ```
   python tools/supervisor/build_declaration_review_package.py --declaration <declaration_path>
   ```

8. Report the absolute evidence package path and SHA-256.

## Loop Decision Rules

| Classification | Next Action |
|---|---|
| STRUCTURED_ALL_GREEN | Adversarial review -> Accept |
| STRUCTURED_NOT_GREEN | Prompt 2 -> Prompt 3 |
| PROSE_ONLY | Prompt 2 -> Prompt 3 |
| MISSING | Prompt 1 -> Prompt 2 -> Prompt 3 |
| SCORES_MISSING | Scoring lane -> Reroute or accept |
| EVIDENCE_MISSING | Evidence packaging lane |
| TASKCARDS_INCOMPLETE | Prompt 2 |
| CONTRADICTORY | Hard stop, investigate |
| BLOCKED_EXTERNAL | Package evidence, stop |

## Max Iterations

Default: 3 outer loops. Configurable via --max-loops.

## Allowed Paths

- `.local/evidences/` (write evidence)
- `.local/supervisor/` (write loop state)
- `reports/supervisor/` (read/write)
- `.supervisor/` (read prompts, schemas, policies)
- `tools/supervisor/` (execute scripts)
- `tests/` (run tests)

## Forbidden Paths

- `registry/format-registry.yaml`
- `AGENTS.md`, `GOVERNANCE.md`
- `plans/master-plan.md` (read only)

## Usage

```
/post-sprint-loop
```
