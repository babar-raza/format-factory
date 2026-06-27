// Tests for FodsDocument.GetSheetPrintArea dedicated coverage.
// Sprint: ff-sprint-s380-dotnet-deepening-20260630
// Ledger: PC-FODS-R423

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R423: Dedicated tests for FodsDocument.GetSheetPrintArea().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetPrintArea.
/// Idempotent (called twice same result).
/// Dogfood: SetPrintArea A1:D10 then Get.
/// Dogfood: multiple sheets distinct print areas.
/// </summary>
public class FodsR423GetSheetPrintAreaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetPrintArea_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea(null!));
    }

    [Fact]
    public void GetSheetPrintArea_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("   "));
    }

    [Fact]
    public void GetSheetPrintArea_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetPrintArea("Missing"));
    }

    [Fact]
    public void GetSheetPrintArea_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string area = doc.GetSheetPrintArea("Report");
        Assert.NotNull(area);
    }

    [Fact]
    public void GetSheetPrintArea_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetSheetPrintArea("Data");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetPrintArea_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetSheetPrintArea("Stable");
        string second = doc.GetSheetPrintArea("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPrintAreaThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Monthly");
        doc.SetSheetPrintArea("Monthly", "A1:D10");
        string area = doc.GetSheetPrintArea("Monthly");
        Assert.Equal("A1:D10", area);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_DistinctPrintAreas()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Jan");
        doc.AddSheet("Feb");
        doc.AddSheet("Mar");
        doc.SetSheetPrintArea("Jan", "A1:C5");
        doc.SetSheetPrintArea("Feb", "A1:E10");
        doc.SetSheetPrintArea("Mar", "B2:F15");
        Assert.Equal("A1:C5", doc.GetSheetPrintArea("Jan"));
        Assert.Equal("A1:E10", doc.GetSheetPrintArea("Feb"));
        Assert.Equal("B2:F15", doc.GetSheetPrintArea("Mar"));
    }
}
