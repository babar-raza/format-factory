// Tests for FodsDocument.GetSheetPrintArea dedicated coverage.
// Sprint: ff-sprint-s402-dotnet-deepening-20260701
// Ledger: PC-FODS-R451

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R451: Dedicated tests for FodsDocument.GetSheetPrintArea().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetPrintArea.
/// Idempotent (called twice same result).
/// Is string type.
/// SetPrintArea+GetSheetPrintArea round-trips.
/// Dogfood: default sheet print area non-null.
/// Dogfood: multiple sheets all non-null.
/// </summary>
public class FodsR451GetSheetPrintAreaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetPrintArea_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea(null!));
    }

    [Fact]
    public void GetSheetPrintArea_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("   "));
    }

    [Fact]
    public void GetSheetPrintArea_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetPrintArea_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string area = doc.GetSheetPrintArea(sheetName);
        Assert.NotNull(area);
    }

    [Fact]
    public void GetSheetPrintArea_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetSheetPrintArea(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetPrintArea_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetSheetPrintArea(sheetName);
        string second = doc.GetSheetPrintArea(sheetName);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetPrintArea_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        object area = doc.GetSheetPrintArea(sheetName);
        Assert.IsType<string>(area);
    }

    [Fact]
    public void GetSheetPrintArea_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        doc.SetSheetPrintArea(sheetName, "A1:D10");
        string area = doc.GetSheetPrintArea(sheetName);
        Assert.Equal("A1:D10", area);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultSheet_PrintAreaNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetName(0);
        string area = doc.GetSheetPrintArea(sheetName);
        Assert.NotNull(area);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        for (int i = 0; i < doc.SheetCount; i++)
        {
            string sheetName = doc.GetSheetName(i);
            Assert.NotNull(doc.GetSheetPrintArea(sheetName));
        }
    }
}
