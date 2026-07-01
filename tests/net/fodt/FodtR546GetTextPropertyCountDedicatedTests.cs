// Tests for FodtDocument.GetTextPropertyCount dedicated coverage.
// Sprint: ff-sprint-s522-dotnet-deepening-20260701
// Ledger: PC-FODT-R546

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R546: Dedicated tests for FodtDocument.GetTextPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTextPropertyCount.
/// TableCount unchanged after GetTextPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR546GetTextPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTextPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTextPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTextPropertyCount();
        int second = doc.GetTextPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTextPropertyCount();
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
        Assert.True(doc.GetTextPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTextPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTextPropertyCount() >= 0);
        }
    }
}
