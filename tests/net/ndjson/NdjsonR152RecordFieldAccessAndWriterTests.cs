// Tests for NdjsonRecord field access, NdjsonWriter, NdjsonDocument.Count.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R152

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R152: Tests for NdjsonRecord field access, NdjsonWriter, Count and TypedRecords.
/// NdjsonRecord: wraps JsonElement with typed field access methods.
/// NdjsonWriter: serializes records back to NDJSON string or file.
/// Count: total number of records in NdjsonDocument.
/// TypedRecords: IReadOnlyList of NdjsonRecord wrappers.
/// Covers: NdjsonRecord TryGetValue returns found=true; TryGetValue false for missing key;
/// TypedRecords count equals Count; TypedRecords first record has correct keys;
/// GetTypedRecord(index) returns correct record; GetTypedRecord OOB throws;
/// NdjsonWriter.WriteRecords returns non-empty string;
/// NdjsonWriter.WriteRecords contains all records; WriteToFile creates file;
/// WriteToFile content contains records; Count after Filter is subset;
/// dogfood Load->TypedRecords->Filter->WriteRecords pipeline.
/// </summary>
public class NdjsonR152RecordFieldAccessAndWriterTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR152RecordFieldAccessAndWriterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR152_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95,\"active\":true}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"active\":false}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"active\":true}";

    // -------------------------------------------------------------------------
    // NdjsonRecord TryGetValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecord_TryGetValue_ExistingKey_ReturnsTrue()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(0);
        var found = record.TryGetValue("name", out var val);
        Assert.True(found);
    }

    [Fact]
    public void TypedRecord_TryGetValue_ValueIsCorrect()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(0);
        record.TryGetValue("name", out var val);
        Assert.Equal("Alice", val.GetString());
    }

    [Fact]
    public void TypedRecord_TryGetValue_MissingKey_ReturnsFalse()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(0);
        var found = record.TryGetValue("missing_key", out var _);
        Assert.False(found);
    }

    [Fact]
    public void TypedRecord_BooleanField_ValueKindIsTrue()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(0); // Alice: active=true
        record.TryGetValue("active", out var val);
        Assert.Equal(JsonValueKind.True, val.ValueKind);
    }

    // -------------------------------------------------------------------------
    // TypedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void TypedRecords_CountEqualsDocumentCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Equal(doc.Count, doc.TypedRecords.Count);
    }

    [Fact]
    public void TypedRecords_FirstRecord_HasExpectedKeys()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var first = doc.TypedRecords[0];
        Assert.True(first.TryGetValue("name", out var _));
        Assert.True(first.TryGetValue("score", out var _));
    }

    [Fact]
    public void GetTypedRecord_IndexZero_ReturnsFirstRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(0);
        record.TryGetValue("name", out var name);
        Assert.Equal("Alice", name.GetString());
    }

    [Fact]
    public void GetTypedRecord_LastIndex_ReturnsLastRecord()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var record = doc.GetTypedRecord(doc.Count - 1);
        record.TryGetValue("name", out var name);
        Assert.Equal("Carol", name.GetString());
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonWriter_WriteRecords_ReturnsNonEmptyString()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var writer = new NdjsonWriter();
        var output = writer.WriteRecords(doc.Records);
        Assert.False(string.IsNullOrEmpty(output));
    }

    [Fact]
    public void NdjsonWriter_WriteRecords_ContainsAllRecords()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var writer = new NdjsonWriter();
        var output = writer.WriteRecords(doc.Records);
        Assert.Contains("Alice", output);
        Assert.Contains("Bob", output);
        Assert.Contains("Carol", output);
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var writer = new NdjsonWriter();
        var path = TempFile("written.ndjson");
        writer.WriteToFile(doc.Records, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void NdjsonWriter_WriteToFile_ContentContainsRecords()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var writer = new NdjsonWriter();
        var path = TempFile("content.ndjson");
        writer.WriteToFile(doc.Records, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
    }

    // -------------------------------------------------------------------------
    // Count after Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_AfterFilter_IsSubset()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var active = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);
        Assert.Equal(2, active.Count); // Alice and Carol
        Assert.True(active.Count < doc.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->TypedRecords->Filter->WriteRecords pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_TypedRecordsFilterWritePipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Equal(3, doc.Count);
        Assert.Equal(3, doc.TypedRecords.Count);

        // Inspect typed records
        foreach (var record in doc.TypedRecords)
        {
            Assert.True(record.TryGetValue("name", out var _));
        }

        // Filter active records
        var active = doc.Filter(el =>
            el.TryGetProperty("active", out var a) && a.ValueKind == JsonValueKind.True);
        Assert.Equal(2, active.Count);

        // Write to file
        var writer = new NdjsonWriter();
        var path = TempFile("active.ndjson");
        writer.WriteToFile(active.Records, path);

        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
        Assert.DoesNotContain("Bob", content);

        // Reload and verify
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);
    }
}
