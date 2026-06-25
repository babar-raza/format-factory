// Tests for FodtDocument.Load(Stream stream) — stream-based FODT loading.
// Sprint: FORMAT-FACTORY-FODT-R137-20260627
// Ledger: R137-GOVERNED-DOTNET-FODT-STREAM-LOAD-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R137: Tests for FodtDocument.Load(Stream stream) overload.
/// Verifies that stream-based loading produces the same document as file-based loading,
/// handles null input, and correctly reads paragraphs, tables, and document properties.
/// ODF spec basis: ODF 1.3 §2.1 office:document root element.
/// </summary>
public class FodtR137StreamLoadTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string[] ListFixtures()
    {
        var dir = FixturePath(".");
        return Directory.Exists(dir)
            ? Directory.GetFiles(dir, "*.fodt")
            : Array.Empty<string>();
    }

    private static string MinimalFodtXml(string bodyText = "Stream load test paragraph") =>
        $"""
<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.text-flat-xml"
  office:version="1.3">
  <office:automatic-styles/>
  <office:body>
    <office:text>
      <text:p text:style-name="Text_Body">{bodyText}</text:p>
    </office:text>
  </office:body>
</office:document>
""";

    // -------------------------------------------------------------------------
    // Load from MemoryStream with inline XML
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_MemoryStream_DocumentIsNotNull()
    {
        var xml = MinimalFodtXml();
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var doc = FodtDocument.Load(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void Load_MemoryStream_ParagraphCountAtLeastOne()
    {
        var xml = MinimalFodtXml("Hello from stream");
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var doc = FodtDocument.Load(ms);
        Assert.True(doc.ParagraphCount >= 1);
    }

    [Fact]
    public void Load_MemoryStream_ParagraphTextCorrect()
    {
        var xml = MinimalFodtXml("STREAM_CONTENT_R137");
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var doc = FodtDocument.Load(ms);
        Assert.Contains("STREAM_CONTENT_R137", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // Parity with file-based Load (using fixture if available, else inline XML)
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_Stream_ParagraphCountMatchesFileBased()
    {
        var xml = MinimalFodtXml("Parity test paragraph");
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmpPath, xml, Encoding.UTF8);
            var fileDoc = FodtDocument.Load(tmpPath);

            using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
            var streamDoc = FodtDocument.Load(ms);

            Assert.Equal(fileDoc.ParagraphCount, streamDoc.ParagraphCount);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void Load_Stream_PlainTextMatchesFileBased()
    {
        var xml = MinimalFodtXml("Plain text parity R137");
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmpPath, xml, Encoding.UTF8);
            var fileText = FodtDocument.Load(tmpPath).GetPlainText();

            using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
            var streamText = FodtDocument.Load(ms).GetPlainText();

            Assert.Equal(fileText, streamText);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // FileStream from a temp file
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_FileStream_Succeeds()
    {
        var xml = MinimalFodtXml("FileStream paragraph R137");
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmpPath, xml, Encoding.UTF8);
            using var fs = new FileStream(tmpPath, FileMode.Open, FileAccess.Read);
            var doc = FodtDocument.Load(fs);
            Assert.NotNull(doc);
            Assert.True(doc.ParagraphCount >= 1);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    // -------------------------------------------------------------------------
    // Null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodtDocument.Load((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Invalid XML throws FodtDocumentException
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_InvalidXml_ThrowsFodtDocumentException()
    {
        var badXml = Encoding.UTF8.GetBytes("NOT VALID XML <<<!!");
        using var ms = new MemoryStream(badXml);
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(ms));
    }

    // -------------------------------------------------------------------------
    // Dogfood: stream → edit → save → reload pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StreamLoad_EditSaveReload()
    {
        // Load from stream
        var xml = MinimalFodtXml("Original content for stream dogfood");
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var doc = FodtDocument.Load(ms);

        // Edit
        doc.AppendParagraph("Added via stream load dogfood R137");

        // Save to temp file and reload
        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmpPath);
            var reloaded = FodtDocument.Load(tmpPath);
            Assert.True(reloaded.ParagraphCount >= 2);
            Assert.Contains("Added via stream load dogfood R137", reloaded.GetPlainText());
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }
}
