using System;
using System.IO;
using Xunit;
namespace FormatFactory.Tsv.Tests;
public class TsvR279GetColumnSumAndMeanDeepTests : IDisposable
{
    private readonly string _tempDir;
    public TsvR279GetColumnSumAndMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR279GetColumnSumAndMeanDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetColumnSum_MultipleColumns_ReturnsCorrectSums()
    {
        var content = CreateTsv("col1\tcol2\tcol3", "10\t100\t1000", "20\t200\t2000", "30\t300\t3000");
        var path = TempFile("sum.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(60, doc.GetColumnSum(0));
        Assert.Equal(600, doc.GetColumnSum(1));
        Assert.Equal(6000, doc.GetColumnSum(2));
    }
    [Fact]
    public void GetColumnMean_NumericColumn_ReturnsMean()
    {
        var content = CreateTsv("values", "10", "20", "30");
        var path = TempFile("mean.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(20, doc.GetColumnMean(0));
    }
    [Fact]
    public void GetColumnMinMax_NumericData_ReturnsCorrect()
    {
        var content = CreateTsv("data", "100", "50", "200", "75");
        var path = TempFile("minmax.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(50, doc.GetColumnMin(0));
        Assert.Equal(200, doc.GetColumnMax(0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesAllStats()
    {
        var content = CreateTsv("a\tb", "1\t2", "3\t4", "5\t6");
        var path = TempFile("roundtrip.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var savePath = TempFile("saved.tsv");
        doc.SaveFile(savePath);
        var reloaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
        Assert.Equal(doc.GetColumnSum(0), reloaded.GetColumnSum(0));
        Assert.Equal(doc.GetColumnMean(0), reloaded.GetColumnMean(0));
    }
    [Fact]
    public void Dogfood_UkGovTsv_SumMeanMinMaxCorrect()
    {
        var ukContent = CreateTsv(
            "Authority\tPopulation\tBudget_Millions",
            "NHS_England\t56000000\t150000",
            "HMRC\t67000000\t80000",
            "DVLA\t48000000\t5000",
            "ONS\t67000000\t3000",
            "DEFRA\t5000000\t8000"
        );
        var path = TempFile("ukgov.tsv");
        File.WriteAllText(path, ukContent);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(5, doc.RowCount);
        Assert.Equal(243000000, doc.GetColumnSum(1));
        Assert.Equal(48600000, doc.GetColumnMean(1));
        Assert.Equal(5000000, doc.GetColumnMin(1));
        Assert.Equal(67000000, doc.GetColumnMax(1));
        Assert.Equal(246000, doc.GetColumnSum(2));
    }
}