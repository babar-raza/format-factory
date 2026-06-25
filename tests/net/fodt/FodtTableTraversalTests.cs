// FormatFactory.Fodt.Tests -- Table traversal tests (TC-RECON-W4-002).
// Verifies FodtBody.Tables, FodtTable, FodtTableRow, FodtTableCell.
// ODF spec basis: ODF 1.3 §9.4.2 table:table, §9.4.4 table:table-row, §9.4.5 table:table-cell.

using System;
using System.IO;
using System.Text;
using System.Xml;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for FODT table traversal via FodtDocument.Tables / FodtBody.Tables.
/// Uses in-memory XML documents — no fixture files required.
/// </summary>
public class FodtTableTraversalTests
{
    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsText   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private const string NsTable  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    /// <summary>Builds a minimal FODT XML string with optional body content.</summary>
    private static string BuildFodt(string bodyContent)
    {
        return $"""
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="{NsOffice}"
  xmlns:text="{NsText}"
  xmlns:table="{NsTable}"
  office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
  office:version="1.3">
  <office:automatic-styles/>
  <office:body>
    <office:text>
{bodyContent}
    </office:text>
  </office:body>
</office:document>
""";
    }

    private static FodtDocument LoadXml(string xml)
    {
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmpPath, xml, Encoding.UTF8);
            return FodtDocument.Load(tmpPath);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // No-table documents
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_EmptyDocument_ReturnsEmptyList()
    {
        var doc = LoadXml(BuildFodt(""));
        Assert.Empty(doc.Tables);
    }

    [Fact]
    public void Tables_ParagraphOnlyDocument_ReturnsEmptyList()
    {
        var xml = BuildFodt("<text:p>Hello</text:p>");
        var doc = LoadXml(xml);
        Assert.Empty(doc.Tables);
    }

    // -------------------------------------------------------------------------
    // Single table
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_SingleTable_ReturnsOneTable()
    {
        var body = $"""
<table:table table:name="Sheet1">
  <table:table-row>
    <table:table-cell><text:p>A1</text:p></table:table-cell>
    <table:table-cell><text:p>B1</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Single(doc.Tables);
    }

    [Fact]
    public void Tables_SingleTable_NameAttributeCorrect()
    {
        var body = $"""
<table:table table:name="MyTable">
  <table:table-row>
    <table:table-cell><text:p>X</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal("MyTable", doc.Tables[0].Name);
    }

    [Fact]
    public void Tables_NoNameAttribute_NameIsEmpty()
    {
        var body = $"""
<table:table>
  <table:table-row>
    <table:table-cell><text:p>X</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(string.Empty, doc.Tables[0].Name);
    }

    // -------------------------------------------------------------------------
    // Rows and cells
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_TwoRows_RowCountIsTwo()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row><table:table-cell><text:p>R1C1</text:p></table:table-cell></table:table-row>
  <table:table-row><table:table-cell><text:p>R2C1</text:p></table:table-cell></table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(2, doc.Tables[0].RowCount);
    }

    [Fact]
    public void Tables_Row_CellCountMatchesActualCells()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row>
    <table:table-cell><text:p>A</text:p></table:table-cell>
    <table:table-cell><text:p>B</text:p></table:table-cell>
    <table:table-cell><text:p>C</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var row = doc.Tables[0].Rows[0];
        Assert.Equal(3, row.CellCount);
    }

    [Fact]
    public void Tables_Cell_GetPlainText_ReturnsCellContent()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row>
    <table:table-cell><text:p>Hello World</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal("Hello World", cell.GetPlainText());
    }

    [Fact]
    public void Tables_Cell_EmptyCell_GetPlainTextReturnsEmpty()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row>
    <table:table-cell/>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal(string.Empty, cell.GetPlainText());
    }

    [Fact]
    public void Tables_Cell_MultiParagraphCell_GetPlainTextJoinsWithNewline()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row>
    <table:table-cell>
      <text:p>Line1</text:p>
      <text:p>Line2</text:p>
    </table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var text = doc.Tables[0].Rows[0].Cells[0].GetPlainText();
        Assert.Equal("Line1\nLine2", text);
    }

    // -------------------------------------------------------------------------
    // GetCellText convenience method
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtTable_GetCellText_ValidCoords_ReturnsCellContent()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row>
    <table:table-cell><text:p>R0C0</text:p></table:table-cell>
    <table:table-cell><text:p>R0C1</text:p></table:table-cell>
  </table:table-row>
  <table:table-row>
    <table:table-cell><text:p>R1C0</text:p></table:table-cell>
    <table:table-cell><text:p>R1C1</text:p></table:table-cell>
  </table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var table = doc.Tables[0];
        Assert.Equal("R0C0", table.GetCellText(0, 0));
        Assert.Equal("R0C1", table.GetCellText(0, 1));
        Assert.Equal("R1C0", table.GetCellText(1, 0));
        Assert.Equal("R1C1", table.GetCellText(1, 1));
    }

    [Fact]
    public void FodtTable_GetCellText_OutOfRangeRow_ReturnsNull()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row><table:table-cell><text:p>X</text:p></table:table-cell></table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Null(doc.Tables[0].GetCellText(99, 0));
    }

    [Fact]
    public void FodtTable_GetCellText_OutOfRangeCol_ReturnsNull()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row><table:table-cell><text:p>X</text:p></table:table-cell></table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Null(doc.Tables[0].GetCellText(0, 99));
    }

    // -------------------------------------------------------------------------
    // Multiple tables
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_MultipleTablesInDocument_AllReturned()
    {
        var body = $"""
<table:table table:name="Table1">
  <table:table-row><table:table-cell><text:p>A</text:p></table:table-cell></table:table-row>
</table:table>
<text:p>Between tables</text:p>
<table:table table:name="Table2">
  <table:table-row><table:table-cell><text:p>B</text:p></table:table-cell></table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(2, doc.Tables.Count);
        Assert.Equal("Table1", doc.Tables[0].Name);
        Assert.Equal("Table2", doc.Tables[1].Name);
    }

    // -------------------------------------------------------------------------
    // Body accessor
    // -------------------------------------------------------------------------

    [Fact]
    public void Body_Tables_MatchesDocumentTables()
    {
        var body = $"""
<table:table table:name="T">
  <table:table-row><table:table-cell><text:p>X</text:p></table:table-cell></table:table-row>
</table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(doc.Tables.Count, doc.Body!.Tables.Count);
        Assert.Equal(doc.Tables[0].Name, doc.Body.Tables[0].Name);
    }
}
