// Tests for FodtDocument.ExportToOutlineJson dedicated coverage.
// Sprint: ff-sprint-s148-dotnet-deepening-20260628
// Ledger: PC-FODT-R158

using System.Text.Json;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R158: Dedicated tests for FodtDocument.ExportToOutlineJson.
/// ExportToOutlineJson returns a JSON array string where each element has
/// "index", "style", "level", and "text" fields.
/// Heading elements get level from text:outline-level; body paragraphs get level=0.
/// Covers: empty doc returns "[]"; single paragraph has index=0; paragraph level=0;
/// heading has level>0; JSON is valid parseable array; multiple entries count correct;
/// index field sequential; text field matches paragraph text; headings and paragraphs mixed;
/// dogfood AppendHeading+AppendParagraph pipeline; dogfood JSON has "text" keys.
/// </summary>
public class FodtR158ExportToOutlineJsonTests
{
    // -------------------------------------------------------------------------
    // Empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_EmptyDocument_ReturnsEmptyArray()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        var trimmed = json.Trim();
        Assert.StartsWith("[", trimmed);
        Assert.EndsWith("]", trimmed);
    }

    // -------------------------------------------------------------------------
    // Single paragraph
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_SingleParagraph_IndexIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.Equal(0, parsed.RootElement[0].GetProperty("index").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_SingleParagraph_LevelIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text.");
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.Equal(0, parsed.RootElement[0].GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_SingleParagraph_TextMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World.");
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.Equal("Hello World.", parsed.RootElement[0].GetProperty("text").GetString());
    }

    // -------------------------------------------------------------------------
    // Heading
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_SingleHeading_LevelGreaterThanZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.True(parsed.RootElement[0].GetProperty("level").GetInt32() > 0);
    }

    // -------------------------------------------------------------------------
    // Multiple entries
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_MultipleEntries_CountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body.");
        doc.AppendHeading("Section", 2);
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.Equal(3, parsed.RootElement.GetArrayLength());
    }

    [Fact]
    public void ExportToOutlineJson_MultipleEntries_IndexSequential()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P0");
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        var arr = parsed.RootElement;
        Assert.Equal(0, arr[0].GetProperty("index").GetInt32());
        Assert.Equal(1, arr[1].GetProperty("index").GetInt32());
        Assert.Equal(2, arr[2].GetProperty("index").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_ValidJson_CanBeParsed()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendParagraph("Body text here.");
        var json = doc.ExportToOutlineJson();
        var ex = Record.Exception(() => JsonDocument.Parse(json));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeadingsAndParagraphs_AllHaveTextKey()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Executive Summary", 1);
        doc.AppendParagraph("Summary content.");
        doc.AppendHeading("Findings", 2);
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        Assert.All(parsed.RootElement.EnumerateArray(), entry =>
        {
            Assert.True(entry.TryGetProperty("text", out _));
        });
    }

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraph_HeadingLevelNonZero_ParagraphLevelZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 2);
        doc.AppendParagraph("Body.");
        var json = doc.ExportToOutlineJson();
        using var parsed = JsonDocument.Parse(json);
        var arr = parsed.RootElement;
        Assert.True(arr[0].GetProperty("level").GetInt32() > 0);
        Assert.Equal(0, arr[1].GetProperty("level").GetInt32());
    }
}
