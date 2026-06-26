// Tests for FodsDocument.GetSheetStats and GetColumnAggregates deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R190

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R190: Tests for FodsDocument.GetSheetStats and GetColumnAggregates deeper coverage.
/// GetSheetStats(sheetName): returns (RowCount, ColCount, CellCount, NonEmptyCellCount).
/// GetColumnAggregates(sheetName, col): returns (Min, Max, Sum, Count).
/// Covers: GetSheetStats RowCount matches GetRowCount; GetSheetStats ColCount matches GetColumnCount;
/// GetSheetStats CellCount matches GetCellCount; GetSheetStats NonEmptyCellCount correct;
/// GetSheetStats on empty sheet; GetColumnAggregates Count correct;
/// GetColumnAggregates Min correct; GetColumnAggregates Max correct;
/// GetColumnAggregates Sum correct; GetColumnAggregates after InsertRowWithValues;
/// GetSheetStats after ClearSheet is zero; GetSheetStats after AddSheet;
/// GetColumnAggregates on single-row; GetColumnAggregates on all-same-value;
/// dogfood CreateNew->SetCells->GetSheetStats->GetColumnAggregates pipeline.
/// </summary>
public class FodsR190GetSheetStatsAndColumnAggregatesTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(1, 2, "82");
        doc.SetCellValue(2, 0, "Carol");
        doc.SetCellValue(2, 1, "Eng");
        doc.SetCellValue(2, 2, "88");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_RowCount_MatchesGetRowCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(doc.GetRowCount(sheetName), stats.RowCount);
    }

    [Fact]
    public void GetSheetStats_ColCount_MatchesGetColumnCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(doc.GetColumnCount(sheetName), stats.ColCount);
    }

    [Fact]
    public void GetSheetStats_CellCount_MatchesGetCellCount()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(doc.GetCellCount(sheetName), stats.CellCount);
    }

    [Fact]
    public void GetSheetStats_NonEmptyCellCount_IsNineForData()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(9, stats.NonEmptyCellCount); // 3x3 all filled
    }

    [Fact]
    public void GetSheetStats_AfterClearSheet_IsZero()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.ClearSheet(sheetName);
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(0, stats.CellCount);
        Assert.Equal(0, stats.NonEmptyCellCount);
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_Count_IsThree()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(3, agg.Count);
    }

    [Fact]
    public void GetColumnAggregates_Min_IsEightyTwo()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(82.0, agg.Min, 0);
    }

    [Fact]
    public void GetColumnAggregates_Max_IsNinetyFive()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(95.0, agg.Max, 0);
    }

    [Fact]
    public void GetColumnAggregates_Sum_IsCorrect()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(95 + 82 + 88, agg.Sum, 0);
    }

    [Fact]
    public void GetColumnAggregates_AfterInsertRowWithValues_CountIncreases()
    {
        var doc = CreateWithData();
        var sheetName = DefaultSheet(doc);
        doc.InsertRowWithValues(sheetName, 3, new[] { "Dave", "Finance", "91" });
        var agg = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(4, agg.Count);
    }

    [Fact]
    public void GetColumnAggregates_AllSameValue_MinEqualsMax()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "50");
        doc.SetCellValue(1, 0, "50");
        doc.SetCellValue(2, 0, "50");
        var agg = doc.GetColumnAggregates(sheetName, 0);
        Assert.Equal(agg.Min, agg.Max, 0);
        Assert.Equal(50.0, agg.Min, 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->GetSheetStats->GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetGetSheetStatsGetColumnAggregates_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];

        // Set 2x3 data
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "10");
        doc.SetCellValue(0, 2, "100");
        doc.SetCellValue(1, 0, "B");
        doc.SetCellValue(1, 1, "20");
        doc.SetCellValue(1, 2, "200");

        // GetSheetStats
        var stats = doc.GetSheetStats(sheetName);
        Assert.Equal(2, stats.RowCount);
        Assert.Equal(3, stats.ColCount);
        Assert.Equal(6, stats.CellCount);
        Assert.Equal(6, stats.NonEmptyCellCount);

        // GetColumnAggregates col1 (10, 20)
        var agg1 = doc.GetColumnAggregates(sheetName, 1);
        Assert.Equal(2, agg1.Count);
        Assert.Equal(10.0, agg1.Min, 0);
        Assert.Equal(20.0, agg1.Max, 0);
        Assert.Equal(30.0, agg1.Sum, 0);

        // GetColumnAggregates col2 (100, 200)
        var agg2 = doc.GetColumnAggregates(sheetName, 2);
        Assert.Equal(2, agg2.Count);
        Assert.Equal(100.0, agg2.Min, 0);
        Assert.Equal(200.0, agg2.Max, 0);
        Assert.Equal(300.0, agg2.Sum, 0);
    }
}
