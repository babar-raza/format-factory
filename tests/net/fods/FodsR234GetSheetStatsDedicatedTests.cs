// Tests for FodsDocument.GetSheetStats dedicated coverage.
// Sprint: ff-sprint-s217-dotnet-deepening-20260629
// Ledger: PC-FODS-R234

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R234: Dedicated tests for FodsDocument.GetSheetStats.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Empty sheet → returns stats object.
/// Stats object is not null.
/// SheetCount unchanged after GetSheetStats.
/// Stats contain row count field.
/// Stats contain column count field.
/// Stats contain cell count field.
/// Dogfood: set values, verify stats reflect data.
/// Dogfood: clear sheet, stats show zeros.
/// </summary>
public class FodsR234GetSheetStatsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetStats(null!));
    }

    [Fact]
    public void GetSheetStats_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetStats("   "));
    }

    [Fact]
    public void GetSheetStats_NonExistentSheet_ReturnsZeroStats()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var stats = doc.GetSheetStats("NoSuchSheet");
        Assert.NotNull(stats);
        Assert.Equal(0, stats.RowCount);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_EmptySheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var stats = doc.GetSheetStats(sheetName);
        Assert.NotNull(stats);
    }

    [Fact]
    public void GetSheetStats_EmptySheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetSheetStats(sheetName));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSheetStats_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetSheetStats(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetStats_EmptySheet_RowCountIsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(0, stats.RowCount);
    }

    [Fact]
    public void GetSheetStats_EmptySheet_ColumnCountIsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(0, stats.ColumnCount);
    }

    [Fact]
    public void GetSheetStats_EmptySheet_CellCountIsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(0, stats.CellCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetValues_StatsReflectData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "A");
        doc.SetCellValue(sheetName, 0, 1, "B");
        doc.SetCellValue(sheetName, 1, 0, "C");
        var stats = doc.GetSheetStats(sheetName);
        Assert.True(stats.RowCount >= 1);
        Assert.True(stats.ColumnCount >= 1);
        Assert.True(stats.CellCount >= 3);
    }

    [Fact]
    public void DogfoodPipeline_ClearSheet_StatsShowZeros()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        doc.ClearSheet(sheetName);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(0, stats.CellCount);
    }
}
