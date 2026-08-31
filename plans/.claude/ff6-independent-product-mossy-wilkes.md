# FF6 Independent Product, Autonomy, and Repeatability Hardening Review

plan_type: independent_review
review_type: independent_investigation
mission_id: FF6-PRODUCTION-LIBRARIES-001
scope: read_only_investigation_with_amendment_proposals
output_root: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\review-output\ff6-independent-review

## Context

The FF6 mission (`FF6-PRODUCTION-LIBRARIES-001`) aims to deliver six independently publishable
Python libraries: IPYNB, ORA (OpenRaster), NRRD, XLIFF, SafeTensors, and UBL. An active agent
is currently executing UBL build lane work and must not be disturbed.

This is a **read-only investigation**. It produces findings, an issue register, and amendment
proposals. It does NOT implement fixes, modify source files, append to the event journal,
or alter any canonical state file. Implementation is deferred to a follow-up governed plan
with proper taskcards.

### Confirmed Contradictions (from planning exploration)
- **ORA namespace split**: `product-goal.yaml` says `format-factory-openraster` / `format_factory.openraster`; `pyproject.toml` says `format-factory-ora` / `format_factory.ora`. Zero code references `format_factory.openraster`.
- **UBL package-matrix stale**: uses legacy `module_import: ubl`, missing `build_mode: native_pyproject`.
- **ORA not in package-matrix**: despite having production source and pyproject.toml.
- **Gap FF6-GAP-001 stale**: says "no source" but ORA has source since Events 74-77.
- **671/689 obligations unresolved** (Event 65 measurement).
- **5 of 6 products have legacy shadow test suites** alongside production source.
- **No `rebuild` command exists** in `controller_events.py` (only `verify` and `append`), so projections cannot be regenerated from the event journal.

### Coexistence rules
- Work in an isolated review worktree (detached HEAD).
- Do NOT modify files in the main checkout.
- Do NOT write to `src/`, `plans/strategic/ff6/events.jsonl`, or `controller-state.yaml`.
- Do NOT append events, claim leases in EXCLUSIVE_WRITE mode, or register as an active sprint agent.
- Record initial/final HEAD SHAs at execution time (not planning time).
- Classify every proposed change: SAFE_NOW / CHECKPOINT_REQUIRED / BLOCKED_BY_ACTIVE_WORK / ALREADY_FIXED / SUPERSEDED.

### Environment notes
- **Windows 11**, Git Bash for POSIX commands.
- Canonical Python: `.venv/Scripts/python` (has pytest, build tools). System Python has no pytest.
- `.local/venv/Scripts/python` also exists (older venv).
- Worktree will NOT have its own venv — must create one or use absolute paths to main `.venv`.
- `Write(src/python/*/**)` is DENIED in `.claude/settings.json` — no source modifications allowed.
- EP-3: any `src/` modifications require skill invocation (not applicable — this is read-only).

---

## Taskcards

### TC-REV-001: Isolation Setup and Concurrency Snapshot
**Status**: READY
**Acceptance**: Worktree exists, initial SHA recorded, active agent state documented, output directory created.
**Evidence**: `review-output/00-concurrency-snapshot.yaml`

Steps:
1. Record initial HEAD SHA: `git rev-parse HEAD` (capture at execution time)
2. Record last event from `plans/strategic/ff6/events.jsonl` (parse last line)
3. Record active task from `controller-state.yaml`
4. List active coordination leases (read-only query of coordination DB if accessible)
5. Record recently modified paths: `git diff --stat HEAD~5..HEAD`
6. Create review worktree:
   ```bash
   git worktree add --detach .local/worktrees/ff6-review-independent-001 HEAD
   ```
   If path already exists, use a unique suffix (e.g., `-002`).
