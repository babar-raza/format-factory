# Verification Matrix
Generated: 2026-07-04
Source: Plan §Validation Matrix Summary

| TC | Validation Type | Command / Method | Evidence Path |
|----|----------------|------------------|---------------|
| TC-ARC-001 | File exists + schema valid | Read + yaml.safe_load | reports/product-architecture/architecture-mission.yaml |
| TC-ARC-002 | File exists + required sections (7) | Read + section presence check | reports/product-architecture/dual-architecture-contract.md |
| TC-ARC-003 | QName node count ≥ 13; all required QNames present | Read + key check | reports/product-architecture/fods-qname-hierarchy.yaml |
| TC-ARC-004 | All 30 format+lang combos present | Read + count check | reports/product-architecture/qname-code-organization-plan.yaml |
| TC-ARC-005 | Hierarchy tree matches §1; all nodes delegate to canonical | Read + structure check | reports/product-architecture/fods-aspose-api-design.yaml |
| TC-ARC-006 | 0 entries with missing qname; 0 entries with missing parser_path | Read + counter check | reports/product-architecture/fods-public-api-to-qname-map.yaml |
| TC-ARC-007 | 30 audit records; no classification = null | Read + count + null check | reports/product-architecture/product-architecture-audit.yaml |
| TC-ARC-008 | Every public symbol has disposition field | Read + missing-field check | reports/product-architecture/qname-api-migration-ledger.yaml |
| TC-ARC-009 | Every audit finding maps to ≥1 gap entry | Cross-reference check | reports/product-architecture/aspose-qname-gap-ledger.yaml |
| TC-ARC-010 | Compiler rejects unmapped capability | python capability_feature_compiler.py --format fods --validate-qnames | stdout rejection log |
| TC-ARC-011 | Skill pre-check blocks speculative API | Invoke /add-dotnet-api with no QName → BLOCKED_SKILL_GAP | .supervisor/skill-registry.yaml |
| TC-ARC-012 | V111-V127 test cases pass | python -m pytest tests/supervisor/test_governance_validators.py -v -k "V11" | test output |
| TC-ARC-013 | Each pilot produces evidence YAML | Read each pilot-evidence/*.yaml | reports/product-architecture/pilot-evidence/ |
| TC-ARC-014 | All FODS+CSV QNames cross-mapped | Read + count check | reports/product-architecture/cross-language-alignment.yaml |
| TC-ARC-015 | Gate blocks missing product | Attempt taskcard for new format without QName hierarchy → BLOCKED | governance validator output |
| TC-ARC-016 | All 30 products have promotion_level | Read + null check | reports/product-architecture/promotion-registry.yaml |
| TC-ARC-017 | V122+V124 pass; skill requires spec_fact_ids | Validator test + skill invocation | test output |
| TC-ARC-018 | All Wave 1 items QUEUED_PENDING_SYSTEM_HEALING_GATE | Read + status check | qname-api-migration-ledger.yaml (Wave 1 section) |
