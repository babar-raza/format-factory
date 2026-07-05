// Tests for FodtDocument.ReplaceText dedicated coverage.
// Sprint: ff-sprint-s165-dotnet-deepening-20260628
// Ledger: PC-FODT-R174

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R174: Dedicated tests for FodtDocument.ReplaceText(string oldText, string newText, StringComparison comparison).
/// ReplaceText replaces all occurrences of oldText with newText in all paragraphs.
/// Returns the total number of replacements made.
/// Throws ArgumentException if oldText is null or empty.
/// Throws ArgumentNullException if newText is null.
/// Covers: null oldText throws ArgumentException; empty oldText throws ArgumentException;
/// null newText throws ArgumentNullException; empty document returns 0;
/// no match returns 0; single match returns 1; text is replaced in paragraph;
/// multiple occurrences returns correct count; replacement in multiple paragraphs;
/// dogfood AppendParagraph->ReplaceText->GetParagraphText; dogfood case-insensitive replacement.
/// </summary>
public class FodtR174ReplaceTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_NullOldText_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentNullException>(() => doc.ReplaceText(null!, "new"));
    }

    [Fact]
    public void ReplaceText_EmptyOldText_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentException>(() => doc.ReplaceText(string.Empty, "new"));
    }

    [Fact]
    public void ReplaceText_NullNewText_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentNullException>(() => doc.ReplaceText("old", null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.ReplaceText("foo", "bar"));
    }

    [Fact]
    public void ReplaceText_NoMatch_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Equal(0, doc.ReplaceText("xyz", "abc"));
    }

    [Fact]
    public void ReplaceText_SingleMatch_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        Assert.Equal(1, doc.ReplaceText("World", "Earth"));
    }

    [Fact]
    public void ReplaceText_ReplacedTextAppearsInParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "Earth");
        Assert.Contains("Earth", doc.GetParagraphText(0)!);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences_ReturnsCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat and cat and cat");
        Assert.Equal(3, doc.ReplaceText("cat", "dog"));
    }

    [Fact]
    public void ReplaceText_MultiParagraph_ReplacesAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("word here");
        doc.AppendParagraph("another word");
        Assert.Equal(2, doc.ReplaceText("word", "term"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_ReplaceText_GetParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        doc.ReplaceText("quick", "slow");
        var text = doc.GetParagraphText(0);
        Assert.Contains("slow", text!);
        Assert.DoesNotContain("quick", text!);
    }

    [Fact]
    public void DogfoodPipeline_CaseInsensitiveReplacement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello WORLD");
        var count = doc.ReplaceText("world", "Earth", StringComparison.OrdinalIgnoreCase);
        Assert.Equal(1, count);
    }
}
