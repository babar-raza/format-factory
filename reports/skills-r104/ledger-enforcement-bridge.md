# Ledger Enforcement Bridge (Skills R104 Wave 5)

## Purpose

When the product-code change ledger validator detects a hash drift (source file changed without updating the ledger), the mainstream stream needs a governed way to fix it. This bridge defines that workflow.

## Enforcement Flow

```
1. Ledger validator detects DRIFT for src/net/fods/FodsDocument.cs
   -> ledger says SHA abc123, actual SHA def456

2. Bridge generates a remediation handoff:
   - skill_id: add-dotnet-object-model-feature (or add-dotnet-api)
   - action: UPDATE_LEDGER_ENTRY
   - source_file: src/net/fods/FodsDocument.cs
   - expected_sha: <current actual SHA>
   - ledger_path: reports/r90/product-code-change-ledger.json

3. Mainstream worker consumes the handoff:
   - Verifies the source change was intentional (part of current sprint)
   - Updates the ledger entry with new SHA
   - Produces a transcript documenting the ledger update

4. Transcript validates:
   - ledger_entry_id is present
   - actual_files_changed includes the ledger file
   - result is PASS
```

## Integration with Supervisor Grading

When the supervisor grades a work item that changed product source:

1. Check if `actual_files_changed` in the transcript includes any `src/` path
2. If yes, verify ledger_entry_id is non-null
3. Run ledger validator to confirm the entry matches current source SHA
4. If mismatch: grade as OVERCLAIMED with reason "ledger entry stale"

## Bridge Handoff Template

```yaml
---
bridge_type: ledger-enforcement-remediation
generated_by: skills-r104
trigger: ledger_validator_drift_detected

remediation:
  skill_id: add-dotnet-object-model-feature
  action: UPDATE_LEDGER_ENTRY
  source_file: "{drifted_source_path}"
  current_sha: "{actual_sha256}"
  stale_sha: "{ledger_sha256}"
  ledger_path: reports/r90/product-code-change-ledger.json

instructions: |
  1. Verify the source change is intentional and part of the current sprint
  2. Update the ledger entry for {drifted_source_path} with SHA {actual_sha256}
  3. Run: .local/venv/Scripts/python tools/supervisor/validate_product_code_ledger.py
  4. Confirm PASS
  5. Record the update in a transcript with ledger_entry_id

transcript_requirement:
  mode: live
  ledger_entry_id: required
  result: PASS
```

## Mainstream Adoption

The mainstream enforcement package (`adoption-enforcement/mainstream-enforcement.yaml`) Rule 3 already requires ledger entries for LIVE src-editing skills. This bridge provides the remediation path when that requirement is violated or when ledger entries become stale after source edits.

## Current Ledger State

The ledger at `reports/r90/product-code-change-ledger.json` tracks SHA-256 hashes for governed source files. Any sprint that modifies these files MUST update the ledger as part of its closeout.
