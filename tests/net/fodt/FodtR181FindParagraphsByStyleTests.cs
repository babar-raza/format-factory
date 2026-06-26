// Tests for FodtDocument.FindParagraphsByStyle dedicated coverage.
// Sprint: ff-sprint-s172-dotnet-deepening-20260628
// Ledger: PC-FODT-R181

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R181: Dedicated tests for FodtDocument.FindParagraphsByStyle(string stylePattern).
/// Returns IReadOnlyList&lt;int&gt; of paragraph indices where the effective style name
/// contains stylePattern (case-insensitive).
/// Effective style: uses explicit text:style-name if set; otherwise uses "Heading"
/// for heading elements, or "" for body paragraphs.
/// Throws ArgumentNullException for null stylePattern.
/// Covers: null stylePattern throws ArgumentNullException; empty doc returns empty;
/// empty pattern matches all paragraphs; heading matches "Heading" (case-insensitive);
/// heading matches "heading" (lower); body paragraph with empty style matches empty pattern;
/// non-matching pattern returns empty; returns IReadOnlyList&lt;int&gt; type;
/// indices are in document order; dogfood AppendHeading->FindParagraphsByStyle pipeline;
/// dogfood mixed content heading indices correct.
/// </summary>
public class FodtR181FindParagraphsByStyleTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_NullPattern_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        Assert.Throws<ArgumentNullException>(() => doc.FindParagraphsByStyle(null!));
    }

    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Empty(result);
    }

    [Fact]
    public void FindParagraphsByStyle_ReturnsIReadOnlyListOfInt()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.IsAssignableFrom<IReadOnlyList<int>>(result);
    }

    [Fact]
    public void FindParagraphsByStyle_EmptyPattern_MatchesAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body 1");
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body 2");
        // Empty pattern: Contains("") is always true
        var result = doc.FindParagraphsByStyle("");
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void FindParagraphsByStyle_HeadingPattern_MatchesHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");      // index 0 — no heading
        doc.AppendHeading("Title", 1);    // index 1 — heading
        doc.AppendHeading("Section", 2);  // index 2 — heading
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void FindParagraphsByStyle_CaseInsensitive_LowercaseMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var result = doc.FindParagraphsByStyle("heading");
        Assert.Equal(1, result.Count);
    }

    [Fact]
    public void FindParagraphsByStyle_NonMatchingPattern_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        doc.AppendHeading("Title", 1);
        var result = doc.FindParagraphsByStyle("ZZZNoSuchStyle");
        Assert.Empty(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeading_FindParagraphsByStyle_ReturnsIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1); // index 0
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Single(result);
        Assert.Equal(0, result[0]);
    }

    [Fact]
    public void DogfoodPipeline_MixedContent_HeadingIndicesCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");      // index 0
        doc.AppendHeading("Chapter 1", 1); // index 1 — heading
        doc.AppendParagraph("Body 1");     // index 2
        doc.AppendHeading("Chapter 2", 1); // index 3 — heading
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, result.Count);
        Assert.Equal(1, result[0]); // first heading at index 1
        Assert.Equal(3, result[1]); // second heading at index 3
    }

    [Fact]
    public void FindParagraphsByStyle_IndicesInDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1); // index 0
        doc.AppendParagraph("P1");  // index 1
        doc.AppendHeading("H2", 2); // index 2
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, result.Count);
        Assert.True(result[0] < result[1]); // in order
    }
}
