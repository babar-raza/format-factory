using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fods.Tests;
public class FodsR437GetSheetCountAndDocumentTitleDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodsR437GetSheetCountAndDocumentTitleDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR437GetSheetCountAndDocumentTitleDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFods(string title, params (string name, string[,] cells)[] sheets)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        sb.AppendLine("<office:document xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"");
        sb.AppendLine("  xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"");
        sb.AppendLine("  xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\">");
        sb.AppendLine("  <office:meta>");
        sb.AppendLine($"    <dc:title xmlns:dc=\"http://purl.org/dc/elements/1.1/\">{title}</dc:title>");
        sb.AppendLine("  </office:meta>");
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
    public void LoadFile_MultipleSheets_ReturnsSheetCount()
    {
        var content = CreateFods("Test", ("Sheet1", new[,] { { "A" } }), ("Sheet2", new[,] { { "B" } }), ("Sheet3", new[,] { { "C" } }));
        var path = TempFile("test.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(3, doc.GetSheetCount());
    }
    [Fact]
    public void GetDocumentTitle_WithTitle_ReturnsTitle()
    {
        var content = CreateFods("My Document Title", ("Data", new[,] { { "X" } }));
        var path = TempFile("title.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("My Document Title", doc.GetDocumentTitle());
    }
    [Fact]
    public void GetCellValue_VariousPositions_ReturnsCorrectValues()
    {
        var content = CreateFods("Test", ("Grid", new[,] { { "R0C0", "R0C1" }, { "R1C0", "R1C1" } }));
        var path = TempFile("cells.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("R0C0", doc.GetCellValue(0, 0, 0));
        Assert.Equal("R0C1", doc.GetCellValue(0, 0, 1));
        Assert.Equal("R1C0", doc.GetCellValue(0, 1, 0));
        Assert.Equal("R1C1", doc.GetCellValue(0, 1, 1));
    }
    [Fact]
    public void SetCellValue_UpdatesValue_ReturnsNewValue()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 5, 5, "Updated");
        Assert.Equal("Updated", doc.GetCellValue(0, 5, 5));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesTitleAndSheets()
    {
        var content = CreateFods("Roundtrip Doc", ("A", new[,] { { "1" } }), ("B", new[,] { { "2" } }));
        var path = TempFile("roundtrip.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        var savePath = TempFile("saved.fods");
        doc.SaveFile(savePath);
        var reloaded = FodsDocument.LoadFile(savePath);
        Assert.Equal(doc.GetSheetCount(), reloaded.GetSheetCount());
        Assert.Equal(doc.GetDocumentTitle(), reloaded.GetDocumentTitle());
    }
    [Fact]
    public void Dogfood_UkGovWorkbook_TitleSheetsAndCellsCorrect()
    {
        var content = CreateFods(
            "UK Government Data 2024",
            ("NHS", new[,] { { "Region", "Population" }, { "England", "56000000" } }),
            ("HMRC", new[,] { { "Tax", "Revenue" }, { "Income", "200000000000" } }),
            ("DVLA", new[,] { { "License", "Count" }, { "Driving", "48000000" } })
        );
        var path = TempFile("ukgov.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("UK Government Data 2024", doc.GetDocumentTitle());
        Assert.Equal(3, doc.GetSheetCount());
        Assert.Equal("England", doc.GetCellValue(0, 1, 0));
        Assert.Equal("200000000000", doc.GetCellValue(1, 1, 1));
    }
}