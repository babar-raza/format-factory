// Tests for FodtTable.GetCellText(rowIndex, colIndex) and FodtTable.Name.
// Sprint: FORMAT-FACTORY-FODT-R135-20260627
// Ledger: R135-GOVERNED-DOTNET-FODT-TABLE-GETCELLTEXT-001

using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R135: Tests for FodtTable.GetCellText(rowIndex, colIndex) zero-based cell access
/// and the FodtTable.Name property from the table:name attribute.
/// Uses in-memory XML documents — no fixture files required.
/// ODF spec basis: ODF 1.3 §9.4.2 table:table, §9.4.5 table:table-cell.
/// </summary>
public class FodtR135TableGetCellTextTests
{
    // -------------------------------------------------------------------------
    // Helpers (matching FodtTableTraversalTests pattern)
    // -------------------------------------------------------------------------

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

    private static string TwoByThreeTable(string tableName = "TestTable") =>
        $"""
    <table:table table:name="{tableName}">
      <table:table-row>
        <table:table-cell><text:p>R0C0</text:p></table:table-cell>
        <table:table-cell><text:p>R0C1</text:p></table:table-cell>
        <table:table-cell><text:p>R0C2</text:p></table:table-cell>
      </table:table-row>
      <table:table-row>
        <table:table-cell><text:p>R1C0</text:p></table:table-cell>
        <table:table-cell><text:p>R1C1</text:p></table:table-cell>
        <table:table-cell><text:p>R1C2</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";

    // -------------------------------------------------------------------------
    // FodtTable.Name
    // -------------------------------------------------------------------------

    [Fact]
    public void Name_ReturnsTableNameAttribute()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable("MySheet")));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("MySheet", table.Name);
    }

    [Fact]
    public void Name_DifferentTableName_ReturnsCorrectName()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable("DataGrid")));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("DataGrid", table.Name);
    }

    // -------------------------------------------------------------------------
    // GetCellText — valid indices
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellText_Row0Col0_ReturnsCorrectText()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("R0C0", table.GetCellText(0, 0));
    }

    [Fact]
    public void GetCellText_Row0Col2_ReturnsCorrectText()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("R0C2", table.GetCellText(0, 2));
    }

    [Fact]
    public void GetCellText_Row1Col0_ReturnsCorrectText()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("R1C0", table.GetCellText(1, 0));
    }

    [Fact]
    public void GetCellText_Row1Col1_ReturnsCorrectText()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Equal("R1C1", table.GetCellText(1, 1));
    }

    // -------------------------------------------------------------------------
    // GetCellText — out-of-bounds returns null
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellText_NegativeRow_ReturnsNull()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Null(table.GetCellText(-1, 0));
    }

    [Fact]
    public void GetCellText_RowIndexTooLarge_ReturnsNull()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Null(table.GetCellText(99, 0));
    }

    [Fact]
    public void GetCellText_ColIndexTooLarge_ReturnsNull()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Null(table.GetCellText(0, 99));
    }

    // -------------------------------------------------------------------------
    // RowCount alignment
    // -------------------------------------------------------------------------

    [Fact]
    public void RowCount_TwoRowTable_ReturnsTwo()
    {
        var doc = LoadXml(BuildFodt(TwoByThreeTable()));
        var table = Assert.Single(doc.Tables);
        Assert.Equal(2, table.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: meeting minutes table with cell retrieval pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MeetingMinutesTable_CellValuesCorrect()
    {
        var body = """
    <table:table table:name="MeetingMinutes">
      <table:table-row>
        <table:table-cell><text:p>Date</text:p></table:table-cell>
        <table:table-cell><text:p>Attendee</text:p></table:table-cell>
        <table:table-cell><text:p>Action</text:p></table:table-cell>
      </table:table-row>
      <table:table-row>
        <table:table-cell><text:p>2026-06-27</text:p></table:table-cell>
        <table:table-cell><text:p>Alice</text:p></table:table-cell>
        <table:table-cell><text:p>Review PR</text:p></table:table-cell>
      </table:table-row>
      <table:table-row>
        <table:table-cell><text:p>2026-06-27</text:p></table:table-cell>
        <table:table-cell><text:p>Bob</text:p></table:table-cell>
        <table:table-cell><text:p>Deploy staging</text:p></table:table-cell>
      </table:table-row>
    </table:table>
""";
        var doc = LoadXml(BuildFodt(body));
        var table = Assert.Single(doc.Tables);

        // Name
        Assert.Equal("MeetingMinutes", table.Name);

        // RowCount
        Assert.Equal(3, table.RowCount);

        // Header row
        Assert.Equal("Date",     table.GetCellText(0, 0));
        Assert.Equal("Attendee", table.GetCellText(0, 1));
        Assert.Equal("Action",   table.GetCellText(0, 2));

        // Data rows
        Assert.Equal("Alice",          table.GetCellText(1, 1));
        Assert.Equal("Deploy staging", table.GetCellText(2, 2));

        // Out-of-bounds column
        Assert.Null(table.GetCellText(1, 5));
    }
}
