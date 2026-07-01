// Tests for FodtDocument.GetPageBreakCount dedicated coverage.
// Sprint: ff-sprint-s436-dotnet-deepening-20260701
// Ledger: PC-FODT-R460

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R460: Dedicated tests for FodtDocument.GetPageBreakCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetPageBreakCount.
/// TableCount unchanged after GetPageBreakCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR460GetPageBreakCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageBreakCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetPageBreakCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetPageBreakCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetPageBreakCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageBreakCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetPageBreakCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageBreakCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetPageBreakCount();
        int second = doc.GetPageBreakCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageBreakCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetPageBreakCount();
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
        Assert.True(doc.GetPageBreakCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetPageBreakCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetPageBreakCount() >= 0);
        }
    }
}
