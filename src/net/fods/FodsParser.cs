// FormatFactory.Fods -- Commercial .NET FODS Parser -- Tier 0 Implementation
// DEC-033 Option B: .NET Commercial Only
// Python FOSS track: src/python/fods/ (Apache-2.0)
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Xml;

namespace FormatFactory.Fods;

/// <summary>
/// Tier 0 streaming parser for Flat OpenDocument Spreadsheet (FODS) files.
/// FODS is the flat-XML variant of ODF Spreadsheet (ODF 1.3 Part 3).
/// Root element: office:document; spreadsheet data under office:body/office:spreadsheet.
///
/// Security posture: DTD prohibited, XmlResolver disabled, file-size guard (50 MB default).
/// Gate 11 status: commercial_readiness_in_progress -- NOT release-ready.
/// </summary>
public sealed class FodsParser
{
    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsTable  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private const string NsDc     = "http://purl.org/dc/elements/1.1/";
    private const string NsMeta   = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0";

    /// <summary>Maximum FODS file size accepted by Parse(). Default: 50 MB.</summary>
    public long MaxFileSizeBytes { get; init; } = 50L * 1024 * 1024;

    /// <summary>
    /// Parse a FODS file and return a <see cref="FodsParseResult"/>.
    /// </summary>
    /// <param name="filePath">Absolute or relative path to the .fods file.</param>
    /// <returns>Parse result; check <see cref="FodsParseResult.IsSuccess"/> and Errors.</returns>
    public FodsParseResult Parse(string filePath)
    {
        var result = new FodsParseResult();

        if (string.IsNullOrWhiteSpace(filePath))
        {
            result.Errors.Add("filePath must not be null or empty.");
            return result;
        }

        if (!File.Exists(filePath))
        {
            result.Errors.Add($"File not found: {filePath}");
            return result;
        }

        var info = new FileInfo(filePath);
        result.FileSizeBytes = info.Length;

        if (info.Length == 0)
        {
            result.Errors.Add("File is empty (0 bytes).");
            return result;
        }

        if (info.Length > MaxFileSizeBytes)
        {
            result.Errors.Add(
                $"File size {info.Length:N0} bytes exceeds limit {MaxFileSizeBytes:N0} bytes.");
            return result;
        }

        var settings = new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver   = null,
        };

        try
        {
            using var reader = XmlReader.Create(filePath, settings);
            ParseDocument(reader, result);
        }
        catch (XmlException ex)
        {
            result.Errors.Add($"XML parse error: {ex.Message}");
        }
        catch (Exception ex)
        {
            result.Errors.Add($"Unexpected error: {ex.GetType().Name}: {ex.Message}");
        }

        if (result.MimeType is not null &&
            !result.MimeType.Equals(
                "application/vnd.oasis.opendocument.spreadsheet-flat-xml",
                StringComparison.OrdinalIgnoreCase))
        {
            result.Warnings.Add(
                $"Unexpected MIME type '{result.MimeType}'; expected " +
                "application/vnd.oasis.opendocument.spreadsheet-flat-xml.");
        }

        if (result.Sheets.Count == 0 && result.IsSuccess)
            result.Warnings.Add("No sheets found in document.");

