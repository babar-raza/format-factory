// Tests for FodtDocument.ExportToOutlineJson()
// Sprint: FORMAT-FACTORY-FODT-OUTLINE-JSON-20260626
// Ledger: R119-GOVERNED-DOTNET-FODT-OUTLINE-JSON-001

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R119: ExportToOutlineJson() — exports document structure as JSON array.
/// Each entry has index, style, level, text. Heading level comes from text:outline-level.
/// Extends R115 with edge cases: empty doc, JSON validity, multi-level headings,
/// mixed paragraphs, and structural properties of the output.
/// </summary>
public class FodtR119ExportToOutlineJsonTests
{
    // ---- Empty document ----

    [Fact]
    public void ExportToOutlineJson_EmptyDoc_ReturnsEmptyArray()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        Assert.Equal("[]", json.Trim());
    }

    // ---- JSON validity ----

    [Fact]
    public void ExportToOutlineJson_NonEmptyDoc_ProducesValidJson()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("Some body text.");

        var json = doc.ExportToOutlineJson();

        // Must parse without exception
        var doc2 = JsonDocument.Parse(json);
        Assert.Equal(JsonValueKind.Array, doc2.RootElement.ValueKind);
    }

    // ---- Entry count matches paragraph count ----

    [Fact]
    public void ExportToOutlineJson_EntryCount_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.AppendParagraph("Body.");
        doc.InsertHeading(2, "Section", 2);
        doc.AppendParagraph("More body.");

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(doc.GetParagraphCount(), arr.GetArrayLength());
    }

    // ---- Required fields present ----

    [Fact]
    public void ExportToOutlineJson_EachEntry_HasIndexStyleLevelText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        doc.AppendParagraph("Content here.");

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;

        foreach (var element in arr.EnumerateArray())
        {
            Assert.True(element.TryGetProperty("index", out _), "Missing 'index'");
            Assert.True(element.TryGetProperty("style", out _), "Missing 'style'");
            Assert.True(element.TryGetProperty("level", out _), "Missing 'level'");
            Assert.True(element.TryGetProperty("text", out _), "Missing 'text'");
        }
    }

    // ---- Index field is sequential ----

    [Fact]
    public void ExportToOutlineJson_IndexField_IsSequential()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 0");
        doc.InsertHeading(1, "Heading 1", 1);
        doc.AppendParagraph("Para 2");

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;

        int idx = 0;
        foreach (var element in arr.EnumerateArray())
        {
            Assert.Equal(idx, element.GetProperty("index").GetInt32());
            idx++;
        }
    }

    // ---- Level field for headings ----

    [Fact]
    public void ExportToOutlineJson_H1_LevelIsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Top Level Heading", 1);

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        var first = arr[0];
        Assert.Equal(1, first.GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_H2_LevelIsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sub Heading", 2);

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(2, arr[0].GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_BodyParagraph_LevelIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text, not a heading.");

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(0, arr[0].GetProperty("level").GetInt32());
    }

    // ---- Text field ----

    [Fact]
    public void ExportToOutlineJson_TextField_MatchesParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph content here.");
        doc.InsertHeading(1, "Heading Text", 1);

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;

        Assert.Equal("Paragraph content here.", arr[0].GetProperty("text").GetString());
        Assert.Equal("Heading Text", arr[1].GetProperty("text").GetString());
    }

    // ---- Special characters in JSON ----

    [Fact]
    public void ExportToOutlineJson_SpecialCharacters_ProperlyEscaped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text with \"quotes\" and \\backslashes\\");

        var json = doc.ExportToOutlineJson();

        // Must produce parseable JSON despite special chars
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(1, arr.GetArrayLength());
        // The text should survive round-trip
        var text = arr[0].GetProperty("text").GetString();
        Assert.Contains("quotes", text!);
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_BuildDocument_ExportOutline_VerifyStructure()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("Overview of the report.");
        doc.InsertHeading(2, "Background", 2);
        doc.AppendParagraph("Historical context.");
        doc.InsertHeading(4, "Methodology", 2);
        doc.AppendParagraph("How the data was collected.");

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;

        Assert.Equal(6, arr.GetArrayLength());

        // H1 at index 0
        Assert.Equal(1, arr[0].GetProperty("level").GetInt32());
        Assert.Equal("Executive Summary", arr[0].GetProperty("text").GetString());

        // H2 at index 2
        Assert.Equal(2, arr[2].GetProperty("level").GetInt32());
        Assert.Equal("Background", arr[2].GetProperty("text").GetString());

        // Body paragraph at index 1 has level 0
        Assert.Equal(0, arr[1].GetProperty("level").GetInt32());
    }
}
