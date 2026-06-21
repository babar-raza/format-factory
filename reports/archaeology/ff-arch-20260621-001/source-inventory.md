# Source Inventory — ff-arch-20260621-001

## .NET Products (src/net/)

| Format | Files | Key Classes | Status |
|--------|-------|-------------|--------|
| csv | CsvDocument.cs, CsvReader.cs, CsvWriter.cs | CsvDocument | Active |
| fods | FodsDocument.cs, FodsParser.cs, FodsWriter.cs, Model/FodsCell.cs, Model/FodsRow.cs, Model/FodsSheet.cs, FodsCsvExporter.cs, FodsHtmlExporter.cs, FodsJsonExporter.cs, FodsOdsExporter.cs, FodsPdfExporter.cs, FodsPngExporter.cs, FodsDocumentExporter.cs, Exceptions/FodsDocumentException.cs | FodsDocument, FodsCell, FodsRow, FodsSheet | Active |
| fodt | FodtDocument.cs, FodtParser.cs, FodtWriter.cs, FodtHtmlExporter.cs, FodtMarkdownExporter.cs, FodtPdfExporter.cs, FodtPngExporter.cs, FodtTxtExporter.cs, Model/FodtBody.cs, Model/FodtParagraph.cs, Spec/Office/Body.cs, Spec/Table/Table.cs, Spec/Table/TableCell.cs, Spec/Table/TableRow.cs, Spec/Text/Heading.cs, Spec/Text/List.cs, Spec/Text/ListItem.cs, Spec/Text/Paragraph.cs, Spec/Text/Span.cs | FodtDocument, FodtParagraph + Spec skeletons | Active+Skeleton |
| html | HtmlWriter.cs | HtmlWriter | Support/utility |
| markdown | MarkdownWriter.cs | MarkdownWriter | Support/utility |
| ndjson | NdjsonDocument.cs, NdjsonReader.cs, NdjsonWriter.cs, NdjsonCsvExporter.cs, NdjsonException.cs | NdjsonDocument | Active |
| netpbm | Model/NetpbmImage.cs, NetpbmParser.cs, NetpbmWriter.cs, NetpbmExporter.cs, NetpbmException.cs | NetpbmImage | Active |
| tsv | TsvDocument.cs, TsvReader.cs, TsvWriter.cs, TsvCsvExporter.cs, TsvException.cs | TsvDocument | Active |
| txt | TxtWriter.cs | TxtWriter | Support/utility |
| zst | ZstDocument.cs, ZstParser.cs, Exceptions/ZstException.cs | ZstDocument | Active |

**Total .NET files: ~57**

## Python Products (src/python/)

| Format | Root Files | Key Modules | Notes |
|--------|-----------|-------------|-------|
| _shared | _base_codec.py, _base_parser.py, _shared_exceptions.py | Base classes | Shared infrastructure |
| abw | abw_codec.py, abw_analytics.py | Analytics split done | Analytics extracted |
| csv | csv_parser.py, csv_stats.py, csv_writer.py | Streaming parser | Active |
| dif | dif_parser.py, dif_stats.py | Parser only | Active |
| fodg | fodg_codec.py, fodg_analytics.py | Analytics split done | Active |
| fodp | fodp_codec.py | Codec only | Active |
| fods | parser.py, writer.py, neutral_model.py, constants.py, exceptions.py, csv_exporter.py | Full FOSS stack | CRITICAL: triple nesting (see below) |
| fodt | parser.py, writer.py, neutral_model.py, constants.py, exceptions.py, models.py, compat.py, list_traversal.py, spec/{text,table}/*.py | Full FOSS + spec stubs | Active + spec layer started |
| gnumeric | gnumeric_codec.py | Codec only | Active |
| ndjson | ndjson_codec.py | Codec only | Active |
| ods | ods_parser.py, ods_stats.py, ods_csv_exporter.py, ods_writer.py | Full FOSS stack | Active |
| odt | odt_parser.py | Parser only | Active |
| pbm | pbm_parser.py, pbm_to_pgm.py, pbm_to_ppm.py | Parser + converters | Active |
| pgm | pgm_parser.py, pgm_to_ppm.py | Parser + converter | Active |
| ppm | ppm_parser.py, ppm_stats.py, ppm_to_pgm.py | Parser + stats | Active |
| qoi | qoi_parser.py, qoi_encoder.py | Parser + encoder | Active |
| sylk | sylk_parser.py | Parser only | Active |
| toml | toml_codec.py | Codec | Active |
| tsv | tsv_parser.py | Parser only | Active |
| xcf | xcf_parser.py, xcf_analytics.py | Analytics split done | Active |
| zst | zst_codec.py, zst_analytics.py | Analytics split done | Active |

**Total Python format packages: 21 + _shared**

## Critical Structural Issue: FODS Triple Nesting

```
src/python/fods/
  __init__.py          <- outer package (DUPLICATE of inner)
  parser.py
  writer.py
  neutral_model.py
  constants.py
  exceptions.py
  csv_exporter.py
  fods/               <- middle nesting (DUPLICATE package root)
    __init__.py
    parser.py
    writer.py
    ...
    fods/             <- INNERMOST package (original?)
      __init__.py
      parser.py
      writer.py
      ...
```

All three levels have IDENTICAL `__init__.py` content. This indicates the package was
accidentally committed at three nesting levels. The installed package
(`format-factory-fods`) likely imports from the innermost level via the egg-info.
This is a BUILD ARTIFACT POLLUTION problem that corrupts source inventory.

## Build Artifacts Found in src/

```
src/
  format_factory_dev.egg-info/          <-- development install artifact
  src.zip                               <-- source archive artifact
  python/
    format_factory_abw.egg-info/
    format_factory_csv.egg-info/
    format_factory_dif.egg-info/
    format_factory_fodg.egg-info/
    format_factory_fodp.egg-info/
    format_factory_fods_python.egg-info/
    format_factory_fodt_python.egg-info/
    format_factory_gnumeric.egg-info/
    format_factory_ndjson.egg-info/
    format_factory_ods.egg-info/
    format_factory_odt.egg-info/
    format_factory_pbm.egg-info/
    format_factory_pgm.egg-info/
    format_factory_ppm.egg-info/
    format_factory_qoi.egg-info/
    format_factory_sylk.egg-info/
    format_factory_toml.egg-info/
    format_factory_tsv.egg-info/
    format_factory_xcf.egg-info/
    format_factory_zst.egg-info/
```

**21 egg-info directories committed to source**. These are build artifacts and should NOT be tracked in git.
They pollute `git status`, inflate source inventory, and risk confusing package import resolution.
