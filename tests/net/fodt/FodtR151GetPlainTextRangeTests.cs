// Tests for FodtDocument.GetPlainTextRange(startIndex, endIndex).
// Sprint: ff-sprint-s137-dotnet-deepening-20260627
// Ledger: PC-FODT-R151

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R151: Tests for FodtDocument.GetPlainTextRange(int startIndex, int endIndex).
/// Returns the plain text of paragraphs [startIndex, endIndex) joined by newline.
/// startIndex>=endIndex returns empty string. startIndex&lt;0 throws ArgumentOutOfRangeException.
/// endIndex>ParagraphCount throws ArgumentOutOfRangeException.
/// Covers: negative startIndex throws; endIndex > count throws; startIndex=endIndex=empty;
/// startIndex > endIndex=empty; single paragraph range; two-paragraph range newline-joined;
/// full range equals GetPlainText(); range excludes paragraphs outside bounds;
/// first paragraph range; dogfood AppendParagraphs×4->GetPlainTextRange verifies subranges.
/// </summary>
public class FodtR151GetPlainTextRangeTests
{
    private static FodtDocument FourParagraphDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        doc.AppendParagraph("Delta");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard checks
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_NegativeStartIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FourParagraphDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(-1, 2));
    }

    [Fact]
    public void GetPlainTextRange_EndIndexBeyondParagraphCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FourParagraphDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(0, 99));
    }

    // -------------------------------------------------------------------------
    // Empty result cases
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_StartEqualEnd_ReturnsEmpty()
    {
        var doc = FourParagraphDoc();
        Assert.Equal(string.Empty, doc.GetPlainTextRange(1, 1));
    }

    [Fact]
    public void GetPlainTextRange_StartGreaterThanEnd_ReturnsEmpty()
    {
        var doc = FourParagraphDoc();
        Assert.Equal(string.Empty, doc.GetPlainTextRange(3, 2));
    }

    // -------------------------------------------------------------------------
    // Single and multi-paragraph ranges
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_SingleParagraph_ReturnsJustThatText()
    {
        var doc = FourParagraphDoc();
        var result = doc.GetPlainTextRange(0, 1);
        Assert.Equal("Alpha", result);
    }

    [Fact]
    public void GetPlainTextRange_TwoParagraphs_JoinedByNewline()
    {
        var doc = FourParagraphDoc();
        var result = doc.GetPlainTextRange(1, 3);
        Assert.Equal("Beta\nGamma", result);
    }

    [Fact]
    public void GetPlainTextRange_FullRange_EqualsGetPlainText()
    {
        var doc = FourParagraphDoc();
        var rangeResult = doc.GetPlainTextRange(0, 4);
        var plainText = doc.GetPlainText();
        Assert.Equal(plainText, rangeResult);
    }

    [Fact]
    public void GetPlainTextRange_LastParagraph_ReturnsDelta()
    {
        var doc = FourParagraphDoc();
        var result = doc.GetPlainTextRange(3, 4);
        Assert.Equal("Delta", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraphs×4 -> verify sub-range slices
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourParagraphs_MiddleRange_ContainsOnlyMiddle()
    {
        var doc = FourParagraphDoc();

        // Range [1, 3) = "Beta\nGamma"
        var middle = doc.GetPlainTextRange(1, 3);
        Assert.Contains("Beta", middle);
        Assert.Contains("Gamma", middle);
        Assert.DoesNotContain("Alpha", middle);
        Assert.DoesNotContain("Delta", middle);
    }
}
