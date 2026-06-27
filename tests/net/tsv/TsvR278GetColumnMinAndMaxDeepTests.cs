using System;
using System.IO;
using Xunit;
namespace FormatFactory.Tsv.Tests;
public class TsvR278GetColumnMinAndMaxDeepTests : IDisposable
{
    private readonly string _tempDir;
    public TsvR278GetColumnMinAndMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR278GetColumnMinAndMaxDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateTsv(params string[] rows) => string.Join("\n", rows);
    [Fact]
    public void LoadFile_ValidTsv_ReturnsRowCount()
    {
        var content = CreateTsv("a\tb\tc", "1\t2\t3", "4\t5\t6");
        var path = TempFile("test.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }
    [Fact]
    public void GetColumnMin_NumericColumn_ReturnsMin()
    {
        var content = CreateTsv("values", "10", "5", "20");
        var path = TempFile("min.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(5, doc.GetColumnMin(0));
    }
    [Fact]
    public void GetColumnMax_NumericColumn_ReturnsMax()
    {
        var content = CreateTsv("values", "10", "5", "20");
        var path = TempFile("max.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(20, doc.GetColumnMax(0));
    }
    [Fact]
    public void GetColumnSum_NumericColumn_ReturnsSum()
    {
        var content = CreateTsv("col", "10", "20", "30");
        var path = TempFile("sum.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(60, doc.GetColumnSum(0));
    }
    [Fact]
    public void GetColumnMean_NumericColumn_ReturnsMean()
    {
        var content = CreateTsv("col", "10", "20", "30");
        var path = TempFile("mean.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(20, doc.GetColumnMean(0));
    }
    [Fact]
    public void Dogfood_UkGovTsvData_MinMaxSumMeanCorrect()
    {
        var ukContent = CreateTsv(
            "Authority\tPopulation\tBudget",
            "NHS England\t56000000\t150000000000",
            "HMRC\t67000000\t80000000000",
            "DVLA\t48000000\t5000000000",
            "ONS\t67000000\t3000000000"
        );
        var path = TempFile("ukgov.tsv");
        File.WriteAllText(path, ukContent);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(48000000, doc.GetColumnMin(1));
        Assert.Equal(67000000, doc.GetColumnMax(1));
        Assert.Equal(238000000, doc.GetColumnSum(1));
        Assert.Equal(59500000000, doc.GetColumnMean(2));
    }
}