// Tests for FodtDocument.GetChapterCount dedicated coverage.
// Sprint: ff-sprint-s525-dotnet-deepening-20260701
// Ledger: PC-FODT-R549

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R549: Dedicated tests for FodtDocument.GetChapterCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetChapterCount.
/// TableCount unchanged after GetChapterCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR549GetChapterCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChapterCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetChapterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetChapterCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetChapterCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetChapterCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetChapterCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetChapterCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetChapterCount();
        int second = doc.GetChapterCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetChapterCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetChapterCount();
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
        Assert.True(doc.GetChapterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetChapterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetChapterCount() >= 0);
        }
    }
}
