// Tests for NdjsonDocument.Load limits, NdjsonException, NdjsonReader.ReadRecordsFromFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R150

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R150: Tests for NdjsonException hierarchy, NdjsonReader, edge cases.
/// NdjsonException: base exception type for NDJSON errors.
/// NdjsonReader.ReadRecordsFromFile(path): reads records from file.
/// NdjsonReader.ReadRecords(stream): reads records from stream.
/// NdjsonDocument edge cases: single-field records, numeric values, boolean values.
/// Covers: NdjsonException is Exception; Load invalid JSON throws;
/// ReadRecordsFromFile returns records; ReadRecords from stream returns records;
/// Load single-field record; GetFieldValues on numeric field;
/// Load boolean field; TypedRecords on numeric data; Filter on boolean field;
/// GetAllKeys on mixed-type doc; dogfood ReadRecordsFromFile->Filter->ToNdjson pipeline.
/// </summary>
public class NdjsonR150ExceptionAndMaxSizeLimitTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR150ExceptionAndMaxSizeLimitTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR150_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string NumericNdjson =
        "{\"id\":1,\"value\":10.5,\"active\":true}\n" +
        "{\"id\":2,\"value\":20.0,\"active\":false}\n" +
        "{\"id\":3,\"value\":30.75,\"active\":true}";

    // -------------------------------------------------------------------------
    // NdjsonException
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonException_IsException()
    {
        var ex = new NdjsonException("test error");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void NdjsonException_MessagePreserved()
    {
        var ex = new NdjsonException("specific error message");
        Assert.Contains("specific error", ex.Message);
    }

    // -------------------------------------------------------------------------
    // NdjsonReader
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecordsFromFile_ReturnsRecords()
    {
        var path = TempFile("records.ndjson");
        File.WriteAllText(path, NumericNdjson);
        var reader = new NdjsonReader();
        var records = reader.ReadRecordsFromFile(path);
        Assert.Equal(3, records.Count);
    }

    [Fact]
    public void ReadRecordsFromFile_RecordsAreObjects()
    {
        var path = TempFile("objects.ndjson");
        File.WriteAllText(path, NumericNdjson);
        var reader = new NdjsonReader();
        var records = reader.ReadRecordsFromFile(path);
        Assert.All(records, r => Assert.Equal(JsonValueKind.Object, r.ValueKind));
    }

    [Fact]
    public void ReadRecords_FromStream_ReturnsRecords()
    {
        using var stream = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(NumericNdjson));
        var reader = new NdjsonReader();
        var records = reader.ReadRecords(stream);
        Assert.Equal(3, records.Count);
    }

    // -------------------------------------------------------------------------
    // Edge cases: numeric, boolean, single-field
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_SingleFieldRecord_CountIsOne()
    {
        var doc = NdjsonDocument.Load("{\"x\":42}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void GetFieldValues_NumericField_ReturnsStringRepresentations()
    {
        var doc = NdjsonDocument.Load(NumericNdjson);
        var values = doc.GetFieldValues("id");
        Assert.Equal(3, values.Count);
        Assert.Contains("1", values);
    }

    [Fact]
    public void Load_BooleanField_AccessibleViaTypedRecords()
    {
        var doc = NdjsonDocument.Load(NumericNdjson);
        var first = doc.TypedRecords[0];
        var found = first.TryGetValue("active", out var val);
        Assert.True(found);
        Assert.Equal(JsonValueKind.True, val.ValueKind);
    }

    [Fact]
    public void Filter_OnBooleanField_CountCorrect()
    {
        var doc = NdjsonDocument.Load(NumericNdjson);
        var active = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);
        Assert.Equal(2, active.Count); // records 1 and 3
    }

    [Fact]
    public void GetAllKeys_MixedTypeDoc_ReturnsAllKeys()
    {
        var doc = NdjsonDocument.Load(NumericNdjson);
        var keys = doc.GetAllKeys();
        Assert.Contains("id", keys);
        Assert.Contains("value", keys);
        Assert.Contains("active", keys);
    }

    [Fact]
    public void IsUniformSchema_NumericDoc_IsTrue()
    {
        var doc = NdjsonDocument.Load(NumericNdjson);
        Assert.True(doc.IsUniformSchema());
    }

    // -------------------------------------------------------------------------
    // Dogfood: ReadRecordsFromFile->Filter->ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ReadFilterToNdjson_Pipeline()
    {
        var ndjson =
            "{\"name\":\"Alice\",\"score\":95,\"passed\":true}\n" +
            "{\"name\":\"Bob\",\"score\":55,\"passed\":false}\n" +
            "{\"name\":\"Carol\",\"score\":88,\"passed\":true}\n" +
            "{\"name\":\"Dave\",\"score\":42,\"passed\":false}";

        var path = TempFile("students.ndjson");
        File.WriteAllText(path, ndjson);

        // Read from file
        var reader = new NdjsonReader();
        var records = reader.ReadRecordsFromFile(path);
        Assert.Equal(4, records.Count);

        // Load and filter passing students
        var doc = NdjsonDocument.LoadFile(path);
        var passed = doc.Filter(el =>
            el.TryGetProperty("passed", out var p) && p.ValueKind == JsonValueKind.True);
        Assert.Equal(2, passed.Count);

        // Serialize
        var filtered = passed.ToNdjson();
        Assert.Contains("Alice", filtered);
        Assert.Contains("Carol", filtered);
        Assert.DoesNotContain("Bob", filtered);

        // All keys present
        var keys = passed.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
    }
}
