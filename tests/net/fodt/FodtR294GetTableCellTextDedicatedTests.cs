// Tests for FodtDocument.GetTableCellText dedicated coverage.
// Sprint: ff-sprint-s279-dotnet-deepening-20260630
// Ledger: PC-FODT-R294

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R294: Dedicated tests for FodtDocument.GetTableCellText(tableIndex, row, col).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// Returns text set by SetTableCellText.
/// TableCount unchanged after GetTableCellText.
/// Called twice returns same result.
/// Dogfood: set text then get matches.
/// </summary>
public class FodtR294GetTableCellTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellText_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(count, 0, 0));
    }

    [Fact]
    public void GetTableCellText_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, 0, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, -1, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_ValidCall_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "Hello");
        string? text = doc.GetTableCellText(0, 0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetTableCellText_ReturnsTextSetBySetTableCellText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 1, 1, "CellContent");
        string? text = doc.GetTableCellText(0, 1, 1);
        Assert.Contains("CellContent", text ?? "");
    }

    [Fact]
    public void GetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.SetTableCellText(0, 0, 0, "data");
        _ = doc.GetTableCellText(0, 0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "stable");
        string? first = doc.GetTableCellText(0, 0, 0);
        string? second = doc.GetTableCellText(0, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTextThenGet_Matches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 4);
        doc.SetTableCellText(0, 0, 0, "Header");
        doc.SetTableCellText(0, 1, 0, "Row1Col0");
        string? header = doc.GetTableCellText(0, 0, 0);
        string? row1 = doc.GetTableCellText(0, 1, 0);
        Assert.Contains("Header", header ?? "");
        Assert.Contains("Row1Col0", row1 ?? "");
    }
}
