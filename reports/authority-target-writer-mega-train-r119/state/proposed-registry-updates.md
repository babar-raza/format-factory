# Proposed Registry Updates
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Status: PROPOSED — Not Applied

All registry changes below are proposals only.
DO NOT apply without coordinator review and human approval per AGENTS.md.
Patch file: `reports/authority-target-writer-mega-train-r119/proposed-authority-updates/csv-writer-registry-patch.yaml`

## Proposed: Add FormatFactory.Csv to Writer Registry
- `writer_id`: ff-csv-writer-net-001
- `target_format`: csv
- `library_name`: FormatFactory.Csv
- `library_path`: src/net/csv/FormatFactory.Csv.csproj
- `status`: MWP_IMPLEMENTED_NOT_RELEASE_READY
- `consumers`: FormatFactory.Fods (FodsCsvExporter)

## Future Proposals (Next Sprints)
- FormatFactory.Html → ff-html-writer-net-001
- FormatFactory.Txt → ff-txt-writer-net-001
- FormatFactory.Markdown → ff-markdown-writer-net-001
