# Playbook System: Structural Integration and Loop Closure

**Plan ID:** glowing-swinging-grove
**Date:** 2026-07-10
**Prior work:** FF-PLAYBOOK-SYSTEM-001 (2026-07-01), audit (2026-07-02)

---

## The Actual Problem

The prior certifications were real. The tools are real. The 217 tests are real. The evidence files have genuine timestamps. None of that is wrong.

What is wrong is that the prior certifications certified the **tools in isolation**. They did not certify that the playbook system connects to the sprint execution loop — because it does not.

The sprint execution loop has five connection points where the playbook system could participate. At every one of them, the current state is disconnected:

| Connection point | Current state |
|-----------------|---------------|
| `next-sprint.md` generation | `generate_supervisor_packet.py` has zero playbook involvement |
| Evidence declaration | Schema has `additionalProperties: false`, no playbook fields |
| Grading loop | `grade_declared_work.py` has no playbook parameters; execution logs written *after* grading completes |
| `autonomous_cycle.py` step 1a | Prints a path to stdout; nothing reads or acts on the output |
| `.local/playbook-executions/` | Written by `playbook_execution_log.py`; consumed only by tests, never by the production pipeline |

This is why the system needs re-auditing every time someone asks "does it work?": the tools pass tests in isolation, but isolated tools produce no observable sprint behavior. There is nothing to degrade and nothing to improve. The re-audit cannot find consistent runtime effects because there are none.

---

## Diagnosis

### Symptoms
- Periodic re-auditing required; each audit proves the tools still work, nothing more
- `next-sprint.md` never contains a playbook reference
- Agents executing FORMAT_FEATURE_EXPANSION, NEW_FORMAT_KICKSTART, etc. receive no playbook context
- Evidence grader is unaware of whether a playbook was applicable
- Playbook execution logs accumulate in `.local/` and are never acted on
- 217 playbook tests are not in CI — can silently break between commits
- V92 (registry file-not-found) is WARN-only despite detecting a structural failure

### Root Causes

**RC-1 (primary): The forward channel is broken at the wrong end.**
`autonomous_cycle.py` step 1a selects a playbook for the **current sprint's** already-completed work and prints the path to stdout. `generate_supervisor_packet.py`, which generates the NEXT sprint's prompt, has zero playbook involvement. Fixing timing alone is necessary but insufficient (see RC-2).

**RC-2: There is no return channel.**
The evidence declaration schema (`additionalProperties: false`) explicitly forbids unknown fields. Workers cannot declare playbook adherence even if they wanted to. The grading engine (`grade_declared_work.py`) receives no playbook parameters — and it could not use them anyway, because playbook execution logs are written after grading completes. The playbook system has no way to know if it had any effect.

**RC-3: Without a return channel, there is no feedback loop.**
The supervisor cannot detect drift (playbook context was in the prompt but the work was done differently). Without drift detection, the system cannot improve consistency over time. Every sprint runs ad-hoc, regardless of what playbook context was available.

**RC-4: CI does not protect the tools that would implement the loop.**
217 tests can silently fail between commits. Any regression in `playbook_selector.py`, `generate_playbook_taskcards.py`, or `playbook_execution_log.py` is invisible until the next manual audit.

**RC-5: V92 mis-tiered.**
Registry file-not-found is WARN. V93-V99 are correctly WARN (drift signals). V92 detects broken references — a different category of failure that warrants blocking.

### What Must Be Preserved
- All tool implementations — real and production-quality; do not rewrite
- MODEL C two-layer architecture — the separation is correct
- Advisory semantics for playbook selection — do not block sprints on playbook failure
- WARN-only semantics for V93-V99 — these are drift signals, not structural failures
- All 217 tests — they are real; they need CI coverage, not replacement
- `apply` mode correctly blocked — out of scope

### What Must Change
Five changes that together close the loop:

