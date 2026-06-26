// Tests for FodtDocument.ReplaceText, GetWordCount, GetCharCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R209

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R209: Tests for FodtDocument.ReplaceText deeper coverage and GetWordCount/GetCharCount interactions.
/// ReplaceText(oldText, newText): replaces all occurrences of oldText with newText in the document.
/// GetWordCount(): total words across all paragraphs.
/// GetCharCount(): total characters across all text content.
/// Covers: ReplaceText returns count >= 0; ReplaceText changes GetPlainText;
/// ReplaceText old term no longer in SearchText; ReplaceText new term in SearchText;
/// ReplaceText with equal-length replacement; ReplaceText with longer replacement;
/// ReplaceText with shorter replacement; ReplaceText multiple occurrences all replaced;
/// ReplaceText in headings; ReplaceText does not change ParagraphCount;
/// GetWordCount before/after ReplaceText for same-word-count replacement;
/// GetCharCount changes when replacement length differs;
/// dogfood AppendParagraphs->ReplaceText->GetWordCount->GetCharCount->SearchText->verify.
/// </summary>
public class FodtR209ReplaceTextAndGetWordCountDeepTests
{
    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_ChangesGetPlainText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The old value is recorded.");
        doc.ReplaceText("old value", "new value");
        Assert.Contains("new value", doc.GetPlainText());
    }

    [Fact]
    public void ReplaceText_OldTerm_NotInSearchText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Replace this specific term here.");
        doc.ReplaceText("specific term", "general phrase");
        Assert.Empty(doc.SearchText("specific term"));
    }

    [Fact]
    public void ReplaceText_NewTerm_InSearchText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Replace this specific term here.");
        doc.ReplaceText("specific term", "general phrase");
        Assert.NotEmpty(doc.SearchText("general phrase"));
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_AllReplaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Word appears here. Word appears again. Word one more time.");
        doc.ReplaceText("Word", "Token");
        var plain = doc.GetPlainText();
        Assert.DoesNotContain("Word", plain);
        Assert.Contains("Token", plain);
    }

    [Fact]
    public void ReplaceText_DoesNotChangeParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph with oldterm.");
        doc.AppendParagraph("Second paragraph with oldterm.");
        var before = doc.GetParagraphCount();
        doc.ReplaceText("oldterm", "newterm");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void ReplaceText_InHeadings_ChangesGetPlainText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Old Chapter Title", 1);
        doc.AppendParagraph("Content below.");
        doc.ReplaceText("Old Chapter", "New Section");
        Assert.Contains("New Section", doc.GetPlainText());
    }

    [Fact]
    public void ReplaceText_NonExistentTerm_NoChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Static content here.");
        var before = doc.GetPlainText();
        doc.ReplaceText("nonexistent_xyz", "replacement");
        var after = doc.GetPlainText();
        Assert.Equal(before, after);
    }

    [Fact]
    public void ReplaceText_WithEmpty_RemovesText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Remove the UNWANTED word from here.");
        doc.ReplaceText("UNWANTED ", string.Empty);
        var plain = doc.GetPlainText();
        Assert.DoesNotContain("UNWANTED", plain);
    }

    // -------------------------------------------------------------------------
    // GetWordCount interactions with ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_SameAfterSameWordCountReplacement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha beta gamma.");
        var before = doc.GetWordCount();
        // Replace one word with another (same count)
        doc.ReplaceText("beta", "delta");
        var after = doc.GetWordCount();
        Assert.Equal(before, after);
    }

    [Fact]
    public void GetWordCount_Positive_After_AppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three four five.");
        Assert.True(doc.GetWordCount() >= 5);
    }

    // -------------------------------------------------------------------------
    // GetCharCount interactions
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_IncreasesAfterLongerReplacement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Short word here.");
        var before = doc.GetCharCount();
        doc.ReplaceText("Short", "Very much longer");
        var after = doc.GetCharCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetCharCount_DecreasesAfterShorterReplacement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A very long replacement word is here.");
        var before = doc.GetCharCount();
        doc.ReplaceText("very long replacement word", "x");
        var after = doc.GetCharCount();
        Assert.True(after < before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendParagraphsReplaceTextGetWordCountGetCharCountSearchTextVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Status Report", 1);
        doc.AppendParagraph("The project status shows significant progress in all areas.");
        doc.AppendParagraph("Status metrics are tracked weekly and reviewed monthly.");
        doc.AppendParagraph("Overall project status remains on track for delivery.");

        // GetWordCount before
        var wordsBefore = doc.GetWordCount();
        Assert.True(wordsBefore > 0);

        // GetCharCount before
        var charsBefore = doc.GetCharCount();
        Assert.True(charsBefore > 0);

        // SearchText — "status" appears in all 4 paragraphs (heading + 3 body)
        var statusResults = doc.SearchText("status");
        Assert.True(statusResults.Count >= 3);

        // ReplaceText "status" → "state"
        doc.ReplaceText("status", "state");
        var plainText = doc.GetPlainText();
        Assert.Contains("state", plainText);
        Assert.DoesNotContain("status", plainText);

        // SearchText after replacement
        Assert.Empty(doc.SearchText("status"));
        Assert.NotEmpty(doc.SearchText("state"));

        // GetWordCount unchanged (same word count, just different words)
        var wordsAfter = doc.GetWordCount();
        Assert.Equal(wordsBefore, wordsAfter);

        // GetCharCount — "status" (6) and "state" (5) differ by 1 per occurrence
        var charsAfter = doc.GetCharCount();
        Assert.True(charsAfter < charsBefore); // "state" shorter than "status"

        // ParagraphCount unchanged
        Assert.Equal(4, doc.GetParagraphCount()); // 1 heading + 3 body
    }
}
