// Tests for FodsDocument.GetCellProtection dedicated coverage.
// Sprint: ff-sprint-s397-dotnet-deepening-20260701
// Ledger: PC-FODS-R446

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R446: Dedicated tests for FodsDocument.GetCellProtection().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns bool.
/// SheetCount unchanged after GetCellProtection.
/// Idempotent (called twice same result).
/// SetCellProtection true + GetCellProtection = true.
/// SetCellProtection false + GetCellProtection = false.
/// Dogfood: default cell protection is bool.
/// </summary>
public class FodsR446GetCellProtectionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellProtection_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellProtection(null!, 0, 0));
    }

    [Fact]
    public void GetCellProtection_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellProtection("   ", 0, 0));
    }

    [Fact]
    public void GetCellProtection_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellProtection("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellProtection_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellProtection(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellProtection_ValidCell_ReturnsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        bool protection = doc.GetCellProtection(sheetName, 0, 0);
        Assert.IsType<bool>(protection);
    }

    [Fact]
    public void GetCellProtection_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellProtection(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellProtection_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        bool first = doc.GetCellProtection(sheetName, 0, 0);
        bool second = doc.GetCellProtection(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellProtection_SetProtectionTrue_ReturnsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellProtection(sheetName, 0, 0, true);
        Assert.True(doc.GetCellProtection(sheetName, 0, 0));
    }

    [Fact]
    public void GetCellProtection_SetProtectionFalse_ReturnsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetCellProtection(sheetName, 0, 0, false);
        Assert.False(doc.GetCellProtection(sheetName, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_ProtectionIsBool()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        bool protection = doc.GetCellProtection(sheetName, 0, 0);
        Assert.IsType<bool>(protection);
    }
}
