# Incremental Migration Plan


## Incremental migration plan

1. **Freeze and inventory**: exclude build artifacts; generate `source_inventory.csv` and `format_capability_matrix.csv`; record baseline public APIs.
2. **Create canonical registries**: add QName/canonical construct registry per format from legal specs; include manifest entries for XML QName, binary records, and grammar constructs.
3. **Build validators before migration**: class-name-to-spec validator, namespace/folder validator, source-to-spec trace validator, duplicate model detector, manual-edit drift detector.
4. **Pilot lane A — XML/QName**: FODT is the best first pilot because current model is small (`FodtBody`, `FodtParagraph`) yet visibly wrong. Introduce `Spec.Office.Body`, `Spec.Text.Paragraph`, compatibility facade `FodtDocument`.
5. **Pilot lane B — table/text grammar**: TSV or NDJSON. Introduce grammar constructs while preserving current function/facade APIs.
6. **Pilot lane C — binary/chunk**: QOI or Netpbm. Introduce spec header/pixel/opcode/chunk objects separated from parser/writer.
7. **Pilot lane D — cross-language alignment**: implement the same FODT or TSV model concept in Python with idiomatic packages but identical manifest identities.
8. **Migrate format families in waves**: FODS/FODT/FODP/FODG/ODS/ODT/Gnumeric/ABW first for QName XML discipline; Netpbm/QOI/XCF/ZST second for binary record discipline; CSV/TSV/NDJSON/SYLK/DIF/TOML third for grammar construct discipline.
9. **Compatibility and deprecation**: keep existing APIs as adapters for at least one migration cycle; add warnings only after tests prove parity.
10. **Closeout**: migration is complete only when generated source can be deleted and regenerated from manifests with no semantic diff outside allowed formatting.



## Next-agent execution handoff

Start in planning/recon mode, not broad rewrite mode. The first implementation sprint should create the governance assets and validators, then perform one small pilot.

Recommended first pilot: **FODT .NET + FODT Python conceptual mirror**.

Taskcards:
- TC-001: Remove generated/build artifacts from source consideration and add ignore/audit rules.
- TC-002: Create canonical construct registry schema.
- TC-003: Seed FODT minimal QName registry from legal ODF/FODT spec facts: office body, text paragraph, text heading, text list, table/table-cell if currently parsed.
- TC-004: Add source-to-spec manifest for existing FODT classes and mark current names as facade/legacy.
- TC-005: Generate new spec-aligned class skeletons and adapters without deleting old behavior.
- TC-006: Add tests proving existing public API still works and new QName model exists.
- TC-007: Repeat for Python FODT using the same manifest identities.
- TC-008: Run validators, document evidence, and stop for audit before expanding to FODS.
