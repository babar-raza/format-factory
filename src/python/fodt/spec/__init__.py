"""
fodt.spec — canonical spec-shaped class hierarchy for OpenDocument Flat Text.

Classes represent ODF specification elements by their QName.
Module layout mirrors the QName namespace prefix:
  spec.text   -> text:* (Paragraph, Heading, Span, List, ListItem)
  spec.table  -> table:* (Table, TableRow, TableCell)

These are NOT production models.
Canonical naming: Text.Paragraph, Table.Table, etc.
"""
