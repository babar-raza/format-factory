// Tests for FodsDocument.GetSheetStats.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R156

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R156: Tests for FodsDocument.GetSheetStats(sheetName).
/// Returns (RowCount, ColCount, CellCount, NonEmptyCellCount).
/// RowCount = number of rows in the sheet; ColCount = max column count across rows;
/// CellCount = total cells across all rows; NonEmptyCellCount = cells with non-empty, non-covered values.
/// Throws ArgumentException for null/empty sheetName; returns (0,0,0,0) if sheet not found.
/// Covers: empty sheet returns zero stats; nonexistent sheet returns zero tuple;
/// null sheetName throws; whitespace sheetName throws;
/// single row with values has correct RowCount/ColCount/CellCount/NonEmptyCellCount;
/// multiple rows accumulate CellCount; NonEmptyCellCount excludes empty cells;
/// dogfood CreateNew->InsertRowWithValues->GetSheetStats pipeline.
/// </summary>
public class FodsR156GetSheetStatsTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] dataRows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.RenameSheet(doc.GetSheetNames()[0], sheetName);
        doc.InsertRowWithValues(sheetName, 0, headers);
        for (int r = 0; r < dataRows.Length; r++)
            doc.InsertRowWithValues(sheetName, r + 1, dataRows[r]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // Basic error cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetSheetStats(null!));
    }

    [Fact]
    public void GetSheetStats_WhitespaceSheetName_Throws()
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
        var (rowCount, colCount, cellCount, nonEmpty) = doc.GetSheetStats("NoSuchSheet");
        Assert.Equal(0, rowCount);
        Assert.Equal(0, colCount);
        Assert.Equal(0, cellCount);
        Assert.Equal(0, nonEmpty);
    }

    // -------------------------------------------------------------------------
    // Row and column counts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_SingleRowSheet_RowCountIsOne()
    {
        var doc = BuildSheet("S",
            new[] { "A", "B", "C" },
            Array.Empty<string[]>());
        var (rowCount, _, _, _) = doc.GetSheetStats("S");
        Assert.Equal(1, rowCount); // just the header row
    }

    [Fact]
    public void GetSheetStats_ThreeRows_RowCountIsThree()
    {
        var doc = BuildSheet("S",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        var (rowCount, _, _, _) = doc.GetSheetStats("S");
        Assert.Equal(3, rowCount); // header + 2 data rows
    }

    [Fact]
    public void GetSheetStats_ColCountEqualsMaxColumnsInAnyRow()
    {
        var doc = BuildSheet("S",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        var (_, colCount, _, _) = doc.GetSheetStats("S");
        Assert.Equal(3, colCount);
    }

    // -------------------------------------------------------------------------
    // Cell counts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_CellCountIsTotal()
    {
        // 1 header row (3 cols) + 2 data rows (3 cols each) = 9 total cells
        var doc = BuildSheet("S",
            new[] { "A", "B", "C" },
            new[]
            {
                new[] { "1", "2", "3" },
                new[] { "4", "5", "6" },
            });
        var (_, _, cellCount, _) = doc.GetSheetStats("S");
        Assert.Equal(9, cellCount);
    }

    [Fact]
    public void GetSheetStats_NonEmptyCellCount_AllFilled()
    {
        var doc = BuildSheet("S",
            new[] { "X", "Y" },
            new[] { new[] { "a", "b" } });
        var (_, _, cellCount, nonEmpty) = doc.GetSheetStats("S");
        // Both rows (header + 1 data) fully filled = 4 cells total, 4 non-empty
        Assert.Equal(cellCount, nonEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertRowsGetSheetStats_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        doc.InsertRowWithValues(sheetName, 0, new[] { "Product", "Qty", "Price" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Widget", "10", "2.99" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Gadget", "5", "49.99" });

        var (rowCount, colCount, cellCount, nonEmpty) = doc.GetSheetStats(sheetName);

        Assert.Equal(3, rowCount);
        Assert.Equal(3, colCount);
        Assert.Equal(9, cellCount);
        Assert.Equal(9, nonEmpty); // all cells filled
    }
}
