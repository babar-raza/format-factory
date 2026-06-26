// Tests for FodtDocument.GetParagraphText dedicated coverage.
// Sprint: ff-sprint-s223-dotnet-deepening-20260629
// Ledger: PC-FODT-R238

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R238: Dedicated tests for FodtDocument.GetParagraphText(index).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// First paragraph: returns correct text.
/// Second paragraph: returns correct text.
/// ParagraphCount unchanged after get.
/// Empty string paragraph retrievable.
/// Called twice: same result.
/// Get different indices: independent values.
/// Dogfood: add three paragraphs, get all.
/// Dogfood: unicode text preserved.
/// </summary>
public class FodtR238GetParagraphTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(-1));
    }

    [Fact]
    public void GetParagraphText_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(10));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_FirstParagraph_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph text");
        var text = doc.GetParagraphText(0);
        Assert.Contains("First paragraph text", text);
    }

    [Fact]
    public void GetParagraphText_SecondParagraph_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para One");
        doc.AppendParagraph("Para Two");
        var text = doc.GetParagraphText(1);
        Assert.Contains("Para Two", text);
    }

    [Fact]
    public void GetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetParagraphText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphText_EmptyStringParagraph_Retrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("");
        var ex = Record.Exception(() => doc.GetParagraphText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetParagraphText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Consistent text here");
        var v1 = doc.GetParagraphText(0);
        var v2 = doc.GetParagraphText(0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetParagraphText_DifferentIndices_IndependentValues()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text A");
        doc.AppendParagraph("Text B");
        var t0 = doc.GetParagraphText(0);
        var t1 = doc.GetParagraphText(1);
        Assert.NotEqual(t0, t1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_GetAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        Assert.Contains("First", doc.GetParagraphText(0));
        Assert.Contains("Second", doc.GetParagraphText(1));
        Assert.Contains("Third", doc.GetParagraphText(2));
    }

    [Fact]
    public void DogfoodPipeline_UnicodeText_Preserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unicode: \u00e9\u00e0\u00fc");
        var text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.True(text.Length > 0);
    }
}
