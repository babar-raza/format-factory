// FodsDocumentEditTests -- Lane D: FODS edit-one-cell save vertical slice
// COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

using System;
using System.IO;
using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public class FodsDocumentEditTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    // ------------------------------------------------------------------
    // ED-01: Edit existing text cell — value persists after save/reload
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_ExistingTextCell_PersistsAfterSaveReload()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        // Edit first cell of first row
        doc.Sheets[0].Rows[0].Cells[0].SetText("TestEdit");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal("TestEdit", reloaded.Sheets[0].Rows[0].Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // ED-02: Edit does not disturb other cells
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_OneCell_DoesNotCorruptOtherCells()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        doc.Sheets[0].Rows[0].Cells[0].SetText("CHANGED");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        // Second cell of first row should still be "World"
        Assert.Equal("World",  reloaded.Sheets[0].Rows[0].Cells[1].Value);
        // First cell of second row should still be "Row2Cell1"
        Assert.Equal("Row2Cell1", reloaded.Sheets[0].Rows[1].Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // ED-03: Edit does not remove sheet metadata (name)
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_Cell_PreservesSheetName()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        doc.Sheets[0].Rows[0].Cells[0].SetText("AnyValue");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal("Sheet1", reloaded.Sheets[0].Name);
    }

    // ------------------------------------------------------------------
    // ED-04: Edit result appears in saved XML as ODF text:p element
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_SavedXml_ContainsTextPWithEditedValue()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        doc.Sheets[0].Rows[0].Cells[0].SetText("VerticalSliceCell");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("VerticalSliceCell", content);
        Assert.Contains("text:p", content);
    }

    // ------------------------------------------------------------------
    // ED-05: Inline minimal FODS — edit empty cell, save, reload
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_EmptyCell_SetText_PersistsAfterReload()
    {
        const string xml =
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
            "<office:document" +
            " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
            " xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
            " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
            " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
            " office:version=\"1.3\">" +
            "<office:body><office:spreadsheet>" +
            "<table:table table:name=\"S1\">" +
            "<table:table-row>" +
            "<table:table-cell/>" +     // empty cell
            "</table:table-row>" +
            "</table:table>" +
            "</office:spreadsheet></office:body>" +
            "</office:document>";

        using var src = new TempFile(xml);
        var doc = FodsDocument.Load(src.Path);

        // Cell starts empty
        Assert.Null(doc.Sheets[0].Rows[0].Cells[0].Value);

        // Set text
        doc.Sheets[0].Rows[0].Cells[0].SetText("Inserted");

        using var out1 = new TempFile();
        doc.Save(out1.Path);

        var reloaded = FodsDocument.Load(out1.Path);
        Assert.Equal("Inserted", reloaded.Sheets[0].Rows[0].Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // ED-06: SetText null throws ArgumentNullException
    // ------------------------------------------------------------------
    [Fact]
    public void SetText_Null_ThrowsArgumentNullException()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);
        Assert.Throws<ArgumentNullException>(() =>
            doc.Sheets[0].Rows[0].Cells[0].SetText(null!));
    }

    // ------------------------------------------------------------------
    // ED-07: Edit handles XML special characters (escaping)
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_XmlSpecialChars_EscapedCorrectly()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        doc.Sheets[0].Rows[0].Cells[0].SetText("<test> & \"value\"");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        // Reload — XML parser would fail if escaping is broken
        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Equal("<test> & \"value\"", reloaded.Sheets[0].Rows[0].Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // ED-08: Edit in-memory only — not visible before save (verify save is needed)
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_InMemoryChange_NotInOriginalFile()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        // Read original value
        var original = doc.Sheets[0].Rows[0].Cells[0].Value;

        // Edit in memory but do not save
        doc.Sheets[0].Rows[0].Cells[0].SetText("InMemoryOnly");

        // Reload original file — should still have old value
        var doc2 = FodsDocument.Load(srcPath);
        Assert.Equal(original, doc2.Sheets[0].Rows[0].Cells[0].Value);
    }

    // ------------------------------------------------------------------
    // ED-09: Sheet count preserved after edit
    // ------------------------------------------------------------------
    [Fact]
    public void Edit_SheetCount_PreservedAfterSaveReload()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);

        doc.Sheets[0].Rows[0].Cells[0].SetText("X");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var reloaded = FodsDocument.Load(tmp.Path);
        Assert.Single(reloaded.Sheets);
    }

    // ------------------------------------------------------------------
    // ED-10: office:value-type="string" set on cell after SetText
    // ------------------------------------------------------------------
    [Fact]
    public void SetText_SetsValueTypeStringInXml()
    {
        var srcPath = Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");
        var doc = FodsDocument.Load(srcPath);
        doc.Sheets[0].Rows[0].Cells[0].SetText("TypeCheck");

        using var tmp = new TempFile();
        doc.Save(tmp.Path);

        var content = File.ReadAllText(tmp.Path);
        Assert.Contains("value-type=\"string\"", content);
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
