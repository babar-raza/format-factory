// Tests for FodsDocument.SetCellValue dedicated coverage.
// Sprint: ff-sprint-s215-dotnet-deepening-20260629
// Ledger: PC-FODS-R232

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R232: Dedicated tests for FodsDocument.SetCellValue.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Negative row → ArgumentOutOfRangeException.
/// Negative col → ArgumentOutOfRangeException.
/// Set string value → no exception.
/// GetCellValue returns set string value.
/// Set numeric string → no exception.
/// SheetCount unchanged.
/// Different cells independent values.
/// Dogfood: set values grid, verify each cell.
/// </summary>
public class FodsR232SetCellValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellValue(null!, 0, 0, "Val"));
    }

    [Fact]
    public void SetCellValue_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellValue("   ", 0, 0, "Val"));
    }

    [Fact]
    public void SetCellValue_NonExistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SetCellValue("NoSheet", 0, 0, "Val"));
    }

    [Fact]
    public void SetCellValue_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellValue(sheetName, -1, 0, "Val"));
    }

    [Fact]
    public void SetCellValue_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.SetCellValue(sheetName, 0, -1, "Val"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ValidString_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetCellValue(sheetName, 0, 0, "Hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellValue_GetCellValue_ReturnsSetValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Format Factory");
        Assert.Equal("Format Factory", doc.GetCellValue(sheetName, 0, 0));
    }

    [Fact]
    public void SetCellValue_NumericString_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetCellValue(sheetName, 0, 0, "42.5"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Test");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellValue_DifferentCellsIndependent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 1, 1, "Beta");
        Assert.Equal("Alpha", doc.GetCellValue(sheetName, 0, 0));
        Assert.Equal("Beta", doc.GetCellValue(sheetName, 1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetGridValues_EachCellCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                doc.SetCellValue(sheetName, r, c, $"R{r}C{c}");
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.Equal($"R{r}C{c}", doc.GetCellValue(sheetName, r, c));
    }
}
