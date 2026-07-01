// Tests for FodtDocument.GetFrameStyleCount dedicated coverage.
// Sprint: ff-sprint-s407-dotnet-deepening-20260701
// Ledger: PC-FODT-R431

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R431: Dedicated tests for FodtDocument.GetFrameStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFrameStyleCount.
/// TableCount unchanged after GetFrameStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR431GetFrameStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFrameStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFrameStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFrameStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFrameStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFrameStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFrameStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFrameStyleCount();
        int second = doc.GetFrameStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFrameStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFrameStyleCount();
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
        Assert.True(doc.GetFrameStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFrameStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFrameStyleCount() >= 0);
        }
    }
}
