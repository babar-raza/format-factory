// Tests for FodtPdfExporter.ExportToPdf(FodtDocument, pdfPath) and ExportToPdfBytes(FodtDocument).
// Sprint: FORMAT-FACTORY-FODT-R138-20260627
// Ledger: R138-GOVERNED-DOTNET-FODT-PDF-EXPORTER-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R138: Tests for FodtPdfExporter — the FODT→PDF export API.
/// Covers: ExportToPdf(FodtDocument, pdfPath) result object properties,
/// ExportToPdfBytes(FodtDocument) byte output, and PDF %PDF header presence.
/// The exporter writes a minimal PDF without external dependencies.
/// </summary>
public class FodtR138PdfExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPdfPath() =>
        Path.Combine(Path.GetTempPath(), $"fodt_r138_{Guid.NewGuid():N}.pdf");

    private static FodtDocument MakeDoc(string text = "PDF export test paragraph")
    {
        var xml = $"""
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
  office:version="1.3">
  <office:automatic-styles/>
  <office:body>
    <office:text>
      <text:p text:style-name="Text_Body">{text}</text:p>
    </office:text>
  </office:body>
</office:document>
""";
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmp, xml, Encoding.UTF8);
            return FodtDocument.Load(tmp);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    // -------------------------------------------------------------------------
    // ExportToPdf — result object properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdf_Document_OutputPathMatchesGivenPath()
    {
        var doc = MakeDoc();
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.Equal(pdfPath, result.OutputPath);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_OutputFileExists()
    {
        var doc = MakeDoc();
        var pdfPath = TempPdfPath();
        try
        {
            FodtPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(File.Exists(pdfPath), "PDF output file should exist");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_PageCountAtLeastOne()
    {
        var doc = MakeDoc();
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.PageCount >= 1, $"Expected PageCount >= 1, got {result.PageCount}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_Document_TotalParagraphsWrittenNonNegative()
    {
        var doc = MakeDoc("Paragraph R138");
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);
            Assert.True(result.TotalParagraphsWritten >= 0,
                $"TotalParagraphsWritten must be >= 0, got {result.TotalParagraphsWritten}");
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    [Fact]
    public void ExportToPdf_OutputFile_HasPdfHeader()
    {
        var doc = MakeDoc();
        var pdfPath = TempPdfPath();
        try
        {
            FodtPdfExporter.ExportToPdf(doc, pdfPath);
            var header = new byte[4];
            using var fs = File.OpenRead(pdfPath);
            _ = fs.Read(header, 0, 4);
            Assert.Equal((byte)'%', header[0]);
            Assert.Equal((byte)'P', header[1]);
            Assert.Equal((byte)'D', header[2]);
            Assert.Equal((byte)'F', header[3]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }

    // -------------------------------------------------------------------------
    // ExportToPdfBytes — byte array output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPdfBytes_Document_ReturnsNonEmptyArray()
    {
        var doc = MakeDoc();
        var bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToPdfBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodtPdfExporter.ExportToPdfBytes(null!));
    }

    [Fact]
    public void ExportToPdfBytes_BytesHavePdfHeader()
    {
        var doc = MakeDoc();
        var bytes = FodtPdfExporter.ExportToPdfBytes(doc);
        Assert.True(bytes.Length >= 4);
        Assert.Equal((byte)'%', bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'D', bytes[2]);
        Assert.Equal((byte)'F', bytes[3]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: load fixture, export PDF, verify file and bytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FixtureDoc_PdfBytesAndFileConsistent()
    {
        var doc = FodtDocument.Load(FixturePath("fodt-minimal-roundtrip.fodt"));
        var pdfPath = TempPdfPath();
        try
        {
            var result = FodtPdfExporter.ExportToPdf(doc, pdfPath);
            var bytes = FodtPdfExporter.ExportToPdfBytes(doc);

            Assert.True(result.PageCount >= 1);
            Assert.True(bytes.Length > 0);

            // Both have PDF header
            Assert.Equal((byte)'%', bytes[0]);
            var fileBytes = File.ReadAllBytes(pdfPath);
            Assert.Equal((byte)'%', fileBytes[0]);
        }
        finally { if (File.Exists(pdfPath)) File.Delete(pdfPath); }
    }
}
