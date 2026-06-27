using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fods.Tests;
public class FodsR438GetCellValueAndSetCellValueDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodsR438GetCellValueAndSetCellValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR438GetCellValueAndSetCellValueDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFods(params (string name, string[,] cells)[] sheets)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        sb.AppendLine("<office:document xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"");
        sb.AppendLine("  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"");
        sb.AppendLine("  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\">");
        sb.AppendLine("  <office:body>");
        sb.AppendLine("    <office:spreadsheet>");
        foreach (var (name, cells) in sheets)
        {
            sb.AppendLine($"      <table:table table:name=\"{name}\">");
            for (int r = 0; r < cells.GetLength(0); r++)
            {
                sb.AppendLine("        <table:table-row>");
                for (int c = 0; c < cells.GetLength(1); c++)
                {
                    var val = cells[r, c];
                    sb.AppendLine($"          <table:table-cell office:value-type=\"string\"><text:p>{val}</text:p></table:table-cell>");
                }
                sb.AppendLine("        </table:table-row>");
            }
            sb.AppendLine("      </table:table>");
        }
        sb.AppendLine("    </office:spreadsheet>");
        sb.AppendLine("  </office:body>");
        sb.AppendLine("</office:document>");
        return sb.ToString();
    }
    [Fact]
    public void LoadFile_ValidFods_ReturnsSheetCount()
    {
        var content = CreateFods(("Sheet1", new[,] { { "A" } }), ("Sheet2", new[,] { { "B" } }));
        var path = TempFile("test.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(2, doc.GetSheetCount());
    }
    [Fact]
    public void GetCellValue_StringAndNumeric_ReturnsCorrect()
    {
        var content = CreateFods(("Data", new[,] { { "Name", "Value" }, { "Test", "42" } }));
        var path = TempFile("cells.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("Name", doc.GetCellValue(0, 0, 0));
        Assert.Equal("42", doc.GetCellValue(0, 1, 1));
    }
    [Fact]
    public void SetCellValue_OverwritesExisting_ReturnsNewValue()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 0, 0, "Original");
        doc.SetCellValue(0, 0, 0, "Updated");
        Assert.Equal("Updated", doc.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void SetCellValue_NewCoordinates_CreatesCell()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 10, 5, "NewCell");
        Assert.Equal("NewCell", doc.GetCellValue(0, 10, 5));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesCellValues()
    {
        var content = CreateFods(("Round", new[,] { { "A", "1" }, { "B", "2" } }));
        var path = TempFile("roundtrip.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        var savePath = TempFile("saved.fods");
        doc.SaveFile(savePath);
        var reloaded = FodsDocument.LoadFile(savePath);
        Assert.Equal(doc.GetCellValue(0, 0, 0), reloaded.GetCellValue(0, 0, 0));
        Assert.Equal(doc.GetCellValue(0, 1, 1), reloaded.GetCellValue(0, 1, 1));
    }
    [Fact]
    public void Dogfood_UkGovSheet_SetAndGetCellValues()
    {
        var content = CreateFods(("UK", new[,] { { "Dept", "Pop" }, { "NHS", "56000000" } }));
        var path = TempFile("ukgov.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("NHS", doc.GetCellValue(0, 1, 0));
        Assert.Equal("56000000", doc.GetCellValue(0, 1, 1));
        doc.SetCellValue(0, 1, 1, "57000000");
        Assert.Equal("57000000", doc.GetCellValue(0, 1, 1));
    }
}