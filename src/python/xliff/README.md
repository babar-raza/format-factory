# format-factory-xliff

Typed, bounded XLIFF 2.0/2.1 lifecycle support under the implicit
`format_factory` namespace: load, validate, edit, and write real
localization interchange files with deterministic output, structured
diagnostics, and resource limits enforced by default.

## Installation

```bash
pip install format-factory-xliff
```

## Common lifecycle

```python
from format_factory.xliff import dump, load, probe, validate

result = probe("messages.xlf")
if result:
    document = load("messages.xlf")
    report = validate(document)
    if report.is_valid:
        dump(document, "canonical.xlf")
```

`probe()` never raises -- it returns a `ProbeResult` (falsy when the source
is not a recognized XLIFF 2.x document) so callers can route unknown input
without a `try`/`except`. `load()` accepts a path, bytes, or a binary
stream. `validate()` returns a `ValidationReport` of structured
`Diagnostic`s rather than raising on the first problem, so a caller can
inspect every conformance issue in one pass.

## Segment QA checks

Six independently pluggable QA checks are reported separately from
`validate()`'s own conformance diagnostics -- QA findings are advisory
(missing/inconsistent translations, drift), never conformance errors:

```python
from format_factory.xliff import run_qa_checks, QA_CHECKS

report = run_qa_checks(document)  # all 6 checks
report = run_qa_checks(document, checks=["length_violations"])  # one check
print(sorted(QA_CHECKS))
# ['length_violations', 'missing_targets', 'placeholder_mismatch',
#  'translation_consistency', 'unchanged_targets', 'whitespace_punctuation_drift']
```

`length_violations` checks a file's declared `slr:sizeRestriction`/
`slr:storageRestriction` cascade (file -> group -> unit, nearest declaring
ancestor wins) against the 4 standard profiles the XLIFF 2.1 Size and
Length Restriction module defines (`xliff:codepoints`, `xliff:utf8`,
`xliff:utf16`, `xliff:utf32`).

## Effective xml:space / xml:lang resolution

`xml:space` and `xml:lang` inherit down the document tree per the XLIFF 2.1
spec's own default-value table (`<source>`/`<target>` resolve `xml:lang`
from the root `srcLang`/`trgLang` rather than their immediate parent).
`effective_attributes_by_unit()` resolves both attributes for every unit in
one pass:

```python
from format_factory.xliff import effective_attributes_by_unit

resolved = effective_attributes_by_unit(document)
space, lang = resolved["u1"]
```

Returns `{unit_id: (effective_xml_space, effective_xml_lang)}`. A file- or
group-level `xml:space`/`xml:lang` cascades to every unit beneath it unless
overridden closer to the unit; a `<data>` element's own fixed `preserve`
default and the `<source>`/`<target>` root-anchored `xml:lang` default are
both modeled explicitly, not folded into the generic parent-inheritance
case. `effective_xml_space()`/`effective_xml_lang()` are the same resolution
rules exposed as reusable primitives for callers who already walk the tree
themselves rather than calling the whole-document convenience function.

## Translation state transitions

```python
from format_factory.xliff import check_state_transitions, DEFAULT_STATE, TransitionPolicy

report = check_state_transitions(before_document, after_document, policy=DEFAULT_STATE)
for violation in report.violations:
    print(violation.segment_id, violation.from_state, "->", violation.to_state)
```

Segments are matched by id between two document snapshots; a `policy` maps
each state to the set of states it may legally transition to. A state the
policy does not mention permits no transition away from it -- fail-closed
by default, not fail-open.

## Template merge and drift detection

