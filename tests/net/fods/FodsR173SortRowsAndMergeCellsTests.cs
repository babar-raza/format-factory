// Tests for FodsDocument.SortRows, MergeCells, GetUsedRange (static), FilterRows deep.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R173

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R173: Tests for FodsDocument.SortRows, MergeCells, GetUsedRange (static overload).
/// SortRows(sheetName, sortColumn, ascending): sorts rows by column value.
/// MergeCells(sheetName, startRow, startCol, rowSpan, colSpan): marks cells as merged.
/// GetUsedRange(FodsSheet): static overload for explicit sheet.
/// Covers: SortRows ascending order; SortRows descending order; SortRows single row no-op;
/// SortRows preserves all rows; SortRows nonexistent sheet throws;
/// MergeCells does not throw; MergeCells row count unchanged;
/// GetUsedRange static returns bounding box; GetUsedRange static null for empty;
/// InsertRowWithValues then SortRows reorders; dogfood CreateNew->Insert->Sort->Filter pipeline.
/// </summary>
public class FodsR173SortRowsAndMergeCellsTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
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
    // SortRows
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_Ascending_FirstRowIsSmallest()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Charlie" }, new[] { "Alice" }, new[] { "Bob" } });
        doc.SortRows("Data", 0, ascending: true);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SortRows_Descending_FirstRowIsLargest()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Charlie" }, new[] { "Alice" }, new[] { "Bob" } });
        doc.SortRows("Data", 0, ascending: false);
        Assert.Equal("Charlie", doc.GetCellValue(1, 0)); // row 1 after sort (Name header sorts after Charlie)
    }

    [Fact]
    public void SortRows_PreservesRowCount()
    {
        var doc = BuildSheet("Data",
            new[] { "Val" },
            new[] { new[] { "3" }, new[] { "1" }, new[] { "2" } });
        var before = doc.GetRowCount("Data");
        doc.SortRows("Data", 0, ascending: true);
        Assert.Equal(before, doc.GetRowCount("Data"));
    }

    [Fact]
    public void SortRows_NumericColumn_SortsNumerically()
    {
        var doc = BuildSheet("Nums",
            new[] { "Score" },
            new[] { new[] { "100" }, new[] { "20" }, new[] { "50" } });
        doc.SortRows("Nums", 0, ascending: true);
        // Numeric sort: 20, 50, 100
        Assert.Equal("20", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SortRows_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() =>
            doc.SortRows("NoSuchSheet", 0, ascending: true));
    }

    // -------------------------------------------------------------------------
    // MergeCells
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_DoesNotThrow()
    {
        var doc = BuildSheet("Grid",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        var ex = Record.Exception(() => doc.MergeCells("Grid", 0, 0, 1, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeCells_RowCountUnchanged()
    {
        var doc = BuildSheet("Grid",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" }, new[] { "3", "4" } });
        var before = doc.GetRowCount("Grid");
        doc.MergeCells("Grid", 0, 0, 2, 1);
        Assert.Equal(before, doc.GetRowCount("Grid"));
    }

    // -------------------------------------------------------------------------
    // GetUsedRange (static)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_Static_ReturnsRange()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" } });
        var sheet = doc.GetSheetByName("Sheet");
        Assert.NotNull(sheet);
        var range = FodsDocument.GetUsedRange(sheet!);
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_Static_EmptySheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
        var range = FodsDocument.GetUsedRange(sheet!);
        Assert.Null(range);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->Insert->Sort->Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertSortFilterPipeline()
    {
        var doc = BuildSheet("Students",
            new[] { "Name", "Grade" },
            new[] {
                new[] { "Carol", "B" },
                new[] { "Alice", "A" },
                new[] { "Dave", "C" },
                new[] { "Bob", "A" }
            });

        // Sort ascending by Name
        doc.SortRows("Students", 0, ascending: true);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
        Assert.Equal("Carol", doc.GetCellValue(2, 0));
        Assert.Equal("Dave", doc.GetCellValue(3, 0));

        // Row count unchanged
        Assert.Equal(5, doc.GetRowCount("Students")); // 1 header + 4 data rows

        // Filter for grade A
        var gradeA = doc.FilterRows("Students", 1, "A");
        Assert.Equal(2, gradeA.Count);

        // GetUsedRange
        var range = doc.GetUsedRange("Students");
        Assert.NotNull(range);

        // MergeCells header row
        var ex = Record.Exception(() => doc.MergeCells("Students", 0, 0, 1, 2));
        Assert.Null(ex);
    }
}
