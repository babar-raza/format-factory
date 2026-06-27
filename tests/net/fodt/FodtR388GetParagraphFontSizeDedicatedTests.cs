// Tests for FodtDocument.GetParagraphFontSize dedicated coverage.
// Sprint: ff-sprint-s370-dotnet-deepening-20260630
// Ledger: PC-FODT-R388

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R388: Dedicated tests for FodtDocument.GetParagraphFontSize().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid paragraph returns non-negative.
/// ParagraphCount unchanged after GetParagraphFontSize.
/// TableCount unchanged after GetParagraphFontSize.
/// Idempotent (called twice same result).
/// Dogfood: SetParagraphFontSize 18 then GetParagraphFontSize returns 18.
/// Dogfood: multiple paragraphs each returns non-negative size.
/// </summary>
public class FodtR388GetParagraphFontSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphFontSize_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFontSize(-1));
    }

    [Fact]
    public void GetParagraphFontSize_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFontSize(99));
    }

    [Fact]
    public void GetParagraphFontSize_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFontSize(0));
    }

    [Fact]
    public void GetParagraphFontSize_ValidParagraph_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        double size = doc.GetParagraphFontSize(0);
        Assert.True(size >= 0);
    }

    [Fact]
    public void GetParagraphFontSize_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphFontSize(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphFontSize_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        doc.AddTable(2, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetParagraphFontSize(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphFontSize_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph");
        double first = doc.GetParagraphFontSize(0);
        double second = doc.GetParagraphFontSize(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontSize18_Returns18()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Headline paragraph");
        doc.SetParagraphFontSize(0, 18.0);
        double size = doc.GetParagraphFontSize(0);
        Assert.Equal(18.0, size, 1);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First");
        doc.AddParagraph("Second");
        doc.AddParagraph("Third");
        Assert.True(doc.GetParagraphFontSize(0) >= 0);
        Assert.True(doc.GetParagraphFontSize(1) >= 0);
        Assert.True(doc.GetParagraphFontSize(2) >= 0);
    }
}
