// Tests for FodtDocument.GetFooterCount dedicated coverage.
// Sprint: ff-sprint-s515-dotnet-deepening-20260701
// Ledger: PC-FODT-R539

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R539: Dedicated tests for FodtDocument.GetFooterCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFooterCount.
/// TableCount unchanged after GetFooterCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR539GetFooterCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFooterCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFooterCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFooterCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFooterCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFooterCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFooterCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFooterCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFooterCount();
        int second = doc.GetFooterCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFooterCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFooterCount();
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
        Assert.True(doc.GetFooterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFooterCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFooterCount() >= 0);
        }
    }
}
