# QName / Spec-Hierarchy Compliance Report

## Verdict

Current compliance is **low overall**. There is useful format behavior, but the source model is not QName/spec-hierarchy driven.


1. **QName flattening and prefix pollution**: FODS/FODT/ODF-like classes are named `FodsCell`, `FodsRow`, `FodsSheet`, `FodtBody`, `FodtParagraph`, etc. This encodes package/format prefix rather than spec QName hierarchy such as `table:table-cell`, `table:table-row`, `table:table`, `office:body`, `text:p`.
2. **Monolithic format services**: Many products expose a parser/codec module with dozens of unrelated capabilities, especially Python `*_codec.py` and `*_parser.py` files. These combine reading, model construction, mutation, analytics, export, and validation.
3. **No visible spec mapping registry**: The extracted source contains no canonical QName registry, spec-to-source manifest, or evidence file mapping classes/functions to legal spec facts.
4. **No visible tests in zip**: The source zip contains build outputs and package metadata, but no test tree. Existing behavior cannot be safely preserved from this archive alone.
5. **Build artifacts included in source**: `bin/`, `obj/`, `build/`, `*.egg-info`, and `__pycache__` are present. These should not be treated as source and should be excluded from migration decisions.
6. **Cross-language model divergence**: .NET has some class-based partial models; Python frequently uses function-first modules and ad-hoc classes, so concepts are not aligned across platforms.
7. **Target writer libraries mixed with product libraries**: .NET CSV/HTML/Markdown/TXT writers are present alongside product formats. They are useful but should be utilities/targets, not spec model roots.
8. **Analytics/spurious feature inflation**: XCF/ZST analytics modules contain many arithmetic feature functions that do not correspond to spec constructs and should not define the model.
9. **Partial format scope hidden by rich APIs**: Many APIs provide probing, stats, conversions, or simple edits while lacking full spec-object model, preservation guarantees, schema validation, or full same-format fidelity.



## Canonical spec-to-source translation rules

### XML/QName formats: FODS, FODT, FODP, FODG, ODS, ODT, ABW, Gnumeric where XML-based
- Namespace URI/prefix becomes a source namespace/module segment. Example: `table:*` => `Spec.Table` / `spec.table`.
- Element local name becomes the class name in PascalCase. Example: `table:table-cell` => `Table.TableCell`; `text:p` => `Text.Paragraph` only if the manifest records local-name `p` and friendly alias `Paragraph`.
- Attributes become typed properties or attribute value objects under the owning element namespace. Attribute QName is preserved in generated metadata.
- Parent-child structure becomes containment. Repeated child QNames become typed collections.
- Mixed content must be represented explicitly with a sequence model, not collapsed to plain strings unless the facade intentionally exposes text convenience.
- Document root and package/container concerns stay separate: `Document` is public facade; `Spec.Office.DocumentContent` or equivalent is spec model.
- Every class carries generated metadata: `QName`, spec source ID, cardinality/allowed parent constraints, and generator version.

### Binary/chunk formats: QOI, XCF, ZST, Netpbm binary variants
- Magic/header/frame/chunk/opcode names must come from the spec when available: e.g., `Header`, `EndMarker`, `IndexOp`, `DiffOp`, `LumaOp`, `RunOp`, `RgbOp`, `RgbaOp` for QOI; `FrameHeader`, `Block`, `ContentSize` for ZST.
- Fields become typed members with size/endian/range metadata.
- Parser state machines are separate from data records.
- Analytics functions must sit outside `Spec` unless the spec defines the metric.

### Text/table/line formats: CSV, TSV, NDJSON, SYLK, DIF, TOML
- Grammar tokens, records, directives, sections, tables, rows, cells, and fields become canonical objects only when the format specification defines them.
- If no QName exists, use a governed canonical identity: `grammar:<format>/<construct>` with evidence and a mapping manifest.
- Public convenience APIs such as `get_headers`, `export_to_csv`, and `filter_records` remain facade/services; they do not define the spec model.


## Per-format compliance snapshot

