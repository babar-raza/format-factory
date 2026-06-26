// Tests for FodtDocument.SetTableCellText dedicated coverage.
// Sprint: ff-sprint-s258-dotnet-deepening-20260630
// Ledger: PC-FODT-R273

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R273: Dedicated tests for FodtDocument.SetTableCellText(tableIndex, row, col, text).
/// Negative table index → throws exception.
/// Out-of-bounds table index → throws exception.
/// No tables → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid set → no exception.
/// Text is retrievable via GetTableCellText.
/// TableCount unchanged after set.
/// Set twice → second text wins.
/// Dogfood: set multiple cells in table, each retrievable.
/// Dogfood: set text then overwrite, final value persists.
/// </summary>
public class FodtR273SetTableCellTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(-1, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(count, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, -1, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, 0, -1, "text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_ValidArgs_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        var ex = Record.Exception(() => doc.SetTableCellText(0, 0, 0, "hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableCellText_TextRetrievableViaGet()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 1, 2, "SampleText");
        Assert.Equal("SampleText", doc.GetTableCellText(0, 1, 2));
    }

    [Fact]
    public void SetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        doc.SetTableCellText(0, 0, 0, "value");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SetTableCellText_SetTwice_SecondValueWins()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "first");
        doc.SetTableCellText(0, 0, 0, "second");
        Assert.Equal("second", doc.GetTableCellText(0, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleCells_EachRetrievable()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "TopLeft");
        doc.SetTableCellText(0, 0, 2, "TopRight");
        doc.SetTableCellText(0, 2, 0, "BottomLeft");
        Assert.Equal("TopLeft", doc.GetTableCellText(0, 0, 0));
        Assert.Equal("TopRight", doc.GetTableCellText(0, 0, 2));
        Assert.Equal("BottomLeft", doc.GetTableCellText(0, 2, 0));
    }

    [Fact]
    public void DogfoodPipeline_SetThenOverwrite_FinalValuePersists()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 1, 1, "original");
        doc.SetTableCellText(0, 1, 1, "overwritten");
        string result = doc.GetTableCellText(0, 1, 1);
        Assert.Equal("overwritten", result);
    }
}
