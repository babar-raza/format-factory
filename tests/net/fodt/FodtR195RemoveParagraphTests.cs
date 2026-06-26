// Tests for FodtDocument.RemoveParagraph dedicated coverage.
// Sprint: ff-sprint-s186-dotnet-deepening-20260628
// Ledger: PC-FODT-R195

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R195: Dedicated tests for FodtDocument.RemoveParagraph(int index).
/// Removes the paragraph (or heading) at the given index from the document.
/// Negative index throws ArgumentOutOfRangeException.
/// index >= ParagraphCount throws ArgumentOutOfRangeException.
/// Valid removal: ParagraphCount decrements by 1.
/// Remaining paragraphs shift up to fill the gap.
/// Removing a heading decrements ParagraphCount.
/// Covers: negative index throws; at-count throws; valid remove decrements count;
/// remaining items shift up; remove heading counts; remove first item shifts;
/// remove last item; ParagraphCount=0 after removing all;
/// dogfood remove middle paragraph; dogfood remove heading.
/// </summary>
public class FodtR195RemoveParagraphTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(-1));
    }

    [Fact]
    public void RemoveParagraph_AtCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(1));
    }

    [Fact]
    public void RemoveParagraph_EmptyDoc_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_ValidRemove_DecrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        var before = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_RemoveFirst_ShiftsRemainingUp()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.RemoveParagraph(0);
        Assert.Equal("Second", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveParagraph_RemoveLast_OnlyFirstRemains()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep");
        doc.AppendParagraph("Remove");
        doc.RemoveParagraph(1);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Keep", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveParagraph_RemoveHeading_DecrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body");
        doc.RemoveParagraph(0);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_RemoveAll_CountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.RemoveParagraph(1);
        doc.RemoveParagraph(0);
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RemoveMiddle_BoundariesPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Middle");
        doc.AppendParagraph("Last");
        doc.RemoveParagraph(1);
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("First", doc.GetParagraphText(0));
        Assert.Equal("Last", doc.GetParagraphText(1));
    }

    [Fact]
    public void DogfoodPipeline_RemoveHeading_BodyParagraphShiftsToIndex0()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter", 1);
        doc.AppendParagraph("Body");
        doc.RemoveParagraph(0);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("Body", doc.GetParagraphText(0));
    }
}
