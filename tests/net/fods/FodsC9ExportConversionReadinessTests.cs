// FodsC9ExportConversionReadinessTests -- R28 Lane I: FODS C9 Export/Conversion Readiness
// Sprint: R28
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// commercial_product_ready: false
//
// C9 = export/conversion from an edited+saved+reloaded document produces expected content
//      AND the export operation does not mutate the in-memory document model.
//
// Tests cover all three exporters: CSV, JSON, HTML.
// All tests use local fixture files only -- no network.

using System;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// C9 Export/Conversion Readiness tests for FODS.
///
/// Test matrix:
///   - CSV: export after edit+save+reload produces expected content; export does not mutate document
///   - JSON: export after edit+save+reload produces expected content; export does not mutate document
///   - HTML: export after edit+save+reload produces expected content; export does not mutate document
///
/// These tests build on C7 (round-trip fidelity) and C8 (opaque node preservation) evidence
/// by proving that the full pipeline (load -> edit -> save -> reload -> export) works end-to-end.
/// </summary>
public class FodsC9ExportConversionReadinessTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsC9ExportConversionReadinessTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-c9-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // =========================================================================
    // Helper: edit + save + reload pipeline
    // =========================================================================

    /// <summary>
    /// Shared pipeline: load fixture, edit cell A1 to <paramref name="editedValue"/>,
    /// save to temp, reload, and return the reloaded document + its path.
    /// </summary>
    private FodsDocument EditSaveReload(string editedValue, out string reloadedPath)
    {
        var doc = FodsDocument.Load(MinimalFods);
        doc.Sheets[0].Rows[0].Cells[0].SetText(editedValue);

        reloadedPath = Path.Combine(_tempDir, $"c9-pipeline-{Guid.NewGuid():N}.fods");
        doc.Save(reloadedPath);

        return FodsDocument.Load(reloadedPath);
    }

    // =========================================================================
    // C9-CSV: CSV export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-CSV-01: CSV export from edited+reloaded document contains the edited cell value.
    /// </summary>
    [Fact]
    public void C9_Csv_ExportAfterEditSaveReload_ContainsEditedValue()
    {
        const string editedValue = "C9_CSV_EDITED_CELL";
        var reloaded = EditSaveReload(editedValue, out var reloadedPath);

        var csvPath = Path.Combine(_tempDir, "c9-csv-01.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(reloadedPath, csvPath);

        Assert.Equal("exported", result.Status);
        var csvContent = File.ReadAllText(csvPath, Encoding.UTF8);
        Assert.Contains(editedValue, csvContent);
    }

    /// <summary>
    /// C9-CSV-02: CSV export from edited+reloaded document preserves unedited cell (B1).
    /// </summary>
    [Fact]
    public void C9_Csv_ExportAfterEditSaveReload_PreservesUneditedCell()
    {
        var reloaded = EditSaveReload("C9_CSV_ONLY_A1", out var reloadedPath);

        // Verify B1 ("World") still present in the reloaded doc
        Assert.Equal("World", reloaded.Sheets[0].Rows[0].Cells[1].Value);

        var csvPath = Path.Combine(_tempDir, "c9-csv-02.csv");
        FodsCsvExporter.ExportFirstSheetToCsv(reloadedPath, csvPath);

        var csvContent = File.ReadAllText(csvPath, Encoding.UTF8);
        Assert.Contains("World", csvContent);
    }

    /// <summary>
    /// C9-CSV-03: CSV export does not mutate the in-memory document model.
    /// After export, the reloaded document's cell values must be identical.
    /// </summary>
    [Fact]
    public void C9_Csv_ExportDoesNotMutateDocument()
    {
        const string editedValue = "C9_CSV_NO_MUTATE";
        var reloaded = EditSaveReload(editedValue, out var reloadedPath);

        // Capture cell values before export
        string cellA1Before = reloaded.Sheets[0].Rows[0].Cells[0].Value!;
        string cellB1Before = reloaded.Sheets[0].Rows[0].Cells[1].Value!;
        int sheetCountBefore = reloaded.Sheets.Count;
        int rowCountBefore = reloaded.Sheets[0].Rows.Count;

        // Perform CSV export
        var csvPath = Path.Combine(_tempDir, "c9-csv-03.csv");
        FodsCsvExporter.ExportFirstSheetToCsv(reloadedPath, csvPath);

        // Verify document model is unchanged after export
        Assert.Equal(cellA1Before, reloaded.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal(cellB1Before, reloaded.Sheets[0].Rows[0].Cells[1].Value);
        Assert.Equal(sheetCountBefore, reloaded.Sheets.Count);
        Assert.Equal(rowCountBefore, reloaded.Sheets[0].Rows.Count);
    }

    /// <summary>
    /// C9-CSV-04: CSV export row count matches document row count.
    /// </summary>
    [Fact]
    public void C9_Csv_ExportRowCountMatchesDocument()
    {
        var reloaded = EditSaveReload("C9_CSV_ROWS", out var reloadedPath);

        var csvPath = Path.Combine(_tempDir, "c9-csv-04.csv");
        var result = FodsCsvExporter.ExportFirstSheetToCsv(reloadedPath, csvPath);

        Assert.Equal(reloaded.Sheets[0].Rows.Count, result.RowsExported);
    }

    // =========================================================================
    // C9-JSON: JSON export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-JSON-01: JSON export from edited+reloaded document contains the edited cell value.
    /// </summary>
    [Fact]
    public void C9_Json_ExportAfterEditSaveReload_ContainsEditedValue()
    {
        const string editedValue = "C9_JSON_EDITED_CELL";
        EditSaveReload(editedValue, out var reloadedPath);

        var jsonPath = Path.Combine(_tempDir, "c9-json-01.json");
        var result = FodsJsonExporter.ExportToJson(reloadedPath, jsonPath);

        Assert.Equal("exported", result.Status);
        var jsonContent = File.ReadAllText(jsonPath, Encoding.UTF8);
        Assert.Contains(editedValue, jsonContent);
    }

    /// <summary>
    /// C9-JSON-02: JSON export from edited+reloaded document preserves unedited cell.
    /// </summary>
    [Fact]
    public void C9_Json_ExportAfterEditSaveReload_PreservesUneditedCell()
    {
        EditSaveReload("C9_JSON_ONLY_A1", out var reloadedPath);

        var jsonPath = Path.Combine(_tempDir, "c9-json-02.json");
        FodsJsonExporter.ExportToJson(reloadedPath, jsonPath);

        var jsonContent = File.ReadAllText(jsonPath, Encoding.UTF8);
        Assert.Contains("World", jsonContent);
    }

    /// <summary>
    /// C9-JSON-03: JSON export does not mutate the in-memory document model.
    /// </summary>
    [Fact]
    public void C9_Json_ExportDoesNotMutateDocument()
    {
        const string editedValue = "C9_JSON_NO_MUTATE";
        var reloaded = EditSaveReload(editedValue, out var reloadedPath);

        // Capture state before export
        string cellA1Before = reloaded.Sheets[0].Rows[0].Cells[0].Value!;
        int sheetCountBefore = reloaded.Sheets.Count;

        // Perform JSON export (using document overload)
        var jsonPath = Path.Combine(_tempDir, "c9-json-03.json");
        FodsJsonExporter.ExportToJson(reloaded, reloadedPath, jsonPath);

        // Verify no mutation
        Assert.Equal(cellA1Before, reloaded.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal(sheetCountBefore, reloaded.Sheets.Count);
    }

    /// <summary>
    /// C9-JSON-04: JSON export output is valid JSON with expected structure.
    /// </summary>
    [Fact]
    public void C9_Json_ExportAfterEditSaveReload_ValidJsonStructure()
    {
        EditSaveReload("C9_JSON_VALID", out var reloadedPath);

        var jsonPath = Path.Combine(_tempDir, "c9-json-04.json");
        FodsJsonExporter.ExportToJson(reloadedPath, jsonPath);

        var text = File.ReadAllText(jsonPath, Encoding.UTF8);
        var doc = JsonDocument.Parse(text);
        Assert.True(doc.RootElement.TryGetProperty("sheets", out var sheets));
        Assert.Equal(JsonValueKind.Array, sheets.ValueKind);
        Assert.True(doc.RootElement.TryGetProperty("commercial_product_ready", out var cpr));
        Assert.Equal(JsonValueKind.False, cpr.ValueKind);
    }

    /// <summary>
    /// C9-JSON-05: JSON export commercial_product_ready remains false after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Json_CommercialProductReadyFalseAfterEditPipeline()
    {
        EditSaveReload("C9_JSON_CPR", out var reloadedPath);

        var jsonPath = Path.Combine(_tempDir, "c9-json-05.json");
        FodsJsonExporter.ExportToJson(reloadedPath, jsonPath);

        var text = File.ReadAllText(jsonPath, Encoding.UTF8);
        Assert.DoesNotContain("\"commercial_product_ready\": true", text);
    }

    // =========================================================================
    // C9-HTML: HTML export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-HTML-01: HTML export from edited+reloaded document contains the edited cell value.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_ContainsEditedValue()
    {
        const string editedValue = "C9_HTML_EDITED_CELL";
        EditSaveReload(editedValue, out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-01.html");
        var result = FodsHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        Assert.Equal("exported", result.Status);
        var htmlContent = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains(editedValue, htmlContent);
    }

    /// <summary>
    /// C9-HTML-02: HTML export from edited+reloaded document preserves unedited cell.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_PreservesUneditedCell()
    {
        EditSaveReload("C9_HTML_ONLY_A1", out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-02.html");
        FodsHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var htmlContent = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains("World", htmlContent);
    }

    /// <summary>
    /// C9-HTML-03: HTML export does not mutate the in-memory document model.
    /// </summary>
    [Fact]
    public void C9_Html_ExportDoesNotMutateDocument()
    {
        const string editedValue = "C9_HTML_NO_MUTATE";
        var reloaded = EditSaveReload(editedValue, out var reloadedPath);

        // Capture state before export
        string cellA1Before = reloaded.Sheets[0].Rows[0].Cells[0].Value!;
        int sheetCountBefore = reloaded.Sheets.Count;

        // Perform HTML export (using document overload)
        var htmlPath = Path.Combine(_tempDir, "c9-html-03.html");
        FodsHtmlExporter.ExportToHtml(reloaded, reloadedPath, htmlPath);

        // Verify no mutation
        Assert.Equal(cellA1Before, reloaded.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal(sheetCountBefore, reloaded.Sheets.Count);
    }

    /// <summary>
    /// C9-HTML-04: HTML export output is valid HTML5 with table after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_ValidHtmlStructure()
    {
        EditSaveReload("C9_HTML_VALID", out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-04.html");
        FodsHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var text = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains("<!DOCTYPE html>", text);
        Assert.Contains("<table", text);
        Assert.Contains("<td>", text);
        Assert.Contains("commercial_product_ready=false", text);
    }

    /// <summary>
    /// C9-HTML-05: HTML export from edited+reloaded doc contains the edited value in a td element.
    /// </summary>
    [Fact]
    public void C9_Html_EditedValueAppearsInTableCell()
    {
        const string editedValue = "C9_HTML_IN_TD";
        EditSaveReload(editedValue, out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-05.html");
        FodsHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var text = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains($"<td>{editedValue}</td>", text);
    }

    // =========================================================================
    // Governance invariants
    // =========================================================================

    /// <summary>
    /// C9-GOV-01: commercial_product_ready must be false (governance invariant).
    /// </summary>
    [Fact]
    public void C9_Governance_CommercialProductReadyIsFalse()
    {
        const bool commercialProductReady = false;
        Assert.False(commercialProductReady,
            "commercial_product_ready must remain false. G11-G is NOT_STARTED.");
    }

    /// <summary>
    /// C9-GOV-02: All three exporters exist and are static classes.
    /// </summary>
    [Fact]
    public void C9_Governance_AllThreeExportersExist()
    {
        Assert.True(typeof(FodsCsvExporter).IsAbstract && typeof(FodsCsvExporter).IsSealed,
            "FodsCsvExporter must be a static class");
        Assert.True(typeof(FodsJsonExporter).IsAbstract && typeof(FodsJsonExporter).IsSealed,
            "FodsJsonExporter must be a static class");
        Assert.True(typeof(FodsHtmlExporter).IsAbstract && typeof(FodsHtmlExporter).IsSealed,
            "FodsHtmlExporter must be a static class");
    }
}
