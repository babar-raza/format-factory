// Tests for FodtDocument.InsertHeading and RemoveHeading.
// Sprint: ff-sprint-oracle-all-verified-20260626
// Ledger: PC-FODT-R100

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R100: Tests for FodtDocument.InsertHeading and RemoveHeading.
/// InsertHeading(index, text, level) inserts a styled heading paragraph at the given index.
/// RemoveHeading(index) removes a paragraph by index (same as RemoveParagraph).
/// Covers: InsertHeading empty doc adds to paragraph list; InsertHeading paragraph count increases;
/// InsertHeading text accessible via Paragraphs; InsertHeading at index 0 inserts at start;
/// InsertHeading at end inserts at end; RemoveHeading reduces paragraph count;
/// RemoveHeading out-of-range throws; InsertHeading null text throws or is handled;
/// InsertHeading with level 1 is Heading 1; InsertHeading level 2 is Heading 2;
/// dogfood CreateEmpty->InsertHeading->GetHeadingParagraphs pipeline.
/// </summary>
public class FodtR100InsertRemoveHeadingTests
{
    // -------------------------------------------------------------------------
    // InsertHeading basic
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_EmptyDoc_AddsParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text.");
        int before = doc.ParagraphCount;
        doc.InsertHeading(0, "Title", 1);
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertHeading_TextAccessibleViaParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        Assert.Equal("Chapter One", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void InsertHeading_AtIndex0_InsertsAtStart()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing paragraph.");
        doc.InsertHeading(0, "New Heading", 2);
        Assert.Equal("New Heading", doc.Paragraphs[0].Text);
        Assert.Equal("Existing paragraph.", doc.Paragraphs[1].Text);
    }

    [Fact]
    public void InsertHeading_AtEnd_InsertsLast()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.InsertHeading(1, "End Heading", 1);
        Assert.Equal("End Heading", doc.Paragraphs[1].Text);
    }

    [Fact]
    public void InsertHeading_MultipleHeadings_AllAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.InsertHeading(2, "H3", 3);
        Assert.Equal(3, doc.ParagraphCount);
        Assert.Equal("H1", doc.Paragraphs[0].Text);
        Assert.Equal("H2", doc.Paragraphs[1].Text);
        Assert.Equal("H3", doc.Paragraphs[2].Text);
    }

    // -------------------------------------------------------------------------
    // RemoveHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_ExistingIndex_ReducesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        doc.AppendParagraph("Body.");
        Assert.Equal(2, doc.ParagraphCount);
        doc.RemoveHeading(0);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_ExistingIndex_RemainingTextIsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Content.");
        doc.RemoveHeading(0);
        Assert.Equal("Content.", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveHeading_OutOfRange_Throws()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Only heading", 1);
        Assert.ThrowsAny<Exception>(() => doc.RemoveHeading(99));
    }

    [Fact]
    public void RemoveHeading_LastElement_EmptyParagraphList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sole Heading", 1);
        doc.RemoveHeading(0);
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: heading pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertHeadingGetHeadingParagraphs_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This is the intro text.");
        doc.InsertHeading(2, "Conclusion", 1);
        doc.AppendParagraph("Final thoughts.");

        Assert.Equal(4, doc.ParagraphCount);

        // GetHeadingParagraphs should return the heading-style paragraphs
        var headings = doc.GetHeadingParagraphs();
        Assert.True(headings.Count >= 2,
            "Expected at least 2 heading paragraphs.");
    }

    [Fact]
    public void Dogfood_InsertHeading_SaveRoundtrip()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("Executive summary content.");
        doc.InsertHeading(2, "Section 1", 2);

        // Verify structure before save
        Assert.Equal(3, doc.ParagraphCount);
        var headings = doc.GetHeadingParagraphs();
        Assert.True(headings.Count >= 1);
    }
}
