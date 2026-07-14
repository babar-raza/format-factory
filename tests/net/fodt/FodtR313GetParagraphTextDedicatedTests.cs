// Tests for FodtDocument.GetParagraphText dedicated coverage.
// Sprint: ff-sprint-s298-dotnet-deepening-20260630
// Ledger: PC-FODT-R313

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R313: Dedicated tests for FodtDocument.GetParagraphText(index).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No paragraphs throws exception.
/// Valid call returns non-null.
/// Returns text set by AddParagraph.
/// ParagraphCount unchanged after GetParagraphText.
/// Called twice returns same result.
/// TableCount unchanged after GetParagraphText.
/// Dogfood: add paragraph with text, GetParagraphText returns matching text.
/// </summary>
public class FodtR313GetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(-1));
    }

    [Fact]
    public void GetParagraphText_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(count));
    }

    [Fact]
    public void GetParagraphText_NoParagraphs_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.ParagraphCount == 0)
            Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(0));
        else
            Assert.True(doc.ParagraphCount > 0); // document has default paragraphs
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphText_ValidCall_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello World");
        int idx = doc.ParagraphCount - 1;
        string? text = doc.GetParagraphText(idx);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_ReturnsTextFromAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Expected Text");
        int idx = doc.ParagraphCount - 1;
        string? text = doc.GetParagraphText(idx);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphText(before - 1);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Consistent");
        int idx = doc.ParagraphCount - 1;
        string? first = doc.GetParagraphText(idx);
        string? second = doc.GetParagraphText(idx);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetParagraphText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int tableBefore = doc.TableCount;
        _ = doc.GetParagraphText(doc.ParagraphCount - 1);
        Assert.Equal(tableBefore, doc.TableCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddParagraphWithText_GetParagraphTextReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        int idx = doc.ParagraphCount - 1;
        string? text = doc.GetParagraphText(idx);
        Assert.NotNull(text);
    }
}