        return result;
    }

    /// <summary>
    /// Convenience method: returns all sheet names from a FODS file.
    /// Throws <see cref="FodsParseException"/> if parsing fails.
    /// </summary>
    public IReadOnlyList<string> GetSheetNames(string filePath)
    {
        var result = Parse(filePath);
        if (!result.IsSuccess)
            throw new FodsParseException(
                $"Parse failed: {string.Join("; ", result.Errors)}");
        var names = new List<string>(result.Sheets.Count);
        foreach (var sheet in result.Sheets)
            names.Add(sheet.Name);
        return names;
    }

    // -------------------------------------------------------------------------
    // Private streaming parser
    // -------------------------------------------------------------------------

    private static void ParseDocument(XmlReader r, FodsParseResult result)
    {
        FodsSheetInfo? currentSheet = null;
        bool inMeta = false;

        while (r.Read())
        {
            if (r.NodeType == XmlNodeType.Element)
            {
                var ns   = r.NamespaceURI;
                var name = r.LocalName;

                // office:document root -- grab mimetype and ODF version
                if (ns == NsOffice && name == "document")
                {
                    result.MimeType   = r.GetAttribute("mimetype", NsOffice)
                                     ?? r.GetAttribute("mimetype");
                    result.OdfVersion = r.GetAttribute("version", NsOffice)
                                     ?? r.GetAttribute("version");
                    continue;
                }

                // office:meta section
                if (ns == NsOffice && name == "meta")
                {
                    inMeta = true;
                    continue;
                }

                if (inMeta)
                {
                    if (ns == NsDc && name == "title")
                    {
                        result.Title = ReadText(r);
                        continue;
                    }
                    if (ns == NsDc && name == "creator")
                    {
                        result.Creator = ReadText(r);
                        continue;
                    }
                    if (ns == NsDc && name == "subject")
                    {
                        result.Subject = ReadText(r);
                        continue;
                    }
                    if (ns == NsMeta && name == "initial-creator")
                    {
                        result.InitialCreator = ReadText(r);
                        continue;
                    }
                }

                // table:table -- start of a sheet
                if (ns == NsTable && name == "table")
                {
                    var sheetName = r.GetAttribute("name", NsTable)
                                 ?? r.GetAttribute("name")
                                 ?? $"Sheet{result.Sheets.Count + 1}";
                    currentSheet = new FodsSheetInfo { Name = sheetName };
                    result.Sheets.Add(currentSheet);
                    continue;
                }

                // table:table-row -- increment row count
                if (currentSheet is not null && ns == NsTable && name == "table-row")
                {
                    currentSheet.RowCount++;
                    continue;
                }

                // table:table-cell and table:covered-table-cell -- increment cell count
                if (currentSheet is not null && ns == NsTable &&
                    (name == "table-cell" || name == "covered-table-cell"))
                {
                    currentSheet.CellCount++;
                    continue;
                }
            }
            else if (r.NodeType == XmlNodeType.EndElement)
            {
                var ns   = r.NamespaceURI;
                var name = r.LocalName;

                if (ns == NsOffice && name == "meta")
                    inMeta = false;

                if (ns == NsTable && name == "table")
                    currentSheet = null;
            }
        }
    }

    /// <summary>Read text content of current element without advancing past end tag.</summary>
    private static string ReadText(XmlReader r)
    {
        if (r.IsEmptyElement)
            return string.Empty;
        return r.ReadElementContentAsString() ?? string.Empty;
    }
}

/// <summary>Result of a <see cref="FodsParser.Parse"/> call.</summary>
public sealed class FodsParseResult
{
    /// <summary>MIME type from office:document/@mimetype, or null if absent.</summary>
    public string? MimeType { get; set; }

    /// <summary>ODF version from office:document/@version, or null if absent.</summary>
    public string? OdfVersion { get; set; }

    /// <summary>dc:title from office:meta, or null if absent.</summary>
    public string? Title { get; set; }

    /// <summary>dc:creator from office:meta, or null if absent.</summary>
    public string? Creator { get; set; }

    /// <summary>dc:subject from office:meta, or null if absent.</summary>
    public string? Subject { get; set; }

    /// <summary>meta:initial-creator from office:meta, or null if absent.</summary>
    public string? InitialCreator { get; set; }

    /// <summary>File size in bytes (0 if file was not opened).</summary>
    public long FileSizeBytes { get; set; }

    /// <summary>Parsed sheet information, in document order.</summary>
    public List<FodsSheetInfo> Sheets { get; } = new();

    /// <summary>Fatal errors encountered during parsing.</summary>
    public List<string> Errors { get; } = new();

    /// <summary>Non-fatal warnings (wrong MIME type, empty sheets, etc.).</summary>
    public List<string> Warnings { get; } = new();

    /// <summary>True iff no fatal errors were recorded.</summary>
    public bool IsSuccess => Errors.Count == 0;
}

/// <summary>Metadata for a single sheet parsed from a FODS file.</summary>
public sealed class FodsSheetInfo
{
    /// <summary>Sheet name from table:table/@name.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Number of table:table-row elements found in this sheet.</summary>
    public int RowCount { get; set; }

    /// <summary>
    /// Number of table:table-cell + table:covered-table-cell elements found.
    /// Includes empty/covered cells as reported in the XML.
    /// </summary>
    public int CellCount { get; set; }
}

/// <summary>
/// Thrown by <see cref="FodsParser.GetSheetNames"/> when parsing fails.
/// </summary>
public sealed class FodsParseException : Exception
{
    public FodsParseException(string message) : base(message) { }
    public FodsParseException(string message, Exception inner) : base(message, inner) { }
}
