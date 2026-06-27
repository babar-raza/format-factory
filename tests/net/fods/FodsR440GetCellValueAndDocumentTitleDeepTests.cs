using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fods.Tests;
public class FodsR440GetCellValueAndDocumentTitleDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodsR440GetCellValueAndDocumentTitleDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR440GetCellValueAndDocumentTitleDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void LoadFile_ValidFods_ReturnsSheetCount()
    {
        var content = CreateFods("Test Doc", ("A", new[,] { { "1" } }), ("B", new[,] { { "2" } }));
        var path = TempFile("test.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(2, doc.GetSheetCount());
    }
    [Fact]
    public void GetCellValue_VariousCells_ReturnsCorrect()
    {
        var content = CreateFods("Test", ("Grid", new[,]
        {
            { "H1", "H2", "H3" },
            { "D1", "D2", "D3" }
        }));
        var path = TempFile("cells.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("H1", doc.GetCellValue(0, 0, 0));
        Assert.Equal("H3", doc.GetCellValue(0, 0, 2));
        Assert.Equal("D2", doc.GetCellValue(0, 1, 1));
    }
    [Fact]
    public void GetDocumentTitle_WithTitle_ReturnsTitle()
    {
        var content = CreateFods("My Spreadsheet", ("Data", new[,] { { "X" } }));
        var path = TempFile("title.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("My Spreadsheet", doc.GetDocumentTitle());
    }
    [Fact]
    public void SetCellValue_ThenGet_ReturnsNewValue()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 0, 0, "Original");
        doc.SetCellValue(0, 0, 0, "Updated");
        Assert.Equal("Updated", doc.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesTitleAndCells()
    {
        var content = CreateFods("Roundtrip", ("Sheet1", new[,] { { "A", "B" } }));
        var path = TempFile("roundtrip.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        var savePath = TempFile("saved.fods");
        doc.SaveFile(savePath);
        var reloaded = FodsDocument.LoadFile(savePath);
        Assert.Equal(doc.GetDocumentTitle(), reloaded.GetDocumentTitle());
        Assert.Equal(doc.GetCellValue(0, 0, 0), reloaded.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void Dogfood_UkGovWorkbook_TitleCellsCorrect()
    {
        var content = CreateFods(
            "UK Government Data 2024",
            ("NHS", new[,] { { "Region", "Population" }, { "England", "56000000" } }),
            ("HMRC", new[,] { { "Tax", "Revenue" }, { "Income", "200000000000" } })
        );
        var path = TempFile("ukgov.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("UK Government Data 2024", doc.GetDocumentTitle());
        Assert.Equal(2, doc.GetSheetCount());
        Assert.Equal("England", doc.GetCellValue(0, 1, 0));
        Assert.Equal("200000000000", doc.GetCellValue(1, 1, 1));
    }
}