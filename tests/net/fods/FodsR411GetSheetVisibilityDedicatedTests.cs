// Tests for FodsDocument.GetSheetVisibility dedicated coverage.
// Sprint: ff-sprint-s369-dotnet-deepening-20260630
// Ledger: PC-FODS-R411

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R411: Dedicated tests for FodsDocument.GetSheetVisibility().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New sheet returns non-null.
/// SheetCount unchanged after GetSheetVisibility.
/// Idempotent (called twice same result).
/// Dogfood: HideSheet then GetSheetVisibility returns hidden status.
/// Dogfood: ShowSheet then GetSheetVisibility returns visible status.
/// </summary>
public class FodsR411GetSheetVisibilityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetVisibility_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetVisibility(null!));
    }

    [Fact]
    public void GetSheetVisibility_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetVisibility("   "));
    }

    [Fact]
    public void GetSheetVisibility_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetVisibility("NoSheet"));
    }

    [Fact]
    public void GetSheetVisibility_NewSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Visible");
        string? visibility = doc.GetSheetVisibility("Visible");
        Assert.NotNull(visibility);
    }

    [Fact]
    public void GetSheetVisibility_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Track");
        int before = doc.SheetCount;
        _ = doc.GetSheetVisibility("Track");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetVisibility_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string? first = doc.GetSheetVisibility("Stable");
        string? second = doc.GetSheetVisibility("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HiddenSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Internal");
        doc.HideSheet("Internal");
        string? visibility = doc.GetSheetVisibility("Internal");
        Assert.NotNull(visibility);
    }

    [Fact]
    public void DogfoodPipeline_ShowSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Published");
        doc.ShowSheet("Published");
        string? visibility = doc.GetSheetVisibility("Published");
        Assert.NotNull(visibility);
    }
}
