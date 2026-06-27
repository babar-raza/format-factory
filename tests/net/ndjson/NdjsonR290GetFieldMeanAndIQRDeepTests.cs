using System;
using System.IO;
using Xunit;
namespace FormatFactory.Ndjson.Tests;
public class NdjsonR290GetFieldMeanAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NdjsonR290GetFieldMeanAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR290GetFieldMeanAndIQRDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateNdjson(params string[] lines) => string.Join("\n", lines);
    [Fact]
    public void LoadFile_ValidNdjson_ReturnsRecordCount()
    {
        var content = CreateNdjson("{\"a\":1}", "{\"a\":2}", "{\"a\":3}");
        var path = TempFile("test.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.RecordCount);
    }
    [Fact]
    public void GetFieldMean_NumericField_ReturnsMean()
    {
        var content = CreateNdjson("{\"v\":10}", "{\"v\":20}", "{\"v\":30}");
        var path = TempFile("mean.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(20, doc.GetFieldMean("v"));
    }
    [Fact]
    public void GetFieldInterquartileRange_OrderedData_ReturnsIQR()
    {
        var content = CreateNdjson("{\"x\":1}", "{\"x\":2}", "{\"x\":3}", "{\"x\":4}", "{\"x\":5}", "{\"x\":6}", "{\"x\":7}");
        var path = TempFile("iqr.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var iqr = doc.GetFieldInterquartileRange("x");
        Assert.Equal(2, iqr);
    }
    [Fact]
    public void GetFieldMinMax_NumericField_ReturnsCorrect()
    {
        var content = CreateNdjson("{\"y\":100}", "{\"y\":50}", "{\"y\":200}", "{\"y\":75}");
        var path = TempFile("minmax.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(50, doc.GetFieldMin("y"));
        Assert.Equal(200, doc.GetFieldMax("y"));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesRecordCountAndFieldStats()
    {
        var content = CreateNdjson("{\"a\":1,\"b\":10}", "{\"a\":2,\"b\":20}", "{\"a\":3,\"b\":30}");
        var path = TempFile("roundtrip.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var savePath = TempFile("saved.ndjson");
        doc.SaveFile(savePath);
        var reloaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(doc.RecordCount, reloaded.RecordCount);
        Assert.Equal(doc.GetFieldMean("a"), reloaded.GetFieldMean("a"), 5);
    }
    [Fact]
    public void Dogfood_UkGovNdjson_MeanIQRCorrect()
    {
        var ukContent = CreateNdjson(
            "{\"Authority\":\"NHS England\",\"Population\":56000000,\"Budget\":150000000000}",
            "{\"Authority\":\"HMRC\",\"Population\":67000000,\"Budget\":80000000000}",
            "{\"Authority\":\"DVLA\",\"Population\":48000000,\"Budget\":5000000000}",
            "{\"Authority\":\"ONS\",\"Population\":67000000,\"Budget\":3000000000}",
            "{\"Authority\":\"DEFRA\",\"Population\":5000000,\"Budget\":8000000000}"
        );
        var path = TempFile("ukgov.ndjson");
        File.WriteAllText(path, ukContent);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.RecordCount);
        Assert.Equal(48600000, doc.GetFieldMean("Population"));
        Assert.Equal(49400000000, doc.GetFieldMean("Budget"));
        Assert.True(doc.GetFieldInterquartileRange("Population") >= 0);
    }
}