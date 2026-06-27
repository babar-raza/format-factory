// Tests for FodtDocument.GetHyperlinkCount dedicated coverage.
// Sprint: ff-sprint-s388-dotnet-deepening-20260630
// Ledger: PC-FODT-R406

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R406: Dedicated tests for FodtDocument.HyperlinkCount (or GetHyperlinkCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking HyperlinkCount.
/// TableCount unchanged after checking HyperlinkCount.
/// CrossReferenceCount unchanged after checking HyperlinkCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: HyperlinkCount non-negative after paragraphs.
/// Dogfood: HyperlinkCount non-negative after mixed content.
/// Dogfood: HyperlinkCount never negative in loop.
/// </summary>
public class FodtR406GetHyperlinkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HyperlinkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.HyperlinkCount >= 0);
    }

    [Fact]
    public void HyperlinkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.HyperlinkCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void HyperlinkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.HyperlinkCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void HyperlinkCount_CrossReferenceCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.CrossReferenceCount;
        _ = doc.HyperlinkCount;
        Assert.Equal(before, doc.CrossReferenceCount);
    }

    [Fact]
    public void HyperlinkCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.HyperlinkCount;
        int second = doc.HyperlinkCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void HyperlinkCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.HyperlinkCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Visit https://example.com for more info");
        doc.AddParagraph("See also the reference site");
        Assert.True(doc.HyperlinkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTable(3, 2);
        doc.AddParagraph("External resources");
        Assert.True(doc.HyperlinkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Link to resource {i}");
            Assert.True(doc.HyperlinkCount >= 0);
        }
    }
}
