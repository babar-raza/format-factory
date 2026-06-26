// Tests for FodtDocument.CountSentences dedicated coverage.
// Sprint: ff-sprint-s237-dotnet-deepening-20260629
// Ledger: PC-FODT-R252

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R252: Dedicated tests for FodtDocument.CountSentences().
/// Empty document → returns 0.
/// Empty document → non-negative result.
/// Single paragraph with one sentence → positive count.
/// ParagraphCount unchanged after call.
/// Called twice → same result.
/// Multiple paragraphs → count increases.
/// After AppendParagraph → count non-decreasing.
/// Document with heading only → count >= 0.
/// Result is always non-negative.
/// Dogfood: add known-sentence content, verify count is positive.
/// </summary>
public class FodtR252CountSentencesTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CountSentences_EmptyDoc_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.CountSentences());
    }

    [Fact]
    public void CountSentences_EmptyDoc_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.CountSentences() >= 0);
    }

    [Fact]
    public void CountSentences_OneSentence_PositiveCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("This is a single sentence.");
        Assert.True(doc.CountSentences() > 0);
    }

    [Fact]
    public void CountSentences_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First sentence. Second sentence.");
        int before = doc.ParagraphCount;
        _ = doc.CountSentences();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void CountSentences_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world. How are you?");
        int first = doc.CountSentences();
        int second = doc.CountSentences();
        Assert.Equal(first, second);
    }

    [Fact]
    public void CountSentences_TwoParagraphs_NonDecreasing()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph sentence.");
        int afterOne = doc.CountSentences();
        doc.AppendParagraph("Second paragraph sentence.");
        int afterTwo = doc.CountSentences();
        Assert.True(afterTwo >= afterOne);
    }

    [Fact]
    public void CountSentences_HeadingOnly_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Main Title", 1);
        int count = doc.CountSentences();
        Assert.True(count >= 0);
    }

    [Fact]
    public void CountSentences_AfterAppendParagraph_NonDecreasing()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.CountSentences();
        doc.AppendParagraph("Added sentence here.");
        int after = doc.CountSentences();
        Assert.True(after >= before);
    }

    [Fact]
    public void CountSentences_AlwaysNonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sentence one. Sentence two. Sentence three.");
        Assert.True(doc.CountSentences() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownContent_PositiveCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Executive Summary", 1);
        doc.AppendParagraph("The company performed well this quarter. Revenue increased by 15 percent. Customer satisfaction reached an all-time high.");
        doc.AppendParagraph("Looking ahead, we expect continued growth. New markets will be explored.");
        Assert.True(doc.CountSentences() > 0);
        Assert.Equal(2, doc.ParagraphCount);
    }
}
