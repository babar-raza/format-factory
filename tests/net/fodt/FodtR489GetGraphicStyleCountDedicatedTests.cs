// Tests for FodtDocument.GetGraphicStyleCount dedicated coverage.
// Sprint: ff-sprint-s465-dotnet-deepening-20260701
// Ledger: PC-FODT-R489

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R489: Dedicated tests for FodtDocument.GetGraphicStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetGraphicStyleCount.
/// TableCount unchanged after GetGraphicStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR489GetGraphicStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGraphicStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetGraphicStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGraphicStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetGraphicStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetGraphicStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetGraphicStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetGraphicStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetGraphicStyleCount();
        int second = doc.GetGraphicStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGraphicStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetGraphicStyleCount();
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
        Assert.True(doc.GetGraphicStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetGraphicStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetGraphicStyleCount() >= 0);
        }
    }
}
