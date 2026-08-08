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
occurrence of the same element -- always schema-position-correct, since
every repeating component in the pinned UBL 2.3 schema appears as one
contiguous run at its own declared sequence position, not only lines.
`replace_party`/`update_component` replace an *already-present*
occurrence in place; `remove_line`/`remove_component` delete one.
`renumber_lines` rewrites line identifiers and returns the applied
old-ID-to-new-ID map, since this package's generic model has no closed
set of "fields that reference a line" to rewrite on the caller's behalf.
Every operation raises `UblValidationError` rather than silently
producing a worse document.

**What is not built:** inserting the *first* occurrence of a component
type a document does not already have at all, and creating a brand-new
`AccountingSupplierParty`/`AccountingCustomerParty` wrapper, both need
header-position knowledge this package does not yet have. `remove_component`'s
refusal is exactly as strong as `validate()` itself: `validate()` does not
currently check for missing mandatory top-level elements, so removing a
document's only mandatory party wrapper is not refused today -- a
disclosed limitation of the validator this function composes, not of the
CRUD operation itself.

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
