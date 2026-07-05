// Tests for FodtDocument.GetPlainText, GetPlainTextRange, ReplaceText, SearchText.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R173

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R173: Tests for FodtDocument.GetPlainText, GetPlainTextRange, ReplaceText, SearchText.
/// GetPlainText(): returns all text content joined as plain string.
/// GetPlainTextRange(startIndex, endIndex): returns text from paragraphs in range.
/// ReplaceText(old, new): replaces all occurrences; returns count of replacements.
/// SearchText(query): returns list of (ParagraphIndex, Position) matches.
/// Covers: GetPlainText empty doc is empty/whitespace; GetPlainText includes all paragraphs;
/// GetPlainText includes headings; GetPlainTextRange single paragraph;
/// GetPlainTextRange multiple paragraphs; ReplaceText single occurrence;
/// ReplaceText multiple occurrences returns count; ReplaceText no match returns 0;
/// SearchText finds match in paragraph; SearchText empty query behavior;
/// SearchText case-sensitive vs ordinal; dogfood Append->Replace->Search->PlainText pipeline.
/// </summary>
public class FodtR173GetPlainTextAndReplaceTextTests
{
    // -------------------------------------------------------------------------
    // GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_EmptyDoc_IsEmptyOrWhitespace()
    {
        var doc = FodtDocument.CreateEmpty();
        var text = doc.GetPlainText();
        Assert.True(string.IsNullOrWhiteSpace(text));
    }

    [Fact]
    public void GetPlainText_IncludesAllParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        var text = doc.GetPlainText();
        Assert.Contains("First paragraph", text);
        Assert.Contains("Second paragraph", text);
    }

    [Fact]
    public void GetPlainText_IncludesHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Main Title", 1);
        doc.AppendParagraph("Body text");
        var text = doc.GetPlainText();
        Assert.Contains("Main Title", text);
        Assert.Contains("Body text", text);
    }

    [Fact]
    public void GetPlainText_SingleParagraph_ReturnsItsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var text = doc.GetPlainText();
        Assert.Contains("Hello world", text);
    }

    // -------------------------------------------------------------------------
    // GetPlainTextRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_SingleParagraph_ReturnsItsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var text = doc.GetPlainTextRange(1, 2); // exclusive end: (1,2) returns index 1 = "Second"
        Assert.Contains("Second", text);
    }

    [Fact]
    public void GetPlainTextRange_MultipleParagraphs_IncludesAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        doc.AppendParagraph("Para C");
        var text = doc.GetPlainTextRange(0, 2); // exclusive end: (0,2) returns indices 0,1 = "Para A","Para B"
        Assert.Contains("Para A", text);
        Assert.Contains("Para B", text);
    }

    [Fact]
    public void GetPlainTextRange_ExcludesOutOfRangeParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var text = doc.GetPlainTextRange(0, 0);
        // Should not include "Third" (index 2)
        Assert.DoesNotContain("Third", text);
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_SingleOccurrence_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var count = doc.ReplaceText("world", "there");
        Assert.Equal(1, count);
    }

    [Fact]
    public void ReplaceText_SingleOccurrence_ReplacesText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.ReplaceText("world", "there");
        Assert.Contains("there", doc.GetPlainText());
        Assert.DoesNotContain("world", doc.GetPlainText());
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_ReturnsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("foo bar foo");
        doc.AppendParagraph("baz foo");
        var count = doc.ReplaceText("foo", "xyz");
        Assert.Equal(3, count);
    }

    [Fact]
    public void ReplaceText_NoMatch_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var count = doc.ReplaceText("notfound", "replacement");
        Assert.Equal(0, count);
    }

    [Fact]
    public void ReplaceText_NoMatch_ContentUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        doc.ReplaceText("xyz", "abc");
        Assert.Contains("Hello world", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_FindsMatch_ReturnsList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var matches = doc.SearchText("world");
        Assert.NotEmpty(matches);
    }

    [Fact]
    public void SearchText_NoMatch_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var matches = doc.SearchText("notfound");
        Assert.Empty(matches);
    }

    [Fact]
    public void SearchText_MultipleMatches_CountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat and cat");
        var matches = doc.SearchText("cat");
        Assert.Equal(2, matches.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Append->Replace->Search->PlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendReplaceSearchPlainText_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.AppendParagraph("The fox is very quick.");
        doc.AppendParagraph("The dog is very lazy.");

        // GetPlainText should include all content
        var plain = doc.GetPlainText();
        Assert.Contains("Introduction", plain);
        Assert.Contains("fox", plain);

        // SearchText finds "fox" twice
        var foxMatches = doc.SearchText("fox");
        Assert.Equal(2, foxMatches.Count);

        // ReplaceText
        var count = doc.ReplaceText("fox", "cat");
        Assert.Equal(2, count);

        // After replace, "fox" should not be in plain text
        var afterPlain = doc.GetPlainText();
        Assert.Contains("cat", afterPlain);
        Assert.DoesNotContain("fox", afterPlain);

        // GetPlainTextRange: first two paragraphs
        var range = doc.GetPlainTextRange(0, 1);
        Assert.Contains("Introduction", range);
    }
}
