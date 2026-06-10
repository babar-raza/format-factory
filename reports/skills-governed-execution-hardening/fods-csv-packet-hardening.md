# FODS CSV Packet and Handoff Hardening
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

---

## Result: PASS — FODS CSV Packet is Safe for Mainstream Consumption

---

## Packet Validation

**File:** reports/skills-product-first/mainstream-consumption-packet.json

All 18 fields validated:
- packet_version: 1.0
- sprint_id: present
- selected_product_gap: GAP-FODS-DOGFOOD-CSV-DOTNET-001 (rank 1, poc_impact 95)
- recommended_skill: add-dotnet-api
- generated_handoff_path: EXISTS on disk
- template_path: EXISTS on disk
- allowed_files: 4 files (narrow — FodsDocument.cs, FodsWorkbook.cs, FodsR114ExportToCsvTests.cs, ledger)
- forbidden_files: 6 entries including registry, master-plan, poc-targets, .vscode/mcp.json, .supervisor/policies.yaml
- required_transcript_fields: 9 fields
- expected_source_diff: present
- expected_tests: present
- expected_raw_logs: present
- expected_ledger_entry: present
- expected_capability_matrix_update: present (see hardening note)
- expected_evidence_manifest_entry: present
- acceptance_criteria: 5 criteria
- downgrade_rules: 2 rules
- auto_repair_guidance: present

---

## Handoff Validation

**File:** reports/skills-product-first/generated-handoffs/handoff-spf-001-add-dotnet-api.yaml

- mode: dry-run (correct for Skills-only sprint)
- skill_id: add-dotnet-api
- format_id: fods
- gap_id: GAP-FODS-DOGFOOD-CSV-DOTNET-001
- enforcement_tier: FAIL_CLOSED
- allowed_files: 3 narrow files (FodsDocument.cs, FodsWorkbook.cs, FodsR114ExportToCsvTests.cs)
- forbidden_files: src/python/*, registry, plans, poc-targets, .vscode/mcp.json
- rollback_note: PRESENT
- focused_test_command: dotnet test tests/net/fods/ --filter FodsR114ExportToCsvTests

**Independent Consumability:**
Mainstream can use this handoff without human explanation.
The handoff tells Mainstream:
1. What product gap to work on ✓
2. Which files are allowed ✓
3. Which files are forbidden ✓
4. Which tests are expected ✓
5. What dogfood/output proof is expected ✓
6. What transcript fields are required ✓
7. What capability delta proposal is expected ✓
8. What must not be updated directly ✓
9. How to validate the handoff and transcript ✓

---

## Hardening Note: Capability Matrix Update

**Current behavior:** `expected_capability_matrix_update` says
"product-capability-matrix/poc-targets.yaml: fods.dogfood_status.fods_to_csv_dotnet → IMPLEMENTED"

This reads as a direct mandatory update to poc-targets.yaml. Since poc-targets.yaml
is in forbidden_files, this creates a contradiction (expect update but can't write it).

**Resolution for this sprint:** The downgrade rule fires if missing:
`{"condition": "capability_matrix_update missing", "result": "ACCEPT_WITH_LIMITATIONS"}`
So this is not a blocking failure — it auto-downgrades.

**Recommendation for future packets:** Change `expected_capability_matrix_update` to
`proposed_capability_delta` pointing to a report file, not a direct authority write.
Example:
```json
"proposed_capability_delta": {
  "report_path": "reports/{sprint}/capability-delta-proposal.yaml",
  "field": "fods.dogfood_status.fods_to_csv_dotnet",
  "proposed_value": "IMPLEMENTED",
  "authority_update_required": false,
  "note": "Supervisor or human approves this delta separately"
}
```

This change does NOT affect current packet consumability.

---

## Safety Summary

| Safety Check | Result |
|---|---|
| Allowed files are narrow | PASS — 3 named files only |
| Forbidden includes registry | PASS |
| Forbidden includes master-plan | PASS |
| Forbidden includes poc-targets | PASS |
| Forbidden includes .vscode/mcp.json | PASS |
| Forbidden includes .supervisor/policies.yaml | PASS |
| Capability update is not blocking | PASS (downgrade rule present) |

**Verdict: FODS_CSV_PACKET_SAFE_FOR_MAINSTREAM_CONSUMPTION**
