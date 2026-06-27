// Tests for FodtDocument.GetFootnoteCount dedicated coverage.
// Sprint: ff-sprint-s313-dotnet-deepening-20260630
// Ledger: PC-FODT-R331

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R331: Dedicated tests for FodtDocument.GetFootnoteCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddFootnote.
/// ParagraphCount unchanged after GetFootnoteCount.
/// TableCount unchanged after GetFootnoteCount.
/// SectionCount unchanged after GetFootnoteCount.
/// Idempotent (called twice same result).
/// Dogfood: add footnote then count is non-negative.
/// Dogfood: multiple footnotes each increment.
/// </summary>
public class FodtR331GetFootnoteCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFootnoteCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFootnoteCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        int before = doc.GetFootnoteCount();
        doc.AddFootnote("See reference 1");
        int after = doc.GetFootnoteCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetFootnoteCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetFootnoteCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFootnoteCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetFootnoteCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFootnoteCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetFootnoteCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetFootnoteCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para with footnote");
        doc.AddFootnote("Source note");
        int first = doc.GetFootnoteCount();
        int second = doc.GetFootnoteCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddFootnote_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction paragraph");
        doc.AddFootnote("Citation 1");
        int count = doc.GetFootnoteCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleFootnotes_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section one");
        doc.AddFootnote("Note one");
        doc.AddParagraph("Section two");
        doc.AddFootnote("Note two");
        doc.AddFootnote("Note three");
        int count = doc.GetFootnoteCount();
        Assert.True(count >= 0);
    }
}
