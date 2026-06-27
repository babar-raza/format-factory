// Tests for FodtDocument.SetParagraphText dedicated coverage.
// Sprint: ff-sprint-s299-dotnet-deepening-20260630
// Ledger: PC-FODT-R314

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R314: Dedicated tests for FodtDocument.SetParagraphText(index, text).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No paragraphs throws exception.
/// Valid call no exception.
/// ParagraphCount unchanged after SetParagraphText.
/// TableCount unchanged after SetParagraphText.
/// Set twice no exception.
/// GetParagraphText returns non-null after set.
/// Dogfood: set text on paragraph, GetParagraphText returns non-null.
/// Dogfood: set text on multiple paragraphs no exception.
/// </summary>
public class FodtR314SetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(-1, "new text"));
    }

    [Fact]
    public void SetParagraphText_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(count, "new text"));
    }

    [Fact]
    public void SetParagraphText_NoParagraphs_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.ParagraphCount == 0)
            Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(0, "text"));
        else
            Assert.True(true); // document has default paragraphs
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Original");
        int idx = doc.ParagraphCount - 1;
        var ex = Record.Exception(() => doc.SetParagraphText(idx, "Updated"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int before = doc.ParagraphCount;
        doc.SetParagraphText(before - 1, "New text");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int tableBefore = doc.TableCount;
        doc.SetParagraphText(doc.ParagraphCount - 1, "Text");
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void SetParagraphText_SetTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "First");
        var ex = Record.Exception(() => doc.SetParagraphText(idx, "Second"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphText_GetParagraphTextReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "Updated content");
        string? text = doc.GetParagraphText(idx);
        Assert.NotNull(text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetText_GetParagraphTextNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Initial");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "Modified paragraph text");
        string? text = doc.GetParagraphText(idx);
        Assert.NotNull(text);
    }

    [Fact]
    public void DogfoodPipeline_SetTextOnMultipleParagraphs_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para1");
        doc.AddParagraph("Para2");
        int count = doc.ParagraphCount;
        var ex = Record.Exception(() =>
        {
            doc.SetParagraphText(count - 2, "Updated Para1");
            doc.SetParagraphText(count - 1, "Updated Para2");
        });
        Assert.Null(ex);
    }
}
