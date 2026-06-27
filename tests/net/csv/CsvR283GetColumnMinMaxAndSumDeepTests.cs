using System;
using System.IO;
using Xunit;
namespace FormatFactory.Csv.Tests;
public class CsvR283GetColumnMinMaxAndSumDeepTests : IDisposable
{
    private readonly string _tempDir;
    public CsvR283GetColumnMinMaxAndSumDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR283GetColumnMinMaxAndSumDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateCsv(params string[] rows) => string.Join("\n", rows);
    [Fact]
    public void LoadFile_ValidCsv_ReturnsRowCount()
    {
        var content = CreateCsv("a,b", "1,2", "3,4");
        var path = TempFile("test.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }
    [Fact]
    public void GetColumnMin_LargeNumbers_ReturnsMin()
    {
        var content = CreateCsv("big", "1000000", "5000000", "2000000");
        var path = TempFile("min.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(1000000, doc.GetColumnMin(0));
    }
    [Fact]
    public void GetColumnMax_LargeNumbers_ReturnsMax()
    {
        var content = CreateCsv("big", "1000000", "5000000", "2000000");
        var path = TempFile("max.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5000000, doc.GetColumnMax(0));
    }
    [Fact]
    public void GetColumnSum_MultipleRows_ReturnsSum()
    {
        var content = CreateCsv("vals", "10", "20", "30", "40", "50");
        var path = TempFile("sum.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.GetColumnSum(0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesMinMaxSum()
    {
        var content = CreateCsv("col1,col2", "5,10", "15,20", "10,5");
        var path = TempFile("roundtrip.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        var savePath = TempFile("saved.csv");
        doc.SaveFile(savePath);
        var reloaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetColumnMin(0), reloaded.GetColumnMin(0));
        Assert.Equal(doc.GetColumnMax(0), reloaded.GetColumnMax(0));
        Assert.Equal(doc.GetColumnSum(0), reloaded.GetColumnSum(0));
    }
    [Fact]
    public void Dogfood_UkGovCsv_MinMaxSumCorrect()
    {
        var ukContent = CreateCsv(
            "Authority,Population,Budget_Millions",
            "NHS England,56000000,150000",
            "HMRC,67000000,80000",
            "DVLA,48000000,5000",
            "ONS,67000000,3000",
            "DEFRA,5000000,8000"
        );
        var path = TempFile("ukgov.csv");
        File.WriteAllText(path, ukContent);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.RowCount);
        Assert.Equal(5000000, doc.GetColumnMin(1));
        Assert.Equal(67000000, doc.GetColumnMax(1));
        Assert.Equal(243000000, doc.GetColumnSum(1));
        Assert.Equal(246000, doc.GetColumnSum(2));
    }
}