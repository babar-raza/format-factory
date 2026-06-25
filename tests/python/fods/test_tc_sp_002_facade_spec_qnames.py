"""V53 spec_qname compliance tests for 9 new FODS Compat/ facades (TC-SP-002).

Verifies that each facade:
  1. Exposes spec_qname at class level (not just instance)
  2. Has correct spec_fact_ref
  3. Has namespace_uri containing oasis
  4. Is importable from src.python.fods.Compat
  5. Inherits from its canonical spec class
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fods.Compat import (
    FodsBody,
    FodsSpreadsheet,
    FodsTableRow,
    FodsCoveredCell,
    FodsParagraph,
    FodsSpan,
    FodsAutomaticStyles,
    FodsStyle,
    FodsDateStyle,
)
from src.python.fods.spec.office.body import Body as SpecBody
from src.python.fods.spec.office.spreadsheet import Spreadsheet as SpecSpreadsheet
from src.python.fods.spec.table.table_row import TableRow as SpecTableRow
from src.python.fods.spec.table.covered_table_cell import CoveredTableCell as SpecCoveredTableCell
from src.python.fods.spec.text.paragraph import Paragraph as SpecParagraph
from src.python.fods.spec.text.span import Span as SpecSpan
from src.python.fods.spec.office.automatic_styles import AutomaticStyles as SpecAutomaticStyles
from src.python.fods.spec.style.style import Style as SpecStyle
from src.python.fods.spec.number.date_style import DateStyle as SpecDateStyle


class TestFodsBodySpecQname:
    def test_spec_qname_class_level(self):
        assert FodsBody.spec_qname == "office:body"

    def test_spec_fact_ref(self):
        assert FodsBody.spec_fact_ref == "FACT-FODS-002"

    def test_namespace_uri(self):
        assert "oasis" in FodsBody.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsBody, SpecBody)

    def test_instantiation(self):
        assert FodsBody() is not None


class TestFodsSpreadsheetSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsSpreadsheet.spec_qname == "office:spreadsheet"

    def test_spec_fact_ref(self):
        assert FodsSpreadsheet.spec_fact_ref == "FACT-FODS-003"

    def test_namespace_uri(self):
        assert "oasis" in FodsSpreadsheet.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsSpreadsheet, SpecSpreadsheet)

    def test_instantiation(self):
        assert FodsSpreadsheet() is not None


class TestFodsTableRowSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsTableRow.spec_qname == "table:table-row"

    def test_spec_fact_ref(self):
        assert FodsTableRow.spec_fact_ref == "FACT-FODS-005"

    def test_namespace_uri(self):
        assert "oasis" in FodsTableRow.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsTableRow, SpecTableRow)

    def test_instantiation(self):
        assert FodsTableRow() is not None


class TestFodsCoveredCellSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsCoveredCell.spec_qname == "table:covered-table-cell"

    def test_spec_fact_ref(self):
        assert FodsCoveredCell.spec_fact_ref == "FACT-FODS-023"

    def test_namespace_uri(self):
        assert "oasis" in FodsCoveredCell.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsCoveredCell, SpecCoveredTableCell)

    def test_instantiation(self):
        assert FodsCoveredCell() is not None


class TestFodsParagraphSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsParagraph.spec_qname == "text:p"

    def test_spec_fact_ref(self):
        assert FodsParagraph.spec_fact_ref == "FACT-FODS-007"

    def test_namespace_uri(self):
        assert "oasis" in FodsParagraph.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsParagraph, SpecParagraph)

    def test_instantiation(self):
        assert FodsParagraph() is not None


class TestFodsSpanSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsSpan.spec_qname == "text:span"

    def test_spec_fact_ref(self):
        assert FodsSpan.spec_fact_ref == "FACT-FODS-007"

    def test_namespace_uri(self):
        assert "oasis" in FodsSpan.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsSpan, SpecSpan)

    def test_instantiation(self):
        assert FodsSpan() is not None


class TestFodsAutomaticStylesSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsAutomaticStyles.spec_qname == "office:automatic-styles"

    def test_spec_fact_ref(self):
        assert FodsAutomaticStyles.spec_fact_ref == "FACT-FODS-008"

    def test_namespace_uri(self):
        assert "oasis" in FodsAutomaticStyles.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsAutomaticStyles, SpecAutomaticStyles)

    def test_instantiation(self):
        assert FodsAutomaticStyles() is not None


class TestFodsStyleSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsStyle.spec_qname == "style:style"

    def test_spec_fact_ref(self):
        assert FodsStyle.spec_fact_ref == "FACT-FODS-009"

    def test_namespace_uri(self):
        assert "oasis" in FodsStyle.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsStyle, SpecStyle)

    def test_instantiation(self):
        assert FodsStyle() is not None


class TestFodsDateStyleSpecQname:
    def test_spec_qname_class_level(self):
        assert FodsDateStyle.spec_qname == "number:date-style"

    def test_spec_fact_ref(self):
        assert FodsDateStyle.spec_fact_ref == "FACT-FODS-010"

    def test_namespace_uri(self):
        assert "oasis" in FodsDateStyle.namespace_uri

    def test_inherits_spec_class(self):
        assert issubclass(FodsDateStyle, SpecDateStyle)

    def test_instantiation(self):
        assert FodsDateStyle() is not None
