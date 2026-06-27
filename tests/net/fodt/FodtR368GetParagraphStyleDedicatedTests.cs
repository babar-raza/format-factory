// Tests for FodtDocument.GetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s350-dotnet-deepening-20260630
// Ledger: PC-FODT-R368

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R368: Dedicated tests for FodtDocument.GetParagraphStyle().
/// Negative paragraph index throws.
/// Out-of-range paragraph index throws.
/// Empty document throws.
/// Valid paragraph returns non-null.
/// ParagraphCount unchanged after GetParagraphStyle.
/// TableCount unchanged after GetParagraphStyle.
/// Idempotent (called twice same result).
/// After SetParagraphStyle returns expected style.
/// Dogfood: multiple paragraphs with different styles each non-null.
/// </summary>
public class FodtR368GetParagraphStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyle_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphStyle(-1));
    }

    [Fact]
    public void GetParagraphStyle_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphStyle(99));
    }

    [Fact]
    public void GetParagraphStyle_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphStyle(0));
    }

    [Fact]
    public void GetParagraphStyle_ValidParagraph_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Sample text");
        string? style = doc.GetParagraphStyle(0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetParagraphStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Counted paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphStyle(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphStyle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Counted paragraph");
        int before = doc.TableCount;
        _ = doc.GetParagraphStyle(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphStyle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph");
        string? first = doc.GetParagraphStyle(0);
        string? second = doc.GetParagraphStyle(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphStyle_AfterSetStyle_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Heading text");
        doc.SetParagraphStyle(0, "Heading 1");
        string? style = doc.GetParagraphStyle(0);
        Assert.NotNull(style);
        Assert.Equal("Heading 1", style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_DifferentStyles()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Title");
        doc.AddParagraph("Body text content goes here");
        doc.AddParagraph("Footer note");
        doc.SetParagraphStyle(0, "Title");
        doc.SetParagraphStyle(1, "Body Text");
        doc.SetParagraphStyle(2, "Footer");
        Assert.NotNull(doc.GetParagraphStyle(0));
        Assert.NotNull(doc.GetParagraphStyle(1));
        Assert.NotNull(doc.GetParagraphStyle(2));
    }
}
