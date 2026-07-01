// Tests for FodsDocument.GetSheetFreezeColumns dedicated coverage.
// Sprint: ff-sprint-s404-dotnet-deepening-20260701
// Ledger: PC-FODS-R453

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R453: Dedicated tests for FodsDocument.GetSheetFreezeColumns().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-negative value.
/// SheetCount unchanged after GetSheetFreezeColumns.
/// Idempotent (called twice same result).
/// Is int type.
/// SetFreezeColumns+GetSheetFreezeColumns round-trips.
/// Dogfood: default sheet freeze columns non-negative.
/// Dogfood: multiple sheets all return non-negative.
/// </summary>
public class FodsR453GetSheetFreezeColumnsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeColumns_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumns(null!));
    }

    [Fact]
    public void GetSheetFreezeColumns_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumns("   "));
    }

    [Fact]
    public void GetSheetFreezeColumns_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeColumns("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeColumns_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int cols = doc.GetSheetFreezeColumns(sheetName);
        Assert.True(cols >= 0);
    }

    [Fact]
    public void GetSheetFreezeColumns_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetFreezeColumns(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetFreezeColumns_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetSheetFreezeColumns(sheetName);
        int second = doc.GetSheetFreezeColumns(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetFreezeColumns_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        object result = doc.GetSheetFreezeColumns(sheetName);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetSheetFreezeColumns_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetSheetFreezeColumns(sheetName, 2);
        int cols = doc.GetSheetFreezeColumns(sheetName);
        Assert.Equal(2, cols);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_FreezeColumnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int cols = doc.GetSheetFreezeColumns(sheetName);
        Assert.True(cols >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.True(doc.GetSheetFreezeColumns(sheetName) >= 0);
        }
    }
}
