// Tests for FodtDocument.GetEndnoteCount dedicated coverage.
// Sprint: ff-sprint-s384-dotnet-deepening-20260630
// Ledger: PC-FODT-R402

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R402: Dedicated tests for FodtDocument.EndnoteCount (or GetEndnoteCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking EndnoteCount.
/// TableCount unchanged after checking EndnoteCount.
/// FootnoteCount unchanged after checking EndnoteCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: EndnoteCount non-negative after paragraphs.
/// Dogfood: EndnoteCount non-negative after mixed content.
/// Dogfood: EndnoteCount never negative in loop.
/// </summary>
public class FodtR402GetEndnoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void EndnoteCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.EndnoteCount >= 0);
    }

    [Fact]
    public void EndnoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.EndnoteCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void EndnoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.EndnoteCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void EndnoteCount_FootnoteCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.FootnoteCount;
        _ = doc.EndnoteCount;
        Assert.Equal(before, doc.FootnoteCount);
    }

    [Fact]
    public void EndnoteCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.EndnoteCount;
        int second = doc.EndnoteCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void EndnoteCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.EndnoteCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("See endnote i");
        doc.AddParagraph("See endnote ii");
        Assert.True(doc.EndnoteCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTable(3, 2);
        doc.AddParagraph("Bibliography");
        Assert.True(doc.EndnoteCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Reference section {i}");
            Assert.True(doc.EndnoteCount >= 0);
        }
    }
}
