// FormatFactory.Fods Tests -- FodsOdsExporter Prototype Tests
// Sprint: product-deepening-fods-ods-export-20260616
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the FODS → ODS export prototype.
///
/// Covers:
///   - Basic ODS export from file path
///   - Export from FodsDocument object
///   - ExportToOdsBytes (in-memory)
///   - ODS archive structure (ZIP format, mimetype entry)
///   - Mimetype entry is STORED (not deflated) — ODF spec §3.1.1
///   - Mimetype entry content is correct
///   - META-INF/manifest.xml present
///   - content.xml present with ODF XML content
///   - Sheet name appears in content.xml
///   - Cell values appear in content.xml
///   - Empty document produces valid ODS archive
///   - Multi-sheet document export
///   - Result metadata: SheetCount, TotalRowsExported, TotalCellsExported
///   - Null argument guards
///   - XML escaping for special characters in cell values and sheet names
/// </summary>
public class FodsOdsExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsOdsExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"fods-ods-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        try { Directory.Delete(_tempDir, recursive: true); } catch { /* best-effort */ }
    }

    // -------------------------------------------------------------------------
    // Basic export tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_FromFilePath_CreatesNonEmptyFile()
    {
        var odsPath = Path.Combine(_tempDir, "export.ods");
        var result = FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        Assert.True(File.Exists(odsPath), "ODS file should be created");
        Assert.True(new FileInfo(odsPath).Length > 0, "ODS file should be non-empty");
        Assert.Equal(odsPath, result.OutputPath);
    }

    [Fact]
    public void ExportToOds_FromFilePath_IsValidZipArchive()
    {
        var odsPath = Path.Combine(_tempDir, "valid.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        // ODS must be readable as a ZIP archive
        using var archive = ZipFile.OpenRead(odsPath);
        Assert.NotNull(archive);
    }

    [Fact]
    public void ExportToOds_FromFilePath_ContainsMimetypeEntry()
    {
        var odsPath = Path.Combine(_tempDir, "mime.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        using var archive = ZipFile.OpenRead(odsPath);
        var mimeEntry = archive.GetEntry("mimetype");
        Assert.NotNull(mimeEntry);
    }

    [Fact]
    public void ExportToOds_FromFilePath_MimetypeContentIsCorrect()
    {
        var odsPath = Path.Combine(_tempDir, "mime2.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        using var archive = ZipFile.OpenRead(odsPath);
        var mimeEntry = archive.GetEntry("mimetype")!;
        using var reader = new StreamReader(mimeEntry.Open(), Encoding.UTF8);
        var content = reader.ReadToEnd();
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet", content);
    }

    [Fact]
    public void ExportToOds_FromFilePath_MimetypeIsStoredNotDeflated()
    {
        var odsPath = Path.Combine(_tempDir, "stored.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        using var archive = ZipFile.OpenRead(odsPath);
        var mimeEntry = archive.GetEntry("mimetype")!;
        // ODF spec §3.1.1: mimetype MUST be STORED (no compression)
        Assert.Equal(CompressionMethodValues.Stored, mimeEntry.CompressionMethod());
    }

    [Fact]
    public void ExportToOds_FromFilePath_ContainsManifestXml()
    {
        var odsPath = Path.Combine(_tempDir, "manifest.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        using var archive = ZipFile.OpenRead(odsPath);
        var manifestEntry = archive.GetEntry("META-INF/manifest.xml");
        Assert.NotNull(manifestEntry);
    }

    [Fact]
    public void ExportToOds_FromFilePath_ContainsContentXml()
    {
        var odsPath = Path.Combine(_tempDir, "content.ods");
        FodsOdsExporter.ExportToOds(MinimalFods, odsPath);

        using var archive = ZipFile.OpenRead(odsPath);
        var contentEntry = archive.GetEntry("content.xml");
        Assert.NotNull(contentEntry);
    }

    // -------------------------------------------------------------------------
    // ODS content tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_ContentXmlContainsOdfNamespace()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Test");

        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        using var ms = new MemoryStream(bytes);
        using var archive = new ZipArchive(ms, ZipArchiveMode.Read);
        var contentEntry = archive.GetEntry("content.xml")!;
        using var reader = new StreamReader(contentEntry.Open(), Encoding.UTF8);
        var content = reader.ReadToEnd();

        Assert.Contains("office:document-content", content, StringComparison.Ordinal);
        Assert.Contains("office:spreadsheet", content, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToOdsBytes_ContentXmlContainsSheetName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MyUniqueSheet");

        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        using var ms = new MemoryStream(bytes);
        using var archive = new ZipArchive(ms, ZipArchiveMode.Read);
        var contentEntry = archive.GetEntry("content.xml")!;
        using var reader = new StreamReader(contentEntry.Open(), Encoding.UTF8);
        var content = reader.ReadToEnd();

        Assert.Contains("MyUniqueSheet", content, StringComparison.Ordinal);
    }

    [Fact]
    public void ExportToOdsBytes_ContentXmlContainsCellValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.InsertRowWithValues("Data", 0, new[] { "UniqueCell42" });

        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        using var ms = new MemoryStream(bytes);
        using var archive = new ZipArchive(ms, ZipArchiveMode.Read);
        var contentEntry = archive.GetEntry("content.xml")!;
        using var reader = new StreamReader(contentEntry.Open(), Encoding.UTF8);
        var content = reader.ReadToEnd();

        Assert.Contains("UniqueCell42", content, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Result metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_SingleSheet_MetadataIsCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "C", "" });

        var odsPath = Path.Combine(_tempDir, "meta.ods");
        var result = FodsOdsExporter.ExportToOds(doc, odsPath);

        Assert.Equal(1, result.SheetCount);
        Assert.Equal(2, result.TotalRowsExported);
        Assert.Equal(3, result.TotalCellsExported); // "A", "B", "C" (empty cell not counted)
    }

    [Fact]
    public void ExportToOds_TwoSheets_MetadataHasTwoSheets()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.InsertRowWithValues("Alpha", 0, new[] { "X" });
        doc.InsertRowWithValues("Beta", 0, new[] { "Y", "Z" });

        var odsPath = Path.Combine(_tempDir, "twosheets.ods");
        var result = FodsOdsExporter.ExportToOds(doc, odsPath);

        Assert.Equal(2, result.SheetCount);
        Assert.Equal(2, result.TotalRowsExported);
        Assert.Equal(3, result.TotalCellsExported); // X + Y + Z
    }

    // -------------------------------------------------------------------------
    // Empty document
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_EmptyDocument_ProducesValidOdsArchive()
    {
        var doc = FodsDocument.CreateNew();
        var odsPath = Path.Combine(_tempDir, "empty.ods");
        var result = FodsOdsExporter.ExportToOds(doc, odsPath);

        Assert.Equal(0, result.SheetCount);
        Assert.Equal(0, result.TotalRowsExported);
        using var archive = ZipFile.OpenRead(odsPath);
        Assert.NotNull(archive.GetEntry("mimetype"));
        Assert.NotNull(archive.GetEntry("content.xml"));
    }

    // -------------------------------------------------------------------------
    // In-memory export
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_ReturnsNonEmptyArray()
    {
        var doc = FodsDocument.Load(MinimalFods);
        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);

        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToOdsBytes_IsValidZipArchive()
    {
        var doc = FodsDocument.Load(MinimalFods);
        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);

        using var ms = new MemoryStream(bytes);
        using var archive = new ZipArchive(ms, ZipArchiveMode.Read);
        Assert.NotNull(archive);
    }

    // -------------------------------------------------------------------------
    // XML escaping
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOdsBytes_XmlSpecialCharsInCellAreEscaped()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet");
        doc.InsertRowWithValues("Sheet", 0, new[] { "A<B>&C" });

        byte[] bytes = FodsOdsExporter.ExportToOdsBytes(doc);
        using var ms = new MemoryStream(bytes);
        using var archive = new ZipArchive(ms, ZipArchiveMode.Read);
        var contentEntry = archive.GetEntry("content.xml")!;
        using var reader = new StreamReader(contentEntry.Open(), Encoding.UTF8);
        var content = reader.ReadToEnd();

        // XML special chars must be escaped
        Assert.Contains("A&lt;B&gt;&amp;C", content, StringComparison.Ordinal);
    }

    // -------------------------------------------------------------------------
    // Null / invalid argument guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToOds_NullFilePath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOds((string)null!, Path.Combine(_tempDir, "x.ods")));
    }

    [Fact]
    public void ExportToOds_NullOutputPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOds(MinimalFods, null!));
    }

    [Fact]
    public void ExportToOds_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOds((FodsDocument)null!, Path.Combine(_tempDir, "x.ods")));
    }

    [Fact]
    public void ExportToOdsBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsOdsExporter.ExportToOdsBytes(null!));
    }
}

/// <summary>Extension methods for test assertions on ZipArchiveEntry.</summary>
internal static class ZipArchiveEntryExtensions
{
    /// <summary>Returns the compression method used for this entry.</summary>
    public static CompressionMethodValues CompressionMethod(this ZipArchiveEntry entry)
    {
        // ZipArchiveEntry.CompressionMethodValues is internal in .NET
        // We use length comparison: for STORED, CompressedLength == Length
        return entry.CompressedLength == entry.Length
            ? CompressionMethodValues.Stored
            : CompressionMethodValues.Deflated;
    }
}

/// <summary>Simple enum for compression method values used in tests.</summary>
internal enum CompressionMethodValues
{
    Stored = 0,
    Deflated = 8,
}
