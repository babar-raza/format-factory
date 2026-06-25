// Tests for FodtTableCell.ColumnSpan, GetPlainText (multi-paragraph), FodtTableRow.CellCount.
// Sprint: FORMAT-FACTORY-FODT-R136-20260627
// Ledger: R136-GOVERNED-DOTNET-FODT-TABLECELL-COLUMNSPAN-001

using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R136: Tests for FodtTableCell.ColumnSpan (table:number-columns-spanned attribute),
/// FodtTableCell.GetPlainText() multi-paragraph joining, and FodtTableRow.CellCount.
/// Uses in-memory XML documents — no fixture files required.
/// ODF spec basis: ODF 1.3 §9.4.5 table:table-cell @table:number-columns-spanned.
/// </summary>
public class FodtR136TableCellColumnSpanTests
{
    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsText   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private const string NsTable  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

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

    private static FodtDocument LoadXml(string xml)
    {
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmp, xml, Encoding.UTF8);
            return FodtDocument.Load(tmp);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    // -------------------------------------------------------------------------
    // FodtTableCell.ColumnSpan — default (no attribute)
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnSpan_NoAttribute_ReturnsOne()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell><text:p>A</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal(1, cell.ColumnSpan);
    }

    // -------------------------------------------------------------------------
    // FodtTableCell.ColumnSpan — explicit attribute value
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnSpan_AttributeTwo_ReturnsTwo()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell table:number-columns-spanned="2"><text:p>Merged</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal(2, cell.ColumnSpan);
    }

    [Fact]
    public void ColumnSpan_AttributeThree_ReturnsThree()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell table:number-columns-spanned="3"><text:p>Wide</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var cell = doc.Tables[0].Rows[0].Cells[0];
        Assert.Equal(3, cell.ColumnSpan);
    }

    // -------------------------------------------------------------------------
    // FodtTableCell.GetPlainText — multi-paragraph joining
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_SingleParagraph_ReturnsText()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell><text:p>Hello</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal("Hello", doc.Tables[0].Rows[0].Cells[0].GetPlainText());
    }

    [Fact]
    public void GetPlainText_TwoParagraphs_JoinedWithNewline()
    {
        var body = """
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
        Assert.Equal("Line1\nLine2", doc.Tables[0].Rows[0].Cells[0].GetPlainText());
    }

    [Fact]
    public void GetPlainText_EmptyCell_ReturnsEmptyString()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell/>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(string.Empty, doc.Tables[0].Rows[0].Cells[0].GetPlainText());
    }

    // -------------------------------------------------------------------------
    // FodtTableRow.CellCount
    // -------------------------------------------------------------------------

    [Fact]
    public void CellCount_ThreeCellRow_ReturnsThree()
    {
        var body = """
    <table:table table:name="T">
      <table:table-row>
        <table:table-cell><text:p>A</text:p></table:table-cell>
        <table:table-cell><text:p>B</text:p></table:table-cell>
        <table:table-cell><text:p>C</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        Assert.Equal(3, doc.Tables[0].Rows[0].CellCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: merge cell header + multi-para note table
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MergedHeaderTable_ColumnSpanAndTextCorrect()
    {
        var body = """
    <table:table table:name="Report">
      <table:table-row>
        <table:table-cell table:number-columns-spanned="3">
          <text:p>Annual Report</text:p>
          <text:p>Confidential</text:p>
        </table:table-cell>
      </table:table-row>
      <table:table-row>
        <table:table-cell><text:p>Q1</text:p></table:table-cell>
        <table:table-cell><text:p>Q2</text:p></table:table-cell>
        <table:table-cell><text:p>Q3</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var table = doc.Tables[0];

        // Row 0: merged header cell
        Assert.Equal(1, table.Rows[0].CellCount);
        Assert.Equal(3, table.Rows[0].Cells[0].ColumnSpan);
        Assert.Equal("Annual Report\nConfidential", table.Rows[0].Cells[0].GetPlainText());

        // Row 1: three normal cells
        Assert.Equal(3, table.Rows[1].CellCount);
        Assert.Equal(1, table.Rows[1].Cells[0].ColumnSpan);
        Assert.Equal("Q1", table.Rows[1].Cells[0].GetPlainText());
        Assert.Equal("Q3", table.Rows[1].Cells[2].GetPlainText());
    }
}
