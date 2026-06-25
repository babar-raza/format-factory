// FormatFactory.Fods -- Commercial .NET FODS to CSV Exporter
// DEC-033 Option B: .NET Commercial Only
// Delegates CSV serialization to FormatFactory.Csv.CsvWriter
// Gate 11 status: commercial_readiness_in_progress (NOT approved — Babar Raza approval required).
// dogfood_status: IMPLEMENTED — delegates CSV serialization to FormatFactory.Csv.CsvWriter

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using FormatFactory.Csv;

namespace FormatFactory.Fods;

/// <summary>
/// Exports a FODS spreadsheet to CSV (comma-separated values).
///
/// Scope:
///   - Exports the FIRST sheet of a FODS document.
///   - Each row becomes one CSV line.
///   - Cell values are taken from text:p content (display/string value).
///   - Numeric values that have no text:p are exported as empty.
///   - Values are properly escaped (commas, quotes, newlines).
///   - Output is UTF-8, LF line endings.
///
/// Limitations (prototype):
///   - Only first sheet exported. Multi-sheet export is future work.
///   - table:number-columns-repeated columns are NOT expanded (counted once).
///   - Covered/merged cells are output as empty (IsCovered=true → empty field).
///   - Formula results not available without evaluation engine.
///   - No XLSX output yet (future G11-E hardening sprint).
///
/// ODF basis:
///   §9.4.2 table:table, §9.4.4 table:table-row, §9.4.5 table:table-cell, §6.1.1 text:p
///
/// Gate 11 status: commercial_readiness_in_progress (NOT approved — Babar Raza approval required).
/// </summary>
public static class FodsCsvExporter
{
    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export the first sheet to CSV at <paramref name="csvPath"/>.
    /// </summary>
    /// <param name="fodsPath">Path to the .fods source file.</param>
    /// <param name="csvPath">Path to write the output .csv file.</param>
    /// <param name="maxFileSizeBytes">File-size guard for the FODS input (default 50 MB).</param>
    /// <returns>Export result with row/column counts and status.</returns>
    /// <exception cref="FodsCsvExportException">On file-not-found, parse failure, or I/O error.</exception>
    public static FodsCsvExportResult ExportFirstSheetToCsv(
        string fodsPath,
        string csvPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new FodsCsvExportException("fodsPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(csvPath))
            throw new FodsCsvExportException("csvPath must not be null or empty.");

        FodsDocument doc;
        try
        {
            doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        }
        catch (FodsDocumentException ex)
        {
            throw new FodsCsvExportException($"Failed to load FODS: {ex.Message}", ex);
        }

        var sheets = doc.Sheets;
        if (sheets.Count == 0)
        {
            // Write empty CSV
            var dir = Path.GetDirectoryName(csvPath);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(csvPath, string.Empty, Encoding.UTF8);
            return new FodsCsvExportResult
            {
                SourcePath   = fodsPath,
                OutputPath   = csvPath,
                SheetName    = string.Empty,
                RowsExported = 0,
                MaxColumns   = 0,
                Status       = "exported_empty_no_sheets",
                Warnings     = { "Source FODS has no sheets." },
            };
        }

        return ExportSheetToCsv(sheets[0], fodsPath, csvPath);
    }

    /// <summary>
    /// Export a single <see cref="FodsSheet"/> to CSV at <paramref name="csvPath"/>.
    /// </summary>
    public static FodsCsvExportResult ExportSheetToCsv(
        FodsSheet sheet,
        string sourcePath,
        string csvPath)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        if (string.IsNullOrWhiteSpace(csvPath))
            throw new FodsCsvExportException("csvPath must not be null or empty.");

        var dir = Path.GetDirectoryName(csvPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var result = new FodsCsvExportResult
        {
            SourcePath = sourcePath ?? string.Empty,
            OutputPath = csvPath,
            SheetName  = sheet.Name,
            Status     = "unknown",
        };

        // Build rows as IEnumerable<IEnumerable<string?>> for CsvWriter delegation
        var rows = sheet.Rows;
        int maxCols = 0;

        var csvRows = new List<IEnumerable<string?>>(rows.Count);
        foreach (var row in rows)
        {
            var cells = row.Cells;
            if (cells.Count > maxCols) maxCols = cells.Count;
            var fields = new List<string?>(cells.Count);
            foreach (var cell in cells)
            {
                // Covered cells (merged) contribute an empty field
                fields.Add(cell.IsCovered ? null : cell.Value);
            }
            csvRows.Add(fields);
        }

        result.RowsExported = rows.Count;
        result.MaxColumns   = maxCols;

        try
        {
            // Delegate serialization to FormatFactory.Csv.CsvWriter (dogfood path)
            CsvWriter.WriteRowsToFile(csvRows, csvPath);
            result.Status = "exported";
        }
        catch (IOException ex)
        {
            throw new FodsCsvExportException($"Failed to write CSV to '{csvPath}': {ex.Message}", ex);
        }

        return result;
    }

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export ALL sheets to individual CSV files
    /// in <paramref name="outputDirPath"/>, named {SheetName}.csv.
    /// R88 Train H: multi-sheet CSV export.
    /// </summary>
    /// <param name="fodsPath">Path to the .fods source file.</param>
    /// <param name="outputDirPath">Directory where per-sheet CSV files are written.</param>
    /// <param name="maxFileSizeBytes">File-size guard for the FODS input (default 50 MB).</param>
    /// <returns>List of export results, one per sheet.</returns>
    public static List<FodsCsvExportResult> ExportAllSheetsToCsv(
        string fodsPath,
        string outputDirPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new FodsCsvExportException("fodsPath must not be null or empty.");
        if (string.IsNullOrWhiteSpace(outputDirPath))
            throw new FodsCsvExportException("outputDirPath must not be null or empty.");

        FodsDocument doc;
        try
        {
            doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        }
        catch (FodsDocumentException ex)
        {
            throw new FodsCsvExportException($"Failed to load FODS: {ex.Message}", ex);
        }

        Directory.CreateDirectory(outputDirPath);
        var results = new List<FodsCsvExportResult>();
        var usedNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var sheet in doc.Sheets)
        {
            // Sanitize sheet name for filesystem
            var safeName = SanitizeFileName(sheet.Name);
            if (string.IsNullOrEmpty(safeName)) safeName = $"sheet_{results.Count + 1}";

            // Handle duplicate names
            var baseName = safeName;
            int suffix = 2;
            while (!usedNames.Add(safeName))
            {
                safeName = $"{baseName}_{suffix}";
                suffix++;
            }

            var csvPath = Path.Combine(outputDirPath, safeName + ".csv");
            var result = ExportSheetToCsv(sheet, fodsPath, csvPath);
            results.Add(result);
        }

        return results;
    }

