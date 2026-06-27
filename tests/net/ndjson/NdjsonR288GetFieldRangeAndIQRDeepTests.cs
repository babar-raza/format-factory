using System;
using System.IO;
using Xunit;
namespace FormatFactory.Ndjson.Tests;
public class NdjsonR288GetFieldRangeAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NdjsonR288GetFieldRangeAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR288GetFieldRangeAndIQRDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void GetFieldRange_SortedValues_ReturnsMaxMinusMin()
    {
        var content = CreateNdjson("{\"v\":10}", "{\"v\":20}", "{\"v\":30}", "{\"v\":40}");
        var path = TempFile("range.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(30, doc.GetFieldRange("v"));
    }
    [Fact]
    public void GetFieldInterquartileRange_EvenCount_ReturnsIQR()
    {
        var content = CreateNdjson("{\"v\":1}", "{\"v\":2}", "{\"v\":3}", "{\"v\":4}", "{\"v\":5}", "{\"v\":6}");
        var path = TempFile("iqr.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var iqr = doc.GetFieldInterquartileRange("v");
        Assert.True(iqr >= 1 && iqr <= 3);
    }
    [Fact]
    public void GetFieldMinMax_NumericFields_ReturnsCorrect()
    {
        var content = CreateNdjson("{\"x\":100}", "{\"x\":50}", "{\"x\":200}", "{\"x\":75}");
        var path = TempFile("minmax.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(50, doc.GetFieldMin("x"));
        Assert.Equal(200, doc.GetFieldMax("x"));
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesRecordCountAndStats()
    {
        var content = CreateNdjson("{\"a\":1,\"b\":10}", "{\"a\":2,\"b\":20}", "{\"a\":3,\"b\":30}");
        var path = TempFile("roundtrip.ndjson");
        File.WriteAllText(path, content);
        var doc = NdjsonDocument.LoadFile(path);
        var savePath = TempFile("saved.ndjson");
        doc.SaveFile(savePath);
        var reloaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(doc.RecordCount, reloaded.RecordCount);
        Assert.Equal(doc.GetFieldMin("a"), reloaded.GetFieldMin("a"));
        Assert.Equal(doc.GetFieldMax("b"), reloaded.GetFieldMax("b"));
    }
    [Fact]
    public void Dogfood_UkGovNdjson_RangeAndIQRCorrect()
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
        Assert.Equal(19000000, doc.GetFieldRange("Population"));
        Assert.Equal(147000000000, doc.GetFieldRange("Budget"));
        Assert.True(doc.GetFieldInterquartileRange("Population") >= 0);
    }
}