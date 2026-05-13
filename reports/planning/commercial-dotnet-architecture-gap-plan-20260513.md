# Commercial .NET Architecture Gap Plan
# Sprint: COMMERCIAL-PRODUCT-DIRECTION-RESET-SWARM-001
# Lane C — Commercial Architecture Blueprint
# Date: 2026-05-13

## Summary

Architecture blueprint for src/net/{format}/ is documented in
docs/commercial-dotnet-architecture.md (pre-existing, confirmed current).

## Gap Analysis

### What Exists Now (C2)
- FodsParser.cs: streaming XmlReader, metadata + sheet/row/cell counts
- FodtParser.cs: streaming XmlReader, metadata + paragraph/list/table counts
- No writer, no exporter, no object model classes

### What Is Needed (C7+)

#### For FODS (src/net/fods/)

| Component | Exists | Needed |
|---|---|---|
| FodsParser.cs (Tier 0 streaming) | YES | Keep as C0-C2 baseline |
| FodsDocument.cs (document root + Load()) | NO | New file |
| Model/Workbook.cs | NO | New file |
| Model/Worksheet.cs | NO | New file |
| Model/Row.cs | NO | New file |
| Model/Cell.cs (with typed value) | NO | New file |
| Model/CellValue.cs | NO | New file |
| Model/Formula.cs | NO | New file |
| Model/Style.cs | NO | New file |
| Model/Metadata.cs | NO | New file |
| Model/OpaqueNode.cs | NO | New file |
| FodsWriter.cs (serializer) | NO | New file |
| FodsExporter.cs (conversion) | NO | New file |

#### For FODT (src/net/fodt/)

| Component | Exists | Needed |
|---|---|---|
| FodtParser.cs (Tier 0 streaming) | YES | Keep as C0-C2 baseline |
| FodtDocument.cs (document root + Load()) | NO | New file |
| Model/Document.cs | NO | New file |
| Model/Section.cs | NO | New file |
| Model/Paragraph.cs | NO | New file |
| Model/Run.cs | NO | New file |
| Model/Heading.cs | NO | New file |
| Model/List.cs | NO | New file |
| Model/ListItem.cs | NO | New file |
| Model/Table.cs | NO | New file |
| Model/TableRow.cs | NO | New file |
| Model/TableCell.cs | NO | New file |
| Model/Style.cs | NO | New file |
| Model/Metadata.cs | NO | New file |
| Model/OpaqueNode.cs | NO | New file |
| FodtWriter.cs (serializer) | NO | New file |
| FodtExporter.cs (conversion) | NO | New file |

### Shared Code Decision

**Decision pending:** A shared `FormatFactory.Core` library could contain:
- OpaqueNode (raw XML preservation)
- Base Metadata model
- Common export interfaces

This requires an explicit human-approved architecture decision before implementation.
Do NOT create shared code without that decision.

## Files Created
- docs/commercial-dotnet-architecture.md (pre-existing, confirmed)
- docs/commercial-dotnet-architecture.yaml (new YAML form)

## Lane C Verdict
LANE_C_PASS_WITH_SHARED_CORE_DECISION_NEEDED
