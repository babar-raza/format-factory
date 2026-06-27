// Tests for FodsDocument.GetDocumentCategory dedicated coverage.
// Sprint: ff-sprint-s386-dotnet-deepening-20260630
// Ledger: PC-FODS-R429

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R429: Dedicated tests for FodsDocument.GetDocumentCategory().
/// New document returns non-null.
/// Is string type.
/// SheetCount unchanged after GetDocumentCategory.
/// Idempotent (called twice same result).
/// SetCategory + GetDocumentCategory round-trips.
/// Long category string round-trips.
/// Empty string round-trips.
/// Multiple round-trips stable.
/// Dogfood: financial category round-trip.
/// Dogfood: overwrite category returns latest.
/// </summary>
public class FodsR429GetDocumentCategoryDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentCategory_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string category = doc.GetDocumentCategory();
        Assert.NotNull(category);
    }

    [Fact]
    public void GetDocumentCategory_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string category = doc.GetDocumentCategory();
        Assert.IsType<string>(category);
    }

    [Fact]
    public void GetDocumentCategory_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDocumentCategory();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentCategory_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentCategory();
        string second = doc.GetDocumentCategory();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentCategory_SetCategory_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentCategory("Finance");
        string result = doc.GetDocumentCategory();
        Assert.Equal("Finance", result);
    }

    [Fact]
    public void GetDocumentCategory_LongCategory_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string longCategory = "Enterprise Resource Planning and Financial Reporting";
        doc.SetDocumentCategory(longCategory);
        string result = doc.GetDocumentCategory();
        Assert.Equal(longCategory, result);
    }

    [Fact]
    public void GetDocumentCategory_EmptyString_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentCategory(string.Empty);
        string result = doc.GetDocumentCategory();
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetDocumentCategory_MultipleRoundTrips_Stable()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentCategory("Operations");
        string first = doc.GetDocumentCategory();
        string second = doc.GetDocumentCategory();
        string third = doc.GetDocumentCategory();
        Assert.Equal(first, second);
        Assert.Equal(second, third);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FinancialCategory_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentCategory("Financial Reports");
        string category = doc.GetDocumentCategory();
        Assert.Equal("Financial Reports", category);
    }

    [Fact]
    public void DogfoodPipeline_OverwriteCategory_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentCategory("Draft");
        doc.SetDocumentCategory("Approved");
        string result = doc.GetDocumentCategory();
        Assert.Equal("Approved", result);
    }
}
