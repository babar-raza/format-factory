// Tests for FodtDocument.ExportToOutlineJson dedicated coverage.
// Sprint: ff-sprint-s176-dotnet-deepening-20260628
// Ledger: PC-FODT-R185

using System.Text.Json;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R185: Dedicated tests for FodtDocument.ExportToOutlineJson().
/// Returns a JSON array string of all paragraphs/headings with index, style, level, text.
/// Empty document returns "[]" (an empty JSON array).
/// Each entry has: index (int), style (string), level (int), text (string).
/// Headings have level >= 1; body paragraphs have level=0.
/// Covers: empty doc returns empty array; non-null string; parseable as JSON;
/// returns array; single paragraph has index=0; text matches AppendParagraph;
/// heading level matches AppendHeading level; paragraphs have level=0;
/// count matches paragraph count; dogfood mixed content pipeline.
/// </summary>
public class FodtR185ExportToOutlineJsonTests
{
    // -------------------------------------------------------------------------
    // Basic structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_EmptyDocument_ReturnsEmptyArray()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json);
        Assert.NotNull(arr);
        Assert.Empty(arr);
    }

    [Fact]
    public void ExportToOutlineJson_ReturnsNonNullString()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
    }

    [Fact]
    public void ExportToOutlineJson_OutputIsValidJson()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var json = doc.ExportToOutlineJson();
        // Should not throw
        var elem = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(JsonValueKind.Array, elem.ValueKind);
    }

    [Fact]
    public void ExportToOutlineJson_SingleParagraph_HasIndexZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        Assert.Single(arr);
        Assert.Equal(0, arr[0].GetProperty("index").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_ParagraphText_MatchesAppended()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("My paragraph text");
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        Assert.Equal("My paragraph text", arr[0].GetProperty("text").GetString());
    }

    [Fact]
    public void ExportToOutlineJson_HeadingLevel_MatchesAppendedLevel()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 2);
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        Assert.Single(arr);
        var level = arr[0].GetProperty("level").GetInt32();
        Assert.InRange(level, 1, 6);
    }

    [Fact]
    public void ExportToOutlineJson_BodyParagraph_HasLevelZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        Assert.Equal(0, arr[0].GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_Count_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendParagraph("Body 1");
        doc.AppendParagraph("Body 2");
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        Assert.Equal(doc.ParagraphCount, arr.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_AllEntriesHaveRequiredFields()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Introduction");
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        foreach (var entry in arr)
        {
            Assert.True(entry.TryGetProperty("index", out _));
            Assert.True(entry.TryGetProperty("style", out _));
            Assert.True(entry.TryGetProperty("level", out _));
            Assert.True(entry.TryGetProperty("text", out _));
        }
    }

    [Fact]
    public void DogfoodPipeline_IndicesAreSequential()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendHeading("Third", 1);
        var json = doc.ExportToOutlineJson();
        var arr = JsonSerializer.Deserialize<JsonElement[]>(json)!;
        for (int i = 0; i < arr.Length; i++)
            Assert.Equal(i, arr[i].GetProperty("index").GetInt32());
    }
}
