// Tests for FodtDocument.GetDocumentStats() and individual stat getters.
// Sprint: FORMAT-FACTORY-FODT-DOCUMENT-STATS-20260626
// Ledger: R122-GOVERNED-DOTNET-FODT-DOCUMENT-STATS-001

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R122: GetDocumentStats() returns a tuple (WordCount, CharCount, ParagraphCount, HeadingCount).
///       Also exercises GetWordCount(), GetCharCount(), GetHeadingCount(), GetParagraphCount()
///       and verifies tuple consistency with individual accessors.
/// </summary>
public class FodtR122GetDocumentStatsTests
{
    // ---- Empty document ----

    [Fact]
    public void GetDocumentStats_EmptyDoc_AllZero()
    {
        var doc = FodtDocument.CreateEmpty();
        var stats = doc.GetDocumentStats();

        Assert.Equal(0, stats.WordCount);
        Assert.Equal(0, stats.CharCount);
        Assert.Equal(0, stats.ParagraphCount);
        Assert.Equal(0, stats.HeadingCount);
    }

    // ---- Single body paragraph ----

    [Fact]
    public void GetDocumentStats_SingleParagraph_ParagraphCountOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        var stats = doc.GetDocumentStats();
        Assert.Equal(1, stats.ParagraphCount);
        Assert.Equal(0, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_TwoWordParagraph_WordCountTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello world");

        var stats = doc.GetDocumentStats();
        Assert.Equal(2, stats.WordCount);
    }

    [Fact]
    public void GetDocumentStats_CharCount_MatchesTextLength()
    {
        var doc = FodtDocument.CreateEmpty();
        const string text = "abcde";
        doc.AppendParagraph(text);

        var stats = doc.GetDocumentStats();
        Assert.Equal(text.Length, stats.CharCount);
    }

    // ---- Heading counted in HeadingCount ----

    [Fact]
    public void GetDocumentStats_Heading_CountedInBothParagraphAndHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Title", 1);

        var stats = doc.GetDocumentStats();
        Assert.Equal(1, stats.ParagraphCount);
        Assert.Equal(1, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_MixedContent_HeadingPlusBodies()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Body one");
        doc.AppendParagraph("Body two");

        var stats = doc.GetDocumentStats();
        Assert.Equal(3, stats.ParagraphCount);
        Assert.Equal(1, stats.HeadingCount);
        Assert.True(stats.WordCount >= 4); // "Title"(1) + "Body one"(2) + "Body two"(2)
    }

    // ---- Tuple matches individual getters ----

    [Fact]
    public void GetDocumentStats_WordCount_MatchesGetWordCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("one two three");
        doc.AppendParagraph("four five");

        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
    }

    [Fact]
    public void GetDocumentStats_CharCount_MatchesGetCharCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("testing chars");

        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetCharCount(), stats.CharCount);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesGetParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para one");
        doc.AppendParagraph("Para two");

        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesGetHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.InsertHeading(1, "H2", 2);
        doc.AppendParagraph("Body");

        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
    }

    // ---- Dogfood: stats before and after edits ----

    [Fact]
    public void DogfoodPipeline_StatsReflectEdits()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");

        var before = doc.GetDocumentStats();
        Assert.Equal(1, before.ParagraphCount);

        doc.AppendParagraph("Beta gamma");
        var after = doc.GetDocumentStats();

        Assert.Equal(2, after.ParagraphCount);
        Assert.True(after.WordCount > before.WordCount);
        Assert.True(after.CharCount > before.CharCount);
    }
}
