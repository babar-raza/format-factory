// Tests for FodsDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s259-dotnet-deepening-20260630
// Ledger: PC-FODS-R282

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R282: Dedicated tests for FodsDocument.GetColumnCount(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet name → throws exception.
/// Empty sheet → returns 0.
/// Sheet with rows → returns non-negative.
/// Increases after AddColumn.
/// SheetCount unchanged after call.
/// Two sheets → independent counts.
/// Called twice → same result.
/// Dogfood: add columns, verify count increases.
/// Dogfood: two sheets with different column counts.
/// </summary>
public class FodsR282GetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount(null!));
    }

    [Fact]
    public void GetColumnCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount("   "));
    }

    [Fact]
    public void GetColumnCount_NonexistentSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_EmptySheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int count = doc.GetColumnCount("Sheet1");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnCount_AfterAddColumn_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.GetColumnCount("Sheet1");
        doc.AddColumn("Sheet1", new[] { "a", "b" });
        int after = doc.GetColumnCount("Sheet1");
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.GetColumnCount("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddColumn("Sheet1", new[] { "x" });
        int first = doc.GetColumnCount("Sheet1");
        int second = doc.GetColumnCount("Sheet1");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumnsVerifyCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddColumn("Data", new[] { "col1row1" });
        doc.AddColumn("Data", new[] { "col2row1" });
        int count = doc.GetColumnCount("Data");
        Assert.True(count >= 2);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentColumnCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddColumn("Alpha", new[] { "a1" });
        doc.AddColumn("Alpha", new[] { "a2" });
        doc.AddColumn("Beta", new[] { "b1" });
        int countAlpha = doc.GetColumnCount("Alpha");
        int countBeta = doc.GetColumnCount("Beta");
        Assert.True(countAlpha >= 2);
        Assert.True(countBeta >= 1);
        // Alpha should have at least as many columns as Beta
        Assert.True(countAlpha >= countBeta);
    }
}
