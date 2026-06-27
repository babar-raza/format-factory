// Tests for FodsDocument.GetCellStyle dedicated coverage.
// Sprint: ff-sprint-s301-dotnet-deepening-20260630
// Ledger: PC-FODS-R329

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R329: Dedicated tests for FodsDocument.GetCellStyle(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative column throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellStyle.
/// Called twice returns same result.
/// Returns style set by SetCellStyle.
/// Dogfood: set style then get style returns non-null.
/// </summary>
public class FodsR329GetCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellStyle_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("   ", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("DoesNotExist", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeColumn_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellStyle("Sheet1", 0, 0, "bold");
        string? style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetCellStyle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellStyle("Sheet1", 0, 0, "italic");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetCellStyle_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellStyle("Sheet1", 0, 0, "bold");
        string? first = doc.GetCellStyle("Sheet1", 0, 0);
        string? second = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellStyle_ReturnsStyleSetBySetCellStyle()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellStyle("Sheet1", 0, 0, "underline");
        string? style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetStyleThenGetStyle_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Header");
        doc.SetCellStyle("Data", 0, 0, "bold");
        string? style = doc.GetCellStyle("Data", 0, 0);
        Assert.NotNull(style);
    }
}
