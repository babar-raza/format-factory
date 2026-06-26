// Tests for FodtDocument.GetHeadingText dedicated coverage.
// Sprint: ff-sprint-s228-dotnet-deepening-20260629
// Ledger: PC-FODT-R243

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R243: Dedicated tests for FodtDocument.GetHeadingText(index).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// First heading: returns correct text.
/// Second heading: returns correct text.
/// ParagraphCount unchanged after get.
/// Called twice: same result.
/// Different indices: independent values.
/// Returns non-null string.
/// Dogfood: add mixed content, get headings by index.
/// Dogfood: heading at level 2 retrievable.
/// </summary>
public class FodtR243GetHeadingTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A Heading", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingText(-1));
    }

    [Fact]
    public void GetHeadingText_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A Heading", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingText(10));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingText_FirstHeading_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First Heading", 1);
        var text = doc.GetHeadingText(0);
        Assert.Contains("First Heading", text);
    }

    [Fact]
    public void GetHeadingText_SecondHeading_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Head One", 1);
        doc.AppendHeading("Head Two", 2);
        var text = doc.GetHeadingText(1);
        Assert.Contains("Head Two", text);
    }

    [Fact]
    public void GetHeadingText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading", 1);
        doc.AppendParagraph("Para");
        int before = doc.ParagraphCount;
        doc.GetHeadingText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeadingText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Stable Heading", 1);
        var v1 = doc.GetHeadingText(0);
        var v2 = doc.GetHeadingText(0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetHeadingText_DifferentIndices_IndependentValues()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading A", 1);
        doc.AppendHeading("Heading B", 2);
        var t0 = doc.GetHeadingText(0);
        var t1 = doc.GetHeadingText(1);
        Assert.NotEqual(t0, t1);
    }

    [Fact]
    public void GetHeadingText_ReturnsNonNullString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Non-null heading", 1);
        var text = doc.GetHeadingText(0);
        Assert.NotNull(text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_GetHeadingsByIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Body of chapter 1");
        doc.AppendHeading("Chapter 2", 1);
        doc.AppendParagraph("Body of chapter 2");
        Assert.Contains("Chapter 1", doc.GetHeadingText(0));
        Assert.Contains("Chapter 2", doc.GetHeadingText(1));
    }

    [Fact]
    public void DogfoodPipeline_Level2Heading_Retrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Main Title", 1);
        doc.AppendHeading("Subsection", 2);
        var text = doc.GetHeadingText(1);
        Assert.Contains("Subsection", text);
    }
}
