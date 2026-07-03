using System;
using System.IO;
using Xunit;
namespace FormatFactory.Csv.Tests;
public class CsvR284GetColumnMeanAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;
    public CsvR284GetColumnMeanAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR284GetColumnMeanAndIQRDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetColumnMean_DecimalValues_ReturnsMean()
    {
        var content = CreateCsv("vals", "1.5", "2.5", "3.0", "4.0");
        var path = TempFile("mean.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(2.75, doc.GetColumnMean(0), 2);
    }
    [Fact]
    public void GetColumnInterquartileRange_SevenValues_ReturnsIQR()
    {
        var content = CreateCsv("v", "1", "2", "3", "4", "5", "6", "7");
        var path = TempFile("iqr.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        var iqr = doc.GetColumnInterquartileRange(0);
        Assert.Equal(2, iqr);
    }
    [Fact]
    public void GetColumnMinMax_MixedData_ReturnsCorrect()
    {
        var content = CreateCsv("data", "-100", "50", "200", "-50", "0");
        var path = TempFile("minmax.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(-100, doc.GetColumnMin(0));
        Assert.Equal(200, doc.GetColumnMax(0));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesMeanAndIQR()
    {
        var content = CreateCsv("c1,c2", "1,10", "2,20", "3,30", "4,40");
        var path = TempFile("roundtrip.csv");
        File.WriteAllText(path, content);
        var doc = CsvDocument.LoadFile(path);
        var savePath = TempFile("saved.csv");
        doc.SaveFile(savePath);
        var reloaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(doc.GetColumnMean(0), reloaded.GetColumnMean(0), 5);
        Assert.Equal(doc.GetColumnInterquartileRange(0), reloaded.GetColumnInterquartileRange(0), 5);
    }
    [Fact]
    public void Dogfood_UkGovCsv_MeanIQRCorrect()
    {
        var ukContent = CreateCsv(
            "Authority,Population,Budget_Billions",
            "NHS England,56000000,150",
            "HMRC,67000000,80",
            "DVLA,48000000,5",
            "ONS,67000000,3",
            "DEFRA,5000000,8"
        );
        var path = TempFile("ukgov.csv");
        File.WriteAllText(path, ukContent);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(5, doc.RowCount);
        Assert.Equal(48600000, doc.GetColumnMean(1));
        Assert.Equal(49.2, doc.GetColumnMean(2), 2);
        Assert.True(doc.GetColumnInterquartileRange(1) >= 0);
    }
}