| # | Change | Root cause addressed |
|---|--------|---------------------|
| C1 | Inject playbook context into `next-sprint.md` | RC-1: agent gets guidance before executing |
| C2 | Add parallel post-grading drift check in `autonomous_cycle.py` | RC-2, RC-3: detect when playbook context was available but work shows no adherence signals |
| C3 | Wire drift findings into `next-sprint.md` synthesis | RC-3: close the feedback loop |
| C4 | Add `tests/playbook/` to CI | RC-4: regressions caught automatically |
| C5 | Escalate V92 to blocking | RC-5: structural failures distinguished from drift |

**What C2 does not do:** It does not modify the evidence schema. It does not affect grading. It is a parallel check, not a grading dimension. This is deliberate — the schema is strict by design (`additionalProperties: false`), and adding playbook adherence as a grading dimension would require workers to actively populate new fields, which introduces behavioral coupling. A parallel post-grading check achieves feedback without that coupling.

---

## Taskcards

### TC-PBHP-001 — Baseline: Verify Actual State at HEAD
**Status:** OPEN

The prior certified state is from commit `f88c884`, 8+ commits behind HEAD. Do not assume it still holds.

Steps:
1. `.venv/Scripts/pytest tests/playbook/ -q 2>&1` — capture actual pass/fail count. This supersedes the stale 217-pass claim.
2. Verify all 8 registry entries resolve: `python -c "import yaml,os; r=yaml.safe_load(open('playbooks/playbook-registry.yaml')); [print(k,os.path.exists(e['canonical_path'])) for k,e in r['playbook_registry']['entries'].items()]"`
3. Run governance validators and capture V92-V99 results specifically.
4. Count actual defined validators: `grep -c "^def validate_" tools/supervisor/governance_validators*.py` — compare to claimed 167.
5. Record HEAD: `git rev-parse HEAD`.

If tests fail, record which ones. If registry entries are missing, that is an immediate P0 finding. Do not skip or interpret results favorably.

**Output:** `.local/evidences/pbhp-baseline/state.yaml` with actual counts and any failures.

---

### TC-PBHP-002 — Forward Channel: Inject Playbook Context into next-sprint.md (C1)
**Status:** OPEN
**Depends on:** TC-PBHP-001

**Problem:** `generate_supervisor_packet.py` generates `next-sprint.md` with zero playbook involvement. The agent executing Sprint N+1 receives no playbook context from the sprint prompt.

**File to modify:** `tools/supervisor/generate_supervisor_packet.py`

**Integration point:** `synthesize_sprint_tasks()` already knows the next sprint's work item types. After this function returns its task list, the applicable playbook for each unique `item_type` should be resolved and injected into the sprint prompt.

**Read first:** Read `generate_supervisor_packet.py` `generate_next_sprint_md()` function signature and its parameter list in full before implementing. The exploration agent described it but the exact signature must be verified before modifying.

**Implementation direction:** Add a non-blocking, exception-isolated playbook resolution step within `generate_next_sprint_md()`. For each unique `item_type` in the `tasks` parameter, call `playbook_selector.select_playbook()` and parse the contract's `phases`, `stop_conditions`, and `playbook_id`. Append a `## Playbook Guidance (advisory)` section to the generated markdown.

```python
# Append to content in generate_next_sprint_md(), after main body:
try:
    import sys as _sys
    _sys.path.insert(0, str(repo_root / "tools" / "playbook"))
    from playbook_selector import select_playbook as _sel
    from generate_playbook_taskcards import parse_contract as _parse
    _seen, _sections = set(), []
    for task in tasks:
        wtype = task.get("item_type", "")
        if wtype and wtype not in _seen:
            _seen.add(wtype)
            path = _sel(wtype)
            if path:
                contract = _parse(str(repo_root / path)) if path else None
                if contract and contract.get("status") == "ACTIVE":
                    _sections.append({
                        "type": wtype, "skill": f"/{contract['playbook_id']}",
                        "phases": contract.get("phases", []),
                        "stop_conditions": contract.get("stop_conditions", []),
                    })
    if _sections:
        pb_block = "\n\n---\n\n## Playbook Guidance (advisory)\n\n"
        pb_block += "> Invoke the listed skill before executing each work item type.\n\n"
        for s in _sections:
            pb_block += f"**{s['type']}** → `{s['skill']}`"
            if s["phases"]:
                pb_block += f"  \nPhases: {' → '.join(s['phases'])}"
            if s["stop_conditions"]:
                pb_block += f"  \nStop if: {'; '.join(s['stop_conditions'])}"
            pb_block += "\n\n"
        content += pb_block
except Exception:
    pass  # advisory — never blocks sprint generation
```

