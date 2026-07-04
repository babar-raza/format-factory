# Evidence Contract
Generated: 2026-07-04
Source: Plan §Evidence Contract

## Required Evidence Files

| TC | Evidence File | Required Fields |
|----|--------------|----------------|
| TC-ARC-001 | reports/product-architecture/architecture-mission.yaml | mission_id, head, sal_fact_total ≥ 14000 |
| TC-ARC-002 | reports/product-architecture/dual-architecture-contract.md | 7 required sections |
| TC-ARC-003 | reports/product-architecture/fods-qname-hierarchy.yaml | ≥13 qname_nodes, all owning_type populated |
| TC-ARC-004 | reports/product-architecture/qname-code-organization-plan.yaml | 30 entries, no null target_subdirs |
| TC-ARC-005 | reports/product-architecture/fods-aspose-api-design.yaml | all public types with canonical_model_type |
| TC-ARC-006 | reports/product-architecture/fods-public-api-to-qname-map.yaml | 0 null qname fields |
| TC-ARC-007 | reports/product-architecture/product-architecture-audit.yaml | 30 records, no null classification |
| TC-ARC-008 | reports/product-architecture/qname-api-migration-ledger.yaml | all symbols with disposition |
| TC-ARC-009 | reports/product-architecture/aspose-qname-gap-ledger.yaml | all CRITICAL findings with task_ids |
| TC-ARC-013 | reports/product-architecture/pilot-evidence/*.yaml (6 files) | verdict: PASS for each |
| TC-ARC-014 | reports/product-architecture/cross-language-alignment.yaml | all FODS QNames cross-mapped |
| TC-ARC-016 | reports/product-architecture/promotion-registry.yaml | 30 records with promotion_level |
| TC-ARC-018 | reports/product-architecture/wave1-taskcards.yaml | all Wave 1 items QUEUED_PENDING_SYSTEM_HEALING_GATE |

## Evidence Traceability Requirement

All evidence artifacts must reference:
- authoritative_plan: plans/.claude/imperative-drifting-conway.md
- requirement_id: REQ-ARC-*
- taskcard_id: TC-ARC-*
- micro_step_id: MS-* (where applicable)

## Evidence NOT Containing Competing Instructions

Evidence files are analysis/proof artifacts only.
They must NOT contain alternative execution instructions that conflict with the authoritative plan.
