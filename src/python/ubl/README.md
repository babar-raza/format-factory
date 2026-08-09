---
visibility: generated
generated_by: codex
---

# Format Factory — UBL

Bounded parsing, editing, validation, and serialization for OASIS UBL 2.3.

## Installation

```bash
pip install format-factory-ubl
```

## Quick start

```python
from format_factory.ubl import dump, load, validate

document = load("invoice.xml")
print(document.root_name, validate(document).is_valid)
dump(document, "invoice-copy.xml")
```

## Current chassis

- Authority-pinned inventory and typed root classes for all 91 UBL 2.3
  document roots.
- Lossless structural XML model preserving QNames, attributes, text, child
  ordering, and extension content.
- Bounded input, element, depth, attribute, text, and output processing.
- DTD/entity rejection and passive signature preservation tracking.
- Deterministic semantic serialization and a collision-safe PEP 420 namespace.

This development chassis recognizes every normative document root, but it is
not yet a UBL conformance certification. Full generated common-component
types, order/cardinality enforcement, XSD cross-validation, code-list hooks,
streaming parsing, curated Invoice/CreditNote/Order workflows, official
corpora, mutation/fuzz evidence, and independent-schema-engine proof remain
mandatory obligations. National invoicing profiles such as Peppol are
separate future packages.

## Official code lists

```python
from format_factory.ubl import official_code_list_registry, validate_code

registry = official_code_list_registry()  # every bundled official UBL 2.3 code list
result = validate_code(registry, some_code)  # deterministic, fully offline
```

`validate_code()` distinguishes "the code is wrong" from "this code names
no list_id" and "this list isn't in the registry" -- an unregistered list
is a gap in the registry's own population, not evidence the code itself
is invalid. `official_code_list_registry()` returns a fresh, mutable
registry each call; a caller may extend it with profile- or
customer-specific lists via the same `CodeListRegistry.register()` any
custom list uses -- there is no architectural difference between
"official" and "custom" lists.

## Document indexing and business-role queries

```python
from format_factory.ubl import DocumentIndex, business_role

index = DocumentIndex(document.root)  # built once, read-only
lines = index.by_business_role("line")       # InvoiceLine/CreditNoteLine/OrderLine/...
duplicates = index.duplicate_ids()
```

`business_role()` classifies an element by local-name suffix (matching
`*Line`, `*Party`, and the other role-shaped names UBL's own generic
component vocabulary uses) rather than an exhaustive per-root-type enum
-- a query that works identically across all 91 supported document
roots.

## Editing core business components

Lines and other repeating root-level components support real CRUD
operations that stay schema-order-safe by construction and refuse any
edit that would make `validate()` report something the source document
did not already have:

```python
from format_factory.ubl import add_line, move_line, remove_line, renumber_lines

document = remove_line(document, line_id="3")
document = move_line(document, line_id="1", to_index=0)
document, id_map = renumber_lines(document, {"1": "INV-1"})
```

```python
from format_factory.ubl import add_component, remove_component, replace_party, update_component

document = replace_party(document, role="AccountingSupplierParty", new_party=new_party)
document = update_component(document, component_name="PaymentMeans", index=0, new_component=new_means)
document = add_component(document, component_name="TaxTotal", new_component=extra_tax_total)
document = remove_component(document, component_name="AllowanceCharge", index=0)
```

`add_line`/`add_component` insert immediately after the last existing
occurrence of the same element when one is already present --
always schema-position-correct, since every repeating component in the
pinned UBL 2.3 schema appears as one contiguous run at its own declared
sequence position, not only lines. When the document has NO existing
occurrence of `component_name` at all, `add_component` looks up the
correct root-level insertion position from the bundled UBL 2.3 schema's
own declared child order (`schema_root_order`, precomputed for all 91
known root types -- no `xmlschema` installation needed at runtime) and
inserts there, proven correct both before an already-present later
sibling and after an already-present earlier one. `replace_party`/
`update_component` replace an *already-present* occurrence in place;
`remove_line`/`remove_component` delete one. `renumber_lines` rewrites
line identifiers and returns the applied old-ID-to-new-ID map, since this
package's generic model has no closed set of "fields that reference a
line" to rewrite on the caller's behalf. Every operation raises
`UblValidationError` rather than silently producing a worse document.

