# Supervisor-Worker Contract

## Overview

The supervisor and worker operate in the same repo/worktree. Communication is file-based: the worker writes evidence, the supervisor inspects it.

## Worker Obligations

1. **Execute work** described in the next-worker prompt or human instruction.
2. **Write evidence directory** under `.local/evidences/<run_id>/`.
3. **Write `evidence-declaration.yaml`** with all required fields (see schema).
4. **Declare all work items** with item_id, title, status, evidence_paths, tests_supporting, acceptance_criteria.
5. **Only claim `completed`** when evidence exists at declared paths and tests pass.
6. **Use `partial`** when work is in progress but not finished.
7. **Use `blocked_external_gate`** when an external approval or resource blocks completion.
8. **Run tests** and record results in declaration (`tests_run`, `test_results`).
9. **Push and publish** follow SCM Agent policy (AGENTS.md §AG4): commit when sprint policy authorizes; push when credentials and branch policy allow. Classify EXTERNAL_BLOCKER when credentials absent. Gate approval: Gates 1-10 use evidence-backed policy gates (AGENTS.md §AG5). Gate 11 G11-G: sole TRUE_EXTERNAL_GATE (Babar Raza).

## Supervisor Obligations

1. **Validate** the declaration schema and check all declared paths exist.
2. **Inspect** each declared evidence artifact.
3. **Grade each work item** independently using the 8-level rubric.
4. **Return rework** for failed/incomplete/overclaimed items.
5. **Issue forward work** from the master plan (product-factory targets).
6. **Generate next-worker prompt** with all 8 required sections.
7. **Write review outputs** to `.local/supervisor/reviews/<run_id>/`.
8. **Copy latest summaries** to `reports/supervisor/latest-*.md`.
9. **Set exit code** correctly (0=success, 3=critical rework, 1=invalid, 9=error).

## Declaration Required Fields

| Field | Type | Description |
|-------|------|-------------|
| run_id | string | Unique run identifier |
| sprint_id | string | Sprint identifier |
| evidence_root | string | Path to evidence directory |
| start_time / end_time | string | ISO timestamps |
| git_head_start / git_head_end | string | Commit SHAs |
| git_status_final | string | Git status at end |
| declared_scope | string | What the sprint intended |
| planned_work_items | array | All work items with evidence |
| completed_work_items | array | Item IDs completed |
| incomplete_work_items | array | Item IDs not completed |
| changed_files | array | Files created or modified |
| tests_run | integer | Total tests executed |
| test_results | object | passed/failed/skipped/errors |
| evidence_artifacts | array | Paths to evidence files |
| reports_created | array | Report file paths |
| worker_self_verdict | string | Worker's assessment |
| worker_self_grade | string | PASS/PARTIAL/FAIL/BLOCKED |
| next_recommended_work | array | Suggested next tasks |

## spec_fact_refs (required-or-explain, SAL-HEAL-A001 2026-06-25)

For every `PRODUCT_SOURCE`, `READINESS`, or `RELEASE_GATE` work item, EITHER:

**Option A — Tier 1 formats** (formats with accessible formal specifications: fods, fodt, ods, odt, fodg, fodp, zst, pbm, pgm, ppm, csv, ndjson, toml, xcf, qoi):
- Provide at the **work item level**: `spec_fact_refs: ["FACT-{FORMAT}-NNN"]`
- IDs must exist in `.local/sal-output/sal-facts-latest.json`
- Example: `spec_fact_refs: ["FACT-FODS-001", "FACT-FODS-004"]`

**Option B — Tier 2 formats** (no public spec or schema-only: gnumeric, abw, sylk, dif, tsv):
- Provide at the **work item level**: `exception_classification: {valid_value}`
- Valid values: `no_public_spec_available`, `schema_authority_available`, `legacy_backfill`, `investigation_only`, `fallback_authority_approved`, `sample_only_non_product`

**Omitting both** is a HARD BLOCK (V13 gate fires, blocks_sprint=True).

**TC-GUARD-001 AND rule** (SAL-HEAL-A001): Every `PRODUCT_SOURCE`/`PRODUCT_TEST` item must have BOTH:
- A gap reference: `gap_ledger_ref` OR `capability_ref`
- Spec authority: `spec_fact_refs` OR `exception_classification` (at work item level)

`gap_ledger_ref` alone is no longer sufficient for TC-GUARD-001 (upgraded 2026-06-25).

## Work Item Status Values

| Status | Meaning |
|--------|---------|
| completed | Done, evidence exists, tests pass |
| partial | In progress, some evidence may exist |
| not_started | Not attempted |
| blocked_external_gate | Blocked by external approval or resource |

