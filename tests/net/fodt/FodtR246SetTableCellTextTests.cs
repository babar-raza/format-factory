// Tests for FodtDocument.SetTableCellText dedicated coverage.
// Sprint: ff-sprint-s231-dotnet-deepening-20260629
// Ledger: PC-FODT-R246

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R246: Dedicated tests for FodtDocument.SetTableCellText(tableIndex, row, col, text).
/// Negative table index → throws exception.
/// OOB table index → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid call → no exception.
/// Text updated: GetTableCellText returns new text.
/// TableCount unchanged after set.
/// Set text twice → latest text returned.
/// Different cells are independent.
/// Dogfood: set multiple cells, all retrievable.
/// </summary>
public class FodtR246SetTableCellTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(-1, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_OobTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(5, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, -1, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, 0, -1, "text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.SetTableCellText(0, 0, 0, "Hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableCellText_TextUpdated_GetReturnsNewText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "UpdatedValue");
        string? text = doc.GetTableCellText(0, 0, 0);
        Assert.Equal("UpdatedValue", text);
    }

    [Fact]
    public void SetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        int before = doc.GetTableCount();
        doc.SetTableCellText(0, 0, 0, "SomeText");
        Assert.Equal(before, doc.GetTableCount());
    }

    [Fact]
    public void SetTableCellText_SetTwice_LatestTextReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "First");
        doc.SetTableCellText(0, 0, 0, "Second");
        string? text = doc.GetTableCellText(0, 0, 0);
        Assert.Equal("Second", text);
    }

    [Fact]
    public void SetTableCellText_DifferentCells_Independent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "CellA");
        doc.SetTableCellText(0, 1, 1, "CellB");
        Assert.Equal("CellA", doc.GetTableCellText(0, 0, 0));
        Assert.Equal("CellB", doc.GetTableCellText(0, 1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleCells_AllRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "R0C0");
        doc.SetTableCellText(0, 0, 1, "R0C1");
        doc.SetTableCellText(0, 1, 0, "R1C0");
        doc.SetTableCellText(0, 2, 2, "R2C2");
        Assert.Equal("R0C0", doc.GetTableCellText(0, 0, 0));
        Assert.Equal("R0C1", doc.GetTableCellText(0, 0, 1));
        Assert.Equal("R1C0", doc.GetTableCellText(0, 1, 0));
        Assert.Equal("R2C2", doc.GetTableCellText(0, 2, 2));
    }
}