`MergeAdapter` is a runtime `Protocol` a caller implements for their own
non-XLIFF template format (a CAT tool's own source format, for example):
extract translatable spans into an XLIFF `XliffDocument` plus a `Skeleton`
carrying everything else verbatim, then merge translated segments back.

```python
from format_factory.xliff import Skeleton, compute_source_digest, merge_with_drift_check

skeleton = Skeleton(template=extracted_template, source_digest=compute_source_digest(original_source))
merged_bytes = merge_with_drift_check(adapter, translated_document, skeleton, live_source=current_source)
```

`merge_with_drift_check` refuses with a drift report instead of silently
merging when `live_source` no longer matches the digest the skeleton was
extracted from -- stale skeletons never produce corrupted output.
`TemplateMergeAdapter` is a working reference adapter for a minimal
`%%TR%% ... %%TR%%`-delimited template syntax, useful for testing the
`MergeAdapter` contract end to end.

## Module coverage and schema validation

```python
from format_factory.xliff import module_coverage_manifest, is_production_complete, schema_validate

for module in module_coverage_manifest():
    print(module)
print("all modules production-complete:", is_production_complete())

report = schema_validate(document)  # bundled OASIS XSD/Schematron/NVDL
```

`module_coverage_manifest()` reports every standard XLIFF 2.1 extension
module (Metadata, Glossary, Resource Data, Size and Length Restriction,
Format Style, Change Tracking, Matches, Validation) this package tracks.
`schema_validate`/`full_schema_validate` run the bundled OASIS-authored
XSD, Schematron, and NVDL files this package vendors under its own
`validation/schemas/` directory -- the same official schema package pinned
for this format's own obligation register.

## Preservation modes

```python
from format_factory.xliff import dumps, PreservationMode, check_preservation

report = check_preservation(document)  # what CANONICAL mode would drop
canonical_bytes = dumps(document, mode=PreservationMode.CANONICAL)
lossless_bytes = dumps(document)  # LOSSLESS is the default
```

`LOSSLESS` (the default) round-trips every unknown/unmodeled element and
attribute verbatim via a dedicated `ExtensionNode` slot. `CANONICAL`
regenerates the document from only what this package's typed model
understands, dropping anything unmodeled -- `check_preservation()` reports
exactly what would be dropped before a caller commits to that choice.

## Security and resource limits

```python
from format_factory.xliff import XLIFF_DEFAULT_LIMITS, load

document = load("messages.xlf", limits=XLIFF_DEFAULT_LIMITS.with_overrides(max_input_bytes=1_000_000))
```

Every load enforces `max_input_bytes`, `max_xml_nodes`, `max_nesting_depth`,
`max_entries` (a per-element attribute-flood guard), and
`max_decompressed_bytes` (cumulative decoded text) incrementally during
parsing, not only after a document is already fully materialized in
memory -- a caller-supplied limit that is smaller than the default is
always honored, never silently relaxed. A whole-package static sweep
(AST-level, not just a runtime test) confirms no module anywhere in this
package can reach networking, process-spawning, or dynamic-import
capabilities.

## Public namespace

The full public surface lives under `format_factory.xliff` -- lifecycle
(`load`/`loads`/`dump`/`dumps`/`probe`/`roundtrip`), the typed model
(`XliffDocument`, `XliffFile`, `Group`, `Unit`, `Segment`,
`InlineElement`, `ExtensionNode`, `Note`, `DataElement`), inline-content
helpers (`flatten_inline_content`, `text_slots`, `replace_text_slots`,
`split_segment`, `join_segments`, `copy_source_to_target`), language
compatibility (`check_source_language_compatibility`,
`check_target_language_compatibility`), and analytics
(`average_source_length`, `translated_segment_count`,
`untranslated_segment_count`).

## Security boundary

XLIFF files are parsed as strict, bounded XML -- no DTD processing, no
external entity resolution, no skeleton or `<file source="...">`
reference is ever fetched from disk or network by this package. See
`SECURITY.md` for the full untrusted-input policy.

## Current scope

The package is still `0.2.0.dev0`. XLIFF 2.2 is not accepted by the
stable profile and XLIFF 1.2 is intentionally not represented by this
model -- callers on 1.2 should convert upstream first. See `MIGRATION.md`
for alpha import-path changes.

## License

Apache-2.0. See the repository root `LICENSE` file.
