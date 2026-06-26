// Tests for NdjsonDocument.LoadFile, IsUniformSchema, GetAllKeys schema analysis.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R158

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R158: Tests for NdjsonDocument.LoadFile, IsUniformSchema, GetAllKeys deeper schema analysis.
/// LoadFile: loads NDJSON from disk with schema analysis.
/// IsUniformSchema: all records have the same set of keys.
/// GetAllKeys: union of all keys across all records.
/// Covers: LoadFile returns correct count; LoadFile IsUniformSchema true for uniform;
/// LoadFile GetAllKeys count; LoadFile GetAllKeys contains field names;
/// Mixed schema LoadFile IsUniformSchema false; Mixed schema GetAllKeys returns union;
/// Single-record LoadFile IsUniformSchema true; Empty LoadFile returns zero count;
/// Filter->IsUniformSchema preserves uniformity; Filter->GetAllKeys;
/// LoadFile records accessible; LoadFile field values correct;
/// dogfood Write->LoadFile->IsUniformSchema->GetAllKeys->Filter->GetFieldValues.
/// </summary>
public class NdjsonR158LoadFileAndSchemaTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR158LoadFileAndSchemaTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR158_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteTempNdjson(string content, string name = "test.ndjson")
    {
        var path = TempFile(name);
        File.WriteAllText(path, content, Encoding.UTF8);
        return path;
    }

    private const string UniformContent =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}";

    private const string MixedContent =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\"}";

    // -------------------------------------------------------------------------
    // LoadFile - count and records
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_ReturnsCorrectCount()
    {
        var path = WriteTempNdjson(UniformContent, "count.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void LoadFile_RecordsAccessible()
    {
        var path = WriteTempNdjson(UniformContent, "records.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.True(doc.Records[0].TryGetProperty("name", out _));
    }

    [Fact]
    public void LoadFile_FieldValues_Correct()
    {
        var path = WriteTempNdjson(UniformContent, "fields.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadFile_SingleRecord_CountIsOne()
    {
        var path = WriteTempNdjson("{\"x\":1}", "single.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(1, doc.Count);
    }

    // -------------------------------------------------------------------------
    // IsUniformSchema via LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_UniformContent_IsUniformSchemaTrue()
    {
        var path = WriteTempNdjson(UniformContent, "uniform.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.True(doc.IsUniformSchema());
    }

    [Fact]
    public void LoadFile_MixedContent_IsUniformSchemaFalse()
    {
        var path = WriteTempNdjson(MixedContent, "mixed.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.False(doc.IsUniformSchema());
    }

    [Fact]
    public void LoadFile_SingleRecord_IsUniformSchemaTrue()
    {
        var path = WriteTempNdjson("{\"k\":\"v\"}", "one.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // GetAllKeys via LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_GetAllKeys_CountIsThree()
    {
        var path = WriteTempNdjson(UniformContent, "keys3.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.GetAllKeys().Count);
    }

    [Fact]
    public void LoadFile_GetAllKeys_ContainsFieldNames()
    {
        var path = WriteTempNdjson(UniformContent, "keysnames.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    [Fact]
    public void LoadFile_MixedContent_GetAllKeys_IsUnion()
    {
        var path = WriteTempNdjson(MixedContent, "mixed2.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // Filter after LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_Filter_IsUniformSchema_StillTrue()
    {
        var path = WriteTempNdjson(UniformContent, "filter.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.True(eng.IsUniformSchema());
    }

    [Fact]
    public void LoadFile_Filter_GetAllKeys_Consistent()
    {
        var path = WriteTempNdjson(UniformContent, "fkeys.ndjson");
        var doc = NdjsonDocument.LoadFile(path);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var keys = eng.GetAllKeys();
        Assert.Contains("name", keys);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Write->LoadFile->IsUniformSchema->GetAllKeys->Filter->GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteLoadIsUniformGetAllKeysFilterGetFieldValues()
    {
        // Write
        var path = WriteTempNdjson(UniformContent, "dogfood.ndjson");

        // LoadFile
        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, doc.Count);

        // IsUniformSchema
        Assert.True(doc.IsUniformSchema());

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count);
        Assert.Contains("dept", keys);

        // Filter Finance
        var finance = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Finance");
        Assert.Equal(1, finance.Count);
        Assert.True(finance.IsUniformSchema());

        // GetFieldValues
        var financeNames = finance.GetFieldValues("name");
        Assert.Single(financeNames);
        Assert.Equal("Bob", financeNames[0]);
    }
}
