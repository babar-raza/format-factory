# Next Agent Execution Prompt — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52
# This file is the exact next prompt to execute after this audit

---

## NEXT SPRINT: FODS Test Cleanup + Commit Authorization + Gate 11 Preparation

**Sprint type:** Product (FOSS Python + .NET Commercial)
**Authority:** This audit verdict — READY_AFTER_TARGETED_MACHINERY_REPAIRS

---

## Step 0: P0 — Fix 32 FODS Python Test Collection Errors

Execute TC-FODS-TEST-FIX-001:

```bash
# Confirm what functions are missing
.venv/Scripts/pytest tests/python/fods/ -q --tb=no --co 2>&1 | grep "ERROR"

# Delete stranded analytics test files (same pattern as SYLK cleanup in 2026-06-18)
# Files to delete: test_r273, r274, r284 (both), r286, r289, r290f, r290l,
#                  r299, r300, r305, r307, r314, r319, r337, r355, r373, r374
#
# Use: git rm tests/python/fods/test_r273_fods_sprint70_gaps.py ... etc.
# OR: Delete files and add to known-failure-ledger.yaml

# Verify after deletion:
.venv/Scripts/pytest tests/python/fods/ -q --tb=no
# Expected: 44+ passed, 0 errors
```

---

## Step 1: P0 — Request User Authorization for Git Commit

This is a TRUE_EXTERNAL_GATE for git commit. Report to user:

"The following files have uncommitted changes that should be committed:
- registry/source-structure-baseline.json
- src/python/fods/neutral_model.py
- src/python/fods/Compat/ (new untracked directory)
- tests/specification-authority-layer/test_qname_structure_validator.py
- tests/supervisor/test_governance_validators.py
- tools/supervisor/governance_validator_runner.py
- tools/supervisor/governance_validators.py

Please authorize: git commit -m 'fix(fods): add Compat facades, fix qname stubs, update governance validators'"

---

## Step 2: Gate 11 Preparation for FODS

After P0 resolves:

```bash
# Run gate check
# /check-gate fods 11

# Or equivalent:
.venv/Scripts/python -c "
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve()))
# Check FODS against Gate 11 criteria
"
```

Read: reports/supervisor/fods-gate11-readiness.md
Follow: /build-evidence-bundle pattern for FODS Gate 11 packet
Submit packet for Babar Raza review → STOP (TRUE_EXTERNAL_GATE)

---

## Step 3: Gate 11 Preparation for FODT

Same as Step 2 for FODT:
- Create FODT Compat/ facades (mirror FODS Compat/)
- Read: reports/supervisor/fodt-gate11-readiness.md
- Follow: /build-evidence-bundle pattern
- Submit for Babar Raza review → STOP

---

## Step 4: Sprint Closeout

Write evidence declaration and run supervisor:
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Machinery Lane (SEPARATE — do not mix with product sprint)

After product sprint closes, in a SEPARATE machinery sprint:

1. TC-SAL-VERIFY-001: Segregate auto-seeded SAL facts
2. TC-CAPABILITY-COMPILER-001: Wire compiler to workbench path
3. TC-SKILL-QNAME-001: Add QName requirement to product skill prompts
4. TC-BACKFILL-001: Create FODS backfill inventory tool

---

## Non-Negotiable Rules for Next Sprint

1. Fix test errors BEFORE running gate check
2. Do NOT run backfill migration and product deepening in same sprint
3. Do NOT claim Gate 11 readiness from test count alone — P1-P11 formal criteria required
4. Do NOT start new analytics functions (rotation suspended, V42 blocks)
5. All new spec/ classes MUST have spec_qname attribute
6. git commit requires explicit user authorization
7. Gate 11 EXECUTION requires Babar Raza — do not self-approve

---

## What to Report to User at End of Sprint

1. Number of FODS test errors remaining (target: 0)
2. Whether git commit was made (requires user auth)
3. FODS Gate 11 packet status (prepared/submitted)
4. FODT Gate 11 packet status (prepared/submitted)
5. Link to evidence bundle
6. Exact next prompt path
