# Parser Notes: OASIS Universal Business Language

## Parsing Strategy
- **Primary module:** xml.etree.ElementTree (stdlib)
- **Reuse pattern:** XML-based codec pattern (similar to FODT/FODP codecs)
- **Estimated LOC:** 400-600

## Detection (Probe)
Check for `.xml` extension with UBL namespace detection. Parse the root element and check for a UBL 2.3 namespace prefix (`urn:oasis:names:specification:ubl:schema:xsd:`). Identify the specific document type from the root element name (Invoice, Order, etc.).

## Loading
Parse the XML document using `xml.etree.ElementTree.parse()`. Extract the document type from the root element. Navigate the namespace-qualified tree to extract business entities (parties, line items, tax totals, monetary amounts). Build a structured model representing the business document with its Common Aggregate Components.

## Writing
Construct the XML tree from the business document model, ensuring proper namespace declarations for the document type and CAC/CBC component libraries. Write support planned.

## Dependencies
- stdlib only (xml.etree.ElementTree)
- No new external dependencies required
