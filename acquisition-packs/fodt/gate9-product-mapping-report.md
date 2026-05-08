---
artifact_id: fodt-gate9-product-mapping-report
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate9-product-mapping-report.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODT Gate 9 product mapping report. run050."
---

# FODT Gate 9 -- Product Mapping Report

**Gate:** 9 -- Product Mapping
**Format:** FODT (Flat OpenDocument Text)
**Run:** run050 (2026-05-08)
**Status:** APPROVED -- Babar Raza (2026-05-08, run050)
**DEC-034:** PASS inline (authorized by run050 execution prompt)

---

## Summary

FODT Gate 9 product mapping defines the tier structure for Python FOSS product source.
The tier map (acquisition-packs/fodt/tier-map.yaml v1.0) organizes 16 features across
5 tiers (0-4). First OSS release includes Tiers 0-2 (12 features).

## Tier Map Summary

| Tier | Name | First Release | Features |
|------|------|--------------|---------|
| 0 | File Identity | Yes | 4 |
| 1 | Core Text Content | Yes | 4 |
| 2 | Structured Content | Yes | 4 |
| 3 | Text Spans and Annotations | No | 3 |
| 4 | Layout and Media | No | 4 |

**First OSS release (Tiers 0-2):** 12 features
**Deferred (Tiers 3-4):** 7 features

## Key Decisions

1. Iterative list traversal (TC-7) is required in Tier 2 implementation.
2. Table extraction is Tier 2 (not Tier 1) given the required neutral model output.
3. Unsupported element detection (draw:frame, text:field) is part of Tier 2.
4. Text spans and annotations are deferred to Tier 3 due to insufficient Gate evidence.
5. No product source created in this sprint.

## ODF Family Reuse from FODS

- Namespace handling: identical to FODS
- File size guard: identical (100MB MAX_FILE_BYTES)
- Error dict return: identical pattern
- Expat XXE protection: identical
- iterparse requirement: same as FODS IR-FODS-002

## DEC-034 Gate 9 Verification (Inline, run050 authorized)

1. Tier map exists: YES (acquisition-packs/fodt/tier-map.yaml v1.0)
2. Tier map is valid YAML: YES (confirmed by sprint writer)
3. All tier entries cite facts or requirements: YES
4. First OSS scope is practical: YES (12 features, Tiers 0-2, mirrors FODS success)
5. No unsupported features claimed: YES (frames, fields, spans are deferred)
6. No product source created: YES (product_source_state: not_created)
7. No legal release claim: YES
8. No package release claim: YES
9. Registry update does not over-approve: YES (gate_9 passed, gate_10 planning_ready)
10. product-readiness updated consistently: YES

**DEC-034 INLINE: PASS 10/10**
