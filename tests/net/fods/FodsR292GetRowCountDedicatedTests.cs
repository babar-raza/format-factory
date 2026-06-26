// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s267-dotnet-deepening-20260630
// Ledger: PC-FODS-R292

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R292: Dedicated tests for FodsDocument.GetRowCount(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Valid sheet returns non-negative count.
/// Row count increases after AddRow.
/// SheetCount unchanged after GetRowCount.
/// Called twice returns same result.
/// Dogfood: new sheet has expected initial row count.
/// Dogfood: add multiple rows, count increases accordingly.
/// </summary>
public class FodsR292GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount(null!));
    }

    [Fact]
    public void GetRowCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("   "));
    }

    [Fact]
    public void GetRowCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("DoesNotExist"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int count = doc.GetRowCount("Sheet1");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowCount_AfterAddRow_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.GetRowCount("Sheet1");
        doc.AddRow("Sheet1", new[] { "a", "b", "c" });
        int after = doc.GetRowCount("Sheet1");
        Assert.True(after > before);
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        _ = doc.GetRowCount("Sheet1");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddRow("Sheet1", new[] { "x", "y" });
        int first = doc.GetRowCount("Sheet1");
        int second = doc.GetRowCount("Sheet1");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetRowCount_TwoSheets_IndependentCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddRow("Sheet1", new[] { "a" });
        doc.AddRow("Sheet2", new[] { "b" });
        doc.AddRow("Sheet2", new[] { "c" });
        int count1 = doc.GetRowCount("Sheet1");
        int count2 = doc.GetRowCount("Sheet2");
        Assert.NotEqual(count1, count2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRows_CountMatchesAdded()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int start = doc.GetRowCount("Data");
        doc.AddRow("Data", new[] { "Row1Col1", "Row1Col2" });
        doc.AddRow("Data", new[] { "Row2Col1", "Row2Col2" });
        int end = doc.GetRowCount("Data");
        Assert.Equal(start + 2, end);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRows_CountGrowsMonotonically()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Log");
        int c0 = doc.GetRowCount("Log");
        doc.AddRow("Log", new[] { "entry1" });
        int c1 = doc.GetRowCount("Log");
        doc.AddRow("Log", new[] { "entry2" });
        int c2 = doc.GetRowCount("Log");
        Assert.True(c1 > c0);
        Assert.True(c2 > c1);
    }
}
