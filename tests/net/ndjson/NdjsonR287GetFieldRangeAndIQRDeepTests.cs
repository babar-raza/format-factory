using System;
using System.IO;
using Xunit;
namespace FormatFactory.Ndjson.Tests;
public class NdjsonR287GetFieldRangeAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NdjsonR287GetFieldRangeAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR287GetFieldRangeAndIQRDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateNdjson(params string[] lines) => string.Join("\n", lines);
    [Fact]
    public void LoadFile_ValidNdjson_ReturnsRecordCount()
    {
        var content = CreateNdjson("{\"a\":1}", "{\"a\":2}", "{\"a\":3}", "{\"a\":4}", "{\"a\":5}");
        var path = TempFile("test.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(5, doc.RecordCount);
    }
    [Fact]
    public void GetFieldMin_NumericField_ReturnsMin()
    {
        var content = CreateNdjson("{\"v\":100}", "{\"v\":50}", "{\"v\":200}");
        var path = TempFile("min.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(50, doc.GetFieldMin("v"));
    }
    [Fact]
    public void GetFieldMax_NumericField_ReturnsMax()
    {
        var content = CreateNdjson("{\"v\":100}", "{\"v\":50}", "{\"v\":200}");
        var path = TempFile("max.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.GetFieldMax("v"));
    }
    [Fact]
    public void GetFieldRange_NumericField_ReturnsRange()
    {
        var content = CreateNdjson("{\"v\":100}", "{\"v\":50}", "{\"v\":200}");
        var path = TempFile("range.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150, doc.GetFieldRange("v"));
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
    public void Dogfood_UkGovRecords_FieldStatsCorrect()
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
        Assert.Equal(5000000, doc.GetFieldMin("Population"));
        Assert.Equal(67000000, doc.GetFieldMax("Population"));
        Assert.Equal(62000000, doc.GetFieldRange("Population"));
        Assert.Equal(77000000000, doc.GetFieldInterquartileRange("Budget"), 1);
    }
}