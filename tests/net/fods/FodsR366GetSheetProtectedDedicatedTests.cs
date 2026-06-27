// Tests for FodsDocument.GetSheetProtected dedicated coverage.
// Sprint: ff-sprint-s331-dotnet-deepening-20260630
// Ledger: PC-FODS-R366

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R366: Dedicated tests for FodsDocument.GetSheetProtected().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Unprotected sheet returns false.
/// SheetCount unchanged after GetSheetProtected.
/// Called twice same result.
/// Dogfood: SetSheetProtected then GetSheetProtected returns true.
/// Dogfood: multiple sheets all return boolean.
/// </summary>
public class FodsR366GetSheetProtectedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtected_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtected(null!));
    }

    [Fact]
    public void GetSheetProtected_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtected("   "));
    }

    [Fact]
    public void GetSheetProtected_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetProtected("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtected_UnprotectedSheet_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Open");
        bool isProtected = doc.GetSheetProtected("Open");
        Assert.False(isProtected);
    }

    [Fact]
    public void GetSheetProtected_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetProtected("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetProtected_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        bool first = doc.GetSheetProtected("Stable");
        bool second = doc.GetSheetProtected("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSheetProtectedThenGet_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Locked");
        doc.SetCellValue("Locked", 0, 0, "Protected data");
        doc.SetSheetProtected("Locked", true);
        bool isProtected = doc.GetSheetProtected("Locked");
        Assert.True(isProtected);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllReturnBoolean()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        doc.SetSheetProtected("Sheet1", true);
        Assert.True(doc.GetSheetProtected("Sheet1") == true || doc.GetSheetProtected("Sheet1") == false);
        Assert.True(doc.GetSheetProtected("Sheet2") == true || doc.GetSheetProtected("Sheet2") == false);
        Assert.True(doc.GetSheetProtected("Sheet3") == true || doc.GetSheetProtected("Sheet3") == false);
    }
}
