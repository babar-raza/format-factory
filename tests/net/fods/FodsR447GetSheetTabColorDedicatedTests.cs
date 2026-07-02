// Tests for FodsDocument.GetSheetTabColor dedicated coverage.
// Sprint: ff-sprint-s398-dotnet-deepening-20260701
// Ledger: PC-FODS-R447

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R447: Dedicated tests for FodsDocument.GetSheetTabColor().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetTabColor.
/// Idempotent (called twice same result).
/// Is string.
/// SetSheetTabColor + GetSheetTabColor round-trips.
/// Dogfood: default tab color non-null.
/// Dogfood: multiple sheets all non-null tab colors.
/// </summary>
public class FodsR447GetSheetTabColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetTabColor_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor(null!));
    }

    [Fact]
    public void GetSheetTabColor_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("   "));
    }

    [Fact]
    public void GetSheetTabColor_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetTabColor("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetTabColor_ValidSheet_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetSheetTabColor(sheetName);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetSheetTabColor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetTabColor(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetTabColor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetSheetTabColor(sheetName);
        string second = doc.GetSheetTabColor(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetTabColor_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetSheetTabColor(sheetName);
        Assert.IsType<string>(color);
    }

    [Fact]
    public void GetSheetTabColor_SetColor_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetSheetTabColor(sheetName, "#FF0000");
        string color = doc.GetSheetTabColor(sheetName);
        Assert.Equal("#FF0000", color);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_TabColorNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string color = doc.GetSheetTabColor(sheetName);
        Assert.NotNull(color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.NotNull(doc.GetSheetTabColor(sheetName));
        }
    }
}
