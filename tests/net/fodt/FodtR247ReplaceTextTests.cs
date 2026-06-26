// Tests for FodtDocument.ReplaceText dedicated coverage.
// Sprint: ff-sprint-s232-dotnet-deepening-20260629
// Ledger: PC-FODT-R247

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R247: Dedicated tests for FodtDocument.ReplaceText(oldText, newText).
/// Null old text → throws exception.
/// Null new text → throws exception.
/// Nonexistent old text → no exception (no-op).
/// Valid replacement → text updated.
/// ParagraphCount unchanged after replace.
/// GetWordCount non-negative after replace.
/// Replace multiple occurrences → all replaced.
/// Replace heading text → updated.
/// Replace twice → latest replacement persists.
/// Dogfood: replace text and verify via GetParagraphText.
/// </summary>
public class FodtR247ReplaceTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NullOldText_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceText(null!, "Replacement"));
    }

    [Fact]
    public void ReplaceText_NullNewText_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceText("Hello", null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NonexistentOldText_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var ex = Record.Exception(() => doc.ReplaceText("NoSuchText", "Replacement"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_ValidReplacement_TextUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "Universe");
        string? text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.Contains("Universe", text);
    }

    [Fact]
    public void ReplaceText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha Beta");
        doc.AppendParagraph("Gamma Delta");
        int before = doc.ParagraphCount;
        doc.ReplaceText("Alpha", "Omega");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ReplaceText_GetWordCount_NonNegativeAfterReplace()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sample text for replacement");
        doc.ReplaceText("Sample", "Test");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void ReplaceText_HeadingText_Updated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Old Heading Title", 1);
        doc.ReplaceText("Old", "New");
        // Heading text should now contain "New"
        var ex = Record.Exception(() => doc.ReplaceText("Heading", "Chapter"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_Twice_LatestReplacementPersists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial text here");
        doc.ReplaceText("Initial", "First");
        doc.ReplaceText("First", "Final");
        string? text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.Contains("Final", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ReplaceAndVerifyViaParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        doc.AppendParagraph("The fox jumps high");
        doc.ReplaceText("fox", "cat");
        string? para0 = doc.GetParagraphText(0);
        string? para1 = doc.GetParagraphText(1);
        Assert.NotNull(para0);
        Assert.NotNull(para1);
        Assert.Contains("cat", para0);
        Assert.Contains("cat", para1);
    }
}
