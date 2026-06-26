// Tests for FodsDocument.FindCellsByValue, GetUsedRange, GetSheetStats, GetColumnAggregates.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R169

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R169: Tests for FodsDocument.FindCellsByValue, GetUsedRange, GetSheetStats, GetColumnAggregates.
/// FindCellsByValue(sheetName, value): returns list of (Row, Col) tuples matching the value.
/// GetUsedRange(): returns (MinRow, MinCol, MaxRow, MaxCol) bounding box or null if empty.
/// GetUsedRange(sheetName): per-sheet version.
/// GetSheetStats(sheetName): returns (RowCount, ColCount, CellCount, NonEmptyCellCount).
/// GetColumnAggregates(sheetName, col): returns (Min, Max, Sum, Count) for numeric column.
/// Covers: FindCellsByValue match found; FindCellsByValue no match returns empty;
/// FindCellsByValue multiple matches; GetUsedRange null for empty sheet;
/// GetUsedRange returns bounding box; GetUsedRange single-cell doc;
/// GetSheetStats RowCount correct; GetSheetStats NonEmptyCellCount correct;
/// GetColumnAggregates sum correct; GetColumnAggregates count correct;
/// dogfood CreateNew->InsertRowWithValues->FindCells->GetUsedRange->GetSheetStats pipeline.
/// </summary>
public class FodsR169FindCellsAndGetUsedRangeTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void FindCellsByValue_MatchFound_ReturnsList()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] { new[] { "Alice", "Eng" }, new[] { "Bob", "Finance" } });
        var results = doc.FindCellsByValue("Data", "Alice");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void FindCellsByValue_NoMatch_ReturnsEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] { new[] { "Alice", "Eng" } });
        var results = doc.FindCellsByValue("Data", "NotExist");
        Assert.Empty(results);
    }

    [Fact]
    public void FindCellsByValue_MultipleMatches_CountCorrect()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Tag" },
            new[] {
                new[] { "Alice", "active" },
                new[] { "Bob", "active" },
                new[] { "Carol", "inactive" }
            });
        var results = doc.FindCellsByValue("Data", "active");
        Assert.Equal(2, results.Count);
    }

    [Fact]
    public void FindCellsByValue_HeaderValue_FoundAtRowZero()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var results = doc.FindCellsByValue("Data", "Name");
        Assert.Contains(results, r => r.Row == 0);
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_EmptySheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        var range = doc.GetUsedRange(sheetName);
        Assert.Null(range);
    }

    [Fact]
    public void GetUsedRange_WithData_ReturnsBoundingBox()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        var range = doc.GetUsedRange("Data");
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_MaxRowIsLastRow()
    {
        var doc = BuildSheet("Data",
            new[] { "X" },
            new[] { new[] { "a" }, new[] { "b" }, new[] { "c" } });
        var range = doc.GetUsedRange("Data");
        Assert.NotNull(range);
        Assert.Equal(3, range!.Value.MaxRow); // 0=header, 1,2,3=data
    }

    [Fact]
    public void GetUsedRange_NoArgs_ReturnsFirstSheetRange()
    {
        var doc = BuildSheet("Main",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
    }

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_RowCount_IsCorrect()
    {
        var doc = BuildSheet("Stats",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" }, new[] { "3", "4" } });
        var stats = doc.GetSheetStats("Stats");
        Assert.Equal(3, stats.RowCount); // header + 2 data rows
    }

    [Fact]
    public void GetSheetStats_NonEmptyCellCount_IsPositive()
    {
        var doc = BuildSheet("Stats",
            new[] { "Col1", "Col2" },
            new[] { new[] { "Val1", "Val2" } });
        var stats = doc.GetSheetStats("Stats");
        Assert.True(stats.NonEmptyCellCount > 0);
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_Sum_IsCorrect()
    {
        var doc = BuildSheet("Nums",
            new[] { "Value" },
            new[] { new[] { "10" }, new[] { "20" }, new[] { "30" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(60.0, agg.Sum, precision: 5);
    }

    [Fact]
    public void GetColumnAggregates_Count_IsCorrect()
    {
        var doc = BuildSheet("Nums",
            new[] { "Value" },
            new[] { new[] { "5" }, new[] { "10" }, new[] { "15" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(3, agg.Count);
    }

    [Fact]
    public void GetColumnAggregates_MinMax_Correct()
    {
        var doc = BuildSheet("Nums",
            new[] { "Value" },
            new[] { new[] { "7" }, new[] { "3" }, new[] { "11" } });
        var agg = doc.GetColumnAggregates("Nums", 0);
        Assert.Equal(3.0, agg.Min, precision: 5);
        Assert.Equal(11.0, agg.Max, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRowWithValues->FindCells->GetUsedRange->GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FindCellsUsedRangeStats_Pipeline()
    {
        var doc = BuildSheet("Pipeline",
            new[] { "Name", "Score", "Tag" },
            new[] {
                new[] { "Alice", "95", "pass" },
                new[] { "Bob", "72", "pass" },
                new[] { "Carol", "85", "pass" },
                new[] { "Dave", "61", "fail" }
            });

        // FindCellsByValue: 3 "pass" cells
        var passCells = doc.FindCellsByValue("Pipeline", "pass");
        Assert.Equal(3, passCells.Count);

        // FindCellsByValue: 1 "fail" cell
        var failCells = doc.FindCellsByValue("Pipeline", "fail");
        Assert.Single(failCells);

        // GetUsedRange: should span all rows and cols
        var range = doc.GetUsedRange("Pipeline");
        Assert.NotNull(range);
        Assert.Equal(4, range!.Value.MaxRow); // rows 0..4

        // GetSheetStats: 5 rows (header + 4 data)
        var stats = doc.GetSheetStats("Pipeline");
        Assert.Equal(5, stats.RowCount);
        Assert.True(stats.NonEmptyCellCount >= 15); // 5 rows * 3 cols

        // GetColumnAggregates on Score column (index 1)
        var agg = doc.GetColumnAggregates("Pipeline", 1);
        Assert.Equal(4, agg.Count);
        Assert.Equal(61.0, agg.Min, precision: 5);
        Assert.Equal(95.0, agg.Max, precision: 5);
    }
}
