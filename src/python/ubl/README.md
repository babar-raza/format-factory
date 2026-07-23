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

## Compatibility

The supported runtime range is Python 3.11–3.14. The production distribution
installs only `format_factory.ubl`; the repository's former top-level `ubl`
alpha is retained solely for characterization and migration work.

## Public API

- `probe`, `load`, `loads`, `dump`, `dumps`, `validate`
- `UblDocument`, `XmlNode`, `ROOT_CLASSES`, `ROOT_NAMES`
- `element_count`, `qname_histogram`, `semantic_sha256`

## License

Apache-2.0
