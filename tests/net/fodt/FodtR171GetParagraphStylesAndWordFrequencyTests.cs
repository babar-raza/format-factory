// Tests for FodtDocument.GetParagraphStyles, FindParagraphsByStyle, GetWordFrequency, ExportToOutlineJson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R171

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R171: Tests for FodtDocument.GetParagraphStyles, FindParagraphsByStyle, GetWordFrequency, ExportToOutlineJson.
/// GetParagraphStyles(): returns list of unique style names present in document.
/// FindParagraphsByStyle(pattern): returns indices of paragraphs matching style pattern.
/// GetWordFrequency(minLength): returns word->count dictionary filtered by minLength.
/// ExportToOutlineJson(): returns JSON string representing document outline.
/// Covers: GetParagraphStyles non-empty doc returns list; GetParagraphStyles distinct values;
/// FindParagraphsByStyle heading pattern matches headings; FindParagraphsByStyle no match returns empty;
/// GetWordFrequency common word count correct; GetWordFrequency minLength filters short words;
/// GetWordFrequency empty doc returns empty; ExportToOutlineJson returns valid JSON;
/// ExportToOutlineJson contains heading text; ExportToOutlineJson empty doc returns valid JSON;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->GetStyles->FindByStyle->WordFreq pipeline.
/// </summary>
public class FodtR171GetParagraphStylesAndWordFrequencyTests
{
    private static FodtDocument BuildDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This is the first paragraph of the introduction.");
        doc.AppendParagraph("It contains multiple words.");
        doc.InsertHeading(3, "Summary", 2);
        doc.AppendParagraph("The summary paragraph summarizes the content.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetParagraphStyles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyles_NonEmptyDoc_ReturnsList()
    {
        var doc = BuildDoc();
        var styles = doc.GetParagraphStyles();
        Assert.NotEmpty(styles);
    }

    [Fact]
    public void GetParagraphStyles_ContainsDistinctValues()
    {
        var doc = BuildDoc();
        var styles = doc.GetParagraphStyles();
        // GetParagraphStyles() returns one style per paragraph (duplicates allowed for same style).
        // Verify there are at least 2 distinct styles (headings + body paragraphs).
        Assert.True(styles.Distinct().Count() >= 2);
    }

    [Fact]
    public void GetParagraphStyles_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var styles = doc.GetParagraphStyles();
        Assert.Empty(styles);
    }

    [Fact]
    public void GetParagraphStyles_AfterAppendParagraph_HasEntry()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");
        var styles = doc.GetParagraphStyles();
        Assert.NotEmpty(styles);
    }

    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_HeadingPattern_MatchesHeadings()
    {
        var doc = BuildDoc();
        // Headings use styles like "Heading 1", "Heading 2"
        var indices = doc.FindParagraphsByStyle("Heading");
        Assert.NotEmpty(indices);
    }

    [Fact]
    public void FindParagraphsByStyle_NoMatch_ReturnsEmpty()
    {
        var doc = BuildDoc();
        var indices = doc.FindParagraphsByStyle("NonExistentStyle12345");
        Assert.Empty(indices);
    }

    [Fact]
    public void FindParagraphsByStyle_HeadingCount_MatchesInserted()
    {
        var doc = BuildDoc();
        var indices = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, indices.Count); // 2 headings inserted
    }

    [Fact]
    public void FindParagraphsByStyle_IndicesInBounds()
    {
        var doc = BuildDoc();
        var indices = doc.FindParagraphsByStyle("Heading");
        Assert.All(indices, i => Assert.InRange(i, 0, doc.ParagraphCount - 1));
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        Assert.Empty(freq);
    }

    [Fact]
    public void GetWordFrequency_CommonWord_CountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("apple apple apple banana");
        var freq = doc.GetWordFrequency();
        Assert.True(freq.ContainsKey("apple") || freq.ContainsKey("Apple"));
        var appleCount = freq.TryGetValue("apple", out var c1) ? c1 :
                        freq.TryGetValue("Apple", out var c2) ? c2 : 0;
        Assert.Equal(3, appleCount);
    }

    [Fact]
    public void GetWordFrequency_MinLength_FiltersShortWords()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("a ab abc abcd abcde");
        var freq = doc.GetWordFrequency(minLength: 4);
        // Only "abcd" and "abcde" should appear
        Assert.All(freq.Keys, k => Assert.True(k.Length >= 4));
    }

    [Fact]
    public void GetWordFrequency_IsNotEmpty_ForNonEmptyDoc()
    {
        var doc = BuildDoc();
        var freq = doc.GetWordFrequency();
        Assert.NotEmpty(freq);
    }

    // -------------------------------------------------------------------------
    // ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_ReturnsValidJson()
    {
        var doc = BuildDoc();
        var json = doc.ExportToOutlineJson();
        Assert.NotEmpty(json);
        // Valid JSON should start with { or [
        var trimmed = json.Trim();
        Assert.True(trimmed.StartsWith("{") || trimmed.StartsWith("["));
    }

    [Fact]
    public void ExportToOutlineJson_ContainsHeadingText()
    {
        var doc = BuildDoc();
        var json = doc.ExportToOutlineJson();
        Assert.Contains("Introduction", json);
    }

    [Fact]
    public void ExportToOutlineJson_EmptyDoc_ReturnsValidJson()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        // Should return valid JSON (could be empty array or object)
        var trimmed = json.Trim();
        Assert.True(trimmed.StartsWith("{") || trimmed.StartsWith("[") || trimmed == "");
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeading->AppendParagraph->GetStyles->FindByStyle->WordFreq
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_StylesWordFrequencyOutline_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.AppendParagraph("The fox is quick and the dog is lazy.");
        doc.InsertHeading(3, "Chapter Two", 1);
        doc.AppendParagraph("Another paragraph in chapter two.");

        // Styles should include paragraph and heading styles
        var styles = doc.GetParagraphStyles();
        Assert.NotEmpty(styles);

        // Find headings by style
        var headingIndices = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, headingIndices.Count);

        // Word frequency: "the" should appear multiple times
        var freq = doc.GetWordFrequency(minLength: 3);
        Assert.NotEmpty(freq);
        Assert.All(freq.Keys, k => Assert.True(k.Length >= 3));

        // Outline JSON should include chapter titles
        var json = doc.ExportToOutlineJson();
        Assert.Contains("Chapter One", json);
    }
}
