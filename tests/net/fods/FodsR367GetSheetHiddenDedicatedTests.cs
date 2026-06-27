// Tests for FodsDocument.GetSheetHidden dedicated coverage.
// Sprint: ff-sprint-s332-dotnet-deepening-20260630
// Ledger: PC-FODS-R367

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R367: Dedicated tests for FodsDocument.GetSheetHidden().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Visible sheet returns false.
/// SheetCount unchanged after GetSheetHidden.
/// Called twice same result.
/// Dogfood: HideSheet then GetSheetHidden returns true.
/// Dogfood: multiple sheets all return boolean.
/// </summary>
public class FodsR367GetSheetHiddenDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetHidden_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetHidden(null!));
    }

    [Fact]
    public void GetSheetHidden_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetHidden("   "));
    }

    [Fact]
    public void GetSheetHidden_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetHidden("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetHidden_VisibleSheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Visible");
        bool isHidden = doc.GetSheetHidden("Visible");
        Assert.False(isHidden);
    }

    [Fact]
    public void GetSheetHidden_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetHidden("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetHidden_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetSheetHidden("Stable");
        bool second = doc.GetSheetHidden("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HideSheetThenGet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Hidden");
        doc.SetCellValue("Hidden", 0, 0, "Internal data");
        doc.HideSheet("Hidden");
        bool isHidden = doc.GetSheetHidden("Hidden");
        Assert.True(isHidden);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllReturnBoolean()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Visible1");
        doc.AddSheet("Visible2");
        doc.AddSheet("Hidden1");
        doc.HideSheet("Hidden1");
        Assert.False(doc.GetSheetHidden("Visible1"));
        Assert.False(doc.GetSheetHidden("Visible2"));
        Assert.True(doc.GetSheetHidden("Hidden1"));
    }
}
