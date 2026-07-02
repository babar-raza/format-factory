// Tests for FodsDocument.GetCellStyle(sheetName, row, col).
// Sprint: FORMAT-FACTORY-FODS-CELL-STYLE-GET-20260626
// Ledger: R126-GOVERNED-DOTNET-FODS-CELL-STYLE-GET-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R126: GetCellStyle(sheetName, row, col) — retrieves the ODF style-name attribute
/// of a cell, or null if no style has been set. SetCellStyle(sheetName, row, col,
/// styleName) is used to set the style first. Tests verify round-trip get, null for
/// unstyled cells, out-of-range returns null, and guards.
/// </summary>
public class FodsR126GetCellStyleTests
{
    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // ---- SetCellStyle then GetCellStyle ----

    [Fact]
    public void GetCellStyle_AfterSetCellStyle_ReturnsStyleName()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "data" });
        doc.SetCellStyle("Sheet1", 0, 0, "Bold");

        var style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.Equal("Bold", style);
    }

    [Fact]
    public void GetCellStyle_AfterSetCellStyle_DifferentCells_CorrectStyle()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B", "C" });
        doc.SetCellStyle("Sheet1", 0, 0, "StyleA");
        doc.SetCellStyle("Sheet1", 0, 2, "StyleC");

        Assert.Equal("StyleA", doc.GetCellStyle("Sheet1", 0, 0));
        Assert.Equal("StyleC", doc.GetCellStyle("Sheet1", 0, 2));
    }

    // ---- Unstyled cell returns null ----

    [Fact]
    public void GetCellStyle_UnstyledCell_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "plain" });

        var style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.Null(style);
    }

    // ---- Style overwrite ----

    [Fact]
    public void GetCellStyle_AfterStyleOverwrite_ReturnsNewStyle()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "cell" });
        doc.SetCellStyle("Sheet1", 0, 0, "OldStyle");
        doc.SetCellStyle("Sheet1", 0, 0, "NewStyle");

        var style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.Equal("NewStyle", style);
    }

    // ---- Out-of-range returns null ----

    [Fact]
    public void GetCellStyle_RowOutOfRange_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "x" });

        Assert.Null(doc.GetCellStyle("Sheet1", 99, 0));
    }

    [Fact]
    public void GetCellStyle_ColOutOfRange_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "x" });

        Assert.Null(doc.GetCellStyle("Sheet1", 0, 99));
    }

    [Fact]
    public void GetCellStyle_NegativeRow_ThrowsOrReturnsNull()
    {
        var doc = MakeDoc();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("Sheet1", -1, 0));
    }

    // ---- Non-existent sheet returns null ----

    [Fact]
    public void GetCellStyle_NonExistentSheet_ThrowsOrReturnsNull()
    {
        var doc = MakeDoc();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("NoSuchSheet", 0, 0));
    }

    // ---- Guard: empty sheet name throws ----

    [Fact]
    public void GetCellStyle_EmptySheetName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() =>
            doc.GetCellStyle("", 0, 0));
    }

    // ---- Dogfood: set styles on multiple rows, get and verify ----

    [Fact]
    public void DogfoodPipeline_MultiRowStyles_EachCellCorrect()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Header" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Value" });

        doc.SetCellStyle("Sheet1", 0, 0, "HeaderStyle");
        doc.SetCellStyle("Sheet1", 1, 0, "DataStyle");

        Assert.Equal("HeaderStyle", doc.GetCellStyle("Sheet1", 0, 0));
        Assert.Equal("DataStyle", doc.GetCellStyle("Sheet1", 1, 0));
        // Unstyled column 1 returns null
        Assert.Null(doc.GetCellStyle("Sheet1", 0, 1));
    }
}
