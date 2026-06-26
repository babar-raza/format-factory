// Tests for FodtDocument.RemoveAllParagraphs dedicated coverage.
// Sprint: ff-sprint-s192-dotnet-deepening-20260629
// Ledger: PC-FODT-R204

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R204: Dedicated tests for FodtDocument.RemoveAllParagraphs().
/// Removes all body paragraphs and headings from the document.
/// After call, ParagraphCount == 0.
/// Calling on empty document is safe (no exception).
/// Removes headings as well as body paragraphs.
/// Does not throw on any valid document.
/// After removal, AppendParagraph still works.
/// After removal, ParagraphCount is 0 regardless of how many were there.
/// Covers: empty doc no-op; single paragraph removed; heading removed;
/// multiple paragraphs all removed; count is 0 after; no exception thrown;
/// append after remove works; dogfood remove then re-add restores count;
/// dogfood mixed content all removed.
/// </summary>
public class FodtR204RemoveAllParagraphsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_EmptyDocument_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.RemoveAllParagraphs());
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveAllParagraphs_EmptyDocument_CountRemainsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_SingleParagraph_CountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_Heading_CountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_MultipleParagraphs_AllRemoved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveAllParagraphs_AfterRemoval_AppendParagraphWorks()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("New");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("New", doc.GetParagraphText(0));
    }

    [Fact]
    public void RemoveAllParagraphs_CalledTwice_StillZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.RemoveAllParagraphs();
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RemoveThenReAdd_CountRestored()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
        doc.AppendParagraph("X");
        doc.AppendParagraph("Y");
        Assert.Equal(2, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MixedContent_AllRemoved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body 1");
        doc.AppendHeading("Heading", 1);
        doc.AppendParagraph("Body 2");
        doc.AppendHeading("Sub", 2);
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }
}
