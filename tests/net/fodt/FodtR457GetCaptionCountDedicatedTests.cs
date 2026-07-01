// Tests for FodtDocument.GetCaptionCount dedicated coverage.
// Sprint: ff-sprint-s433-dotnet-deepening-20260701
// Ledger: PC-FODT-R457

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R457: Dedicated tests for FodtDocument.GetCaptionCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCaptionCount.
/// TableCount unchanged after GetCaptionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR457GetCaptionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCaptionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCaptionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCaptionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCaptionCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCaptionCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCaptionCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCaptionCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCaptionCount();
        int second = doc.GetCaptionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCaptionCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCaptionCount();
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
        Assert.True(doc.GetCaptionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCaptionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCaptionCount() >= 0);
        }
    }
}