**What this does NOT do:** Does not enforce phases. Does not affect grading. Does not block sprints. Provides context before sprint execution instead of after.

**Test to add (regression control):** In `tests/playbook/test_supervisor_integration.py`, add `test_next_sprint_md_includes_playbook_context()`:
- Build a minimal task list with `item_type: FORMAT_FEATURE_EXPANSION`
- Call `generate_next_sprint_md()` with it
- Assert output contains `## Playbook Guidance`
- Assert output contains `/format-feature-expansion`
- Assert at least one phase from the contract appears

**Tradeoff:** `generate_supervisor_packet.py` gains a dependency on `tools/playbook/`. If `playbook_selector` fails to import, the try/except silently omits the section. The test above catches broken imports at CI time.

**Output:** Modified `generate_supervisor_packet.py`; new test.

---

### TC-PBHP-003 — Return Check: Post-Grading Drift Detection (C2)
**Status:** OPEN
**Depends on:** TC-PBHP-002

**Problem:** The schema has `additionalProperties: false` — workers cannot declare playbook adherence. The grading engine has no playbook parameters. Modifying the schema and grader introduces behavioral coupling (workers must actively populate new fields). A parallel post-grading check achieves the same feedback without schema modification.

**Design:** After `grade_declared_work.grade_all()` completes (step 3 in `autonomous_cycle.py`), run a separate `check_playbook_drift()` function. This function:
1. For each work item in the declaration, calls `select_playbook(item["item_type"])` to check if a playbook was applicable.
2. If applicable, checks the declaration's `evidence_paths` and `notes` fields for any mention of the playbook's required phases (simple string membership check).
3. If a playbook was applicable and none of its phases appear in the evidence, creates a `PLAYBOOK_DRIFT` finding.

**Where to add this:** New function in `tools/playbook/playbook_drift_checker.py`. Called from `autonomous_cycle.py` after step 3 (grading), before step 4 (packet generation). Non-blocking: all exceptions are caught and logged; the cycle continues regardless.

```python
# tools/playbook/playbook_drift_checker.py

def check_playbook_drift(declaration: dict, repo_root: Path) -> list[dict]:
    """
    Post-grading drift check. For each work item with an applicable playbook,
    checks whether evidence paths or notes mention the playbook's required phases.
    Returns a list of PLAYBOOK_DRIFT findings (may be empty). Never raises.
    """
    findings = []
    try:
        from playbook_selector import select_playbook
        from generate_playbook_taskcards import parse_contract

        for item in declaration.get("planned_work_items", []):
            item_type = item.get("item_type", "")
            if not item_type:
                continue
            path = select_playbook(item_type)
            if not path:
                continue
            contract = parse_contract(str(repo_root / path))
            if not contract or contract.get("status") != "ACTIVE":
                continue
            phases = contract.get("phases", [])
            if not phases:
                continue

            # Check if any phase appears in evidence paths or notes
            evidence_text = " ".join(
                str(p) for p in item.get("evidence_paths", [])
            ) + " " + str(item.get("notes", ""))

            phases_seen = [p for p in phases if p.lower() in evidence_text.lower()]
            if not phases_seen:
                findings.append({
                    "finding_type": "PLAYBOOK_DRIFT",
                    "work_item_id": item.get("item_id", ""),
                    "work_item_type": item_type,
                    "applicable_playbook": path,
                    "required_phases": phases,
                    "phases_evidenced": [],
                    "description": (
                        f"Playbook '{path}' was applicable for {item_type} "
                        f"but none of its {len(phases)} required phases appear "
                        f"in the item's evidence paths or notes."
                    ),
                    "severity": "WARN",
                    "blocks_sprint": False,
                })
    except Exception as e:
        findings.append({
            "finding_type": "PLAYBOOK_DRIFT_CHECK_ERROR",
            "error": str(e),
            "severity": "INFO",
            "blocks_sprint": False,
        })
    return findings
```

