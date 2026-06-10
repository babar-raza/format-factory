# Final Plan Hardening Diff
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-FINAL-HARDENING-001

---

## H-001 — Remove all hardcoded absolute paths

**Problem:** Execution commands reference ZIP path and SHA-256 computation using values that
could be instantiated with hardcoded `C:\Users\prora\` if an agent does not follow the
REPO_ROOT derivation pattern.

**Fix applied in final-ready-to-send-execution-prompt.md:**

REPO_ROOT detection is the FIRST mandatory step (before any lane work):

```bash
# Bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
ZIP_PATH="$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip"
```

```powershell
# PowerShell
$REPO_ROOT = (git rev-parse --show-toplevel)
$ZIP_PATH = "$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip"
```

SHA-256 computation uses shell variable, not hardcoded path:
```bash
$PYTHON -c "
import hashlib, os, zipfile
path = os.environ['ZIP_PATH']  # or pass as arg
with open(path,'rb') as f: data = f.read()
sha = hashlib.sha256(data).hexdigest()
size = len(data)
with zipfile.ZipFile(path) as z: count = len(z.namelist())
print(f'SHA-256: {sha}')
print(f'Bytes: {size}')
print(f'Files: {count}')
" ZIP_PATH="$ZIP_PATH"
```

review-package-proof.md path field:
```
ZIP absolute path: [computed from REPO_ROOT at runtime — no hardcoded user home directory]
```

Banned string check on ALL 22 output files:
```
Scan for literal: C:\Users\prora\
Expected: NONE found in any output file
```

---

## H-002 — Expand banned-string scan to all generated artifacts

**Problem:** The banned-string check only scanned the final execution prompt. Other artifacts
(gap-analysis.md, evidence YAML, etc.) could contain banned strings.

**Fix applied in final-ready-to-send-execution-prompt.md — V-check addition:**

Added as V-check "V-BAN" (runs after V12):
```python
# V-BAN: banned-string scan across ALL artifact files in both output directories
import pathlib
BANNED = [
  'C:\\Users\\prora\\',         # machine-specific absolute path
  'VERDICT: COMPLETE',           # generic template verdict
  'VERDICT: BLOCKED',            # generic template verdict
  'VERDICT: PARTIAL',            # generic template verdict
  'worker_self_verdict: PASS',   # pre-filled verdict
  'exactly 19',                  # brittle count assertion
  'exactly 25',                  # brittle count assertion
  'exactly 20'                   # brittle count assertion
]
DIRS = [
  'reports/specification-authority-layer-production-healing',
  '.local/evidences/specification-authority-layer-production-healing'
]
violations = []
for d in DIRS:
    for p in pathlib.Path(d).rglob('*'):
        if p.is_file():
            try:
                text = p.read_text(encoding='utf-8', errors='replace')
                for b in BANNED:
                    if b in text:
                        violations.append(f'{p}: contains [{b}]')
            except Exception: pass
if violations:
    print('V-BAN FAIL:')
    for v in violations: print(' ', v)
else:
    print('V-BAN PASS: BANNED_STRINGS_SCAN_PASS')
```

---

## H-003 — Clarify repair-sprint vs healing-sprint evidence root labels

**Problem:** The two evidence roots differ only by the `-plan-repair` suffix and can be confused.

**Fix applied in final-ready-to-send-execution-prompt.md:**

4 canonical labels defined at the top of Section 3 (Allowed Paths) and referenced at each
write point in the execution sequence:

```
HEALING_SPRINT_EVIDENCE_ROOT:
  .local/evidences/specification-authority-layer-production-healing/
  Purpose: Artifacts produced by THIS healing sprint
  Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001
  Status: THIS SPRINT — write here

HEALING_SPRINT_REVIEW_ROOT:
  .local/supervisor/reviews/specification-authority-layer-production-healing/
  Purpose: Review package ZIP for this healing sprint
  Status: THIS SPRINT — ZIP goes here

REPAIR_SPRINT_EVIDENCE_ROOT:
  .local/evidences/specification-authority-layer-production-healing-plan-repair/
  Purpose: Artifacts from the REPAIR sprint (already complete)
  Status: DO NOT WRITE — other sprint, already closed

REPAIR_SPRINT_REVIEW_ROOT:
  .local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/
  Purpose: Review package from the repair sprint (already complete)
  Status: DO NOT WRITE — other sprint, already closed
