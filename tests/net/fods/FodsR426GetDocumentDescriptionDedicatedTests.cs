// Tests for FodsDocument.GetDocumentDescription dedicated coverage.
// Sprint: ff-sprint-s383-dotnet-deepening-20260630
// Ledger: PC-FODS-R426

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R426: Dedicated tests for FodsDocument.GetDocumentDescription().
/// New document returns non-null.
/// SheetCount unchanged after GetDocumentDescription.
/// Idempotent (called twice same result).
/// Returns string type.
/// Dogfood: SetDocumentDescription then Get.
/// Dogfood: SetDescription confidential text then Get.
/// Dogfood: Set empty string then Get.
/// Dogfood: multiple Set+Get round-trips.
/// </summary>
public class FodsR426GetDocumentDescriptionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentDescription_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
    }

    [Fact]
    public void GetDocumentDescription_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetDocumentDescription();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentDescription_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentDescription();
        string second = doc.GetDocumentDescription();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentDescription_ReturnsStringType()
    {
        var doc = FodsDocument.CreateNew();
        object desc = doc.GetDocumentDescription();
        Assert.IsType<string>(desc);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetDescriptionThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentDescription("Monthly financial summary");
        string desc = doc.GetDocumentDescription();
        Assert.Equal("Monthly financial summary", desc);
    }

    [Fact]
    public void DogfoodPipeline_SetConfidentialDescriptionThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentDescription("Internal use only — confidential");
        string desc = doc.GetDocumentDescription();
        Assert.Equal("Internal use only — confidential", desc);
    }

    [Fact]
    public void DogfoodPipeline_SetEmptyStringThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentDescription("");
        string desc = doc.GetDocumentDescription();
        Assert.Equal("", desc);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSetGetRoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentDescription("Draft version");
        Assert.Equal("Draft version", doc.GetDocumentDescription());
        doc.SetDocumentDescription("Reviewed version");
        Assert.Equal("Reviewed version", doc.GetDocumentDescription());
        doc.SetDocumentDescription("Final version");
        Assert.Equal("Final version", doc.GetDocumentDescription());
    }
}