**Calling site in `autonomous_cycle.py`:** After step 3 (grading), before packet generation:
```python
# After grade_all() returns:
try:
    from playbook_drift_checker import check_playbook_drift as _drift_check
    _drift_findings = _drift_check(decl, repo_root)
    if _drift_findings:
        print(f"  [PLAYBOOK_DRIFT] {len(_drift_findings)} finding(s):")
        for f in _drift_findings:
            if f.get("finding_type") == "PLAYBOOK_DRIFT":
                print(f"    {f['work_item_id']}: {f['applicable_playbook']} phases not evidenced")
    # Write findings to a file for TC-PBHP-004 to consume:
    drift_path = _r / ".local" / "supervisor" / "playbook-drift-findings.json"
    drift_path.write_text(json.dumps(_drift_findings, indent=2))
except Exception as _e:
    print(f"  [PLAYBOOK_DRIFT] drift check failed (non-blocking): {_e}")
```

**Honest limits of this check:**
- Phase detection is string membership in evidence_paths and notes. False negatives are common (agent completes phases but uses different wording). This is expected and acceptable for a WARN-only signal.
- False positives can occur if phase names appear in unrelated evidence paths (unlikely for names like `read_codec` or `verify_import`, but possible).
- The check is a signal, not a verdict. It is never used in grading.

**Test to add:** `tests/playbook/test_supervisor_integration.py` — `test_drift_check_detects_missing_phases()`:
- Create a declaration with a FORMAT_FEATURE_EXPANSION work item and evidence_paths that do NOT mention any phase names
- Call `check_playbook_drift()` — assert at least one PLAYBOOK_DRIFT finding returned
- Create a declaration with evidence_paths that DO mention a phase name
- Call `check_playbook_drift()` — assert no PLAYBOOK_DRIFT findings returned

**Output:** `tools/playbook/playbook_drift_checker.py`; `autonomous_cycle.py` drift check call; new tests.

---

### TC-PBHP-004 — Feedback: Wire Drift Findings into Sprint Synthesis (C3)
**Status:** OPEN
**Depends on:** TC-PBHP-003

**Problem:** Drift findings are written to `.local/supervisor/playbook-drift-findings.json` but `generate_supervisor_packet.py` does not read this file. The feedback loop is still open.

**File to modify:** `tools/supervisor/generate_supervisor_packet.py` — `synthesize_sprint_tasks()` function.

**Design:** When synthesizing tasks for the next sprint, check if `playbook-drift-findings.json` exists and has PLAYBOOK_DRIFT findings. For each finding, add a task item:
- `item_type: PLAYBOOK_DRIFT_FOLLOWUP`
- `title: "Playbook adherence followup: [work_item_id]"`
- `description: "[applicable_playbook] phases not evidenced in prior sprint"`
- `priority: LOW` (never displaces actual product work)

This closes the loop: drift in Sprint N → task added to Sprint N+1 → agent corrects the gap → evidence includes phase references → drift check passes.

**Read first:** Verify `synthesize_sprint_tasks()` actually controls which items go into `next-sprint.md` and how task priority interacts with other items. The function at lines 442-451 is what exploration described; read it fully before modifying.

**Non-blocking guard:** If `playbook-drift-findings.json` does not exist or is malformed, `synthesize_sprint_tasks()` continues with zero drift tasks. No exception propagates.

**Limit:** Adding PLAYBOOK_DRIFT_FOLLOWUP tasks will make `next-sprint.md` include remediation items. If drift is widespread (many playbooks, many unmatched phases), this could flood the sprint plan. The implementation should cap drift tasks at 3 per sprint and de-duplicate by `applicable_playbook` rather than by `work_item_id`.

