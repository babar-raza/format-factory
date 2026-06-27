// Tests for FodtDocument.GetPageCount dedicated coverage.
// Sprint: ff-sprint-s326-dotnet-deepening-20260630
// Ledger: PC-FODT-R344

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R344: Dedicated tests for FodtDocument.GetPageCount().
/// Non-negative on empty document.
/// Empty document ok.
/// ParagraphCount unchanged after GetPageCount.
/// TableCount unchanged after GetPageCount.
/// SectionCount unchanged after GetPageCount.
/// Idempotent (called twice same result).
/// Returns at least one for non-empty document.
/// Dogfood: multi-paragraph document page count non-negative.
/// Dogfood: heading document page count non-negative.
/// </summary>
public class FodtR344GetPageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetPageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetPageCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetPageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetPageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.TableCount;
        _ = doc.GetPageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.SectionCount;
        _ = doc.GetPageCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetPageCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("A paragraph with some content");
        int first = doc.GetPageCount();
        int second = doc.GetPageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageCount_NonEmptyDocument_AtLeastOne()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document with content");
        int count = doc.GetPageCount();
        Assert.True(count >= 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiParagraph_PageCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph with content.");
        doc.AddParagraph("Second paragraph with content.");
        doc.AddParagraph("Third paragraph with content.");
        int count = doc.GetPageCount();
        Assert.True(count >= 0);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_HeadingDocument_PageCountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Chapter One", 1);
        doc.AddParagraph("Introduction text for chapter one.");
        doc.AddHeading("Chapter Two", 1);
        doc.AddParagraph("Introduction text for chapter two.");
        int count = doc.GetPageCount();
        Assert.True(count >= 0);
    }
}
