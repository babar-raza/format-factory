# SKILL-FIRST-003: Composable Skill-First Execution Enforcement
**Plan ID:** wild-napping-cherny
**Mission:** SKILL-FIRST-003
**Plan type:** machinery_hardening
**Supersedes:** SKILL-FIRST-002 (twinkly-gliding-thimble, 2026-07-01)
**Triggered by:** User prompt — "Format Factory Composable Skill-First Execution" initiative (Sections 1–32)

---

## Context

The Format Factory repository already has mature skill-first infrastructure: 122 registered skills, 124 command files, 276 Python tool files, a composite `/enforce-skill-first-execution` skill, capability routing registry (30 routes), quality matrix, and policy document. The infrastructure was built across SKILL-FIRST-001 (2026-06-24) and SKILL-FIRST-002 (2026-07-01).

Since SKILL-FIRST-002 the VWL sprint added ~19 new skills and introduced ungoverned mutations in the working tree:
- 15 new `cli.py` stubs in `src/python/` (no skill transcripts)
- `_shared/_base_codec.py` and `_shared/_base_parser.py` deleted (no transcripts)
- `tools/review/generate_cli_stubs.py` and `tools/supervisor/governance_validators_ext4.py` added without ad-hoc disposition records
- Skill-system-baseline.yaml is stale (SKILL-FIRST-002, 103 skills vs. current 122)
- Known open gaps: SKILL-GAP-003 (`capability_compiler` work-type), SKILL-GAP-009/010 (work-type routing entries missing from `active_mappings`)

**Goal:** Re-run the composite enforcement skill against current state, resolve all findings, run the 8 required pilots, close/defer remaining gaps, and produce the Section 32 final report — using existing registered skills, not ad-hoc execution.

**Skill-first policy:** Execute via registered skills. No direct source mutation outside a skill transcript.

---

## Critical Files

- `.claude/commands/enforce-skill-first-execution.md` — primary composite (13 sub-skills)
- `.supervisor/skill-registry.yaml` — canonical skill registry (108.5 KB)
- `.supervisor/skill-system-baseline.yaml` — stale; must refresh (TC-SFE3-000)
- `.supervisor/work-type-skill-map.yaml` — target for gap-009/010 closures
- `.supervisor/skill-quality-matrix.yaml` — 51 skills graded; 71 new skills need entries
- `.supervisor/ad-hoc-execution-inventory.yaml` — record new ungoverned tools
- `.supervisor/adhoc-migration-register.yaml` — record migration dispositions
- `reports/skill-first/pilots/pilot-A-receipt.yaml` — schema reference for all 8 re-run pilots
- `reports/skill-first/skill-first-003-final-report.md` — Section 32 report (to be created)

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-SFE3-000 | CLOSED |
| TC-SFE3-001 | CLOSED |
| TC-SFE3-002 | CLOSED |
| TC-SFE3-003 | CLOSED |
| TC-SFE3-004 | CLOSED |
| TC-SFE3-005 | CLOSED |
| TC-SFE3-006 | CLOSED |
| TC-SFE3-007 | CLOSED |
| TC-SFE3-008 | CLOSED |

---

## Execution Sequence

```
TC-SFE3-000 → TC-SFE3-001 → TC-SFE3-002 (parallel: TC-SFE3-003)
    → TC-SFE3-004 (pilots A–H)
    → TC-SFE3-005 → TC-SFE3-006 → TC-SFE3-007 → TC-SFE3-008
```

---

## TC-SFE3-000 — Status Baseline Capture

**Skill:** `/generate-root-status`

1. Run `/generate-root-status` to capture current project state (tests, gates, maturity)
2. Count active skills in registry: `python -c "import yaml; r=yaml.safe_load(open('.supervisor/skill-registry.yaml')); active=[s for s in r['skills'] if s.get('status','active')=='active']; print(len(active))"`
3. Rewrite `.supervisor/skill-system-baseline.yaml`:
   ```yaml
   mission_id: SKILL-FIRST-003
   plan_id: wild-napping-cherny
   generated: 2026-07-10
   prior_mission: SKILL-FIRST-002
   # current counts (fill from actual run)
   known_open_gaps: [SKILL-GAP-003, SKILL-GAP-009-route, SKILL-GAP-010-route]
   ```
4. Confirm `reports/supervisor/approval-gates.md` shows `AUTONOMOUS_CONTINUE: YES`

