// FodsAdvancedRoundtripTests -- TRUE-AUTONOMOUS-CONTINUATION: FODS C7 deepening
// Sprint: TRUE-AUTONOMOUS-MAINSTREAM-CONTINUATION-001
// Added: 2026-06-10
// commercial_product_ready: false
//
// Tests additional roundtrip scenarios: multi-cell edits, multi-row edits,
// inline-constructed fixtures, and bulk edit + verify patterns.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsAdvancedRoundtripTests : IDisposable
{
    private readonly string _tempDir;

    private const string InlineMultiRow =
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
        "<office:document" +
        " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
        " xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
        " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
        " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
        " office:version=\"1.3\">" +
        "<office:body><office:spreadsheet>" +
        "<table:table table:name=\"Data\">" +
        "<table:table-row>" +
        "<table:table-cell office:value-type=\"string\"><text:p>A1</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>B1</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>C1</text:p></table:table-cell>" +
        "</table:table-row>" +
        "<table:table-row>" +
        "<table:table-cell office:value-type=\"string\"><text:p>A2</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>B2</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>C2</text:p></table:table-cell>" +
        "</table:table-row>" +
        "<table:table-row>" +
        "<table:table-cell office:value-type=\"string\"><text:p>A3</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>B3</text:p></table:table-cell>" +
        "<table:table-cell office:value-type=\"string\"><text:p>C3</text:p></table:table-cell>" +
        "</table:table-row>" +
        "</table:table>" +
        "</office:spreadsheet></office:body></office:document>";

    public FodsAdvancedRoundtripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-advanced-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private FodsDocument LoadInline()
    {
        var path = Path.Combine(_tempDir, "inline.fods");
        File.WriteAllText(path, InlineMultiRow);
        return FodsDocument.Load(path);
    }

    [Fact]
    public void MultiCellEdit_AllCellsPersist()
    {
        var doc = LoadInline();
        doc.Sheets[0].Rows[0].Cells[0].SetText("X1");
        doc.Sheets[0].Rows[0].Cells[1].SetText("X2");
        doc.Sheets[0].Rows[0].Cells[2].SetText("X3");

        var path = Path.Combine(_tempDir, "multi-cell.fods");
        doc.Save(path);

        var reloaded = FodsDocument.Load(path);
        Assert.Equal("X1", reloaded.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal("X2", reloaded.Sheets[0].Rows[0].Cells[1].Value);
        Assert.Equal("X3", reloaded.Sheets[0].Rows[0].Cells[2].Value);
    }

    [Fact]
    public void MultiRowEdit_UntouchedRowsSurvive()
    {
        var doc = LoadInline();
        doc.Sheets[0].Rows[0].Cells[0].SetText("EDITED_ROW0");
        doc.Sheets[0].Rows[2].Cells[0].SetText("EDITED_ROW2");

        var path = Path.Combine(_tempDir, "multi-row.fods");
        doc.Save(path);

        var reloaded = FodsDocument.Load(path);
        Assert.Equal("EDITED_ROW0", reloaded.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal("A2", reloaded.Sheets[0].Rows[1].Cells[0].Value); // untouched
        Assert.Equal("EDITED_ROW2", reloaded.Sheets[0].Rows[2].Cells[0].Value);
    }

    [Fact]
    public void TripleRoundtrip_DataStable()
    {
        var doc = LoadInline();
        doc.Sheets[0].Rows[0].Cells[0].SetText("PASS1");

        for (int i = 0; i < 3; i++)
        {
            var path = Path.Combine(_tempDir, $"triple-{i}.fods");
            doc.Save(path);
            doc = FodsDocument.Load(path);
        }

        Assert.Equal("PASS1", doc.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal("B1", doc.Sheets[0].Rows[0].Cells[1].Value);
        Assert.Equal("A2", doc.Sheets[0].Rows[1].Cells[0].Value);
        Assert.Equal(3, doc.Sheets[0].Rows.Count);
    }

    [Fact]
    public void SheetName_PreservedAcrossEdit()
    {
        var doc = LoadInline();
        Assert.Equal("Data", doc.Sheets[0].Name);

        doc.Sheets[0].Rows[0].Cells[0].SetText("NAME_CHECK");

        var path = Path.Combine(_tempDir, "name-check.fods");
        doc.Save(path);

        var reloaded = FodsDocument.Load(path);
        Assert.Equal("Data", reloaded.Sheets[0].Name);
    }

    [Fact]
    public void CellCount_PreservedAfterEdit()
    {
        var doc = LoadInline();
        int r0cells = doc.Sheets[0].Rows[0].Cells.Count;
        int r1cells = doc.Sheets[0].Rows[1].Cells.Count;

        doc.Sheets[0].Rows[0].Cells[0].SetText("COUNT_CHECK");

        var path = Path.Combine(_tempDir, "count-check.fods");
        doc.Save(path);

        var reloaded = FodsDocument.Load(path);
        Assert.Equal(r0cells, reloaded.Sheets[0].Rows[0].Cells.Count);
        Assert.Equal(r1cells, reloaded.Sheets[0].Rows[1].Cells.Count);
    }

    [Fact]
    public void UnicodeValue_SurvivesRoundtrip()
    {
        var doc = LoadInline();
        doc.Sheets[0].Rows[0].Cells[0].SetText("Caf\u00e9 \u00fc\u00f6\u00e4");

        var path = Path.Combine(_tempDir, "unicode.fods");
        doc.Save(path);

        var reloaded = FodsDocument.Load(path);
        Assert.Equal("Caf\u00e9 \u00fc\u00f6\u00e4", reloaded.Sheets[0].Rows[0].Cells[0].Value);
    }
}
