// Tests for FodtDocument.RemoveAllParagraphs dedicated coverage.
// Sprint: ff-sprint-s179-dotnet-deepening-20260628
// Ledger: PC-FODT-R188

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R188: Dedicated tests for FodtDocument.RemoveAllParagraphs().
/// Removes all paragraph and heading elements from the document body.
/// No guards — safe to call on empty document.
/// After call: ParagraphCount=0; GetHeadingCount()=0.
/// Covers: empty doc no-op; single paragraph removed; multiple paragraphs removed;
/// headings also removed; ParagraphCount=0 after; GetHeadingCount()=0 after;
/// can re-append after removal; wordCount=0 after; idempotent (double call safe);
/// dogfood populate-remove-repopulate pipeline.
/// </summary>
public class FodtR188RemoveAllParagraphsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_EmptyDocument_NoOp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.RemoveAllParagraphs(); // should not throw
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_SingleParagraph_ParagraphCountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only one");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_MultipleParagraphs_AllRemoved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_HeadingsAlsoRemoved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Body");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void RemoveAllParagraphs_WordCountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.AppendHeading("Title", 1);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void RemoveAllParagraphs_Idempotent_DoubleCallSafe()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");
        doc.RemoveAllParagraphs();
        doc.RemoveAllParagraphs(); // second call should not throw
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_CanReAppendAfterRemoval()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old");
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("New");
        Assert.Equal(1, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PopulateThenRemoveThenRepopulate()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Old Title", 1);
        doc.AppendParagraph("Old Body");
        doc.RemoveAllParagraphs();
        doc.AppendHeading("New Title", 1);
        doc.AppendParagraph("New Body");
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void DogfoodPipeline_MixedContentCleared_GetWordCountZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro paragraph");
        doc.AppendHeading("Main Section", 1);
        doc.AppendParagraph("Body content here");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.GetWordCount());
        Assert.Equal(0, doc.ParagraphCount);
    }
}
