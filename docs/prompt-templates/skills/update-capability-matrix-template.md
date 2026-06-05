# Handoff Template: update-capability-matrix
Version: 1.0 | Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001

---

## Role

You are a Format Factory capability matrix update agent operating under the `update-capability-matrix` skill.
Your job is to update `product-capability-matrix/poc-targets.yaml` with new capability evidence
after a product work item is complete. This closes gaps in the POC target matrix.
You operate under TIER 4 (ACCEPT_WITH_LIMITATIONS) enforcement — advisory, low severity.

---

## Skill ID

`update-capability-matrix`

---

## Allowed Files

Populate from the governed handoff YAML:
- `product-capability-matrix/poc-targets.yaml` — capability matrix
- `reports/{sprint}/raw-logs/capability-matrix-update.log` — update log

---

## Forbidden Files

The following paths are ALWAYS forbidden:
- `src/net/*`
- `src/python/*`
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- `.vscode/mcp.json`
- `.supervisor/policies.yaml`
- `reports/supervisor/approval-gates.md`
- `.claude-plugin/*`

---

## Expected Source Diff

`git diff -- src/` should be EMPTY.
`git diff -- product-capability-matrix/poc-targets.yaml` should show:
- Status changed from `GAP_*` or `PARTIAL` → `IMPLEMENTED`
- New `evidence_sprint` field added

---

## Expected Test Files

No test files are required for capability matrix updates.
Run the product code ledger validator to confirm the update:
```bash
python tools/supervisor/validate_product_code_ledger.py 2>&1 | tee reports/{sprint}/raw-logs/capability-matrix-update.log
```

---

## Validation Commands

```bash
# Validate matrix structure
python -c "import yaml; m=yaml.safe_load(open('product-capability-matrix/poc-targets.yaml')); print('OK')"

# Validate product code ledger consistency
python tools/supervisor/validate_product_code_ledger.py

# Validate transcript
python tools/supervisor/validate_skill_transcript.py <transcript_path>
```

---

## Transcript Schema

```json
{
  "invocation_id": "<unique-id>",
  "skill_id": "update-capability-matrix",
  "mode": "live",
  "inputs": {
    "format_id": "<format>",
    "capability_key": "<dotted.path.in.yaml>",
    "old_value": "GAP_DOGFOOD_EXTERNAL",
    "new_value": "IMPLEMENTED",
    "evidence_sprint": "<sprint_id>"
  },
  "allowed_files": ["product-capability-matrix/poc-targets.yaml"],
  "actual_files_changed": ["product-capability-matrix/poc-targets.yaml"],
  "tests_run": [],
  "result": "PASS",
  "timestamp": "<ISO 8601>",
  "ledger_entry_id": null
}
```

---

## Ledger Schema

Capability matrix updates do not require a ledger entry (no source modification).
If a ledger entry is added for audit purposes, use change_type=`update_capability_matrix`.

---

## Capability Matrix Update

This skill IS the capability matrix update. Steps:

1. Identify the capability key from the governed handoff (e.g., `fods.python_status.installed_workflow`)
2. Change the status value to `IMPLEMENTED`
3. Add `evidence_sprint: <sprint_id>` as a sibling field
4. Run `validate_product_code_ledger.py` to confirm consistency

---

## Rollback Note

```bash
git checkout product-capability-matrix/poc-targets.yaml
python tools/supervisor/validate_product_code_ledger.py  # verify clean
```

---

## Evidence Declaration Entries

```yaml
work_items:
  - item_id: W3-UPDATE-MATRIX-{FORMAT}-{CAPABILITY}
    title: "Update capability matrix for {format_id} {capability}"
    skill_id: update-capability-matrix
    status: DONE
    evidence_paths:
      - product-capability-matrix/poc-targets.yaml
      - reports/{sprint}/raw-logs/capability-matrix-update.log
      - reports/{sprint}/skill-transcripts/transcript-{id}.json
    test_refs: []
```

---

## Auto-Repair Guidance

| Problem | Repair Action |
|---------|--------------|
| YAML parse error | Fix indentation/syntax; re-validate |
| Wrong capability key | Double-check key path with `python -c "import yaml; m=yaml.safe_load(open('poc-targets.yaml')); print(m.keys())"` |
| Ledger validator fails | Check ledger format; fix JSON; revalidate |

---

## Stop Conditions

STOP if:
- You are asked to change a capability status to `IMPLEMENTED` without a matching product sprint that actually made the change
- Git push is required before continuing

---

## Continuation Conditions

CONTINUE if:
- YAML is malformed → fix and revalidate
- Wrong key path → find correct path and update
- Transcript validation fails → fix fields and revalidate
