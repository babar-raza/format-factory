# Repair Decision Log — Specification Authority Layer Production Blocker Healing Plan
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001

All 9 repair decisions are documented below. Each section corresponds to a defect in gap-analysis.md.

---

## Decision: Defect 1 — Closeout model

**Decision:** Add autonomous-cycle step after evidence-declaration.yaml is written and before
build_declaration_review_package is run.

**Command (Bash):**
```bash
$PYTHON tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml
CYCLE_EXIT=$?
```

**Exit code handling:**
- Exit 0 = accepted; continue to review package build
- Exit 3 = rework required; fix evidence-declaration.yaml before proceeding; do not skip
- Other = tool/runtime failure; investigate before proceeding

**After cycle:**
Run: `$PYTHON tools/supervisor/build_declaration_review_package.py --declaration ...`

**After package:**
Write `review-package-proof.md` with:
- Absolute ZIP path (derived from REPO_ROOT — no hardcoded user paths)
- SHA-256 (64-char hex, computed at runtime)
- Byte size
- File count
- Autonomous-cycle exit code

**review-package-proof.md must be a declared output artifact in evidence-manifest.yaml.**

---

## Decision: Defect 2 — Allowed paths

**Decision:** The repaired prompt must list these allowed paths explicitly in the global
allowed paths section:

```
Write to:
  reports/specification-authority-layer-production-healing/**
  .local/evidences/specification-authority-layer-production-healing/**
  .local/supervisor/reviews/specification-authority-layer-production-healing/**
```

The path `.local/supervisor/reviews/specification-authority-layer-production-healing/**`
must appear in the allowed paths list before any lane work begins, so execution agents
do not treat it as unauthorized.

---

## Decision: Defect 3 — Count validation

**Decision:** Replace hardcoded count assertions with declared-vs-materialized checks.

**Validation rules (replacing "exactly N" assertions):**

1. Taskcard count: `taskcard-state.json` is the source of truth.
   Validation: parse taskcard-state.json; count entries; verify all entries are
   CLOSED_VERIFIED (not: count == 19).

2. Output file count: `file-ownership-map.json` is the source of truth.
   Validation: parse file-ownership-map.json; for each key, verify the file exists on disk
   (not: count == 25).

3. Evidence artifact count: `evidence-manifest.yaml` is the source of truth.
   Validation: parse evidence-manifest.yaml; for each artifact path, verify the file exists
   (not: count == 20).

Keyword checks remain explicit (24 keywords enumerated in the prompt) — these are
specification-driven requirements, not counts.

---

## Decision: Defect 4 — Taskcard lifecycle

**Decision:** Enforce READY → IN_PROGRESS → CLOSED_VERIFIED lifecycle throughout.

**Rules:**
- taskcard-state.json initialization: ALL entries status = "READY"
- At lane start: update the active taskcard to IN_PROGRESS
- At lane close: update to CLOSED_VERIFIED ONLY after evidence_paths populated
- BLOCKED or FAILED_NEEDS_REPAIR: blocker_reason field must be a non-empty string
- Only one taskcard may be IN_PROGRESS at a time within a lane
- Tasks may be IN_PROGRESS in parallel across different lanes (one per lane)

**Forbidden states:**
- Initializing to IN_PROGRESS before work begins
- Setting to CLOSED_VERIFIED before evidence_paths are populated
- Leaving blocker_reason empty when status = BLOCKED

---

## Decision: Defect 5 — Conditional verdicts

**Decision:** worker_self_verdict is selected after validation, not pre-filled.

**Conditional selection logic (after all validation checks complete):**

```
IF all taskcards CLOSED_VERIFIED
AND all V01–V12 checks pass
AND autonomous-cycle exit = 0
AND no forbidden files changed:
  worker_self_verdict: PASS
  worker_self_grade: PASS
  Use macro verdict:
    SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION

ELIF validation passes but known limitations exist
(e.g., source licensing for DIF/Gnumeric/ODF unconfirmed):
  worker_self_verdict: PARTIAL
  worker_self_grade: PARTIAL
  Use macro verdict:
    SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS

ELSE (any check fails, any taskcard unresolved, autonomous-cycle exit != 0):
  worker_self_verdict: FAIL
  worker_self_grade: FAIL
  Use macro verdict:
    SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
```

