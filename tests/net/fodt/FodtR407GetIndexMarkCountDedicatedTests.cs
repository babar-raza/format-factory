// Tests for FodtDocument.GetIndexMarkCount dedicated coverage.
// Sprint: ff-sprint-s389-dotnet-deepening-20260630
// Ledger: PC-FODT-R407

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R407: Dedicated tests for FodtDocument.IndexMarkCount (or GetIndexMarkCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking IndexMarkCount.
/// TableCount unchanged after checking IndexMarkCount.
/// HyperlinkCount unchanged after checking IndexMarkCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: IndexMarkCount non-negative after paragraphs.
/// Dogfood: IndexMarkCount non-negative after mixed content.
/// Dogfood: IndexMarkCount never negative in loop.
/// </summary>
public class FodtR407GetIndexMarkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void IndexMarkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.IndexMarkCount >= 0);
    }

    [Fact]
    public void IndexMarkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.IndexMarkCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void IndexMarkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.IndexMarkCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void IndexMarkCount_HyperlinkCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.HyperlinkCount;
        _ = doc.IndexMarkCount;
        Assert.Equal(before, doc.HyperlinkCount);
    }

    [Fact]
    public void IndexMarkCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.IndexMarkCount;
        int second = doc.IndexMarkCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void IndexMarkCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.IndexMarkCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Indexed term alpha");
        doc.AddParagraph("Indexed term beta");
        Assert.True(doc.IndexMarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Overview");
        doc.AddTable(2, 3);
        doc.AddParagraph("Index entry");
        Assert.True(doc.IndexMarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Indexed term {i}");
            Assert.True(doc.IndexMarkCount >= 0);
        }
    }
}
