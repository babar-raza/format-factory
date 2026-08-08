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
extraction functions. Analytics: `element_count`, `qname_histogram`,
`semantic_sha256`.

## License

Apache-2.0
