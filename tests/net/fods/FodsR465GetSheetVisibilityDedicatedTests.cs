// Tests for FodsDocument.GetSheetVisibility dedicated coverage.
// Sprint: ff-sprint-s416-dotnet-deepening-20260701
// Ledger: PC-FODS-R465

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R465: Dedicated tests for FodsDocument.GetSheetVisibility().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null string.
/// SheetCount unchanged after GetSheetVisibility.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetSheetVisibility + GetSheetVisibility round-trips.
/// Dogfood: default sheet visibility non-null.
/// Dogfood: multiple sheets all have non-null visibility.
/// </summary>
public class FodsR465GetSheetVisibilityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
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
    public void GetSheetVisibility_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetVisibility("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetVisibility_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string visibility = doc.GetSheetVisibility("Sheet1");
        Assert.NotNull(visibility);
    }

    [Fact]
    public void GetSheetVisibility_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetVisibility("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetVisibility_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetSheetVisibility("Sheet1");
        string second = doc.GetSheetVisibility("Sheet1");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetVisibility_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetSheetVisibility("Sheet1");
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetSheetVisibility_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hidden");
        doc.SetSheetVisibility("Hidden", "hidden");
        string visibility = doc.GetSheetVisibility("Hidden");
        Assert.Equal("hidden", visibility);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_VisibilityNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string visibility = doc.GetSheetVisibility("Report");
        Assert.NotNull(visibility);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var names = new[] { "Sheet1", "Sheet2", "Sheet3" };
        foreach (var name in names)
        {
            doc.AddSheet(name);
            Assert.NotNull(doc.GetSheetVisibility(name));
        }
    }
}
