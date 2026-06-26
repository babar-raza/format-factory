// Tests for FodtDocument.SetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s242-dotnet-deepening-20260629
// Ledger: PC-FODT-R257

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R257: Dedicated tests for FodtDocument.SetParagraphStyle(int index, string styleName).
/// Null style name → throws exception.
/// Negative index → throws exception.
/// OOB index → throws exception.
/// Valid call → no exception.
/// ParagraphCount unchanged after call.
/// Paragraph text unchanged after style change.
/// Called on first paragraph → no exception.
/// Called on last paragraph → no exception.
/// Called twice same paragraph → no exception.
/// Dogfood: set style on each paragraph, verify count unchanged.
/// </summary>
public class FodtR257SetParagraphStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_NullStyleName_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphStyle(0, null!));
    }

    [Fact]
    public void SetParagraphStyle_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphStyle(-1, "Bold"));
    }

    [Fact]
    public void SetParagraphStyle_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphStyle(10, "Bold"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "Emphasis"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        int before = doc.ParagraphCount;
        doc.SetParagraphStyle(0, "Bold");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphStyle_ParagraphTextUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep this text");
        doc.SetParagraphStyle(0, "Italic");
        string? text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.Contains("Keep this text", text);
    }

    [Fact]
    public void SetParagraphStyle_FirstParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "Normal"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphStyle_LastParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        int last = doc.ParagraphCount - 1;
        var ex = Record.Exception(() => doc.SetParagraphStyle(last, "Body"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphStyle_CalledTwiceSameParagraph_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Target");
        doc.SetParagraphStyle(0, "Style1");
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "Style2"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetStyleOnEach_CountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para0");
        doc.AppendParagraph("Para1");
        doc.AppendParagraph("Para2");
        int before = doc.ParagraphCount;
        for (int i = 0; i < doc.ParagraphCount; i++)
            doc.SetParagraphStyle(i, "Custom");
        Assert.Equal(before, doc.ParagraphCount);
    }
}