## Violation Consequences

- **OVERCLAIMED**: Worker declares `completed` but no evidence exists at declared paths. Triggers critical rework. Autonomous continuation blocked.
- **REJECTED**: Evidence exists but is fundamentally wrong. Triggers critical rework.
- **REWORK_REQUIRED**: Evidence incomplete or tests failing. Non-critical but must be addressed.

## ZIP Policy

ZIP is NOT required. ZIP is only used for:
- External upload or transfer
- Archival
- Delivery-package inspection
- Cross-machine transfer

The declaration-driven loop works without ZIP.

## Autonomous Loop Integration

This contract operates within the autonomous supervision loop. After the worker writes `evidence-declaration.yaml` and the supervisor grades it:

1. If all items are ACCEPTED (exit 0), the supervisor generates a new `next-sprint.md` with forward work
2. The worker reads `next-sprint.md` as its next sprint prompt and repeats the cycle
3. This continues until `max_iterations` is reached or a hard stop is encountered

The worker is **stateless** — it does not need memory of prior sprints. All state is carried by:
- `reports/supervisor/session-resume.md` (last sprint outcome)
- `reports/supervisor/approval-gates.md` (YES/NO continuation)
- `reports/supervisor/next-sprint.md` (work items)
- `.local/supervisor/continuation-signal.json` (iteration counter)

For the full replication guide, see:
[Autonomous Supervision — Replication Guide](autonomous-supervision-replication-guide.md)

---

## Common LLM Downgrade Patterns (with remediation)

The LLM semantic verification layer reads actual evidence file content and can downgrade grades. The following patterns have been observed to cause downgrades across multiple sprints:

### Pattern W0: Preflight items without verifiable iteration proof

**Symptom:** REWORK_REQUIRED for a preflight item like `W0-PREFLIGHT`.

**Root cause:** The LLM reads `continuation-signal.json` and checks:
1. Whether `iteration` in the signal matches the sprint being declared
2. Whether `autonomous_continue` is truthy
3. Whether any test code or automated verification is cited

**Remediation options:**
- **Option A (preferred):** Use `item_type: GOVERNANCE_DOC` for preflight items. This auto-exempts the item from LLM adequacy checks. Example:
  ```yaml
  - item_id: W0-PREFLIGHT
    title: "Verify continuation signal"
    status: completed
    item_type: GOVERNANCE_DOC
    exemption_reason: "Read-only preflight check: confirmed autonomous_continue=true"
    evidence_paths:
      - .local/supervisor/continuation-signal.json
      - reports/supervisor/approval-gates.md
  ```
- **Option B:** Include a path to the actual `continuation-signal.json` so the LLM can verify the iteration number directly.

**Anti-overclaim rule:** Do NOT adjust the grader to accept missing verification — provide the proof.

---

### Pattern W2: Generator items with insufficient candidate count

**Symptom:** REWORK_REQUIRED for task generator items like `W2-CANDIDATES`.

**Root cause:** The LLM counts tasks in `product-task-candidates.json` and compares to the declared sprint goal count. If the file has fewer tasks than claimed, it flags as inadequate.

**Remediation:** Run `autonomous_task_generator.py` AFTER adding all expansion goals. Verify `total_candidates` in the output equals the sprint target. Do NOT declare the generator item complete until the JSON reflects the correct count.

**Checklist before declaring complete:**
```bash
python tools/supervisor/autonomous_task_generator.py --verify
# Output should show: total_candidates = <N> (where N matches sprint plan)
```

---

### Pattern W13: Full-suite verification items with log-file-only evidence

**Symptom:** ACCEPTED_WITH_LIMITATIONS (ceiling) for full-suite verification items.

**Root cause:** The `tests_supporting` population logic looks for evidence paths matching `*test_*.py`. A `.log` file does not match, so `tests_supporting` stays empty, and the item cannot reach `ACCEPTED_VERIFIED`.

**Remediation:** Always cite the individual test files in `evidence_paths`, not only the log file. The log is supplementary, not primary evidence.

**Correct pattern:**
```yaml
- item_id: W13-FULL-SUITE
  title: "Run targeted tests to confirm all Sprint N tests pass"
  status: completed
  exemption_reason: "Verification item: N targeted tests pass"
  evidence_paths:
    - tests/python/abw/test_r148_abw_word_wrap.py
    - tests/python/abw/test_r148_abw_has_paragraph.py
    - tests/python/gnumeric/test_r148_gnumeric_get_all_values.py
    # ... all test files that were run
    - .local/evidences/<run_id>/sprint-targeted-tests.log  # supplementary
```