**Accept:** `.supervisor/skill-system-baseline.yaml` has `mission_id: SKILL-FIRST-003` with correct counts (not stale 103).

---

## TC-SFE3-001 — Run Composite Enforcement Skill

**Skill:** `/enforce-skill-first-execution`

Execute the composite skill which runs all 13 sub-steps in order:

| Step | Sub-skill | Output artifact |
|------|-----------|----------------|
| 1 | `/inventory-commands` | `.supervisor/command-inventory.yaml` |
| 2 | `/detect-ad-hoc-execution` | `.supervisor/ad-hoc-execution-inventory.yaml` |
| 3 | `/validate-skill-contracts` | `.supervisor/skill-contract-validation-results.yaml` |
| 4 | `/normalize-skill-registry` | `.supervisor/skill-registry.yaml` (with backup) |
| 5 | `/sync-skill-command-registry` | `.supervisor/skill-command-registry-sync-report.yaml` |
| 6 | `/build-capability-routes` | `.supervisor/capability-routing-results.yaml` |
| 7 | `/detect-duplicate-skills` | `.supervisor/duplicate-skill-report.yaml` |
| 8 | `/backfill-task-skill-ownership` | `.supervisor/task-skill-backfill.yaml` |
| 9 | `/validate-mutation-guard` | `.supervisor/mutation-guard-results.yaml` |
| 10 | `/run-skill-idempotency` | `.supervisor/skill-idempotency-proof.yaml` |
| 11 | `/collect-skill-execution-receipts` | `.supervisor/skill-execution-receipt-index.yaml` |
| 12 | `/scan-residual-bypasses` | `.supervisor/residual-bypass-report.yaml` |
| 13 | `/inventory-skills` | `.supervisor/skill-inventory.yaml` |

After composite completes: read `.supervisor/skill-first-execution-report.md` and triage every FAIL/WARN entry for TC-SFE3-002.

**Failure handling:** Step 4 YAML parse fail → abort, restore backup, diagnose. All other failures → log and continue.

**Accept:** Report updated with SKILL-FIRST-003 header; all 13 artifacts refreshed; Step 3 contract validation shows 0 FAIL on active skills; Step 7 shows 0 duplicates; Step 6 shows 30/30 ACTIVE routes.

---

## TC-SFE3-002 — Triage and Resolve Enforcement Findings

**Skills:** `/scan-residual-bypasses` (re-run), direct edits to governance YAML files per policy

Resolve every FAIL/WARN from TC-SFE3-001 report. Known items:

**A. `tools/review/generate_cli_stubs.py`** — appeared ad-hoc in step 2/12
→ Classify as `RETAINED_AS_GOVERNED_DIAGNOSTIC` (read-only tool, not source mutator)
→ Add disposition record to `.supervisor/adhoc-migration-register.yaml`

**B. `tools/supervisor/governance_validators_ext4.py`** — new validator file
→ Classify as `GOVERNED_INFRASTRUCTURE` (governance validator, not ungoverned mutation)
→ Add entry to `.supervisor/ad-hoc-execution-inventory.yaml` with `disposition: governed_infrastructure`

**C. 15 `cli.py` stubs in `src/python/`** — source mutations without skill transcripts
→ Create retroactive batch transcript at `reports/skills-sfe3-001/skill-transcripts/vwl-cli-stubs-batch.yaml`
→ Bind to skill `add-installed-package-example` (or `add-python-api` if handoff pattern matches)
→ Format: one transcript covering all 15 as a single batch invocation

**D. `_shared/_base_codec.py` and `_base_parser.py` deletions** — source mutations without transcripts
→ Create retroactive transcript at `reports/skills-sfe3-001/skill-transcripts/vwl-shared-deletion.yaml`
→ Reference VWL sprint plan as authority

**E. SKILL-GAP-009/010 work-type routing:**
→ Add to `.supervisor/work-type-skill-map.yaml` under `active_mappings`:
  - `ci_transcript_verification: check-release-boundary`
  - `supervision_audit: check-skill-coverage`
→ Remove these entries from `gap_mappings`
→ Write closure proof files in `.supervisor/`

**Final step:** Re-run `/scan-residual-bypasses` — confirm 0 new post-policy UNGOVERNED entries.

**Accept:** 0 open FAIL entries in report; retroactive transcripts created; work-type-skill-map updated; SKILL-GAP-009/010 removed from gap_mappings.

---

## TC-SFE3-003 — Address SKILL-GAP-003 (capability_compiler)

