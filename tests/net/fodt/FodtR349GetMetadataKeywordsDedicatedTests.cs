// Tests for FodtDocument.GetMetadataKeywords dedicated coverage.
// Sprint: ff-sprint-s331-dotnet-deepening-20260630
// Ledger: PC-FODT-R349

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R349: Dedicated tests for FodtDocument.GetMetadataKeywords().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataKeywords.
/// TableCount unchanged after GetMetadataKeywords.
/// SectionCount unchanged after GetMetadataKeywords.
/// Idempotent (called twice same result).
/// After SetKeywords returns correct keywords.
/// Dogfood: document with keywords and content returns non-null.
/// Dogfood: keywords unchanged after AddParagraph.
/// </summary>
public class FodtR349GetMetadataKeywordsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataKeywords_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataKeywords());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataKeywords_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? keywords = doc.GetMetadataKeywords();
        Assert.NotNull(keywords);
    }

    [Fact]
    public void GetMetadataKeywords_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataKeywords();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataKeywords_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body");
        int before = doc.TableCount;
        _ = doc.GetMetadataKeywords();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataKeywords_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body");
        int before = doc.SectionCount;
        _ = doc.GetMetadataKeywords();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataKeywords_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetKeywords("analysis, report, quarterly");
        string? first = doc.GetMetadataKeywords();
        string? second = doc.GetMetadataKeywords();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataKeywords_AfterSetKeywords_ReturnsKeywords()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetKeywords("finance, budget, 2026");
        string? keywords = doc.GetMetadataKeywords();
        Assert.NotNull(keywords);
        Assert.Equal("finance, budget, 2026", keywords);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithKeywordsAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetKeywords("strategy, planning, roadmap");
        doc.SetTitle("Strategic Plan");
        doc.AddParagraph("This document outlines the strategic plan for the year.");
        string? keywords = doc.GetMetadataKeywords();
        Assert.NotNull(keywords);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_KeywordsUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetKeywords("original, keywords, here");
        string? keywordsBefore = doc.GetMetadataKeywords();
        doc.AddParagraph("New paragraph does not affect keywords");
        string? keywordsAfter = doc.GetMetadataKeywords();
        Assert.Equal(keywordsBefore, keywordsAfter);
    }
}
