// Tests for FodsDocument.GetSheetTabColor dedicated coverage.
// Sprint: ff-sprint-s415-dotnet-deepening-20260701
// Ledger: PC-FODS-R464

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R464: Dedicated tests for FodsDocument.GetSheetTabColor().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null string.
/// SheetCount unchanged after GetSheetTabColor.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetSheetTabColor + GetSheetTabColor round-trips.
/// Dogfood: default tab color non-null.
/// Dogfood: multiple sheets all have non-null tab color.
/// </summary>
public class FodsR464GetSheetTabColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetTabColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor(null!));
    }

    [Fact]
    public void GetSheetTabColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("   "));
    }

    [Fact]
    public void GetSheetTabColor_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetTabColor_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string color = doc.GetSheetTabColor("Sheet1");
        Assert.NotNull(color);
    }

    [Fact]
    public void GetSheetTabColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetTabColor("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetTabColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetSheetTabColor("Sheet1");
        string second = doc.GetSheetTabColor("Sheet1");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetTabColor_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetSheetTabColor("Sheet1");
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetSheetTabColor_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Summary");
        doc.SetSheetTabColor("Summary", "#FF5733");
        string color = doc.GetSheetTabColor("Summary");
        Assert.Equal("#FF5733", color);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_TabColorNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string color = doc.GetSheetTabColor("Report");
        Assert.NotNull(color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var names = new[] { "Alpha", "Beta", "Gamma" };
        foreach (var name in names)
        {
            doc.AddSheet(name);
            Assert.NotNull(doc.GetSheetTabColor(name));
        }
    }
}
