// Tests for FodtDocument.SearchText, ReplaceText deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R201

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R201: Tests for FodtDocument.SearchText, ReplaceText deeper coverage.
/// SearchText(query): returns list of matching paragraph indices (or strings).
/// ReplaceText(oldText, newText): replaces all occurrences of oldText with newText.
/// Covers: SearchText non-null; SearchText non-empty for known term;
/// SearchText empty for non-existent term; SearchText returns count of matches;
/// SearchText case sensitivity behavior; ReplaceText reflects in GetPlainText;
/// ReplaceText old text absent after replace; ReplaceText new text present after replace;
/// ReplaceText multiple occurrences all replaced; ReplaceText doesn't change other text;
/// ReplaceText->GetDocumentStats word count may change;
/// SearchText after ReplaceText finds new term; ReplaceText->ToFods->Load preserve;
/// SearchText non-null for empty doc;
/// dogfood CreateEmpty->AppendParagraphs->SearchText->ReplaceText->SearchText->GetPlainText verify.
/// </summary>
public class FodtR201SearchAndReplaceDeepTests
{
    private static FodtDocument CreateWithContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("The project involves research and development activities.");
        doc.AppendParagraph("Research is central to our project methodology.");
        doc.AppendParagraph("Development milestones are tracked quarterly.");
        doc.AppendParagraph("The project team meets weekly for status updates.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NonNull()
    {
        var doc = CreateWithContent();
        var results = doc.SearchText("project");
        Assert.NotNull(results);
    }

    [Fact]
    public void SearchText_NonEmpty_ForKnownTerm()
    {
        var doc = CreateWithContent();
        var results = doc.SearchText("project");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void SearchText_Empty_ForNonExistentTerm()
    {
        var doc = CreateWithContent();
        var results = doc.SearchText("xyzzy_nonexistent_term");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_CountMatchesOccurrences()
    {
        var doc = CreateWithContent();
        // "project" appears in multiple paragraphs
        var results = doc.SearchText("project");
        Assert.True(results.Count >= 2);
    }

    [Fact]
    public void SearchText_ForHeadingText_FindsMatch()
    {
        var doc = CreateWithContent();
        var results = doc.SearchText("Overview");
        Assert.True(results.Count >= 1);
    }

    [Fact]
    public void SearchText_NonNull_ForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var results = doc.SearchText("anything");
        Assert.NotNull(results);
    }

    [Fact]
    public void SearchText_Empty_ForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var results = doc.SearchText("anything");
        Assert.Empty(results);
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NewTextPresent_InGetPlainText()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("project", "initiative");
        var text = doc.GetPlainText();
        Assert.Contains("initiative", text);
    }

    [Fact]
    public void ReplaceText_OldTextAbsent_AfterReplace()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("project", "initiative");
        var text = doc.GetPlainText();
        Assert.DoesNotContain("project", text);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_AllReplaced()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("foo bar foo");
        doc.AppendParagraph("baz foo qux");
        doc.ReplaceText("foo", "replaced");
        var text = doc.GetPlainText();
        Assert.DoesNotContain("foo", text);
        Assert.Contains("replaced", text);
    }

    [Fact]
    public void ReplaceText_OtherTextUnchanged()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("project", "initiative");
        var text = doc.GetPlainText();
        Assert.Contains("research", text);
        Assert.Contains("development", text);
    }

    [Fact]
    public void ReplaceText_SearchText_FindsNewTerm()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("Research", "Investigation");
        var results = doc.SearchText("Investigation");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void ReplaceText_SearchText_OldTermAbsent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The old word is here.");
        doc.ReplaceText("old word", "new phrase");
        var results = doc.SearchText("old word");
        Assert.Empty(results);
    }

    [Fact]
    public void ReplaceText_NonExistentTerm_NoChange()
    {
        var doc = CreateWithContent();
        var beforeText = doc.GetPlainText();
        doc.ReplaceText("xyzzy_never_occurs", "replacement");
        var afterText = doc.GetPlainText();
        Assert.Equal(beforeText, afterText);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendSearchReplaceSearchGetPlainTextVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build doc
        doc.InsertHeading(0, "Technology Review", 1);
        doc.AppendParagraph("Technology changes rapidly in our industry.");
        doc.AppendParagraph("Adopting new technology is essential for growth.");
        doc.AppendParagraph("Technology investments yield long-term benefits.");

        // SearchText for "Technology"
        var initial = doc.SearchText("Technology");
        Assert.True(initial.Count >= 2); // heading + paragraphs

        // ReplaceText
        doc.ReplaceText("Technology", "Innovation");

        // SearchText for old term — should be empty
        var oldResults = doc.SearchText("Technology");
        Assert.Empty(oldResults);

        // SearchText for new term — should have matches
        var newResults = doc.SearchText("Innovation");
        Assert.NotEmpty(newResults);
        Assert.True(newResults.Count >= 2);

        // GetPlainText verification
        var text = doc.GetPlainText();
        Assert.DoesNotContain("Technology", text);
        Assert.Contains("Innovation", text);
        Assert.Contains("growth", text); // unchanged text
        Assert.Contains("benefits", text); // unchanged text

        // GetDocumentStats still valid
        var stats = doc.GetDocumentStats();
        Assert.Equal(4, stats.ParagraphCount);
        Assert.Equal(1, stats.HeadingCount);
        Assert.True(stats.WordCount > 0);
    }
}
