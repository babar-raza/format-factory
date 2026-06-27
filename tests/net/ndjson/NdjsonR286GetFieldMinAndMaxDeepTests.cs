using System;
using System.IO;
using Xunit;
namespace FormatFactory.Ndjson.Tests;
public class NdjsonR286GetFieldMinAndMaxDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NdjsonR286GetFieldMinAndMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR286GetFieldMinAndMaxDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetFieldMin_NumericField_ReturnsMin()
    {
        var content = CreateNdjson("{\"value\":10}", "{\"value\":5}", "{\"value\":20}");
        var path = TempFile("min.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.GetFieldMin("value"));
    }
    [Fact]
    public void GetFieldMax_NumericField_ReturnsMax()
    {
        var content = CreateNdjson("{\"value\":10}", "{\"value\":5}", "{\"value\":20}");
        var path = TempFile("max.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(20, doc.GetFieldMax("value"));
    }
    [Fact]
    public void GetFieldRange_NumericField_ReturnsRange()
    {
        var content = CreateNdjson("{\"value\":10}", "{\"value\":5}", "{\"value\":20}");
        var path = TempFile("range.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(15, doc.GetFieldRange("value"));
    }
    [Fact]
    public void GetFieldInterquartileRange_NumericField_ReturnsIQR()
    {
        var content = CreateNdjson("{\"v\":1}", "{\"v\":2}", "{\"v\":3}", "{\"v\":4}", "{\"v\":5}");
        var path = TempFile("iqr.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var iqr = doc.GetFieldInterquartileRange("v");
        Assert.True(iqr >= 0);
    }
    [Fact]
    public void Dogfood_UkGovNdjsonRecords_FieldStatsCorrect()
    {
        var ukContent = CreateNdjson(
            "{\"Authority\":\"NHS England\",\"Population\":56000000,\"Budget\":150000000000}",
            "{\"Authority\":\"HMRC\",\"Population\":67000000,\"Budget\":80000000000}",
            "{\"Authority\":\"DVLA\",\"Population\":48000000,\"Budget\":5000000000}",
            "{\"Authority\":\"ONS\",\"Population\":67000000,\"Budget\":3000000000}"
        );
        var path = TempFile("ukgov.ndjson");
        File.WriteAllText(path, ukContent);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, doc.RecordCount);
        Assert.Equal(48000000, doc.GetFieldMin("Population"));
        Assert.Equal(67000000, doc.GetFieldMax("Population"));
        Assert.Equal(19000000, doc.GetFieldRange("Population"));
        Assert.Equal(59500000000, doc.GetFieldInterquartileRange("Budget"), 1);
    }
}