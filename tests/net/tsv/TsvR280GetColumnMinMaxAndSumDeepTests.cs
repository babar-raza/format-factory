using System;
using System.IO;
using Xunit;
namespace FormatFactory.Tsv.Tests;
public class TsvR280GetColumnMinMaxAndSumDeepTests : IDisposable
{
    private readonly string _tempDir;
    public TsvR280GetColumnMinMaxAndSumDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR280GetColumnMinMaxAndSumDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetColumnMin_NegativeValues_ReturnsMin()
    {
        var content = CreateTsv("values", "-10", "5", "-20", "15");
        var path = TempFile("min.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(-20, doc.GetColumnMin(0));
    }
    [Fact]
    public void GetColumnMax_NegativeValues_ReturnsMax()
    {
        var content = CreateTsv("values", "-10", "5", "-20", "15");
        var path = TempFile("max.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(15, doc.GetColumnMax(0));
    }
    [Fact]
    public void GetColumnSum_LargeNumbers_ReturnsCorrectSum()
    {
        var content = CreateTsv("big", "1000000", "2000000", "3000000");
        var path = TempFile("sum.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6000000, doc.GetColumnSum(0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesStats()
    {
        var content = CreateTsv("a\tb", "1\t10", "2\t20", "3\t30");
        var path = TempFile("roundtrip.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var savePath = TempFile("saved.tsv");
        doc.SaveFile(savePath);
        var reloaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
        Assert.Equal(doc.GetColumnMin(0), reloaded.GetColumnMin(0));
        Assert.Equal(doc.GetColumnMax(0), reloaded.GetColumnMax(0));
        Assert.Equal(doc.GetColumnSum(0), reloaded.GetColumnSum(0));
    }
    [Fact]
    public void Dogfood_UkGovTsv_MinMaxSumCorrect()
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