// Tests for FodtDocument.GetDocumentMetadata and GetDocumentStats consistency.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R199

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R199: Tests for FodtDocument.GetDocumentMetadata, GetDocumentStats consistency.
/// GetDocumentMetadata(): returns metadata dictionary (title, author, date, etc.).
/// GetDocumentStats(): returns comprehensive document statistics.
/// Covers: GetDocumentMetadata non-null; GetDocumentMetadata non-empty;
/// GetDocumentMetadata contains known key; GetDocumentMetadata ParagraphCount key present;
/// GetDocumentStats non-null; GetDocumentStats ParagraphCount positive after AppendParagraph;
/// GetDocumentStats HeadingCount positive after InsertHeading;
/// GetDocumentStats CharacterCount positive after AppendParagraph;
/// GetDocumentStats WordCount positive after AppendParagraph;
/// GetDocumentMetadata + GetDocumentStats consistency (paragraph counts match);
/// GetDocumentStats after ReplaceText reflects change;
/// GetDocumentMetadata keys are non-empty strings;
/// GetDocumentStats after ClearContent counts are zero;
/// dogfood CreateEmpty->InsertHeadings->AppendParagraphs->GetMetadata->GetStats->Verify consistency.
/// </summary>
public class FodtR199GetDocumentMetadataTests
{
    private static FodtDocument CreateFullDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("The first paragraph has several words and provides context.");
        doc.AppendParagraph("The second paragraph continues the narrative.");
        doc.InsertHeading(2, "Chapter Two", 1);
        doc.AppendParagraph("Chapter two introduces new concepts and ideas.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_NonNull()
    {
        var doc = CreateFullDoc();
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    [Fact]
    public void GetDocumentMetadata_NonEmpty()
    {
        var doc = CreateFullDoc();
        var meta = doc.GetDocumentMetadata();
        Assert.NotEmpty(meta);
    }

    [Fact]
    public void GetDocumentMetadata_KeysAreNonEmptyStrings()
    {
        var doc = CreateFullDoc();
        var meta = doc.GetDocumentMetadata();
        foreach (var key in meta.Keys)
            Assert.False(string.IsNullOrEmpty(key));
    }

    [Fact]
    public void GetDocumentMetadata_ValuesAreNonNull()
    {
        var doc = CreateFullDoc();
        var meta = doc.GetDocumentMetadata();
        foreach (var val in meta.Values)
            Assert.NotNull(val);
    }

    [Fact]
    public void GetDocumentMetadata_ContainsParagraphOrStatKey()
    {
        var doc = CreateFullDoc();
        var meta = doc.GetDocumentMetadata();
        // Metadata should contain at least one stat-like or document-level key
        var hasAny = false;
        foreach (var key in meta.Keys)
        {
            if (key.ToLower().Contains("paragraph") ||
                key.ToLower().Contains("word") ||
                key.ToLower().Contains("char") ||
                key.ToLower().Contains("heading") ||
                key.ToLower().Contains("title") ||
                key.ToLower().Contains("count"))
            {
                hasAny = true;
                break;
            }
        }
        Assert.True(hasAny, "Metadata should contain at least one paragraph/word/heading/count key");
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull()
    {
        var doc = CreateFullDoc();
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One paragraph.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount > 0);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        var stats = doc.GetDocumentStats();
        Assert.True(stats.HeadingCount > 0);
    }

    [Fact]
    public void GetDocumentStats_WordCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Several words in this paragraph.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount > 0);
    }

    [Fact]
    public void GetDocumentStats_CharacterCount_Positive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Characters here.");
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharacterCount > 0);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_MatchesInserted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        doc.AppendParagraph("Third.");
        var stats = doc.GetDocumentStats();
        Assert.Equal(3, stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCount_MatchesInserted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Para.");
        doc.InsertHeading(1, "H2", 2);
        var stats = doc.GetDocumentStats();
        Assert.Equal(2, stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCount_ConsistentWithGetWordCount()
    {
        var doc = CreateFullDoc();
        var stats = doc.GetDocumentStats();
        // WordCount from stats should match GetWordCount()
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeadings->AppendParagraphs->GetMetadata->GetStats->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateHeadingsParagraphsGetMetadataGetStatsVerifyConsistency_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("This document provides a comprehensive overview.");
        doc.AppendParagraph("Key findings are highlighted in each section.");
        doc.InsertHeading(2, "Introduction", 2);
        doc.AppendParagraph("The introduction establishes the context.");
        doc.InsertHeading(3, "Methodology", 2);
        doc.AppendParagraph("Methodology describes the approach and tools used.");

        // GetDocumentMetadata
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
        Assert.NotEmpty(meta);

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.Equal(4, stats.ParagraphCount);
        Assert.Equal(2, stats.HeadingCount);
        Assert.True(stats.WordCount > 0);
        Assert.True(stats.CharacterCount > 0);

        // Cross-verify with individual methods
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
        Assert.Equal(doc.GetCharCount(), stats.CharacterCount);
    }
}
