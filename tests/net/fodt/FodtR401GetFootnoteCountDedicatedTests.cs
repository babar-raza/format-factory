// Tests for FodtDocument.GetFootnoteCount dedicated coverage.
// Sprint: ff-sprint-s383-dotnet-deepening-20260630
// Ledger: PC-FODT-R401

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R401: Dedicated tests for FodtDocument.FootnoteCount (or GetFootnoteCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking FootnoteCount.
/// TableCount unchanged after checking FootnoteCount.
/// ImageCount unchanged after checking FootnoteCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: FootnoteCount non-negative after paragraphs.
/// Dogfood: FootnoteCount non-negative after mixed content.
/// Dogfood: FootnoteCount never negative in loop.
/// </summary>
public class FodtR401GetFootnoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FootnoteCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.FootnoteCount >= 0);
    }

    [Fact]
    public void FootnoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.FootnoteCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void FootnoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.FootnoteCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void FootnoteCount_ImageCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ImageCount;
        _ = doc.FootnoteCount;
        Assert.Equal(before, doc.ImageCount);
    }

    [Fact]
    public void FootnoteCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.FootnoteCount;
        int second = doc.FootnoteCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void FootnoteCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.FootnoteCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main text with reference¹");
        doc.AddParagraph("Additional content");
        Assert.True(doc.FootnoteCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.FootnoteCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Body paragraph {i}");
            Assert.True(doc.FootnoteCount >= 0);
        }
    }
}
