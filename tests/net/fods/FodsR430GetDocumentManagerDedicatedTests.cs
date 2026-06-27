// Tests for FodsDocument.GetDocumentManager dedicated coverage.
// Sprint: ff-sprint-s387-dotnet-deepening-20260630
// Ledger: PC-FODS-R430

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R430: Dedicated tests for FodsDocument.GetDocumentManager().
/// New document returns non-null.
/// Is string type.
/// SheetCount unchanged after GetDocumentManager.
/// Idempotent (called twice same result).
/// SetDocumentManager + GetDocumentManager round-trips.
/// Long manager name round-trips.
/// Empty string round-trips.
/// Multiple round-trips stable.
/// Dogfood: set manager name and verify.
/// Dogfood: overwrite manager returns latest.
/// </summary>
public class FodsR430GetDocumentManagerDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentManager_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string manager = doc.GetDocumentManager();
        Assert.NotNull(manager);
    }

    [Fact]
    public void GetDocumentManager_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string manager = doc.GetDocumentManager();
        Assert.IsType<string>(manager);
    }

    [Fact]
    public void GetDocumentManager_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        _ = doc.GetDocumentManager();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentManager_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentManager();
        string second = doc.GetDocumentManager();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentManager_SetManager_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentManager("Jane Smith");
        string result = doc.GetDocumentManager();
        Assert.Equal("Jane Smith", result);
    }

    [Fact]
    public void GetDocumentManager_LongName_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string longName = "Director of Finance and Corporate Strategy, North America Division";
        doc.SetDocumentManager(longName);
        string result = doc.GetDocumentManager();
        Assert.Equal(longName, result);
    }

    [Fact]
    public void GetDocumentManager_EmptyString_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentManager(string.Empty);
        string result = doc.GetDocumentManager();
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void GetDocumentManager_MultipleRoundTrips_Stable()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentManager("Alice Johnson");
        string first = doc.GetDocumentManager();
        string second = doc.GetDocumentManager();
        string third = doc.GetDocumentManager();
        Assert.Equal(first, second);
        Assert.Equal(second, third);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetManagerAndVerify()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentManager("Robert Chen");
        string manager = doc.GetDocumentManager();
        Assert.Equal("Robert Chen", manager);
    }

    [Fact]
    public void DogfoodPipeline_OverwriteManager_ReturnsLatest()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentManager("First Manager");
        doc.SetDocumentManager("Updated Manager");
        string result = doc.GetDocumentManager();
        Assert.Equal("Updated Manager", result);
    }
}
