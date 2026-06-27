// Tests for FodsDocument.GetDocumentTitle dedicated coverage.
// Sprint: ff-sprint-s381-dotnet-deepening-20260630
// Ledger: PC-FODS-R424

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R424: Dedicated tests for FodsDocument.GetDocumentTitle().
/// New document returns non-null.
/// SheetCount unchanged after GetDocumentTitle.
/// Idempotent (called twice same result).
/// Returns string type.
/// Dogfood: SetDocumentTitle then Get.
/// Dogfood: SetDocumentTitle Q4 Annual Report 2026 then Get.
/// Dogfood: Set empty string then Get.
/// Dogfood: multiple Set+Get round-trips.
/// </summary>
public class FodsR424GetDocumentTitleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentTitle_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string title = doc.GetDocumentTitle();
        Assert.NotNull(title);
    }

    [Fact]
    public void GetDocumentTitle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetDocumentTitle();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentTitle_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentTitle();
        string second = doc.GetDocumentTitle();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentTitle_ReturnsStringType()
    {
        var doc = FodsDocument.CreateNew();
        object title = doc.GetDocumentTitle();
        Assert.IsType<string>(title);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTitleThenGet_ReturnsTitle()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentTitle("Budget Analysis");
        string title = doc.GetDocumentTitle();
        Assert.Equal("Budget Analysis", title);
    }

    [Fact]
    public void DogfoodPipeline_SetLongTitleThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentTitle("Q4 Annual Report 2026");
        string title = doc.GetDocumentTitle();
        Assert.Equal("Q4 Annual Report 2026", title);
    }

    [Fact]
    public void DogfoodPipeline_SetEmptyStringThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentTitle("");
        string title = doc.GetDocumentTitle();
        Assert.Equal("", title);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSetGetRoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentTitle("Draft");
        Assert.Equal("Draft", doc.GetDocumentTitle());
        doc.SetDocumentTitle("Final");
        Assert.Equal("Final", doc.GetDocumentTitle());
        doc.SetDocumentTitle("Approved");
        Assert.Equal("Approved", doc.GetDocumentTitle());
    }
}
