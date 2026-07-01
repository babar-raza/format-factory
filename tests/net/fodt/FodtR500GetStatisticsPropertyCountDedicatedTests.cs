// Tests for FodtDocument.GetStatisticsPropertyCount dedicated coverage.
// Sprint: ff-sprint-s476-dotnet-deepening-20260701
// Ledger: PC-FODT-R500

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R500: Dedicated tests for FodtDocument.GetStatisticsPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetStatisticsPropertyCount.
/// TableCount unchanged after GetStatisticsPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR500GetStatisticsPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStatisticsPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetStatisticsPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetStatisticsPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetStatisticsPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetStatisticsPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetStatisticsPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetStatisticsPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetStatisticsPropertyCount();
        int second = doc.GetStatisticsPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetStatisticsPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetStatisticsPropertyCount();
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
        Assert.True(doc.GetStatisticsPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetStatisticsPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetStatisticsPropertyCount() >= 0);
        }
    }
}
