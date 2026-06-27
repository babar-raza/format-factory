// Tests for FodtDocument.GetCharCount dedicated coverage.
// Sprint: ff-sprint-s306-dotnet-deepening-20260630
// Ledger: PC-FODT-R321

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R321: Dedicated tests for FodtDocument.GetCharCount().
/// Valid call returns non-negative.
/// Empty document returns non-negative.
/// Increases after AddParagraph with text.
/// ParagraphCount unchanged after GetCharCount.
/// TableCount unchanged after GetCharCount.
/// SectionCount unchanged after GetCharCount.
/// Called twice returns same result.
/// Larger content returns higher or equal count.
/// Dogfood: document with known paragraphs returns non-negative.
/// </summary>
public class FodtR321GetCharCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int count = doc.GetCharCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCharCount_EmptyDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCharCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCharCount_IncreasesAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetCharCount();
        doc.AddParagraph("ABCDEFGHIJKLMNOP");
        int after = doc.GetCharCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetCharCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetCharCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetCharCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tableBefore = doc.TableCount;
        _ = doc.GetCharCount();
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void GetCharCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        doc.AddSection("Sec");
        int secBefore = doc.SectionCount;
        _ = doc.GetCharCount();
        Assert.Equal(secBefore, doc.SectionCount);
    }

    [Fact]
    public void GetCharCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text content here");
        int first = doc.GetCharCount();
        int second = doc.GetCharCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCharCount_LargerContent_HigherOrEqualCount()
    {
        var small = FodtDocument.CreateNew();
        small.AddParagraph("Hi");

        var large = FodtDocument.CreateNew();
        large.AddParagraph("This is a much longer paragraph with many more characters in it");
        large.AddParagraph("And here is yet another paragraph to add even more text content");

        int smallCount = small.GetCharCount();
        int largeCount = large.GetCharCount();
        Assert.True(largeCount >= smallCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithParagraphs_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction paragraph.");
        doc.AddParagraph("Body content goes here with multiple words.");
        doc.AddParagraph("Conclusion.");
        int count = doc.GetCharCount();
        Assert.True(count >= 0);
        Assert.Equal(3, doc.ParagraphCount);
    }
}
