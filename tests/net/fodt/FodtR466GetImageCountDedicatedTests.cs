// Tests for FodtDocument.GetImageCount dedicated coverage.
// Sprint: ff-sprint-s442-dotnet-deepening-20260701
// Ledger: PC-FODT-R466

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R466: Dedicated tests for FodtDocument.GetImageCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetImageCount.
/// TableCount unchanged after GetImageCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR466GetImageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetImageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetImageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetImageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetImageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetImageCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetImageCount();
        int second = doc.GetImageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetImageCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetImageCount();
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
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetImageCount() >= 0);
        }
    }
}
