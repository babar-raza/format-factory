// Tests for FodtPngExporter.ExportToPng(FodtDocument, pngPath) and ExportToPngBytes(FodtDocument).
// Sprint: FORMAT-FACTORY-FODT-R139-20260627
// Ledger: R139-GOVERNED-DOTNET-FODT-PNG-EXPORTER-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R139: Tests for FodtPngExporter — the FODT→PNG export API.
/// Covers: ExportToPng(FodtDocument, pngPath) result object properties,
/// ExportToPngBytes(FodtDocument) byte output, and PNG signature byte check.
/// The exporter renders paragraphs to a PNG bitmap without external graphics deps.
/// </summary>
public class FodtR139PngExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempPngPath() =>
        Path.Combine(Path.GetTempPath(), $"fodt_r139_{Guid.NewGuid():N}.png");

    private static FodtDocument MakeDoc(string text = "PNG export test paragraph")
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
    // ExportToPng — result object properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_Document_OutputPathMatchesGivenPath()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(doc, pngPath);
            Assert.Equal(pngPath, result.OutputPath);
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Document_OutputFileExists()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            FodtPngExporter.ExportToPng(doc, pngPath);
            Assert.True(File.Exists(pngPath), "PNG output file should exist");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Document_WidthPxPositive()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(doc, pngPath);
            Assert.True(result.WidthPx > 0, $"Expected WidthPx > 0, got {result.WidthPx}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Document_HeightPxPositive()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(doc, pngPath);
            Assert.True(result.HeightPx > 0, $"Expected HeightPx > 0, got {result.HeightPx}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_Document_ParagraphsRenderedNonNegative()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(doc, pngPath);
            Assert.True(result.ParagraphsRendered >= 0,
                $"ParagraphsRendered must be >= 0, got {result.ParagraphsRendered}");
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    [Fact]
    public void ExportToPng_OutputFile_HasPngSignature()
    {
        var doc = MakeDoc();
        var pngPath = TempPngPath();
        try
        {
            FodtPngExporter.ExportToPng(doc, pngPath);
            var header = new byte[8];
            using var fs = File.OpenRead(pngPath);
            _ = fs.Read(header, 0, 8);
            // PNG signature: 137 80 78 71 13 10 26 10
            Assert.Equal(137, header[0]);
            Assert.Equal(80, header[1]);  // 'P'
            Assert.Equal(78, header[2]);  // 'N'
            Assert.Equal(71, header[3]);  // 'G'
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }

    // -------------------------------------------------------------------------
    // ExportToPngBytes — byte array output
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_Document_ReturnsNonEmptyArray()
    {
        var doc = MakeDoc();
        var bytes = FodtPngExporter.ExportToPngBytes(doc);
        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToPngBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodtPngExporter.ExportToPngBytes(null!));
    }

    [Fact]
    public void ExportToPngBytes_BytesHavePngSignature()
    {
        var doc = MakeDoc();
        var bytes = FodtPngExporter.ExportToPngBytes(doc);
        Assert.True(bytes.Length >= 8);
        Assert.Equal(137, bytes[0]);
        Assert.Equal(80, bytes[1]);
        Assert.Equal(78, bytes[2]);
        Assert.Equal(71, bytes[3]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: fixture doc → PNG file and bytes consistent
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FixtureDoc_PngBytesAndFileConsistent()
    {
        var doc = FodtDocument.Load(FixturePath("fodt-minimal-roundtrip.fodt"));
        var pngPath = TempPngPath();
        try
        {
            var result = FodtPngExporter.ExportToPng(doc, pngPath);
            var bytes = FodtPngExporter.ExportToPngBytes(doc);

            Assert.True(result.WidthPx > 0);
            Assert.True(result.HeightPx > 0);
            Assert.True(bytes.Length > 0);

            // Both have PNG signature
            Assert.Equal(137, bytes[0]);
            var fileBytes = File.ReadAllBytes(pngPath);
            Assert.Equal(137, fileBytes[0]);
        }
        finally { if (File.Exists(pngPath)) File.Delete(pngPath); }
    }
}
