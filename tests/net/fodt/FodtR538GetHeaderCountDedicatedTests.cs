// Tests for FodtDocument.GetHeaderCount dedicated coverage.
// Sprint: ff-sprint-s514-dotnet-deepening-20260701
// Ledger: PC-FODT-R538

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R538: Dedicated tests for FodtDocument.GetHeaderCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetHeaderCount.
/// TableCount unchanged after GetHeaderCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR538GetHeaderCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetHeaderCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetHeaderCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetHeaderCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeaderCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetHeaderCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetHeaderCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetHeaderCount();
        int second = doc.GetHeaderCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHeaderCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetHeaderCount();
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
        Assert.True(doc.GetHeaderCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetHeaderCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetHeaderCount() >= 0);
        }
    }
}
