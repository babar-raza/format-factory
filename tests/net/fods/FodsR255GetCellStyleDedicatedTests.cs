// Tests for FodsDocument.GetCellStyle dedicated coverage.
// Sprint: ff-sprint-s237-dotnet-deepening-20260629
// Ledger: PC-FODS-R255

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R255: Dedicated tests for FodsDocument.GetCellStyle(sheetName, row, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Empty cell → returns non-null style object.
/// Valid call → no exception.
/// SheetCount unchanged after call.
/// Style for plain cell is non-null.
/// Dogfood: set cell value, get style, verify non-null.
/// </summary>
public class FodsR255GetCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellStyle_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("   ", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle(sheetName, -1, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle(sheetName, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.GetCellStyle(sheetName, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellStyle_PlainCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "PlainText");
        var style = doc.GetCellStyle(sheetName, 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        _ = doc.GetCellStyle(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellStyle_CalledTwice_NonNullBothTimes()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        var style1 = doc.GetCellStyle(sheetName, 0, 0);
        var style2 = doc.GetCellStyle(sheetName, 0, 0);
        Assert.NotNull(style1);
        Assert.NotNull(style2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValue_GetStyle_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Header");
        doc.SetCellValue(sheetName, 0, 1, "Value");
        doc.SetCellValue(sheetName, 1, 0, "Data");
        var style00 = doc.GetCellStyle(sheetName, 0, 0);
        var style01 = doc.GetCellStyle(sheetName, 0, 1);
        Assert.NotNull(style00);
        Assert.NotNull(style01);
    }
}