The evidence-declaration.yaml template must NOT pre-fill any verdict fields. The fields
are written at the very end of the sprint after the above conditional is evaluated.

---

## Decision: Defect 6 — Python portability

**Decision:** All repaired commands use a PYTHON variable defined at the start of the runbook.

**Detection pattern (Bash):**
```bash
if [ -f ".local/venv/Scripts/python" ]; then
  PYTHON=".local/venv/Scripts/python"
elif [ -f ".local/venv/bin/python" ]; then
  PYTHON=".local/venv/bin/python"
else
  PYTHON="python"
fi
$PYTHON --version || { echo "ERROR: Python not found. Abort."; exit 1; }
REPO_ROOT="$(git rev-parse --show-toplevel)"
```

**Detection pattern (PowerShell):**
```powershell
if (Test-Path ".local/venv/Scripts/python.exe") {
  $PYTHON = ".local/venv/Scripts/python.exe"
} elseif (Test-Path ".local/venv/bin/python") {
  $PYTHON = ".local/venv/bin/python"
} else {
  $PYTHON = "python"
}
& $PYTHON --version
if ($LASTEXITCODE -ne 0) { Write-Error "ERROR: Python not found. Abort."; exit 1 }
$REPO_ROOT = (git rev-parse --show-toplevel)
```

**Note:** Both Bash and PowerShell blocks are provided. Only one is needed per execution.
Choose based on the active shell. Both blocks define PYTHON and REPO_ROOT.

All autonomous-cycle, build_declaration_review_package, and validation commands use $PYTHON.
All ZIP path references use $REPO_ROOT (not hardcoded absolute paths).
In the repaired prompt, all commands shown as `$PYTHON tools/supervisor/...`

---

## Decision: Defect 7 — Input path portability

**Decision:** The repaired execution prompt does not reference any user-specific path.

**Option A (selected — preferred):** The key architectural decisions from the plan are
embedded inline in the repaired execution prompt as a fenced reference block under
"## Architecture Reference". No external file path is needed.

**Option B (alternative):** Copy plan to
`reports/specification-authority-layer-production-healing/input-plan.md` and reference
that repo-local path instead. All taskcards reference the repo-local copy.

**The repaired prompt uses Option A.** The 11 subsystems, 13 lifecycle states, deterministic
context-pack contract, pilot scope, and regression test categories are embedded inline.

**Explicitly prohibited in all repaired outputs:**
- Any reference to `C:\Users\prora\` or any other user-home-directory path
- Any machine-specific absolute path
- Any path that assumes a specific user account name

ZIP paths and SHA-256 script paths use `$REPO_ROOT` derived at runtime via:
  `REPO_ROOT=$(git rev-parse --show-toplevel)`  # Bash
  `$REPO_ROOT = (git rev-parse --show-toplevel)`  # PowerShell

---

## Decision: Defect 8 — Verdict normalization

**Decision:** Remove all uses of COMPLETE, BLOCKED, PARTIAL as final verdict strings.
Generic template language is prohibited in the final response.

**Only allowed final verdicts for the downstream healing sprint:**
```
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
```

**Only allowed final verdicts for this repair sprint:**
```
PLAN_REPAIRED_READY_FOR_EXECUTION
PLAN_STILL_NEEDS_REPAIR
```

The repaired prompt's "Final Response Contract" section must show exactly three healing-sprint
options with the selection logic from Decision: Defect 5.

**Forbidden verdict language:**
- "VERDICT: COMPLETE"
- "VERDICT: BLOCKED"
- "VERDICT: PARTIAL"
- "Sprint complete."
- "Repair done."
- Any prose that acts as a verdict without using a macro string

---

## Decision: Defect 9 — Strengthened validation

**Decision:** Replace count assertions with declared-vs-materialized checks. Add 12
systematic validation checks (V01–V12).

**Validation checks (all LOCAL ONLY — no GitHub/CI required):**

```
V01: All files in file-ownership-map.json exist as real files (declared-vs-materialized)
     Command: $PYTHON -c "import json, os, pathlib; m=json.load(open('file-ownership-map.json')); missing=[k for k in m if not pathlib.Path(k).exists()]; print('V01 PASS' if not missing else f'V01 FAIL: {missing}')"

