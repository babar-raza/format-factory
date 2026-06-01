// R86 Train G: FODS .NET exporter edge-case hardening tests
// Sprint: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR86ExporterHardeningTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsR86ExporterHardeningTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "fods-r86-hardening-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // === CSV EscapeCsvField Edge Cases ===

    [Fact]
    public void EscapeCsvField_TabCharacter_NotQuoted()
    {
        var result = FodsCsvExporter.EscapeCsvField("col1\tcol2");
        Assert.Equal("col1\tcol2", result);
    }

    [Fact]
    public void EscapeCsvField_OnlySpaces_ReturnedAsIs()
    {
        var result = FodsCsvExporter.EscapeCsvField("   ");
        Assert.Equal("   ", result);
    }

    [Fact]
    public void EscapeCsvField_MixedSpecialChars_ProperlyEscaped()
    {
        var result = FodsCsvExporter.EscapeCsvField("a,b\"c\nd");
        Assert.StartsWith("\"", result);
        Assert.EndsWith("\"", result);
        Assert.Contains("\"\"", result);
    }

    // === CSV Export Integration ===

    [Fact]
    public void CsvExport_MinimalFixture_ProducesFile()
    {
        var outPath = Path.Combine(_tempDir, "minimal.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, outPath);
        Assert.True(result.Status == "Success" || result.Status == "exported", $"Unexpected status: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    // === JSON Export Integration ===

    [Fact]
    public void JsonExport_MinimalFixture_ContainsFormatField()
    {
        var outPath = Path.Combine(_tempDir, "minimal.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outPath);
        Assert.True(result.Status == "Success" || result.Status == "exported", $"Unexpected status: {result.Status}");
        var json = File.ReadAllText(outPath);
        Assert.Contains("\"format\"", json);
        Assert.Contains("\"sheets\"", json);
    }

    [Fact]
    public void JsonExport_MinimalFixture_ContainsPrototypeFlag()
    {
        var outPath = Path.Combine(_tempDir, "proto.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outPath);
        Assert.True(result.Status == "Success" || result.Status == "exported", $"Unexpected status: {result.Status}");
        var json = File.ReadAllText(outPath);
        Assert.Contains("\"prototype\"", json);
    }

    // === HTML Export Integration ===

    [Fact]
    public void HtmlExport_MinimalFixture_ProducesValidHtml()
    {
        var outPath = Path.Combine(_tempDir, "minimal.html");
        var result = FodsHtmlExporter.ExportToHtml(MinimalFods, outPath);
        Assert.True(result.Status == "Success" || result.Status == "exported", $"Unexpected status: {result.Status}");
        var html = File.ReadAllText(outPath);
        Assert.Contains("<html", html);
        Assert.Contains("</html>", html);
    }

    [Fact]
    public void HtmlExport_MinimalFixture_HasTableElement()
    {
        var outPath = Path.Combine(_tempDir, "table.html");
        var result = FodsHtmlExporter.ExportToHtml(MinimalFods, outPath);
        Assert.True(result.Status == "Success" || result.Status == "exported", $"Unexpected status: {result.Status}");
        var html = File.ReadAllText(outPath);
        Assert.Contains("<table", html);
    }
}
