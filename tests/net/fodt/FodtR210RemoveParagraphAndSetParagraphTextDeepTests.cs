// Tests for FodtDocument.RemoveParagraph, SetParagraphText deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R210

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R210: Tests for FodtDocument.RemoveParagraph, SetParagraphText deeper coverage.
/// RemoveParagraph(index): removes the paragraph at the given zero-based index.
/// SetParagraphText(index, text): replaces the text of a paragraph at the given index.
/// Covers: RemoveParagraph decrements ParagraphCount; RemoveParagraph first shifts others;
/// RemoveParagraph last removes correctly; RemoveParagraph middle removes correctly;
/// RemoveParagraph from GetParagraphTexts not present;
/// SetParagraphText changes text; SetParagraphText GetPlainText reflects change;
/// SetParagraphText does not change ParagraphCount; SetParagraphText multiple times;
/// SetParagraphText SearchText finds new text; SetParagraphText old text not in SearchText;
/// RemoveParagraph then SetParagraphText on remaining;
/// dogfood AppendParagraphs->RemoveParagraph->SetParagraphText->verify pipeline.
/// </summary>
public class FodtR210RemoveParagraphAndSetParagraphTextDeepTests
{
    // -------------------------------------------------------------------------
    // RemoveParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_DecrementsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        doc.AppendParagraph("Second paragraph.");
        doc.AppendParagraph("Third paragraph.");
        var before = doc.GetParagraphCount();
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveParagraph_First_ShiftsOthers()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha content.");
        doc.AppendParagraph("Beta content.");
        doc.AppendParagraph("Gamma content.");
        doc.RemoveParagraph(0); // Remove Alpha
        var texts = doc.GetParagraphTexts();
        Assert.True(texts[0].Contains("Beta"));
    }

    [Fact]
    public void RemoveParagraph_Last_ReducesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        doc.AppendParagraph("Third.");
        doc.RemoveParagraph(2); // Remove Third
        Assert.Equal(2, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveParagraph_Middle_RemovesCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Middle to remove.");
        doc.AppendParagraph("Third.");
        doc.RemoveParagraph(1); // Remove Middle
        var texts = doc.GetParagraphTexts();
        Assert.False(texts.Exists(t => t.Contains("Middle to remove")));
    }

    [Fact]
    public void RemoveParagraph_NotInGetParagraphTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep this paragraph.");
        doc.AppendParagraph("Remove this specific content.");
        doc.RemoveParagraph(1);
        var texts = doc.GetParagraphTexts();
        Assert.False(texts.Exists(t => t.Contains("Remove this specific content")));
    }

    [Fact]
    public void RemoveParagraph_All_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only paragraph.");
        doc.RemoveParagraph(0);
        Assert.Equal(0, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // SetParagraphText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ChangesText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text here.");
        doc.SetParagraphText(0, "Updated text here.");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts[0].Contains("Updated text"));
    }

    [Fact]
    public void SetParagraphText_GetPlainText_ReflectsChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old content.");
        doc.SetParagraphText(0, "New content.");
        Assert.Contains("New content", doc.GetPlainText());
        Assert.DoesNotContain("Old content", doc.GetPlainText());
    }

    [Fact]
    public void SetParagraphText_DoesNotChangeParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        var before = doc.GetParagraphCount();
        doc.SetParagraphText(0, "Updated first.");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetParagraphText_MultipleTimes_LastWins()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original.");
        doc.SetParagraphText(0, "First update.");
        doc.SetParagraphText(0, "Second update.");
        doc.SetParagraphText(0, "Final update.");
        Assert.Contains("Final update", doc.GetPlainText());
        Assert.DoesNotContain("Original", doc.GetPlainText());
    }

    [Fact]
    public void SetParagraphText_SearchText_FindsNewText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original paragraph text.");
        doc.SetParagraphText(0, "Replacement search target text.");
        Assert.NotEmpty(doc.SearchText("search target"));
    }

    [Fact]
    public void SetParagraphText_SearchText_OldTextNotFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original unique marker text.");
        doc.SetParagraphText(0, "Completely different content.");
        Assert.Empty(doc.SearchText("unique marker"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendParagraphsRemoveParagraphSetParagraphTextVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("Introduction paragraph about the main topic.");
        doc.AppendParagraph("Middle paragraph with supporting evidence.");
        doc.AppendParagraph("Conclusion paragraph summarizing findings.");

        // ParagraphCount: 1 heading + 3 body = 4
        Assert.Equal(4, doc.GetParagraphCount());

        // SetParagraphText on body paragraph (index 1 = Introduction)
        doc.SetParagraphText(1, "Revised introduction with updated information.");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("Revised introduction")));
        Assert.False(texts.Exists(t => t.Contains("Introduction paragraph about")));

        // ParagraphCount unchanged
        Assert.Equal(4, doc.GetParagraphCount());

        // RemoveParagraph (index 2 = Middle paragraph)
        doc.RemoveParagraph(2);
        Assert.Equal(3, doc.GetParagraphCount());

        // GetParagraphTexts after removal
        var textsAfter = doc.GetParagraphTexts();
        Assert.False(textsAfter.Exists(t => t.Contains("supporting evidence")));
        Assert.True(textsAfter.Exists(t => t.Contains("Conclusion")));

        // SearchText after changes
        Assert.NotEmpty(doc.SearchText("Revised introduction"));
        Assert.Empty(doc.SearchText("supporting evidence"));
        Assert.NotEmpty(doc.SearchText("Conclusion"));

        // GetWordCount still positive
        Assert.True(doc.GetWordCount() > 0);

        // SetParagraphText on last paragraph
        doc.SetParagraphText(2, "Final conclusion with key results.");
        Assert.Contains("key results", doc.GetPlainText());
    }
}
