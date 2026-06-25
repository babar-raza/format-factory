// Tests for FodsDocument.MimeType and OdfVersion document metadata properties.
// Sprint: FORMAT-FACTORY-FODS-DOCUMENT-METADATA-20260626
// Ledger: R131-GOVERNED-DOTNET-FODS-DOCUMENT-METADATA-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R131: FodsDocument.MimeType returns the ODF spreadsheet MIME type string.
/// FodsDocument.OdfVersion returns the ODF specification version string (non-null).
/// Both properties are stable across multiple accesses and survive round-trips through
/// InsertRowWithValues mutations (document content changes do not alter metadata).
/// </summary>
public class FodsR131DocumentMetadataTests
{
    // ---- MimeType: value and format ----

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
        Assert.Contains("spreadsheet", doc.MimeType, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void MimeType_CreateNew_ContainsOasis()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Contains("oasis", doc.MimeType, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void MimeType_IsStableAcrossAccesses()
    {
        var doc = FodsDocument.CreateNew();
        var first  = doc.MimeType;
        var second = doc.MimeType;
        Assert.Equal(first, second);
    }

    // ---- MimeType: survives mutations ----

    [Fact]
    public void MimeType_AfterInsertRow_Unchanged()
    {
        var doc = FodsDocument.CreateNew();
        var before = doc.MimeType;

        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B", "C" });

        Assert.Equal(before, doc.MimeType);
    }

    // ---- OdfVersion: value ----

    [Fact]
    public void OdfVersion_CreateNew_IsNotNull()
    {
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_CreateNew_IsNonEmptyString()
    {
        var doc = FodsDocument.CreateNew();
        Assert.False(string.IsNullOrWhiteSpace(doc.OdfVersion),
            "OdfVersion should be a non-empty version string");
    }

    [Fact]
    public void OdfVersion_IsStableAcrossAccesses()
    {
        var doc = FodsDocument.CreateNew();
        var first  = doc.OdfVersion;
        var second = doc.OdfVersion;
        Assert.Equal(first, second);
    }

    // ---- OdfVersion: survives mutations ----

    [Fact]
    public void OdfVersion_AfterClearSheet_Unchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "x", "y" });
        var before = doc.OdfVersion;

        doc.ClearSheet("Sheet1");

        Assert.Equal(before, doc.OdfVersion);
    }

    // ---- Dogfood: both properties consistent ----

    [Fact]
    public void DogfoodPipeline_MimeTypeAndOdfVersion_BothStableAfterMutations()
    {
        var doc = FodsDocument.CreateNew();
        var mimeTypeBefore   = doc.MimeType;
        var odfVersionBefore = doc.OdfVersion;

        // Perform multiple mutations
        doc.InsertRowWithValues("Sheet1", 0, new[] { "v1", "v2" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "v3", "v4" });
        doc.AddSheet("Sheet2");
        doc.RenameSheet("Sheet2", "Summary");
        doc.ClearSheet("Sheet1");

        Assert.Equal(mimeTypeBefore,   doc.MimeType);
        Assert.Equal(odfVersionBefore, doc.OdfVersion);
        Assert.NotNull(doc.MimeType);
        Assert.NotNull(doc.OdfVersion);
    }
}
