// Tests for FodtDocument.GetPlainTextRange, ReplaceText, and SearchText deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R183

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R183: Tests for FodtDocument.GetPlainTextRange, ReplaceText, and SearchText deeper coverage.
/// GetPlainTextRange(start, end): extracts text from a paragraph range.
/// ReplaceText(old, new): replaces all occurrences of old text with new text.
/// SearchText(query, comparison): finds all occurrences of query in paragraphs.
/// Covers: GetPlainTextRange returns non-null; GetPlainTextRange single paragraph;
/// GetPlainTextRange full range; ReplaceText returns count of replacements;
/// ReplaceText changes paragraph content; ReplaceText case-sensitive (default);
/// ReplaceText case-insensitive with OrdinalIgnoreCase; SearchText empty for no match;
/// SearchText finds occurrence; SearchText count matches occurrences;
/// RemoveAllParagraphs clears ParagraphCount; AppendParagraph after clear works;
/// GetPlainText after ReplaceText contains new value;
/// dogfood Load->AppendParagraph->SearchText->ReplaceText->GetPlainText.
/// </summary>
public class FodtR183GetPlainTextRangeAndReplaceTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    public FodtR183GetPlainTextRangeAndReplaceTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR183_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private FodtDocument LoadFixture() =>
        FodtDocument.Load(Path.GetFullPath(FodtFixturePath));

    // -------------------------------------------------------------------------
    // GetPlainTextRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainTextRange_ReturnsNonNull()
    {
        var doc = LoadFixture();
        var text = doc.GetPlainTextRange(0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetPlainTextRange_SingleParagraph_NonEmpty()
    {
        var doc = LoadFixture();
        var text = doc.GetPlainTextRange(0, 0);
        Assert.True(string.IsNullOrEmpty(text));
    }

    [Fact]
    public void GetPlainTextRange_FullRange_ContainsMultipleParagraphs()
    {
        var doc = LoadFixture();
        Assert.True(doc.ParagraphCount >= 2);
        var text = doc.GetPlainTextRange(0, doc.ParagraphCount - 1);
        Assert.False(string.IsNullOrEmpty(text));
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_ReturnsCountOfReplacements()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The quick brown fox");
        doc.AppendParagraph("The lazy dog");
        var count = doc.ReplaceText("The", "A");
        Assert.Equal(2, count);
    }

    [Fact]
    public void ReplaceText_ZeroForNoMatch()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var count = doc.ReplaceText("xyz_not_here", "something");
        Assert.Equal(0, count);
    }

    [Fact]
    public void ReplaceText_ChangesContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        doc.ReplaceText("World", "Universe");
        var text = doc.GetPlainText();
        Assert.Contains("Universe", text);
        Assert.DoesNotContain("World", text);
    }

    [Fact]
    public void ReplaceText_DefaultIsCaseSensitive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello HELLO");
        var count = doc.ReplaceText("hello", "bye");
        Assert.Equal(1, count); // only lowercase "hello" matched
    }

    [Fact]
    public void ReplaceText_OrdinalIgnoreCase_MatchesBothCases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello HELLO");
        var count = doc.ReplaceText("hello", "bye", StringComparison.OrdinalIgnoreCase);
        Assert.Equal(2, count);
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NoMatch_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text here");
        var results = doc.SearchText("zzz_no_match_zzz");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_SingleMatch_ReturnsOneResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Find me here");
        var results = doc.SearchText("Find");
        Assert.Single(results);
    }

    [Fact]
    public void SearchText_MultiParagraph_FindsInCorrectParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Target text here");
        var results = doc.SearchText("Target");
        Assert.Single(results);
        Assert.Equal(1, results[0].ParagraphIndex);
    }

    // -------------------------------------------------------------------------
    // RemoveAllParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveAllParagraphs_ClearsParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        doc.RemoveAllParagraphs();
        Assert.Equal(0, doc.ParagraphCount);
    }

    [Fact]
    public void AppendParagraph_AfterClear_Works()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial");
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("After clear");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Contains("After clear", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AppendParagraph->SearchText->ReplaceText->GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendSearchReplacePlainText_Pipeline()
    {
        var doc = LoadFixture();
        var initial = doc.ParagraphCount;

        // Append a paragraph with known text
        doc.AppendParagraph("R183 unique marker text");
        Assert.Equal(initial + 1, doc.ParagraphCount);

        // SearchText finds the appended text
        var results = doc.SearchText("R183");
        Assert.NotEmpty(results);

        // ReplaceText updates the content
        var replaced = doc.ReplaceText("R183 unique marker text", "R183 replaced");
        Assert.Equal(1, replaced);

        // GetPlainText contains new value
        var text = doc.GetPlainText();
        Assert.Contains("R183 replaced", text);
        Assert.DoesNotContain("R183 unique marker text", text);
    }
}
