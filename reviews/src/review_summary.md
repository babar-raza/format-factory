# File Format Factory src(12) Review and QName Restructuring Plan

## Executive summary

The extracted `src(12).zip` source tree is not ready for broad migration. It contains useful format behavior, but it is organized around product/package prefixes, convenience modules, and generated minimum-working-product code rather than around spec QNames and canonical grammar constructs.

The most serious issue is architectural: the system generated libraries that can parse/write/export small slices of formats, but it did not generate a traceable spec model. Therefore the correction cannot be a rename-only cleanup. The repo needs a governed spec-to-source layer: canonical QName/construct registries, deterministic namespace/class generators, source-to-spec manifests, validators, and compatibility adapters.

## What was inspected

- Uploaded archive: `/mnt/data/src(12).zip`
- Working directory: `/mnt/data/fff_src12_work`
- Report directory: `/mnt/data/fff_src12_reports`
- Relevant source/control files counted after excluding build/cache folders: 183
- C# files in archive: 105
- Python files in archive: 209
- Project files: 10 `.csproj`, 20 Python `pyproject.toml`

## Formats/products found

- net/_readme.md: 1 source/control files; load/parse/probe; QName compliance LOW; risk MEDIUM
- net/csv: 4 source/control files; load/parse/probe, object-model-lite, write/save; QName compliance MEDIUM-LOW; risk MEDIUM
- net/fods: 16 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- net/fodt: 12 source/control files; load/parse/probe, object-model-lite, write/save, export/convert; QName compliance LOW; risk HIGH
- net/html: 2 source/control files; write/save; QName compliance LOW; risk MEDIUM
- net/markdown: 2 source/control files; write/save; QName compliance LOW; risk MEDIUM
- net/ndjson: 6 source/control files; load/parse/probe, object-model-lite, write/save, export/convert; QName compliance MEDIUM-LOW; risk MEDIUM
- net/netpbm: 7 source/control files; load/parse/probe, object-model-lite, write/save, export/convert; QName compliance MEDIUM-LOW; risk MEDIUM
- net/tsv: 6 source/control files; load/parse/probe, object-model-lite, write/save, export/convert; QName compliance MEDIUM-LOW; risk MEDIUM
- net/txt: 2 source/control files; write/save; QName compliance LOW; risk MEDIUM
- net/zst: 4 source/control files; load/parse/probe, object-model-lite, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/_readme.md: 1 source/control files; load/parse/probe, export/convert, validation-lite; QName compliance LOW; risk MEDIUM
- python/_shared: 4 source/control files; load/parse/probe, validation-lite; QName compliance LOW; risk MEDIUM
- python/abw: 4 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/csv: 5 source/control files; load/parse/probe, write/save, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/dif: 4 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk MEDIUM
- python/fodg: 5 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/fodp: 4 source/control files; load/parse/probe, export/convert; QName compliance LOW; risk HIGH
- python/fods: 26 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/fodt: 10 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/gnumeric: 4 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/ndjson: 3 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/ods: 6 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk HIGH
- python/odt: 3 source/control files; load/parse/probe, object-model-lite, validation-lite; QName compliance LOW; risk HIGH
- python/pbm: 5 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/pgm: 4 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/ppm: 5 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/qoi: 4 source/control files; load/parse/probe, object-model-lite, write/save, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/sylk: 3 source/control files; load/parse/probe, object-model-lite, write/save, export/convert, validation-lite; QName compliance LOW; risk MEDIUM
- python/toml: 3 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/tsv: 3 source/control files; load/parse/probe, write/save, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM
- python/xcf: 4 source/control files; load/parse/probe, object-model-lite, export/convert, validation-lite; QName compliance LOW; risk MEDIUM
- python/zst: 5 source/control files; load/parse/probe, write/save, export/convert, validation-lite; QName compliance MEDIUM-LOW; risk MEDIUM

## Major issues


