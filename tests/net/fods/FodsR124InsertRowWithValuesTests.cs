// Tests for FodsDocument.InsertRowWithValues(sheetName, rowIndex, values).
// Sprint: FORMAT-FACTORY-FODS-INSERT-ROW-VALUES-20260626
// Ledger: R124-GOVERNED-DOTNET-FODS-INSERT-ROW-VALUES-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R124: InsertRowWithValues(sheetName, rowIndex, values) — inserts a new row at
/// the given index and populates columns with the supplied values. Null entries
/// in the list produce empty cells. Tests verify cell population, null handling,
/// index behavior, and guards.
/// </summary>
public class FodsR124InsertRowWithValuesTests
{
    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // ---- Basic: values populate cells ----

    [Fact]
    public void InsertRowWithValues_SingleValue_CellPopulated()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Hello" });
        Assert.Equal("Hello", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void InsertRowWithValues_MultipleValues_AllCellsPopulated()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Alpha", "Beta", "Gamma" });

        Assert.Equal("Alpha", doc.GetCellValue(0, 0));
        Assert.Equal("Beta", doc.GetCellValue(0, 1));
        Assert.Equal("Gamma", doc.GetCellValue(0, 2));
    }

    // ---- Null values produce empty cells ----

    [Fact]
    public void InsertRowWithValues_NullEntry_ProducesEmptyOrNullCell()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new string?[] { "First", null, "Third" });

        Assert.Equal("First", doc.GetCellValue(0, 0));
        // Middle cell should be null/empty
        var middle = doc.GetCellValue(0, 1);
        Assert.True(middle == null || middle == string.Empty,
            $"Expected null or empty for null-value cell, got '{middle}'");
        Assert.Equal("Third", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void InsertRowWithValues_AllNulls_RowExistsWithNullCells()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new string?[] { null, null });
        // Row is inserted; cells are null/empty
        var v0 = doc.GetCellValue(0, 0);
        var v1 = doc.GetCellValue(0, 1);
        Assert.True(v0 == null || v0 == string.Empty);
        Assert.True(v1 == null || v1 == string.Empty);
    }

    // ---- Row index: inserts at correct position ----

    [Fact]
    public void InsertRowWithValues_AtIndex0_BecomesFirstRow()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Existing" });
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Inserted" });

        // "Inserted" was placed at 0; "Existing" shifted to 1
        Assert.Equal("Inserted", doc.GetCellValue(0, 0));
        Assert.Equal("Existing", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void InsertRowWithValues_AtEnd_AppendsBeyondExisting()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Row0" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Row1" });

        Assert.Equal("Row0", doc.GetCellValue(0, 0));
        Assert.Equal("Row1", doc.GetCellValue(1, 0));
    }

    // ---- Empty values list ----

    [Fact]
    public void InsertRowWithValues_EmptyList_DoesNotThrow()
    {
        var doc = MakeDoc();
        var ex = Record.Exception(() =>
            doc.InsertRowWithValues("Sheet1", 0, Array.Empty<string>()));
        Assert.Null(ex);
    }

    // ---- Guard: non-existent sheet throws ----

    [Fact]
    public void InsertRowWithValues_NonExistentSheet_Throws()
    {
        var doc = MakeDoc();
        Assert.Throws<InvalidOperationException>(() =>
            doc.InsertRowWithValues("NoSuch", 0, new[] { "X" }));
    }

    // ---- Guard: empty sheet name throws ----

    [Fact]
    public void InsertRowWithValues_EmptySheetName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() =>
            doc.InsertRowWithValues("", 0, new[] { "X" }));
    }

    // ---- Dogfood: insert multiple rows then export HTML ----

    [Fact]
    public void DogfoodPipeline_InsertMultipleRows_HtmlContainsAllValues()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Alice", "Engineering" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Bob", "Marketing" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Carol", "Finance" });

        var html = doc.ExportSheetToHtml("Sheet1");

        Assert.Contains("Alice", html);
        Assert.Contains("Bob", html);
        Assert.Contains("Carol", html);
        Assert.Contains("Engineering", html);
        Assert.Contains("Marketing", html);
        Assert.Contains("Finance", html);
    }
}