```

Hard error rule: Writing to REPAIR_SPRINT_EVIDENCE_ROOT or REPAIR_SPRINT_REVIEW_ROOT during
this healing sprint → STOP immediately; this is an out-of-bounds write.

---

## H-004 — Mandatory preflight governance reads

**Problem:** The repaired prompt had no governance reads step. CLAUDE.md requires reading
session-resume.md and approval-gates.md before sprint work begins.

**Fix applied in final-ready-to-send-execution-prompt.md — Step 0b (before lane work):**

Read in order (record PRESENT or MISSING; MISSING = caveat, not failure):
```bash
for f in CLAUDE.md AGENTS.md docs/governance/ai-authority-boundary.md \
          plans/master-plan.md reports/supervisor/session-resume.md \
          reports/supervisor/approval-gates.md .supervisor/policies.yaml \
          ".supervisor/schemas/evidence-declaration.schema.json" \
          tools/supervisor/autonomous_cycle.py \
          tools/supervisor/build_declaration_review_package.py; do
  [ -f "$f" ] && echo "PRESENT: $f" || echo "MISSING (caveat): $f"
done
```

AUTONOMOUS_CONTINUE gate:
```bash
# Check if AUTONOMOUS_CONTINUE: NO blocks this sprint
if grep -q "AUTONOMOUS_CONTINUE: NO" reports/supervisor/approval-gates.md 2>/dev/null; then
  echo "BLOCKED: AUTONOMOUS_CONTINUE: NO — address contradictions before proceeding"
  echo "See: reports/supervisor/contradictions.md"
  exit 1
fi
echo "AUTONOMOUS_CONTINUE: OK — proceeding with sprint"
```

Note: MISSING approval-gates.md → treat as AUTONOMOUS_CONTINUE: YES (caveat, not failure).

---

## H-005 — Python setup: Bash and PowerShell blocks

**Problem:** Phase 1 repair only addressed Python detection generically. The final prompt
needs both Bash and PowerShell blocks with explicit REPO_ROOT derivation.

**Fix applied in final-ready-to-send-execution-prompt.md — Step 0a:**

```bash
# === Bash ===
if [ -f ".local/venv/Scripts/python" ]; then
  PYTHON=".local/venv/Scripts/python"
elif [ -f ".local/venv/bin/python" ]; then
  PYTHON=".local/venv/bin/python"
else
  PYTHON="python"
fi
$PYTHON --version || { echo "ERROR: Python not found. Abort."; exit 1; }
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "REPO_ROOT=$REPO_ROOT"
ZIP_PATH="$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip"
DECL_PATH="$REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml"
```

```powershell
# === PowerShell ===
if (Test-Path ".local/venv/Scripts/python.exe") { $PYTHON = ".local/venv/Scripts/python.exe" }
elseif (Test-Path ".local/venv/bin/python") { $PYTHON = ".local/venv/bin/python" }
else { $PYTHON = "python" }
& $PYTHON --version
if ($LASTEXITCODE -ne 0) { Write-Error "ERROR: Python not found. Abort."; exit 1 }
$REPO_ROOT = (git rev-parse --show-toplevel)
Write-Host "REPO_ROOT=$REPO_ROOT"
$ZIP_PATH = "$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip"
$DECL_PATH = "$REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml"
```

Note: Choose one block based on active shell. Both define PYTHON, REPO_ROOT, ZIP_PATH, DECL_PATH.
All subsequent commands use $PYTHON, $REPO_ROOT, $ZIP_PATH, $DECL_PATH.

---

## H-006 — TC-REPAIR-013b closure ordering: 6-item gate

**Problem:** The evidence closeout taskcard lacked explicit actionable gate checks before
setting status = CLOSED_VERIFIED.

**Fix applied in final-ready-to-send-execution-prompt.md — before setting CLOSED_VERIFIED:**

```bash
# GATE CHECK — all 6 items must pass before CLOSED_VERIFIED
echo "=== Gate Check: TC-REPAIR-013b closure gate ==="

# Gate 1: evidence-declaration.yaml exists and parses
$PYTHON -c "import yaml; yaml.safe_load(open('$DECL_PATH'))" && echo "Gate 1 PASS" || echo "Gate 1 FAIL"

# Gate 2: evidence-manifest.yaml exists and parses
$PYTHON -c "import yaml; yaml.safe_load(open('$REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-manifest.yaml'))" && echo "Gate 2 PASS" || echo "Gate 2 FAIL"

# Gate 3: autonomous-cycle exit code captured and equals 0
echo "Gate 3: CYCLE_EXIT=$CYCLE_EXIT"
[ "$CYCLE_EXIT" = "0" ] && echo "Gate 3 PASS" || echo "Gate 3 FAIL: cycle exit was $CYCLE_EXIT"

# Gate 4: ZIP exists
[ -f "$ZIP_PATH" ] && echo "Gate 4 PASS" || echo "Gate 4 FAIL: ZIP missing at $ZIP_PATH"

