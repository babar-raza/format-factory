using System;
using System.IO;
using Xunit;
namespace FormatFactory.Csv.Tests;
public class CsvR280GetColumnSumAndMeanDeepTests : IDisposable
{
    private readonly string _tempDir;
    public CsvR280GetColumnSumAndMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR280GetColumnSumAndMeanDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateCsv(params string[] rows)
    {
        return string.Join("\n", rows);
    }
    [Fact]
    public void LoadFile_ValidCsv_ReturnsRowCount()
    {
        var content = CreateCsv("a,b,c", "1,2,3", "4,5,6");
        var path = TempFile("test.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(2, doc.RowCount);
    }
    [Fact]
    public void GetColumnSum_NumericColumn_ReturnsSum()
    {
        var content = CreateCsv("values", "10", "20", "30");
        var path = TempFile("sum.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(60, doc.GetColumnSum(0));
    }
    [Fact]
    public void GetColumnMean_NumericColumn_ReturnsMean()
    {
        var content = CreateCsv("values", "10", "20", "30");
        var path = TempFile("mean.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(20, doc.GetColumnMean(0));
    }
    [Fact]
    public void GetColumnMinMax_NumericColumn_ReturnsCorrect()
    {
        var content = CreateCsv("col1,col2", "10,100", "5,200", "15,50");
        var path = TempFile("minmax.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetColumnMin(0));
        Assert.Equal(15, doc.GetColumnMax(0));
        Assert.Equal(50, doc.GetColumnMin(1));
        Assert.Equal(200, doc.GetColumnMax(1));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesData()
    {
        var content = CreateCsv("a,b", "1,2", "3,4");
        var path = TempFile("roundtrip.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        var savePath = TempFile("saved.csv");
        doc.SaveFile(savePath);
        var reloaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
        Assert.Equal(doc.GetColumnSum(0), reloaded.GetColumnSum(0));
    }
    [Fact]
    public void Dogfood_UkGovCsvData_SumMeanCorrect()
    {
        var ukContent = CreateCsv(
            "Authority,Population,Budget",
            "NHS England,56000000,150000000000",
            "HMRC,67000000,80000000000",
            "DVLA,48000000,5000000000",
            "ONS,67000000,3000000000"
        );
        var path = TempFile("ukgov.csv");
        File.WriteAllText(path, ukContent);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
        var popSum = doc.GetColumnSum(1);
        var budgetMean = doc.GetColumnMean(2);
        Assert.Equal(238000000, popSum);
        Assert.Equal(59500000000, budgetMean);
    }
}