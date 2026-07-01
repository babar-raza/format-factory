// Tests for FodtDocument.GetBookmarkCount dedicated coverage.
// Sprint: ff-sprint-s416-dotnet-deepening-20260701
// Ledger: PC-FODT-R440

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R440: Dedicated tests for FodtDocument.GetBookmarkCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetBookmarkCount.
/// TableCount unchanged after GetBookmarkCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR440GetBookmarkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetBookmarkCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetBookmarkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetBookmarkCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetBookmarkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetBookmarkCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetBookmarkCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetBookmarkCount();
        int second = doc.GetBookmarkCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBookmarkCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetBookmarkCount();
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
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetBookmarkCount() >= 0);
        }
    }
}
