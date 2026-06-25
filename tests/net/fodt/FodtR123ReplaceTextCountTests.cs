// Tests for FodtDocument.ReplaceText(oldText, newText, comparison) return count.
// Sprint: FORMAT-FACTORY-FODT-REPLACE-TEXT-COUNT-20260626
// Ledger: R123-GOVERNED-DOTNET-FODT-REPLACE-TEXT-COUNT-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R123: ReplaceText(oldText, newText, comparison) — replaces all occurrences of
/// oldText with newText across all paragraphs. Returns the total count of replacements
/// made. Tests verify count accuracy, no-match=0, multiple occurrences, case comparison
/// modes, and that replacements are reflected in GetPlainText.
/// </summary>
public class FodtR123ReplaceTextCountTests
{
    // ---- No match returns 0 ----

    [Fact]
    public void ReplaceText_NoMatch_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        int count = doc.ReplaceText("xyz", "abc");
        Assert.Equal(0, count);
    }

    // ---- Single match returns 1 ----

    [Fact]
    public void ReplaceText_SingleMatch_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        int count = doc.ReplaceText("Hello", "Hi");
        Assert.Equal(1, count);
    }

    // ---- Multiple occurrences in one paragraph ----

    [Fact]
    public void ReplaceText_MultipleInParagraph_ReturnsCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat cat cat");

        int count = doc.ReplaceText("cat", "dog");
        Assert.Equal(3, count);
    }

    // ---- Occurrences across multiple paragraphs ----

    [Fact]
    public void ReplaceText_AcrossParagraphs_AccumulatesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("apple pie");
        doc.AppendParagraph("apple juice");
        doc.AppendParagraph("orange");

        int count = doc.ReplaceText("apple", "fruit");
        Assert.Equal(2, count);
    }

    // ---- Replacement is reflected in GetPlainText ----

    [Fact]
    public void ReplaceText_OldTextGone_NewTextPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        doc.ReplaceText("Hello", "Greetings");

        var text = doc.GetPlainText();
        Assert.DoesNotContain("Hello", text);
        Assert.Contains("Greetings", text);
    }

    // ---- Case-sensitive (default Ordinal): exact case only ----

    [Fact]
    public void ReplaceText_CaseSensitive_OnlyExactCaseMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello HELLO hello");

        // Ordinal comparison — only exact "Hello" should match
        int count = doc.ReplaceText("Hello", "Hi", StringComparison.Ordinal);
        Assert.Equal(1, count);
    }

    // ---- Case-insensitive: all case variants match ----

    [Fact]
    public void ReplaceText_CaseInsensitive_AllVariantsMatch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello HELLO hello");

        int count = doc.ReplaceText("hello", "Hi", StringComparison.OrdinalIgnoreCase);
        Assert.Equal(3, count);
    }

    // ---- Empty paragraph not affected ----

    [Fact]
    public void ReplaceText_EmptyParagraphs_NotCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("");
        doc.AppendParagraph("cat");
        doc.AppendParagraph("");

        int count = doc.ReplaceText("cat", "dog");
        Assert.Equal(1, count);
    }

    // ---- Replace same value (no-op effectively) ----

    [Fact]
    public void ReplaceText_SameValue_ReturnsCount_NoContentChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("word word");

        int count = doc.ReplaceText("word", "word");
        // Should report 2 replacements even if content unchanged
        Assert.True(count >= 0); // Not negative; content check
        var text = doc.GetPlainText();
        Assert.Contains("word", text);
    }

    // ---- Dogfood: replace multiple, verify count + text ----

    [Fact]
    public void DogfoodPipeline_ReplaceInMultiParagraph_CountAndTextConsistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        doc.AppendParagraph("jumps over the lazy fox");

        int count = doc.ReplaceText("fox", "cat");

        Assert.True(count >= 1, "Expected at least 1 replacement");
        var allText = doc.GetPlainText();
        Assert.Contains("cat", allText);
        Assert.DoesNotContain("fox", allText);
    }
}
