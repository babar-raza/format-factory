using System;
using System.IO;
using Xunit;
namespace FormatFactory.Csv.Tests;
public class CsvR281GetColumnMinAndMaxDeepTests : IDisposable
{
    private readonly string _tempDir;
    public CsvR281GetColumnMinAndMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR281GetColumnMinAndMaxDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateCsv(params string[] rows) => string.Join("\n", rows);
    [Fact]
    public void LoadFile_ValidCsv_ReturnsRowCount()
    {
        var content = CreateCsv("a,b,c", "1,2,3", "4,5,6");
        var path = TempFile("test.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }
    [Fact]
    public void GetColumnMin_NumericColumn_ReturnsMinimum()
    {
        var content = CreateCsv("values", "100", "50", "200", "75");
        var path = TempFile("min.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(50, doc.GetColumnMin(0));
    }
    [Fact]
    public void GetColumnMax_NumericColumn_ReturnsMaximum()
    {
        var content = CreateCsv("values", "100", "50", "200", "75");
        var path = TempFile("max.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.GetColumnMax(0));
    }
    [Fact]
    public void GetColumnSum_NumericColumn_ReturnsSum()
    {
        var content = CreateCsv("values", "10", "20", "30", "40");
        var path = TempFile("sum.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(100, doc.GetColumnSum(0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesMinMax()
    {
        var content = CreateCsv("col1,col2", "5,100", "15,200", "10,50");
        var path = TempFile("roundtrip.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        var savePath = TempFile("saved.csv");
        doc.SaveFile(savePath);
        var reloaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetColumnMin(0), reloaded.GetColumnMin(0));
        Assert.Equal(doc.GetColumnMax(1), reloaded.GetColumnMax(1));
    }
    [Fact]
    public void Dogfood_UkGovCsv_MinMaxCorrect()
    {
        var ukContent = CreateCsv(
            "Authority,Population,Revenue_Billions",
            "NHS England,56000000,150",
            "HMRC,67000000,800",
            "DVLA,48000000,5",
            "ONS,67000000,3",
            "DEFRA,5000000,8"
        );
        var path = TempFile("ukgov.csv");
        File.WriteAllText(path, ukContent);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.RowCount);
        Assert.Equal(5000000, doc.GetColumnMin(1));
        Assert.Equal(67000000, doc.GetColumnMax(1));
        Assert.Equal(3, doc.GetColumnMin(2));
        Assert.Equal(800, doc.GetColumnMax(2));
    }
}