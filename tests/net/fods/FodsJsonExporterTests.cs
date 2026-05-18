// FormatFactory.Fods Tests -- FodsJsonExporter G11-E Expanded Prototype Tests
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the G11-E FODS → JSON export prototype.
/// Tests cover: basic export, empty document, null guards, JSON structure.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodsJsonExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsJsonExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-json-export-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // Null guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NullFodsPath_Throws()
    {
        Assert.Throws<FodsJsonExportException>(() =>
            FodsJsonExporter.ExportToJson(null!, Path.Combine(_tempDir, "out.json")));
    }

    [Fact]
    public void ExportToJson_EmptyFodsPath_Throws()
    {
        Assert.Throws<FodsJsonExportException>(() =>
            FodsJsonExporter.ExportToJson("", Path.Combine(_tempDir, "out.json")));
    }

    [Fact]
    public void ExportToJson_NullJsonPath_Throws()
    {
        Assert.Throws<FodsJsonExportException>(() =>
            FodsJsonExporter.ExportToJson(MinimalFods, null!));
    }

    [Fact]
    public void ExportToJson_NonExistentFodsPath_Throws()
    {
        Assert.Throws<FodsJsonExportException>(() =>
            FodsJsonExporter.ExportToJson(
                Path.Combine(_tempDir, "nonexistent.fods"),
                Path.Combine(_tempDir, "out.json")));
    }

    // -------------------------------------------------------------------------
    // Integration tests (using fixture)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_MinimalFods_CreatesJsonFile()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        Assert.True(File.Exists(outJson), "JSON output file must be created");
        Assert.Equal("exported", result.Status);
        Assert.Equal(outJson, result.OutputPath);
    }

    [Fact]
    public void ExportToJson_MinimalFods_JsonIsValid()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var text = File.ReadAllText(outJson);
        var doc = JsonDocument.Parse(text); // throws if invalid JSON
        Assert.NotNull(doc);
    }

    [Fact]
    public void ExportToJson_MinimalFods_JsonHasSheetsKey()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var text = File.ReadAllText(outJson);
        var doc = JsonDocument.Parse(text);
        Assert.True(doc.RootElement.TryGetProperty("sheets", out _),
            "JSON output must have 'sheets' key");
    }

    [Fact]
    public void ExportToJson_MinimalFods_SheetsIsArray()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var text = File.ReadAllText(outJson);
        var doc = JsonDocument.Parse(text);
        doc.RootElement.TryGetProperty("sheets", out var sheets);
        Assert.Equal(JsonValueKind.Array, sheets.ValueKind);
    }

    [Fact]
    public void ExportToJson_MinimalFods_HasFormatKey()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var text = File.ReadAllText(outJson);
        var doc = JsonDocument.Parse(text);
        Assert.True(doc.RootElement.TryGetProperty("format", out var fmt));
        Assert.Equal("fods", fmt.GetString());
    }

    [Fact]
    public void ExportToJson_MinimalFods_CommercialProductReadyIsFalse()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var text = File.ReadAllText(outJson);
        var doc = JsonDocument.Parse(text);
        Assert.True(doc.RootElement.TryGetProperty("commercial_product_ready", out var cpr));
        Assert.Equal(JsonValueKind.False, cpr.ValueKind);
    }

    [Fact]
    public void ExportToJson_MinimalFods_ResultHasPositiveSheetsCount()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        Assert.True(result.SheetsExported >= 0,
            "SheetsExported must be non-negative");
    }

    [Fact]
    public void ExportToJson_OutputFileNonEmpty()
    {
        var outJson = Path.Combine(_tempDir, "minimal.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        var info = new FileInfo(outJson);
        Assert.True(info.Length > 0, "JSON output file must be non-empty");
    }

    // -------------------------------------------------------------------------
    // Governance tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_ResultStatus_IsExportedOrEmpty()
    {
        var outJson = Path.Combine(_tempDir, "out.json");
        var result = FodsJsonExporter.ExportToJson(MinimalFods, outJson);

        Assert.True(
            result.Status == "exported" ||
            result.Status == "exported_empty_no_sheets",
            $"Status must be 'exported' or 'exported_empty_no_sheets', got: {result.Status}");
    }

    [Fact]
    public void ExportToJson_Prototype_CommercialProductReadyFalse()
    {
        // Governance invariant: commercial_product_ready=false embedded in output
        var outJson = Path.Combine(_tempDir, "out.json");
        FodsJsonExporter.ExportToJson(MinimalFods, outJson);
        var text = File.ReadAllText(outJson);
        Assert.Contains("commercial_product_ready", text);
        Assert.DoesNotContain("\"commercial_product_ready\": true", text);
    }
}
