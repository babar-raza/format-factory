# R85 Train D — Product-Direction Supervisor Policy

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Changes Applied

### .supervisor/policies.yaml — product_factory section added

New policies:
- product_factory_direction_required: true
- evidence_supports_product_not_finish_line: true
- poc_targets_required: true
- commercial_net_products_required: 3
- foss_reduced_products_required: 3
- poc_matrix_file: product-capability-matrix/poc-targets.yaml
- installed_package_proof_required_for_package_claims: true
- same_format_save_required_for_product_claims: true
- editable_object_model_required_for_product_claims: true
- dogfood_export_required: true
- sprint_with_evidence_only_no_product_progress: PARTIAL_NOT_SUCCESS
- required_next_sprint_lanes: [7 required lanes]
- supervisor_loop_required_after_bundle: true

### .supervisor/prompts/next-sprint-generator.md — PRODUCT-FACTORY DIRECTION section added

Required product lanes now in template:
1. Commercial .NET product advancement (FODS/FODT/Netpbm)
2. Reduced/FOSS product advancement (ZST/Netpbm Python/SYLK)
3. Dogfooding export lane
4. Package/install proof lane
5. POC matrix update lane
6. State/memory sync lane
7. Final supervisor loop trigger

Insufficient sprint classification added:
- Sprint with evidence-only closure and no product progress = PARTIAL_NOT_SUCCESS

### Tests added
tests/supervisor/test_r85_product_factory_policies.py — 28 tests, all pass

## Verification

28/28 policy tests PASS:
- policies.yaml has product_factory section with all required fields
- next-sprint-generator.md has product-factory direction section
- poc-targets.yaml has 3 commercial + 3 FOSS products, no overclaim

## TRAIN_D_STATUS: COMPLETE
