// FormatFactory.Fodt -- Commercial .NET FODT Parser -- Tier 0 Implementation
// DEC-033 Option B: .NET Commercial Only
// Python FOSS track: src/python/fodt/ (Apache-2.0)
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.Collections.Generic;
using System.IO;
using System.Xml;

namespace FormatFactory.Fodt;

/// <summary>
/// Tier 0 streaming parser for Flat OpenDocument Text (FODT) files.
/// FODT is the flat-XML variant of ODF Text Document (ODF 1.3 Part 3).
/// Root element: office:document; text content under office:body/office:text.
///
/// Security posture: DTD prohibited, XmlResolver disabled, file-size guard (50 MB default).
/// Gate 11 status: commercial_readiness_in_progress -- NOT release-ready.
/// </summary>
public sealed class FodtParser
{
    private const string NsOffice = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";
    private const string NsText   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0";
    private const string NsTable  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0";
    private const string NsDc     = "http://purl.org/dc/elements/1.1/";
    private const string NsMeta   = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0";

    /// <summary>Maximum FODT file size accepted by Parse(). Default: 50 MB.</summary>
    public long MaxFileSizeBytes { get; init; } = 50L * 1024 * 1024;

    /// <summary>
    /// Parse a FODT file and return a <see cref="FodtParseResult"/>.
    /// </summary>
    /// <param name="filePath">Absolute or relative path to the .fodt file.</param>
    /// <returns>Parse result; check <see cref="FodtParseResult.IsSuccess"/> and Errors.</returns>
    public FodtParseResult Parse(string filePath)
    {
        var result = new FodtParseResult();

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
                "application/vnd.oasis.opendocument.text-flat-xml",
                StringComparison.OrdinalIgnoreCase))
        {
            result.Warnings.Add(
                $"Unexpected MIME type '{result.MimeType}'; expected " +
                "application/vnd.oasis.opendocument.text-flat-xml.");
        }

        return result;
    }

    /// <summary>
    /// Convenience method: returns the paragraph count from a FODT file.
    /// Throws <see cref="FodtParseException"/> if parsing fails.
    /// </summary>
    public int GetParagraphCount(string filePath)
    {
        var result = Parse(filePath);
        if (!result.IsSuccess)
            throw new FodtParseException(
                $"Parse failed: {string.Join("; ", result.Errors)}");
        return result.ParagraphCount;
    }

    // -------------------------------------------------------------------------
    // Private streaming parser
    // -------------------------------------------------------------------------

    private static void ParseDocument(XmlReader r, FodtParseResult result)
    {
        bool inMeta       = false;
        bool inBody       = false;
        FodtTableInfo? currentTable = null;
        int tableRowDepth = 0;

        while (r.Read())
        {
            if (r.NodeType == XmlNodeType.Element)
            {
                var ns   = r.NamespaceURI;
                var name = r.LocalName;

                // office:document root -- mimetype and version
                if (ns == NsOffice && name == "document")
                {
                    result.MimeType   = r.GetAttribute("mimetype", NsOffice)
                                     ?? r.GetAttribute("mimetype");
                    result.OdfVersion = r.GetAttribute("version", NsOffice)
                                     ?? r.GetAttribute("version");
                    continue;
                }

                // office:meta
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

                // office:body
                if (ns == NsOffice && name == "body")
                {
                    inBody = true;
                    continue;
                }

                if (!inBody) continue;

                // text:p (paragraph) and text:h (heading) -- counted as paragraphs
                if (ns == NsText && (name == "p" || name == "h"))
                {
                    result.ParagraphCount++;
                    if (name == "h")
                        result.HeadingCount++;
                    continue;
                }

                // text:list
                if (ns == NsText && name == "list")
                {
                    result.ListCount++;
                    continue;
                }

                // table:table
                if (ns == NsTable && name == "table")
                {
                    var tableName = r.GetAttribute("name", NsTable)
                                 ?? r.GetAttribute("name");
                    currentTable = new FodtTableInfo { Name = tableName };
                    result.Tables.Add(currentTable);
                    tableRowDepth = 0;
                    continue;
                }

                // table:table-row
                if (currentTable is not null && ns == NsTable && name == "table-row")
                {
                    currentTable.RowCount++;
                    tableRowDepth++;
                    continue;
                }

                // table:table-cell / covered-table-cell
                if (currentTable is not null && ns == NsTable &&
                    (name == "table-cell" || name == "covered-table-cell"))
                {
                    currentTable.CellCount++;
                    continue;
                }
            }
            else if (r.NodeType == XmlNodeType.EndElement)
            {
                var ns   = r.NamespaceURI;
                var name = r.LocalName;

                if (ns == NsOffice && name == "meta")  inMeta = false;
                if (ns == NsOffice && name == "body")  inBody = false;

                if (ns == NsTable && name == "table-row" && tableRowDepth > 0)
                    tableRowDepth--;

                if (ns == NsTable && name == "table")
                    currentTable = null;
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

/// <summary>Result of a <see cref="FodtParser.Parse"/> call.</summary>
public sealed class FodtParseResult
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

    /// <summary>Count of text:p and text:h elements in office:body.</summary>
    public int ParagraphCount { get; set; }

    /// <summary>Count of text:h elements (subset of ParagraphCount).</summary>
    public int HeadingCount { get; set; }

    /// <summary>Count of text:list elements in office:body.</summary>
    public int ListCount { get; set; }

    /// <summary>Table information, in document order.</summary>
    public List<FodtTableInfo> Tables { get; } = new();

    /// <summary>Fatal errors encountered during parsing.</summary>
    public List<string> Errors { get; } = new();

    /// <summary>Non-fatal warnings (wrong MIME type, etc.).</summary>
    public List<string> Warnings { get; } = new();

    /// <summary>True iff no fatal errors were recorded.</summary>
    public bool IsSuccess => Errors.Count == 0;
}

/// <summary>Metadata for a single table parsed from a FODT file.</summary>
public sealed class FodtTableInfo
{
    /// <summary>Table name from table:table/@name, or null if absent.</summary>
    public string? Name { get; set; }

    /// <summary>Number of table:table-row elements found in this table.</summary>
    public int RowCount { get; set; }

    /// <summary>
    /// Number of table:table-cell + table:covered-table-cell elements found.
    /// </summary>
    public int CellCount { get; set; }
}

/// <summary>
/// Thrown by <see cref="FodtParser.GetParagraphCount"/> when parsing fails.
/// </summary>
public sealed class FodtParseException : Exception
{
    public FodtParseException(string message) : base(message) { }
    public FodtParseException(string message, Exception inner) : base(message, inner) { }
}
