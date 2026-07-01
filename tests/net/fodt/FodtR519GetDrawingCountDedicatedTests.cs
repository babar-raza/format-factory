// Tests for FodtDocument.GetDrawingCount dedicated coverage.
// Sprint: ff-sprint-s495-dotnet-deepening-20260701
// Ledger: PC-FODT-R519

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R519: Dedicated tests for FodtDocument.GetDrawingCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetDrawingCount.
/// TableCount unchanged after GetDrawingCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR519GetDrawingCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDrawingCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetDrawingCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDrawingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetDrawingCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDrawingCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetDrawingCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDrawingCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetDrawingCount();
        int second = doc.GetDrawingCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDrawingCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetDrawingCount();
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
        Assert.True(doc.GetDrawingCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetDrawingCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetDrawingCount() >= 0);
        }
    }
}
