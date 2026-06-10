# RCA Next Fixtures (R2/R3 Preparation)
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## RCA R2 Scope
Extend the proof graph to include the 4 new writer libraries:

### New Node Types Required
- `TargetWriterLibrary` node for each of FormatFactory.{Csv,Html,Txt,Markdown}
- `ExporterIntegration` node linking each exporter to its writer

### New Proof Links Required
- `claim:fods:export_csv_dotnet` → `TargetWriterLibrary(ff-csv-writer-net-001)` via `uses_writer`
- `TargetWriterLibrary(ff-csv-writer-net-001)` → `ImplementationArtifact(FodsCsvExporter.cs)` via `implemented_by`
- `ImplementationArtifact(FodsCsvExporter.cs)` → `TestArtifact(FodsCsvExporterTests.cs)` via `tested_by`
- `TestArtifact` → `DogfoodArtifact(fods-csv-output-sample)` via `produces`

### Pilot Status Changes After R2
- `claim:fods:export_csv_dotnet`: BLOCKED → READY (if all links present + tests pass)
- `claim:fods:export_html_dotnet`: BLOCKED → READY (if all links present + tests pass)
- `claim:fodt:export_txt_dotnet`: BLOCKED → READY (if all links present + tests pass)
- `claim:fodt:export_markdown_dotnet`: BLOCKED → READY (if all links present + tests pass)

## RCA R3 Scope (Tentative)
- FODT → HTML new capability claim
- Sylk/DIF FOSS RCA pilot
- Deeper requirement coverage for FODS/FODT

## Fixtures Needed for R2
1. `writer_node_fixtures.jsonl` — TargetWriterLibrary nodes (4 nodes)
2. `exporter_integration_edges.jsonl` — uses_writer edges (4 edges)
3. `r2_proof_graph_golden.json` — golden replay fixture for R2
