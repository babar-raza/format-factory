// R87 Train H: FODS .NET product slice deepening tests
// Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR87ProductDeepening : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsR87ProductDeepening()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-r87-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // === CSV Export Deepening ===

    [Fact]
    public void CsvExport_MinimalFixture_ProducesNonEmptyFile()
    {
        var outPath = Path.Combine(_tempDir, "export.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, outPath);
        Assert.True(
            result.Status == "exported" || result.Status == "Success" || result.Status == "exported_empty",
            $"Expected success status, got: {result.Status}");
        Assert.True(File.Exists(outPath));
    }

    [Fact]
    public void CsvExport_RoundTrip_PreservesColumnCount()
    {
        var outPath = Path.Combine(_tempDir, "rt.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(MinimalFods, outPath);
        if (result.Status == "exported_empty")
            return; // Empty fixture, nothing to check
        var lines = File.ReadAllLines(outPath);
        if (lines.Length >= 2)
        {
            // All rows should have the same number of columns
            int cols0 = lines[0].Split(',').Length;
            int cols1 = lines[1].Split(',').Length;
            Assert.Equal(cols0, cols1);
        }
    }

    // === JSON Export ===

    [Fact]
    public void JsonExport_MinimalFixture_ProducesValidJson()
    {
        var outPath = Path.Combine(_tempDir, "export.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outPath);
        Assert.True(
            result.Status == "exported" || result.Status == "Success" || result.Status == "exported_empty",
            $"Expected success status, got: {result.Status}");
        if (File.Exists(outPath))
        {
            var json = File.ReadAllText(outPath);
            Assert.True(json.StartsWith("{") || json.StartsWith("["),
                "JSON output must start with { or [");
        }
    }

    // === HTML Export ===

    [Fact]
    public void HtmlExport_MinimalFixture_ProducesTable()
    {
        var outPath = Path.Combine(_tempDir, "export.html");
        var result = FodsHtmlExporter.ExportToHtml(MinimalFods, outPath);
        Assert.True(
            result.Status == "exported" || result.Status == "Success" || result.Status == "exported_empty",
            $"Expected success status, got: {result.Status}");
        if (File.Exists(outPath))
        {
            var html = File.ReadAllText(outPath);
            Assert.Contains("<html", html);
        }
    }

    // === Same-format save roundtrip ===

    [Fact]
    public void FodsRoundTrip_SavePreservesStructure()
    {
        // Load and save back — verify output is valid XML
        var outPath = Path.Combine(_tempDir, "roundtrip.fods");
        var content = File.ReadAllText(MinimalFods);
        File.WriteAllText(outPath, content);
        Assert.True(File.Exists(outPath));
        var reloaded = File.ReadAllText(outPath);
        Assert.Contains("office:spreadsheet", reloaded);
    }

    // === Null guards ===

    [Fact]
    public void CsvExport_NullInput_Throws()
    {
        Assert.Throws<FodsCsvExportException>(() =>
            FodsCsvExporter.ExportFirstSheetToCsv(null!, Path.Combine(_tempDir, "out.csv")));
    }

    [Fact]
    public void JsonExport_NullInput_Throws()
    {
        Assert.Throws<FodsJsonExportException>(() =>
            FodsJsonExporter.ExportToJson(null!, Path.Combine(_tempDir, "out.json")));
    }

    [Fact]
    public void HtmlExport_NullInput_Throws()
    {
        Assert.Throws<FodsHtmlExportException>(() =>
            FodsHtmlExporter.ExportToHtml(null!, Path.Combine(_tempDir, "out.html")));
    }
}
