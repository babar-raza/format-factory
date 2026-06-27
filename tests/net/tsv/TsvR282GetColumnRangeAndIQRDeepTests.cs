using System;
using System.IO;
using Xunit;
namespace FormatFactory.Tsv.Tests;
public class TsvR282GetColumnRangeAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;
    public TsvR282GetColumnRangeAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR282GetColumnRangeAndIQRDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetColumnRange_NumericColumn_ReturnsMaxMinusMin()
    {
        var content = CreateTsv("values", "10", "50", "30", "40");
        var path = TempFile("range.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(40, doc.GetColumnRange(0));
    }
    [Fact]
    public void GetColumnInterquartileRange_OrderedData_ReturnsIQR()
    {
        var content = CreateTsv("v", "1", "2", "3", "4", "5", "6", "7");
        var path = TempFile("iqr.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var iqr = doc.GetColumnInterquartileRange(0);
        Assert.True(iqr >= 1 && iqr <= 3);
    }
    [Fact]
    public void GetColumnSum_MultipleColumns_ReturnsCorrect()
    {
        var content = CreateTsv("c1\tc2\tc3", "1\t10\t100", "2\t20\t200", "3\t30\t300");
        var path = TempFile("sum.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetColumnSum(0));
        Assert.Equal(60, doc.GetColumnSum(1));
        Assert.Equal(600, doc.GetColumnSum(2));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesRangeAndIQR()
    {
        var content = CreateTsv("a\tb", "1\t10", "2\t20", "3\t30", "4\t40");
        var path = TempFile("roundtrip.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var savePath = TempFile("saved.tsv");
        doc.SaveFile(savePath);
        var reloaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetColumnRange(0), reloaded.GetColumnRange(0));
        Assert.Equal(doc.GetColumnInterquartileRange(0), reloaded.GetColumnInterquartileRange(0), 5);
    }
    [Fact]
    public void Dogfood_UkGovTsv_RangeIQRCorrect()
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
        Assert.Equal(19000000, doc.GetColumnRange(1));
        Assert.Equal(147000000000, doc.GetColumnRange(2));
        Assert.True(doc.GetColumnInterquartileRange(1) >= 0);
    }
}