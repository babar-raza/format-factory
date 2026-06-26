// Tests for FodtDocument.RemoveParagraph dedicated coverage.
// Sprint: ff-sprint-s246-dotnet-deepening-20260630
// Ledger: PC-FODT-R261

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R261: Dedicated tests for FodtDocument.RemoveParagraph(index).
/// Negative index → throws exception.
/// Out-of-bounds index → throws exception.
/// Valid removal → no exception.
/// ParagraphCount decreases after removal.
/// Remaining paragraphs still accessible.
/// Remove first paragraph shifts remaining.
/// Remove last paragraph.
/// Dogfood: add 3 paragraphs, remove middle, verify count=2 and texts.
/// Dogfood: add and remove multiple paragraphs verify count tracks.
/// </summary>
public class FodtR261RemoveParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Para one");
        Assert.ThrowsAny<Exception>(() => doc.RemoveParagraph(-1));
    }

    [Fact]
    public void RemoveParagraph_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Only paragraph");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.RemoveParagraph(count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraph_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        var ex = Record.Exception(() => doc.RemoveParagraph(0));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveParagraph_ParagraphCountDecreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        int before = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        Assert.True(doc.ParagraphCount < before);
    }

    [Fact]
    public void RemoveParagraph_RemainingParagraphsAccessible()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Keep this");
        doc.AppendParagraph("Remove this");
        doc.RemoveParagraph(1);
        // Remaining paragraph should still be accessible
        string text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void RemoveParagraph_RemoveFirst_ShiftsRemaining()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.RemoveParagraph(0);
        // After removing index 0, "Second" becomes index 0
        string text = doc.GetParagraphText(0);
        Assert.Contains("Second", text);
    }

    [Fact]
    public void RemoveParagraph_RemoveLast_CountDecreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.RemoveParagraph(before - 1);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThree_RemoveMiddle_VerifyCountAndTexts()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("Chapter One");
        doc.AppendParagraph("Chapter Two");
        doc.AppendParagraph("Chapter Three");
        // Remove middle paragraph (index 1)
        doc.RemoveParagraph(1);
        Assert.Equal(2, doc.ParagraphCount);
        // First paragraph should still be "Chapter One"
        Assert.Contains("Chapter One", doc.GetParagraphText(0));
        // Second paragraph should now be "Chapter Three"
        Assert.Contains("Chapter Three", doc.GetParagraphText(1));
    }

    [Fact]
    public void DogfoodPipeline_AddAndRemoveMultiple_CountTracks()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("P3");
        doc.AppendParagraph("P4");
        int afterAdd = doc.ParagraphCount;
        doc.RemoveParagraph(0);
        doc.RemoveParagraph(0);
        Assert.Equal(afterAdd - 2, doc.ParagraphCount);
    }
}
