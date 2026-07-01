// Tests for FodtDocument.GetSpanCount dedicated coverage.
// Sprint: ff-sprint-s505-dotnet-deepening-20260701
// Ledger: PC-FODT-R529

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R529: Dedicated tests for FodtDocument.GetSpanCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSpanCount.
/// TableCount unchanged after GetSpanCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR529GetSpanCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSpanCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSpanCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSpanCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSpanCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSpanCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSpanCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSpanCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSpanCount();
        int second = doc.GetSpanCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSpanCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSpanCount();
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
        Assert.True(doc.GetSpanCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSpanCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSpanCount() >= 0);
        }
    }
}
