// Tests for FodsDocument.GetSheetZoomLevel dedicated coverage.
// Sprint: ff-sprint-s377-dotnet-deepening-20260630
// Ledger: PC-FODS-R420

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R420: Dedicated tests for FodsDocument.GetSheetZoomLevel().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New sheet returns positive value.
/// SheetCount unchanged after GetSheetZoomLevel.
/// Idempotent (called twice same result).
/// Dogfood: SetZoomLevel 150+Get=150.
/// Dogfood: multiple sheets distinct zoom levels.
/// </summary>
public class FodsR420GetSheetZoomLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
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
    public void GetSheetZoomLevel_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetZoomLevel("Missing"));
    }

    [Fact]
    public void GetSheetZoomLevel_NewSheet_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("View");
        int zoom = doc.GetSheetZoomLevel("View");
        Assert.True(zoom > 0);
    }

    [Fact]
    public void GetSheetZoomLevel_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetSheetZoomLevel("Data");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetZoomLevel_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        int first = doc.GetSheetZoomLevel("Stable");
        int second = doc.GetSheetZoomLevel("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetZoomLevel150ThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetSheetZoomLevel("Report", 150);
        int zoom = doc.GetSheetZoomLevel("Report");
        Assert.Equal(150, zoom);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_DistinctZoomLevels()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Summary");
        doc.AddSheet("Detail");
        doc.AddSheet("Chart");
        doc.SetSheetZoomLevel("Summary", 100);
        doc.SetSheetZoomLevel("Detail", 125);
        doc.SetSheetZoomLevel("Chart", 75);
        Assert.Equal(100, doc.GetSheetZoomLevel("Summary"));
        Assert.Equal(125, doc.GetSheetZoomLevel("Detail"));
        Assert.Equal(75, doc.GetSheetZoomLevel("Chart"));
    }
}
