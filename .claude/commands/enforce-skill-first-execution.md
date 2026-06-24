---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: COMPOSITE_SKILL
idempotency: "Safe to rerun — each step is idempotent; steps 4-5 produce same output if registry unchanged"
loc_budget: "N/A — composite orchestration"
---

# /enforce-skill-first-execution

Run all 13 atomic skill-first governance checks in sequence and produce a unified
execution report. Enforces skill-first policy compliance across the repository.

## Purpose

Orchestrate the complete skill-first governance audit. Identifies ad-hoc scripts,
broken skill contracts, drift between registries, duplicate skills, ungoverned mutations,
and unbound taskcard skills. Produces a single execution report summarizing all findings.

## Composition Order

Steps 1-3 are read-only (non-blocking on failure). Steps 4-5 mutate registries (abort on YAML failure).
Steps 6-13 are read-only (non-blocking on failure).

```
1.  inventory-commands            → .supervisor/command-inventory.yaml
2.  detect-ad-hoc-execution       → .supervisor/ad-hoc-execution-inventory.yaml
3.  validate-skill-contracts      → .supervisor/skill-contract-validation-results.yaml
4.  normalize-skill-registry      → .supervisor/skill-registry.yaml (backup first)
5.  sync-skill-command-registry   → .claude/commands/command-registry.yaml (backup first)
6.  build-capability-routes       → .supervisor/capability-routing-results.yaml
7.  detect-duplicate-skills       → .supervisor/duplicate-skill-report.yaml
8.  backfill-task-skill-ownership → .supervisor/taskcard-skill-backfill.yaml
9.  validate-mutation-guard       → .supervisor/mutation-guard-results.yaml
10. run-skill-idempotency         → .supervisor/skill-idempotency-proof.yaml
11. collect-skill-execution-receipts → .supervisor/skill-execution-receipt-index.yaml
12. scan-residual-bypasses        → .supervisor/residual-bypass-report.yaml
13. inventory-skills              → .supervisor/skill-inventory.yaml
```

## Steps

1. **Read run_id** from `.local/supervisor/skill-first-run-id.json`

2. **Steps 1-3 (read-only):**
   - Run `/inventory-commands`: if fails, log error and continue
   - Run `/detect-ad-hoc-execution`: if fails, log error and continue
   - Run `/validate-skill-contracts`: if fails, log error and continue

3. **Step 4 (registry mutation with backup):**
   - Run `/normalize-skill-registry`
   - If YAML parse fails: ABORT the entire orchestration (do not proceed to step 5)
   - Success: continue to step 5

4. **Step 5 (registry mutation with backup):**
   - Run `/sync-skill-command-registry`
   - If command-registry.yaml is malformed: ABORT (do not proceed to step 6)
   - If sync detects BROKEN_POINTER or ORPHAN entries: log them and CONTINUE (non-blocking)
   - Success: continue to step 6

5. **Steps 6-12 (read-only):**
   - Run each skill; if any fails, log error and continue to next step

6. **Step 13 (read-only, conditional):**
   - If `inventory-skills` is registered in skill-registry.yaml: run `/inventory-skills`
   - If not yet registered (Pilot C not yet run): SKIP with log message

7. **Aggregate and report:**
   - Collect all output YAML files
   - Write `.supervisor/skill-first-execution-report.md` with one-section summary per step

## Failure Handling

| Step | On Failure |
|------|-----------|
| 1-3 | Log error and CONTINUE |
| 4 (normalize-skill-registry) | ABORT entire orchestration; restore from backup |
| 5 (sync-skill-command-registry) | ABORT if YAML malformed; CONTINUE if only flags |
| 6-12 | Log error and CONTINUE |
| 13 | Skip if skill not registered |

## Output

`.supervisor/skill-first-execution-report.md` — unified report with one section per step:
- Step name, output file, key findings count, verdict

## Allowed Paths

- All `.supervisor/*.yaml` output files (write)
- `.claude/commands/command-registry.yaml` (write via sync — backup first)
- `.supervisor/skill-registry.yaml` (write via normalize — backup first)
- `.local/archive/` (write backups)

## Forbidden Paths

- `src/**`
- `AGENTS.md`, `CLAUDE.md`
- `registry/format-registry.yaml`

## Constraints

- Steps 4 and 5 must backup before any modification
- Never deletes registry entries
- Steps 1-3 and 6-13 are non-blocking — errors logged, not fatal

## Idempotency Contract

Safe to rerun. Each step is idempotent. Steps 4-5 produce identical output on unchanged inputs.
Step 5 second pass reports `auto_repaired: 0` (Gate V11 proof).

## Usage

```
/enforce-skill-first-execution
```
