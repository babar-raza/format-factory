// Tests for FodtDocument.GetColorCount dedicated coverage.
// Sprint: ff-sprint-s441-dotnet-deepening-20260701
// Ledger: PC-FODT-R465

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R465: Dedicated tests for FodtDocument.GetColorCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetColorCount.
/// TableCount unchanged after GetColorCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR465GetColorCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetColorCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColorCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetColorCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetColorCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetColorCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetColorCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetColorCount();
        int second = doc.GetColorCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColorCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetColorCount();
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
        Assert.True(doc.GetColorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetColorCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetColorCount() >= 0);
        }
    }
}
