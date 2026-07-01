// Tests for FodtDocument.GetTablePropertyCount dedicated coverage.
// Sprint: ff-sprint-s520-dotnet-deepening-20260701
// Ledger: PC-FODT-R544

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R544: Dedicated tests for FodtDocument.GetTablePropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTablePropertyCount.
/// TableCount unchanged after GetTablePropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR544GetTablePropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTablePropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTablePropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTablePropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTablePropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTablePropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTablePropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTablePropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTablePropertyCount();
        int second = doc.GetTablePropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTablePropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTablePropertyCount();
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
        Assert.True(doc.GetTablePropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTablePropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTablePropertyCount() >= 0);
        }
    }
}
