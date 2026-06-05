# Mainstream Requirement-Backed Handoff Template

**Purpose:** Mainstream uses this template to produce a governed handoff to Skills or the next sprint, anchored to specific claim IDs and required evidence.
**Consumer:** Skills stream, next-sprint prompt generator, EvidenceGraphImporter
**Authority:** This handoff is evidence of work scope and intent; it is not a capability acceptance.

---

## Handoff Metadata

- handoff_id: (e.g., handoff-fods-cell-write-{date})
- produced_at: (ISO8601 datetime)
- produced_by: mainstream
- sprint_id: (sprint that produced this handoff)
- handoff_type: (one of: implementation_complete, testing_complete, dogfood_complete, delta_ready)

## Required Claim IDs

required_claim_ids:
- claim_id_1: (e.g., claim-fods-cell_write-save)
- claim_id_2: (e.g., claim-fods-export-001)
(list all claims this handoff is evidence for)

## Work Completed

- source_files_changed: (list of file paths)
- test_files_added: (list of test file paths)
- dogfood_artifacts_produced: (list of {path, checksum})
- evidence_package_ref: (path to evidence-declaration.yaml if available)

## Evidence Summary

For each required_claim_id, state what evidence was produced:
- claim-fods-cell_write-save: added 5 roundtrip tests in FodsR*SaveRoundtrip.cs; dogfood produced at examples/net/fods/dogfood-output.fods with checksum abc123; validator_used=manual format inspection

## Gap Statement (honest)

State what is still missing for each claim to reach accepted_for_poc:
- claim-fods-cell_write-save: DogfoodProof linked in graph — MISSING (EvidenceGraphImporter must run to link dogfood artifact)

## Phrasing Contract

This handoff says: "here is evidence to promote these claims."
This handoff does NOT say: "these claims are now accepted" or "POC target is ready."
The CapabilityCoverageEvaluator determines coverage; the Supervisor decides acceptance.

## Next Action

next_action_required: (one of: run_evidence_graph_importer, run_coverage_evaluator, submit_capability_delta, request_policy_decision)
validation_command: (command to run to verify gap closure)
