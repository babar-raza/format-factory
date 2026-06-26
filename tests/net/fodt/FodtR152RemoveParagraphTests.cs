// Tests for FodtDocument.RemoveParagraph(int index).
// Sprint: ff-sprint-s139-dotnet-deepening-20260627
// Ledger: PC-FODT-R152

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R152: Tests for FodtDocument.RemoveParagraph(int index).
/// Removes the paragraph at the given index, shifting subsequent paragraphs up.
/// Throws ArgumentOutOfRangeException for out-of-range indices.
/// Covers: negative index throws; index=ParagraphCount throws; index beyond count throws;
/// removes correct paragraph (ParagraphCount decreases by 1); first paragraph removed correctly;
/// last paragraph removed correctly; middle paragraph removed correctly;
/// remaining paragraphs shift correctly; empty doc throws on index 0;
/// dogfood AppendParagraphs×4->RemoveParagraph(1)->verify remaining texts pipeline.
/// </summary>
public class FodtR152RemoveParagraphTests
{
    // -------------------------------------------------------------------------
    // Guard checks
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(-1));
    }

    [Fact]
    public void RemoveParagraph_IndexEqualCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(1));
    }

    [Fact]
    public void RemoveParagraph_LargeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(99));
    }

    [Fact]
    public void RemoveParagraph_EmptyDoc_IndexZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(0));
    }

    // -------------------------------------------------------------------------
    // Correct removal
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_DecreasesParagraphCountByOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.RemoveParagraph(0);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_FirstParagraph_RemainingIsSecond()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.RemoveParagraph(0);
        Assert.Equal("Second", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveParagraph_LastParagraph_RemainingIsFirst()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Last");
        doc.RemoveParagraph(1);
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("First", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void RemoveParagraph_MiddleParagraph_OthersTwoRemain()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        doc.RemoveParagraph(1);  // Remove "B"
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("A", doc.Paragraphs[0].Text);
        Assert.Equal("C", doc.Paragraphs[1].Text);
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraphs×4 -> RemoveParagraph(1) -> verify remaining
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourParagraphs_RemoveIndex1_VerifyRemainingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");    // This will be removed
        doc.AppendParagraph("Gamma");
        doc.AppendParagraph("Delta");

        doc.RemoveParagraph(1);  // Remove "Beta"

        Assert.Equal(3, doc.ParagraphCount);
        Assert.Equal("Alpha", doc.Paragraphs[0].Text);
        Assert.Equal("Gamma", doc.Paragraphs[1].Text);
        Assert.Equal("Delta", doc.Paragraphs[2].Text);

        var plainText = doc.GetPlainText();
        Assert.DoesNotContain("Beta", plainText);
        Assert.Contains("Alpha", plainText);
        Assert.Contains("Gamma", plainText);
        Assert.Contains("Delta", plainText);
    }
}
