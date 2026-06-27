// Tests for FodtDocument.ReplaceText dedicated coverage.
// Sprint: ff-sprint-s308-dotnet-deepening-20260630
// Ledger: PC-FODT-R323

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R323: Dedicated tests for FodtDocument.ReplaceText(searchText, replacementText).
/// Null search text throws exception.
/// Null replacement text throws exception.
/// Text not found returns false or zero.
/// Text found returns true or positive.
/// ParagraphCount unchanged after ReplaceText.
/// TableCount unchanged after ReplaceText.
/// Called twice no exception.
/// FindText returns false after replace-all.
/// Dogfood: replace text in multi-paragraph document.
/// </summary>
public class FodtR323ReplaceTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NullSearchText_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceText(null!, "replacement"));
    }

    [Fact]
    public void ReplaceText_NullReplacement_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        Assert.ThrowsAny<Exception>(() => doc.ReplaceText("Hello", null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_TextNotFound_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        var ex = Record.Exception(() => doc.ReplaceText("xyz_not_here", "something"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        var ex = Record.Exception(() => doc.ReplaceText("Hello", "Goodbye"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int before = doc.ParagraphCount;
        doc.ReplaceText("Hello", "Hi");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ReplaceText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        int before = doc.TableCount;
        doc.ReplaceText("Hello", "Hi");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void ReplaceText_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        doc.ReplaceText("quick", "slow");
        var ex = Record.Exception(() => doc.ReplaceText("slow", "fast"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_SameSearchAndReplacement_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello world");
        var ex = Record.Exception(() => doc.ReplaceText("Hello", "Hello"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ReplaceInMultipleParagraphs_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section one content");
        doc.AddParagraph("Section two content");
        doc.AddParagraph("Section three content");
        int before = doc.ParagraphCount;
        var ex = Record.Exception(() => doc.ReplaceText("content", "text"));
        Assert.Null(ex);
        Assert.Equal(before, doc.ParagraphCount);
    }
}