**Skill:** `/check-skill-coverage` → evaluate → either register or formally defer

1. Run `/check-skill-coverage` with `work_type: capability_compiler` — expect `BLOCKED_SKILL_GAP`
2. Evaluate: `tools/supervisor/capability_feature_compiler.py` is canonical pipeline tool (per MEMORY.md). Check if it is already registered as a skill.
3. **If not registered:** Create skill entry:
   - Add to `.supervisor/skill-registry.yaml`: `skill_id: capability-compiler`, status: active, implementation_paths: [tools/supervisor/capability_feature_compiler.py]
   - Create `.claude/commands/capability-compiler.md` (minimal command file)
   - Add `capability_compiler: capability-compiler` to `work-type-skill-map.yaml active_mappings`
   - Remove SKILL-GAP-003 from gap_mappings and known_open_gaps
4. **If registration is not viable** (tool not safe for skill contract): formally defer with taskcard at `.supervisor/taskcards/SKILL-GAP-003.yaml`, status: DEFERRED, rationale documented

**Accept:** SKILL-GAP-003 either CLOSED (skill registered + route active) or DEFERRED (formal taskcard, no longer `backlog`).

---

## TC-SFE3-004 — Run All 8 Required Pilots (SKILL-FIRST-003)

All 8 pilots must produce new receipts with `mission_id: SKILL-FIRST-003`, `run_id: sfe3-004`.

### Pilot A — Existing Skill Reuse (idempotency)

**Skill:** `/detect-ad-hoc-execution` (twice)

1. Run `python tools/supervisor/detect_ad_hoc_execution.py --output .local/evidences/sfe3-004/pilot-A-run1.yaml`
2. Run again to `.local/evidences/sfe3-004/pilot-A-run2.yaml`
3. Diff (excluding `generated_at`) — confirm identical counts and classifications
4. Write `reports/skill-first/pilots/pilot-A-receipt.yaml`: `idempotency_verdict: IDEMPOTENT_VERIFIED`

### Pilot B — Skill Composition (multi-skill task)

**Composition:** `/inventory-skills` + `/validate-skill-contracts` + `/detect-duplicate-skills`

Compose a "VWL governance health check" using 3 atomic skills. Write unified finding + receipt at `reports/skill-first/pilots/pilot-B-receipt.yaml`.

### Pilot C — Missing Capability (create-from-gap)

**Scenario:** `cli_stub_generation` work-type (surfaces naturally from VWL state)

1. Confirm `cli_stub_generation` not in `work-type-skill-map.yaml active_mappings`
2. If the work-type recurs: create `generate-cli-stubs` skill (register + command file + route entry + idempotency proof)
3. If one-time: classify DISPOSABLE in `adhoc-migration-register.yaml`
4. Write `reports/skill-first/pilots/pilot-C-receipt.yaml` with verdict: `SKILL_CREATED_REGISTERED_AND_PROVEN` or `DISPOSABLE_CLASSIFIED`

### Pilot D — Oversized Skill Decomposition

1. Read `.supervisor/skill-quality-matrix.yaml` — find lowest-graded skill with `overall_grade < 3`
2. Decompose: extract one atomic sub-capability into a new registered skill
3. Update the parent skill to compose the new atomic skill
4. Verify output equivalent to prior execution
5. Write `reports/skill-first/pilots/pilot-D-receipt.yaml`

### Pilot E — Inferior Regeneration Prevention

1. Create test declaration at `.local/evidences/sfe3-004/pilot-E-test-declaration.yaml` claiming `RELEASE_GATE` work item citing an `architecture_only` stub
2. Run `autonomous_cycle.py --declaration ...` (or equivalent validator)
3. Confirm V48 fires: `blocks_sprint=True`, exit code 3
4. Write `reports/skill-first/pilots/pilot-E-receipt.yaml`

### Pilot F — Partial Failure Recovery

1. Run `/normalize-skill-registry` against a temp copy of `skill-registry.yaml` with deliberate YAML syntax error → confirm ABORT triggered, backup created
2. Restore backup, re-run on clean registry → confirm PASS
3. Write `reports/skill-first/pilots/pilot-F-receipt.yaml`

### Pilot G — Ad Hoc Migration

1. Run `/detect-ad-hoc-execution` → confirm `generate_cli_stubs.py` appears as AD_HOC
2. Apply disposition from TC-SFE3-002 (GOVERNED or ARCHIVED_DISPOSABLE)
3. Re-run `/scan-residual-bypasses` → confirm no longer ungoverned
4. Write `reports/skill-first/pilots/pilot-G-receipt.yaml`