**Test to add:** `test_supervisor_integration.py` — `test_drift_findings_produce_followup_tasks()`:
- Write a synthetic `playbook-drift-findings.json` to a temp directory
- Call `synthesize_sprint_tasks()` pointing to that temp directory
- Assert at least one PLAYBOOK_DRIFT_FOLLOWUP item appears in the returned task list

**Output:** Modified `synthesize_sprint_tasks()` in `generate_supervisor_packet.py`; new test.

---

### TC-PBHP-005 — Structural Hardening: CI Gate and V92 Escalation (C4, C5)
**Status:** OPEN
**Depends on:** TC-PBHP-001 (for baseline pass count)

**5a — Add `tests/playbook/` to CI**

File: `.github/workflows/ci.yml`

Add to `test-full` job (not `test-fast`):
```yaml
- name: Playbook test suite
  run: .venv/Scripts/pytest tests/playbook/ -q --tb=short
```

This is the regression control for TC-PBHP-002, TC-PBHP-003, TC-PBHP-004. Without it, the integration tests added in those taskcards do not run automatically.

**Risk:** If TC-PBHP-001 reveals tests failing at HEAD, those must be fixed before this CI step can be added without immediately breaking the build. That is a P0 finding from TC-PBHP-001.

**5b — Escalate V92 to blocking**

File: `tools/supervisor/governance_validators_ext2.py`

V92 detects ACTIVE registry entries pointing to nonexistent files. This is not drift — it is a broken reference that means the registry no longer reflects reality. It should block the sprint the same way other structural failures do.

Change V92's failure return from:
```python
"result": "WARN", "blocks_sprint": False,
```
to:
```python
"result": "FAIL", "blocks_sprint": True,
"summary": f"V92: {len(missing)} ACTIVE registry entry(s) reference nonexistent files — GOV_BLOCK",
```

PASS case unchanged. Tests: update TestV92 in `test_governance_validators.py` to assert `FAIL` and `blocks_sprint: True` for the file-not-found case.

**Risk:** A file rename without updating the registry now blocks the sprint. This is the correct behavior — the registry is broken, and the signal should be actionable.

**5c — Resolve validator count discrepancy (if found)**

From TC-PBHP-001: the actual defined validator count vs. claimed 167. If discrepant:
- Reduce `expected_count` to match actual count
- Create gap entries for any planned-but-unimplemented validators
- Add `test_expected_count_matches_actual()` to `test_governance_validators.py`

This test catches count drift in CI via `tests/supervisor/` which already runs.

**Output:** CI workflow change; updated V92; count correction if needed; new tests.

---

## Execution Order

```
TC-PBHP-001  (baseline — read-only, establishes true starting point)
     ↓
TC-PBHP-002  (forward channel — inject into next-sprint.md)
     ↓
TC-PBHP-003  (return check — drift detector, written independently)
     ↓
TC-PBHP-004  (feedback — wire drift into sprint synthesis)
     ↓
TC-PBHP-005  (CI + V92 — structural hardening, can run in parallel with 002-004)
```

TC-PBHP-005 is independent and can start immediately after TC-PBHP-001. TC-PBHP-002, 003, 004 are a chain (each depends on the prior).

---

## Loop Closure Verification

After all five taskcards close, the integration loop exists end-to-end. Prove it with one complete cycle:

1. Generate `next-sprint.md` for a sprint with `FORMAT_FEATURE_EXPANSION` work item → assert contains `## Playbook Guidance` section
2. Simulate a sprint where the agent does NOT mention any phase names in evidence → `check_playbook_drift()` returns at least one PLAYBOOK_DRIFT finding
3. Simulate `synthesize_sprint_tasks()` consuming that finding → next sprint plan contains a PLAYBOOK_DRIFT_FOLLOWUP item
4. Run the full test suite: `tests/playbook/` via CI step → zero failures

This is one end-to-end proof, not 8 separate pilots. The pilots in the prior certification proved tools in isolation. This verification proves the loop closes.

