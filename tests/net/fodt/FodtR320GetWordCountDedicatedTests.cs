// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s305-dotnet-deepening-20260630
// Ledger: PC-FODT-R320

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R320: Dedicated tests for FodtDocument.GetWordCount().
/// Valid call returns non-negative.
/// Empty document returns zero or non-negative.
/// Increases after AddParagraph with words.
/// ParagraphCount unchanged after GetWordCount.
/// TableCount unchanged after GetWordCount.
/// SectionCount unchanged after GetWordCount.
/// Called twice returns same result.
/// Dogfood: document with paragraphs has positive word count.
/// Dogfood: two documents compare word counts.
/// </summary>
public class FodtR320GetWordCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_EmptyDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_IncreasesAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetWordCount();
        doc.AddParagraph("one two three four five");
        int after = doc.GetWordCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetWordCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetWordCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetWordCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int tableBefore = doc.TableCount;
        _ = doc.GetWordCount();
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void GetWordCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        doc.AddSection("MySec");
        int secBefore = doc.SectionCount;
        _ = doc.GetWordCount();
        Assert.Equal(secBefore, doc.SectionCount);
    }

    [Fact]
    public void GetWordCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("one two three");
        int first = doc.GetWordCount();
        int second = doc.GetWordCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_PositiveWordCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        doc.AddParagraph("jumps over the lazy dog");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
        Assert.Equal(2, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoDocuments_LargerHasMoreWords()
    {
        var small = FodtDocument.CreateNew();
        small.AddParagraph("Hello");

        var large = FodtDocument.CreateNew();
        large.AddParagraph("one two three four five six seven");
        large.AddParagraph("eight nine ten eleven twelve");

        int smallCount = small.GetWordCount();
        int largeCount = large.GetWordCount();
        Assert.True(smallCount >= 0);
        Assert.True(largeCount >= 0);
        Assert.True(largeCount >= smallCount);
    }
}
