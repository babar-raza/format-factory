// Tests for FodtDocument.GetParagraphText dedicated coverage.
// Sprint: ff-sprint-s337-dotnet-deepening-20260630
// Ledger: PC-FODT-R355

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R355: Dedicated tests for FodtDocument.GetParagraphText().
/// Negative index throws.
/// Out-of-range index throws.
/// Returns non-null for valid index.
/// ParagraphCount unchanged after GetParagraphText.
/// TableCount unchanged after GetParagraphText.
/// SectionCount unchanged after GetParagraphText.
/// Idempotent (called twice same result).
/// After AddParagraph returns correct text.
/// Dogfood: multiple paragraphs each returns correct text.
/// </summary>
public class FodtR355GetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(-1));
    }

    [Fact]
    public void GetParagraphText_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Only one paragraph");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(5));
    }

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test paragraph content");
        string? text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.TableCount;
        _ = doc.GetParagraphText(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphText_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.SectionCount;
        _ = doc.GetParagraphText(0);
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetParagraphText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph text");
        string? first = doc.GetParagraphText(0);
        string? second = doc.GetParagraphText(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphText_AfterAddParagraph_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox jumps over the lazy dog");
        string? text = doc.GetParagraphText(0);
        Assert.NotNull(text);
        Assert.Equal("The quick brown fox jumps over the lazy dog", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph content");
        doc.AddParagraph("Second paragraph content");
        doc.AddParagraph("Third paragraph content");
        Assert.Equal("First paragraph content", doc.GetParagraphText(0));
        Assert.Equal("Second paragraph content", doc.GetParagraphText(1));
        Assert.Equal("Third paragraph content", doc.GetParagraphText(2));
    }
}
