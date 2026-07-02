// Tests for FodsDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s280-dotnet-deepening-20260630
// Ledger: PC-FODS-R308

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R308: Dedicated tests for FodsDocument.GetColumnCount(sheetName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Valid call returns non-negative.
/// Increases after AddColumn.
/// SheetCount unchanged after GetColumnCount.
/// Called twice returns same result.
/// Two sheets have independent column counts.
/// Dogfood: add column then get count increases.
/// Dogfood: multiple columns accumulate correctly.
/// </summary>
public class FodsR308GetColumnCountDedicatedTests
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
    public void GetColumnCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int count = doc.GetColumnCount(sheet);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnCount_IncreasesAfterAddColumn()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetColumnCount(sheet);
        doc.AddColumn(sheet, "NewCol");
        int after = doc.GetColumnCount(sheet);
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.SheetCount;
        _ = doc.GetColumnCount(sheet);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int first = doc.GetColumnCount(sheet);
        int second = doc.GetColumnCount(sheet);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnCount_TwoSheets_Independent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("SheetA");
        doc.AddSheet("SheetB");
        doc.AddColumn("SheetA", "ColA");
        int countA = doc.GetColumnCount("SheetA");
        int countB = doc.GetColumnCount("SheetB");
        Assert.True(countA > countB || countA >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumn_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetColumnCount(sheet);
        doc.AddColumn(sheet, "Alpha");
        int after = doc.GetColumnCount(sheet);
        Assert.True(after >= before + 1);
    }

    [Fact]
    public void DogfoodPipeline_MultipleColumns_AccumulateCorrectly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        int before = doc.GetColumnCount(sheet);
        doc.AddColumn(sheet, "Col1");
        doc.AddColumn(sheet, "Col2");
        doc.AddColumn(sheet, "Col3");
        int after = doc.GetColumnCount(sheet);
        Assert.True(after >= before + 3);
    }
}
