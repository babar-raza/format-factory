// Tests for FodtDocument.ExtractPlainParagraphs dedicated coverage.
// Sprint: ff-sprint-s234-dotnet-deepening-20260629
// Ledger: PC-FODT-R249

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R249: Dedicated tests for FodtDocument.ExtractPlainParagraphs().
/// Empty document → returns non-null result.
/// Empty document → returns empty or zero-count list.
/// Paragraphs-only → count matches appended paragraphs.
/// Headings-only → returns empty (headings excluded).
/// Mixed content → only plain paragraphs returned.
/// ParagraphCount unchanged after call.
/// Text of plain paragraphs is preserved.
/// Called twice → same result.
/// After append paragraph → count increases.
/// Dogfood: mixed headings and paragraphs, verify only paragraphs returned.
/// </summary>
public class FodtR249ExtractPlainParagraphsTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractPlainParagraphs_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.ExtractPlainParagraphs();
        Assert.NotNull(result);
    }

    [Fact]
    public void ExtractPlainParagraphs_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Empty(list);
    }

    [Fact]
    public void ExtractPlainParagraphs_ParagraphsOnly_CountMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Equal(3, list.Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_HeadingsOnly_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading One", 1);
        doc.AppendHeading("Heading Two", 2);
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Empty(list);
    }

    [Fact]
    public void ExtractPlainParagraphs_MixedContent_OnlyParagraphsReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        doc.AppendParagraph("Body text one");
        doc.AppendHeading("Chapter Two", 1);
        doc.AppendParagraph("Body text two");
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Equal(2, list.Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        _ = doc.ExtractPlainParagraphs();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ExtractPlainParagraphs_TextPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("UniqueTextContent");
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Contains("UniqueTextContent", list);
    }

    [Fact]
    public void ExtractPlainParagraphs_CalledTwice_SameCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para One");
        doc.AppendParagraph("Para Two");
        var list1 = new System.Collections.Generic.List<string>(doc.ExtractPlainParagraphs());
        var list2 = new System.Collections.Generic.List<string>(doc.ExtractPlainParagraphs());
        Assert.Equal(list1.Count, list2.Count);
    }

    [Fact]
    public void ExtractPlainParagraphs_AfterAppend_CountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial");
        var before = new System.Collections.Generic.List<string>(doc.ExtractPlainParagraphs()).Count;
        doc.AppendParagraph("Added");
        var after = new System.Collections.Generic.List<string>(doc.ExtractPlainParagraphs()).Count;
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_OnlyPlainParagraphsReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        doc.AppendParagraph("Welcome to the document");
        doc.AppendHeading("Section 1", 2);
        doc.AppendParagraph("First section body");
        doc.AppendParagraph("More section body");
        doc.AppendHeading("Conclusion", 1);
        var result = doc.ExtractPlainParagraphs();
        var list = new System.Collections.Generic.List<string>(result);
        Assert.Equal(3, list.Count);
        Assert.Contains("Welcome to the document", list);
        Assert.Contains("First section body", list);
        Assert.Contains("More section body", list);
    }
}
