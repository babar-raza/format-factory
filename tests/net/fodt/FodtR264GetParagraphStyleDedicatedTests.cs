// Tests for FodtDocument.GetParagraphStyle dedicated coverage.
// Sprint: ff-sprint-s249-dotnet-deepening-20260630
// Ledger: PC-FODT-R264

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R264: Dedicated tests for FodtDocument.GetParagraphStyle(index).
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid index → returns non-null string.
/// Default style → returns a non-empty string.
/// After SetParagraphStyle → GetParagraphStyle returns that style.
/// ParagraphCount unchanged by GetParagraphStyle.
/// Called twice → same result.
/// Dogfood: set two different styles on two paragraphs, verify independently.
/// Dogfood: set style, get it, verify matches.
/// </summary>
public class FodtR264GetParagraphStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyle_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphStyle(-1));
    }

    [Fact]
    public void GetParagraphStyle_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Para");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphStyle(count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyle_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Some text");
        string style = doc.GetParagraphStyle(0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetParagraphStyle_DefaultStyle_NonEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Default paragraph");
        string style = doc.GetParagraphStyle(0);
        Assert.NotEmpty(style);
    }

    [Fact]
    public void GetParagraphStyle_AfterSetStyle_ReturnsSetStyle()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Paragraph to style");
        doc.SetParagraphStyle(0, "Heading1");
        string style = doc.GetParagraphStyle(0);
        Assert.Equal("Heading1", style);
    }

    [Fact]
    public void GetParagraphStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        int before = doc.ParagraphCount;
        doc.GetParagraphStyle(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphStyle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Consistent");
        string first = doc.GetParagraphStyle(0);
        string second = doc.GetParagraphStyle(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoParagraphsDifferentStyles_IndependentStyles()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Heading text");
        doc.AppendParagraph("Body text");
        doc.SetParagraphStyle(0, "Heading1");
        doc.SetParagraphStyle(1, "Text_Body");
        Assert.Equal("Heading1", doc.GetParagraphStyle(0));
        Assert.Equal("Text_Body", doc.GetParagraphStyle(1));
    }

    [Fact]
    public void DogfoodPipeline_SetStyleGetStyle_Matches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "Quotations");
        string retrieved = doc.GetParagraphStyle(0);
        Assert.Equal("Quotations", retrieved);
    }
}
