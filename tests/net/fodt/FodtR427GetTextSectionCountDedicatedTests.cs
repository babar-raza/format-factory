// Tests for FodtDocument.GetTextSectionCount dedicated coverage.
// Sprint: ff-sprint-s403-dotnet-deepening-20260701
// Ledger: PC-FODT-R427

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R427: Dedicated tests for FodtDocument.GetTextSectionCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetTextSectionCount.
/// TableCount unchanged after GetTextSectionCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR427GetTextSectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextSectionCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetTextSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTextSectionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetTextSectionCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTextSectionCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetTextSectionCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTextSectionCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetTextSectionCount();
        int second = doc.GetTextSectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTextSectionCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetTextSectionCount();
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
        Assert.True(doc.GetTextSectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetTextSectionCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetTextSectionCount() >= 0);
        }
    }
}