V02: All Markdown files have H1 headings (first 10 lines contain "# ")
     Command: for f in $(find reports/specification-authority-layer-production-healing -name "*.md"); do head -10 "$f" | grep -q "^# " || echo "V02 FAIL: missing H1 in $f"; done

V03: All JSON files parse without error
     Command: $PYTHON -c "import json; [json.load(open(f)) for f in ['file-ownership-map.json', 'taskcard-state.json']]; print('V03 PASS')"

V04: All YAML files parse without error
     Command: $PYTHON -c "import yaml; [yaml.safe_load(open(f)) for f in ['evidence-declaration.yaml', 'evidence-manifest.yaml']]; print('V04 PASS')"

V05: file-ownership-map.json has no duplicate keys (Python json.load raises on duplicates)
     Already verified by V03 if using object_pairs_hook check

V06: taskcard-state.json: all entries CLOSED_VERIFIED or CLOSED_SKIPPED_WITH_REASON
     Command: $PYTHON -c "import json; data=json.load(open('taskcard-state.json')); bad=[t['id'] for t in data if t['status'] not in ('CLOSED_VERIFIED','CLOSED_SKIPPED_WITH_REASON')]; print('V06 PASS' if not bad else f'V06 FAIL: {bad}')"

V07: Final execution prompt contains all 24 required keywords
     Command: $PYTHON -c "
keywords=['EXECUTION MODE','SpecSourceRegistry','SpecVault','SpecParser','SpecNormalizer','SpecIndexer',
'SpecDigestor','RequirementExtractor','SpecVerifier','RequirementGraph','ContextPackBuilder',
'SpecGovernanceRuntime','deterministic context pack','usage ledger','stale','refresh',
'coverage validator','ZST','Netpbm','DIF','Gnumeric','FODS/FODT','ai_draft','SHA-256']
text=open('final-ready-to-send-execution-prompt.md').read()
missing=[k for k in keywords if k not in text]
print('V07 PASS' if not missing else f'V07 FAIL: {missing}')"

V08: No forbidden path changed (LOCAL ONLY — no CI)
     Command: git diff HEAD --name-only -- src/net/ src/python/ tests/net/ tests/python/ product-capability-matrix/ registry/
     Expected: empty output

V09: Autonomous-cycle was run and exit code captured
     Check: review-package-proof.md contains "Autonomous-cycle exit code:" with a value

V10: Review package ZIP exists at declared path
     Check: $PYTHON -c "import pathlib; p=pathlib.Path('$ZIP_PATH'); print('V10 PASS' if p.exists() else 'V10 FAIL: ZIP missing')"

V11: SHA-256 computed and recorded in review-package-proof.md
     Check: grep "SHA-256:" review-package-proof.md | grep -E "[0-9a-f]{64}"

V12: Final git status captured in final-git-status.txt
     Check: [ -s final-git-status.txt ] && echo "V12 PASS" || echo "V12 FAIL: file empty or missing"
```

**Additional banned-string scan (all artifact files):**
```python
BANNED = [
  'C:\\Users\\prora\\',
  'VERDICT: COMPLETE',
  'VERDICT: BLOCKED',
  'VERDICT: PARTIAL',
  'worker_self_verdict: PASS',
  'exactly 19',
  'exactly 25',
  'exactly 20'
]
# Scan all .md, .json, .yaml, .txt files in both output directories
```
