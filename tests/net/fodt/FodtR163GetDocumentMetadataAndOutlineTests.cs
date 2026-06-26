// Tests for FodtDocument.GetDocumentMetadata, GetDocumentOutline, Tables.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R163

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R163: Tests for FodtDocument.GetDocumentMetadata, GetDocumentOutline, Tables.
/// GetDocumentMetadata(): returns a read-only dictionary of document properties.
/// GetDocumentOutline(): returns ordered list of (Level, Text) for headings.
/// Tables: IReadOnlyList of FodtTable elements in the document.
/// Covers: GetDocumentMetadata returns non-null dictionary; GetDocumentMetadata keys are non-empty;
/// GetDocumentMetadata consistent across calls; GetDocumentMetadata empty doc returns dict;
/// GetDocumentOutline empty doc is empty; GetDocumentOutline single heading has level and text;
/// GetDocumentOutline multiple headings ordered by insertion; GetDocumentOutline non-heading excluded;
/// GetDocumentOutline level 1 entry present after InsertHeading(0,text,1);
/// Tables empty doc is empty list; Tables count is read-only (no setter);
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->GetOutline->GetMetadata pipeline.
/// </summary>
public class FodtR163GetDocumentMetadataAndOutlineTests
{
    // -------------------------------------------------------------------------
    // GetDocumentMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_ReturnsNonNullDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    [Fact]
    public void GetDocumentMetadata_EmptyDoc_ReturnsDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.IsAssignableFrom<IReadOnlyDictionary<string, string>>(meta);
    }

    [Fact]
    public void GetDocumentMetadata_ConsistentAcrossCalls()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta1 = doc.GetDocumentMetadata();
        var meta2 = doc.GetDocumentMetadata();
        Assert.Equal(meta1.Count, meta2.Count);
    }

    [Fact]
    public void GetDocumentMetadata_KeysAreNonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        foreach (var key in meta.Keys)
            Assert.False(string.IsNullOrEmpty(key));
    }

    // -------------------------------------------------------------------------
    // GetDocumentOutline
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentOutline_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetDocumentOutline());
    }

    [Fact]
    public void GetDocumentOutline_SingleHeading_HasLevelAndText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Chapter 1", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_MultipleHeadings_OrderedByInsertion()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Some body text.");
        doc.InsertHeading(2, "Section 1.1", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline.Count);
        Assert.Equal("Introduction", outline[0].Text);
        Assert.Equal("Section 1.1", outline[1].Text);
    }

    [Fact]
    public void GetDocumentOutline_BodyParagraphExcluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Heading", 1);
        doc.AppendParagraph("Body paragraph not in outline.");
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
    }

    [Fact]
    public void GetDocumentOutline_Level1HeadingPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Top-Level", 1);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(1, outline[0].Level);
    }

    [Fact]
    public void GetDocumentOutline_Level2Heading_Level2InOutline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sub-Section", 2);
        var outline = doc.GetDocumentOutline();
        Assert.Equal(2, outline[0].Level);
    }

    // -------------------------------------------------------------------------
    // Tables
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_EmptyDoc_IsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.Tables);
    }

    [Fact]
    public void Tables_IsReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<FodtTable>>(doc.Tables);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeading->AppendParagraph->GetOutline->GetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_HeadingsParagraphsOutlineMetadata_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Introduction paragraph.");
        doc.InsertHeading(2, "Background", 2);
        doc.AppendParagraph("Background content.");
        doc.InsertHeading(4, "Conclusion", 1);

        // Outline should have 3 headings
        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal("Title", outline[0].Text);
        Assert.Equal("Background", outline[1].Text);
        Assert.Equal("Conclusion", outline[2].Text);

        // Levels
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal(1, outline[2].Level);

        // Metadata accessible
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);

        // Tables still empty
        Assert.Empty(doc.Tables);
    }
}
