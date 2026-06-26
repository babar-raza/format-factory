// Tests for FodtDocument.SetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s195-dotnet-deepening-20260629
// Ledger: PC-FODT-R208

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R208: Dedicated tests for FodtDocument.SetParagraphStyle(int index, string styleName).
/// null styleName → throws ArgumentNullException.
/// index &lt; 0 → throws ArgumentOutOfRangeException.
/// index >= ParagraphCount → throws ArgumentOutOfRangeException.
/// Valid: does not throw.
/// ParagraphCount unchanged after call.
/// Paragraph text unchanged after style change.
/// Called on heading paragraph: no exception.
/// Called twice: no exception.
/// Covers: null style throws; negative index throws; at-count throws;
/// valid no exception; count unchanged; text unchanged;
/// heading paragraph no exception; called twice no exception;
/// dogfood three paras style each; dogfood style does not change text.
/// </summary>
public class FodtR208SetParagraphStyleTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_NullStyleName_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentNullException>(() => doc.SetParagraphStyle(0, null!));
    }

    [Fact]
    public void SetParagraphStyle_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(-1, "Bold"));
    }

    [Fact]
    public void SetParagraphStyle_AtCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(1, "Bold"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_ValidCall_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "MyStyle"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphStyle_ValidCall_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var before = doc.ParagraphCount;
        doc.SetParagraphStyle(0, "Bold");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphStyle_ValidCall_TextUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("OriginalText");
        doc.SetParagraphStyle(0, "Heading1");
        Assert.Equal("OriginalText", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphStyle_HeadingParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "CustomHeading"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphStyle_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        doc.SetParagraphStyle(0, "Style1");
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "Style2"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_StyleEach()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        for (int i = 0; i < 3; i++)
            doc.SetParagraphStyle(i, $"Style{i}");
        // All texts still accessible
        Assert.Equal("A", doc.GetParagraphText(0));
        Assert.Equal("B", doc.GetParagraphText(1));
        Assert.Equal("C", doc.GetParagraphText(2));
    }

    [Fact]
    public void DogfoodPipeline_StyleDoesNotChangeText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.SetParagraphStyle(0, "BoldLarge");
        Assert.Equal("Hello World", doc.GetParagraphText(0));
        Assert.Equal(1, doc.ParagraphCount);
    }
}
