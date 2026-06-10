# EXECUTION MODE — SPECIFICATION AUTHORITY LAYER PRODUCTION BLOCKER HEALING
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001
Role: Single-go execution agent. Read this entire prompt before taking any action.
Mode: PLAN EXECUTION — Build the Specification Authority Layer as described below.
Authority: This is the definitive ready-to-send execution prompt. All 9 Phase 1 defects and
           all 10 Phase 2 hardening issues have been addressed.

---

## Section 1 — Role and Sprint Identity

You are executing sprint:
  FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

This sprint builds the Specification Authority Layer for the Format Factory project — a
production-grade system that makes file-format specifications available to agents and LLMs
in a reliable, traceable, verifiable way. The layer addresses 10 production blockers in the
current architecture.

You are NOT re-planning. You are NOT reinterpreting. You execute this prompt as specified.
If you encounter a hard stop (blocker, forbidden action, gate approval required), stop
immediately and report it. Do not attempt workarounds.

---

## Section 2 — Hard Prohibitions (always enforced, no exceptions)

- Do NOT edit src/net/**, src/python/**, tests/net/**, tests/python/**
- Do NOT edit product-capability-matrix/poc-targets.yaml
- Do NOT edit registry/format-registry.yaml
- Do NOT git commit, git push, git reset --hard, git clean, git stash
- Do NOT approve Gate 8 or Gate 11
- Do NOT mark commercial_product_ready=true
- Do NOT publish to any package registry
- Do NOT call external LLM APIs or store secrets
- Do NOT write to REPAIR_SPRINT_EVIDENCE_ROOT (see Section 5)
- Do NOT write to REPAIR_SPRINT_REVIEW_ROOT (see Section 5)
- Do NOT write to any path not in Section 3

---

## Section 3 — Allowed Paths

```
Write to:
  reports/specification-authority-layer-production-healing/**
  .local/evidences/specification-authority-layer-production-healing/**
  .local/supervisor/reviews/specification-authority-layer-production-healing/**

Read only:
  reports/specification-authority-layer-production-healing-plan-repair/**
  docs/governance/**
  docs/prompt-templates/**
  tools/supervisor/**
  .supervisor/schemas/**
  .supervisor/prompts/**
  plans/master-plan.md
  state/current-state.md
  CLAUDE.md
  AGENTS.md
```

---

## Section 4 — Preflight (Step 0 — do before any lane work)

### Step 0a — PYTHON and REPO_ROOT setup (H-005 fix)

Choose ONE block based on active shell. Both define PYTHON, REPO_ROOT, ZIP_PATH, DECL_PATH.

**Bash:**
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
echo "REPO_ROOT=$REPO_ROOT"
ZIP_PATH="$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing/declaration-review-package.zip"
DECL_PATH="$REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml"
```

**PowerShell:**
```powershell
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

### Step 0b — Governance reads (H-004 fix)

Read in order. Record PRESENT or MISSING for each. MISSING = caveat, not failure.

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

**AUTONOMOUS_CONTINUE gate:**
```bash
if grep -q "AUTONOMOUS_CONTINUE: NO" reports/supervisor/approval-gates.md 2>/dev/null; then
  echo "BLOCKED: AUTONOMOUS_CONTINUE: NO — address contradictions first"
  echo "See: reports/supervisor/contradictions.md"
  exit 1
fi
echo "AUTONOMOUS_CONTINUE: OK — proceeding"
```

If approval-gates.md is MISSING: treat as AUTONOMOUS_CONTINUE: YES (caveat).

### Step 0c — Git state capture

```bash
git status --short
git branch --show-current
git log --oneline -5
mkdir -p reports/specification-authority-layer-production-healing
mkdir -p .local/evidences/specification-authority-layer-production-healing
mkdir -p ".local/supervisor/reviews/specification-authority-layer-production-healing"
```

---

## Section 5 — Evidence Root Labels (H-003 fix)

Four canonical labels. Reference these at every write point in the execution sequence.

| Label | Path | This Sprint |
|-------|------|-------------|
| HEALING_SPRINT_EVIDENCE_ROOT | .local/evidences/specification-authority-layer-production-healing/ | WRITE HERE |
| HEALING_SPRINT_REVIEW_ROOT | .local/supervisor/reviews/specification-authority-layer-production-healing/ | ZIP GOES HERE |
| REPAIR_SPRINT_EVIDENCE_ROOT | .local/evidences/specification-authority-layer-production-healing-plan-repair/ | DO NOT WRITE — other sprint |
| REPAIR_SPRINT_REVIEW_ROOT | .local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/ | DO NOT WRITE — other sprint |

**Hard error:** Writing to REPAIR_SPRINT_EVIDENCE_ROOT or REPAIR_SPRINT_REVIEW_ROOT →
STOP immediately. This is an out-of-bounds write. Report: "OUT_OF_BOUNDS_WRITE detected."

---

## Section 6 — What You Are Building

### 10 Production Blockers Being Addressed

1. No deterministic context-pack contract — specs retrieved differently each run
2. No lifecycle model — no formal state machine for spec artifacts
3. No staleness chain — invalidation not propagated downstream
4. No regression controls — no test coverage for spec layer failures
5. No usage ledger production model — no append-only tracking of spec usage
6. No four-stream enforcement — spec handoffs not enforced at stream boundaries
7. Shallow execution prompt — original prompt lacked architectural depth
8. Taskcard count contradiction — 19 vs actual count mismatch
9. Pilot scope too broad — 5 formats at shallow depth vs 3 at production depth
10. Two missing subsystems — SpecNormalizer and SpecSourceRegistry absent

### 11 Subsystems (in pipeline order)

1. SpecSourceRegistry — authoritative registry of all approved specification sources
2. SpecVault — immutable raw snapshot store with SHA-256 content addressing
3. SpecParser — format-specific parser producing structured AST/JSON from raw spec
4. SpecNormalizer — cross-format normalization to canonical schema
5. SpecIndexer — lexical and semantic index over normalized artifacts
6. SpecDigestor — compressed digest generation for LLM context window management
7. RequirementExtractor — structured requirement extraction from normalized artifacts
8. SpecVerifier — requirement verification against spec source with provenance
9. RequirementGraph — dependency graph of requirements across specs
10. ContextPackBuilder — deterministic context pack assembly with manifest.sha256
11. SpecGovernanceRuntime — enforcement of ai-authority-boundary at all handoffs

### 13 Lifecycle States (A through M)

A. source_candidate — proposed source not yet registered
B. registered_source — source approved in SpecSourceRegistry
C. raw_snapshot — immutable snapshot in SpecVault (sha256 assigned)
D. parsed_artifact — SpecParser produced structured output
E. normalized_artifact — SpecNormalizer applied canonical schema
F. indexed_artifact — SpecIndexer completed indexing
G. digest_artifact — SpecDigestor produced compressed digest
H. candidate_requirement — RequirementExtractor produced unverified requirement
I. verified_requirement — SpecVerifier confirmed requirement with provenance
J. context_pack — ContextPackBuilder assembled deterministic pack with manifest.sha256
K. usage_record — ContextPack consumed; recorded in usage ledger
L. coverage_record — coverage validator evaluated requirement coverage
M. refresh_event — staleness check triggered re-ingestion

### Deterministic Context-Pack Contract

Same source sha256 + same request type + same index version → same manifest.sha256.
Staleness chain: if source sha256 changes → all downstream artifacts (states D through J)
are marked stale → SpecGovernanceRuntime triggers refresh → re-ingest from state B.
Anti-bypass rules:
  - No ad-hoc URL citations without registered source in SpecSourceRegistry
  - No memory-only spec claims (all claims backed by evidence)
  - No raw AI summary as authority (ai_draft label required; never promoted to verified)

### Usage Ledger

Append-only: `.local/spec-usage-ledger/usage-YYYYMMDD.jsonl`
Fields: timestamp, context_pack_id, consumer_stream, requirement_ids, source_sha256,
        manifest_sha256.
No deletion, no in-place update. Every ContextPack consumption adds one record.

### Four-Stream Enforcement

Mainstream Product handoffs: must provide context_pack_id + requirement_ids.
Acceleration Layer: same requirements for spec-dependent work.
Skills (Governed Execution): no ad-hoc URL citations; must use registered sources.
Supervisor: validates context_pack_id in evidence declarations.

### Regression Control Suite — 9 Categories (A through I)

A. Schema validation — spec artifacts match declared JSON schema
B. Provenance — all requirements trace to registered_source with sha256
C. Parser — round-trip: raw_snapshot → parsed → re-serialized matches original
D. Context pack — deterministic: same inputs → same manifest.sha256
E. Requirement verifier negatives — unverified requirements not promoted to verified
F. coverage validator — coverage_record correctly identifies uncovered requirements
G. Four-stream integration — handoff gates reject missing context_pack_id
H. Refresh/staleness — stale artifacts trigger refresh; clean do not
I. Anti-bypass — ad-hoc URL citations, memory-only claims, ai_draft bypasses blocked

### Pilot Scope

Minimum (3 formats — complete before extended):
  - ZST (Zstandard) — public spec, well-defined, no licensing risk
  - Netpbm — public domain spec, minimal complexity
  - DIF (Data Interchange Format) — public spec

Extended preparation (source registration + fetch-plan only):
  - Gnumeric — open-source; spec available via project docs
  - FODS/FODT — OASIS ODF public spec

---

## Section 7 — Taskcard Lifecycle Rules (H-006 fix)

- Initialize all taskcards as `"status": "READY"` in taskcard-state.json
- At lane start: update active taskcard to `IN_PROGRESS`
- At lane close: update to `CLOSED_VERIFIED` ONLY after evidence_paths populated
- BLOCKED / FAILED_NEEDS_REPAIR: `blocker_reason` must be non-empty string
- Only one taskcard IN_PROGRESS per lane at a time

**6-item gate — must all PASS before setting evidence closeout taskcard to CLOSED_VERIFIED:**

```bash
# Run ALL before setting CLOSED_VERIFIED:
# Gate 1: evidence-declaration.yaml parses
$PYTHON -c "import yaml; yaml.safe_load(open('$DECL_PATH'))" && echo "Gate 1 PASS" || echo "Gate 1 FAIL"

# Gate 2: evidence-manifest.yaml parses
$PYTHON -c "import yaml; yaml.safe_load(open('$REPO_ROOT/.local/evidences/specification-authority-layer-production-healing/evidence-manifest.yaml'))" && echo "Gate 2 PASS" || echo "Gate 2 FAIL"

# Gate 3: autonomous-cycle exit = 0
[ "$CYCLE_EXIT" = "0" ] && echo "Gate 3 PASS" || echo "Gate 3 FAIL: exit=$CYCLE_EXIT"

# Gate 4: ZIP exists
[ -f "$ZIP_PATH" ] && echo "Gate 4 PASS" || echo "Gate 4 FAIL"

# Gate 5: SHA-256 is 64-char hex
echo "$SHA256" | grep -qE "^[0-9a-f]{64}$" && echo "Gate 5 PASS" || echo "Gate 5 FAIL"

# Gate 6: review-package-proof.md has SHA-256 and exit code fields
grep -q "SHA-256:" reports/specification-authority-layer-production-healing/review-package-proof.md && \
grep -q "Autonomous-cycle exit code:" reports/specification-authority-layer-production-healing/review-package-proof.md && \
echo "Gate 6 PASS" || echo "Gate 6 FAIL"
```

If any gate FAIL: set taskcard status = BLOCKED, blocker_reason = which gate failed.
Fix and re-run gate check. Only after all 6 PASS: set status = CLOSED_VERIFIED.

---

## Section 8 — Execution Sequence (Steps 1–20)

All steps write to HEALING_SPRINT_EVIDENCE_ROOT or reports/specification-authority-layer-production-healing/.
Never write to REPAIR_SPRINT_EVIDENCE_ROOT.

**Step 1:** Create lane-ownership.md, file-ownership-map.json, overlap-check.md, taskcard-state.json (all READY), coordinator-integration-log.md.
  → Write to: reports/specification-authority-layer-production-healing/

**Step 2:** Create 00-review.md — review the architectural plan for completeness and safety.
  → Write to: reports/specification-authority-layer-production-healing/

**Step 3–11:** Lane B — build all 11 subsystem tool implementations:
  SpecSourceRegistry, SpecVault, SpecParser, SpecNormalizer, SpecIndexer, SpecDigestor,
  RequirementExtractor, SpecVerifier, RequirementGraph, ContextPackBuilder, SpecGovernanceRuntime.
  → Write to: reports/specification-authority-layer-production-healing/ (implementation plans)
  → Write to: src/specification-authority-layer/ (tool code)

**Step 12–14:** Minimum pilot deliverables for ZST, Netpbm, DIF (all 13 items from Section 10).
  → Write to: reports/specification-authority-layer-production-healing/

**Step 15:** Extended prep for Gnumeric and FODS/FODT (source registration + fetch-plan).
  → Write to: reports/specification-authority-layer-production-healing/

**Step 16:** Run regression control suite (9 categories A–I, 42+ tests).
  → Test files: tests/specification-authority-layer/

**Step 17:** Capture final git status.
  ```bash
  git status --short > reports/specification-authority-layer-production-healing/final-git-status.txt
  git log --oneline -5 >> reports/specification-authority-layer-production-healing/final-git-status.txt
  ```

**Step 18:** Run V01–V12 + V-BAN validation checks (Section 9 — LOCAL ONLY, H-008 fix).

**Step 19 — Evidence closeout (Fix #1, Fix #5, Fix #9):**
  a. Select conditional verdict (Fix #5 — do NOT pre-fill):
     IF all taskcards CLOSED_VERIFIED AND V-checks pass AND gate items met:
       worker_self_verdict: PASS
       macro_verdict: SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
     ELIF limitations exist:
       worker_self_verdict: PARTIAL
       macro_verdict: SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
     ELSE:
       worker_self_verdict: FAIL
       macro_verdict: SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED

  b. Write evidence-declaration.yaml to HEALING_SPRINT_EVIDENCE_ROOT (not repair root).
  c. Write evidence-manifest.yaml to HEALING_SPRINT_EVIDENCE_ROOT.
  d. Run autonomous-cycle (Fix #1):
     ```bash
     $PYTHON tools/supervisor/autonomous_cycle.py --declaration "$DECL_PATH"
     CYCLE_EXIT=$?
     echo "autonomous-cycle exit: $CYCLE_EXIT"
     # 0 = accepted; continue
     # 3 = rework; fix declaration; re-run
     # other = investigate
     ```
  e. Build review package:
     ```bash
     $PYTHON tools/supervisor/build_declaration_review_package.py --declaration "$DECL_PATH"
     ```
     ZIP at: $ZIP_PATH  (derived from REPO_ROOT — no hardcoded user path)

     **Fallback ZIP (if builder unavailable):** Create ZIP at $ZIP_PATH containing all
     output files from reports/specification-authority-layer-production-healing/,
     both YAML files from HEALING_SPRINT_EVIDENCE_ROOT, final-git-status.txt,
     validation-results.md, review-package-proof.md (placeholder), and
     fallback-package-manifest.json (file list with sizes and SHA-256). Note "fallback ZIP" in proof.

  f. Compute SHA-256:
     ```bash
     SHA256=$($PYTHON -c "
     import hashlib, os, zipfile
     path = os.environ['ZIP_PATH']
     data = open(path,'rb').read()
     sha = hashlib.sha256(data).hexdigest()
     size = len(data)
     count = len(zipfile.ZipFile(path).namelist())
     print(sha, size, count)
     " ZIP_PATH="$ZIP_PATH")
     ```
  g. Write review-package-proof.md (Fix #9):
     ```markdown
     # Review Package Proof
     Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001
     ZIP absolute path: [derived from REPO_ROOT at runtime — no hardcoded user path]
     SHA-256: [64-char hex — computed above]
     Byte size: [computed above]
     File count: [computed above]
     Autonomous-cycle exit code: [CYCLE_EXIT value]
     ```
  h. Run 6-item gate check (Section 7). If all PASS: set evidence taskcard CLOSED_VERIFIED.

**Step 20:** Final response (Section 12).

---

## Section 9 — Validation Checks V01–V12 + V-BAN (H-008 fix)

VALIDATION SCOPE: LOCAL ONLY.

Explicit exclusions:
- No GitHub Actions run required
- No CI pipeline check required
- No remote push required
- No external service calls required
- No network access required

```bash
# V01 — All declared output files exist (declared-vs-materialized)
$PYTHON -c "
import json, pathlib
m = json.load(open('reports/specification-authority-layer-production-healing/file-ownership-map.json'))
missing = [k for k in m if not pathlib.Path(k).exists()]
print('V01 PASS' if not missing else f'V01 FAIL: {missing}')
"

# V02 — All Markdown files have H1 headings
for f in reports/specification-authority-layer-production-healing/*.md; do
  head -10 "$f" | grep -q "^# " || echo "V02 FAIL: missing H1 in $f"
done; echo "V02 CHECK DONE"

# V03 — All JSON files parse
$PYTHON -c "
import json
for f in ['reports/specification-authority-layer-production-healing/file-ownership-map.json',
          'reports/specification-authority-layer-production-healing/taskcard-state.json']:
    json.load(open(f))
print('V03 PASS')
"

# V04 — All YAML files parse
$PYTHON -c "
import yaml, os
ev = os.environ['REPO_ROOT']
for f in [f'{ev}/.local/evidences/specification-authority-layer-production-healing/evidence-declaration.yaml',
          f'{ev}/.local/evidences/specification-authority-layer-production-healing/evidence-manifest.yaml']:
    yaml.safe_load(open(f))
print('V04 PASS')
" REPO_ROOT="$REPO_ROOT"

# V05 — No duplicate keys in file-ownership-map.json
$PYTHON -c "
import json
pairs = []
with open('reports/specification-authority-layer-production-healing/file-ownership-map.json') as fh:
    json.load(fh, object_pairs_hook=lambda p: pairs.extend(p) or dict(p))
keys = [k for k,v in pairs]
dups = list(set(k for k in keys if keys.count(k)>1))
print('V05 PASS' if not dups else f'V05 FAIL: {dups}')
"

# V06 — All taskcards in terminal state
$PYTHON -c "
import json
data = json.load(open('reports/specification-authority-layer-production-healing/taskcard-state.json'))
terminal = {'CLOSED_VERIFIED','CLOSED_SKIPPED_WITH_REASON'}
bad = [t['id'] for t in data if t['status'] not in terminal]
print('V06 PASS' if not bad else f'V06 FAIL: {bad}')
"

# V07 — All 24 required keywords in final execution prompt
$PYTHON -c "
keywords = ['EXECUTION MODE','SpecSourceRegistry','SpecVault','SpecParser','SpecNormalizer',
'SpecIndexer','SpecDigestor','RequirementExtractor','SpecVerifier','RequirementGraph',
'ContextPackBuilder','SpecGovernanceRuntime','deterministic context pack','usage ledger',
'stale','refresh','coverage validator','ZST','Netpbm','DIF','Gnumeric','FODS/FODT',
'ai_draft','SHA-256']
# Scan the prompt file for this sprint (adjust filename as needed)
text = open('reports/specification-authority-layer-production-healing/final-execution-prompt.md').read()
missing = [k for k in keywords if k not in text]
print('V07 PASS' if not missing else f'V07 FAIL: {missing}')
"

# V08 — No forbidden path changed (LOCAL ONLY)
git diff HEAD --name-only -- src/net/ src/python/ tests/net/ tests/python/ \
  product-capability-matrix/ registry/
# Expected: empty output

# V09 — Autonomous-cycle was run
grep -q "Autonomous-cycle exit code:" reports/specification-authority-layer-production-healing/review-package-proof.md \
  && echo "V09 PASS" || echo "V09 FAIL"

# V10 — ZIP exists
[ -f "$ZIP_PATH" ] && echo "V10 PASS" || echo "V10 FAIL: $ZIP_PATH missing"

# V11 — SHA-256 in proof
grep -qE "SHA-256: [0-9a-f]{64}" reports/specification-authority-layer-production-healing/review-package-proof.md \
  && echo "V11 PASS" || echo "V11 FAIL"

# V12 — final-git-status.txt captured
[ -s reports/specification-authority-layer-production-healing/final-git-status.txt ] \
  && echo "V12 PASS" || echo "V12 FAIL"

# V-BAN — banned-string scan across ALL artifact files (H-002 fix)
$PYTHON -c "
import pathlib
BANNED = ['C:\\\\Users\\\\prora\\\\', 'VERDICT: COMPLETE', 'VERDICT: BLOCKED', 'VERDICT: PARTIAL',
'worker_self_verdict: PASS', 'exactly 19', 'exactly 25', 'exactly 20']
dirs = ['reports/specification-authority-layer-production-healing',
        '.local/evidences/specification-authority-layer-production-healing']
violations = []
for d in dirs:
    for p in pathlib.Path(d).rglob('*'):
        if p.is_file():
            try:
                text = p.read_text(encoding='utf-8', errors='replace')
                for b in BANNED:
                    if b in text:
                        violations.append(f'{p}: [{b}]')
            except: pass
if violations:
    print('V-BAN FAIL:')
    for v in violations: print(' ', v)
else:
    print('V-BAN PASS: BANNED_STRINGS_SCAN_PASS')
"
```

---

## Section 10 — Required Tool Implementations (13 tools — see repaired-final-single-go-execution-prompt.md Section 6)

All 13 tools as documented in the Phase 1 repaired prompt:
spec_source_registry, spec_vault_ingest, spec_parser, spec_normalizer, spec_indexer,
spec_digestor, requirement_extractor, spec_verifier, requirement_graph,
context_pack_builder, spec_governance_runtime, coverage_validator, staleness_checker.

Each tool requires: purpose, inputs, outputs, validation, error handling.

---

## Section 11 — Minimum Pilot Deliverables and Extended Prep

**Minimum (ZST, Netpbm, DIF — all 13 items required):**
1. SpecSourceRegistry: ZST source registered (source_id, license = PUBLIC_SPEC)
2. SpecSourceRegistry: Netpbm source registered
3. SpecSourceRegistry: DIF source registered
4. SpecVault: ZST raw snapshot ingested (sha256 recorded)
5. SpecVault: Netpbm raw snapshot ingested
6. SpecVault: DIF raw snapshot ingested
7. spec_parser: ZST parsed artifact (validates against schema)
8. spec_parser: Netpbm parsed artifact
9. spec_parser: DIF parsed artifact
10. RequirementExtractor: at least 5 candidate requirements for ZST
11. SpecVerifier: at least 3 verified requirements for ZST (with provenance)
12. ContextPackBuilder: one deterministic context pack for ZST (manifest.sha256 stable)
13. Regression suite: at least 1 test in each of 9 categories (A–I) passing

**Extended prep (Gnumeric, FODS/FODT — source registration + fetch-plan only):**
- Gnumeric: 1 registry entry + 1 fetch-plan document
- FODS/FODT: 1 registry entry + 1 fetch-plan document (OASIS ODF)

---

## Section 12 — Final Response Contract (H-009 fix)

Use exactly one macro verdict:
```
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
```

**Selection logic:**
```
IF all taskcards CLOSED_VERIFIED
AND V-BAN PASS (BANNED_STRINGS_SCAN_PASS)
AND all V01–V12 checks PASS
AND CYCLE_EXIT = 0
AND all 6 closure gate items confirmed:
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION

ELIF all pass but known limitations (e.g., source licensing unconfirmed):
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS

ELSE:
  → SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED
    blocker_reason: [list each failing check]
```

**Explicitly PROHIBITED (H-009):**
- "VERDICT: COMPLETE" / "VERDICT: BLOCKED" / "VERDICT: PARTIAL"
- "Sprint complete." / "All done." / "Repair done." / "Done." as verdict
- Any response without one of the three macro strings above
- Any response with more than one macro string
- Pre-filled `worker_self_verdict: PASS`

**Required final response fields:**
1. Exact macro verdict (one of the three above)
2. Review package absolute path (REPO_ROOT-derived — no hardcoded user path)
3. Review package SHA-256 (64-char hex, computed at runtime)
4. Autonomous-cycle exit code (integer)
5. List of all output files with PRESENT/MISSING status
6. All V01–V12 + V-BAN check results
7. Explicit: "No product source files modified. No commit. No push."

---

## Required Keywords Verification (24 keywords — all present in this prompt)

EXECUTION MODE | SpecSourceRegistry | SpecVault | SpecParser | SpecNormalizer | SpecIndexer
SpecDigestor | RequirementExtractor | SpecVerifier | RequirementGraph | ContextPackBuilder
SpecGovernanceRuntime | deterministic context pack | usage ledger | stale | refresh
coverage validator | ZST | Netpbm | DIF | Gnumeric | FODS/FODT | ai_draft | SHA-256

## Required Hardening Markers (8 markers — all present in this prompt)

REPO_ROOT | PLAN_REPAIRED_READY_FOR_EXECUTION | PLAN_STILL_NEEDS_REPAIR | LOCAL ONLY
AUTONOMOUS_CONTINUE | REPAIR_SPRINT_EVIDENCE_ROOT | fallback-package-manifest.json | Test-Path
