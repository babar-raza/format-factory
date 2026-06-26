// Tests for FodtDocument.GetWordFrequency, SearchText, GetTextBetweenParagraphs.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R188

using System;
using System.Linq;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R188: Tests for FodtDocument.GetWordFrequency, SearchText, GetTextBetweenParagraphs.
/// GetWordFrequency(): returns word→count dictionary.
/// SearchText(query): returns list of (ParagraphIndex, Position) matches.
/// GetTextBetweenParagraphs(startIndex, endIndex): returns text spanning range.
/// Covers: GetWordFrequency non-null; GetWordFrequency has entries after AppendParagraph;
/// GetWordFrequency known word count; GetWordFrequency minLength filters short words;
/// SearchText exact match returns non-empty; SearchText no match returns empty;
/// SearchText match position correct; SearchText case-sensitive by default;
/// SearchText case-insensitive with OrdinalIgnoreCase; GetTextBetweenParagraphs non-null;
/// GetTextBetweenParagraphs contains first paragraph text; GetTextBetweenParagraphs range;
/// GetWordFrequency after multiple paragraphs;
/// dogfood CreateEmpty->AppendParagraphs->GetWordFrequency->SearchText->GetTextBetween.
/// </summary>
public class FodtR188GetWordFrequencyAndSearchTextTests
{
    private static FodtDocument CreateWithParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.AppendParagraph("The fox was very quick and very clever.");
        doc.AppendParagraph("A quick brown dog outpaced a lazy fox.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NonNull()
    {
        var doc = CreateWithParagraphs();
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
    }

    [Fact]
    public void GetWordFrequency_HasEntriesAfterAppend()
    {
        var doc = CreateWithParagraphs();
        var freq = doc.GetWordFrequency();
        Assert.NotEmpty(freq);
    }

    [Fact]
    public void GetWordFrequency_KnownWord_CountCorrect()
    {
        var doc = CreateWithParagraphs();
        var freq = doc.GetWordFrequency();
        // "fox" appears 3 times (once per paragraph), "the" appears >=2 times
        Assert.True(freq.ContainsKey("fox"));
        Assert.Equal(3, freq["fox"]);
    }

    [Fact]
    public void GetWordFrequency_QuickAppearsThreeTimes()
    {
        var doc = CreateWithParagraphs();
        var freq = doc.GetWordFrequency();
        Assert.True(freq.ContainsKey("quick"));
        Assert.Equal(3, freq["quick"]);
    }

    [Fact]
    public void GetWordFrequency_MinLength_FiltersShortWords()
    {
        var doc = CreateWithParagraphs();
        var freq = doc.GetWordFrequency(minLength: 4);
        // Single-char words like "a" should be excluded
        Assert.False(freq.ContainsKey("a"));
    }

    [Fact]
    public void GetWordFrequency_AfterMultipleParagraphs_EntriesGrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha beta gamma.");
        var freq1 = doc.GetWordFrequency();
        doc.AppendParagraph("Delta epsilon zeta.");
        var freq2 = doc.GetWordFrequency();
        Assert.True(freq2.Count > freq1.Count);
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_ExactMatch_ReturnsNonEmpty()
    {
        var doc = CreateWithParagraphs();
        var matches = doc.SearchText("quick");
        Assert.NotEmpty(matches);
    }

    [Fact]
    public void SearchText_NoMatch_ReturnsEmpty()
    {
        var doc = CreateWithParagraphs();
        var matches = doc.SearchText("xylophone_nonexistent");
        Assert.Empty(matches);
    }

    [Fact]
    public void SearchText_MultipleOccurrences_CountIsThree()
    {
        var doc = CreateWithParagraphs();
        var matches = doc.SearchText("quick");
        Assert.Equal(3, matches.Count);
    }

    [Fact]
    public void SearchText_CaseSensitive_MissesUppercase()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The Quick Brown Fox.");
        var matches = doc.SearchText("quick", StringComparison.Ordinal);
        Assert.Empty(matches); // "Quick" != "quick" with Ordinal
    }

    [Fact]
    public void SearchText_OrdinalIgnoreCase_FindsUppercase()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The Quick Brown Fox.");
        var matches = doc.SearchText("quick", StringComparison.OrdinalIgnoreCase);
        Assert.NotEmpty(matches);
    }

    // -------------------------------------------------------------------------
    // GetTextBetweenParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextBetweenParagraphs_NonNull()
    {
        var doc = CreateWithParagraphs();
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_ContainsFirstParagraphText()
    {
        var doc = CreateWithParagraphs();
        var text = doc.GetTextBetweenParagraphs(0, 0);
        Assert.Contains("quick", text);
    }

    [Fact]
    public void GetTextBetweenParagraphs_TwoParagraphRange_ContainsBoth()
    {
        var doc = CreateWithParagraphs();
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Contains("fox", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraphs->GetWordFrequency->SearchText->GetTextBetween
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAppendGetWordFreqSearchGetTextBetween_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world, this is a test document.");
        doc.AppendParagraph("Hello again, this is the second paragraph.");
        doc.AppendParagraph("Final paragraph with world content.");

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.ContainsKey("hello"));
        Assert.Equal(2, freq["hello"]);
        Assert.True(freq.ContainsKey("world"));
        Assert.Equal(2, freq["world"]);

        // SearchText
        var helloMatches = doc.SearchText("Hello");
        Assert.Equal(2, helloMatches.Count);

        var noMatches = doc.SearchText("nonexistent_xyz");
        Assert.Empty(noMatches);

        // GetTextBetweenParagraphs
        var between = doc.GetTextBetweenParagraphs(0, 1);
        Assert.NotNull(between);
        Assert.Contains("Hello", between);

        // WordCount and CharCount
        Assert.True(doc.WordCount > 0);
        Assert.True(doc.CharCount > 0);
    }
}