# Gate 5: SHA-256 is 64-char hex (set in previous step)
echo "$SHA256" | grep -qE "^[0-9a-f]{64}$" && echo "Gate 5 PASS" || echo "Gate 5 FAIL: SHA256 invalid"

# Gate 6: review-package-proof.md written with all fields
grep -q "SHA-256:" reports/specification-authority-layer-production-healing/review-package-proof.md && \
grep -q "Autonomous-cycle exit code:" reports/specification-authority-layer-production-healing/review-package-proof.md && \
echo "Gate 6 PASS" || echo "Gate 6 FAIL: review-package-proof.md incomplete"

echo "=== If any FAIL above: status = BLOCKED; fix and re-run gate check ==="
echo "=== If all PASS: update taskcard status to CLOSED_VERIFIED ==="
```

---

## H-007 — Fallback ZIP contents

**Problem:** The fallback ZIP creation instruction was underspecified.

**Fix applied in final-ready-to-send-execution-prompt.md — fallback ZIP section:**

If build_declaration_review_package.py is unavailable, create fallback ZIP containing
exactly these files (relative to REPO_ROOT):

From reports/specification-authority-layer-production-healing/:
- lane-ownership.md
- file-ownership-map.json
- overlap-check.md
- taskcard-state.json
- coordinator-integration-log.md
- 00-preflight.md (if exists)
- 00-review.md (the healing plan's review, if different from repair sprint review)
- all tool implementation files
- all pilot deliverable output files
- validation-results.md
- final-git-status.txt
- review-package-proof.md (placeholder if SHA not yet computed — write after ZIP)

From .local/evidences/specification-authority-layer-production-healing/:
- evidence-declaration.yaml
- evidence-manifest.yaml

Additional file (fallback only — created at ZIP root):
- fallback-package-manifest.json

fallback-package-manifest.json format:
```json
{
  "sprint_id": "FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001",
  "fallback": true,
  "builder": "manual-zip",
  "files": [
    {"path": "relative/path/to/file.md", "size_bytes": 1234, "sha256": "..."}
  ]
}
```

Note in review-package-proof.md: "Built via fallback ZIP (build_declaration_review_package.py unavailable)"

---

## H-008 — Local-only validation scope

**Problem:** V08 did not explicitly state that no CI/CD run is required.

**Fix applied in final-ready-to-send-execution-prompt.md — before V-check list:**

```
VALIDATION SCOPE: LOCAL ONLY

Explicit exclusions:
  - No GitHub Actions run required or expected
  - No CI pipeline check required
  - No remote push required to validate
  - No external service calls required
  - No network access required for any V01–V12 check

All validation checks run against local working tree only.
```

V08 clarified:
```bash
# V08 — No forbidden path changed (LOCAL ONLY — compares working tree to HEAD, no network)
git diff HEAD --name-only -- src/net/ src/python/ tests/net/ tests/python/ \
  product-capability-matrix/ registry/
# Expected output: empty
# If non-empty: list each file; sprint cannot close until diff is clean
```

Optional (if available):
```bash
# Run local evidence validator if present
if [ -f "tools/supervisor/validate_evidence_for_supervisor.py" ]; then
  $PYTHON tools/supervisor/validate_evidence_for_supervisor.py \
    --declaration "$DECL_PATH"
else
  echo "validate_evidence_for_supervisor.py not found — caveat, not failure"
fi
```

---

## H-009 — Strengthen final verdict rules

**Problem:** Generic prose acting as a verdict was not explicitly banned.

**Fix applied in final-ready-to-send-execution-prompt.md — Section 12 (Final Response Contract):**

Use exactly one macro verdict:
```
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
```

Selection logic:
```
IF all taskcards CLOSED_VERIFIED
AND BANNED_STRINGS_SCAN_PASS
AND all V01–V12 + V-BAN checks pass
AND autonomous-cycle exit = 0
AND all 6 closure gate items confirmed:
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION

ELIF any check fails OR any taskcard not CLOSED_VERIFIED:
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
    blocker_reason: [list each failing check]

ELIF all pass but known limitations:
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
```

Explicitly PROHIBITED in the final response:
- "VERDICT: COMPLETE" / "VERDICT: BLOCKED" / "VERDICT: PARTIAL"
- "Sprint complete." / "All done." / "Repair done." / "Done." (as verdict)
- Any response that does not contain one of the three macro strings above
- Any response that contains more than one macro string
- "worker_self_verdict: PASS" pre-filled before validation

Required final response fields (5 mandatory):
1. Exact macro verdict (one of the three above)
2. Review package absolute path (REPO_ROOT-derived, 64-char SHA-256)
3. Autonomous-cycle exit code (integer)
4. List of all output files with PRESENT/MISSING status
5. Explicit statement: "No product source files modified. No commit. No push."
