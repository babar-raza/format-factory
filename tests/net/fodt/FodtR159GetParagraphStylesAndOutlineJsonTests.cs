// Tests for FodtDocument.GetParagraphStyles and ExportToOutlineJson.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R159

using System.Text.Json;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R159: Tests for FodtDocument.GetParagraphStyles and ExportToOutlineJson.
/// GetParagraphStyles returns a list of style-name strings for each paragraph
/// (empty string when no style-name attribute is set).
/// ExportToOutlineJson serializes the document outline to a JSON array;
/// each entry includes "index", "style", "level", "text" fields;
/// heading paragraphs have level > 0; body paragraphs have level = 0.
/// Covers: GetParagraphStyles empty doc returns empty list; count matches ParagraphCount;
/// ExportToOutlineJson empty doc returns valid JSON array;
/// ExportToOutlineJson single heading produces level > 0;
/// body paragraph produces level 0; JSON is parseable;
/// all entries have required fields; text content appears in JSON;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->ExportToOutlineJson pipeline.
/// </summary>
public class FodtR159GetParagraphStylesAndOutlineJsonTests
{
    // -------------------------------------------------------------------------
    // GetParagraphStyles
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphStyles_EmptyDoc_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetParagraphStyles());
    }

    [Fact]
    public void GetParagraphStyles_CountMatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One.");
        doc.AppendParagraph("Two.");
        doc.InsertHeading(2, "Section", 1);
        var styles = doc.GetParagraphStyles();
        Assert.Equal(doc.ParagraphCount, styles.Count);
    }

    [Fact]
    public void GetParagraphStyles_ReturnsStringForEachParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text.");
        var styles = doc.GetParagraphStyles();
        // Each element should be a string (null or empty = empty string per implementation)
        Assert.Single(styles);
        Assert.NotNull(styles[0]);
    }

    // -------------------------------------------------------------------------
    // ExportToOutlineJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOutlineJson_EmptyDoc_ReturnsEmptyArray()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        var parsed = JsonDocument.Parse(json);
        Assert.Equal(JsonValueKind.Array, parsed.RootElement.ValueKind);
        Assert.Equal(0, parsed.RootElement.GetArrayLength());
    }

    [Fact]
    public void ExportToOutlineJson_IsValidJson()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Body text here.");
        var json = doc.ExportToOutlineJson();
        // Should not throw
        var parsed = JsonDocument.Parse(json);
        Assert.Equal(JsonValueKind.Array, parsed.RootElement.ValueKind);
    }

    [Fact]
    public void ExportToOutlineJson_EntryCount_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("Para.");
        doc.InsertHeading(2, "H2", 2);
        var json = doc.ExportToOutlineJson();
        var parsed = JsonDocument.Parse(json);
        Assert.Equal(doc.ParagraphCount, parsed.RootElement.GetArrayLength());
    }

    [Fact]
    public void ExportToOutlineJson_HeadingEntry_HasLevelGreaterThanZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        var json = doc.ExportToOutlineJson();
        var entries = JsonDocument.Parse(json).RootElement;
        bool foundHeadingWithLevel = false;
        foreach (var entry in entries.EnumerateArray())
        {
            if (entry.GetProperty("level").GetInt32() > 0)
                foundHeadingWithLevel = true;
        }
        Assert.True(foundHeadingWithLevel, "Expected at least one heading entry with level > 0.");
    }

    [Fact]
    public void ExportToOutlineJson_BodyParagraph_HasLevelZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just a body paragraph.");
        var json = doc.ExportToOutlineJson();
        var entry = JsonDocument.Parse(json).RootElement[0];
        Assert.Equal(0, entry.GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_EntryHasRequiredFields()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sample.");
        var json = doc.ExportToOutlineJson();
        var entry = JsonDocument.Parse(json).RootElement[0];
        Assert.True(entry.TryGetProperty("index", out _), "Missing 'index' field.");
        Assert.True(entry.TryGetProperty("style", out _), "Missing 'style' field.");
        Assert.True(entry.TryGetProperty("level", out _), "Missing 'level' field.");
        Assert.True(entry.TryGetProperty("text", out _), "Missing 'text' field.");
    }

    [Fact]
    public void ExportToOutlineJson_TextContent_AppearsInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique content XYZ-123.");
        var json = doc.ExportToOutlineJson();
        Assert.Contains("Unique content XYZ-123", json);
    }

    // -------------------------------------------------------------------------
    // Dogfood: full pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInsertHeadingAppendParagraph_OutlineJsonPipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("This document covers key metrics.");
        doc.InsertHeading(2, "Results", 2);
        doc.AppendParagraph("All targets met.");

        Assert.Equal(4, doc.ParagraphCount);

        var json = doc.ExportToOutlineJson();
        var entries = JsonDocument.Parse(json).RootElement;
        Assert.Equal(4, entries.GetArrayLength());

        // Verify first entry is heading with level 1
        var first = entries[0];
        Assert.Equal(1, first.GetProperty("level").GetInt32());
        Assert.Contains("Executive Summary", first.GetProperty("text").GetString()!);

        // Verify body paragraph has level 0
        var body = entries[1];
        Assert.Equal(0, body.GetProperty("level").GetInt32());
    }
}
