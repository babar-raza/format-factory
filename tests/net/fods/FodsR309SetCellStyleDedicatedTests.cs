// Tests for FodsDocument.SetCellStyle dedicated coverage.
// Sprint: ff-sprint-s281-dotnet-deepening-20260630
// Ledger: PC-FODS-R309

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R309: Dedicated tests for FodsDocument.SetCellStyle(sheetName, row, col, style).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call no exception.
/// SheetCount unchanged after SetCellStyle.
/// Set twice no exception.
/// Dogfood: set bold style no exception.
/// Dogfood: set style on multiple cells no exception.
/// </summary>
public class FodsR309SetCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellStyle(null!, 0, 0, "bold"));
    }

    [Fact]
    public void SetCellStyle_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellStyle("   ", 0, 0, "bold"));
    }

    [Fact]
    public void SetCellStyle_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetCellStyle("NoSuchSheet", 0, 0, "bold"));
    }

    [Fact]
    public void SetCellStyle_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.SetCellStyle(sheet, -1, 0, "bold"));
    }

    [Fact]
    public void SetCellStyle_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.SetCellStyle(sheet, 0, -1, "bold"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() => doc.SetCellStyle(sheet, 0, 0, "bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.SetCellStyle(sheet, 0, 0, "italic");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SetCellStyle_SetTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.SetCellStyle(sheet, 0, 0, "bold");
        var ex = Record.Exception(() => doc.SetCellStyle(sheet, 0, 0, "italic"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetBoldStyle_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "Header");
        var ex = Record.Exception(() => doc.SetCellStyle(sheet, 0, 0, "bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetStyleOnMultipleCells_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        var ex = Record.Exception(() =>
        {
            doc.SetCellStyle(sheet, 0, 0, "bold");
            doc.SetCellStyle(sheet, 0, 1, "italic");
            doc.SetCellStyle(sheet, 1, 0, "underline");
        });
        Assert.Null(ex);
    }
}
