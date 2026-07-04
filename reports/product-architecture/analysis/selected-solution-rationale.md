# Selected Solution Rationale
Generated: 2026-07-04

## Summary of Key Decisions

1. **QName hierarchy format:** Flat YAML list with parent_qnames/child_qnames cross-refs.
   Rationale: Consistent with existing registry files. Readable. Easy to validate by counting entries.

2. **Promotion registry:** Two registries (arc = architecture; blossom = source CI).
   Rationale: Honors blossom TC-CQGA-018/019's planned registry/promotion-ledger.yaml. No duplication.
   promotion_manager.py cross-references both — it does NOT duplicate blossom's state machine.

3. **Validator extension file:** New governance_validators_ext4.py, IDs V111-V127.
   Rationale: ext3.py is owned by PQLM-001 (blossom). V90-V94 reserved for blossom dotnet_semantic.py.
   V110 is taken by governance_validators_path.py. V111 is the first available ID.

4. **Wave 1 source migration:** QUEUED only — no source written in this plan.
   Rationale: System healing Lanes 1-6 must complete before product source regeneration (per plan §Context critical constraint).

5. **cross-referencing honey gap matrices for TC-ARC-007:**
   If honey TC-REVIEW-001/002 complete first, read their matrices as supplementary inputs.
   Arc TC-ARC-007 adds the QName-mapping and API-design classification layer on top.
   No re-doing the same format recon honey already did.
