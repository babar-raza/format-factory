// Tests for FodtDocument.GetEmbeddedObjectCount dedicated coverage.
// Sprint: ff-sprint-s469-dotnet-deepening-20260701
// Ledger: PC-FODT-R493

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R493: Dedicated tests for FodtDocument.GetEmbeddedObjectCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetEmbeddedObjectCount.
/// TableCount unchanged after GetEmbeddedObjectCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR493GetEmbeddedObjectCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEmbeddedObjectCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetEmbeddedObjectCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetEmbeddedObjectCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetEmbeddedObjectCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetEmbeddedObjectCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetEmbeddedObjectCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetEmbeddedObjectCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetEmbeddedObjectCount();
        int second = doc.GetEmbeddedObjectCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEmbeddedObjectCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetEmbeddedObjectCount();
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
        Assert.True(doc.GetEmbeddedObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetEmbeddedObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetEmbeddedObjectCount() >= 0);
        }
    }
}
