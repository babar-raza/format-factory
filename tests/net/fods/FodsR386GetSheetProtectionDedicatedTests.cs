// Tests for FodsDocument.GetSheetProtection dedicated coverage.
// Sprint: ff-sprint-s348-dotnet-deepening-20260630
// Ledger: PC-FODS-R386

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R386: Dedicated tests for FodsDocument.GetSheetProtection().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// New sheet returns false (unprotected).
/// SheetCount unchanged after GetSheetProtection.
/// Idempotent (called twice same result).
/// Dogfood: ProtectSheet then GetSheetProtection returns true.
/// Dogfood: UnprotectSheet then GetSheetProtection returns false.
/// Dogfood: multiple sheets mixed protection states.
/// </summary>
public class FodsR386GetSheetProtectionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtection_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtection(null!));
    }

    [Fact]
    public void GetSheetProtection_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtection("   "));
    }

    [Fact]
    public void GetSheetProtection_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtection("Phantom"));
    }

    [Fact]
    public void GetSheetProtection_NewSheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Open");
        bool isProtected = doc.GetSheetProtection("Open");
        Assert.False(isProtected);
    }

    [Fact]
    public void GetSheetProtection_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Secure");
        int before = doc.SheetCount;
        _ = doc.GetSheetProtection("Secure");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetProtection_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetSheetProtection("Stable");
        bool second = doc.GetSheetProtection("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterProtectSheet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Locked");
        doc.ProtectSheet("Locked");
        bool isProtected = doc.GetSheetProtection("Locked");
        Assert.True(isProtected);
    }

    [Fact]
    public void DogfoodPipeline_AfterUnprotectSheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Editable");
        doc.ProtectSheet("Editable");
        doc.UnprotectSheet("Editable");
        bool isProtected = doc.GetSheetProtection("Editable");
        Assert.False(isProtected);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_MixedProtection()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Protected");
        doc.AddSheet("Unprotected");
        doc.ProtectSheet("Protected");
        Assert.True(doc.GetSheetProtection("Protected"));
        Assert.False(doc.GetSheetProtection("Unprotected"));
    }
}
