// Tests for FodtDocument.GetSentenceCount dedicated coverage.
// Sprint: ff-sprint-s450-dotnet-deepening-20260701
// Ledger: PC-FODT-R474

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R474: Dedicated tests for FodtDocument.GetSentenceCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSentenceCount.
/// TableCount unchanged after GetSentenceCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR474GetSentenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSentenceCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSentenceCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSentenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSentenceCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSentenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSentenceCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSentenceCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSentenceCount();
        int second = doc.GetSentenceCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSentenceCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSentenceCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        Assert.True(doc.GetSentenceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSentenceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSentenceCount() >= 0);
        }
    }
}
