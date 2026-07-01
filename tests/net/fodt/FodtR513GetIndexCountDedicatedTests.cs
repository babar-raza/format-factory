// Tests for FodtDocument.GetIndexCount dedicated coverage.
// Sprint: ff-sprint-s489-dotnet-deepening-20260701
// Ledger: PC-FODT-R513

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R513: Dedicated tests for FodtDocument.GetIndexCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetIndexCount.
/// TableCount unchanged after GetIndexCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR513GetIndexCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIndexCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetIndexCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetIndexCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetIndexCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetIndexCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetIndexCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetIndexCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetIndexCount();
        int second = doc.GetIndexCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetIndexCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetIndexCount();
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
        Assert.True(doc.GetIndexCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetIndexCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetIndexCount() >= 0);
        }
    }
}
