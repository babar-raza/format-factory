// Tests for FodsDocument.GetDocumentSubject dedicated coverage.
// Sprint: ff-sprint-s384-dotnet-deepening-20260630
// Ledger: PC-FODS-R427

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R427: Dedicated tests for FodsDocument.GetDocumentSubject().
/// New document returns non-null.
/// SheetCount unchanged after GetDocumentSubject.
/// Idempotent (called twice same result).
/// Returns string type.
/// Dogfood: SetDocumentSubject then Get.
/// Dogfood: SetSubject Quarterly Review 2026 then Get.
/// Dogfood: Set empty string then Get.
/// Dogfood: multiple Set+Get round-trips.
/// </summary>
public class FodsR427GetDocumentSubjectDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentSubject_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
    }

    [Fact]
    public void GetDocumentSubject_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetDocumentSubject();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentSubject_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentSubject();
        string second = doc.GetDocumentSubject();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentSubject_ReturnsStringType()
    {
        var doc = FodsDocument.CreateNew();
        object subject = doc.GetDocumentSubject();
        Assert.IsType<string>(subject);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetSubjectThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentSubject("Financial Analysis");
        string subject = doc.GetDocumentSubject();
        Assert.Equal("Financial Analysis", subject);
    }

    [Fact]
    public void DogfoodPipeline_SetQuarterlyReviewThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentSubject("Quarterly Review 2026");
        string subject = doc.GetDocumentSubject();
        Assert.Equal("Quarterly Review 2026", subject);
    }

    [Fact]
    public void DogfoodPipeline_SetEmptyStringThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentSubject("");
        string subject = doc.GetDocumentSubject();
        Assert.Equal("", subject);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSetGetRoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentSubject("Audit");
        Assert.Equal("Audit", doc.GetDocumentSubject());
        doc.SetDocumentSubject("Risk Assessment");
        Assert.Equal("Risk Assessment", doc.GetDocumentSubject());
        doc.SetDocumentSubject("Compliance");
        Assert.Equal("Compliance", doc.GetDocumentSubject());
    }
}