1. **QName flattening and prefix pollution**: FODS/FODT/ODF-like classes are named `FodsCell`, `FodsRow`, `FodsSheet`, `FodtBody`, `FodtParagraph`, etc. This encodes package/format prefix rather than spec QName hierarchy such as `table:table-cell`, `table:table-row`, `table:table`, `office:body`, `text:p`.
2. **Monolithic format services**: Many products expose a parser/codec module with dozens of unrelated capabilities, especially Python `*_codec.py` and `*_parser.py` files. These combine reading, model construction, mutation, analytics, export, and validation.
3. **No visible spec mapping registry**: The extracted source contains no canonical QName registry, spec-to-source manifest, or evidence file mapping classes/functions to legal spec facts.
4. **No visible tests in zip**: The source zip contains build outputs and package metadata, but no test tree. Existing behavior cannot be safely preserved from this archive alone.
5. **Build artifacts included in source**: `bin/`, `obj/`, `build/`, `*.egg-info`, and `__pycache__` are present. These should not be treated as source and should be excluded from migration decisions.
6. **Cross-language model divergence**: .NET has some class-based partial models; Python frequently uses function-first modules and ad-hoc classes, so concepts are not aligned across platforms.
7. **Target writer libraries mixed with product libraries**: .NET CSV/HTML/Markdown/TXT writers are present alongside product formats. They are useful but should be utilities/targets, not spec model roots.
8. **Analytics/spurious feature inflation**: XCF/ZST analytics modules contain many arithmetic feature functions that do not correspond to spec constructs and should not define the model.
9. **Partial format scope hidden by rich APIs**: Many APIs provide probing, stats, conversions, or simple edits while lacking full spec-object model, preservation guarantees, schema validation, or full same-format fidelity.


## Root causes

1. The generation pipeline appears capability/API-first rather than spec-model-first.
2. There is no visible enforceable canonical QName/construct registry in the source zip.
3. Namespaces are package namespaces such as `FormatFactory.Fods`, not spec namespaces such as `Spec.Table`, `Spec.Text`, `Spec.Office`.
4. Python package generation favors flat function modules, making parity with .NET object models difficult.
5. Build artifacts are included, obscuring source review and making inventory noisy.
6. Tests are absent from the zip, so preservation cannot be proven locally from this archive.


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


## Keep/remove/migrate summary

- **Keep behavior**: parsers, writers, exporters, probes, and mutation helpers contain useful work and should be preserved behind facades/adapters.
- **Move utilities**: CSV/HTML/Markdown/TXT target writers should become shared target/conversion utilities.
- **Split monoliths**: `FodsDocument`, `FodtDocument`, Python `*_codec.py`, and Python `*_parser.py` files should be split into `Spec`, `Reading`, `Writing`, `Validation`, `Conversion`, and `Public` layers.
- **Rename through migration, not direct edits**: old names such as `FodsCell` should become compatibility wrappers over `Spec.Table.TableCell`.
- **Quarantine analytics**: XCF/ZST arithmetic analytics should not influence spec model design.
- **Remove generated artifacts**: exclude `bin`, `obj`, `build`, `egg-info`, and `__pycache__` from source decisions.


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


## Risks and mitigations

- **Risk: losing working behavior during refactor**. Mitigation: freeze baseline API tests, migrate behind adapters, and compare roundtrip outputs.
- **Risk: invented QName names**. Mitigation: require manifest evidence before class generation.
- **Risk: endless parallel models**. Mitigation: only one canonical spec model per format; public APIs are adapters.
- **Risk: Python/.NET divergence**. Mitigation: shared construct registry and identical canonical IDs.
- **Risk: source regenerated badly later**. Mitigation: add CI gates and generator rules before product migration.

## Verification plan

Minimum gates before first pilot closes:
- Source inventory generated and reviewed.
- Capability matrix generated and reviewed.
- Canonical construct registry exists for pilot format.
- Every new spec class has manifest evidence.
- Existing public facade tests pass.
- New QName/spec model tests pass.
- Old and new parser/writer paths produce equivalent results for fixtures.
- Validator rejects prefix-polluted model classes in `Spec` layer.
- Regeneration is deterministic.

## Exact files/reports written

- `source_inventory.csv`
- `format_capability_matrix.csv`
- `qname_compliance_report.md`
- `target_architecture.md`
- `migration_plan.md`
- `next_agent_handoff.md`
- `review_summary.md`


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

