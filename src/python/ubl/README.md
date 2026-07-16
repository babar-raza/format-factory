# Format Factory — ubl

Parse, edit, and write OASIS UBL 2.x (Invoice, CreditNote, Order) business documents with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:25:44+00:00 source=package-metadata -->
```bash
pip install format-factory-ubl
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from ubl.ubl_codec import load_ubl, write_ubl, check_tax_consistency

model = load_ubl("invoice.xml")
print(model["document_type"], model["id"], model["monetary_total"])

# Optional sanity check before writing -- non-authoritative, see Features below
issues = check_tax_consistency(model)

write_ubl(model, "invoice-copy.xml")  # warns (non-fatal) if issues is non-empty
```

## Features

- Tax totals (`cac:TaxTotal`/`cac:TaxSubtotal`) and legal monetary total (`cac:LegalMonetaryTotal`)
- Full party depth: postal address, VAT/tax scheme, legal entity, contact, Peppol endpoint id
- Write-side party round-trip (supplier/customer/buyer/seller all re-emitted, not dropped)
- CreditNote document type alongside Invoice and Order
- `check_tax_consistency()` — an opt-in, non-authoritative arithmetic sanity check

**IMPORTANT SCOPE NOTE:** tax/monetary handling is **transcription, not validated computation** — this codec re-emits whatever values a source document already contains; it does not derive a tax amount from a rate. There is **no XSD/Schematron/Peppol BIS 3.0 validation** — a written document is not guaranteed schema-valid or e-invoicing-conformant. Only Invoice/CreditNote/Order of UBL's 91 document types are supported. See `reports/spec-coverage/ubl-deferred.json` for the full, honest scope boundary.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:25:44+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:25:44+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | OASIS Universal Business Language |
| Track | python |
| Package | format-factory-ubl |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS UBL 2.3 |
| QName coverage | 4/4 implemented |
| Source files | 17 |
| Test files | 7 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:25:44+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