**What is not built:** `add_component` determines correct ROOT-level
position for a first occurrence, but has no opinion on that component's
own INTERNAL field structure for a component type this package's typed
model does not otherwise represent -- building one still requires the
caller to construct `new_component`'s own children directly, as in the
example above. Creating a brand-new
`AccountingSupplierParty`/`AccountingCustomerParty` wrapper is not built.
`remove_component`'s refusal is exactly as strong as `validate()` itself:
`validate()` does not currently check for missing mandatory top-level
elements, so removing a document's only mandatory party wrapper is not
refused today -- a disclosed limitation of the validator this function
composes, not of the CRUD operation itself.

## Cross-field arithmetic reconciliation

`validate()`/`schema_validate()` check structure and cardinality; they
cannot check arithmetic the XSD has no way to express -- that invoice
lines actually sum to the declared total, for example. `reconcile_invoice`
does, as a report-only pass that never mutates the document and never
raises:

```python
from decimal import Decimal
from format_factory.ubl import reconcile_invoice

report = reconcile_invoice(document.root, tolerance=Decimal("0.01"))
if not report.is_valid:
    for diagnostic in report.diagnostics:
        print(diagnostic.code, diagnostic.message)
```

Checks that invoice-line `LineExtensionAmount`s sum to
`cac:LegalMonetaryTotal`'s own declared line extension, that each
`cac:TaxTotal`'s subtotals sum to its own declared amount, and allowance/
charge totals -- each flagged only when present and inconsistent; an
absent aggregate is not an error. `tolerance` is an explicit
rounding-tolerance policy (a delta within it is not reported); the
default of zero preserves exact-match behavior for a caller who does not
opt in. A currency mismatch between lines and their total is reported
separately, since summing mismatched currencies without an exchange rate
the document does not carry would silently produce a meaningless number.

## Digital signatures (opt-in)

```python
from format_factory.ubl import SignatureBackendRegistry, sign_document, verify_signature

registry = SignatureBackendRegistry()
registry.register(my_backend)
result = verify_signature(registry, document)
if result.backend_registered:
    print(result.verified)
```

Both `sign_document()`/`verify_signature()` are always safe to call: with
no backend registered, they report `backend_registered=False` /
`verified=None` rather than raising or silently passing. Signing/
verification logic itself is supplied by the caller's own backend --
this package tracks signature presence and passively preserves signed
content, it does not ship a cryptographic implementation.

## Extension content adapters (opt-in)

Every foreign-namespace extension payload already round-trips generically
as `XmlNode`, lossless, with no adapter required. `ExtensionAdapterRegistry`
adds an opt-in, pluggable typed-decode layer on top, the same
runtime-populated-registry pattern `CodeListRegistry`/`SignatureBackendRegistry`
already use, keyed by QName instead of a list ID or a signature backend:

```python
from format_factory.ubl import ExtensionAdapterRegistry, decode_extension

registry = ExtensionAdapterRegistry()
registry.register(extension_node.qname, my_decoder)
result = decode_extension(registry, extension_node)
if result.adapter_known:
    print(result.decoded)
```

There is no built-in adapter for any namespace -- vendor and customization
extensions (digital signatures, PEPPOL, national customs authorities, and
similar) all differ, and this package has no verified spec data describing
any one of them. `decode_extension()` never raises and never alters
`result.node`: a QName with no registered adapter is reported as
`adapter_known=False` rather than an error, so calling it on every
extension node in a document is always safe, decoded or not.

## Profile-specific validation

`validate()` checks the stable structural chassis only, deliberately
independent of any customization profile's own business rules (EN 16931,
PEPPOL BIS, and similar rulesets are numerous, versioned, and not
something this package bundles). `ProfileValidatorRegistry` gives a
caller a place to register one, keyed by `cbc:CustomizationID` --
`ProfileID` identifies the business process a document participates in,
not which ruleset applies to it, so it is deliberately not the key:

