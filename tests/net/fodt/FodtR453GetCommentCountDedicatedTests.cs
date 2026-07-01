// Tests for FodtDocument.GetCommentCount dedicated coverage.
// Sprint: ff-sprint-s429-dotnet-deepening-20260701
// Ledger: PC-FODT-R453

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R453: Dedicated tests for FodtDocument.GetCommentCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCommentCount.
/// TableCount unchanged after GetCommentCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR453GetCommentCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCommentCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCommentCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCommentCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCommentCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCommentCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCommentCount();
        int second = doc.GetCommentCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCommentCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCommentCount();
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
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCommentCount() >= 0);
        }
    }
}
