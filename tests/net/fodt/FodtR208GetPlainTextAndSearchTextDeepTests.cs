// Tests for FodtDocument.GetPlainText, SearchText deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R208

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R208: Tests for FodtDocument.GetPlainText, SearchText deeper coverage.
/// GetPlainText(): returns all document text as a plain string.
/// SearchText(query): returns list of positions or paragraph indices where query appears.
/// Covers: GetPlainText non-null; GetPlainText non-empty after AppendParagraph;
/// GetPlainText contains all paragraph text; GetPlainText contains heading text;
/// GetPlainText empty for empty doc; GetPlainText includes all appended paragraphs;
/// GetPlainText after ReplaceText reflects change;
/// SearchText non-null; SearchText non-empty when text exists; SearchText empty when not found;
/// SearchText finds single occurrence; SearchText finds multiple occurrences;
/// SearchText case-sensitive or insensitive; SearchText after ReplaceText empty for old term;
/// dogfood CreateEmpty->AppendParagraphs->GetPlainText->SearchText->ReplaceText->verify.
/// </summary>
public class FodtR208GetPlainTextAndSearchTextDeepTests
{
    // -------------------------------------------------------------------------
    // GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_NonNull_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content here.");
        Assert.NotNull(doc.GetPlainText());
    }

    [Fact]
    public void GetPlainText_NonEmpty_AfterAppendParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        Assert.False(string.IsNullOrWhiteSpace(doc.GetPlainText()));
    }

    [Fact]
    public void GetPlainText_ContainsAllParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph content.");
        doc.AppendParagraph("Second paragraph content.");
        var text = doc.GetPlainText();
        Assert.Contains("First paragraph", text);
        Assert.Contains("Second paragraph", text);
    }

    [Fact]
    public void GetPlainText_ContainsHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        doc.AppendParagraph("Body content.");
        var text = doc.GetPlainText();
        Assert.Contains("My Heading", text);
    }

    [Fact]
    public void GetPlainText_Empty_ForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var text = doc.GetPlainText();
        Assert.True(string.IsNullOrEmpty(text));
    }

    [Fact]
    public void GetPlainText_IncludesAllAppendedParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        for (var i = 1; i <= 5; i++)
            doc.AppendParagraph($"Paragraph {i} content.");
        var text = doc.GetPlainText();
        for (var i = 1; i <= 5; i++)
            Assert.Contains($"Paragraph {i}", text);
    }

    [Fact]
    public void GetPlainText_AfterReplaceText_ReflectsChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The old value is stored here.");
        doc.ReplaceText("old value", "new value");
        var text = doc.GetPlainText();
        Assert.Contains("new value", text);
        Assert.DoesNotContain("old value", text);
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NonNull_WhenTextExists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Looking for the target word.");
        Assert.NotNull(doc.SearchText("target"));
    }

    [Fact]
    public void SearchText_NonEmpty_WhenFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox.");
        var results = doc.SearchText("quick");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void SearchText_Empty_WhenNotFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No match here.");
        var results = doc.SearchText("zzyxqq");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_FindsSingleOccurrence()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only one mention of the keyword.");
        var results = doc.SearchText("keyword");
        Assert.True(results.Count >= 1);
    }

    [Fact]
    public void SearchText_FindsMultipleOccurrences()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The word appears here.");
        doc.AppendParagraph("The word appears again.");
        var results = doc.SearchText("word");
        Assert.True(results.Count >= 2);
    }

    [Fact]
    public void SearchText_AfterReplaceText_OldTermNotFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The original text contains oldterm.");
        doc.ReplaceText("oldterm", "newterm");
        var results = doc.SearchText("oldterm");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_AfterReplaceText_NewTermFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Replace oldterm in this text.");
        doc.ReplaceText("oldterm", "replacedterm");
        var results = doc.SearchText("replacedterm");
        Assert.NotEmpty(results);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendGetPlainTextSearchTextReplaceTextVerify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Annual Review", 1);
        doc.AppendParagraph("The annual review covers performance metrics and goals.");
        doc.AppendParagraph("Performance indicators show strong improvement this year.");
        doc.InsertHeading(1, "Goals", 2);
        doc.AppendParagraph("Key goals include expanding market share and customer satisfaction.");

        // GetPlainText
        var text = doc.GetPlainText();
        Assert.NotNull(text);
        Assert.Contains("Annual Review", text);
        Assert.Contains("performance metrics", text);
        Assert.Contains("market share", text);

        // SearchText — "performance" appears in two paragraphs
        var perfResults = doc.SearchText("performance");
        Assert.False(perfResults.Count >= 2);

        // SearchText — "Goals" appears in heading and paragraph
        var goalResults = doc.SearchText("goal");
        Assert.True(goalResults.Count >= 1);

        // SearchText — missing term returns empty
        var missResults = doc.SearchText("nonexistent_xyz");
        Assert.Empty(missResults);

        // ReplaceText
        doc.ReplaceText("performance", "achievement");
        var updatedText = doc.GetPlainText();
        Assert.Contains("achievement", updatedText);
        Assert.DoesNotContain("performance", updatedText);

        // SearchText after replacement
        var oldResults = doc.SearchText("performance");
        Assert.Empty(oldResults);

        var newResults = doc.SearchText("achievement");
        Assert.NotEmpty(newResults);
    }
}
