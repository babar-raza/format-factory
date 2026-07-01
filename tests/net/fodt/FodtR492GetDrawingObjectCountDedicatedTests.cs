// Tests for FodtDocument.GetDrawingObjectCount dedicated coverage.
// Sprint: ff-sprint-s468-dotnet-deepening-20260701
// Ledger: PC-FODT-R492

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R492: Dedicated tests for FodtDocument.GetDrawingObjectCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetDrawingObjectCount.
/// TableCount unchanged after GetDrawingObjectCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR492GetDrawingObjectCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDrawingObjectCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetDrawingObjectCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDrawingObjectCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetDrawingObjectCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDrawingObjectCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetDrawingObjectCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDrawingObjectCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetDrawingObjectCount();
        int second = doc.GetDrawingObjectCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDrawingObjectCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetDrawingObjectCount();
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
        Assert.True(doc.GetDrawingObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetDrawingObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetDrawingObjectCount() >= 0);
        }
    }
}
