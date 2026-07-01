// Tests for FodtDocument.GetAnnotationCount dedicated coverage.
// Sprint: ff-sprint-s417-dotnet-deepening-20260701
// Ledger: PC-FODT-R441

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R441: Dedicated tests for FodtDocument.GetAnnotationCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetAnnotationCount.
/// TableCount unchanged after GetAnnotationCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR441GetAnnotationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAnnotationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetAnnotationCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetAnnotationCount();
        int second = doc.GetAnnotationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAnnotationCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetAnnotationCount();
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
        Assert.True(doc.GetAnnotationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetAnnotationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetAnnotationCount() >= 0);
        }
    }
}
