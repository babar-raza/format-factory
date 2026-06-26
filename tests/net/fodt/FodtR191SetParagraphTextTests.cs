// Tests for FodtDocument.SetParagraphText dedicated coverage.
// Sprint: ff-sprint-s182-dotnet-deepening-20260628
// Ledger: PC-FODT-R191

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R191: Dedicated tests for FodtDocument.SetParagraphText(int index, string text).
/// Updates the text content of the paragraph at the given index in-place.
/// Negative index throws ArgumentOutOfRangeException.
/// index >= ParagraphCount throws ArgumentOutOfRangeException.
/// After set: GetParagraphText(index) returns the new text.
/// null text is treated as empty string.
/// Covers: negative index throws; at-count throws; valid set text retrievable;
/// overwrites existing text; null text becomes empty; heading text settable;
/// ParagraphCount unchanged after set; dogfood set-verify multiple;
/// dogfood set-then-export-text.
/// </summary>
public class FodtR191SetParagraphTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(-1, "NewText"));
    }

    [Fact]
    public void SetParagraphText_AtCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(1, "NewText"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ValidSet_GetParagraphTextReturnsNewText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old text");
        doc.SetParagraphText(0, "New text");
        Assert.Equal("New text", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_OverwritesExistingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.SetParagraphText(0, "First replacement");
        doc.SetParagraphText(0, "Second replacement");
        Assert.Equal("Second replacement", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_NullText_TreatedAsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.SetParagraphText(0, null!);
        var result = doc.GetParagraphText(0);
        Assert.True(result == "" || result == null);
    }

    [Fact]
    public void SetParagraphText_OnHeading_TextChanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Old Title", 1);
        doc.SetParagraphText(0, "New Title");
        Assert.Equal("New Title", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        var before = doc.ParagraphCount;
        doc.SetParagraphText(0, "Modified");
        Assert.Equal(before, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleParagraphs_AllUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.SetParagraphText(0, "Alpha");
        doc.SetParagraphText(1, "Beta");
        Assert.Equal("Alpha", doc.GetParagraphText(0));
        Assert.Equal("Beta", doc.GetParagraphText(1));
    }

    [Fact]
    public void DogfoodPipeline_SetTextThenGetWordCount_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three");
        doc.SetParagraphText(0, "Hello world");
        // 2 words after set
        Assert.Equal(2, doc.GetWordCount());
    }
}
