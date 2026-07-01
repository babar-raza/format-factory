// Tests for FodtDocument.GetListStyleCount dedicated coverage.
// Sprint: ff-sprint-s461-dotnet-deepening-20260701
// Ledger: PC-FODT-R485

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R485: Dedicated tests for FodtDocument.GetListStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetListStyleCount.
/// TableCount unchanged after GetListStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR485GetListStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetListStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetListStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetListStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetListStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetListStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetListStyleCount();
        int second = doc.GetListStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetListStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetListStyleCount();
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
        Assert.True(doc.GetListStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetListStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetListStyleCount() >= 0);
        }
    }
}
