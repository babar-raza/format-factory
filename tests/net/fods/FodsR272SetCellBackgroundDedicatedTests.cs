// Tests for FodsDocument.SetCellBackground dedicated coverage.
// Sprint: ff-sprint-s253-dotnet-deepening-20260630
// Ledger: PC-FODS-R272

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R272: Dedicated tests for FodsDocument.SetCellBackground(sheetName, row, col, colorName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid call → no exception.
/// SheetCount unchanged after call.
/// Setting background twice → no exception (second overrides).
/// Multiple cells can have backgrounds set independently.
/// Dogfood: set background, verify SheetCount and CellValue unaffected.
/// Dogfood: set backgrounds on two cells, verify no exception and sheet accessible.
/// </summary>
public class FodsR272SetCellBackgroundDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBackground_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBackground(null!, 0, 0, "Red"));
    }

    [Fact]
    public void SetCellBackground_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBackground("   ", 0, 0, "Blue"));
    }

    [Fact]
    public void SetCellBackground_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellBackground("NoSuchSheet", 0, 0, "Green"));
    }

    [Fact]
    public void SetCellBackground_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellBackground(sheetName, -1, 0, "Yellow"));
    }

    [Fact]
    public void SetCellBackground_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellBackground(sheetName, 0, -1, "Yellow"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBackground_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetCellBackground(sheetName, 0, 0, "LightBlue"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBackground_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.SetCellBackground(sheetName, 0, 0, "Yellow");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellBackground_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellBackground(sheetName, 0, 0, "Red");
        var ex = Record.Exception(() => doc.SetCellBackground(sheetName, 0, 0, "Blue"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBackground_MultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellBackground(sheetName, 0, 0, "Red");
        doc.SetCellBackground(sheetName, 1, 1, "Green");
        doc.SetCellBackground(sheetName, 2, 2, "Blue");
        // All should succeed without exception — verify via SheetCount
        Assert.Equal(1, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetBackground_CellValueUnaffected()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Important Data");
        doc.SetCellBackground(sheetName, 0, 0, "Orange");
        // Cell value should still be intact
        string val = doc.GetCellValue(sheetName, 0, 0);
        Assert.Equal("Important Data", val);
    }

    [Fact]
    public void DogfoodPipeline_TwoCellsBackground_SheetAccessible()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Header1", "Header2" });
        doc.SetCellBackground(sheetName, 0, 0, "LightGray");
        doc.SetCellBackground(sheetName, 0, 1, "LightGreen");
        // Sheet should remain accessible with correct count
        Assert.Equal(1, doc.SheetCount);
        string cell = doc.GetCellValue(sheetName, 0, 0);
        Assert.NotNull(cell);
    }
}
