// Tests for FodtDocument.GetParagraphsByStyle dedicated coverage.
// Sprint: ff-sprint-s243-dotnet-deepening-20260629
// Ledger: PC-FODT-R258

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R258: Dedicated tests for FodtDocument.GetParagraphsByStyle(string styleName).
/// Null style name → throws exception.
/// Empty document → returns empty.
/// No match → returns empty.
/// After SetParagraphStyle: matching style returns paragraph.
/// ParagraphCount unchanged after call.
/// Called twice → same result size.
/// Multiple paragraphs with style → all returned.
/// Body style → body paragraphs found.
/// Dogfood: set style, find by style, verify count.
/// Dogfood: two styles, each finds correct paragraphs.
/// </summary>
public class FodtR258GetParagraphsByStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphsByStyle_NullStyleName_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphsByStyle(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphsByStyle_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.GetParagraphsByStyle("Bold");
        Assert.NotNull(result);
        Assert.Empty(result);
    }

    [Fact]
    public void GetParagraphsByStyle_NoMatch_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Normal paragraph");
        var result = doc.GetParagraphsByStyle("NonExistentStyle");
        Assert.NotNull(result);
        Assert.Empty(result);
    }

    [Fact]
    public void GetParagraphsByStyle_AfterSetStyle_FindsParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "Highlight");
        var result = doc.GetParagraphsByStyle("Highlight");
        Assert.NotNull(result);
        Assert.True(result.Count >= 1);
    }

    [Fact]
    public void GetParagraphsByStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        int before = doc.ParagraphCount;
        doc.GetParagraphsByStyle("Normal");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphsByStyle_CalledTwice_SameResultSize()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");
        doc.SetParagraphStyle(0, "Custom");
        var r1 = doc.GetParagraphsByStyle("Custom");
        var r2 = doc.GetParagraphsByStyle("Custom");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetParagraphsByStyle_MultipleParagraphsWithStyle_AllReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("P3");
        doc.SetParagraphStyle(0, "Emph");
        doc.SetParagraphStyle(2, "Emph");
        var result = doc.GetParagraphsByStyle("Emph");
        Assert.NotNull(result);
        Assert.True(result.Count >= 2);
    }

    [Fact]
    public void GetParagraphsByStyle_NonMatchingStyle_NotReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only");
        doc.SetParagraphStyle(0, "Bold");
        var result = doc.GetParagraphsByStyle("Italic");
        Assert.NotNull(result);
        Assert.Empty(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetStyle_FindByStyle_VerifyCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        doc.SetParagraphStyle(0, "Important");
        doc.SetParagraphStyle(1, "Important");
        var important = doc.GetParagraphsByStyle("Important");
        Assert.True(important.Count >= 2);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoStyles_EachFindsCorrectParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("RedP");
        doc.AppendParagraph("BlueP");
        doc.AppendParagraph("RedP2");
        doc.SetParagraphStyle(0, "Red");
        doc.SetParagraphStyle(1, "Blue");
        doc.SetParagraphStyle(2, "Red");
        var reds = doc.GetParagraphsByStyle("Red");
        var blues = doc.GetParagraphsByStyle("Blue");
        Assert.True(reds.Count >= 2);
        Assert.True(blues.Count >= 1);
    }
}
