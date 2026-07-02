// Tests for FodsDocument.GetCellValue dedicated coverage.
// Sprint: ff-sprint-s279-dotnet-deepening-20260630
// Ledger: PC-FODS-R307

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R307: Dedicated tests for FodsDocument.GetCellValue(sheetName, row, col).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Negative row throws exception.
/// Negative col throws exception.
/// Valid call returns non-null.
/// Returns value set by SetCellValue.
/// SheetCount unchanged after GetCellValue.
/// Called twice returns same result.
/// Dogfood: set then get matches.
/// </summary>
public class FodsR307GetCellValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(null!, 0, 0));
    }

    [Fact]
    public void GetCellValue_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("   ", 0, 0));
    }

    [Fact]
    public void GetCellValue_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(sheet, -1, 0));
    }

    [Fact]
    public void GetCellValue_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.GetCellValue(sheet, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "hello");
        string? val = doc.GetCellValue(sheet, 0, 0);
        Assert.NotNull(val);
    }

    [Fact]
    public void GetCellValue_ReturnsValueSetBySetCellValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 1, 2, "TestValue");
        string? val = doc.GetCellValue(sheet, 1, 2);
        Assert.Equal("TestValue", val);
    }

    [Fact]
    public void GetCellValue_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        doc.SetCellValue(sheet, 0, 0, "data");
        _ = doc.GetCellValue(sheet, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellValue_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 0, 0, "stable");
        string? first = doc.GetCellValue(sheet, 0, 0);
        string? second = doc.GetCellValue(sheet, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetThenGet_Matches()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.SetCellValue(sheet, 2, 3, "DogfoodValue");
        string? val = doc.GetCellValue(sheet, 2, 3);
        Assert.Contains("DogfoodValue", val ?? "");
    }
}
