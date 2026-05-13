// FodtDocumentRoundtripTests -- Lane E: FODT load/save no-edit roundtrip
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using System.Xml;
using Xunit;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtDocumentRoundtripTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    // ------------------------------------------------------------------
    // RT-01: Load minimal FODT from fixture — succeeds
    // ------------------------------------------------------------------
    [Fact]
    public void Load_MinimalFodtFixture_Succeeds()
    {
        var path = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(path);

        Assert.Equal("application/vnd.oasis.opendocument.text-flat-xml", doc.MimeType);
        Assert.Equal("1.3", doc.OdfVersion);
        Assert.NotNull(doc.Body);
    }

    // ------------------------------------------------------------------
    // RT-02: Paragraph count correct
    // ------------------------------------------------------------------
    [Fact]
    public void Load_MinimalFodtFixture_CorrectParagraphCount()
    {
        var path = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(path);

        // 3 text:p + 1 text:h = 4 top-level paragraph/heading elements
        Assert.Equal(4, doc.Paragraphs.Count);
    }

    // ------------------------------------------------------------------
    // RT-03: No-edit roundtrip — paragraph count preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_NoEdit_PreservesParagraphCount()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);
        var originalCount = doc.Paragraphs.Count;

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal(originalCount, reloaded.Paragraphs.Count);
    }

    // ------------------------------------------------------------------
    // RT-04: No-edit roundtrip — paragraph text preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_NoEdit_PreservesParagraphText()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("Hello, world.",              reloaded.Paragraphs[0].Text);
        Assert.Equal("Second paragraph.",          reloaded.Paragraphs[1].Text);
        Assert.Equal("A Heading",                  reloaded.Paragraphs[2].Text);
        Assert.Equal("Third paragraph after heading.", reloaded.Paragraphs[3].Text);
    }

    // ------------------------------------------------------------------
    // RT-05: Saved file is valid XML
    // ------------------------------------------------------------------
    [Fact]
    public void Save_NoEdit_ProducesValidXml()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit };
        using var reader = XmlReader.Create(tmp.Path, settings);
        while (reader.Read()) { }
    }

    // ------------------------------------------------------------------
    // RT-06: Saved file root is ODF office:document
    // ------------------------------------------------------------------
    [Fact]
    public void Save_NoEdit_RootIsOdfDocument()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("office:document", content);
        Assert.Contains("urn:oasis:names:tc:opendocument:xmlns:office:1.0", content);
    }

    // ------------------------------------------------------------------
    // RT-07: Save is not a no-op
    // ------------------------------------------------------------------
    [Fact]
    public void Save_WritesNonEmptyFile()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var info = new FileInfo(tmp.Path);
        Assert.True(info.Length > 0, "Save() wrote an empty file — must not be a no-op.");
        Assert.True(info.Length > 100, "Save() output is suspiciously small.");
    }

    // ------------------------------------------------------------------
    // RT-08: Load null path throws FodtDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_NullPath_ThrowsFodtDocumentException()
    {
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(null!));
    }

    // ------------------------------------------------------------------
    // RT-09: Load missing file throws FodtDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_MissingFile_ThrowsFodtDocumentException()
    {
        Assert.Throws<FodtDocumentException>(() =>
            FodtDocument.Load("/does/not/exist.fodt"));
    }

    // ------------------------------------------------------------------
    // RT-10: DTD file throws FodtDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_DtdFile_ThrowsFodtDocumentException()
    {
        const string dtdXml =
            "<?xml version=\"1.0\"?>" +
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>" +
            "<root>&xxe;</root>";
        using var tmp = new TempFile(dtdXml);
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(tmp.Path));
    }

    // ------------------------------------------------------------------
    // RT-11: Load file too large throws FodtDocumentException
    // ------------------------------------------------------------------
    [Fact]
    public void Load_FileTooLarge_ThrowsFodtDocumentException()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        Assert.Throws<FodtDocumentException>(() =>
            FodtDocument.Load(srcPath, maxFileSizeBytes: 10));
    }

    // ------------------------------------------------------------------
    // RT-12: Heading detected correctly (IsHeading)
    // ------------------------------------------------------------------
    [Fact]
    public void Load_Heading_IsHeadingTrue()
    {
        var path = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(path);

        // Index 2 is text:h
        Assert.True(doc.Paragraphs[2].IsHeading);
        Assert.False(doc.Paragraphs[0].IsHeading);
    }

    // ------------------------------------------------------------------
    // RT-13: Inline minimal FODT — roundtrip succeeds
    // ------------------------------------------------------------------
    [Fact]
    public void Roundtrip_InlineMinimalFodt_Succeeds()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:text>" +
            "<text:p>Only paragraph</text:p>" +
            "</office:text></office:body>" +
            "</office:document>";

        using var src = new TempFile(xml);
        var doc = FodtDocument.Load(src.Path);

        using var out1 = new TempFile();
        doc.Save(out1.Path);

        var reloaded = FodtDocument.Load(out1.Path);
        Assert.Single(reloaded.Paragraphs);
        Assert.Equal("Only paragraph", reloaded.Paragraphs[0].Text);
    }

    // ------------------------------------------------------------------
    // Helper
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
