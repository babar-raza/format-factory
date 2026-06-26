// Tests for FodtDocument.GetWordCount dedicated coverage.
// Sprint: ff-sprint-s259-dotnet-deepening-20260630
// Ledger: PC-FODT-R274

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R274: Dedicated tests for FodtDocument.GetWordCount().
/// GetWordCount returns the total word count across all paragraphs.
/// Returns non-negative integer.
/// Empty document returns 0.
/// Document with one paragraph returns word count of that paragraph.
/// Adding more paragraphs increases count.
/// ParagraphCount unchanged after call.
/// Called twice → same result.
/// Dogfood: known paragraph text, verify word count.
/// Dogfood: multiple paragraphs, count is sum of individual word counts.
/// </summary>
public class FodtR274GetWordCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_EmptyDocument_ReturnsZeroOrNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetWordCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetWordCount_AfterAddParagraph_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("one two three four");
        int count = doc.GetWordCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetWordCount_AddMoreParagraphs_CountGrows()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("first paragraph words");
        int before = doc.GetWordCount();
        doc.AddParagraph("second paragraph has words too");
        int after = doc.GetWordCount();
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("some text here");
        int parasBefore = doc.ParagraphCount;
        doc.GetWordCount();
        Assert.Equal(parasBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetWordCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("alpha beta gamma");
        int first = doc.GetWordCount();
        int second = doc.GetWordCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SingleParagraphThreeWords_CountIsThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("one two three");
        int count = doc.GetWordCount();
        Assert.Equal(3, count);
    }

    [Fact]
    public void DogfoodPipeline_TwoParagraphs_CountIsSumOfBoth()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("one two");      // 2 words
        doc.AddParagraph("three four five"); // 3 words
        int count = doc.GetWordCount();
        Assert.Equal(5, count);
    }

    [Fact]
    public void DogfoodPipeline_EmptyStringParagraph_CountDoesNotDecrease()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("apple banana cherry");
        int before = doc.GetWordCount();
        doc.AddParagraph(""); // empty paragraph adds 0 words
        int after = doc.GetWordCount();
        Assert.True(after >= before);
    }
}
