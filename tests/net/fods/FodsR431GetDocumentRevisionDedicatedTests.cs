// Tests for FodsDocument.GetDocumentRevision dedicated coverage.
// Sprint: ff-sprint-s388-dotnet-deepening-20260630
// Ledger: PC-FODS-R431

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R431: Dedicated tests for FodsDocument.GetDocumentRevision().
/// New document returns non-null.
/// Is string type.
/// SheetCount unchanged after GetDocumentRevision.
/// Idempotent (called twice same result).
/// SetDocumentRevision + GetDocumentRevision round-trips.
/// Numeric revision string round-trips.
/// Empty string round-trips.
/// Multiple round-trips stable.
/// Dogfood: version string round-trip.
/// Dogfood: overwrite revision returns latest.
/// </summary>
public class FodsR431GetDocumentRevisionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentRevision_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string revision = doc.GetDocumentRevision();
        Assert.NotNull(revision);
    }

    [Fact]
    public void GetDocumentRevision_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string revision = doc.GetDocumentRevision();
        Assert.IsType<string>(revision);
    }

    [Fact]
    public void GetDocumentRevision_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDocumentRevision();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentRevision_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentRevision();
        string second = doc.GetDocumentRevision();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentRevision_SetRevision_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision("3");
        string result = doc.GetDocumentRevision();
        Assert.Equal("3", result);
    }

    [Fact]
    public void GetDocumentRevision_NumericRevision_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision("42");
        string result = doc.GetDocumentRevision();
        Assert.Equal("42", result);
    }

    [Fact]
    public void GetDocumentRevision_EmptyString_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision(string.Empty);
        string result = doc.GetDocumentRevision();
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetDocumentRevision_MultipleRoundTrips_Stable()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision("5");
        string first = doc.GetDocumentRevision();
        string second = doc.GetDocumentRevision();
        string third = doc.GetDocumentRevision();
        Assert.Equal(first, second);
        Assert.Equal(second, third);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_VersionString_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision("v2.1");
        string revision = doc.GetDocumentRevision();
        Assert.Equal("v2.1", revision);
    }

    [Fact]
    public void DogfoodPipeline_OverwriteRevision_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentRevision("1");
        doc.SetDocumentRevision("2");
        string result = doc.GetDocumentRevision();
        Assert.Equal("2", result);
    }
}
