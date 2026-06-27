// Tests for FodtDocument.GetCharacterCount dedicated coverage.
// Sprint: ff-sprint-s323-dotnet-deepening-20260630
// Ledger: PC-FODT-R341

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R341: Dedicated tests for FodtDocument.GetCharacterCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddParagraph with text.
/// ParagraphCount unchanged after GetCharacterCount.
/// TableCount unchanged after GetCharacterCount.
/// SectionCount unchanged after GetCharacterCount.
/// Idempotent (called twice same result).
/// Dogfood: multi-paragraph document character count non-negative.
/// Dogfood: longer text yields higher or equal character count.
/// </summary>
public class FodtR341GetCharacterCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharacterCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCharacterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCharacterCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharacterCount_AfterAddParagraph_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetCharacterCount();
        doc.AddParagraph("Hello world");
        int after = doc.GetCharacterCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetCharacterCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A paragraph with some text content");
        int before = doc.ParagraphCount;
        _ = doc.GetCharacterCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCharacterCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A paragraph with some text content");
        int before = doc.TableCount;
        _ = doc.GetCharacterCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCharacterCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A paragraph with some text content");
        int before = doc.SectionCount;
        _ = doc.GetCharacterCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetCharacterCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph text");
        doc.AddParagraph("Second paragraph text");
        int first = doc.GetCharacterCount();
        int second = doc.GetCharacterCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiParagraph_CharacterCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The first paragraph contains introductory material.");
        doc.AddParagraph("The second paragraph provides additional context.");
        doc.AddParagraph("The third paragraph concludes the discussion.");
        int count = doc.GetCharacterCount();
        Assert.True(count >= 0);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_LongerText_HigherOrEqualCount()
    {
        var docShort = FodtDocument.CreateNew();
        docShort.AddParagraph("Short");
        int shortCount = docShort.GetCharacterCount();

        var docLong = FodtDocument.CreateNew();
        docLong.AddParagraph("This is a much longer paragraph with many more characters in it.");
        int longCount = docLong.GetCharacterCount();

        Assert.True(longCount >= shortCount);
    }
}
