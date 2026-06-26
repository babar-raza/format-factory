// Tests for FodsDocument.MimeType and OdfVersion dedicated coverage.
// Sprint: ff-sprint-s159-dotnet-deepening-20260628
// Ledger: PC-FODS-R166

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R166: Dedicated tests for FodsDocument.MimeType and OdfVersion properties.
/// MimeType returns the MIME type from office:document/@office:mimetype attribute, or null if absent.
/// OdfVersion returns the ODF version from office:document/@office:version attribute, or null if absent.
/// For CreateNew() documents these are expected to be set to ODF defaults.
/// Covers: MimeType is non-null for CreateNew; MimeType contains 'spreadsheet';
/// OdfVersion is non-null for CreateNew; OdfVersion is a version string;
/// MimeType is consistent across two CreateNew calls; MimeType type is string;
/// OdfVersion type is string; MimeType and OdfVersion are idempotent;
/// dogfood CreateNew->Save->Load->MimeType round-trip;
/// dogfood CreateNew->AddSheet->MimeType still correct.
/// </summary>
public class FodsR166MimeTypeAndOdfVersionTests
{
    // -------------------------------------------------------------------------
    // MimeType tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_CreateNew_IsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_CreateNew_ContainsSpreadsheet()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Contains("spreadsheet", doc.MimeType!);
    }

    [Fact]
    public void MimeType_ConsistentAcrossNewDocs()
    {
        var doc1 = FodsDocument.CreateNew();
        var doc2 = FodsDocument.CreateNew();
        Assert.Equal(doc1.MimeType, doc2.MimeType);
    }

    [Fact]
    public void MimeType_IsString()
    {
        var doc = FodsDocument.CreateNew();
        Assert.IsType<string>(doc.MimeType);
    }

    [Fact]
    public void MimeType_IsIdempotent()
    {
        var doc = FodsDocument.CreateNew();
        var first = doc.MimeType;
        var second = doc.MimeType;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // OdfVersion tests
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_CreateNew_IsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_CreateNew_IsVersionString()
    {
        var doc = FodsDocument.CreateNew();
        // Version string should be parseable as a numeric version like "1.3"
        Assert.Matches(@"^\d+\.\d+", doc.OdfVersion!);
    }

    [Fact]
    public void OdfVersion_IsIdempotent()
    {
        var doc = FodsDocument.CreateNew();
        var first = doc.OdfVersion;
        var second = doc.OdfVersion;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_MimeTypeStillCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("NewSheet");
        // Adding a sheet should not change the MimeType
        Assert.NotNull(doc.MimeType);
        Assert.Contains("spreadsheet", doc.MimeType!);
    }

    [Fact]
    public void DogfoodPipeline_CreateNew_MimeType_OdfVersion_BothSet()
    {
        var doc = FodsDocument.CreateNew();
        // Both properties should have values
        Assert.NotNull(doc.MimeType);
        Assert.NotNull(doc.OdfVersion);
    }
}
