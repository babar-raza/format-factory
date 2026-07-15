# Spec Evidence: OASIS Universal Business Language

## Primary Specification
- **Title:** Universal Business Language Version 2.3
- **Version:** UBL 2.3
- **URL:** https://docs.oasis-open.org/ubl/UBL-2.3.html
- **Body:** OASIS
- **Accessed:** 2026-07-14
- **License:** RF (OASIS)

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: Yes (XSD provided by OASIS for all document types)
- Actively maintained: Yes

## Key Structural Facts
- UBL defines 82 document types (Invoice, Order, DespatchAdvice, etc.), each with its own root element and namespace
- Documents use a Common Aggregate Components (CAC) library of reusable structures like `Party`, `Address`, `Price`, and `TaxTotal`
- All elements are namespace-qualified; the main namespaces are `urn:oasis:names:specification:ubl:schema:xsd:` prefixed per document type
- Extension points allow embedding custom data via `<ext:UBLExtensions>` without breaking schema validation
