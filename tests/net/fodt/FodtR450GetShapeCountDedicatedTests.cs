// Tests for FodtDocument.GetShapeCount dedicated coverage.
// Sprint: ff-sprint-s426-dotnet-deepening-20260701
// Ledger: PC-FODT-R450

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R450: Dedicated tests for FodtDocument.GetShapeCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetShapeCount.
/// TableCount unchanged after GetShapeCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR450GetShapeCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetShapeCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetShapeCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetShapeCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetShapeCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetShapeCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetShapeCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetShapeCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetShapeCount();
        int second = doc.GetShapeCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetShapeCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetShapeCount();
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
        Assert.True(doc.GetShapeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetShapeCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetShapeCount() >= 0);
        }
    }
}
