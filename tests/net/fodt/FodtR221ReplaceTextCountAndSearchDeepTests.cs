// Tests for FodtDocument.ReplaceText, SearchText, GetDocumentStats deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R221

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R221: Tests for FodtDocument.ReplaceText, SearchText, GetDocumentStats deeper coverage.
/// ReplaceText(old, new): replaces all occurrences of old text with new text.
/// SearchText(query): returns list of paragraph indices containing the query string.
/// GetPlainText(): returns the full document as plain text string.
/// Covers: ReplaceText non-null after; ReplaceText new text appears in content;
/// ReplaceText old text removed; ReplaceText multiple occurrences all replaced;
/// ReplaceText same text no-op; ReplaceText affects ExportToPlainText;
/// SearchText non-null; SearchText finds known text; SearchText returns empty for unknown;
/// SearchText returns correct indices; SearchText after ReplaceText finds new text;
/// GetPlainText non-null; GetPlainText contains paragraph text; GetPlainText contains heading;
/// GetPlainText after AppendParagraph includes new;
/// dogfood CreateDoc->ReplaceText->SearchText->GetPlainText->Verify pipeline.
/// </summary>
public class FodtR221ReplaceTextCountAndSearchDeepTests
{
    private static FodtDocument CreateDocWithRepeatingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("The project started in January and the project team is ready.");
        doc.AppendParagraph("Project management ensures the project stays on track.");
        doc.InsertHeading(3, "Project Goals", 2);
        doc.AppendParagraph("The main project goal is to deliver quality results.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NewTextAppearsInContent()
    {
        var doc = CreateDocWithRepeatingText();
        doc.ReplaceText("project", "initiative");
        var text = doc.ExportToPlainText();
        Assert.Contains("initiative", text.ToLower());
    }

    [Fact]
    public void ReplaceText_DoesNotThrow()
    {
        var doc = CreateDocWithRepeatingText();
        var ex = Record.Exception(() => doc.ReplaceText("project", "initiative"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_SameText_NoOp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var ex = Record.Exception(() => doc.ReplaceText("hello", "hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_NonExistentText_NoOp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var ex = Record.Exception(() => doc.ReplaceText("xyz_not_present", "replaced"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_AffectsWordFrequency()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("alpha beta alpha gamma alpha.");
        doc.ReplaceText("alpha", "delta");
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        // After replace, delta should appear, alpha reduced/gone
        Assert.False(freq.ContainsKey("alpha"));
    }

    [Fact]
    public void ReplaceText_MultipleCallsChained_Works()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three.");
        doc.ReplaceText("one", "1");
        doc.ReplaceText("two", "2");
        doc.ReplaceText("three", "3");
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
    }

    [Fact]
    public void ReplaceText_UpdatesGetWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        var before = doc.GetWordCount();
        doc.ReplaceText("quick", "slow");
        // Word count shouldn't change (same number of words)
        Assert.Equal(before, doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NonNull()
    {
        var doc = CreateDocWithRepeatingText();
        Assert.NotNull(doc.SearchText("project"));
    }

    [Fact]
    public void SearchText_FindsKnownText()
    {
        var doc = CreateDocWithRepeatingText();
        var results = doc.SearchText("project");
        Assert.True(results.Count > 0);
    }

    [Fact]
    public void SearchText_UnknownText_ReturnsEmpty()
    {
        var doc = CreateDocWithRepeatingText();
        var results = doc.SearchText("xyzzy_nonexistent_phrase");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_ReturnsIndices_InRange()
    {
        var doc = CreateDocWithRepeatingText();
        var results = doc.SearchText("project");
        foreach (var idx in results)
        {
            Assert.True(idx >= 0);
            Assert.True(idx < doc.GetParagraphCount());
        }
    }

    [Fact]
    public void SearchText_AfterReplaceText_FindsNewText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps.");
        doc.ReplaceText("quick", "slow");
        var results = doc.SearchText("slow");
        Assert.True(results.Count > 0);
    }

    [Fact]
    public void SearchText_AfterReplaceText_OldTextGone()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps.");
        doc.ReplaceText("quick", "slow");
        var results = doc.SearchText("quick");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_Heading_IsSearchable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Unique Heading Text Here", 1);
        doc.AppendParagraph("Body paragraph does not contain the heading term.");
        var results = doc.SearchText("Unique");
        Assert.True(results.Count > 0);
    }

    // -------------------------------------------------------------------------
    // GetPlainText (ExportToPlainText as proxy)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_NonNull()
    {
        var doc = CreateDocWithRepeatingText();
        Assert.NotNull(doc.ExportToPlainText());
    }

    [Fact]
    public void GetPlainText_ContainsParagraphText()
    {
        var doc = CreateDocWithRepeatingText();
        var text = doc.ExportToPlainText();
        Assert.Contains("project", text.ToLower());
    }

    [Fact]
    public void GetPlainText_ContainsHeadingText()
    {
        var doc = CreateDocWithRepeatingText();
        var text = doc.ExportToPlainText();
        Assert.Contains("Overview", text);
    }

    [Fact]
    public void GetPlainText_AfterAppendParagraph_IncludesNew()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial paragraph content.");
        var before = doc.ExportToPlainText();
        doc.AppendParagraph("New paragraph added after.");
        var after = doc.ExportToPlainText();
        Assert.True(after.Length > before.Length);
        Assert.Contains("New paragraph added after", after);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ReplaceText_SearchText_GetPlainText_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Research Report", 1);
        doc.AppendParagraph("The research team conducted extensive research on this topic.");
        doc.AppendParagraph("Research findings indicate significant improvement in results.");
        doc.InsertHeading(3, "Research Methods", 2);
        doc.AppendParagraph("The research methods were carefully selected for accuracy.");

        // SearchText before replace
        var researchResults = doc.SearchText("research");
        Assert.True(researchResults.Count >= 3); // In multiple paragraphs

        // GetPlainText before replace
        var textBefore = doc.ExportToPlainText();
        Assert.Contains("Research", textBefore);
        Assert.Contains("research", textBefore);

        // ReplaceText
        doc.ReplaceText("research", "study");
        doc.ReplaceText("Research", "Study");

        // SearchText after replace — old text gone
        var oldTermResults = doc.SearchText("research");
        Assert.Empty(oldTermResults);

        // SearchText for new term
        var newTermResults = doc.SearchText("study");
        Assert.True(newTermResults.Count >= 3);

        // GetPlainText after replace
        var textAfter = doc.ExportToPlainText();
        Assert.Contains("study", textAfter.ToLower());
        Assert.DoesNotContain("research", textAfter.ToLower());

        // GetWordFrequency after replace
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.False(freq.ContainsKey("research"));

        // GetDocumentStats unchanged structure
        var stats = doc.GetDocumentStats();
        Assert.Equal(2, stats.HeadingCount);
        Assert.Equal(5, stats.ParagraphCount); // 2 headings + 3 body paragraphs
    }
}
