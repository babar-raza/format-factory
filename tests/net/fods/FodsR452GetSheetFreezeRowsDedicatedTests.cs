// Tests for FodsDocument.GetSheetFreezeRows dedicated coverage.
// Sprint: ff-sprint-s403-dotnet-deepening-20260701
// Ledger: PC-FODS-R452

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R452: Dedicated tests for FodsDocument.GetSheetFreezeRows().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-negative value.
/// SheetCount unchanged after GetSheetFreezeRows.
/// Idempotent (called twice same result).
/// Is int type.
/// SetFreezeRows+GetSheetFreezeRows round-trips.
/// Dogfood: default sheet freeze rows non-negative.
/// Dogfood: multiple sheets all return non-negative.
/// </summary>
public class FodsR452GetSheetFreezeRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeRows_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRows(null!));
    }

    [Fact]
    public void GetSheetFreezeRows_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRows("   "));
    }

    [Fact]
    public void GetSheetFreezeRows_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezeRows("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezeRows_ValidSheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int rows = doc.GetSheetFreezeRows(sheetName);
        Assert.True(rows >= 0);
    }

    [Fact]
    public void GetSheetFreezeRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetFreezeRows(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetFreezeRows_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetSheetFreezeRows(sheetName);
        int second = doc.GetSheetFreezeRows(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetFreezeRows_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object result = doc.GetSheetFreezeRows(sheetName);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetSheetFreezeRows_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetSheetFreezeRows(sheetName, 3);
        int rows = doc.GetSheetFreezeRows(sheetName);
        Assert.Equal(3, rows);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_FreezeRowsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        int rows = doc.GetSheetFreezeRows(sheetName);
        Assert.True(rows >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.True(doc.GetSheetFreezeRows(sheetName) >= 0);
        }
    }
}
