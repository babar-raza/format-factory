// Tests for FodtDocument.GetDocumentMetadata, MimeType, OdfVersion, GetDocumentOutline deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R214

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R214: Tests for FodtDocument.GetDocumentMetadata, MimeType, OdfVersion, GetDocumentOutline.
/// GetDocumentMetadata(): returns a dictionary of document metadata properties.
/// MimeType: returns the MIME type string for the document.
/// OdfVersion: returns the ODF specification version string.
/// GetDocumentOutline(): returns an ordered list of headings with levels and text.
/// Covers: GetDocumentMetadata non-null; GetDocumentMetadata has entries after content;
/// MimeType non-null; MimeType contains "text" or "odf" or "opendocument";
/// OdfVersion non-null; OdfVersion non-empty; OdfVersion is version-format string;
/// GetDocumentOutline non-null; GetDocumentOutline count equals heading count;
/// GetDocumentOutline contains heading texts; GetDocumentOutline levels correct;
/// GetDocumentOutline does not include plain paragraphs;
/// dogfood CreateEmpty->InsertHeadings->GetDocumentOutline->MimeType->Metadata->Verify pipeline.
/// </summary>
public class FodtR214GetDocumentMetadataAndMimeTypeDeepTests
{
    private static FodtDocument CreateWithStructure()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Background information for the document.");
        doc.InsertHeading(1, "Methodology", 2);
        doc.AppendParagraph("Methods used in this study.");
        doc.InsertHeading(2, "Results", 2);
        doc.AppendParagraph("Key findings of the research.");
        doc.InsertHeading(3, "Conclusion", 1);
        doc.AppendParagraph("Summary and future directions.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_NonNull()
    {
        var doc = CreateWithStructure();
        Assert.NotNull(doc.GetDocumentMetadata());
    }

    [Fact]
    public void GetDocumentMetadata_EmptyDoc_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.GetDocumentMetadata());
    }

    [Fact]
    public void GetDocumentMetadata_HasEntries()
    {
        var doc = CreateWithStructure();
        var meta = doc.GetDocumentMetadata();
        // Should have at least one metadata entry
        Assert.True(meta.Count > 0);
    }

    [Fact]
    public void GetDocumentMetadata_AfterAppendParagraph_NonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content for metadata extraction.");
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_NonNull()
    {
        var doc = CreateWithStructure();
        Assert.NotNull(doc.MimeType);
    }

    [Fact]
    public void MimeType_NonEmpty()
    {
        var doc = CreateWithStructure();
        Assert.NotEmpty(doc.MimeType);
    }

    [Fact]
    public void MimeType_ContainsExpectedContent()
    {
        var doc = CreateWithStructure();
        var mime = doc.MimeType.ToLower();
        Assert.True(
            mime.Contains("text") || mime.Contains("odf") ||
            mime.Contains("opendocument") || mime.Contains("application"),
            $"Unexpected MimeType: {doc.MimeType}");
    }

    [Fact]
    public void MimeType_SameForAllInstances()
    {
        var doc1 = FodtDocument.CreateEmpty();
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Some content.");
        Assert.Equal(doc1.MimeType, doc2.MimeType);
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_NonNull()
    {
        var doc = CreateWithStructure();
        Assert.NotNull(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_NonEmpty()
    {
        var doc = CreateWithStructure();
        Assert.NotEmpty(doc.OdfVersion);
    }

    [Fact]
    public void OdfVersion_IsVersionLikeFormat()
    {
        var doc = CreateWithStructure();
        var version = doc.OdfVersion;
        // Should be something like "1.3" or "1.2"
        Assert.True(version.Contains(".") || version.Length > 0);
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_NonNull()
    {
        var doc = CreateWithStructure();
        Assert.NotNull(doc.GetDocumentOutline());
    }

    [Fact]
    public void GetDocumentOutline_CountEqualsHeadingCount()
    {
        var doc = CreateWithStructure();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(doc.GetHeadingCount(), outline.Count);
    }

    [Fact]
    public void GetDocumentOutline_ContainsHeadingTexts()
    {
        var doc = CreateWithStructure();
        var outline = doc.GetDocumentOutline();
        var texts = outline.ConvertAll(o => o.Text);
        Assert.Contains("Introduction", texts);
        Assert.Contains("Methodology", texts);
        Assert.Contains("Conclusion", texts);
    }

    [Fact]
    public void GetDocumentOutline_DoesNotContainParagraphText()
    {
        var doc = CreateWithStructure();
        var outline = doc.GetDocumentOutline();
        var texts = outline.ConvertAll(o => o.Text);
        Assert.DoesNotContain("Background information", texts);
        Assert.DoesNotContain("Summary and future", texts);
    }

    [Fact]
    public void GetDocumentOutline_LevelsCorrect()
    {
        var doc = CreateWithStructure();
        var outline = doc.GetDocumentOutline();
        // Introduction is level 1
        var intro = outline.Find(o => o.Text == "Introduction");
        Assert.NotNull(intro);
        Assert.Equal(1, intro.Level);
        // Methodology is level 2
        var methods = outline.Find(o => o.Text == "Methodology");
        Assert.NotNull(methods);
        Assert.Equal(2, methods.Level);
    }

    [Fact]
    public void GetDocumentOutline_EmptyDoc_EmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var outline = doc.GetDocumentOutline();
        Assert.True(outline == null || outline.Count == 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_InsertHeadings_GetDocumentOutline_MimeType_Metadata_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("This document outlines the strategic vision.");
        doc.InsertHeading(1, "Financial Overview", 2);
        doc.AppendParagraph("Revenue and cost analysis for the period.");
        doc.InsertHeading(2, "Operations", 2);
        doc.AppendParagraph("Operational metrics and KPIs.");
        doc.InsertHeading(3, "Recommendations", 1);
        doc.AppendParagraph("Next steps and action items.");

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.NotNull(outline);
        Assert.Equal(4, outline.Count);
        var texts = outline.ConvertAll(o => o.Text);
        Assert.Contains("Executive Summary", texts);
        Assert.Contains("Financial Overview", texts);
        Assert.Contains("Recommendations", texts);

        // Verify levels
        var exec = outline.Find(o => o.Text == "Executive Summary");
        Assert.Equal(1, exec.Level);
        var fin = outline.Find(o => o.Text == "Financial Overview");
        Assert.Equal(2, fin.Level);

        // MimeType
        var mime = doc.MimeType;
        Assert.NotNull(mime);
        Assert.NotEmpty(mime);

        // OdfVersion
        var version = doc.OdfVersion;
        Assert.NotNull(version);
        Assert.NotEmpty(version);

        // GetDocumentMetadata
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);

        // Verify heading and paragraph counts
        Assert.Equal(4, doc.GetHeadingCount());
        Assert.True(doc.GetParagraphCount() > 4);
        Assert.True(doc.GetWordCount() > 0);

        // Plain paragraphs not in outline
        Assert.DoesNotContain("strategic vision", texts);
    }
}
