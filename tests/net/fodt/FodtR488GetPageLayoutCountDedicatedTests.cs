// Tests for FodtDocument.GetPageLayoutCount dedicated coverage.
// Sprint: ff-sprint-s464-dotnet-deepening-20260701
// Ledger: PC-FODT-R488

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R488: Dedicated tests for FodtDocument.GetPageLayoutCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetPageLayoutCount.
/// TableCount unchanged after GetPageLayoutCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR488GetPageLayoutCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageLayoutCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetPageLayoutCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetPageLayoutCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetPageLayoutCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageLayoutCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetPageLayoutCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageLayoutCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetPageLayoutCount();
        int second = doc.GetPageLayoutCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageLayoutCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetPageLayoutCount();
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
        Assert.True(doc.GetPageLayoutCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetPageLayoutCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetPageLayoutCount() >= 0);
        }
    }
}
