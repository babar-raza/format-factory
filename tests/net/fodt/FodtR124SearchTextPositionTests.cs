// Tests for FodtDocument.SearchText(query, comparison) returning (ParagraphIndex, Position) tuples.
// Sprint: FORMAT-FACTORY-FODT-SEARCH-POSITION-20260626
// Ledger: R124-GOVERNED-DOTNET-FODT-SEARCH-POSITION-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R124: SearchText(query, comparison) returns List of (ParagraphIndex, Position) tuples.
/// Tests verify tuple structure, ParagraphIndex accuracy, character Position accuracy,
/// multiple matches per paragraph, cross-paragraph results, and case comparison behavior.
/// </summary>
public class FodtR124SearchTextPositionTests
{
    // ---- Returns empty list when no match ----

    [Fact]
    public void SearchText_NoMatch_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        var results = doc.SearchText("zzz");
        Assert.Empty(results);
    }

    // ---- Single match: correct ParagraphIndex and Position ----

    [Fact]
    public void SearchText_SingleMatch_CorrectParagraphIndex()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta target here");

        var results = doc.SearchText("target");
        Assert.Single(results);
        Assert.Equal(1, results[0].ParagraphIndex); // second paragraph = index 1
    }

    [Fact]
    public void SearchText_SingleMatch_CorrectPosition()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        var results = doc.SearchText("world");
        Assert.Single(results);
        Assert.Equal(6, results[0].Position); // "world" starts at index 6
    }

    // ---- First paragraph: ParagraphIndex = 0 ----

    [Fact]
    public void SearchText_FirstParagraph_ParagraphIndexZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("match here");

        var results = doc.SearchText("match");
        Assert.Single(results);
        Assert.Equal(0, results[0].ParagraphIndex);
        Assert.Equal(0, results[0].Position);
    }

    // ---- Multiple matches in one paragraph ----

    [Fact]
    public void SearchText_MultiplInParagraph_AllFound()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("cat sat on the cat mat");

        var results = doc.SearchText("cat");
        Assert.Equal(2, results.Count);
        Assert.All(results, r => Assert.Equal(0, r.ParagraphIndex));
    }

    [Fact]
    public void SearchText_MultipleInParagraph_PositionsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        // "ab" at positions 0 and 3
        doc.AppendParagraph("ab-ab");

        var results = doc.SearchText("ab");
        Assert.Equal(2, results.Count);
        Assert.Equal(0, results[0].Position);
        Assert.Equal(3, results[1].Position);
    }

    // ---- Multiple paragraphs: indices reflect para order ----

    [Fact]
    public void SearchText_AcrossParagraphs_IndicesDistinct()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("first fox here");
        doc.AppendParagraph("no match");
        doc.AppendParagraph("fox again");

        var results = doc.SearchText("fox");
        Assert.Equal(2, results.Count);
        Assert.Equal(0, results[0].ParagraphIndex);
        Assert.Equal(2, results[1].ParagraphIndex);
    }

    // ---- Case-sensitive (Ordinal): only exact case ----

    [Fact]
    public void SearchText_Ordinal_CaseSensitive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fox fox FOX");

        var results = doc.SearchText("fox", StringComparison.Ordinal);
        // Only lowercase "fox" matches
        Assert.Single(results);
    }

    // ---- Case-insensitive (OrdinalIgnoreCase) ----

    [Fact]
    public void SearchText_OrdinalIgnoreCase_AllVariants()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fox fox FOX");

        var results = doc.SearchText("fox", StringComparison.OrdinalIgnoreCase);
        Assert.Equal(3, results.Count);
    }

    // ---- Dogfood: results drive SetParagraphText replacement ----

    [Fact]
    public void DogfoodPipeline_SearchThenSetParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original text with keyword");
        doc.AppendParagraph("No match here"); // must not contain "keyword" substring
        doc.AppendParagraph("Another keyword line");

        var results = doc.SearchText("keyword");
        // Paragraphs with keyword: indices 0 and 2
        var paraIndices = results.Select(r => r.ParagraphIndex).Distinct().ToList();

        Assert.Contains(0, paraIndices);
        Assert.Contains(2, paraIndices);
        Assert.DoesNotContain(1, paraIndices);

        // Replace text in found paragraphs
        foreach (var idx in paraIndices)
        {
            var oldText = doc.GetParagraphText(idx) ?? "";
            doc.SetParagraphText(idx, oldText.Replace("keyword", "FOUND"));
        }

        Assert.Contains("FOUND", doc.GetParagraphText(0) ?? "");
        Assert.Contains("FOUND", doc.GetParagraphText(2) ?? "");
        Assert.DoesNotContain("FOUND", doc.GetParagraphText(1) ?? "");
    }
}
