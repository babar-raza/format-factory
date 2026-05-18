// FormatFactory.Fods Tests -- Multi-Sheet Export Hardening (G11-E Expanded Prototype)
// Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
// Gate 11 status: commercial_readiness_in_progress — G11-G NOT approved
// commercial_product_ready: false
//
// Hardening test: verifies multi-sheet FODS export via JSON and HTML exporters.
// Tests prototype-level behaviour only — no commercial readiness claim.

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// G11-E hardening: multi-sheet export tests.
/// Validates JSON and HTML exporters handle documents with 2+ sheets correctly.
/// Prototype status — no commercial readiness claim.
/// </summary>
public class FodsMultiSheetHardeningTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MultiSheetFods =
        Path.Combine(FixturesDir, "fods-multi-sheet.fods");

    private readonly string _tempDir;

    public FodsMultiSheetHardeningTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-multisheet-hardening-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string ExportJson()
    {
        var outPath = Path.Combine(_tempDir, "multi.json");
        FodsJsonExporter.ExportToJson(MultiSheetFods, outPath);
        return File.ReadAllText(outPath);
    }

    private string ExportHtml()
    {
        var outPath = Path.Combine(_tempDir, "multi.html");
        FodsHtmlExporter.ExportToHtml(MultiSheetFods, outPath);
        return File.ReadAllText(outPath);
    }

    [Fact]
    public void JsonExporter_MultiSheet_ProducesCorrectSheetCount()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var sheets = root.RootElement.GetProperty("sheets");
        Assert.Equal(2, sheets.GetArrayLength());
    }

    [Fact]
    public void JsonExporter_MultiSheet_FirstSheetNameIsSummary()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var firstSheet = root.RootElement.GetProperty("sheets")[0];
        Assert.Equal("Summary", firstSheet.GetProperty("name").GetString());
    }

    [Fact]
    public void JsonExporter_MultiSheet_SecondSheetNameIsDetails()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var secondSheet = root.RootElement.GetProperty("sheets")[1];
        Assert.Equal("Details", secondSheet.GetProperty("name").GetString());
    }

    [Fact]
    public void JsonExporter_MultiSheet_SummarySheetHasTwoRows()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var summaryRows = root.RootElement.GetProperty("sheets")[0].GetProperty("rows");
        Assert.Equal(2, summaryRows.GetArrayLength());
    }

    [Fact]
    public void JsonExporter_MultiSheet_DetailsSheetHasThreeRows()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var detailsRows = root.RootElement.GetProperty("sheets")[1].GetProperty("rows");
        Assert.Equal(3, detailsRows.GetArrayLength());
    }

    [Fact]
    public void JsonExporter_MultiSheet_TotalCellIsFortyTwo()
    {
        var json = ExportJson();
        using var root = JsonDocument.Parse(json);
        var summaryRows = root.RootElement.GetProperty("sheets")[0].GetProperty("rows");
        var dataRow = summaryRows[1];
        var totalCell = dataRow[1];
        Assert.Equal("42", totalCell.GetString());
    }

    [Fact]
    public void HtmlExporter_MultiSheet_ContainsBothSheetNames()
    {
        var html = ExportHtml();
        Assert.Contains("Summary", html);
        Assert.Contains("Details", html);
    }

    [Fact]
    public void HtmlExporter_MultiSheet_ContainsWidgetContent()
    {
        var html = ExportHtml();
        Assert.Contains("Widget A", html);
        Assert.Contains("WB-002", html);
    }

    [Fact]
    public void JsonExporter_MultiSheet_ResultStatusIsSuccess()
    {
        var outPath = Path.Combine(_tempDir, "multi2.json");
        var result = FodsJsonExporter.ExportToJson(MultiSheetFods, outPath);
        Assert.Equal("exported", result.Status);
    }

    [Fact]
    public void JsonExporter_MultiSheet_ResultSheetsExportedIsTwo()
    {
        var outPath = Path.Combine(_tempDir, "multi3.json");
        var result = FodsJsonExporter.ExportToJson(MultiSheetFods, outPath);
        Assert.Equal(2, result.SheetsExported);
    }
}
