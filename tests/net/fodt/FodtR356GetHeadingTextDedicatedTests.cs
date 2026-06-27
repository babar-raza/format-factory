// Tests for FodtDocument.GetHeadingText dedicated coverage.
// Sprint: ff-sprint-s338-dotnet-deepening-20260630
// Ledger: PC-FODT-R356

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R356: Dedicated tests for FodtDocument.GetHeadingText().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document with no headings: index 0 throws.
/// Returns non-null for valid index.
/// ParagraphCount unchanged after GetHeadingText.
/// TableCount unchanged after GetHeadingText.
/// Idempotent (called twice same result).
/// After AddHeading returns correct text.
/// Dogfood: multiple headings each returns correct text.
/// </summary>
public class FodtR356GetHeadingTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingText_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Introduction", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingText(-1));
    }

    [Fact]
    public void GetHeadingText_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Introduction", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingText(10));
    }

    [Fact]
    public void GetHeadingText_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingText(0));
    }

    [Fact]
    public void GetHeadingText_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Executive Summary", 1);
        string? text = doc.GetHeadingText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetHeadingText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Overview", 1);
        doc.AddParagraph("Body paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetHeadingText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeadingText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Overview", 1);
        int before = doc.TableCount;
        _ = doc.GetHeadingText(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetHeadingText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Stable Heading", 2);
        string? first = doc.GetHeadingText(0);
        string? second = doc.GetHeadingText(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHeadingText_AfterAddHeading_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Annual Revenue Report", 1);
        string? text = doc.GetHeadingText(0);
        Assert.NotNull(text);
        Assert.Equal("Annual Revenue Report", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleHeadings_EachReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Chapter One", 1);
        doc.AddHeading("Section 1.1", 2);
        doc.AddHeading("Chapter Two", 1);
        Assert.Equal("Chapter One", doc.GetHeadingText(0));
        Assert.Equal("Section 1.1", doc.GetHeadingText(1));
        Assert.Equal("Chapter Two", doc.GetHeadingText(2));
    }
}
