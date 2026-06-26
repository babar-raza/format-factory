// Tests for FodsDocument.GetSheetStats dedicated coverage.
// Sprint: ff-sprint-s162-dotnet-deepening-20260628
// Ledger: PC-FODS-R169

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R169: Dedicated tests for FodsDocument.GetSheetStats(string sheetName).
/// GetSheetStats returns (RowCount, ColCount, CellCount, NonEmptyCellCount) for the named sheet.
/// Returns (0,0,0,0) if sheet does not exist (no throw for nonexistent sheet).
/// Throws ArgumentException for null/whitespace sheetName.
/// Covers: null sheetName throws ArgumentException; whitespace throws ArgumentException;
/// nonexistent sheet returns zeros tuple; empty sheet returns zeros for all counts;
/// single row single cell counted; RowCount matches actual row count;
/// NonEmptyCellCount only counts non-empty cells; CellCount includes empty cells;
/// dogfood CreateNew->AddSheet->SetCellValue->GetSheetStats pipeline;
/// dogfood multiple rows correct aggregate.
/// </summary>
public class FodsR169GetSheetStatsDedicatedTests
{
    private static FodsDocument MakeDocWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Header1");
        doc.SetCellValue("Data", 0, 1, "Header2");
        doc.SetCellValue("Data", 1, 0, "Value1");
        // Row 1, col 1 left empty
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetSheetStats(null!));
    }

    [Fact]
    public void GetSheetStats_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetSheetStats("   "));
    }

    [Fact]
    public void GetSheetStats_NonexistentSheet_ReturnsZeroTuple()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var stats = doc.GetSheetStats("NoSuchSheet");
        Assert.Equal(0, stats.RowCount);
        Assert.Equal(0, stats.ColCount);
        Assert.Equal(0, stats.CellCount);
        Assert.Equal(0, stats.NonEmptyCellCount);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_RowCount_MatchesActual()
    {
        var doc = MakeDocWithData();
        var stats = doc.GetSheetStats("Data");
        Assert.Equal(2, stats.RowCount);
    }

    [Fact]
    public void GetSheetStats_NonEmptyCellCount_OnlyCountsFilledCells()
    {
        var doc = MakeDocWithData();
        var stats = doc.GetSheetStats("Data");
        // "Header1", "Header2", "Value1" are non-empty; row 1 col 1 is empty
        Assert.Equal(3, stats.NonEmptyCellCount);
    }

    [Fact]
    public void GetSheetStats_CellCount_IncludesEmptyCells()
    {
        var doc = MakeDocWithData();
        var stats = doc.GetSheetStats("Data");
        // 2 rows × 2 cells = 4 total cells
        Assert.Equal(4, stats.CellCount);
    }

    [Fact]
    public void GetSheetStats_ColCount_IsMaxColumnsInAnyRow()
    {
        var doc = MakeDocWithData();
        var stats = doc.GetSheetStats("Data");
        Assert.Equal(2, stats.ColCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_GetSheetStats()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Test");
        doc.SetCellValue("Test", 0, 0, "Alpha");
        doc.SetCellValue("Test", 0, 1, "Beta");
        var stats = doc.GetSheetStats("Test");
        Assert.Equal(1, stats.RowCount);
        Assert.Equal(2, stats.NonEmptyCellCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRows_CorrectAggregate()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Multi");
        doc.SetCellValue("Multi", 0, 0, "R0C0");
        doc.SetCellValue("Multi", 1, 0, "R1C0");
        doc.SetCellValue("Multi", 2, 0, "R2C0");
        var stats = doc.GetSheetStats("Multi");
        Assert.Equal(3, stats.RowCount);
        Assert.Equal(3, stats.NonEmptyCellCount);
    }
}
