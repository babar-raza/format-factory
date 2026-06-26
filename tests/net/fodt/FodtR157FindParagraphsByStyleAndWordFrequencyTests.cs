// Tests for FodtDocument.FindParagraphsByStyle and GetWordFrequency.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R157

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R157: Tests for FodtDocument.FindParagraphsByStyle and GetWordFrequency.
/// FindParagraphsByStyle(pattern) returns paragraph indices where the effective style name
/// contains the pattern (case-insensitive substring). Heading elements with no explicit style
/// use the synthetic "Heading" style.
/// GetWordFrequency(minLength) returns a case-insensitive frequency map of words;
/// punctuation is stripped; words shorter than minLength are excluded.
/// Covers: FindParagraphsByStyle empty doc returns empty; heading found by "Heading" pattern;
/// case-insensitive style match; no match returns empty list; body paragraph found by style;
/// GetWordFrequency empty doc returns empty; single word has count 1; repeated word counted;
/// minLength filters short words; case-insensitive grouping; punctuation stripped;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->FindParagraphsByStyle pipeline.
/// </summary>
public class FodtR157FindParagraphsByStyleAndWordFrequencyTests
{
    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Empty(result);
    }

    [Fact]
    public void FindParagraphsByStyle_HeadingByPattern_ReturnsIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Contains(0, result);
    }

    [Fact]
    public void FindParagraphsByStyle_CaseInsensitive_Matches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter", 1);
        // "heading" (lowercase) should still match
        var lower = doc.FindParagraphsByStyle("heading");
        Assert.NotEmpty(lower);
    }

    [Fact]
    public void FindParagraphsByStyle_NoMatch_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just a body paragraph.");
        var result = doc.FindParagraphsByStyle("CustomStyleThatDoesNotExist");
        Assert.Empty(result);
    }

    [Fact]
    public void FindParagraphsByStyle_MultipleHeadings_AllReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Part One", 1);
        doc.AppendParagraph("Body text.");
        doc.InsertHeading(2, "Part Two", 2);

        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, result.Count);
        Assert.Contains(0, result);
        Assert.Contains(2, result);
    }

    [Fact]
    public void FindParagraphsByStyle_BodyParagraphExcludedFromHeadingSearch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text only.");
        var result = doc.FindParagraphsByStyle("Heading");
        Assert.Empty(result);
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_EmptyDoc_ReturnsEmptyDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        Assert.Empty(freq);
    }

    [Fact]
    public void GetWordFrequency_SingleWord_CountIsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var freq = doc.GetWordFrequency();
        Assert.True(freq.ContainsKey("hello"));
        Assert.Equal(1, freq["hello"]);
    }

    [Fact]
    public void GetWordFrequency_RepeatedWord_CountedCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat cat cat");
        var freq = doc.GetWordFrequency();
        Assert.Equal(3, freq["cat"]);
    }

    [Fact]
    public void GetWordFrequency_CaseInsensitiveGrouping()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Dog dog DOG");
        var freq = doc.GetWordFrequency();
        Assert.Equal(3, freq["dog"]);
    }

    [Fact]
    public void GetWordFrequency_MinLengthFiltersShortWords()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("a an the quick fox");
        // minLength=4 excludes "a", "an", "the" (3 chars)
        var freq = doc.GetWordFrequency(minLength: 4);
        Assert.DoesNotContain("a", freq.Keys);
        Assert.DoesNotContain("an", freq.Keys);
        Assert.DoesNotContain("the", freq.Keys);
        Assert.Contains("quick", freq.Keys);
        Assert.Contains("fox", freq.Keys);
    }

    [Fact]
    public void GetWordFrequency_PunctuationStripped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello, world! Hello.");
        var freq = doc.GetWordFrequency();
        // "hello" should be grouped together (commas/periods stripped)
        Assert.Equal(2, freq["hello"]);
        Assert.Equal(1, freq["world"]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: combined pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertHeadings_FindByStyle_WordFrequency_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The quick brown fox jumps over the lazy dog.");
        doc.InsertHeading(2, "Conclusion", 1);
        doc.AppendParagraph("The end.");

        // 4 paragraphs total
        Assert.Equal(4, doc.ParagraphCount);

        // Find headings
        var headingIndices = doc.FindParagraphsByStyle("Heading");
        Assert.Equal(2, headingIndices.Count);

        // Word frequency: "the" appears at least twice (paragraphs 1 and 3)
        var freq = doc.GetWordFrequency(minLength: 2);
        Assert.True(freq.ContainsKey("the"));
        Assert.True(freq["the"] >= 2);
    }
}