**Anti-overclaim rule:** Do NOT add `.log` file matching to the `tests_supporting` logic — log files are weaker evidence than test code and the ceiling is intentional.

---

---

## EVIDENCE SCHEMA RULE (mandatory — TC-INFRA-DEC-001)

**The grader computes `has_evidence` per work item by reading `planned_work_items[].evidence_paths`.
It does NOT read `evidence_artifacts[].related_work_items` for this computation.**

For each work item:
- `planned_work_items[].evidence_paths` → list of file paths the grader checks for existence on disk → drives `has_evidence`
- `evidence_artifacts[].related_work_items` → manifest materialization only (human-readable, LLM context) → does NOT affect `has_evidence`

**If a work item's `evidence_paths` list is absent or empty AND status is `completed`, the grader returns OVERCLAIMED.**

### Required pattern (correct):

```yaml
planned_work_items:
  - item_id: TC-MY-001
    title: "My task"
    status: completed
    evidence_paths:                         # ← grader reads THIS for has_evidence
      - path/to/evidence-file.md
      - path/to/source-file.py
    tests_supporting:
      - tests/python/myformat/test_feature.py

evidence_artifacts:                         # ← supplemental; LLM context only
  - path: path/to/evidence-file.md
    type: proof_document
    description: "Describes what the file proves"
    related_work_items:
      - TC-MY-001
```

### Anti-pattern (causes OVERCLAIMED):

```yaml
planned_work_items:
  - item_id: TC-MY-001
    status: completed
    # NO evidence_paths here ← grader sees has_evidence=false → OVERCLAIMED

evidence_artifacts:
  - path: path/to/evidence-file.md
    related_work_items:
      - TC-MY-001           # ← this field is NOT checked by has_evidence logic
```

**Root cause of OVERCLAIMED verdicts (documented 2026-06-22):** Workers historically used
`evidence_artifacts[].related_work_items` as the sole evidence linkage, believing it was
equivalent to per-item `evidence_paths`. It is NOT. The grader's `inspect_item()` function
(in `inspect_declared_evidence.py`) reads `item.get("evidence_paths", [])` from the
`planned_work_items` dict entry. The `evidence_artifacts` array is populated in the manifest
for human review but is not traversed for per-item `has_evidence`.

---

## AGGREGATE TESTS_RUN RULE (mandatory — TC-INFRA-DEC-002)

**The grader and `session-resume.md` read the top-level aggregate fields ONLY.**
Per-item narrative strings (e.g., "13 passed in 1.72s") are for human context only and
are ignored by all automated consumers.

### Required: populate the top-level aggregate before submitting

```yaml
tests_run: 16          # sum of ALL test counts from ALL work items in this sprint
test_results:
  passed: 16           # sum of all per-item pass counts
  failed: 0            # sum of all per-item fail counts
  skipped: 0
  errors: 0
```

### Anti-pattern (causes misreported results):

```yaml
tests_run: 0           # ← grader and session-resume.md see "0 tests run"
test_results:
  passed: 0            # ← even if per-item tests actually ran and passed
planned_work_items:
  - item_id: TC-MY-001
    # per-item test note here is IGNORED by all automated consumers
```

**Rule:** Before submitting a declaration, sum all per-item test counts into the top-level
aggregate. A sprint that runs 13 tests but declares `tests_run: 0` will appear as having
run no tests in grading history and `session-resume.md`.

**Validation:** Run `python tools/supervisor/sprint_executor_validate.py <declaration> --repair`
which emits a WARNING when `tests_run == 0` but per-item `evidence_paths` or inline test
result strings are present, suggesting a forgotten aggregate population.

---

## Lane Execution Ledger

The pipeline anti-skip checker requires `lane-execution-ledger.json` in `evidence_root` to confirm which lanes were executed. Running `evidence_auto_packager.py` automatically generates this file from your declared work items.

**Auto-generation (TC-B4):** As of 2026-06-11, calling `evidence_auto_packager.py pack()` writes `lane-execution-ledger.json` to `evidence_root` automatically — no manual step required.

**Manual format** (if not using `evidence_auto_packager.py`):
```json
{
  "lanes": [
    {"lane_id": "SUPERVISOR_TOOL", "items": ["W1", "W2", "W3"], "status": "COMPLETED"},
    {"lane_id": "PRODUCT_SOURCE", "items": ["W4", "W5"], "status": "COMPLETED"}
  ],
  "generated_by": "worker"
}
```
