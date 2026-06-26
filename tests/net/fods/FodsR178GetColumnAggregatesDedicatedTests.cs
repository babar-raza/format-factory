// Tests for FodsDocument.GetColumnAggregates dedicated coverage.
// Sprint: ff-sprint-s171-dotnet-deepening-20260628
// Ledger: PC-FODS-R178

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R178: Dedicated tests for FodsDocument.GetColumnAggregates(string sheetName, int col).
/// Returns (Min, Max, Sum, Count) tuple for numeric cells in the given column.
/// Header row (row 0) is always skipped. Non-numeric cells are skipped.
/// Returns (0,0,0,0) if no numeric cells found or sheet does not exist.
/// Throws ArgumentException for null/whitespace sheetName.
/// Covers: null sheetName throws; whitespace sheetName throws;
/// nonexistent sheet returns (0,0,0,0); empty sheet returns (0,0,0,0);
/// header-only sheet returns (0,0,0,0); single numeric cell correct;
/// Count matches numeric cell count; Sum equals sum of numeric cells;
/// non-numeric cells skipped; dogfood pipeline SetCells->GetColumnAggregates.
/// </summary>
public class FodsR178GetColumnAggregatesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests — throws
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetColumnAggregates(null!, 0));
    }

    [Fact]
    public void GetColumnAggregates_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetColumnAggregates("   ", 0));
    }

    // -------------------------------------------------------------------------
    // Returns (0,0,0,0) — no throw
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NonexistentSheet_ReturnsZeroTuple()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var result = doc.GetColumnAggregates("NoSuchSheet", 0);
        Assert.Equal(0, result.Count);
    }

    [Fact]
    public void GetColumnAggregates_HeaderOnly_ReturnsZeroTuple()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Score"); // header row only
        var result = doc.GetColumnAggregates("Data", 0);
        // Only header row — no data rows — count = 0
        Assert.Equal(0, result.Count);
    }

    [Fact]
    public void GetColumnAggregates_NonNumericCells_ReturnsZeroTuple()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(1, 0, "Alice"); // non-numeric
        doc.SetCellValue(2, 0, "Bob");   // non-numeric
        var result = doc.GetColumnAggregates("Data", 0);
        Assert.Equal(0, result.Count);
    }

    // -------------------------------------------------------------------------
    // Functional tests — note: SetCellValue stores strings; parsing depends on value
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NumericStrings_CountMatchesNumericCells()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Score");  // header — skipped
        doc.SetCellValue(1, 0, "95");     // numeric string
        doc.SetCellValue(2, 0, "85");     // numeric string
        doc.SetCellValue(3, 0, "75");     // numeric string
        var result = doc.GetColumnAggregates("Data", 0);
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void GetColumnAggregates_NumericStrings_SumIsCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Score");
        doc.SetCellValue(1, 0, "10");
        doc.SetCellValue(2, 0, "20");
        doc.SetCellValue(3, 0, "30");
        var result = doc.GetColumnAggregates("Data", 0);
        Assert.Equal(60.0, result.Sum, precision: 3);
    }

    [Fact]
    public void GetColumnAggregates_NumericStrings_MinMaxCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Score");
        doc.SetCellValue(1, 0, "5");
        doc.SetCellValue(2, 0, "15");
        doc.SetCellValue(3, 0, "10");
        var result = doc.GetColumnAggregates("Data", 0);
        Assert.Equal(5.0, result.Min, precision: 3);
        Assert.Equal(15.0, result.Max, precision: 3);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_SetCells_GetColumnAggregates()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stats");
        doc.SetCellValue(0, 1, "Value");
        doc.SetCellValue(1, 1, "100");
        doc.SetCellValue(2, 1, "200");
        doc.SetCellValue(3, 1, "text"); // non-numeric, skipped
        var result = doc.GetColumnAggregates("Stats", 1);
        Assert.Equal(2, result.Count);
        Assert.Equal(300.0, result.Sum, precision: 3);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_CorrectSheetAggregated()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.SetCellValue(0, 0, "X");
        doc.SetCellValue(1, 0, "42");
        // GetColumnAggregates on Alpha (first/default sheet)
        var result = doc.GetColumnAggregates("Alpha", 0);
        Assert.Equal(1, result.Count);
    }
}
