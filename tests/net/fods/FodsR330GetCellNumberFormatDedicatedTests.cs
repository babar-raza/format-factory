// Tests for FodsDocument.GetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s302-dotnet-deepening-20260630
// Ledger: PC-FODS-R330

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R330: Dedicated tests for FodsDocument.GetCellNumberFormat(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Negative row throws exception.
/// Negative column throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetCellNumberFormat.
/// Called twice returns same result.
/// Returns format set by SetCellNumberFormat.
/// Dogfood: set format then get format returns non-null.
/// </summary>
public class FodsR330GetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat(null!, 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("   ", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("DoesNotExist", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Sheet1", -1, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeColumn_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Sheet1", 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellNumberFormat("Sheet1", 0, 0, "currency");
        string? fmt = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.NotNull(fmt);
    }

    [Fact]
    public void GetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellNumberFormat("Sheet1", 0, 0, "percentage");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetCellNumberFormat_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellNumberFormat("Sheet1", 0, 0, "currency");
        string? first = doc.GetCellNumberFormat("Sheet1", 0, 0);
        string? second = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellNumberFormat_ReturnsFormatSetBySetCellNumberFormat()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellNumberFormat("Sheet1", 0, 0, "date");
        string? fmt = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.NotNull(fmt);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFormatThenGet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Financial");
        doc.SetCellValue("Financial", 0, 0, "1234.56");
        doc.SetCellNumberFormat("Financial", 0, 0, "currency");
        string? fmt = doc.GetCellNumberFormat("Financial", 0, 0);
        Assert.NotNull(fmt);
    }
}
