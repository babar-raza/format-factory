// Tests for FodtDocument.ClearParagraph dedicated coverage.
// Sprint: ff-sprint-s251-dotnet-deepening-20260630
// Ledger: PC-FODT-R266

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R266: Dedicated tests for FodtDocument.ClearParagraph(index).
/// ClearParagraph erases the text content of a paragraph without removing the paragraph.
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid index → no exception.
/// ParagraphCount unchanged (paragraph kept, just empty).
/// Paragraph text empty or whitespace after clear.
/// Other paragraphs unaffected.
/// Called twice → same result (idempotent on already-clear paragraph).
/// Dogfood: add text, clear, verify empty.
/// Dogfood: clear middle paragraph, verify neighbors unchanged.
/// </summary>
public class FodtR266ClearParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearParagraph_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Content");
        Assert.ThrowsAny<Exception>(() => doc.ClearParagraph(-1));
    }

    [Fact]
    public void ClearParagraph_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Content");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.ClearParagraph(count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearParagraph_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Some text to clear");
        var ex = Record.Exception(() => doc.ClearParagraph(0));
        Assert.Null(ex);
    }

    [Fact]
    public void ClearParagraph_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        int before = doc.ParagraphCount;
        doc.ClearParagraph(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ClearParagraph_TextEmptyOrWhitespaceAfterClear()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Lots of content here");
        doc.ClearParagraph(0);
        string text = doc.GetParagraphText(0);
        Assert.True(text == null || text.Trim().Length == 0);
    }

    [Fact]
    public void ClearParagraph_OtherParagraphsUnaffected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Keep this text");
        doc.AppendParagraph("Clear this text");
        doc.ClearParagraph(1);
        // First paragraph should be untouched
        string firstText = doc.GetParagraphText(0);
        Assert.Contains("Keep this text", firstText);
    }

    [Fact]
    public void ClearParagraph_CalledTwice_StillNoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Twice cleared");
        doc.ClearParagraph(0);
        var ex = Record.Exception(() => doc.ClearParagraph(0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTextClearVerifyEmpty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("This is the paragraph content before clearing.");
        // Verify text exists before clear
        string beforeClear = doc.GetParagraphText(0);
        Assert.NotNull(beforeClear);
        // Clear and verify
        doc.ClearParagraph(0);
        string afterClear = doc.GetParagraphText(0);
        Assert.True(afterClear == null || afterClear.Trim().Length == 0);
    }

    [Fact]
    public void DogfoodPipeline_ClearMiddle_VerifyNeighborsUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First stays");
        doc.AppendParagraph("Middle gets cleared");
        doc.AppendParagraph("Last stays");
        doc.ClearParagraph(1);
        Assert.Contains("First stays", doc.GetParagraphText(0));
        Assert.Contains("Last stays", doc.GetParagraphText(2));
        Assert.Equal(3, doc.ParagraphCount);
    }
}
