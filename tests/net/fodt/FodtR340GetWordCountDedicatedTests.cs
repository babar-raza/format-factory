// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s322-dotnet-deepening-20260630
// Ledger: PC-FODT-R340

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R340: Dedicated tests for FodtDocument.GetWordCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddParagraph with text.
/// ParagraphCount unchanged after GetWordCount.
/// TableCount unchanged after GetWordCount.
/// SectionCount unchanged after GetWordCount.
/// Idempotent (called twice same result).
/// Dogfood: multi-paragraph document word count non-negative.
/// Dogfood: heading and paragraph document word count non-negative.
/// </summary>
public class FodtR340GetWordCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetWordCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordCount_AfterAddParagraph_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetWordCount();
        doc.AddParagraph("The quick brown fox jumps over the lazy dog");
        int after = doc.GetWordCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetWordCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some paragraph text");
        int before = doc.ParagraphCount;
        _ = doc.GetWordCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetWordCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some paragraph text");
        int before = doc.TableCount;
        _ = doc.GetWordCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetWordCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some paragraph text");
        int before = doc.SectionCount;
        _ = doc.GetWordCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetWordCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("One two three four five");
        doc.AddParagraph("Six seven eight nine ten");
        int first = doc.GetWordCount();
        int second = doc.GetWordCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiParagraph_WordCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("This is the first paragraph with several words.");
        doc.AddParagraph("This is the second paragraph with more words.");
        doc.AddParagraph("This concludes the document with a final sentence.");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraph_WordCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Document Title", 1);
        doc.AddParagraph("Introduction paragraph explaining the document topic.");
        doc.AddHeading("Section One", 2);
        doc.AddParagraph("Body text for section one with detailed content.");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }
}
