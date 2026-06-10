# False-Pass / False-Stop Risk Report

## False-Pass Risks (prevented)
1. FODS export_csv — blocked: FodsCsvExporter is product-local, no target writer
2. FODS export_html — blocked: FodsHtmlExporter is product-local, no target writer
3. FODT export_markdown — blocked: FodtMarkdownExporter is product-local, no target writer
4. FODT export_txt — blocked: FodtTxtExporter is product-local, no target writer
5. DIF overclaim — caveated: empirical spec only, not official authority
6. Stale proof — blocked: claim:zst:old-compress stale, cannot pass coverage

## False-Stop Risks (mitigated)
1. FODT no R2 context pack — fixture-backed, clearly caveated, pilots run
2. DIF empirical — accepted_with_limitations, not rejected, visible caveat
