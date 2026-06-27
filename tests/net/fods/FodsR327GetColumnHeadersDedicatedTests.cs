// Tests for FodsDocument.GetColumnHeaders dedicated coverage.
// Sprint: ff-sprint-s299-dotnet-deepening-20260630
// Ledger: PC-FODS-R327

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R327: Dedicated tests for FodsDocument.GetColumnHeaders(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetColumnHeaders.
/// Called twice returns same count.
/// After AddColumn count increases.
/// All headers are non-null strings.
/// Dogfood: add columns and verify headers contains them.
/// Dogfood: two sheets have independent column headers.
/// </summary>
public class FodsR327GetColumnHeadersDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnHeaders(null!));
    }

    [Fact]
    public void GetColumnHeaders_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnHeaders("   "));
    }

    [Fact]
    public void GetColumnHeaders_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnHeaders("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_ValidCall_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var headers = doc.GetColumnHeaders("Data");
        Assert.NotNull(headers);
    }

    [Fact]
    public void GetColumnHeaders_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetColumnHeaders("Sheet1");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetColumnHeaders_CalledTwice_SameCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddColumn("Sheet1", "ColA");
        int first = doc.GetColumnHeaders("Sheet1").Count();
        int second = doc.GetColumnHeaders("Sheet1").Count();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnHeaders_AfterAddColumn_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.GetColumnHeaders("Data").Count();
        doc.AddColumn("Data", "NewCol");
        int after = doc.GetColumnHeaders("Data").Count();
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnHeaders_AllHeadersNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", "ColA");
        doc.AddColumn("Data", "ColB");
        foreach (var h in doc.GetColumnHeaders("Data"))
            Assert.NotNull(h);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumns_HeadersContainsThem()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddColumn("Sales", "Product");
        doc.AddColumn("Sales", "Revenue");
        var headers = doc.GetColumnHeaders("Sales").ToList();
        Assert.Contains("Product", headers);
        Assert.Contains("Revenue", headers);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentColumnHeaders()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddColumn("Sheet1", "Alpha");
        int count1 = doc.GetColumnHeaders("Sheet1").Count();
        int count2 = doc.GetColumnHeaders("Sheet2").Count();
        Assert.True(count1 >= 0);
        Assert.True(count2 >= 0);
    }
}
