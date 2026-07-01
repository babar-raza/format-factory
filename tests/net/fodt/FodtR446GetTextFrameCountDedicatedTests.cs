// Tests for FodtDocument.GetTextFrameCount dedicated coverage.
// Sprint: ff-sprint-s422-dotnet-deepening-20260701
// Ledger: PC-FODT-R446

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R446: Dedicated tests for FodtDocument.GetTextFrameCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTextFrameCount.
/// TableCount unchanged after GetTextFrameCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR446GetTextFrameCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextFrameCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextFrameCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextFrameCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTextFrameCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextFrameCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTextFrameCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextFrameCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTextFrameCount();
        int second = doc.GetTextFrameCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextFrameCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTextFrameCount();
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
        Assert.True(doc.GetTextFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTextFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTextFrameCount() >= 0);
        }
    }
}