```python
from format_factory.ubl import ProfileValidatorRegistry, validate_profile

registry = ProfileValidatorRegistry().register(customization_id, my_validator)
report = validate_profile(document, registry)
if report is None:
    print("no profile-specific ruleset ran for this document's customization ID")
elif not report.is_valid:
    print(report.diagnostics)
```

`register()` returns a *new* registry rather than mutating the caller's
own -- a registry already shared or cached cannot be changed out from
under its holder by an unrelated registration elsewhere. `validate_profile`
returns `None`, never an empty or passing report, when the document
declares no customization ID or nothing is registered for the one it
declares: `None` is not evidence of conformance, it means no
profile-specific ruleset ran at all, and a caller must not read it as
"passed."

## Version migration

`dumps()` refuses to serialize a document that does not declare the
stable UBL 2.3 profile -- older documents must be migrated first, not
silently relabeled. `migrate_document()` supports only the UBL 2.1-to-2.3
direction, the one pair this package has an acquired, diffed authority
source for (a direct structural diff of the official OASIS UBL 2.1 and
2.3 release packages): of UBL 2.3's 91 root document types, exactly 65
had a UBL 2.1 schema that differs from 2.3 only by optional additions and
cardinality widenings, never a removal or a tightening, so a valid UBL
2.1 document of one of those 65 types is already valid 2.3 *content* --
migration only relabels `cbc:UBLVersionID`, and only after re-validating
the relabeled result against the stable 2.3 profile:

```python
from format_factory.ubl import load, migrate_document, dumps

document = load(path.read_bytes())          # declared_version == "2.1"
migrated, report = migrate_document(document)
print(report.note)                          # what changed and why it's safe
output = dumps(migrated)                     # declared_version == "2.3"
```

`migrate_document()` raises `UblValidationError` -- never returns a
partially-migrated result -- when the document does not declare UBL 2.1,
when its root type is not one of the 65 additive/relaxing-only types, or
when the relabeled result fails `validate()`. The other 26 UBL 2.3 root
types (for example `BusinessCard`, `ImportCustomsDeclaration`) never had
a UBL 2.1 schema at all and are refused, not silently attempted. The
source `document` is never mutated; `migrate_document()` always returns a
new object plus a `MigrationReport` recording what was checked.

## Official OASIS sample corpus

```python
from pathlib import Path
official_samples = sorted(Path("samples/by-format/ubl/official").glob("*.xml"))
```

55 real OASIS UBL 2.3 example instance documents (vendored from the same
official release package this product's own XSD schemas come from) live
under `samples/by-format/ubl/official/`, alongside a manifest recording
each sample's declared UBL version and whether it round-trips through
`dumps()` byte-for-byte -- see that directory's own
`_official-corpus-manifest.yaml` for the full accounting.

## Compatibility

The supported runtime range is Python 3.11–3.14. The production distribution
installs only `format_factory.ubl`; the repository's former top-level `ubl`
alpha is retained solely for characterization and migration work.

## Public API

Lifecycle: `probe`, `load`, `loads`, `dump`, `dumps`, `validate`. Model:
`UblDocument`, `XmlNode`, `ROOT_CLASSES`, `ROOT_NAMES`,
`document_type_coverage`, `create_empty`, `detect_document_type`. Query:
`DocumentIndex`, `QueryMatch`, `business_role`, `external_reference_of`,
`DuplicateId`. Code lists: `CodeList`, `CodeListRegistry`,
`official_code_list_registry`, `validate_code`, `parse_genericode`,
`load_bundled_code_lists`. Signatures: `SignatureBackend`,
`SignatureBackendRegistry`, `sign_document`, `verify_signature`. Party/
address helpers: `Party`, `PostalAddress`, `Contact`, `Country`,
`TaxScheme`, and their `*_of()` extraction functions. Line-item helpers:
`LineItem`, `OrderLine`, `CreditNoteLine`, `DespatchLine`,
`DocumentReference`, `DocumentResponse`, `Response`, and their `*_of()`
extraction functions. Editing: `add_line`, `remove_line`, `move_line`,
`renumber_lines`, `replace_party`, `update_component`, `add_component`,
`remove_component`. Analytics: `element_count`, `qname_histogram`,
`semantic_sha256`.

## License

Apache-2.0
