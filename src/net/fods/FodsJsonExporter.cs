// FormatFactory.Fods -- Commercial .NET FODS → JSON Exporter (G11-E Expanded Prototype)
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
//
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;

namespace FormatFactory.Fods;

/// <summary>
/// G11-E Expanded Prototype: Exports a FODS spreadsheet to JSON.
///
/// Scope:
///   - Exports all sheets as a JSON array under "sheets".
///   - Each sheet has "name" (string) and "rows" (array of string arrays).
///   - Cell values are taken from text:p content (display/string value).
///   - Null/covered cells are exported as null in JSON.
///   - Output is UTF-8, indented JSON, no BOM.
///
/// Limitations (prototype):
///   - table:number-columns-repeated columns are NOT expanded.
///   - Formula results not available without evaluation engine.
///   - No type inference — all values are strings or null.
///   - Single-document export only (all sheets).
///
/// JSON output shape:
/// {
///   "format": "fods",
///   "prototype": true,
///   "commercial_product_ready": false,
///   "sheets": [
///     { "name": "Sheet1", "rows": [["A1","B1"],["A2","B2"]] }
///   ]
/// }
///
/// ODF basis: §9.4.2 table:table, §9.4.4 table:table-row, §9.4.5 table:table-cell, §6.1.1 text:p
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodsJsonExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export all sheets to JSON at <paramref name="jsonPath"/>.
    /// </summary>
    /// <param name="fodsPath">Path to the .fods source file.</param>
    /// <param name="jsonPath">Path to write the output .json file.</param>
    /// <param name="maxFileSizeBytes">File-size guard for the FODS input (default 50 MB).</param>
    /// <returns>Export result with sheet/row counts and status.</returns>
    /// <exception cref="FodsJsonExportException">On file-not-found, parse failure, or I/O error.</exception>
    public static FodsJsonExportResult ExportToJson(
        string fodsPath,
        string jsonPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new FodsJsonExportException("fodsPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(jsonPath))
            throw new FodsJsonExportException("jsonPath must not be null or empty.");

        FodsDocument doc;
        try
        {
            doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        }
        catch (FodsDocumentException ex)
        {
            throw new FodsJsonExportException($"Failed to load FODS: {ex.Message}", ex);
        }

        return ExportToJson(doc, fodsPath, jsonPath);
    }

    /// <summary>
    /// Export all sheets of a loaded <see cref="FodsDocument"/> to JSON at <paramref name="jsonPath"/>.
    /// </summary>
    public static FodsJsonExportResult ExportToJson(
        FodsDocument doc,
        string sourcePath,
        string jsonPath)
    {
        ArgumentNullException.ThrowIfNull(doc);
        if (string.IsNullOrWhiteSpace(jsonPath))
            throw new FodsJsonExportException("jsonPath must not be null or empty.");

        var dir = Path.GetDirectoryName(jsonPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodsJsonExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = jsonPath,
        };

        var sheets = doc.Sheets;
        result.SheetsExported = sheets.Count;

        var sheetsData = new List<object>();
        int totalRows = 0;

        foreach (var sheet in sheets)
        {
            var rowsData = new List<List<string?>>();
            foreach (var row in sheet.Rows)
            {
                var cellValues = new List<string?>();
                foreach (var cell in row.Cells)
                    cellValues.Add(cell.IsCovered ? null : cell.Value);
                rowsData.Add(cellValues);
                totalRows++;
            }
            sheetsData.Add(new Dictionary<string, object>
            {
                ["name"] = sheet.Name,
                ["rows"] = rowsData,
            });
        }

        result.TotalRowsExported = totalRows;

        var envelope = new Dictionary<string, object>
        {
            ["format"] = "fods",
            ["prototype"] = true,
            ["commercial_product_ready"] = false,
            ["gate11_status"] = "g11e_prototype_complete",
            ["sheets"] = sheetsData,
        };

        try
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.Never,
            };
            var json = JsonSerializer.Serialize(envelope, options);
            // Normalize to LF, no BOM
            json = json.Replace("\r\n", "\n");
            File.WriteAllText(jsonPath, json, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            result.Status = sheets.Count == 0 ? "exported_empty_no_sheets" : "exported";
        }
        catch (IOException ex)
        {
            throw new FodsJsonExportException($"Failed to write JSON to '{jsonPath}': {ex.Message}", ex);
        }

        return result;
    }
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodsJsonExporter.ExportToJson"/>.</summary>
public sealed class FodsJsonExportResult
{
    public string SourcePath { get; init; } = string.Empty;
    public string OutputPath { get; init; } = string.Empty;
    public int SheetsExported { get; set; }
    public int TotalRowsExported { get; set; }
    public string Status { get; set; } = "unknown";
    public List<string> Warnings { get; } = new();
}

// -------------------------------------------------------------------------
// Exception type
// -------------------------------------------------------------------------

/// <summary>Thrown by <see cref="FodsJsonExporter"/> when export cannot proceed.</summary>
public sealed class FodsJsonExportException : Exception
{
    public FodsJsonExportException(string message) : base(message) { }
    public FodsJsonExportException(string message, Exception inner) : base(message, inner) { }
}
