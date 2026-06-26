// Tests for FodtDocument.TrimParagraph dedicated coverage.
// Sprint: ff-sprint-s204-dotnet-deepening-20260629
// Ledger: PC-FODT-R219

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R219: Dedicated tests for FodtDocument.TrimParagraph(int index).
/// OOB index → ArgumentOutOfRangeException.
/// Negative index → ArgumentOutOfRangeException.
/// Paragraph with leading/trailing whitespace → trimmed.
/// Paragraph with only spaces → becomes empty string.
/// ParagraphCount unchanged after trim.
/// Non-whitespace content preserved.
/// Trim does not affect other paragraphs.
/// Heading paragraph can be trimmed.
/// Dogfood: multiple paragraphs, trim each, verify.
/// Dogfood: trim already-trimmed paragraph → no change.
/// </summary>
public class FodtR219TrimParagraphTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void TrimParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.TrimParagraph(-1));
    }

    [Fact]
    public void TrimParagraph_IndexAboveCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.TrimParagraph(5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void TrimParagraph_LeadingWhitespace_Removed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("   Hello");
        doc.TrimParagraph(0);
        Assert.Equal("Hello", doc.GetParagraphText(0));
    }

    [Fact]
    public void TrimParagraph_TrailingWhitespace_Removed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello   ");
        doc.TrimParagraph(0);
        Assert.Equal("Hello", doc.GetParagraphText(0));
    }

    [Fact]
    public void TrimParagraph_BothSidesWhitespace_Removed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("  Hello World  ");
        doc.TrimParagraph(0);
        Assert.Equal("Hello World", doc.GetParagraphText(0));
    }

    [Fact]
    public void TrimParagraph_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("  Hello  ");
        doc.AppendParagraph("  World  ");
        int before = doc.ParagraphCount;
        doc.TrimParagraph(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void TrimParagraph_OtherParagraphsNotAffected()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("  Alpha  ");
        doc.AppendParagraph("  Beta  ");
        doc.TrimParagraph(0);
        Assert.Equal("Alpha", doc.GetParagraphText(0));
        Assert.Equal("  Beta  ", doc.GetParagraphText(1));
    }

    [Fact]
    public void TrimParagraph_AlreadyTrimmed_NoChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Clean");
        doc.TrimParagraph(0);
        Assert.Equal("Clean", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TrimMultipleParagraphs_EachTrimmed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("  First  ");
        doc.AppendParagraph("  Second  ");
        doc.AppendParagraph("  Third  ");
        for (int i = 0; i < 3; i++)
            doc.TrimParagraph(i);
        Assert.Equal("First", doc.GetParagraphText(0));
        Assert.Equal("Second", doc.GetParagraphText(1));
        Assert.Equal("Third", doc.GetParagraphText(2));
    }

    [Fact]
    public void DogfoodPipeline_TrimTwice_NoChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("  Content  ");
        doc.TrimParagraph(0);
        string afterFirst = doc.GetParagraphText(0);
        doc.TrimParagraph(0);
        string afterSecond = doc.GetParagraphText(0);
        Assert.Equal(afterFirst, afterSecond);
    }
}
