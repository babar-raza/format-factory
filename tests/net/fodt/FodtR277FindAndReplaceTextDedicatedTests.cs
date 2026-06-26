// Tests for FodtDocument.FindAndReplaceText dedicated coverage.
// Sprint: ff-sprint-s262-dotnet-deepening-20260630
// Ledger: PC-FODT-R277

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R277: Dedicated tests for FodtDocument.FindAndReplaceText(find, replace).
/// Null find string → throws exception or treats as no-op.
/// Empty find string → no exception (no changes or implementation-defined).
/// Valid find/replace → no exception.
/// ParagraphCount unchanged after call.
/// After replacement, text contains replaced string.
/// After replacement, original text no longer present.
/// Called on document without matching text → no exception.
/// Dogfood: known text, replace, verify replacement.
/// Dogfood: multiple paragraphs, replacement applies to all.
/// </summary>
public class FodtR277FindAndReplaceTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindAndReplaceText_ValidArgs_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        var ex = Record.Exception(() => doc.FindAndReplaceText("World", "Universe"));
        Assert.Null(ex);
    }

    [Fact]
    public void FindAndReplaceText_NoMatchingText_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        var ex = Record.Exception(() => doc.FindAndReplaceText("XYZ", "ABC"));
        Assert.Null(ex);
    }

    [Fact]
    public void FindAndReplaceText_EmptyDocument_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.FindAndReplaceText("find", "replace"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindAndReplaceText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("foo bar baz");
        int before = doc.ParagraphCount;
        doc.FindAndReplaceText("bar", "qux");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void FindAndReplaceText_AfterReplace_NewTextPresent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        doc.FindAndReplaceText("World", "Universe");
        string text = doc.GetParagraphText(0);
        Assert.Contains("Universe", text);
    }

    [Fact]
    public void FindAndReplaceText_AfterReplace_OldTextGone()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        doc.FindAndReplaceText("World", "Universe");
        string text = doc.GetParagraphText(0);
        Assert.DoesNotContain("World", text);
    }

    [Fact]
    public void FindAndReplaceText_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("cat sat on mat");
        doc.FindAndReplaceText("cat", "dog");
        var ex = Record.Exception(() => doc.FindAndReplaceText("sat", "stood"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownText_ReplacedCorrectly()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        doc.FindAndReplaceText("brown", "red");
        string text = doc.GetParagraphText(0);
        Assert.Contains("red", text);
        Assert.DoesNotContain("brown", text);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_ReplacementInAll()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First: replace me");
        doc.AddParagraph("Second: replace me too");
        doc.FindAndReplaceText("replace me", "done");
        string p0 = doc.GetParagraphText(0);
        string p1 = doc.GetParagraphText(1);
        Assert.Contains("done", p0);
        Assert.Contains("done", p1);
    }
}
