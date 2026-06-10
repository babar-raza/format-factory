# Evidence Bundle Contract
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## Bundle Location

Primary reports directory: `reports/spec-authority-plan-repair/spec-authority-plan-repair-20260607-e382e5f/`
Local bundle copy: `.local/spec-authority-plan-repair/spec-authority-plan-repair-20260607-e382e5f/`

---

## Required Files (22 items)

1. `repaired-plan.md` — full repaired healing plan with all 10 repairs applied
2. `repaired-plan.json` — machine-readable plan with metadata, repairs_applied, verdicts
3. `plan-readiness-review.md` — 15-category plan readiness review
4. `evidence-import-review.md` — GAP-001..010 re-verified against HEAD e382e5f
5. `required-plan-repairs.md` — 10+ mandatory repairs with actions and validation
6. `lane-ownership-map.md` — 9-lane model narrative
7. `lane-ownership-map.json` — 9-lane model machine-readable
8. `authority-healing-state-machine.md` — 32-state machine narrative
9. `authority-healing-state-machine.json` — 32-state machine machine-readable
10. `taskcard-schema.md` — taskcard field definitions narrative
11. `taskcard-schema.json` — taskcard schema machine-readable
12. `authority-healing-taskcards.md` — 25 taskcards narrative
13. `authority-healing-taskcards.json` — 25 taskcards machine-readable
14. `taskcard-state.json` — initial state of all 25 taskcards
15. `taskcard-transition-ledger.jsonl` — transition log for this sprint
16. `rollback-recovery-plan.md` — 12 failure modes narrative
17. `rollback-recovery-plan.json` — 12 failure modes machine-readable
18. `verification-gates.md` — 20 verification gates narrative
19. `verification-gates.json` — 20 verification gates machine-readable
20. `plan-completeness-check.md` — 20-item completeness check
21. `adversarial-review.md` — independent review, 10 questions
22. `validate_repaired_plan.py` — validator script
23. `raw-logs/` (all command outputs: preflight.txt, repo-state.txt, validate-repaired-plan.txt)
24. `final-summary.md` — final sprint summary with verdict
25. `single-go-execution-prompt.md` — execution prompt (only if validator exits 0 and no CRITICAL adversarial issues)
26. `SHA256-MANIFEST.txt` — SHA-256 of all files in .local/ bundle

---

## Self-Containedness

A reviewer with this bundle can:
- Understand the full plan-repair sprint intent and findings
- Run validate_repaired_plan.py to verify artifact integrity
- Read the single-go-execution-prompt.md to understand what the next sprint should do

The bundle requires ${REPO_ROOT} to be present for path resolution. This is an inherent constraint for repo-local bundles.

---

## Copy Command

```bash
cp -r "${REPO_ROOT}/reports/spec-authority-plan-repair/${RUN_ID}/" \
       "${REPO_ROOT}/.local/spec-authority-plan-repair/${RUN_ID}/"
```

---

## SHA256 Manifest

```bash
find "${REPO_ROOT}/.local/spec-authority-plan-repair/${RUN_ID}/" -type f | sort | \
  xargs sha256sum > "${REPO_ROOT}/.local/spec-authority-plan-repair/${RUN_ID}/SHA256-MANIFEST.txt"
```

Report the SHA-256 of SHA256-MANIFEST.txt itself as the bundle fingerprint.
