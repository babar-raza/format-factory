"""V53 spec_qname compliance tests for FODT Compat/ facades (TC-SP-005).

Verifies that each facade:
  1. Exposes spec_qname at class level
  2. Has correct spec_fact_ref
  3. Has namespace_uri containing oasis
  4. Inherits from its canonical spec class
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fodt.Compat import (
    FodtDocument,
    FodtParagraph,
    FodtHeading,
    FodtSpan,
    FodtTableCell,
    FodtList,
    FodtListItem,
    FodtTable,
    FodtTableRow,
)
from src.python.fodt.spec.text.paragraph import Paragraph as SpecParagraph
from src.python.fodt.spec.text.heading import Heading as SpecHeading
from src.python.fodt.spec.text.span import Span as SpecSpan
from src.python.fodt.spec.text.list_ import List as SpecList
from src.python.fodt.spec.text.list_item import ListItem as SpecListItem
from src.python.fodt.spec.table.table import Table as SpecTable
from src.python.fodt.spec.table.table_row import TableRow as SpecTableRow
from src.python.fodt.spec.table.table_cell import TableCell as SpecTableCell


class TestFodtParagraphSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtParagraph.spec_qname == "text:p"

    def test_spec_fact_ref(self):
        assert FodtParagraph.spec_fact_ref == "FACT-FODT-003"

    def test_namespace_uri(self):
        assert "oasis" in FodtParagraph.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtParagraph, SpecParagraph)

    def test_instantiation(self):
        assert FodtParagraph({}) is not None


class TestFodtHeadingSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtHeading.spec_qname == "text:h"

    def test_spec_fact_ref(self):
        assert FodtHeading.spec_fact_ref == "FACT-FODT-004"

    def test_namespace_uri(self):
        assert "oasis" in FodtHeading.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtHeading, SpecHeading)

    def test_instantiation(self):
        assert FodtHeading({}) is not None


class TestFodtSpanSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtSpan.spec_qname == "text:span"

    def test_spec_fact_ref(self):
        assert FodtSpan.spec_fact_ref == "FACT-FODT-006"

    def test_namespace_uri(self):
        assert "oasis" in FodtSpan.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtSpan, SpecSpan)

    def test_instantiation(self):
        assert FodtSpan({}) is not None


class TestFodtListSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtList.spec_qname == "text:list"

    def test_spec_fact_ref(self):
        assert FodtList.spec_fact_ref == "FACT-FODT-005"

    def test_namespace_uri(self):
        assert "oasis" in FodtList.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtList, SpecList)

    def test_instantiation(self):
        assert FodtList({}) is not None


class TestFodtListItemSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtListItem.spec_qname == "text:list-item"

    def test_spec_fact_ref(self):
        assert FodtListItem.spec_fact_ref == "FACT-FODT-005"

    def test_namespace_uri(self):
        assert "oasis" in FodtListItem.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtListItem, SpecListItem)

    def test_instantiation(self):
        assert FodtListItem({}) is not None


class TestFodtTableSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtTable.spec_qname == "table:table"

    def test_spec_fact_ref(self):
        assert FodtTable.spec_fact_ref == "FACT-FODT-007"

    def test_namespace_uri(self):
        assert "oasis" in FodtTable.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtTable, SpecTable)

    def test_instantiation(self):
        assert FodtTable({}) is not None


class TestFodtTableRowSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtTableRow.spec_qname == "table:table-row"

    def test_spec_fact_ref(self):
        assert FodtTableRow.spec_fact_ref == "FACT-FODT-007"

    def test_namespace_uri(self):
        assert "oasis" in FodtTableRow.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtTableRow, SpecTableRow)

    def test_instantiation(self):
        assert FodtTableRow({}) is not None


class TestFodtTableCellSpecQname:
    def test_spec_qname_class_level(self):
        assert FodtTableCell.spec_qname == "table:table-cell"

    def test_spec_fact_ref(self):
        assert FodtTableCell.spec_fact_ref == "FACT-FODT-007"

    def test_namespace_uri(self):
        assert "oasis" in FodtTableCell.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodtTableCell, SpecTableCell)

    def test_instantiation(self):
        assert FodtTableCell({}) is not None
