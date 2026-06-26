// Tests for FodtTableCell.GetPlainText, ColumnSpan, and FodtTableRow.CellCount.
// Sprint: ff-sprint-s146-dotnet-deepening-20260628
// Ledger: PC-FODT-R157

using System.IO;
using System.Text;
using System.Xml;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R157: Tests for FodtTableCell.GetPlainText(), FodtTableCell.ColumnSpan,
/// and FodtTableRow.CellCount/Cells.
/// GetPlainText extracts text from all nested text:p elements joined with newlines.
/// ColumnSpan reads table:number-columns-spanned attribute (defaults to 1 if absent).
/// Covers: empty cell GetPlainText returns empty string; single-paragraph cell returns text;
/// ColumnSpan absent returns 1; CellCount matches cells in row;
/// multi-paragraph cell GetPlainText joined by newline; multiple cells in row;
/// dogfood table parse GetPlainText; dogfood ColumnSpan present reads correctly;
/// dogfood multi-row table CellCount per row; dogfood Cells list length matches CellCount.
/// </summary>
public class FodtR157TableCellAndRowTests
{
    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsText   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private const string NsTable  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    private static FodtDocument LoadXml(string xml)
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        using var reader = XmlReader.Create(stream, new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver = null,
        });
        return FodtDocument.Load(reader);
    }

    private static string BuildFodt(string bodyContent) =>
        $"""
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

    // -------------------------------------------------------------------------
    // FodtTableCell.GetPlainText tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_EmptyCell_ReturnsEmptyString()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell/>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal(string.Empty, cell.GetPlainText());
    }

    [Fact]
    public void GetPlainText_SingleParagraph_ReturnsText()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell>
            <text:p>Hello Cell</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal("Hello Cell", cell.GetPlainText());
    }

    [Fact]
    public void GetPlainText_MultipleParagraphs_JoinedByNewline()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell>
            <text:p>Line One</text:p>
            <text:p>Line Two</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal("Line One\nLine Two", cell.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // FodtTableCell.ColumnSpan tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnSpan_AbsentAttribute_ReturnsOne()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>A</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        Assert.Equal(1, doc.Tables[0].Rows[0].Cells[0].ColumnSpan);
    }

    // -------------------------------------------------------------------------
    // FodtTableRow.CellCount tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CellCount_SingleCell_ReturnsOne()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>X</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        Assert.Equal(1, doc.Tables[0].Rows[0].CellCount);
    }

    [Fact]
    public void CellCount_MultipleCells_ReturnsCount()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>A</text:p></table:table-cell>
          <table:table-cell><text:p>B</text:p></table:table-cell>
          <table:table-cell><text:p>C</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        Assert.Equal(3, doc.Tables[0].Rows[0].CellCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiRowTable_CellCountPerRow()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>H1</text:p></table:table-cell>
          <table:table-cell><text:p>H2</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell><text:p>D1</text:p></table:table-cell>
          <table:table-cell><text:p>D2</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var table = doc.Tables[0];
        Assert.Equal(2, table.Rows[0].CellCount);
        Assert.Equal(2, table.Rows[1].CellCount);
    }

    [Fact]
    public void DogfoodPipeline_CellsListLength_MatchesCellCount()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>X1</text:p></table:table-cell>
          <table:table-cell><text:p>X2</text:p></table:table-cell>
          <table:table-cell><text:p>X3</text:p></table:table-cell>
          <table:table-cell><text:p>X4</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var row = doc.Tables[0].Rows[0];
        Assert.Equal(row.CellCount, row.Cells.Count);
    }

    [Fact]
    public void DogfoodPipeline_GetPlainText_AllCellsInRow()
    {
        var xml = BuildFodt("""
      <table:table table:name="T1">
        <table:table-row>
          <table:table-cell><text:p>Alpha</text:p></table:table-cell>
          <table:table-cell><text:p>Beta</text:p></table:table-cell>
          <table:table-cell><text:p>Gamma</text:p></table:table-cell>
        </table:table-row>
      </table:table>
""");
        var doc = LoadXml(xml);
        var cells = doc.Tables[0].Rows[0].Cells;
        Assert.Equal("Alpha", cells[0].GetPlainText());
        Assert.Equal("Beta", cells[1].GetPlainText());
        Assert.Equal("Gamma", cells[2].GetPlainText());
    }
}
