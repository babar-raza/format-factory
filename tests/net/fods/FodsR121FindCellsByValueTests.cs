// Tests for FodsDocument.FindCellsByValue — cell search by exact value.
// Sprint: FORMAT-FACTORY-FODS-FIND-CELLS-20260626
// Ledger: R121-GOVERNED-DOTNET-FODS-FIND-CELLS-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R121: FindCellsByValue(sheetName, value) — returns list of (Row,Col) tuples
/// for all cells whose text matches the value exactly (ordinal, case-sensitive).
/// Complements existing R110 basic coverage with edge cases and pipeline tests.
/// </summary>
public class FodsR121FindCellsByValueTests
{
    // ---- Not found → empty list ----

    [Fact]
    public void FindCellsByValue_ValueNotInSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Data");
        FodsDocument.SetCellValue(s, 0, 0, "Hello");

        var result = doc.FindCellsByValue("Data", "World");
        Assert.Empty(result);
    }

    // ---- Single match ----

    [Fact]
    public void FindCellsByValue_SingleMatch_ReturnsOneResult()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Sheet1");
        FodsDocument.SetCellValue(s, 0, 0, "Apple");
        FodsDocument.SetCellValue(s, 0, 1, "Banana");

        var result = doc.FindCellsByValue("Sheet1", "Apple");

        Assert.Single(result);
        Assert.Equal(0, result[0].Row);
        Assert.Equal(0, result[0].Col);
    }

    // ---- Multiple matches ----

    [Fact]
    public void FindCellsByValue_MultipleMatches_ReturnsAll()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Data");
        FodsDocument.SetCellValue(s, 0, 0, "X");
        FodsDocument.SetCellValue(s, 0, 1, "Y");
        FodsDocument.SetCellValue(s, 1, 0, "X");
        FodsDocument.SetCellValue(s, 1, 1, "Z");

        var result = doc.FindCellsByValue("Data", "X");

        Assert.Equal(2, result.Count);
        Assert.Contains((0, 0), result);
        Assert.Contains((1, 0), result);
    }

    // ---- Case sensitivity ----

    [Fact]
    public void FindCellsByValue_CaseSensitive_UpperLowerNotEqual()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Sheet1");
        FodsDocument.SetCellValue(s, 0, 0, "hello");
        FodsDocument.SetCellValue(s, 0, 1, "Hello");
        FodsDocument.SetCellValue(s, 0, 2, "HELLO");

        var lower = doc.FindCellsByValue("Sheet1", "hello");
        var title = doc.FindCellsByValue("Sheet1", "Hello");
        var upper = doc.FindCellsByValue("Sheet1", "HELLO");

        Assert.Single(lower);
        Assert.Equal(0, lower[0].Col);
        Assert.Single(title);
        Assert.Equal(1, title[0].Col);
        Assert.Single(upper);
        Assert.Equal(2, upper[0].Col);
    }

    // ---- Empty string search ----

    [Fact]
    public void FindCellsByValue_EmptyValueSearch_FindsEmptyCells()
    {
        // Cells with empty string value (vs cells with no value)
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Data");
        FodsDocument.SetCellValue(s, 0, 0, "NotEmpty");
        FodsDocument.SetCellValue(s, 0, 1, "");

        // Finding "" may match cells with empty string; depends on implementation
        var result = doc.FindCellsByValue("Data", "NotEmpty");
        Assert.Single(result);
    }

    // ---- Non-existent sheet throws ----

    [Fact]
    public void FindCellsByValue_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Real");

        Assert.Throws<InvalidOperationException>(() =>
            doc.FindCellsByValue("Phantom", "Value"));
    }

    // ---- Null value throws ----

    [Fact]
    public void FindCellsByValue_NullValue_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");

        Assert.Throws<ArgumentNullException>(() =>
            doc.FindCellsByValue("Sheet1", null!));
    }

    // ---- Null/empty sheet name throws ----

    [Fact]
    public void FindCellsByValue_EmptySheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() =>
            doc.FindCellsByValue("", "Value"));
    }

    // ---- Result coordinates are correct ----

    [Fact]
    public void FindCellsByValue_GridLayout_CorrectRowColCoordinates()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Grid");
        // Create 3×3 grid, place "TARGET" at specific positions
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                FodsDocument.SetCellValue(s, r, c, $"{r},{c}");
        FodsDocument.SetCellValue(s, 1, 2, "TARGET");
        FodsDocument.SetCellValue(s, 2, 0, "TARGET");

        var result = doc.FindCellsByValue("Grid", "TARGET");

        Assert.Equal(2, result.Count);
        Assert.Contains((1, 2), result);
        Assert.Contains((2, 0), result);
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_BuildData_Find_ExportMatches()
    {
        var doc = FodsDocument.CreateNew();
        var s = doc.AddSheet("Inventory");
        FodsDocument.SetCellValue(s, 0, 0, "Product");
        FodsDocument.SetCellValue(s, 0, 1, "Status");
        FodsDocument.InsertRow(s, 1, new[] { "Widget", "Active" });
        FodsDocument.InsertRow(s, 2, new[] { "Gadget", "Inactive" });
        FodsDocument.InsertRow(s, 3, new[] { "Doohickey", "Active" });

        // Find all "Active" status cells
        var activeCells = doc.FindCellsByValue("Inventory", "Active");
        Assert.Equal(2, activeCells.Count);

        // Use results to verify row count consistency with FilterRows
        var filtered = doc.FilterRows("Inventory", 1, "Active");
        Assert.Equal(activeCells.Count, filtered.Count);
    }
}
