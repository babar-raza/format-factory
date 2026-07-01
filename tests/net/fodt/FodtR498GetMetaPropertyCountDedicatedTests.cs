// Tests for FodtDocument.GetMetaPropertyCount dedicated coverage.
// Sprint: ff-sprint-s474-dotnet-deepening-20260701
// Ledger: PC-FODT-R498

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R498: Dedicated tests for FodtDocument.GetMetaPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetMetaPropertyCount.
/// TableCount unchanged after GetMetaPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR498GetMetaPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetaPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetMetaPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetMetaPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetMetaPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetaPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetMetaPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetaPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetMetaPropertyCount();
        int second = doc.GetMetaPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetaPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetMetaPropertyCount();
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
        Assert.True(doc.GetMetaPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetMetaPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetMetaPropertyCount() >= 0);
        }
    }
}
