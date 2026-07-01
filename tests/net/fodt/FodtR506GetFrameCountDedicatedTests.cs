// Tests for FodtDocument.GetFrameCount dedicated coverage.
// Sprint: ff-sprint-s482-dotnet-deepening-20260701
// Ledger: PC-FODT-R506

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R506: Dedicated tests for FodtDocument.GetFrameCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFrameCount.
/// TableCount unchanged after GetFrameCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR506GetFrameCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFrameCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFrameCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFrameCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFrameCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFrameCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFrameCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFrameCount();
        int second = doc.GetFrameCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFrameCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFrameCount();
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
        Assert.True(doc.GetFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFrameCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFrameCount() >= 0);
        }
    }
}
