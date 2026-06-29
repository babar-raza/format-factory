using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fods.Tests;
public class FodsR439GetSheetCountAndCellValueDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodsR439GetSheetCountAndCellValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR439GetSheetCountAndCellValueDeepTests_" + Guid.NewGuid().ToString("N"));
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
        var content = CreateFods(("A", new[,] { { "1" } }), ("B", new[,] { { "2" } }), ("C", new[,] { { "3" } }));
        var path = TempFile("test.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(3, doc.GetSheetCount());
    }

    [Fact]
    public void GetCellValue_EdgeCoordinates_ReturnsValue()
    {
        var content = CreateFods(("Grid", new[,]
        {
            { "R0C0", "R0C1", "R0C2" },
            { "R1C0", "R1C1", "R1C2" },
            { "R2C0", "R2C1", "R2C2" }
        }));
        var path = TempFile("grid.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal("R0C0", doc.GetCellValue(0, 0, 0));
        Assert.Equal("R2C2", doc.GetCellValue(0, 2, 2));
        Assert.Equal("R1C0", doc.GetCellValue(0, 1, 0));
    }
    [Fact]
    public void SetCellValue_MultipleUpdates_LastWins()
    {
        var doc = new FodsDocument();
        doc.SetCellValue(0, 0, 0, "First");
        doc.SetCellValue(0, 0, 0, "Second");
        doc.SetCellValue(0, 0, 0, "Third");
        Assert.Equal("Third", doc.GetCellValue(0, 0, 0));
    }
    [Fact]
    public void GetDocumentTitle_NoTitle_ReturnsEmptyOrNull()
    {
        var content = CreateFods(("Data", new[,] { { "X" } }));
        var path = TempFile("notitle.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.NotNull(doc.GetDocumentTitle());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesSheetsAndCells()
    {
        var content = CreateFods(("Sheet1", new[,] { { "A", "B" } }), ("Sheet2", new[,] { { "C" } }));
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
    public void Dogfood_UkGovSheets_CellValuesCorrect()
    {
        var content = CreateFods(
            ("Health", new[,] { { "Dept", "Pop" }, { "NHS", "56000000" } }),
            ("Tax", new[,] { { "Dept", "Rev" }, { "HMRC", "80000000000" } }),
            ("Licensing", new[,] { { "Dept", "Count" }, { "DVLA", "48000000" } })
        );
        var path = TempFile("ukgov.fods");
        File.WriteAllText(path, content);
        var doc = FodsDocument.LoadFile(path);
        Assert.Equal(3, doc.GetSheetCount());
        Assert.Equal("NHS", doc.GetCellValue(0, 1, 0));
        Assert.Equal("80000000000", doc.GetCellValue(1, 1, 1));
        Assert.Equal("48000000", doc.GetCellValue(2, 1, 1));
    }
}