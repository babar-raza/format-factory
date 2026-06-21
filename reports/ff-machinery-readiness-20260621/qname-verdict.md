# QName System Verdict
# Run: ff-machinery-readiness-20260621-3024f68c
# Generated: 2026-06-21

## Verdict: METADATA_ONLY

QName is **defined and partially documented** but does NOT currently shape any product source.

## Evidence

### What Exists
- `registry/odf-ontology/qname-to-code-map.yaml` — 29 ODF QName mappings
- `registry/odf-ontology/canonical-class-inventory.yaml` — 28 canonical classes
- `registry/odf-ontology/namespace-tree.yaml` — ODF namespace hierarchy
- `registry/odf-ontology/containment-graph.yaml` — element containment
- `registry/odf-ontology/attribute-property-map.yaml` — attribute mappings
- `registry/odf-ontology/prefix-namespace-registry.yaml` — namespace prefixes
- Skills: `spec-literal-qname-to-code-mapping`, `spec-shaped-product-architecture-blueprint`, `spec-parity-verification`

### What Is Missing
| Proof Required | Status |
|---|---|
| QName map consumed by source generator | NOT FOUND |
| QName map enforced by CI validator | NOT FOUND |
| Canonical class hierarchy in src/python/fods/ | NOT FOUND (flat dict model) |
| Canonical class hierarchy in src/net/fods/ | NOT FOUND (format-prefixed FodsDocument) |
| Non-ODF formats have concept registry | NOT FOUND |
| QName-to-test mapping | NOT FOUND |
| QName gap becomes executable taskcard automatically | NOT FOUND |

### src/python/fods/ — QName Compliance Check
The FODS Python product uses a flat dict-based neutral model. No class hierarchy reflecting
`office:document → office:spreadsheet → table:table → table:table-row → table:table-cell` exists.

The `src/python/fods/Compat/` directory was created recently (untracked) and contains
facade classes, but these are facades without underlying canonical classes.

The `src/python/fods/fods/` directory (nested package stub from GAP-ARCH-003) was created
but not yet materialized with canonical implementation.

### src/net/fods/ — QName Compliance Check
The .NET product uses `FodsDocument.cs` (1386 LOC monolith) with format-prefixed naming.
No `Office/Document.cs`, `Table/Table.cs` canonical hierarchy exists.

## Root Cause
The spec-to-feature-radical-correction-plan.md identifies this as a systemic failure:
- QName ontology was built but never connected to source generation
- Product was built before QName-driven architecture was designed
- No machinery enforces QName in source

## Required Actions (in priority order)
1. **TC-QNAME-ENFORCE-001**: Add a source validator that checks src/net/fods/ class names against qname-to-code-map.yaml — currently NONE exists
2. **TC-QNAME-ENFORCE-002**: Add source validator for src/python/fods/ canonical package structure
3. **TC-QNAME-BACKFILL-001**: Implement canonical Python package hierarchy (src/python/fods/office/, table/, text/) with spec QNames
4. **TC-QNAME-BACKFILL-002**: Implement canonical .NET namespace hierarchy
5. **TC-QNAME-EXPAND-001**: Extend qname-to-code-map.yaml to cover all ODF concepts used in FODS/FODT products
6. **TC-QNAME-NONODF-001**: Create concept registries for non-ODF formats (ZST, CSV, PBM, etc.)

## Idempotency Result
This is the first audit run. Prior artifacts: none. Full baseline established.
