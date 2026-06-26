// Tests for FodtDocument.GetDocumentOutline and GetDocumentMetadata.
// Sprint: ff-sprint-s145-dotnet-deepening-20260628
// Ledger: PC-FODT-R156

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R156: Tests for FodtDocument.GetDocumentOutline and GetDocumentMetadata.
/// GetDocumentOutline returns a list of (Level, Text) tuples from all heading elements.
/// GetDocumentMetadata returns a dictionary of metadata fields from the office:meta element.
/// Covers: GetDocumentOutline empty doc returns empty; single heading returns one entry;
/// single heading level and text are correct; multiple headings returned in order;
/// paragraphs excluded from outline; GetDocumentMetadata empty doc returns empty dict;
/// GetDocumentMetadata returns IReadOnlyDictionary;
/// dogfood multi-level headings outline levels correct;
/// dogfood headings+paragraphs outline count matches headings only;
/// dogfood all outline entries have non-empty text.
/// </summary>
public class FodtR156GetDocumentOutlineAndMetadataTests
{
    // -------------------------------------------------------------------------
    // GetDocumentOutline tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_EmptyDocument_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var outline = doc.GetDocumentOutline();
        Assert.NotNull(outline);
        Assert.Empty(outline);
    }

    [Fact]
    public void GetDocumentOutline_SingleHeading_ReturnsOneEntry()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
    }

    [Fact]
    public void GetDocumentOutline_SingleHeading_HasCorrectLevel()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline[0].Level);
    }

    [Fact]
    public void GetDocumentOutline_SingleHeading_HasCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal("My Title", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_MultipleHeadings_ReturnsAllInOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Section 1.1", 2);
        doc.AppendHeading("Chapter 2", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("Chapter 1", outline[0].Text);
        Assert.Equal("Section 1.1", outline[1].Text);
        Assert.Equal("Chapter 2", outline[2].Text);
    }

    [Fact]
    public void GetDocumentOutline_ParagraphsExcluded_ReturnsOnlyHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body text.");
        doc.AppendHeading("Section", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline.Count);
    }

    // -------------------------------------------------------------------------
    // GetDocumentMetadata tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_EmptyDocument_ReturnsEmptyDict()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
        Assert.Empty(meta);
    }

    [Fact]
    public void GetDocumentMetadata_ReturnsIReadOnlyDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.IsAssignableFrom<IReadOnlyDictionary<string, string>>(meta);
    }

    // -------------------------------------------------------------------------
    // Dogfood: GetDocumentOutline pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleHeadingLevels_OutlineLevelsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1 Title", 1);
        doc.AppendHeading("H2 Section", 2);
        doc.AppendHeading("H3 Subsection", 3);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal(3, outline[2].Level);
    }

    [Fact]
    public void DogfoodPipeline_HeadingsAndParagraphs_OutlineCountMatchesHeadingsOnly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Executive Summary", 1);
        doc.AppendParagraph("This is the summary.");
        doc.AppendHeading("Findings", 2);
        doc.AppendParagraph("Key findings here.");
        doc.AppendHeading("Conclusion", 1);

        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.All(outline, entry => Assert.False(string.IsNullOrEmpty(entry.Text)));
    }
}
