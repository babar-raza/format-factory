using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fods.Tests;
public class FodsR436GetSheetCountAndCellValueDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodsR436GetSheetCountAndCellValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR436GetSheetCountAndCellValueDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFodsContent(string sheetName, string[,] cells)
    {
        var rows = new System.Text.StringBuilder();
        for (int r = 0; r < cells.GetLength(0); r++)
        {
            rows.Append("<table:table-row>");
            for (int c = 0; c < cells.GetLength(1); c++)
            {
                var val = cells[r, c];
                var isNumeric = double.TryParse(val, out _);
                rows.Append($"<table:table-cell office:value-type=\"{(isNumeric ? "float" : "string")}\"{(isNumeric ? $" office:value=\"{val}\"" : "")}><text:p>{val}</text:p></table:table-cell>");
            }
            rows.Append("</table:table-row>");
        }
        return $@"<?xml version=""1.0"" encoding=""UTF-8""?>
<office:document xmlns:office=""urn:oasis:names:tc:opendocument:xmlns:office:1.0""
                 xmlns:table=""urn:oasis:names:tc:opendocument:xmlns:table:1.0""
                 xmlns:text=""urn:oasis:names:tc:opendocument:xmlns:text:1.0"">
  <office:body>
    <office:spreadsheet>
      <table:table table:name=""{sheetName}"">
        {rows}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>";
    }
    [Fact]
    public void LoadFile_ValidFods_ReturnsSheetCount()
    {
        var content = CreateFodsContent("Sheet1", new[,] { { "A1", "B1" }, { "A2", "B2" } });
        var path = TempFile("test.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(1, doc.GetSheetCount());
    }
    [Fact]
    public void GetCellValue_ValidCoordinates_ReturnsValue()
    {
        var content = CreateFodsContent("Data", new[,] { { "Name", "Value" }, { "NHS", "56000000" } });
        var path = TempFile("cell.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("Name", doc.GetCellValue(0, 0, 0));
        Assert.Equal("56000000", doc.GetCellValue(0, 1, 1));
    }
    [Fact]
    public void SetCellValue_ThenGet_ReturnsNewValue()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 0, 0, "Test");
        Assert.Equal("Test", doc.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void GetDocumentTitle_ValidFods_ReturnsTitle()
    {
        var content = CreateFodsContent("Budget", new[,] { { "Dept", "Amount" } });
        var path = TempFile("title.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.NotNull(doc.GetDocumentTitle());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesData()
    {
        var content = CreateFodsContent("Round", new[,] { { "A", "1" } });
        var path = TempFile("roundtrip.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        var savePath = TempFile("saved.fods");
        doc.SaveFile(savePath);
        var reloaded = FodsDocument.LoadFile(savePath);
        Assert.Equal(doc.GetSheetCount(), reloaded.GetSheetCount());
        Assert.Equal(doc.GetCellValue(0, 0, 0), reloaded.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void Dogfood_UkGovSpreadsheet_SheetCountAndCellValuesCorrect()
    {
        var content = CreateFodsContent("UK Gov", new[,]
        {
            { "Authority", "Population", "Budget" },
            { "NHS England", "56000000", "150000000000" },
            { "HMRC", "67000000", "80000000000" },
            { "DVLA", "48000000", "5000000000" }
        });
        var path = TempFile("ukgov.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(1, doc.GetSheetCount());
        Assert.Equal("NHS England", doc.GetCellValue(0, 1, 0));
        Assert.Equal("150000000000", doc.GetCellValue(0, 1, 2));
    }
}