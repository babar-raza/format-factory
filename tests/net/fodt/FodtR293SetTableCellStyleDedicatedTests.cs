// Tests for FodtDocument.SetTableCellStyle dedicated coverage.
// Sprint: ff-sprint-s278-dotnet-deepening-20260630
// Ledger: PC-FODT-R293

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R293: Dedicated tests for FodtDocument.SetTableCellStyle(tableIndex, row, col, style).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// TableCount unchanged after SetTableCellStyle.
/// Set twice no exception.
/// Dogfood: add table, set style, no exception.
/// Dogfood: set style on multiple cells no exception.
/// </summary>
public class FodtR293SetTableCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellStyle_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellStyle(-1, 0, 0, "bold"));
    }

    [Fact]
    public void SetTableCellStyle_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellStyle(count, 0, 0, "bold"));
    }

    [Fact]
    public void SetTableCellStyle_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellStyle(0, 0, 0, "bold"));
    }

    [Fact]
    public void SetTableCellStyle_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellStyle(0, -1, 0, "bold"));
    }

    [Fact]
    public void SetTableCellStyle_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellStyle(0, 0, -1, "bold"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellStyle_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.SetTableCellStyle(0, 0, 0, "bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableCellStyle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.SetTableCellStyle(0, 0, 0, "italic");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SetTableCellStyle_SetTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellStyle(0, 0, 0, "bold");
        var ex = Record.Exception(() => doc.SetTableCellStyle(0, 0, 0, "italic"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableSetStyle_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 4);
        var ex = Record.Exception(() =>
        {
            doc.SetTableCellStyle(0, 0, 0, "bold");
            doc.SetTableCellText(0, 0, 0, "Header");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetStyleOnMultipleCells_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() =>
        {
            doc.SetTableCellStyle(0, 0, 0, "bold");
            doc.SetTableCellStyle(0, 0, 1, "italic");
            doc.SetTableCellStyle(0, 1, 0, "underline");
            doc.SetTableCellStyle(0, 1, 1, "bold");
        });
        Assert.Null(ex);
    }
}
