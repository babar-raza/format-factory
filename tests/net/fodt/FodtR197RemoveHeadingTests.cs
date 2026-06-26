// Tests for FodtDocument.RemoveHeading dedicated coverage.
// Sprint: ff-sprint-s188-dotnet-deepening-20260628
// Ledger: PC-FODT-R197

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R197: Dedicated tests for FodtDocument.RemoveHeading(int index).
/// Removes the element at the given index only if it is a heading (text:h).
/// Negative index throws ArgumentOutOfRangeException.
/// index >= ParagraphCount throws ArgumentOutOfRangeException.
/// Non-heading at index throws InvalidOperationException.
/// Valid removal: ParagraphCount decrements by 1.
/// Remaining paragraphs shift up.
/// GetHeadingParagraphs count decrements.
/// Covers: negative index throws; at-count throws; body-para at index throws;
/// valid heading removed; ParagraphCount decrements; remaining shifts up;
/// GetHeadingParagraphs count decrements; remove first heading shifts;
/// dogfood remove single heading; dogfood heading text gone after remove.
/// </summary>
public class FodtR197RemoveHeadingTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(-1));
    }

    [Fact]
    public void RemoveHeading_AtCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveHeading(1));
    }

    [Fact]
    public void RemoveHeading_BodyParagraphAtIndex_ThrowsInvalidOperationException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        Assert.Throws<InvalidOperationException>(() => doc.RemoveHeading(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveHeading_ValidHeading_DecrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 2);
        var before = doc.ParagraphCount;
        doc.RemoveHeading(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveHeading_ValidHeading_RemainingShiftsUp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First Heading", 1);
        doc.AppendHeading("Second Heading", 2);
        doc.RemoveHeading(0);
        Assert.Equal("Second Heading", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveHeading_ValidHeading_HeadingParagraphsDecrements()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 2);
        doc.RemoveHeading(0);
        Assert.Equal(1, doc.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void RemoveHeading_RemoveOnlyHeading_ParagraphCountZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Solo", 1);
        doc.RemoveHeading(0);
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RemoveSingleHeading_DocEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("To Remove", 1);
        doc.RemoveHeading(0);
        Assert.Equal(0, doc.ParagraphCount);
        Assert.Empty(doc.GetHeadingParagraphs());
    }

    [Fact]
    public void DogfoodPipeline_HeadingTextGoneAfterRemove()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Disappear", 1);
        doc.AppendParagraph("Body");
        doc.RemoveHeading(0);
        // heading at index 0 is gone; body paragraph shifts to 0
        Assert.Equal("Body", doc.GetParagraphText(0));
    }
}
