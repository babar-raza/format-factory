using FormatFactory.Fodt;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R115 Train A/B: ExportToOutlineJson + FindParagraphsByStyle — structured document pipeline.
/// </summary>
public class FodtR115ExportOutlineJsonTests
{
    private static FodtDocument MakeDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This is the first body paragraph.");
        doc.InsertHeading(2, "Methods", 2);
        doc.AppendParagraph("A description of methods used.");
        doc.InsertHeading(4, "Conclusion", 1);
        return doc;
    }

    [Fact]
    public void ExportToOutlineJson_ReturnsValidJson()
    {
        var doc = MakeDoc();
        var json = doc.ExportToOutlineJson();
        Assert.NotNull(json);
        // Must parse as valid JSON array
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(JsonValueKind.Array, arr.ValueKind);
    }

    [Fact]
    public void ExportToOutlineJson_ContainsExpectedParagraphCount()
    {
        var doc = MakeDoc();
        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(5, arr.GetArrayLength());
    }

    [Fact]
    public void ExportToOutlineJson_HeadingsHaveLevelGreaterThanZero()
    {
        var doc = MakeDoc();
        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        int headingsFound = 0;
        foreach (var elem in arr.EnumerateArray())
        {
            int level = elem.GetProperty("level").GetInt32();
            if (level > 0) headingsFound++;
        }
        Assert.True(headingsFound >= 2);
    }

    [Fact]
    public void ExportToOutlineJson_BodyParagraphsHaveLevelZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body text");
        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(0, arr[0].GetProperty("level").GetInt32());
    }

    [Fact]
    public void ExportToOutlineJson_EmptyDoc_ReturnsEmptyArray()
    {
        var doc = FodtDocument.CreateEmpty();
        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;
        Assert.Equal(0, arr.GetArrayLength());
    }

    [Fact]
    public void ExportToOutlineJson_ContainsIndexField()
    {
        var doc = MakeDoc();
        var arr = JsonDocument.Parse(doc.ExportToOutlineJson()).RootElement;
        for (int i = 0; i < arr.GetArrayLength(); i++)
            Assert.Equal(i, arr[i].GetProperty("index").GetInt32());
    }

    [Fact]
    public void FindParagraphsByStyle_HeadingStyle_ReturnHeadingIndices()
    {
        var doc = MakeDoc();
        var indices = doc.FindParagraphsByStyle("Heading");
        // InsertHeading creates text:h elements (outline-level based), matched as "Heading" synthetically
        Assert.True(indices.Count >= 2, $"Expected >= 2 heading indices but got {indices.Count}");
        // All returned indices should be for non-body paragraphs (the outline JSON level > 0)
        var json = doc.ExportToOutlineJson();
        var arr = System.Text.Json.JsonDocument.Parse(json).RootElement;
        foreach (var idx in indices)
            Assert.True(arr[idx].GetProperty("level").GetInt32() > 0,
                $"Index {idx} expected heading level > 0");
    }

    [Fact]
    public void FindParagraphsByStyle_NoMatch_ReturnsEmpty()
    {
        var doc = MakeDoc();
        var result = doc.FindParagraphsByStyle("XYZ_NONEXISTENT");
        Assert.Empty(result);
    }

    [Fact]
    public void FindParagraphsByStyle_CaseInsensitive_Finds()
    {
        var doc = MakeDoc();
        var upper = doc.FindParagraphsByStyle("HEADING");
        var lower = doc.FindParagraphsByStyle("heading");
        Assert.Equal(upper.Count, lower.Count);
    }

    [Fact]
    public void ExportToOutlineJson_DogfoodPipeline_HeadingsExtractable()
    {
        // Dogfood: build doc → export outline JSON → extract headings programmatically
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.AppendParagraph("Body text here.");
        doc.InsertHeading(2, "Section 1.1", 2);

        var json = doc.ExportToOutlineJson();
        var arr = JsonDocument.Parse(json).RootElement;

        var headings = arr.EnumerateArray()
            .Where(e => e.GetProperty("level").GetInt32() > 0)
            .Select(e => e.GetProperty("text").GetString())
            .ToList();

        Assert.Contains("Chapter 1", headings);
        Assert.Contains("Section 1.1", headings);
        Assert.DoesNotContain("Body text here.", headings);
    }
}
