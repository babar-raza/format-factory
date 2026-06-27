using System;
using System.IO;
using Xunit;
namespace FormatFactory.Tsv.Tests;
public class TsvR281GetColumnSumAndMeanDeepTests : IDisposable
{
    private readonly string _tempDir;
    public TsvR281GetColumnSumAndMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR281GetColumnSumAndMeanDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateTsv(params string[] rows) => string.Join("\n", rows);
    [Fact]
    public void LoadFile_ValidTsv_ReturnsRowCount()
    {
        var content = CreateTsv("a\tb", "1\t2", "3\t4");
        var path = TempFile("test.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }
    [Fact]
    public void GetColumnSum_FloatValues_ReturnsSum()
    {
        var content = CreateTsv("vals", "1.5", "2.5", "3.0");
        var path = TempFile("sum.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(7.0, doc.GetColumnSum(0), 5);
    }
    [Fact]
    public void GetColumnMean_FloatValues_ReturnsMean()
    {
        var content = CreateTsv("vals", "1.5", "2.5", "3.0");
        var path = TempFile("mean.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(2.333, doc.GetColumnMean(0), 3);
    }
    [Fact]
    public void GetColumnMinMax_MultipleColumns_ReturnsCorrect()
    {
        var content = CreateTsv("col1\tcol2", "10\t100", "5\t200", "15\t50");
        var path = TempFile("minmax.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetColumnMin(0));
        Assert.Equal(15, doc.GetColumnMax(0));
        Assert.Equal(50, doc.GetColumnMin(1));
        Assert.Equal(200, doc.GetColumnMax(1));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesSumAndMean()
    {
        var content = CreateTsv("a\tb", "1\t2", "2\t3", "3\t4");
        var path = TempFile("roundtrip.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var savePath = TempFile("saved.tsv");
        doc.SaveFile(savePath);
        var reloaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetColumnSum(0), reloaded.GetColumnSum(0));
        Assert.Equal(doc.GetColumnMean(0), reloaded.GetColumnMean(0), 5);
    }
    [Fact]
    public void Dogfood_UkGovTsv_SumMeanCorrect()
    {
        var ukContent = CreateTsv(
            "Authority\tPopulation\tBudget_Millions",
            "NHS England\t56000000\t150000",
            "HMRC\t67000000\t80000",
            "DVLA\t48000000\t5000",
            "ONS\t67000000\t3000"
        );
        var path = TempFile("ukgov.tsv");
        File.WriteAllText(path, ukContent);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(238000000, doc.GetColumnSum(1));
        Assert.Equal(59500000, doc.GetColumnMean(1));
        Assert.Equal(59500, doc.GetColumnMean(2), 1);
    }
}