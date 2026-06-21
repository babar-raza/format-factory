# Target Architecture


## Target architecture

```
src/
  dotnet/
    FormatFactory.<Format>/
      Public/                 # stable user facade and compatibility adapters
      Spec/
        <NamespaceOrGrammar>/  # QName/spec construct classes only
      Reading/                # parsers/readers/builders
      Writing/                # serializers/savers
      Validation/             # schema/grammar/semantic validators
      Conversion/             # exporters/importers outside spec model
      Internal/               # shared utilities, limits, IO helpers
      Generated/              # generated manifests/declarations, if committed
  python/
    format_factory_<format>/
      public.py
      spec/<namespace_or_grammar>/
      reading/
      writing/
      validation/
      conversion/
      internal/
      generated/
  shared/
    spec-manifests/
    qname-registry/
    generation-rules/
```

Do not put generated `bin`, `obj`, `build`, `egg-info`, or `__pycache__` into source governance. Existing public class/module names should be preserved initially as adapters that delegate to the new model.



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
