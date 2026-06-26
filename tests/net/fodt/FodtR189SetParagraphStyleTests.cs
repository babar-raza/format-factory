// Tests for FodtDocument.SetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s180-dotnet-deepening-20260628
// Ledger: PC-FODT-R189

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R189: Dedicated tests for FodtDocument.SetParagraphStyle(int index, string styleName).
/// Sets the text:style-name attribute on the paragraph at the given index.
/// null styleName throws ArgumentNullException.
/// Negative index throws ArgumentOutOfRangeException.
/// index >= ParagraphCount throws ArgumentOutOfRangeException.
/// Valid set: GetParagraphStyleName(index) returns the set value.
/// Covers: null styleName throws; negative index throws; at-count throws;
/// valid set returns style; overwrites existing style; heading style set;
/// empty string style accepted; style persists after append;
/// dogfood set multiple paragraphs; dogfood AppendParagraph then SetParagraphStyle.
/// </summary>
public class FodtR189SetParagraphStyleTests
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
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(-1, "MyStyle"));
    }

    [Fact]
    public void SetParagraphStyle_AtCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(1, "MyStyle"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_ValidSet_GetParagraphStyleNameReturnsIt()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.SetParagraphStyle(0, "CustomStyle");
        Assert.Equal("CustomStyle", doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void SetParagraphStyle_OverwritesExistingStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.SetParagraphStyle(0, "FirstStyle");
        doc.SetParagraphStyle(0, "SecondStyle");
        Assert.Equal("SecondStyle", doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void SetParagraphStyle_OnHeading_StyleSet()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        doc.SetParagraphStyle(0, "Heading1");
        Assert.Equal("Heading1", doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void SetParagraphStyle_EmptyString_Accepted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.SetParagraphStyle(0, "");
        // Empty string is valid (should not throw); result may be "" or null
        var style = doc.GetParagraphStyleName(0);
        Assert.True(style == "" || style == null);
    }

    [Fact]
    public void SetParagraphStyle_StylePersistsAfterAnotherAppend()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.SetParagraphStyle(0, "Bold");
        doc.AppendParagraph("Second");
        Assert.Equal("Bold", doc.GetParagraphStyleName(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleParagraphStyles_IndependentStyles()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.SetParagraphStyle(0, "StyleA");
        doc.SetParagraphStyle(1, "StyleB");
        Assert.Equal("StyleA", doc.GetParagraphStyleName(0));
        Assert.Equal("StyleB", doc.GetParagraphStyleName(1));
    }

    [Fact]
    public void DogfoodPipeline_AppendThenSetStyle_StyleAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter", 1);
        doc.AppendParagraph("Body text");
        doc.SetParagraphStyle(1, "BodyText");
        Assert.Equal("BodyText", doc.GetParagraphStyleName(1));
    }
}
