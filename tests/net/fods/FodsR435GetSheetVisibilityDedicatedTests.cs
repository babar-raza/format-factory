// Tests for FodsDocument.GetSheetVisibility dedicated coverage.
// Sprint: ff-sprint-s391-dotnet-deepening-20260630
// Ledger: PC-FODS-R435

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R435: Dedicated tests for FodsDocument.GetSheetVisibility().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetVisibility.
/// Idempotent (called twice same result).
/// Is string type.
/// Dogfood: default sheet visibility non-null.
/// Dogfood: multiple sheets all return non-null visibility.
/// </summary>
public class FodsR435GetSheetVisibilityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
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
        string sheetName = doc.GetSheetName(0);
        string visibility = doc.GetSheetVisibility(sheetName);
        Assert.NotNull(visibility);
    }

    [Fact]
    public void GetSheetVisibility_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetVisibility(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetVisibility_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetSheetVisibility(sheetName);
        string second = doc.GetSheetVisibility(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetVisibility_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string visibility = doc.GetSheetVisibility(sheetName);
        Assert.IsType<string>(visibility);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_VisibilityNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string visibility = doc.GetSheetVisibility(sheetName);
        Assert.NotNull(visibility);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.NotNull(doc.GetSheetVisibility(sheetName));
        }
    }
}
