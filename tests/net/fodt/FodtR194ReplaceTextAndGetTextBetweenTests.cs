// Tests for FodtDocument.ReplaceText, GetTextBetweenParagraphs, GetPlainTextRange.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R194

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R194: Tests for FodtDocument.ReplaceText, GetTextBetweenParagraphs, GetPlainTextRange.
/// ReplaceText(oldText, newText): replaces all occurrences of oldText with newText.
/// GetTextBetweenParagraphs(startIndex, endIndex): returns joined text from range of paragraphs.
/// GetPlainTextRange(startIndex, endIndex): returns plain text for index range.
/// Covers: ReplaceText updates paragraph text; ReplaceText count of replacements;
/// ReplaceText non-matching text leaves doc unchanged; ReplaceText multiple occurrences;
/// ReplaceText returns number of replacements; GetTextBetweenParagraphs non-null;
/// GetTextBetweenParagraphs contains expected text; GetTextBetweenParagraphs range correct;
/// GetTextBetweenParagraphs single paragraph; GetPlainTextRange non-null;
/// GetPlainTextRange contains expected text; GetPlainTextRange range subset;
/// GetPlainTextRange whole doc; ReplaceText->GetPlainTextRange reflects change;
/// dogfood CreateEmpty->AppendParagraphs->ReplaceText->GetTextBetween->GetPlainTextRange.
/// </summary>
public class FodtR194ReplaceTextAndGetTextBetweenTests
{
    private static FodtDocument CreateWithContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world from Alice.");
        doc.AppendParagraph("Hello world from Bob.");
        doc.AppendParagraph("Goodbye from Carol.");
        doc.AppendParagraph("The end of document.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_UpdatesParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        doc.ReplaceText("world", "everyone");
        var text = doc.GetPlainText();
        Assert.Contains("everyone", text);
        Assert.DoesNotContain("world", text);
    }

    [Fact]
    public void ReplaceText_NonMatching_LeavesDocUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        doc.ReplaceText("NONEXISTENT_XYZ", "replacement");
        var text = doc.GetPlainText();
        Assert.Contains("Hello world", text);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_AllReplaced()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("Hello", "Hi");
        var text = doc.GetPlainText();
        Assert.DoesNotContain("Hello", text);
        Assert.Contains("Hi", text);
    }

    [Fact]
    public void ReplaceText_ReturnsCount()
    {
        var doc = CreateWithContent();
        var count = doc.ReplaceText("Hello", "Hi");
        Assert.True(count >= 1);
    }

    [Fact]
    public void ReplaceText_ZeroForNonMatching()
    {
        var doc = CreateWithContent();
        var count = doc.ReplaceText("NONEXISTENT_XYZ", "replacement");
        Assert.Equal(0, count);
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NonNull()
    {
        var doc = CreateWithContent();
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_ContainsFirstParagraph()
    {
        var doc = CreateWithContent();
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Contains("Alice", text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_ContainsRange()
    {
        var doc = CreateWithContent();
        var text = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Contains("Alice", text);
        Assert.Contains("Bob", text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_SingleParagraph()
    {
        var doc = CreateWithContent();
        var text = doc.GetTextBetweenParagraphs(2, 3); // exclusive end: (2,3) returns index 2 = Carol
        Assert.Contains("Carol", text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_DoesNotIncludeBeyondRange()
    {
        var doc = CreateWithContent();
        // Range 0..1 should not contain Carol (para 2)
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.DoesNotContain("Carol", text);
    }

    // -------------------------------------------------------------------------
    // GetPlainTextRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NonNull()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainTextRange(0, 2);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetPlainTextRange_ContainsExpectedText()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainTextRange(0, 1); // exclusive end: (0,1) returns index 0 = Alice
        Assert.Contains("Alice", text);
    }

    [Fact]
    public void GetPlainTextRange_WholeDoc_ContainsAll()
    {
        var doc = CreateWithContent();
        var text = doc.GetPlainTextRange(0, doc.ParagraphCount - 1);
        Assert.Contains("Alice", text);
        Assert.Contains("Bob", text);
        Assert.Contains("Carol", text);
    }

    [Fact]
    public void GetPlainTextRange_Subset_OnlyContainsRange()
    {
        var doc = CreateWithContent();
        // Range 0..1 (exclusive) is only Alice's paragraph (index 0)
        var text = doc.GetPlainTextRange(0, 1);
        Assert.Contains("Alice", text);
    }

    [Fact]
    public void ReplaceText_GetPlainTextRange_ReflectsChange()
    {
        var doc = CreateWithContent();
        doc.ReplaceText("Alice", "Alicia");
        var text = doc.GetPlainTextRange(0, 1); // exclusive end: returns index 0 = Alicia's paragraph
        Assert.Contains("Alicia", text);
        Assert.DoesNotContain("Alice", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraphs->ReplaceText->GetTextBetween->GetPlainTextRange
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendReplaceGetTextBetweenGetPlainRange_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First section: introduction text.");
        doc.AppendParagraph("Second section: methods and approach.");
        doc.AppendParagraph("Third section: results and discussion.");
        doc.AppendParagraph("Fourth section: conclusion remarks.");

        Assert.Equal(4, doc.ParagraphCount);

        // ReplaceText
        var count = doc.ReplaceText("section:", "chapter:");
        Assert.Equal(4, count);

        var allText = doc.GetPlainText();
        Assert.Contains("chapter:", allText);
        Assert.DoesNotContain("section:", allText);

        // GetTextBetweenParagraphs 0..2 (exclusive end: returns indices 0,1 = introduction+methods)
        var firstTwo = doc.GetTextBetweenParagraphs(0, 2);
        Assert.Contains("introduction", firstTwo);
        Assert.Contains("methods", firstTwo);
        Assert.DoesNotContain("results", firstTwo);

        // GetPlainTextRange 2..4 (exclusive end: returns indices 2,3 = results+conclusion)
        var lastTwo = doc.GetPlainTextRange(2, 4);
        Assert.Contains("results", lastTwo);
        Assert.Contains("conclusion", lastTwo);
        Assert.DoesNotContain("introduction", lastTwo);
    }
}
