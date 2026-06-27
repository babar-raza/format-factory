using System;
using System.IO;
using Xunit;
namespace FormatFactory.Ndjson.Tests;
public class NdjsonR289GetFieldMinMaxAndRangeDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NdjsonR289GetFieldMinMaxAndRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR289GetFieldMinMaxAndRangeDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void SaveLoad_RoundTrip_PreservesRecordCountAndFieldStats()
    {
        var content = CreateNdjson("{\"x\":10}", "{\"x\":20}", "{\"x\":30}");
        var path = TempFile("roundtrip.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var savePath = TempFile("saved.ndjson");
        doc.SaveFile(savePath);
        var reloaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(doc.RecordCount, reloaded.RecordCount);
        Assert.Equal(doc.GetFieldMin("x"), reloaded.GetFieldMin("x"));
        Assert.Equal(doc.GetFieldMax("x"), reloaded.GetFieldMax("x"));
    }
    [Fact]
    public void Dogfood_UkGovNdjson_MinMaxRangeCorrect()
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
        Assert.Equal(3000000000, doc.GetFieldMin("Budget"));
        Assert.Equal(150000000000, doc.GetFieldMax("Budget"));
        Assert.Equal(147000000000, doc.GetFieldRange("Budget"));
    }
}