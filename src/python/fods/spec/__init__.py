"""
fods.spec — canonical spec-shaped class hierarchy for OpenDocument Flat Spreadsheet.

Classes in this package represent ODF specification elements by their QName.
Module layout mirrors the QName namespace prefix:
  spec.office   → office:* elements
  spec.table    → table:* elements
  spec.text     → text:* elements
  spec.style    → style:* elements
  spec.number   → number:* elements

These are NOT production models (see models.py for FodsDocument/FodsSheet/etc.).
Canonical naming: Table.Table, Office.Document, etc. (namespace.LocalName).
"""
