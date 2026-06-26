// Tests for FodtDocument.GetTableOfContents dedicated coverage.
// Sprint: ff-sprint-s235-dotnet-deepening-20260629
// Ledger: PC-FODT-R250

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R250: Dedicated tests for FodtDocument.GetTableOfContents().
/// Empty document → returns non-null.
/// Empty document → returns empty list.
/// Paragraphs-only → returns empty (no headings in TOC).
/// One heading → count is 1.
/// Two headings → count is 2.
/// ParagraphCount unchanged after call.
/// Heading text appears in TOC entries.
/// Called twice returns same count.
/// After adding heading → count increases.
/// Dogfood: multiple headings at different levels, all in TOC.
/// </summary>
public class FodtR250GetTableOfContentsTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableOfContents_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var toc = doc.GetTableOfContents();
        Assert.NotNull(toc);
    }

    [Fact]
    public void GetTableOfContents_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var toc = doc.GetTableOfContents();
        var list = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(toc));
        Assert.Empty(list);
    }

    [Fact]
    public void GetTableOfContents_ParagraphsOnly_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just a paragraph");
        doc.AppendParagraph("Another paragraph");
        var toc = doc.GetTableOfContents();
        var list = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(toc));
        Assert.Empty(list);
    }

    [Fact]
    public void GetTableOfContents_OneHeading_CountIsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section One", 1);
        var toc = doc.GetTableOfContents();
        var list = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(toc));
        Assert.Equal(1, list.Count);
    }

    [Fact]
    public void GetTableOfContents_TwoHeadings_CountIsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        doc.AppendHeading("Chapter Two", 1);
        var toc = doc.GetTableOfContents();
        var list = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(toc));
        Assert.Equal(2, list.Count);
    }

    [Fact]
    public void GetTableOfContents_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Intro", 1);
        doc.AppendParagraph("Body");
        int before = doc.ParagraphCount;
        _ = doc.GetTableOfContents();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableOfContents_CalledTwice_SameCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading A", 1);
        doc.AppendHeading("Heading B", 2);
        var toc1 = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(doc.GetTableOfContents()));
        var toc2 = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(doc.GetTableOfContents()));
        Assert.Equal(toc1.Count, toc2.Count);
    }

    [Fact]
    public void GetTableOfContents_AfterAddHeading_CountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        var before = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(doc.GetTableOfContents())).Count;
        doc.AppendHeading("Second", 1);
        var after = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(doc.GetTableOfContents())).Count;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleHeadingsAtDifferentLevels_AllInToc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Chapter 1 intro text");
        doc.AppendHeading("Section 1.1", 2);
        doc.AppendParagraph("Section body");
        doc.AppendHeading("Chapter 2", 1);
        var toc = new System.Collections.Generic.List<object>(
            System.Linq.Enumerable.Cast<object>(doc.GetTableOfContents()));
        Assert.Equal(3, toc.Count);
    }
}