    /// <summary>
    /// Export a single <see cref="FodsSheet"/> to a CSV string (no file I/O).
    /// R89 Train I: in-memory CSV export.
    /// </summary>
    public static string ExportSheetToCsvString(FodsSheet sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);

        var csvRows = new List<IEnumerable<string?>>(sheet.Rows.Count);
        foreach (var row in sheet.Rows)
        {
            var fields = new List<string?>(row.Cells.Count);
            foreach (var cell in row.Cells)
                fields.Add(cell.IsCovered ? null : cell.Value);
            csvRows.Add(fields);
        }
        // Delegate to FormatFactory.Csv.CsvWriter (dogfood path)
        return CsvWriter.WriteRows(csvRows);
    }

    /// <summary>Sanitize a string for use as a filename.</summary>
    private static string SanitizeFileName(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return string.Empty;
        var invalid = Path.GetInvalidFileNameChars();
        var sb = new StringBuilder(name.Length);
        foreach (var c in name)
        {
            sb.Append(Array.IndexOf(invalid, c) >= 0 ? '_' : c);
        }
        return sb.ToString().Trim();
    }

    // -------------------------------------------------------------------------
    // CSV escaping (RFC 4180 compatible)
    // -------------------------------------------------------------------------

    /// <summary>
    /// Escape a single CSV field value per RFC 4180.
    /// Delegates to <see cref="CsvWriter.EscapeField"/> (FormatFactory.Csv target writer library).
    /// Kept for API compatibility.
    /// </summary>
    public static string EscapeCsvField(string? value) => CsvWriter.EscapeField(value);
}

// -------------------------------------------------------------------------
// Result type
// -------------------------------------------------------------------------

/// <summary>Result returned by <see cref="FodsCsvExporter.ExportFirstSheetToCsv"/>.</summary>
public sealed class FodsCsvExportResult
{
    /// <summary>Path to the FODS source file.</summary>
    public string SourcePath { get; init; } = string.Empty;

    /// <summary>Path to the written CSV file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Name of the sheet that was exported.</summary>
    public string SheetName { get; init; } = string.Empty;

    /// <summary>Number of rows written to CSV.</summary>
    public int RowsExported { get; set; }

    /// <summary>Maximum number of columns across all rows.</summary>
    public int MaxColumns { get; set; }

    /// <summary>Export status: "exported", "exported_empty_no_sheets", or "unknown".</summary>
    public string Status { get; set; } = "unknown";

    /// <summary>Non-fatal warnings encountered during export.</summary>
    public List<string> Warnings { get; } = new();
}

// -------------------------------------------------------------------------
// Exception type
// -------------------------------------------------------------------------

/// <summary>Thrown by <see cref="FodsCsvExporter"/> when export cannot proceed.</summary>
public sealed class FodsCsvExportException : Exception
{
    public FodsCsvExportException(string message) : base(message) { }
    public FodsCsvExportException(string message, Exception inner) : base(message, inner) { }
}
