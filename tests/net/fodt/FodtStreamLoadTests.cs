// Tests for FodtDocument.Load(Stream) overload (QF-3-002, TC-QF-R-005)

using System;
using System.IO;
using System.Text;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtStreamLoadTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void Load_Stream_LoadsDocument()
    {
        using var stream = File.OpenRead(SampleFodtPath);
        var doc = FodtDocument.Load(stream);
        Assert.NotNull(doc);
        Assert.NotNull(doc.Paragraphs);
    }

    [Fact]
    public void Load_Stream_ProducesSameParagraphCount_AsFileLoad()
    {
        var fileDoc = FodtDocument.Load(SampleFodtPath);
        using var stream = File.OpenRead(SampleFodtPath);
        var streamDoc = FodtDocument.Load(stream);
        Assert.Equal(fileDoc.Paragraphs.Count, streamDoc.Paragraphs.Count);
    }

    [Fact]
    public void Load_Stream_MemoryStream_Works()
    {
        byte[] bytes = File.ReadAllBytes(SampleFodtPath);
        using var ms = new MemoryStream(bytes);
        var doc = FodtDocument.Load(ms);
        Assert.NotNull(doc);
        Assert.NotNull(doc.Paragraphs);
    }

    [Fact]
    public void Load_NullStream_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodtDocument.Load((Stream)null!));
    }

    [Fact]
    public void Load_Stream_DtdContent_ThrowsFodtDocumentException()
    {
        const string dtdXml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>" +
            "<office:document xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\">" +
            "<office:body><office:text/></office:body></office:document>";
        var bytes = Encoding.UTF8.GetBytes(dtdXml);
        using var ms = new MemoryStream(bytes);
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(ms));
    }
}
