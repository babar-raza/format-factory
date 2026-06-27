// Tests for FodsDocument.GetDocumentKeywords dedicated coverage.
// Sprint: ff-sprint-s385-dotnet-deepening-20260630
// Ledger: PC-FODS-R428

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R428: Dedicated tests for FodsDocument.GetDocumentKeywords().
/// New document returns non-null.
/// Is string type.
/// SheetCount unchanged after GetDocumentKeywords.
/// Idempotent (called twice same result).
/// SetKeywords + GetDocumentKeywords round-trips.
/// Long keywords string round-trips.
/// Empty string round-trips.
/// Multiple round-trips stable.
/// </summary>
public class FodsR428GetDocumentKeywordsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentKeywords_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string keywords = doc.GetDocumentKeywords();
        Assert.NotNull(keywords);
    }

    [Fact]
    public void GetDocumentKeywords_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string keywords = doc.GetDocumentKeywords();
        Assert.IsType<string>(keywords);
    }

    [Fact]
    public void GetDocumentKeywords_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDocumentKeywords();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentKeywords_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentKeywords();
        string second = doc.GetDocumentKeywords();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentKeywords_SetKeywords_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentKeywords("finance, quarterly, 2026");
        string result = doc.GetDocumentKeywords();
        Assert.Equal("finance, quarterly, 2026", result);
    }

    [Fact]
    public void GetDocumentKeywords_LongKeywords_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string longKeywords = "alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa";
        doc.SetDocumentKeywords(longKeywords);
        string result = doc.GetDocumentKeywords();
        Assert.Equal(longKeywords, result);
    }

    [Fact]
    public void GetDocumentKeywords_EmptyString_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentKeywords(string.Empty);
        string result = doc.GetDocumentKeywords();
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetDocumentKeywords_MultipleRoundTrips_Stable()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentKeywords("spreadsheet, data, analysis");
        string first = doc.GetDocumentKeywords();
        string second = doc.GetDocumentKeywords();
        string third = doc.GetDocumentKeywords();
        Assert.Equal(first, second);
        Assert.Equal(second, third);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAndGet_ReturnsExpected()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentKeywords("budget, forecast, revenue");
        string keywords = doc.GetDocumentKeywords();
        Assert.Equal("budget, forecast, revenue", keywords);
    }

    [Fact]
    public void DogfoodPipeline_OverwriteKeywords_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentKeywords("original, keywords");
        doc.SetDocumentKeywords("updated, keywords, new");
        string result = doc.GetDocumentKeywords();
        Assert.Equal("updated, keywords, new", result);
    }
}
