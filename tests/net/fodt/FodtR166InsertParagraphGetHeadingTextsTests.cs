// Tests for FodtDocument.InsertParagraph, GetHeadingTexts, GetHeadingParagraphs, RemoveHeading.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R166

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R166: Tests for FodtDocument.InsertParagraph, GetHeadingTexts, GetHeadingParagraphs, RemoveHeading.
/// InsertParagraph(index, text): inserts a paragraph at the given index; shifts subsequent paragraphs.
/// GetHeadingTexts(): returns a list of heading paragraph text strings.
/// GetHeadingParagraphs(): returns the list of FodtParagraph objects that are headings.
/// RemoveHeading(index): removes the heading paragraph at the given paragraph index.
/// Covers: InsertParagraph at 0 shifts others; InsertParagraph increments ParagraphCount;
/// InsertParagraph returns FodtParagraph; InsertParagraph OOB throws;
/// GetHeadingTexts empty doc is empty; GetHeadingTexts single heading correct;
/// GetHeadingTexts multiple headings in order; GetHeadingTexts body paragraph excluded;
/// GetHeadingParagraphs count matches heading count; GetHeadingParagraphs is IsHeading=true;
/// RemoveHeading removes correct paragraph; RemoveHeading decrements count;
/// dogfood CreateEmpty->InsertParagraph->InsertHeading->GetHeadingTexts->RemoveHeading pipeline.
/// </summary>
public class FodtR166InsertParagraphGetHeadingTextsTests
{
    // -------------------------------------------------------------------------
    // InsertParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_AtZero_ShiftsOthers()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original first.");
        doc.InsertParagraph(0, "Inserted first.");
        Assert.Equal("Inserted first.", doc.GetParagraphText(0));
        Assert.Equal("Original first.", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_IncrementsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing.");
        var before = doc.ParagraphCount;
        doc.InsertParagraph(0, "New.");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_ReturnsFodtParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        var para = doc.InsertParagraph(0, "Returned.");
        Assert.IsType<FodtParagraph>(para);
    }

    [Fact]
    public void InsertParagraph_AtEnd_AppendsBehavior()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.InsertParagraph(1, "Second.");
        Assert.Equal("Second.", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_OobIndex_Throws()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.InsertParagraph(5, "OOB"));
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_SingleHeading_CorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Overview", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Single(texts);
        Assert.Equal("Overview", texts[0]);
    }

    [Fact]
    public void GetHeadingTexts_MultipleHeadings_InOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.AppendParagraph("Body text.");
        doc.InsertHeading(2, "Chapter 2", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(2, texts.Count);
        Assert.Equal("Chapter 1", texts[0]);
        Assert.Equal("Chapter 2", texts[1]);
    }

    [Fact]
    public void GetHeadingTexts_BodyParagraphExcluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Heading", 1);
        doc.AppendParagraph("Not a heading.");
        var texts = doc.GetHeadingTexts();
        Assert.Single(texts);
        Assert.DoesNotContain("Not a heading.", texts);
    }

    // -------------------------------------------------------------------------
    // GetHeadingParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_CountMatchesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Body.");
        doc.InsertHeading(2, "H2", 2);
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(2, headings.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_AllAreIsHeadingTrue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Section A", 1);
        doc.InsertHeading(1, "Section B", 2);
        var headings = doc.GetHeadingParagraphs();
        foreach (var h in headings)
            Assert.True(h.IsHeading);
    }

    // -------------------------------------------------------------------------
    // RemoveHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_DecrementsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Removable", 1);
        doc.AppendParagraph("Body.");
        var before = doc.ParagraphCount;
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_TextNoLongerInHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Gone", 1);
        doc.InsertHeading(1, "Stays", 2);
        doc.RemoveHeading(0);
        Assert.DoesNotContain("Gone", doc.GetHeadingTexts());
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertParagraph->InsertHeading->GetHeadingTexts->RemoveHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertParagraphsHeadingsRemove_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Introduction", 1);
        doc.InsertParagraph(1, "First body paragraph.");
        doc.AppendParagraph("Second body paragraph.");
        doc.InsertHeading(3, "Conclusion", 1);

        Assert.Equal(4, doc.ParagraphCount);
        Assert.Equal(2, doc.GetHeadingTexts().Count);
        Assert.Equal(2, doc.GetHeadingParagraphs().Count);

        // Remove first heading
        doc.RemoveHeading(0);
        Assert.Equal(3, doc.ParagraphCount);
        Assert.Equal(1, doc.GetHeadingTexts().Count);
        Assert.Equal("Conclusion", doc.GetHeadingTexts()[0]);

        // Insert new paragraph at position 0
        doc.InsertParagraph(0, "New preamble.");
        Assert.Equal("New preamble.", doc.GetParagraphText(0));
        Assert.Equal(4, doc.ParagraphCount);
    }
}
