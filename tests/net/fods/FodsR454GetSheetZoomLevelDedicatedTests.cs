// Tests for FodsDocument.GetSheetZoomLevel dedicated coverage.
// Sprint: ff-sprint-s405-dotnet-deepening-20260701
// Ledger: PC-FODS-R454

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R454: Dedicated tests for FodsDocument.GetSheetZoomLevel().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns positive value.
/// SheetCount unchanged after GetSheetZoomLevel.
/// Idempotent (called twice same result).
/// Is int type.
/// SetZoomLevel+GetSheetZoomLevel round-trips.
/// Dogfood: default sheet zoom level positive.
/// Dogfood: multiple sheets all return positive.
/// </summary>
public class FodsR454GetSheetZoomLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetZoomLevel_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel(null!));
    }

    [Fact]
    public void GetSheetZoomLevel_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel("   "));
    }

    [Fact]
    public void GetSheetZoomLevel_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetZoomLevel_ValidSheet_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int zoom = doc.GetSheetZoomLevel(sheetName);
        Assert.True(zoom > 0);
    }

    [Fact]
    public void GetSheetZoomLevel_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetZoomLevel(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetZoomLevel_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetSheetZoomLevel(sheetName);
        int second = doc.GetSheetZoomLevel(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetZoomLevel_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        object result = doc.GetSheetZoomLevel(sheetName);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetSheetZoomLevel_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetSheetZoomLevel(sheetName, 150);
        int zoom = doc.GetSheetZoomLevel(sheetName);
        Assert.Equal(150, zoom);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_ZoomLevelPositive()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int zoom = doc.GetSheetZoomLevel(sheetName);
        Assert.True(zoom > 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.True(doc.GetSheetZoomLevel(sheetName) > 0);
        }
    }
}
