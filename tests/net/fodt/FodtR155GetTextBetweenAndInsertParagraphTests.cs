// Tests for FodtDocument.GetTextBetweenParagraphs and InsertParagraph.
// Sprint: ff-sprint-s143-dotnet-deepening-20260627
// Ledger: PC-FODT-R155

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R155: Tests for FodtDocument.GetTextBetweenParagraphs and FodtDocument.InsertParagraph.
/// GetTextBetweenParagraphs returns null for invalid range (negative start, start>=end, end>count).
/// InsertParagraph inserts a new paragraph at the given index; at count it acts as append.
/// Covers: GetTextBetweenParagraphs negative startIndex returns null; startIndex>=endIndex returns null;
/// endIndex>count returns null; valid range returns joined text; single range returns single paragraph;
/// InsertParagraph negative index throws; index>count throws; index=0 inserts before first;
/// index=count acts as append; dogfood Append×3->InsertParagraph->GetTextBetweenParagraphs pipeline.
/// </summary>
public class FodtR155GetTextBetweenAndInsertParagraphTests
{
    private static FodtDocument ThreeParagraphDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs guard tests (returns null on invalid)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NegativeStart_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        Assert.Null(doc.GetTextBetweenParagraphs(-1, 2));
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartEqualToEnd_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        Assert.Null(doc.GetTextBetweenParagraphs(1, 1));
    }

    [Fact]
    public void GetTextBetweenParagraphs_StartGreaterThanEnd_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        Assert.Null(doc.GetTextBetweenParagraphs(2, 1));
    }

    [Fact]
    public void GetTextBetweenParagraphs_EndBeyondCount_ReturnsNull()
    {
        var doc = ThreeParagraphDoc();
        Assert.Null(doc.GetTextBetweenParagraphs(0, 99));
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_SingleRange_ReturnsSingleText()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(1, 2); // ["Beta"]
        Assert.Equal("Beta", result);
    }

    [Fact]
    public void GetTextBetweenParagraphs_TwoParas_JoinedByNewline()
    {
        var doc = ThreeParagraphDoc();
        var result = doc.GetTextBetweenParagraphs(0, 2); // ["Alpha", "Beta"]
        Assert.Equal("Alpha\nBeta", result);
    }

    // -------------------------------------------------------------------------
    // InsertParagraph guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = ThreeParagraphDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(-1, "New"));
    }

    [Fact]
    public void InsertParagraph_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = ThreeParagraphDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(99, "New"));
    }

    // -------------------------------------------------------------------------
    // InsertParagraph functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_IndexZero_InsertsBeforeFirst()
    {
        var doc = ThreeParagraphDoc();
        doc.InsertParagraph(0, "Intro");
        Assert.Equal("Intro", doc.Paragraphs[0].Text);
        Assert.Equal("Alpha", doc.Paragraphs[1].Text);
    }

    [Fact]
    public void InsertParagraph_IndexEqualToCount_ActsAsAppend()
    {
        var doc = ThreeParagraphDoc();
        doc.InsertParagraph(doc.ParagraphCount, "Epilog");
        Assert.Equal("Epilog", doc.Paragraphs[doc.ParagraphCount - 1].Text);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Append×3 -> InsertParagraph -> GetTextBetweenParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertParagraph_GetTextBetween_ContainsInserted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Third");
        doc.InsertParagraph(1, "Second"); // insert between First and Third

        Assert.Equal(3, doc.ParagraphCount);
        Assert.Equal("First", doc.Paragraphs[0].Text);
        Assert.Equal("Second", doc.Paragraphs[1].Text);
        Assert.Equal("Third", doc.Paragraphs[2].Text);

        var between = doc.GetTextBetweenParagraphs(0, 3);
        Assert.Equal("First\nSecond\nThird", between);
    }
}
