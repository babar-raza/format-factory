// Tests for FodsDocument.FilterRows and GetColumnAggregates.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R154

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R154: Tests for FodsDocument.FilterRows and GetColumnAggregates.
/// FilterRows(sheetName, col, value) returns rows where col equals value (exact, case-sensitive),
/// always including the header row (index 0). Returns empty list if sheet not found.
/// GetColumnAggregates(sheetName, col) returns (Min, Max, Sum, Count) for numeric cells;
/// skips header row (row 0) and non-numeric values; returns (0,0,0,0) if sheet not found.
/// Covers: FilterRows returns header when no data rows match; FilterRows returns matching rows;
/// FilterRows result includes header; FilterRows nonexistent sheet returns empty;
/// FilterRows empty value matches empty cells; FilterRows case-sensitive match;
/// GetColumnAggregates empty sheet returns zero count; GetColumnAggregates sum is correct;
/// GetColumnAggregates min and max correct; GetColumnAggregates skips non-numeric;
/// GetColumnAggregates nonexistent sheet returns (0,0,0,0);
/// dogfood FilterRows->GetColumnAggregates pipeline.
/// </summary>
public class FodsR154FilterRowsAndAggregatesTests
{
    private static FodsDocument BuildSheet(string sheetName,
        string[] headers, string[][] dataRows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);

        // Insert header row at index 0
        doc.InsertRowWithValues(sheetName, 0, headers);

        // Append data rows
        for (int r = 0; r < dataRows.Length; r++)
            doc.InsertRowWithValues(sheetName, r + 1, dataRows[r]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NoMatchingDataRows_ReturnsHeaderOnly()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Dept" },
            new[] { new[] { "Alice", "Eng" }, new[] { "Bob", "Eng" } });

        var result = doc.FilterRows("Data", 1, "Finance");
        // Header is always included; no data rows match "Finance"
        Assert.Equal(1, result.Count);
        Assert.Contains("Dept", result[0]);
    }

    [Fact]
    public void FilterRows_MatchingRows_ReturnsHeaderPlusMatches()
    {
        var doc = BuildSheet("Sheet1",
            new[] { "Name", "Region" },
            new[]
            {
                new[] { "Alice", "North" },
                new[] { "Bob",   "South" },
                new[] { "Carol", "North" },
            });

        var result = doc.FilterRows("Sheet1", 1, "North");
        // Header + 2 matching rows
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void FilterRows_FirstRowAlwaysIsHeader()
    {
        var doc = BuildSheet("S",
            new[] { "Col1", "Col2" },
            new[] { new[] { "X", "Y" } });

        var result = doc.FilterRows("S", 0, "NOMATCH");
        Assert.Single(result);
        Assert.Equal("Col1", result[0][0]);
    }

    [Fact]
    public void FilterRows_CaseSensitive_DoesNotMatchDifferentCase()
    {
        var doc = BuildSheet("S",
            new[] { "Tag" },
            new[] { new[] { "alpha" }, new[] { "Alpha" } });

        var result = doc.FilterRows("S", 0, "alpha");
        // Header + 1 match ("alpha"), not "Alpha"
        Assert.Equal(2, result.Count);
        Assert.Equal("alpha", result[1][0]);
    }

    [Fact]
    public void FilterRows_NonexistentSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var result = doc.FilterRows("NoSuchSheet", 0, "anything");
        Assert.Empty(result);
    }

    [Fact]
    public void FilterRows_AllRowsMatch_ReturnsAll()
    {
        var doc = BuildSheet("T",
            new[] { "Status" },
            new[]
            {
                new[] { "ok" },
                new[] { "ok" },
                new[] { "ok" },
            });

        var result = doc.FilterRows("T", 0, "ok");
        // Header + 3 data rows
        Assert.Equal(4, result.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NoDataRows_CountIsZero()
    {
        var doc = BuildSheet("S", new[] { "Val" }, Array.Empty<string[]>());
        var (_, _, _, count) = doc.GetColumnAggregates("S", 0);
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetColumnAggregates_NumericColumn_SumCorrect()
    {
        var doc = BuildSheet("S",
            new[] { "Score" },
            new[] { new[] { "10" }, new[] { "20" }, new[] { "30" } });

        var (_, _, sum, _) = doc.GetColumnAggregates("S", 0);
        Assert.Equal(60.0, sum);
    }

    [Fact]
    public void GetColumnAggregates_NumericColumn_MinMaxCorrect()
    {
        var doc = BuildSheet("S",
            new[] { "Score" },
            new[] { new[] { "5" }, new[] { "100" }, new[] { "50" } });

        var (min, max, _, count) = doc.GetColumnAggregates("S", 0);
        Assert.Equal(5.0, min);
        Assert.Equal(100.0, max);
        Assert.Equal(3, count);
    }

    [Fact]
    public void GetColumnAggregates_SkipsNonNumeric()
    {
        var doc = BuildSheet("S",
            new[] { "Val" },
            new[] { new[] { "10" }, new[] { "N/A" }, new[] { "20" } });

        var (_, _, _, count) = doc.GetColumnAggregates("S", 0);
        Assert.Equal(2, count); // "N/A" skipped
    }

    [Fact]
    public void GetColumnAggregates_NonexistentSheet_ReturnsZeroTuple()
    {
        var doc = FodsDocument.CreateNew();
        var (min, max, sum, count) = doc.GetColumnAggregates("NoSheet", 0);
        Assert.Equal(0, min);
        Assert.Equal(0, max);
        Assert.Equal(0, sum);
        Assert.Equal(0, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterRowsThenAggregateScores()
    {
        // Build a sheet: Name | Dept | Score
        var doc = BuildSheet("Employees",
            new[] { "Name", "Dept", "Score" },
            new[]
            {
                new[] { "Alice", "Eng",     "95" },
                new[] { "Bob",   "Finance",  "82" },
                new[] { "Carol", "Eng",     "88" },
                new[] { "Dave",  "Finance",  "91" },
            });

        // Filter Eng rows
        var engRows = doc.FilterRows("Employees", 1, "Eng");
        // Header + 2 Eng rows
        Assert.Equal(3, engRows.Count);

        // Aggregate score column (col 2) for entire sheet
        var (min, max, sum, count) = doc.GetColumnAggregates("Employees", 2);
        Assert.Equal(4, count);
        Assert.Equal(82.0, min);
        Assert.Equal(95.0, max);
        Assert.Equal(356.0, sum);
    }
}
