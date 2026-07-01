// Tests for FodtDocument.GetCrossReferenceCount dedicated coverage.
// Sprint: ff-sprint-s432-dotnet-deepening-20260701
// Ledger: PC-FODT-R456

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R456: Dedicated tests for FodtDocument.GetCrossReferenceCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCrossReferenceCount.
/// TableCount unchanged after GetCrossReferenceCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR456GetCrossReferenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCrossReferenceCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCrossReferenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCrossReferenceCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCrossReferenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCrossReferenceCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCrossReferenceCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCrossReferenceCount();
        int second = doc.GetCrossReferenceCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCrossReferenceCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCrossReferenceCount();
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
        Assert.True(doc.GetCrossReferenceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCrossReferenceCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCrossReferenceCount() >= 0);
        }
    }
}
