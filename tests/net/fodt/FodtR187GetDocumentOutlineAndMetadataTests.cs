// Tests for FodtDocument.GetDocumentOutline, GetDocumentMetadata, GetParagraphStyles, ExportToOutlineJson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R187

using System.Collections.Generic;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R187: Tests for FodtDocument.GetDocumentOutline, GetDocumentMetadata, GetParagraphStyles, ExportToOutlineJson.
/// GetDocumentOutline(): returns list of (Level, Text) heading tuples.
/// GetDocumentMetadata(): returns key/value metadata dictionary.
/// GetParagraphStyles(): returns all distinct style names in document.
/// ExportToOutlineJson(): serializes outline to JSON string.
/// Covers: GetDocumentOutline non-null; GetDocumentOutline count after AddHeadings;
/// GetDocumentOutline first item level; GetDocumentOutline first item text;
/// GetDocumentMetadata non-null; GetDocumentMetadata is dict;
/// GetParagraphStyles non-null; GetParagraphStyles is non-empty for doc with styles;
/// ExportToOutlineJson is non-null; ExportToOutlineJson contains heading text;
/// ExportToOutlineJson is valid JSON bracket; GetDocumentOutline after RemoveHeading;
/// GetParagraphStyles after SetParagraphStyle;
/// dogfood CreateEmpty->InsertHeadings->GetDocumentOutline->ExportToOutlineJson.
/// </summary>
public class FodtR187GetDocumentOutlineAndMetadataTests
{
    private static FodtDocument CreateWithHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.InsertHeading(1, "Background", 2);
        doc.InsertHeading(2, "Methods", 1);
        doc.AppendParagraph("Some body text here.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_NonNull()
    {
        var doc = CreateWithHeadings();
        var outline = doc.GetDocumentOutline();
        Assert.NotNull(outline);
    }

    [Fact]
    public void GetDocumentOutline_CountAfterInsertingThreeHeadings()
    {
        var doc = CreateWithHeadings();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
    }

    [Fact]
    public void GetDocumentOutline_FirstItem_LevelIsOne()
    {
        var doc = CreateWithHeadings();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level);
    }

    [Fact]
    public void GetDocumentOutline_FirstItem_TextIsIntroduction()
    {
        var doc = CreateWithHeadings();
        var outline = doc.GetDocumentOutline();
        Assert.Equal("Introduction", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_SecondItem_LevelIsTwo()
    {
        var doc = CreateWithHeadings();
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline[1].Level);
    }

    [Fact]
    public void GetDocumentOutline_AfterRemoveHeading_CountDecreases()
    {
        var doc = CreateWithHeadings();
        var before = doc.GetDocumentOutline().Count;
        // Find heading paragraph index (headings are at paragraph indices 0,1,2)
        doc.RemoveHeading(0);
        var after = doc.GetDocumentOutline().Count;
        Assert.Equal(before - 1, after);
    }

    // -------------------------------------------------------------------------
    // GetDocumentMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var metadata = doc.GetDocumentMetadata();
        Assert.NotNull(metadata);
    }

    [Fact]
    public void GetDocumentMetadata_IsReadOnlyDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var metadata = doc.GetDocumentMetadata();
        Assert.IsAssignableFrom<IReadOnlyDictionary<string, string>>(metadata);
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyles_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        var styles = doc.GetParagraphStyles();
        Assert.NotNull(styles);
    }

    [Fact]
    public void GetParagraphStyles_AfterSetParagraphStyle_ContainsStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "Heading1");
        var styles = doc.GetParagraphStyles();
        Assert.Contains("Heading1", styles);
    }

    // -------------------------------------------------------------------------
    // ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_NonNull()
    {
        var doc = CreateWithHeadings();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
    }

    [Fact]
    public void ExportToOutlineJson_ContainsHeadingText()
    {
        var doc = CreateWithHeadings();
        var json = doc.ExportToOutlineJson();
        Assert.Contains("Introduction", json);
    }

    [Fact]
    public void ExportToOutlineJson_IsValidJsonBracket()
    {
        var doc = CreateWithHeadings();
        var json = doc.ExportToOutlineJson();
        var trimmed = json.Trim();
        Assert.True(trimmed.StartsWith("[") || trimmed.StartsWith("{"),
            $"Expected JSON to start with '[' or '{{' but got: {trimmed.Substring(0, Math.Min(20, trimmed.Length))}");
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeadings->GetDocumentOutline->ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertGetOutlineExportJson_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Insert headings
        doc.InsertHeading(0, "Chapter One", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.InsertHeading(2, "Section 1.2", 2);
        doc.AppendParagraph("Content paragraph.");

        // Verify paragraph count
        Assert.True(doc.ParagraphCount >= 4);

        // GetDocumentOutline
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("Chapter One", outline[0].Text);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Section 1.1", outline[1].Text);
        Assert.Equal(2, outline[1].Level);

        // ExportToOutlineJson
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        Assert.Contains("Chapter One", json);
        Assert.Contains("Section 1.1", json);

        // GetDocumentMetadata
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }
}
