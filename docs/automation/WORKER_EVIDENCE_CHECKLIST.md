# Worker Evidence Checklist

Use this checklist before writing `evidence-declaration.yaml` and running `autonomous-cycle`.
It prevents the most common LLM downgrade patterns observed across 12+ sprints.

---

## Before Declaring Any Item `completed`

- [ ] Evidence files exist at every declared `evidence_paths` location
- [ ] Tests pass: `test_results.failed == 0`
- [ ] If the item has NO test evidence AND no `exemption_reason`, the LLM will likely flag it as inadequate
- [ ] If `evidence_paths` contains ONLY `.log` files: grade capped at ACCEPTED_WITH_LIMITATIONS (cite test files too)

---

## Preflight Items (W0-PREFLIGHT pattern)

Items that verify pipeline state (continuation signal, approval gates) are commonly downgraded.

**Before declaring complete, verify:**
- [ ] Use `item_type: GOVERNANCE_DOC` OR provide a path to the actual `continuation-signal.json`
- [ ] Add `exemption_reason` explaining why no test code exists for this item
- [ ] The iteration number in `continuation-signal.json` matches the sprint being declared

**Correct pattern:**
```yaml
- item_id: W0-PREFLIGHT
  title: "Verify continuation signal and approval-gates (iter N)"
  status: completed
  item_type: GOVERNANCE_DOC
  exemption_reason: "Read-only preflight: confirmed autonomous_continue=true (iteration N)"
  evidence_paths:
    - .local/supervisor/continuation-signal.json
    - reports/supervisor/approval-gates.md
  test_results: {passed: 0, failed: 0, skipped: 0, errors: 0}
```

**Failure mode (W0-PREFLIGHT REWORK_REQUIRED):**
- Missing `exemption_reason` + no test evidence → LLM flags as inadequate
- Iteration mismatch between declaration claim and actual signal file
- `autonomous_continue: false` in signal while claiming "YES"

---

## Generator Items (W2-CANDIDATES pattern)

Items that produce task candidate files are commonly downgraded when the file count is wrong.

**Before declaring complete, verify:**
- [ ] Run `autonomous_task_generator.py` AFTER adding all expansion goals
- [ ] Open `product-task-candidates.json` and count actual tasks = sprint target count
- [ ] `total_candidates` in the JSON equals the number of tasks you intend to implement

**Verification command:**
```bash
python -c "import json; d=json.load(open('product-task-candidates.json')); print(f'total_candidates: {d[\"total_candidates\"]}')"
```

**Failure mode (W2-CANDIDATES REWORK_REQUIRED):**
- Task generator run before expansion goals were added → file has fewer tasks than claimed
- LLM counts tasks in the file and detects the deficit directly

---

## Full-Suite Verification Items (W13-FULL-SUITE pattern)

Items that prove a full test suite run are capped at ACCEPTED_WITH_LIMITATIONS if evidence_paths contains only log files.

**Before declaring complete:**
- [ ] List the individual test files (not just the log) in `evidence_paths`
- [ ] The log file is supplementary — include it too, but it must not be the only evidence

**Correct pattern:**
```yaml
- item_id: W13-FULL-SUITE
  title: "Run targeted tests to confirm all N Sprint tests pass"
  status: completed
  exemption_reason: "Verification item: N targeted tests pass; log at <run_id>/sprint-tests.log"
  evidence_paths:
    - tests/python/abw/test_r148_abw_word_wrap.py
    - tests/python/abw/test_r148_abw_has_paragraph.py
    # ... all test files that were run
    - .local/evidences/<run_id>/sprint-tests.log   # supplementary only
  test_results: {passed: N, failed: 0, skipped: 0, errors: 0}
```

**Failure mode (W13 ceiling):**
- `evidence_paths: [".local/evidences/<run_id>/sprint-tests.log"]` only → no `/test_` match → ACCEPTED_WITH_LIMITATIONS

---

## Lane Execution Ledger

The pipeline checks for `lane-execution-ledger.json` in `evidence_root`.

**Auto-satisfied:** Running `evidence_auto_packager.py` writes this file automatically.

**Manual (if not using auto-packager):**
```bash
cat > .local/evidences/<run_id>/lane-execution-ledger.json << 'EOF'
{
  "lanes": [
    {"lane_id": "SUPERVISOR_TOOL", "items": ["W0","W1","W2"], "status": "COMPLETED"},
    {"lane_id": "PRODUCT_SOURCE", "items": ["W3","W4"], "status": "COMPLETED"}
  ],
  "generated_by": "worker"
}
EOF
```

---

## Sprint Closeout Sequence

```bash
# 1. Write evidence directory
mkdir -p .local/evidences/<run_id>

# 2. Run tests and capture results
.local/venv/Scripts/python -m pytest tests/python/<format>/ -v 2>&1 | tee .local/evidences/<run_id>/test-run.log

# 3. Write evidence-declaration.yaml (manually or via auto-packager)
.local/venv/Scripts/python tools/supervisor/evidence_auto_packager.py \
  --sprint-id <sprint_id> --run-id <run_id> \
  --evidence-root .local/evidences/<run_id> \
  --output .local/evidences/<run_id>/evidence-declaration.yaml

# 4. Run autonomous-cycle
.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml

# 5. Build and report review package (MANDATORY)
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Quick Reference: Grade Ceiling by Evidence Type

| Evidence type | Grade ceiling |
|---|---|
| No evidence paths | OVERCLAIMED |
| Paths exist, tests failing | REWORK_REQUIRED |
| Paths exist, no test code, no exemption | ACCEPTED_WITH_LIMITATIONS |
| Log file only (no test_*.py) | ACCEPTED_WITH_LIMITATIONS |
| Test files cited, tests passing | ACCEPTED_VERIFIED (if LLM adequate) |
| `item_type: GOVERNANCE_DOC` | ACCEPTED (exempt from LLM adequacy) |

---

## References

- [Supervisor-Worker Contract](supervisor-worker-contract.md) — full field list and grade rubric
- [Autonomous Supervision Guide](autonomous-supervision-replication-guide.md) — architecture and loop
- `tools/supervisor/evidence_auto_packager.py` — auto-generates 80% of the declaration
- `tools/supervisor/grade_declared_work.py` — grading logic source of truth
