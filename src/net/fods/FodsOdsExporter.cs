// FormatFactory.Fods -- Commercial .NET FODS → ODS Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: product-deepening-fods-ods-export-20260616
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
//
// Pure .NET ODS writer — uses System.IO.Compression (no NuGet deps).
// ODS is an ODF ZIP archive (OASIS OpenDocument 1.3 §3.1.1).

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Text;

namespace FormatFactory.Fods;

/// <summary>
/// Result returned by <see cref="FodsOdsExporter.ExportToOds"/>.
/// </summary>
public sealed class FodsOdsExportResult
{
    /// <summary>Path to the generated ODS file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Number of sheets exported.</summary>
    public int SheetCount { get; init; }

    /// <summary>Total rows exported across all sheets.</summary>
    public int TotalRowsExported { get; init; }

    /// <summary>Total cells exported across all sheets.</summary>
    public int TotalCellsExported { get; init; }
}

/// <summary>
/// G11-E Expanded Prototype: Exports a FODS spreadsheet to ODS format.
///
/// ODS is an ODF ZIP archive (OASIS ODF 1.3, §3.1.1). This exporter produces:
///   - mimetype  — "application/vnd.oasis.opendocument.spreadsheet" (uncompressed, first entry)
///   - META-INF/manifest.xml — manifest declaring content.xml
///   - content.xml — full spreadsheet content as ODF XML
///
/// Scope:
///   - All sheets exported with their rows and cell values.
///   - Cell values exported as string type (text:p elements).
///   - Empty cells represented as empty table:table-cell elements.
///   - Output is a valid ODS ZIP archive openable by LibreOffice/Excel.
///
/// Limitations (prototype):
///   - No cell formatting (font, color, alignment).
///   - No formula evaluation — raw cell text only.
///   - No merged cells (table:covered-table-cell not written).
///   - All cells use office:value-type="string" regardless of actual type.
///   - No styles.xml or meta.xml (optional per ODF spec).
///
/// Security:
///   - All cell values are XML-escaped.
///   - File size guard via <see cref="FodsDocument.MaxFileSizeBytes"/>.
///
/// ODF basis:
///   §3.1.1  ODF Package (ZIP) structure
///   §3.1.2  office:document-content root
///   §3.7    office:spreadsheet
///   §9.4.2  table:table (sheet)
///   §9.4.4  table:table-row
///   §9.4.5  table:table-cell
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodsOdsExporter
{
    // ODS namespace declarations
    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsTable = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private const string NsText = "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private const string NsDc = "http://purl.org/dc/elements/1.1/";
    private const string NsMeta = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0";

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export to ODS at <paramref name="odsPath"/>.
    /// </summary>
    public static FodsOdsExportResult ExportToOds(
        string fodsPath,
        string odsPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new ArgumentNullException(nameof(fodsPath));
        if (string.IsNullOrWhiteSpace(odsPath))
            throw new ArgumentNullException(nameof(odsPath));

        var doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        return ExportToOds(doc, odsPath);
    }

    /// <summary>
    /// Export an already-loaded <see cref="FodsDocument"/> to ODS at <paramref name="odsPath"/>.
    /// </summary>
    public static FodsOdsExportResult ExportToOds(FodsDocument document, string odsPath)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        if (string.IsNullOrWhiteSpace(odsPath))
            throw new ArgumentNullException(nameof(odsPath));

        var sheetNames = document.GetSheetNames();
        int totalRows = 0, totalCells = 0;

        string contentXml = BuildContentXml(document, sheetNames, ref totalRows, ref totalCells);

        using var fileStream = new FileStream(odsPath, FileMode.Create, FileAccess.Write, FileShare.None);
        WriteOdsArchive(fileStream, contentXml);

        return new FodsOdsExportResult
        {
            OutputPath = odsPath,
            SheetCount = sheetNames.Count,
            TotalRowsExported = totalRows,
            TotalCellsExported = totalCells,
        };
    }

    /// <summary>
    /// Export a FODS document to an ODS byte array (no file I/O).
    /// </summary>
    public static byte[] ExportToOdsBytes(FodsDocument document)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));

        var sheetNames = document.GetSheetNames();
        int totalRows = 0, totalCells = 0;
        string contentXml = BuildContentXml(document, sheetNames, ref totalRows, ref totalCells);

        using var ms = new MemoryStream();
        WriteOdsArchive(ms, contentXml);
        return ms.ToArray();
    }

    // -------------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------------

    private static void WriteOdsArchive(Stream output, string contentXml)
    {
        // ODS requires mimetype to be the FIRST entry, stored uncompressed (STORED, not DEFLATED)
        using var archive = new ZipArchive(output, ZipArchiveMode.Create, leaveOpen: true);

        // 1. mimetype (STORED, uncompressed — required by ODF spec §3.1.1)
        var mimetype = archive.CreateEntry("mimetype", CompressionLevel.NoCompression);
        using (var w = new StreamWriter(mimetype.Open(), new UTF8Encoding(false)))
            w.Write("application/vnd.oasis.opendocument.spreadsheet");

        // 2. META-INF/manifest.xml
        var manifest = archive.CreateEntry("META-INF/manifest.xml");
        using (var w = new StreamWriter(manifest.Open(), new UTF8Encoding(false)))
            w.Write(BuildManifestXml());

        // 3. content.xml
        var content = archive.CreateEntry("content.xml");
        using (var w = new StreamWriter(content.Open(), new UTF8Encoding(false)))
            w.Write(contentXml);
    }

    private static string BuildManifestXml()
    {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
               "<manifest:manifest xmlns:manifest=\"urn:oasis:names:tc:opendocument:xmlns:manifest:1.0\" manifest:version=\"1.3\">\n" +
               "  <manifest:file-entry manifest:full-path=\"/\" manifest:version=\"1.3\" manifest:media-type=\"application/vnd.oasis.opendocument.spreadsheet\"/>\n" +
               "  <manifest:file-entry manifest:full-path=\"content.xml\" manifest:media-type=\"text/xml\"/>\n" +
               "</manifest:manifest>\n";
    }

    private static string BuildContentXml(
        FodsDocument doc,
        IReadOnlyList<string> sheetNames,
        ref int totalRows,
        ref int totalCells)
    {
        var sb = new StringBuilder();
        sb.Append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.Append("<office:document-content");
        sb.Append($" xmlns:office=\"{NsOffice}\"");
        sb.Append($" xmlns:table=\"{NsTable}\"");
        sb.Append($" xmlns:text=\"{NsText}\"");
        sb.Append(" office:version=\"1.3\">\n");
        sb.Append("<office:body>\n");
        sb.Append("<office:spreadsheet>\n");

        foreach (var name in sheetNames)
        {
            sb.Append($"<table:table table:name=\"{XmlEscape(name)}\">\n");

            int rowCount = doc.GetRowCount(name);
            int colCount = doc.GetColumnCount(name);

            for (int r = 0; r < rowCount; r++)
            {
                var vals = doc.GetRowValues(name, r);
                sb.Append("<table:table-row>\n");
                for (int c = 0; c < colCount; c++)
                {
                    string cellVal = (c < vals.Count ? vals[c] : null) ?? string.Empty;
                    if (string.IsNullOrEmpty(cellVal))
                    {
                        sb.Append("<table:table-cell/>\n");
                    }
                    else
                    {
                        sb.Append("<table:table-cell office:value-type=\"string\">\n");
                        sb.Append($"<text:p>{XmlEscape(cellVal)}</text:p>\n");
                        sb.Append("</table:table-cell>\n");
                        totalCells++;
                    }
                }
                sb.Append("</table:table-row>\n");
                totalRows++;
            }

            sb.Append("</table:table>\n");
        }

        sb.Append("</office:spreadsheet>\n");
        sb.Append("</office:body>\n");
        sb.Append("</office:document-content>\n");
        return sb.ToString();
    }

    private static string XmlEscape(string text)
    {
        return text
            .Replace("&", "&amp;")
            .Replace("<", "&lt;")
            .Replace(">", "&gt;")
            .Replace("\"", "&quot;")
            .Replace("'", "&apos;");
    }
}
