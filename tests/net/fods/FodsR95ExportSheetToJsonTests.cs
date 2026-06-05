// R95 Train L: FODS .NET ExportSheetToJson Tests
// Governed skill: /add-dotnet-api
// Ledger: R95-GOVERNED-DOTNET-FODS-EXPORTSHEETTOJSON-001
// Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR95ExportSheetToJsonTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void ExportSheetToJson_ReturnsNonEmptyString()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var json = doc.ExportSheetToJson();
        Assert.False(string.IsNullOrWhiteSpace(json));
    }

    [Fact]
    public void ExportSheetToJson_ContainsArrayBrackets()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var json = doc.ExportSheetToJson();
        Assert.Contains("[", json);
        Assert.Contains("]", json);
    }

    [Fact]
    public void ExportSheetToJson_ContainsObjectBraces()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        var json = doc.ExportSheetToJson();
        Assert.Contains("{", json);
        Assert.Contains("}", json);
    }

    [Fact]
    public void ExportSheetToJson_ByName_Works()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        var names = doc.GetSheetNames();
        Assert.True(names.Count > 0);
        var json = doc.ExportSheetToJson(names[0]);
        Assert.False(string.IsNullOrWhiteSpace(json));
    }

    [Fact]
    public void ExportSheetToJson_InvalidSheet_Throws()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToJson("NoSuchSheet"));
    }

    [Fact]
    public void ExportSheetToJson_NullSheet_Throws()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.ExportSheetToJson(null!));
    }

    [Fact]
    public void ExportSheetToJson_UsesHeadersAsKeys()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        var headers = doc.GetColumnHeaders();
        var json = doc.ExportSheetToJson();
        if (headers.Count > 0)
        {
            Assert.Contains($"\"{headers[0]}\"", json);
        }
    }

    [Fact]
    public void ExportSheetToJson_IsValidJsonStructure()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var json = doc.ExportSheetToJson().Trim();
        Assert.StartsWith("[", json);
        Assert.EndsWith("]", json);
    }
}