---

## What This Plan Does Not Do

**Deliberately out of scope:**

- **Does not modify the evidence schema.** `additionalProperties: false` is correct strict design. Adding playbook adherence fields would impose behavioral coupling on workers. The parallel drift check achieves the same goal without schema modification.

- **Does not add playbook adherence as a grading dimension.** The execution log is written after grading completes, making it structurally impossible to affect current-sprint grades without redesigning the grading flow. That is a larger change than this plan scope.

- **Does not implement apply mode.** Correctly gated pending S-F2F-06 risk review.

- **Does not call `generate_playbook_taskcards.py` from the supervisor.** The tool generates YAML taskcard documents, not sprint markdown. Incorporating its output into `next-sprint.md` requires a rendering step that is not yet designed.

- **Does not rewrite working tool implementations.**

- **Does not add value proof records or run idempotency pilots.** Those are documentation tasks. This plan addresses production behavior.

---

## Tradeoffs and Honest Limits

| Change | Tradeoff | Limit |
|--------|----------|-------|
| TC-PBHP-002 (injection) | Adds playbook dependency to `generate_supervisor_packet.py`; exception-isolated so non-blocking | Agent can still ignore the guidance — advisory only |
| TC-PBHP-003 (drift check) | String-membership phase detection: false negatives common | Signal is WARN only, never blocks; not a grading dimension |
| TC-PBHP-004 (feedback) | PLAYBOOK_DRIFT_FOLLOWUP tasks inflate sprint plans | Capped at 3 per sprint, de-duplicated by playbook |
| TC-PBHP-005b (V92 blocking) | File rename without registry update blocks sprint | Correct behavior; GOV_BLOCK resolves when registry updated |

**What this plan cannot achieve:** Guaranteed compliance with playbook phases. Agents can receive the guidance, see the phases in the sprint prompt, and still work ad-hoc. The drift check will detect this and create followup tasks, but enforcement requires a fundamentally different authority model (one that blocks sprints on incomplete phases, which conflicts with the Supreme Directive). This plan creates a feedback loop that drives consistency over time without enforcement.

**What "strong, consistent results across reruns" looks like after this plan:** Each sprint involving a known work item type (FORMAT_FEATURE_EXPANSION, etc.) receives the applicable playbook phases in its prompt. If the agent ignores them, a PLAYBOOK_DRIFT finding appears in the next sprint's priorities, making it visible and actionable. Over N sprints, drift findings trend toward zero as agents adapt. This is not enforcement — it is a self-correcting feedback loop.

---

## Critical Files

- `tools/supervisor/generate_supervisor_packet.py` — TC-PBHP-002 (forward channel), TC-PBHP-004 (feedback)
- `tools/supervisor/autonomous_cycle.py` — TC-PBHP-003 (drift check call site)
- `tools/playbook/playbook_drift_checker.py` — TC-PBHP-003 (new file)
- `tools/supervisor/governance_validators_ext2.py` — TC-PBHP-005 (V92)
- `.github/workflows/ci.yml` — TC-PBHP-005 (CI gate)
- `tests/playbook/test_supervisor_integration.py` — all integration regression tests
- `tests/supervisor/test_governance_validators.py` — V92 test update, count test

---

## Regression Controls

After plan closes, the following tests run on every commit:

| Test | What it catches |
|------|----------------|
| `test_supervisor_integration.py::test_next_sprint_md_includes_playbook_context` | TC-PBHP-002 regression |
| `test_supervisor_integration.py::test_drift_check_detects_missing_phases` | TC-PBHP-003 regression |
| `test_supervisor_integration.py::test_drift_findings_produce_followup_tasks` | TC-PBHP-004 regression |
| `test_governance_validators.py::TestV92::test_fail_blocks_when_file_missing` | TC-PBHP-005b regression |
| `test_governance_validators.py::test_expected_count_matches_actual` | Validator count drift |
| CI: `pytest tests/playbook/ -q` | Any regression in 217 playbook tool tests |
