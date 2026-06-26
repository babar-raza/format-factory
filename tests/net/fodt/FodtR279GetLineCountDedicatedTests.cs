// Tests for FodtDocument.GetLineCount dedicated coverage.
// Sprint: ff-sprint-s264-dotnet-deepening-20260630
// Ledger: PC-FODT-R279

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R279: Dedicated tests for FodtDocument.GetLineCount().
/// GetLineCount returns the total number of text lines in the document.
/// Returns non-negative integer.
/// New/empty document returns 0 or non-negative.
/// After adding paragraphs, count is non-negative.
/// Adding more paragraphs does not decrease count.
/// ParagraphCount unchanged after call.
/// Called twice → same result.
/// Dogfood: add single-line paragraph, count >= 1.
/// Dogfood: add multi-paragraph content, count grows.
/// </summary>
public class FodtR279GetLineCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLineCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int count = doc.GetLineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLineCount_NewDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetLineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLineCount_AfterAddParagraph_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First line of text");
        int count = doc.GetLineCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetLineCount_MoreParagraphsDoNotDecreaseCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("One paragraph");
        int before = doc.GetLineCount();
        doc.AddParagraph("Another paragraph");
        int after = doc.GetLineCount();
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLineCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int parasBefore = doc.ParagraphCount;
        doc.GetLineCount();
        Assert.Equal(parasBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetLineCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Consistent content");
        int first = doc.GetLineCount();
        int second = doc.GetLineCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SingleLineParagraph_CountAtLeastOne()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("This is one line");
        int count = doc.GetLineCount();
        Assert.True(count >= 1);
    }

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_CountAtLeastThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Line one");
        doc.AddParagraph("Line two");
        doc.AddParagraph("Line three");
        int count = doc.GetLineCount();
        Assert.True(count >= 3);
    }

    [Fact]
    public void DogfoodPipeline_AddingParagraphsGrowsCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First");
        int after1 = doc.GetLineCount();
        doc.AddParagraph("Second");
        int after2 = doc.GetLineCount();
        Assert.True(after2 >= after1);
    }
}