- **net/_readme.md**: LOW; red flags: none detected by heuristic, still requires manifest audit
- **net/csv**: MEDIUM-LOW; red flags: CsvDocument; CsvReader; CsvReaderException; CsvWriter; CsvWriterException
- **net/fods**: LOW; red flags: FodsCell; FodsCsvExportException; FodsCsvExportResult; FodsCsvExporter; FodsDocument; FodsDocumentException; FodsDocumentExporter; FodsHtmlExportException; FodsHtmlExportResult; FodsHtmlExporter; FodsJsonExportException; FodsJsonExportResult; FodsJsonExporter; FodsOdsExportResult; FodsOdsExporter; FodsParseException; FodsParseResult; FodsParser; FodsPdfExportResult; FodsPdfExporter; FodsPngExportResult; FodsPngExporter; FodsRow; FodsSheet; FodsSheetInfo; FodsWriter
- **net/fodt**: LOW; red flags: FodtBody; FodtDocument; FodtDocumentException; FodtHtmlExportException; FodtHtmlExportResult; FodtHtmlExporter; FodtMarkdownExportException; FodtMarkdownExportResult; FodtMarkdownExporter; FodtParagraph; FodtParseException; FodtParseResult; FodtParser; FodtPdfExportResult; FodtPdfExporter; FodtPngExportResult; FodtPngExporter; FodtTableInfo; FodtTxtExportException; FodtTxtExportResult; FodtTxtExporter; FodtWriter
- **net/html**: LOW; red flags: HtmlWriter; HtmlWriterException
- **net/markdown**: LOW; red flags: MarkdownWriter; MarkdownWriterException
- **net/ndjson**: MEDIUM-LOW; red flags: NdjsonCsvExporter; NdjsonDocument; NdjsonException; NdjsonReader; NdjsonWriter
- **net/netpbm**: MEDIUM-LOW; red flags: NetpbmException; NetpbmExporter; NetpbmFormatException; NetpbmImage; NetpbmParser; NetpbmSizeException; NetpbmWriter
- **net/tsv**: MEDIUM-LOW; red flags: TsvCsvExporter; TsvDocument; TsvException; TsvReader; TsvWriter
- **net/txt**: LOW; red flags: TxtWriter; TxtWriterException
- **net/zst**: MEDIUM-LOW; red flags: ZstDocument; ZstException; ZstFileNotFoundException; ZstFileSizeException; ZstInvalidMagicException; ZstParser
- **python/_readme.md**: LOW; red flags: none detected by heuristic, still requires manifest audit
- **python/_shared**: LOW; red flags: none detected by heuristic, still requires manifest audit
- **python/abw**: LOW; red flags: AbwError; AbwParseError
- **python/csv**: MEDIUM-LOW; red flags: CsvError; CsvInputError; CsvParseError; CsvSizeError; CsvWriteError
- **python/dif**: LOW; red flags: DifCell; DifDocument; DifError; DifInvalidFormatError; DifSizeError
- **python/fodg**: LOW; red flags: FodgError; FodgParseError
- **python/fodp**: LOW; red flags: FodpError; FodpParseError
- **python/fods**: LOW; red flags: FodsCell; FodsCsvExportError; FodsDocument; FodsError; FodsInputError; FodsParseError; FodsSheet; FodsSizeError
- **python/fodt**: LOW; red flags: FodtDocument; FodtError; FodtInputError; FodtParagraph; FodtParseError; FodtSizeError; FodtSpan
- **python/gnumeric**: LOW; red flags: GnumericError; GnumericParseError
- **python/ndjson**: MEDIUM-LOW; red flags: NdjsonError; NdjsonParseError
- **python/ods**: LOW; red flags: OdsCell; OdsCsvExportError; OdsDocument; OdsError; OdsInvalidContainerError; OdsRow; OdsSheet; OdsSizeError
- **python/odt**: LOW; red flags: OdtDocument; OdtError; OdtHeading; OdtInvalidContainerError; OdtListItem; OdtParagraph; OdtSizeError
- **python/pbm**: MEDIUM-LOW; red flags: PbmDecodeError; PbmError; PbmImage; PbmInvalidHeaderError; PbmInvalidMagicError; PbmSizeError
- **python/pgm**: MEDIUM-LOW; red flags: PgmDecodeError; PgmError; PgmImage; PgmInvalidHeaderError; PgmInvalidMagicError; PgmSizeError
- **python/ppm**: MEDIUM-LOW; red flags: PpmDecodeError; PpmError; PpmImage; PpmInvalidHeaderError; PpmInvalidMagicError; PpmSizeError
- **python/qoi**: MEDIUM-LOW; red flags: QoiDecodeError; QoiEncodeError; QoiError; QoiImage; QoiInvalidHeaderError; QoiInvalidMagicError; QoiSizeError
- **python/sylk**: LOW; red flags: SylkCell; SylkDocument; SylkError; SylkInvalidFormatError; SylkParseError; SylkSizeError
- **python/toml**: MEDIUM-LOW; red flags: TomlError; TomlInputError; TomlParseError; TomlWriteError
- **python/tsv**: MEDIUM-LOW; red flags: TsvError; TsvInputError; TsvParseError; TsvSizeError
- **python/xcf**: LOW; red flags: XcfError; XcfImage; XcfInvalidHeaderError; XcfInvalidMagicError; XcfParseError; XcfSizeError
- **python/zst**: MEDIUM-LOW; red flags: ZstDecompressError; ZstDecompressionError; ZstError; ZstFileNotFoundError; ZstInvalidFrameError; ZstOutputLimitExceeded; ZstReadError