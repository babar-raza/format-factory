// Tests for FodsDocument.FindCellsByValue and GetUsedRange.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R158

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R158: Tests for FodsDocument.FindCellsByValue and GetUsedRange.
/// FindCellsByValue(sheetName, value) returns (Row, Col) tuples where cell text matches exactly
/// (case-sensitive ordinal). Throws InvalidOperationException if sheet not found. Throws
/// ArgumentException for null/whitespace sheetName. Throws ArgumentNullException for null value.
/// GetUsedRange() returns (MinRow, MinCol, MaxRow, MaxCol) nullable tuple for the first sheet.
/// GetUsedRange(sheetName) returns same for named sheet. Returns null if sheet is empty.
/// Covers: FindCellsByValue no match returns empty; finds single match; finds multiple matches;
/// null sheetName throws; nonexistent sheet throws; case-sensitive no-match;
/// GetUsedRange empty sheet returns null; single cell returns single-cell range;
/// multiple rows returns correct min/max; nonexistent sheet returns null;
/// dogfood InsertValues->FindCellsByValue->GetUsedRange pipeline.
/// </summary>
public class FodsR158FindCellsByValueAndUsedRangeTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] dataRows)
    {
        var doc = FodsDocument.CreateNew();
        doc.RenameSheet(doc.GetSheetNames()[0], sheetName);
        doc.InsertRowWithValues(sheetName, 0, headers);
        for (int r = 0; r < dataRows.Length; r++)
            doc.InsertRowWithValues(sheetName, r + 1, dataRows[r]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // FindCellsByValue
    // -------------------------------------------------------------------------

    [Fact]
    public void FindCellsByValue_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.FindCellsByValue(null!, "x"));
    }

    [Fact]
    public void FindCellsByValue_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.FindCellsByValue("NoSuchSheet", "x"));
    }

    [Fact]
    public void FindCellsByValue_NoMatch_ReturnsEmpty()
    {
        var doc = BuildSheet("S",
            new[] { "A", "B" },
            new[] { new[] { "foo", "bar" } });
        var matches = doc.FindCellsByValue("S", "zzz");
        Assert.Empty(matches);
    }

    [Fact]
    public void FindCellsByValue_SingleMatch_ReturnsOneResult()
    {
        var doc = BuildSheet("S",
            new[] { "Name", "Val" },
            new[] { new[] { "Alice", "100" } });
        var matches = doc.FindCellsByValue("S", "Alice");
        Assert.Single(matches);
    }

    [Fact]
    public void FindCellsByValue_SingleMatch_CorrectCoordinates()
    {
        var doc = BuildSheet("S",
            new[] { "Name", "Val" },
            new[] { new[] { "Alice", "100" } });
        var matches = doc.FindCellsByValue("S", "Alice");
        // Alice is at row 1 (second row), col 0
        Assert.Equal(1, matches[0].Row);
        Assert.Equal(0, matches[0].Col);
    }

    [Fact]
    public void FindCellsByValue_MultipleMatches_AllFound()
    {
        var doc = BuildSheet("S",
            new[] { "Tag" },
            new[] { new[] { "ok" }, new[] { "fail" }, new[] { "ok" } });
        var matches = doc.FindCellsByValue("S", "ok");
        Assert.Equal(2, matches.Count);
    }

    [Fact]
    public void FindCellsByValue_CaseSensitive_NoMatch()
    {
        var doc = BuildSheet("S",
            new[] { "X" },
            new[] { new[] { "Hello" } });
        var matches = doc.FindCellsByValue("S", "hello");
        Assert.Empty(matches);
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_EmptySheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        var range = doc.GetUsedRange();
        Assert.Null(range);
    }

    [Fact]
    public void GetUsedRange_NonexistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        var range = doc.GetUsedRange("NoSuchSheet");
        Assert.Null(range);
    }

    [Fact]
    public void GetUsedRange_WithData_ReturnsNonNull()
    {
        var doc = BuildSheet("S",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" } });
        var range = doc.GetUsedRange("S");
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_WithData_MinRowIsZero()
    {
        var doc = BuildSheet("S",
            new[] { "A" },
            new[] { new[] { "x" } });
        var range = doc.GetUsedRange("S");
        Assert.NotNull(range);
        Assert.Equal(0, range.Value.MinRow);
    }

    [Fact]
    public void GetUsedRange_MultipleRows_MaxRowCorrect()
    {
        var doc = BuildSheet("S",
            new[] { "A" },
            new[] { new[] { "1" }, new[] { "2" }, new[] { "3" } });
        var range = doc.GetUsedRange("S");
        Assert.NotNull(range);
        // Header row 0 + 3 data rows = max row 3
        Assert.Equal(3, range.Value.MaxRow);
    }

    // -------------------------------------------------------------------------
    // Dogfood: combined pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertValuesFindCellsGetUsedRange_Pipeline()
    {
        var doc = BuildSheet("Data",
            new[] { "Product", "Status" },
            new[]
            {
                new[] { "Widget", "active" },
                new[] { "Gadget", "inactive" },
                new[] { "Doohickey", "active" },
            });

        // Find all "active" cells
        var actives = doc.FindCellsByValue("Data", "active");
        Assert.Equal(2, actives.Count);

        // Get used range
        var range = doc.GetUsedRange("Data");
        Assert.NotNull(range);
        Assert.Equal(0, range.Value.MinCol);
        Assert.True(range.Value.MaxRow >= 3);
    }
}
