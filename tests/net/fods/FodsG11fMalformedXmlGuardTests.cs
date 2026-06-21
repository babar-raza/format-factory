// FormatFactory.Fods Tests -- G11-F Malformed XML Guard (G11-F Hardening Slice)
// Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
// Gate 11 status: commercial_readiness_in_progress — G11-G NOT approved
// commercial_product_ready: false
//
// Documents and verifies the parser's resilience to malformed/adversarial XML inputs.
// Tests prototype-level behaviour only — no commercial readiness claim.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// G11-F hardening: malformed XML guard tests.
/// Verifies FodsParser does not crash or expose internals when given:
/// - Empty files
/// - Truncated XML
/// - Non-XML content
/// - Oversized files (size guard)
/// - Null/empty path
/// Prototype status — no commercial readiness claim.
/// </summary>
public class FodsG11fMalformedXmlGuardTests : IDisposable
{
    private readonly string _tempDir;
    private readonly FodsParser _parser = new FodsParser();

    public FodsG11fMalformedXmlGuardTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-malformed-guard-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string WriteTemp(string name, string content)
    {
        var path = Path.Combine(_tempDir, name);
        File.WriteAllText(path, content, System.Text.Encoding.UTF8);
        return path;
    }

    private string WriteTempBytes(string name, byte[] content)
    {
        var path = Path.Combine(_tempDir, name);
        File.WriteAllBytes(path, content);
        return path;
    }

    [Fact]
    public void Parser_NullPath_ReturnsErrorNotThrow()
    {
        var result = _parser.Parse(null!);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_EmptyPath_ReturnsError()
    {
        var result = _parser.Parse("");
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_NonExistentFile_ReturnsError()
    {
        var result = _parser.Parse(Path.Combine(_tempDir, "does-not-exist.fods"));
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_EmptyFile_ReturnsError()
    {
        var path = WriteTempBytes("empty.fods", Array.Empty<byte>());
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_TruncatedXml_ReturnsError()
    {
        var path = WriteTemp("truncated.fods", "<?xml version=\"1.0\"?><office:document");
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_NonXmlContent_ReturnsError()
    {
        var path = WriteTemp("notxml.fods", "This is not XML at all. PK\x03\x04 binary garbage.");
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_WrongRootElement_ReturnsErrorOrEmptyDocument()
    {
        // Valid XML but wrong root — not an ODF document
        var path = WriteTemp("wrongroot.fods",
            "<?xml version=\"1.0\"?><html><body><p>Not FODS</p></body></html>");
        var result = _parser.Parse(path);
        // Either error or empty sheets — must NOT return success with data
        if (result.IsSuccess)
            Assert.Empty(result.Sheets);
        else
            Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void Parser_FileSizeGuard_RejectsOversized()
    {
        // Parser with 1-byte max file size should reject any real file
        var tinyParser = new FodsParser { MaxFileSizeBytes = 1 };
        var path = WriteTemp("valid-but-oversized.fods", "<root/>");
        var result = tinyParser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    // -----------------------------------------------------------------------
    // R28 Lane H: C9 Malformed-Input Resilience — FodsDocument.Load
    // -----------------------------------------------------------------------

    /// <summary>
    /// C9-MAL-FODS-01: FodsDocument.Load rejects empty XML (valid XML, no ODF structure).
    /// The file contains a minimal XML root element but no office:document or office:spreadsheet.
    /// Document should either throw FodsDocumentException or load with zero sheets.
    /// </summary>
    [Fact]
    public void Document_Load_EmptyXml_NoOdfStructure_ThrowsOrEmptySheets()
    {
        var path = WriteTemp("empty-xml.fods",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><root/>");
        // FodsDocument.Load uses XDocument.Load which will succeed on valid XML,
        // but the resulting document has no office:body/office:spreadsheet.
        var doc = FodsDocument.Load(path);
        // Must NOT crash; sheets list must be empty since there is no ODF structure.
        Assert.Empty(doc.Sheets);
    }

    /// <summary>
    /// C9-MAL-FODS-02: FodsDocument.Load handles valid ODF document missing office:spreadsheet.
    /// The file has office:document and office:body but no office:spreadsheet child.
    /// </summary>
    [Fact]
    public void Document_Load_MissingSpreadsheet_ReturnsEmptySheets()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body>" +
            "<!-- office:spreadsheet deliberately absent -->" +
            "</office:body>" +
            "</office:document>";
        var path = WriteTemp("no-spreadsheet.fods", xml);

        var doc = FodsDocument.Load(path);
        // Must not crash; sheets must be empty because office:spreadsheet is absent.
        Assert.Empty(doc.Sheets);
        // MimeType should still be readable from the root element.
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet-flat-xml", doc.MimeType);
    }

    /// <summary>
    /// C9-MAL-FODS-03: FodsDocument.Load rejects truncated XML file with FodsDocumentException.
    /// The file is cut off mid-tag, producing invalid XML.
    /// </summary>
    [Fact]
    public void Document_Load_TruncatedFile_ThrowsFodsDocumentException()
    {
        var path = WriteTemp("truncated-doc.fods",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\">" +
            "<office:body><office:spreadsheet><table:table table:name=\"Sheet1\"");
        var ex = Assert.Throws<FodsDocumentException>(() => FodsDocument.Load(path));
        Assert.Contains("XML parse error", ex.Message);
    }

    /// <summary>
    /// C9-MAL-FODS-04: FodsParser.Parse handles valid ODF document missing office:spreadsheet gracefully.
    /// Returns success with zero sheets and a warning.
    /// </summary>
    [Fact]
    public void Parser_MissingSpreadsheet_ReturnsSuccessWithWarning()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body>" +
            "</office:body>" +
            "</office:document>";
        var path = WriteTemp("parser-no-spreadsheet.fods", xml);

        var result = _parser.Parse(path);
        Assert.True(result.IsSuccess);
        Assert.Empty(result.Sheets);
        Assert.NotEmpty(result.Warnings); // "No sheets found in document."
    }

    /// <summary>
    /// C9-SEC-FODS-01: Parser rejects XML with DTD declarations (security guard — FACT-FODS-009).
    /// FodsParser uses DtdProcessing.Prohibit and XmlResolver = null.
    /// A file with an internal DTD subset must be rejected rather than processed.
    /// </summary>
    [Fact]
    public void Parser_XmlWithDtd_RejectsWithError()
    {
        // XML with an internal DTD subset — must be rejected by DtdProcessing.Prohibit
        const string xmlWithDtd =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<!DOCTYPE fods [<!ELEMENT fods ANY>]>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "</office:document>";
        var path = WriteTemp("dtd-injection.fods", xmlWithDtd);
        var result = _parser.Parse(path);
        Assert.False(result.IsSuccess);
        Assert.NotEmpty(result.Errors);
    }

    /// <summary>
    /// C9-SEC-FODS-02: CSV exporter handles FODS with no sheets (exports empty CSV).
    /// </summary>
    [Fact]
    public void CsvExporter_NoSheets_ExportsEmptyCsv()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:spreadsheet>" +
            "</office:spreadsheet></office:body>" +
            "</office:document>";
        var fodsPath = WriteTemp("no-sheets.fods", xml);
        var csvPath = Path.Combine(_tempDir, "no-sheets.csv");

        var result = FodsCsvExporter.ExportFirstSheetToCsv(fodsPath, csvPath);
        Assert.Equal("exported_empty_no_sheets", result.Status);
        Assert.Equal(0, result.RowsExported);
    }
}
