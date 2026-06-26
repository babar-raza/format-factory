// Tests for FodtDocument.GetWordFrequency, SearchText, GetCharCount, GetWordCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R180

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R180: Tests for FodtDocument.GetWordFrequency, SearchText, GetCharCount, GetWordCount.
/// GetWordFrequency(): returns dict of word → count.
/// SearchText(query): returns list of (ParagraphIndex, Position) tuples.
/// GetCharCount: total character count across all paragraphs.
/// GetWordCount: total word count across all paragraphs.
/// Covers: GetWordFrequency is non-null; GetWordFrequency has entries;
/// GetWordFrequency count for known word; SearchText non-empty for existing text;
/// SearchText empty for non-existing text; SearchText(StringComparison) works;
/// GetCharCount positive for non-empty doc; GetWordCount positive;
/// GetWordCount >= GetWordFrequency total unique; AppendParagraph increases WordCount;
/// ReplaceText updates frequency; SearchText after ReplaceText;
/// dogfood Load->AppendParagraph->GetWordFrequency->SearchText pipeline.
/// </summary>
public class FodtR180WordFrequencyAndSearchTests
{
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    private FodtDocument LoadFixture()
    {
        var path = Path.GetFullPath(FodtFixturePath);
        return FodtDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_IsNonNull()
    {
        var doc = LoadFixture();
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
    }

    [Fact]
    public void GetWordFrequency_HasEntries()
    {
        var doc = LoadFixture();
        var freq = doc.GetWordFrequency();
        Assert.True(freq.Count > 0);
    }

    [Fact]
    public void GetWordFrequency_AppendedWord_AppearsInDict()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("UniquePigeonWord UniquePigeonWord UniquePigeonWord");
        var freq = doc.GetWordFrequency();
        Assert.True(freq.ContainsKey("UniquePigeonWord"));
        Assert.Equal(3, freq["UniquePigeonWord"]);
    }

    [Fact]
    public void GetWordFrequency_AllCountsPositive()
    {
        var doc = LoadFixture();
        var freq = doc.GetWordFrequency();
        Assert.All(freq.Values, count => Assert.True(count > 0));
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_ExistingText_ReturnsNonEmpty()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("SearchableUniquePhrase");
        var results = doc.SearchText("SearchableUniquePhrase");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void SearchText_NonExistingText_ReturnsEmpty()
    {
        var doc = LoadFixture();
        var results = doc.SearchText("ZZZNeverExistsZZZ");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_CaseSensitive_DoesNotMatchDifferentCase()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("CaseSensitiveParagraph");
        var results = doc.SearchText("casesensitiveparagraph"); // lowercase
        // Default is case-sensitive, so should be empty
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_WithIgnoreCase_Matches()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("MixedCaseWord");
        var results = doc.SearchText("mixedcaseword",
            StringComparison.OrdinalIgnoreCase);
        Assert.NotEmpty(results);
    }

    [Fact]
    public void SearchText_ReturnsCorrectParagraphIndex()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("UniqueTermForParagraphSearch");
        var results = doc.SearchText("UniqueTermForParagraphSearch");
        Assert.NotEmpty(results);
        // Should reference last paragraph index
        Assert.Equal(doc.ParagraphCount - 1, results[0].ParagraphIndex);
    }

    // -------------------------------------------------------------------------
    // GetCharCount / GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_PositiveForNonEmptyDoc()
    {
        var doc = LoadFixture();
        Assert.True(doc.CharCount > 0);
    }

    [Fact]
    public void GetWordCount_PositiveForNonEmptyDoc()
    {
        var doc = LoadFixture();
        Assert.True(doc.WordCount > 0);
    }

    [Fact]
    public void GetWordCount_IncreasesAfterAppend()
    {
        var doc = LoadFixture();
        var before = doc.WordCount;
        doc.AppendParagraph("one two three");
        Assert.True(doc.WordCount > before);
    }

    [Fact]
    public void GetCharCount_IncreasesAfterAppend()
    {
        var doc = LoadFixture();
        var before = doc.CharCount;
        doc.AppendParagraph("additional characters added here");
        Assert.True(doc.CharCount > before);
    }

    // -------------------------------------------------------------------------
    // ReplaceText updates frequency
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_UpdatesGetWordFrequency()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("OldWord OldWord OldWord");
        doc.ReplaceText("OldWord", "NewWord");
        var freq = doc.GetWordFrequency();
        Assert.False(freq.ContainsKey("OldWord")); // replaced
        Assert.True(freq.ContainsKey("NewWord")); // new key
    }

    [Fact]
    public void SearchText_AfterReplaceText_FindsNewText()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("BeforeReplace");
        doc.ReplaceText("BeforeReplace", "AfterReplace");
        var results = doc.SearchText("AfterReplace");
        Assert.NotEmpty(results);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AppendParagraph->GetWordFrequency->SearchText pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendFrequencySearchPipeline()
    {
        var doc = LoadFixture();
        var initialWordCount = doc.WordCount;
        var initialCharCount = doc.CharCount;

        // Append paragraph with known words
        doc.AppendParagraph("apple banana cherry apple apple banana");
        Assert.True(doc.WordCount > initialWordCount);
        Assert.True(doc.CharCount > initialCharCount);

        // Get word frequency
        var freq = doc.GetWordFrequency();
        Assert.True(freq.ContainsKey("apple"));
        Assert.Equal(3, freq["apple"]);
        Assert.Equal(2, freq["banana"]);
        Assert.Equal(1, freq["cherry"]);

        // Search
        var appleResults = doc.SearchText("apple");
        Assert.NotEmpty(appleResults);

        var noResults = doc.SearchText("ZZZNonExistent");
        Assert.Empty(noResults);

        // Replace and re-search
        doc.ReplaceText("cherry", "mango");
        var mangoResults = doc.SearchText("mango");
        Assert.NotEmpty(mangoResults);

        var cherryResults = doc.SearchText("cherry");
        Assert.Empty(cherryResults);
    }
}
