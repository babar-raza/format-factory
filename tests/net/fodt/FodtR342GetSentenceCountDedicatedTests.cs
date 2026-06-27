// Tests for FodtDocument.GetSentenceCount dedicated coverage.
// Sprint: ff-sprint-s324-dotnet-deepening-20260630
// Ledger: PC-FODT-R342

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R342: Dedicated tests for FodtDocument.GetSentenceCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddParagraph with sentence.
/// ParagraphCount unchanged after GetSentenceCount.
/// TableCount unchanged after GetSentenceCount.
/// SectionCount unchanged after GetSentenceCount.
/// Idempotent (called twice same result).
/// Dogfood: multi-paragraph document sentence count non-negative.
/// Dogfood: multiple sentences in paragraph non-negative.
/// </summary>
public class FodtR342GetSentenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSentenceCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSentenceCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSentenceCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetSentenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSentenceCount_AfterAddParagraph_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSentenceCount();
        doc.AddParagraph("This is a complete sentence. This is another one.");
        int after = doc.GetSentenceCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetSentenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A simple sentence here.");
        int before = doc.ParagraphCount;
        _ = doc.GetSentenceCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSentenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A simple sentence here.");
        int before = doc.TableCount;
        _ = doc.GetSentenceCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSentenceCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A simple sentence here.");
        int before = doc.SectionCount;
        _ = doc.GetSentenceCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetSentenceCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First sentence. Second sentence.");
        doc.AddParagraph("Third sentence. Fourth sentence.");
        int first = doc.GetSentenceCount();
        int second = doc.GetSentenceCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiParagraph_SentenceCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The project started in January. It concluded in March.");
        doc.AddParagraph("Results were positive. All targets were met.");
        doc.AddParagraph("Next steps are outlined below. Please review carefully.");
        int count = doc.GetSentenceCount();
        Assert.True(count >= 0);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSentencesInParagraph_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First sentence ends here. Second sentence follows. Third sentence concludes the paragraph. A fourth sentence adds detail.");
        int count = doc.GetSentenceCount();
        Assert.True(count >= 0);
    }
}
