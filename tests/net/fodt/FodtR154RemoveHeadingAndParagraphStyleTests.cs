// Tests for FodtDocument.RemoveHeading and FodtDocument.SetParagraphStyle.
// Sprint: ff-sprint-s141-dotnet-deepening-20260627
// Ledger: PC-FODT-R154

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R154: Tests for FodtDocument.RemoveHeading and FodtDocument.SetParagraphStyle.
/// RemoveHeading removes the heading paragraph at the given index; throws if index is out of range
/// or the element at that index is not a heading. SetParagraphStyle sets the style-name attribute
/// on the paragraph element at the given index.
/// Covers: RemoveHeading negative index throws ArgumentOutOfRangeException;
/// RemoveHeading equal-count index throws; RemoveHeading on body paragraph throws InvalidOperationException;
/// RemoveHeading reduces count by 1; RemoveHeading first heading removes it; remaining paragraph intact;
/// SetParagraphStyle null styleName throws ArgumentNullException;
/// SetParagraphStyle negative index throws ArgumentOutOfRangeException;
/// SetParagraphStyle equal-count index throws;
/// dogfood AppendHeading->AppendParagraph->RemoveHeading->SetParagraphStyle pipeline.
/// </summary>
public class FodtR154RemoveHeadingAndParagraphStyleTests
{
    // -------------------------------------------------------------------------
    // RemoveHeading guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(-1));
    }

    [Fact]
    public void RemoveHeading_IndexEqualToParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(doc.ParagraphCount));
    }

    [Fact]
    public void RemoveHeading_OnBodyParagraph_ThrowsInvalidOperationException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text, not a heading.");
        Assert.Throws<InvalidOperationException>(() => doc.RemoveHeading(0));
    }

    // -------------------------------------------------------------------------
    // RemoveHeading functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_ReducesParagraphCountByOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Content.");
        int before = doc.ParagraphCount;
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_RemovesFirstHeading_BodyParagraphRemains()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        doc.AppendParagraph("Body content.");
        doc.RemoveHeading(0);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Body content.", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveHeading_GetHeadingTexts_ReflectsRemoval()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Part A", 1);
        doc.AppendHeading("Part B", 1);
        doc.RemoveHeading(0); // removes "Part A"
        var headings = doc.GetHeadingTexts();
        Assert.Single(headings);
        Assert.Equal("Part B", headings[0]);
    }

    // -------------------------------------------------------------------------
    // SetParagraphStyle guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_NullStyleName_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text.");
        Assert.Throws<ArgumentNullException>(() => doc.SetParagraphStyle(0, null!));
    }

    [Fact]
    public void SetParagraphStyle_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text.");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(-1, "Heading_1"));
    }

    [Fact]
    public void SetParagraphStyle_IndexEqualToParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text.");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphStyle(doc.ParagraphCount, "Heading_1"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendHeading -> AppendParagraph -> RemoveHeading -> SetParagraphStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendRemoveHeading_SetParagraphStyle_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Draft Title", 1);
        doc.AppendParagraph("Section content.");

        // Remove the heading
        doc.RemoveHeading(0);
        Assert.Equal(1, doc.ParagraphCount);

        // Apply a style to the remaining paragraph (should not throw)
        var ex = Record.Exception(() => doc.SetParagraphStyle(0, "Custom_Body_Style"));
        Assert.Null(ex);

        // Paragraph is still accessible
        Assert.Equal("Section content.", doc.Paragraphs[0].Text);
    }
}