7. Create output directory:
   ```bash
   mkdir -p .local/review-output/ff6-independent-review
   ```
   All deliverables go here (absolute path: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\review-output\ff6-independent-review\`).
8. Prune stale worktrees: `git worktree prune` (removes prunable entries only — safe).

**Gate**: Worktree created and writable. If worktree creation fails (path length, disk space), fall back to working directly from the main checkout with read-only tools (Read, Grep, Glob, Bash read-only commands). The review can proceed without a worktree — it's read-only.

**Rollback**: `git worktree remove .local/worktrees/ff6-review-independent-001` if cleanup needed.

---

### TC-REV-002: Current Truth Inventory
**Status**: READY
**Depends on**: TC-REV-001
**Acceptance**: Product inventory table, package identity reconciliation, shadow test contamination map, obligation state map, state file freshness audit — all written to output.
**Evidence**: `review-output/01-truth-inventory.yaml`

#### 2.1 Product source and test inventory
For each of the 6 products (ipynb, ora, nrrd, xliff, safetensors, ubl), collect:
- Production .py count and LOC in `src/python/{fmt}/src/format_factory/{fmt}/`
- Test file count and test function count in `tests/python/{fmt}/`
- `__all__` symbol count from production `__init__.py`
- pyproject.toml: distribution name, namespace, version, dependencies
- Egg-info presence, build artifact presence
- Package-matrix entry status and correctness

#### 2.2 Package identity reconciliation
Cross-reference three canonical sources for every product:
- `plans/strategic/ff6/product-goal.yaml` (distribution, import_namespace)
- `src/python/{fmt}/pyproject.toml` (name, packages include)
- `packaging/python/package-matrix.yaml` (module_import, build_mode, local_dependencies)

Document every inconsistency.

#### 2.3 Shadow test contamination mapping
For each product with legacy code (ipynb, nrrd, xliff, safetensors, ubl):
```bash
for f in tests/python/{fmt}/test_*.py; do
  has_legacy=$(grep -c "from ${fmt}\.\|import ${fmt}\." "$f" 2>/dev/null || echo 0)
  has_prod=$(grep -c "from format_factory\.${fmt}" "$f" 2>/dev/null || echo 0)
  echo "$f: legacy=$has_legacy prod=$has_prod"
done
```
Cross-reference with controller-state.yaml shadow_package_evidence_gap percentages.

#### 2.4 Obligation state mapping
For each product, read:
- `plans/strategic/ff6/obligations/{fmt}.yaml` — total count
- `reports/format-contract-layer/{fmt}-obligation-reconciliation.json` — proof status distribution (PROMOTING / PARTIAL_NONPROMOTING / MISSING)
- `shared/format-contracts/implementation-evidence/{fmt}.yaml` — selector-bound evidence

#### 2.5 State file freshness audit
For each canonical state file, check last-modified commit vs event journal head:
```bash
for f in plans/strategic/ff6/controller-state.yaml \
         plans/strategic/ff6/current-state.yaml \
         plans/strategic/ff6/current-gaps.yaml \
         plans/strategic/ff6/product-goal.yaml \
         plans/strategic/ff6/execution-recovery-directive.yaml \
         packaging/python/package-matrix.yaml \
         registry/format-contract-registry.yaml; do
  echo "=== $f ==="
  git log -1 --format='%h %ci %s' -- "$f"
done
```

#### 2.6 Event journal integrity
```bash
.venv/Scripts/python -m tools.ff6.controller_events verify
```
Expected: PASS through all events. Any chain break is a P0 finding.

---

### TC-REV-003: Failure Reproduction
**Status**: READY
**Depends on**: TC-REV-002
**Acceptance**: Each highlighted failure reproduced or refuted with exact commands and output. Security surface audit completed for all 6 products.
**Evidence**: `review-output/02-failure-reproduction.yaml`

#### 3.1 OpenRaster namespace inconsistency
```bash
grep -r "format_factory\.openraster" src/ tests/ 2>/dev/null | head -5
# Expected: zero matches
ls src/python/ora/src/format_factory/ora/__init__.py
# Expected: exists
git log -1 --format='%h %ci %s' -- plans/strategic/ff6/product-goal.yaml
git log -1 --format='%h %ci %s' -- src/python/ora/pyproject.toml
```

#### 3.2 Legacy/shadow test contamination (IPYNB deep-dive)
Categorize all test files in `tests/python/ipynb/` by import path. For each of the 6 capabilities with NO valid evidence (IPYNB-OUTPUT-001, IPYNB-CELLNAME-001, IPYNB-CELLNAMEUNIQUE-001, IPYNB-ID-001, IPYNB-EXPORT-001, IPYNB-WRITE-001), verify whether any test uses the shipped namespace (`format_factory.ipynb`).

#### 3.3 Independent test collection (GAP-005 reproduction)
Attempt test collection WITHOUT installed packages. This will fail — document the exact errors:
```bash
.venv/Scripts/python -m pytest tests/python/ipynb --collect-only 2>&1 | tail -20
.venv/Scripts/python -m pytest tests/python/nrrd --collect-only 2>&1 | tail -20
.venv/Scripts/python -m pytest tests/python/ora --collect-only 2>&1 | tail -20
.venv/Scripts/python -m pytest tests/python/xliff --collect-only 2>&1 | tail -20
.venv/Scripts/python -m pytest tests/python/safetensors --collect-only 2>&1 | tail -20
.venv/Scripts/python -m pytest tests/python/ubl --collect-only 2>&1 | tail -20
```
Note: `.venv` has the packages editable-installed, so collection may succeed. If so, test from a fresh venv in the worktree to reproduce the clean-checkout failure:
```bash
cd .local/worktrees/ff6-review-independent-001
python -m venv .review-venv
.review-venv/Scripts/python -m pytest tests/python/ipynb --collect-only 2>&1 | tail -20
```

#### 3.4 Security surface audit
For each format, read the `security/` module and codec reader to check for:

**ORA** (ZIP+XML+PNG — highest risk):
- Read `src/python/ora/src/format_factory/ora/security/` — check resource limits, XML parser config
- Read `src/python/ora/src/format_factory/ora/codec/stack_xml.py` — check entity resolution, DOCTYPE handling
- Read `src/python/ora/src/format_factory/ora/codec/container.py` — check ZIP path traversal, symlink, bomb protection
- Read `src/python/ora/src/format_factory/ora/codec/png_metadata.py` — check PNG validation depth

Reproduce the 4 highlighted ORA issues:
1. Craft UTF-16 XML with DOCTYPE — does raw ASCII search miss it?
2. Supply entity expansion — is it accepted despite DOCTYPE prohibition?
3. Supply truncated/corrupt PNG — is it accepted in strict mode?
4. Supply ZIP with non-UTF-8 filenames — is flag enforcement missing?

**XLIFF and UBL** (XML): Check for XXE, billion laughs, encoding enforcement.
**SafeTensors** (binary): Check header size limits, offset overlap validation, integer overflow.
**NRRD** (binary+text): Check header injection, detached data path traversal, dimension limits.
**IPYNB** (JSON): Check JSON size limits, base64 attachment limits, output size limits.

#### 3.5 Package build and identity verification
Create a fresh venv in the worktree and attempt wheel builds:
```bash
cd .local/worktrees/ff6-review-independent-001
python -m venv .build-venv
.build-venv/Scripts/pip install build setuptools
.build-venv/Scripts/python -m build src/python/core --wheel --outdir .local/review-output/ff6-independent-review/wheels/
for fmt in ipynb nrrd xliff safetensors ubl ora; do
  .build-venv/Scripts/python -m build src/python/$fmt --wheel --outdir .local/review-output/ff6-independent-review/wheels/ 2>&1
done
```
For each wheel: extract METADATA, verify `Name:` matches pyproject.toml. Attempt clean-venv import:
```bash
.build-venv/Scripts/pip install .local/review-output/ff6-independent-review/wheels/format_factory_core-*.whl
for fmt in ipynb nrrd xliff safetensors ubl ora; do
  .build-venv/Scripts/pip install .local/review-output/ff6-independent-review/wheels/format_factory_${fmt}-*.whl
  .build-venv/Scripts/python -c "import format_factory.${fmt}; print('OK:', format_factory.${fmt}.__name__)" 2>&1
done
```

#### 3.6 State file divergence
Compare `controller-state.yaml` transition_sequence against the actual last event in `events.jsonl`:
```bash
.venv/Scripts/python -c "
import json, yaml
with open('plans/strategic/ff6/events.jsonl') as f:
    lines = [json.loads(l) for l in f if l.strip()]
    last = lines[-1]
    print(f'Journal head: sequence={last[\"sequence\"]}, event_id={last[\"event_id\"]}')
with open('plans/strategic/ff6/controller-state.yaml') as f:
    state = yaml.safe_load(f)
    print(f'Projection: sequence={state[\"transition_sequence\"]}, event_id={state[\"last_verified_event\"][\"event_id\"]}')
    if state['transition_sequence'] != last['sequence']:
        print('FINDING: Projection is STALE')
    else:
        print('OK: Projection is current')
"
```

#### 3.7 Mutation resistance analysis
Read mutation test results from Event 73 (commit `2f84d840`). Check:
- Which modules have weakest mutation scores
- Whether mutation tests target shipped namespace or shadow package
- Read the test files that drive mutation testing

#### 3.8 Product depth assessment
For each product, read the full production source tree and evaluate depth against the criteria listed in the original review request. Document present/absent capabilities per format.

---

### TC-REV-004: Root Cause Analysis
**Status**: READY
**Depends on**: TC-REV-003
**Acceptance**: Each failure class traced to a root cause. Root causes categorized.
**Evidence**: `review-output/03-root-cause-analysis.yaml`

#### 4.1 Why do truth sources diverge (ORA namespace)?
Trace git history of both files. Root cause: `product-goal.yaml` written by Codex before source existed; ORA source written by Claude using format_id `ora` consistently; goal record never updated.

#### 4.2 Why can't projections be regenerated?
`controller_events.py` has only `verify` and `append` — no `rebuild`. The controller-state.yaml is manually maintained. This means it's a hand-edited truth source, not a derived projection. This is a systemic architectural issue.

#### 4.3 Why do legacy shadows persist?
Check if any production code imports from legacy files. If not, they persist because no cleanup task was ever executed. Check if `Compat/` and `spec/` directories are imported by anything:
```bash
for fmt in ipynb nrrd xliff safetensors ubl; do
  echo "=== $fmt ==="
  grep -r "from.*Compat\|from.*spec\." src/python/$fmt/src/format_factory/$fmt/ 2>/dev/null | head -5
done
```

#### 4.4 Why can't tests be collected on clean checkout?
Map the dependency chain. Root cause: namespace package `format_factory` requires installed wheels; test files import from `format_factory.{fmt}`; without installed packages, Python can't resolve the namespace.

#### 4.5 Obligation classification inflation
Check if any obligation at PARTIAL_NONPROMOTING has been counted as "implemented" in capability maps, gap ledger, or controller state.

---

### TC-REV-005: Traction and Ecosystem Analysis
**Status**: READY
**Depends on**: TC-REV-003 (needs product depth assessment)
**Acceptance**: Per-product traction analysis with MINIMUM_USEFUL / PROFESSIONAL / DIFFERENTIATED tiers.
**Evidence**: `review-output/04-traction-analysis.yaml`

For each product, document:
- Existing ecosystem alternatives and their strengths/weaknesses
- Credible differentiation for FF6 libraries
- Three readiness tiers with specific criteria
- Key integrations likely to drive adoption
- Package naming quality for PyPI discoverability

Use WebSearch if available; otherwise use known ecosystem knowledge (nbformat, pynrrd, safetensors, translate-toolkit/polib for XLIFF, python-ubl for UBL, no well-known ORA library).

**Fallback**: If WebSearch is unavailable, produce the analysis from training knowledge and mark claims as `confidence: high/medium/low` based on certainty.

---

### TC-REV-006: Autonomous Execution Model Validation
**Status**: READY
**Depends on**: TC-REV-002
**Acceptance**: Goal driver tested from worktree, cross-agent resume simulated, check_continuation vs goal_driver compared, execution contract gap analysis produced.
**Evidence**: `review-output/05-execution-model-validation.yaml`

#### 6.1 Goal driver determinism test
```bash
.venv/Scripts/python -m tools.ff6.goal_driver check 2>&1
.venv/Scripts/python -m tools.ff6.goal_driver resume 2>&1
```
Record output. Verify it selects a valid next task.

#### 6.2 Cross-agent resume simulation
A fresh Codex agent would:
1. Read committed state files only (no `.local/` ephemeral state)
2. Run `goal_driver resume`
3. Get the same next task

Verify: does goal_driver output depend on any `.local/` file? If yes, that's a portability gap.

#### 6.3 check_continuation comparison
```bash
.venv/Scripts/python tools/supervisor/check_continuation.py 2>&1
```
Expected: SESSION_MISMATCH or similar (no continuation signal for this session). Document the difference from goal_driver.

#### 6.4 Execution contract gap analysis
Read AGENTS.md, `docs/governance/codex-adapter.md`, `docs/governance/kilo-adapter.md`. Document:
- What's shared between agents (same contract)
- What diverges (agent-specific state, different task selection, different evidence rules)
- What's missing for true agent interchangeability

This is a GAP ANALYSIS of the existing system, NOT a new contract. The amendment proposal (TC-REV-008) will recommend specific fixes.

---

### TC-REV-007: Repeatability Assessment
**Status**: READY
**Depends on**: TC-REV-003 (needs package build results)
**Acceptance**: Clean-build test results, regeneration pilot results or blocker chain, projection rebuild assessment.
**Evidence**: `review-output/06-repeatability-assessment.yaml`

#### 7.1 Clean-checkout build test
Use the wheels built in TC-REV-003 Task 3.5. If they succeeded, attempt:
```bash
# In the build venv from TC-REV-003
.build-venv/Scripts/python -c "
from format_factory.ipynb import load, dump
from format_factory.nrrd import load as nrrd_load
from format_factory.safetensors import load as st_load
# etc. — verify basic API availability
print('All imports OK')
"
```

#### 7.2 Destructive regeneration pilot (ORA)
In the review worktree ONLY:
1. Record ORA's current public API (`__all__` from `__init__.py`)
2. Record source file hashes
3. Record test results (if tests can be collected)
4. Check if any regeneration process exists:
   ```bash
   grep -r "regenerat\|kickstart\|scaffold\|new.format" tools/ .claude/commands/ 2>/dev/null | head -20
   ```
5. If `/new-format-kickstart` skill exists, document what it would produce vs what ORA currently has
6. Document the blocker chain for full regeneration

This does NOT delete ORA source — it assesses whether the documented regeneration process could reconstruct it.

#### 7.3 State projection rebuild assessment
**KNOWN FINDING**: `controller_events.py` has only `verify` and `append` — no `rebuild` command. Document this as:
- Finding: controller-state.yaml cannot be regenerated from events.jsonl
- Root cause: no rebuild tooling exists
- Impact: if the projection drifts from the journal, there's no automated way to correct it
- Evidence: `grep -n "add_subparser\|subcommand" tools/ff6/controller_events.py`

---

### TC-REV-008: Deliverable Production
**Status**: READY
**Depends on**: TC-REV-002 through TC-REV-007
**Acceptance**: All 10 deliverables produced in the output directory, evidence bundle ZIP created with absolute path printed.
**Evidence**: Evidence bundle ZIP at `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\review-output\ff6-independent-review\evidence-bundle.zip`

#### Deliverable priority order
If context exhausts mid-production, ensure these are produced first:

**P0 (must produce)**:
1. Executive truth report (`01-executive-truth-report.md`)
2. Root-cause issue register (`05-issue-register.yaml`)
3. Product-readiness matrix (`02-product-readiness-matrix.yaml`)

**P1 (should produce)**:
4. Canonical-state audit (`03-canonical-state-audit.yaml`)
5. Existing-plan amendment proposal (`06-plan-amendment-proposal.yaml`)
6. Integration queue (`07-integration-queue.yaml`)

**P2 (produce if context allows)**:
7. Repeatability specification (`08-repeatability-specification.md`)
8. Execution contract gap analysis (`04-execution-contract-gap-analysis.md`)
9. Destructive-regeneration pilot report (`09-regeneration-pilot-report.md`)
10. Traction and adoption analysis (`10-traction-analysis.yaml`)

**Always last**: Evidence bundle ZIP (bundles all of the above).

#### Deliverable schemas

**Executive truth report** (Markdown): Current state of all 6 products, autonomous execution state, repeatability state, publication state, most serious contradictions, what the active agent is changing, what must not be disturbed.

**Product-readiness matrix** (YAML): Per product — package identity (dist name, import namespace, version), capability depth counts, obligation counts by proof status, test quality (count, namespace, mutation score), security maturity, interop maturity, docs maturity, independent build/install/publish status, MINIMUM_USEFUL/PROFESSIONAL/DIFFERENTIATED readiness percentage, largest blockers, recommended next vertical slice.

**Canonical-state audit** (YAML): Per artifact — file path, what it claims to be (canonical/derived/stale), what it actually is, conflicts with other artifacts, recommended disposition (keep canonical / make derived / delete / archive), rebuild process if derived, state-transition invariants, failure behavior when inconsistent.

**Execution contract gap analysis** (Markdown): Gap analysis of AGENTS.md + goal_driver + coordination system + codex-adapter. What's shared, what diverges, what's missing. NOT a new contract — amendment proposals only.

**Root-cause issue register** (YAML): Per issue — stable ID (REV-NNN), severity (P0-P4), product or system scope, symptom, reproduction command, root cause category, evidence file/line, current owner if any, active-agent overlap, sustainable fix (description only — no implementation), migration steps, acceptance criteria, concurrency classification (SAFE_NOW / CHECKPOINT_REQUIRED / BLOCKED_BY_ACTIVE_WORK / ALREADY_FIXED / SUPERSEDED), final status after reconciliation.

**Existing-plan amendment proposal** (YAML): Amendments grouped by severity (P0-P4). Each amendment: existing section/task being changed, problem, proposed replacement or addition, reason, dependencies, migration, acceptance checks, whether active work is affected, integration timing.

**Integration queue** (YAML): Machine-readable queue ordered by dependencies, risk, active-agent overlap, product value, throughput, parallel-execution ability. Each entry: amendment ID, severity, safe lanes, blocked lanes, estimated effort.

**Repeatability specification** (Markdown): Exact commands for bootstrap, environment validation, product build, each test category, docs build, evidence bundle, independent extraction, publication dry run, state projection rebuild, agent resume. No undocumented shell state.

**Destructive-regeneration pilot report** (Markdown or YAML): Selected product, why selected, original baseline, regeneration inputs, regeneration procedure, manual interventions required, before/after API comparison, test results, gaps, exact work needed.

**Traction analysis** (YAML): Per product — ecosystem alternatives, differentiation, three tiers with criteria, key integrations, PyPI discoverability, adoption obstacles.

#### Evidence bundle
```bash
cd C:\Users\prora\OneDrive\Documents\GitHub\format-factory
.venv/Scripts/python -c "
import zipfile, os, glob
output_dir = '.local/review-output/ff6-independent-review'
zip_path = os.path.join(output_dir, 'evidence-bundle.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in glob.glob(os.path.join(output_dir, '*')):
        if not f.endswith('.zip'):
            zf.write(f, os.path.basename(f))
print(f'Evidence bundle: {os.path.abspath(zip_path)}')
"
```
Print the absolute path: `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\review-output\ff6-independent-review\evidence-bundle.zip`

---

### TC-REV-009: Reconciliation with Active Agent
**Status**: READY
**Depends on**: TC-REV-008
**Acceptance**: Final SHA recorded, findings reclassified against new commits, evidence bundle updated.
**Evidence**: `review-output/11-reconciliation.yaml`

#### 9.1 Fetch latest commits
```bash
git log --oneline {initial_sha}..HEAD
```
(Where `{initial_sha}` was captured in TC-REV-001.)

#### 9.2 Reclassify findings
For each commit made during the review:
- Read commit message and changed files
- Check if any review finding was addressed
- Mark findings as ALREADY_FIXED or SUPERSEDED where applicable
- Update concurrency classifications

#### 9.3 Update evidence bundle
Re-zip with reconciliation results. Print final absolute path.

---

## Rollback and Recovery

### Worktree cleanup
```bash
git worktree remove .local/worktrees/ff6-review-independent-001 --force
```
Safe because the worktree contains no committed changes — it's detached HEAD at a recorded SHA.

### If the agent crashes mid-review
- All deliverables are written incrementally to the output directory.
- A new session can read the output directory and resume from the last completed taskcard.
- The concurrency snapshot (TC-REV-001) provides the base SHA for reconciliation.

### Shared mutable state protection
- The coordination SQLite DB is shared across agents but this review only READS it (no lease claims, no writes).
- The event journal is not modified.
- No `.local/supervisor/` signal files are written.

### If worktree creation fails
- Fall back to running the review from the main checkout using read-only tools.
- The review is entirely read-only, so no worktree isolation is strictly necessary.
- The worktree's main value is for the clean-build test (TC-REV-003 Task 3.5) and regeneration pilot (TC-REV-007 Task 7.2).

---

## Verification

The review is complete when:
1. All P0 deliverables exist in the output directory (truth report, issue register, product-readiness matrix)
2. Every finding cites a concrete file path, command, or commit SHA
3. Every proposed change is classified (SAFE_NOW / CHECKPOINT_REQUIRED / BLOCKED_BY_ACTIVE_WORK / ALREADY_FIXED / SUPERSEDED)
4. The evidence bundle ZIP exists and its absolute path is printed
5. The final SHA comparison against the initial SHA is recorded
6. No modifications were made to the active agent's checkout or canonical state files
7. No events were appended to the journal
8. No source files were modified


## Taskcard Status Summary

| TC-ID | Status |
|---|---|
| TC-REV-001 | CLOSED |
| TC-REV-002 | CLOSED |
| TC-REV-003 | CLOSED |
| TC-REV-004 | CLOSED |
| TC-REV-005 | CLOSED |
| TC-REV-006 | CLOSED |
| TC-REV-007 | CLOSED |
| TC-REV-008 | CLOSED |
| TC-REV-009 | CLOSED |

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-08-05T06:32:45.750372+00:00"
  locked_by: "32ee0156fdd1"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
