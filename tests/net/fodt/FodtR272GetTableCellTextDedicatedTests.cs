// Tests for FodtDocument.GetTableCellText dedicated coverage.
// Sprint: ff-sprint-s257-dotnet-deepening-20260630
// Ledger: PC-FODT-R272

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R272: Dedicated tests for FodtDocument.GetTableCellText(tableIndex, row, col).
/// Negative table index → throws exception.
/// Out-of-bounds table index → throws exception.
/// No tables → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Out-of-bounds row → throws exception.
/// Out-of-bounds col → throws exception.
/// Valid cell → returns string (non-null, possibly empty).
/// After SetTableCellText, returns the set text.
/// TableCount unchanged after call.
/// Dogfood: set text then get it back.
/// Dogfood: multiple cells independent.
/// </summary>
public class FodtR272GetTableCellTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellText_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
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
    public void GetTableCellText_ValidCell_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        string? text = doc.GetTableCellText(0, 0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetTableCellText_AfterSetTableCellText_ReturnsSetText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "HelloCell");
        string text = doc.GetTableCellText(0, 0, 0);
        Assert.Equal("HelloCell", text);
    }

    [Fact]
    public void GetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        doc.GetTableCellText(0, 0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetThenGet_TextRoundTrips()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 1, 2, "CellContent");
        string result = doc.GetTableCellText(0, 1, 2);
        Assert.Equal("CellContent", result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_Independent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "Alpha");
        doc.SetTableCellText(0, 1, 1, "Beta");
        doc.SetTableCellText(0, 2, 2, "Gamma");
        Assert.Equal("Alpha", doc.GetTableCellText(0, 0, 0));
        Assert.Equal("Beta", doc.GetTableCellText(0, 1, 1));
        Assert.Equal("Gamma", doc.GetTableCellText(0, 2, 2));
    }
}
