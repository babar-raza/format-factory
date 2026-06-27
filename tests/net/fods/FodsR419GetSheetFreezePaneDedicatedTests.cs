// Tests for FodsDocument.GetSheetFreezePane dedicated coverage.
// Sprint: ff-sprint-s376-dotnet-deepening-20260630
// Ledger: PC-FODS-R419

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R419: Dedicated tests for FodsDocument.GetSheetFreezePane().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Valid sheet returns non-null.
/// SheetCount unchanged after GetSheetFreezePane.
/// Idempotent (called twice same result).
/// Dogfood: SetFreezePane row=1,col=1 then Get.
/// Dogfood: multiple sheets each returns non-null.
/// </summary>
public class FodsR419GetSheetFreezePaneDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetFreezePane_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezePane(null!));
    }

    [Fact]
    public void GetSheetFreezePane_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezePane("   "));
    }

    [Fact]
    public void GetSheetFreezePane_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetFreezePane("Missing"));
    }

    [Fact]
    public void GetSheetFreezePane_ValidSheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("View");
        string pane = doc.GetSheetFreezePane("View");
        Assert.NotNull(pane);
    }

    [Fact]
    public void GetSheetFreezePane_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetSheetFreezePane("Data");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetFreezePane_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetSheetFreezePane("Stable");
        string second = doc.GetSheetFreezePane("Stable");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFreezePaneThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetSheetFreezePane("Report", 1, 1);
        string pane = doc.GetSheetFreezePane("Report");
        Assert.NotNull(pane);
        Assert.NotEmpty(pane);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_EachNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Jan");
        doc.AddSheet("Feb");
        doc.AddSheet("Mar");
        Assert.NotNull(doc.GetSheetFreezePane("Jan"));
        Assert.NotNull(doc.GetSheetFreezePane("Feb"));
        Assert.NotNull(doc.GetSheetFreezePane("Mar"));
    }
}