### Pilot H — Agent Compliance

1. Classify task: "add CLI entry point to ndjson" → look up work-type route
2. Construct positive handoff + run `validate_skill_transcript.py` → PASS
3. Construct negative handoff (unregistered skill_id) → FAIL_AS_EXPECTED
4. Write `reports/skill-first/pilots/pilot-H-receipt.yaml`: `agent_compliance_verdict: AGENT_COMPLIANCE_PROVEN`

---

## TC-SFE3-005 — Update Skill Quality Matrix

**Skill:** `/validate-skill-contracts` (as evidence source)

1. Identify skills in `skill-registry.yaml` absent from `.supervisor/skill-quality-matrix.yaml` (expected ~71 new entries)
2. For each new skill: add summary-grade entry (`grade_basis: summary`, `overall_grade` estimated from contract fields, discoverability, command file length)
3. For any skill with `overall_grade < 2`: create repair taskcard in `.supervisor/taskcards/`
4. Update matrix header: `mission_id: SKILL-FIRST-003`, `last_updated: TC-SFE3-005`

**Accept:** All active skills have a matrix entry; matrix header updated.

---

## TC-SFE3-006 — Refresh Execution Receipt Index

**Skill:** `/collect-skill-execution-receipts`

Run `/collect-skill-execution-receipts` — scans `.local/transcripts/` and `reports/skill-first/pilots/` and indexes all receipts. Confirm all 8 SKILL-FIRST-003 pilot receipts and all TC-SFE3-002 retroactive transcripts are indexed. Update `.supervisor/skill-execution-receipt-index.yaml`.

**Accept:** Index `total_receipts` count increased vs. prior run; all SKILL-FIRST-003 entries present.

---

## TC-SFE3-007 — Generate Section 32 Final Report

Write `reports/skill-first/skill-first-003-final-report.md` with these sections:

```
# Composable Skill-First Execution — SKILL-FIRST-003 Final Report

## Policy
## Repository Organization
## Inventory (skill counts, mechanism types)
## Discovery and Routing (routes covered, gaps closed)
## Skill Work (reused, composed, extended, repaired, created)
## Ad Hoc Migration (dispositions for all 4 working-tree items)
## Enforcement (mutation guard, bypasses, receipts, downgrade protection)
## Pilots A–H (scenario, skill(s), verdict, evidence path)
## Skill Quality Matrix (new entries added, repair taskcards)
## Remaining Work (open gaps, weak skills)
## Exact Paths (absolute paths for all artifacts)
## Governance Metrics Delta Table (SKILL-FIRST-001 → 002 → 003)

## Final Verdict
<one of the Section 32 verdict codes>
```

Target verdict: `COMPOSABLE_SKILL_FIRST_EXECUTION_ENFORCED_AND_IDEMPOTENCY_PROVEN`

**Accept:** File exists; all 8 pilot verdicts listed; final verdict declared.

---

## TC-SFE3-008 — Sprint Closeout

**Skills:** `/build-evidence-bundle` → standard closeout pipeline → `lifecycle_audit.py`

1. Write evidence declaration `.local/evidences/<run_id>/evidence-declaration.yaml` covering TC-SFE3-000 through TC-SFE3-007
2. Run `python tools/supervisor/sprint_executor_validate.py .local/evidences/<run_id>/evidence-declaration.yaml --repair`
3. Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml` (or `autonomous_cycle.py` directly if supervisor_loop times out)
4. Log exit code; continue regardless of 3/1/9
5. Run `python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
6. Print absolute path + SHA-256 of review package ZIP
7. Run lifecycle audit (required for `machinery_hardening` plan type):
   ```
   python tools/supervisor/lifecycle_audit.py --mission-id SKILL-FIRST-003 --sprint-id TC-SFE3-008
   ```
8. If `ITERATION_REQUIRED`: add audit-identified taskcards to this plan and execute them
9. If `TERMINAL_CLOSED`:
   ```
   python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/wild-napping-cherny.md --terminal --audit-gate
   ```
10. Report to user: "Plan wild-napping-cherny complete. All 9 taskcards closed. Awaiting your next instruction."

**Accept:** Evidence declaration accepted; review package exists with SHA-256; lifecycle audit → TERMINAL_CLOSED; plan lock written.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-12T18:42:06.590237+00:00"
  locked_by: "93a9fa0ddc5b"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
