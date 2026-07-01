// Tests for FodsDocument.GetSheetColumnCount dedicated coverage.
// Sprint: ff-sprint-s395-dotnet-deepening-20260701
// Ledger: PC-FODS-R444

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R444: Dedicated tests for FodsDocument.GetSheetColumnCount().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-negative count.
/// SheetCount unchanged after GetSheetColumnCount.
/// Idempotent (called twice same result).
/// Is integer.
/// Dogfood: default sheet non-negative column count.
/// Dogfood: multiple sheets all non-negative.
/// </summary>
public class FodsR444GetSheetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetColumnCount_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount(null!));
    }

    [Fact]
    public void GetSheetColumnCount_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("   "));
    }

    [Fact]
    public void GetSheetColumnCount_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetColumnCount_ValidSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int count = doc.GetSheetColumnCount(sheetName);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetColumnCount(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetColumnCount_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetSheetColumnCount(sheetName);
        int second = doc.GetSheetColumnCount(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetColumnCount_IsInteger()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int count = doc.GetSheetColumnCount(sheetName);
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int count = doc.GetSheetColumnCount(sheetName);
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.True(doc.GetSheetColumnCount(sheetName) >= 0);
        }
    }
}
