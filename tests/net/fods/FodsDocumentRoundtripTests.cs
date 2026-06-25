// FodsDocumentRoundtripTests -- Lane C: FODS load/save no-edit roundtrip
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using System.Xml;
using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsDocumentRoundtripTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    // ------------------------------------------------------------------
    // RT-01: Load minimal FODS from fixture — succeeds
    // ------------------------------------------------------------------
    [Fact]
    public void Load_MinimalFodsFixture_Succeeds()
    {
        var path = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(path);

        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet-flat-xml",
                     doc.MimeType);
        Assert.Equal("1.3", doc.OdfVersion);
        Assert.Single(doc.Sheets);
        Assert.Equal("Sheet1", doc.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // RT-02: No-edit roundtrip — sheet count and name preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_NoEdit_PreservesSheetStructure()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);

        Assert.Single(reloaded.Sheets);
        Assert.Equal("Sheet1", reloaded.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // RT-03: No-edit roundtrip — row count preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_NoEdit_PreservesRowCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal(2, reloaded.Sheets[0].Rows.Count);
    }

    // ------------------------------------------------------------------
    // RT-04: No-edit roundtrip — cell values preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_NoEdit_PreservesCellValues()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        var row0 = reloaded.Sheets[0].Rows[0];
        Assert.Equal("Hello",  row0.Cells[0].Value);
        Assert.Equal("World",  row0.Cells[1].Value);
        var row1 = reloaded.Sheets[0].Rows[1];
        Assert.Equal("Row2Cell1", row1.Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // RT-05: Saved file is valid XML
    // ------------------------------------------------------------------
    [Fact]
    public void Save_NoEdit_ProducesValidXml()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        // Should not throw
        var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit };
        using var reader = XmlReader.Create(tmp.Path, settings);
        while (reader.Read()) { }
    }

    // ------------------------------------------------------------------
    // RT-06: Saved file root element is ODF office:document
    // ------------------------------------------------------------------
    [Fact]
    public void Save_NoEdit_RootIsOdfDocument()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("office:document", content);
        Assert.Contains("urn:oasis:names:tc:opendocument:xmlns:office:1.0", content);
    }

    // ------------------------------------------------------------------
    // RT-07: Save is not a no-op — file is non-empty
    // ------------------------------------------------------------------
    [Fact]
    public void Save_WritesNonEmptyFile()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var info = new FileInfo(tmp.Path);
        Assert.True(info.Length > 0, "Save() wrote an empty file — must not be a no-op.");
        Assert.True(info.Length > 100, "Save() output is suspiciously small.");
    }

    // ------------------------------------------------------------------
    // RT-08: Load null path throws FodsDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_NullPath_ThrowsFodsDocumentException()
    {
        Assert.Throws<FodsDocumentException>(() => FodsDocument.Load((string)null!));
    }

    // ------------------------------------------------------------------
    // RT-09: Load missing file throws FodsDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_MissingFile_ThrowsFodsDocumentException()
    {
        Assert.Throws<FodsDocumentException>(() =>
            FodsDocument.Load("/does/not/exist.fods"));
    }

    // ------------------------------------------------------------------
    // RT-10: Load DTD file throws FodsDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_DtdFile_ThrowsFodsDocumentException()
    {
        const string dtdXml =
            "<?xml version=\"1.0\"?>" +
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>" +
            "<root>&xxe;</root>";
        using var tmp = new TempFile(dtdXml);
        Assert.Throws<FodsDocumentException>(() => FodsDocument.Load(tmp.Path));
    }

    // ------------------------------------------------------------------
    // RT-11: Load file too large throws FodsDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_FileTooLarge_ThrowsFodsDocumentException()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        Assert.Throws<FodsDocumentException>(() =>
            FodsDocument.Load(srcPath, maxFileSizeBytes: 10));
    }

    // ------------------------------------------------------------------
    // RT-12: Inline minimal FODS string — roundtrip succeeds
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_InlineMinimalFods_Succeeds()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:spreadsheet>" +
            "<table:table table:name=\"Data\"/>" +
            "</office:spreadsheet></office:body>" +
            "</office:document>";

        using var src = new TempFile(xml);
        var doc = FodsDocument.Load(src.Path);

        using var out1 = new TempFile();
        doc.Save(out1.Path);

        var reloaded = FodsDocument.Load(out1.Path);
        Assert.Single(reloaded.Sheets);
        Assert.Equal("Data", reloaded.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // RT-13: Reload after two saves returns same structure
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_SaveTwice_StillValid()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        using var tmp1 = new TempFile();
        doc.Save(tmp1.Path);

        var doc2 = FodsDocument.Load(tmp1.Path);
        using var tmp2 = new TempFile();
        doc2.Save(tmp2.Path);

        var reloaded = FodsDocument.Load(tmp2.Path);
        Assert.Single(reloaded.Sheets);
        Assert.Equal("Sheet1", reloaded.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // Helper: temporary file
    // ------------------------------------------------------------------
    private sealed class TempFile : IDisposable
    {
        public string Path { get; }

        public TempFile(string content)
        {
            Path = System.IO.Path.GetTempFileName();
            File.WriteAllText(Path, content, System.Text.Encoding.UTF8);
        }

        public TempFile()
        {
            Path = System.IO.Path.GetTempFileName();
        }

        public void Dispose()
        {
            if (File.Exists(Path)) File.Delete(Path);
        }
    }
}
