// FodtDocumentEditTests -- Lane F: FODT edit-one-paragraph save vertical slice
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using Xunit;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtDocumentEditTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    // ------------------------------------------------------------------
    // ED-01: Edit existing paragraph — text persists after save/reload
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_ExistingParagraph_PersistsAfterSaveReload()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        doc.Paragraphs[0].SetText("TestEditParagraph");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("TestEditParagraph", reloaded.Paragraphs[0].Text);
    }

    // ------------------------------------------------------------------
    // ED-02: Edit one paragraph — other paragraphs preserved
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_OneParagraph_DoesNotCorruptOthers()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        doc.Paragraphs[0].SetText("CHANGED");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("Second paragraph.", reloaded.Paragraphs[1].Text);
        Assert.Equal("A Heading",         reloaded.Paragraphs[2].Text);
    }

    // ------------------------------------------------------------------
    // ED-03: Edit does not remove metadata (mimetype, version)
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_Paragraph_PreservesDocumentMetadata()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        doc.Paragraphs[0].SetText("AnyValue");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("application/vnd.oasis.opendocument.text-flat-xml", reloaded.MimeType);
        Assert.Equal("1.3", reloaded.OdfVersion);
    }

    // ------------------------------------------------------------------
    // ED-04: Edit result appears in saved XML with ODF text:p representation
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_SavedXml_ContainsEditedTextInTextP()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        doc.Paragraphs[0].SetText("VerticalSliceParagraph");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("VerticalSliceParagraph", content);
        Assert.Contains("text:p", content);
    }

    // ------------------------------------------------------------------
    // ED-05: Edit heading — persists after save/reload, still isHeading
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_Heading_PersistsAfterSaveReload()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        // Paragraph[2] is a heading
        Assert.True(doc.Paragraphs[2].IsHeading);
        doc.Paragraphs[2].SetText("Edited Heading");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("Edited Heading", reloaded.Paragraphs[2].Text);
        Assert.True(reloaded.Paragraphs[2].IsHeading);
    }

    // ------------------------------------------------------------------
    // ED-06: SetText null throws ArgumentNullException
    // ------------------------------------------------------------------
    [Fact]
    public void SetText_Null_ThrowsArgumentNullException()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);
        Assert.Throws<ArgumentNullException>(() =>
            doc.Paragraphs[0].SetText(null!));
    }

    // ------------------------------------------------------------------
    // ED-07: Edit handles XML special characters (escaping)
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_XmlSpecialChars_EscapedCorrectly()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);

        doc.Paragraphs[0].SetText("<special> & \"chars\"");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal("<special> & \"chars\"", reloaded.Paragraphs[0].Text);
    }

    // ------------------------------------------------------------------
    // ED-08: Edit in-memory only — not in original file before save
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_InMemoryChange_NotInOriginalFileBeforeSave()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);
        var original = doc.Paragraphs[0].Text;

        doc.Paragraphs[0].SetText("InMemoryOnly");

        // Reload original file — should still have old value
        var doc2 = FodtDocument.Load(srcPath);
        Assert.Equal(original, doc2.Paragraphs[0].Text);
    }

    // ------------------------------------------------------------------
    // ED-09: Paragraph count unchanged after edit
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_ParagraphCount_UnchangedAfterSaveReload()
    {
        var srcPath = Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");
        var doc = FodtDocument.Load(srcPath);
        var originalCount = doc.Paragraphs.Count;

        doc.Paragraphs[0].SetText("X");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodtDocument.Load(tmp.Path);
        Assert.Equal(originalCount, reloaded.Paragraphs.Count);
    }

    // ------------------------------------------------------------------
    // ED-10: Inline minimal FODT — edit and reload
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_InlineMinimalFodt_PersistsAfterReload()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.text-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:text>" +
            "<text:p>Original text</text:p>" +
            "</office:text></office:body>" +
            "</office:document>";

        using var src = new TempFile(xml);
        var doc = FodtDocument.Load(src.Path);
        doc.Paragraphs[0].SetText("Replaced text");

        using var out1 = new TempFile();
        doc.Save(out1.Path);

        var reloaded = FodtDocument.Load(out1.Path);
        Assert.Equal("Replaced text", reloaded.Paragraphs[0].Text);
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
