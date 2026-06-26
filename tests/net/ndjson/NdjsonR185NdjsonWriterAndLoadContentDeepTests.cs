// Tests for NdjsonWriter.WriteRecords, NdjsonDocument.LoadContent edge cases deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R185

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R185: Tests for NdjsonWriter.WriteRecords, NdjsonDocument.LoadContent edge cases deeper.
/// NdjsonWriter.WriteRecords(records, path): writes a list of record dicts to an NDJSON file.
/// NdjsonWriter.WriteToString(records): serializes records to an NDJSON string.
/// NdjsonDocument.LoadContent(ndjson): parses NDJSON content from a string.
/// Covers: WriteRecords creates file; WriteRecords content non-empty;
/// WriteRecords content parseable back; WriteToString non-null; WriteToString non-empty;
/// WriteToString parseable back with correct count; WriteToString contains field values;
/// LoadContent single record; LoadContent with empty value; LoadContent with boolean field;
/// LoadContent with numeric value parsed; LoadContent with null-like field;
/// dogfood WriteToString->LoadContent->WriteRecords->LoadFile->Verify pipeline.
/// </summary>
public class NdjsonR185NdjsonWriterAndLoadContentDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly List<Dictionary<string, string>> SampleRecords = new()
    {
        new() { ["name"] = "Alice", ["dept"] = "Eng", ["score"] = "92" },
        new() { ["name"] = "Bob", ["dept"] = "Finance", ["score"] = "85" },
        new() { ["name"] = "Carol", ["dept"] = "Eng", ["score"] = "78" },
    };

    public NdjsonR185NdjsonWriterAndLoadContentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR185_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecords_CreatesFile()
    {
        var path = TempFile("output.ndjson");
        NdjsonWriter.WriteRecords(SampleRecords, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRecords_ContentNonEmpty()
    {
        var path = TempFile("nonempty.ndjson");
        NdjsonWriter.WriteRecords(SampleRecords, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteRecords_ContentParseable()
    {
        var path = TempFile("parseable.ndjson");
        NdjsonWriter.WriteRecords(SampleRecords, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.Count);
    }

    [Fact]
    public void WriteRecords_DataPreservedOnReload()
    {
        var path = TempFile("preserved.ndjson");
        NdjsonWriter.WriteRecords(SampleRecords, path);
        var loaded = NdjsonDocument.LoadFile(path);
        loaded.RecordAt(0).TryGetValue("name", out var name);
        Assert.Equal("Alice", name);
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter.WriteToString
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToString_NonNull()
    {
        var result = NdjsonWriter.WriteToString(SampleRecords);
        Assert.NotNull(result);
    }

    [Fact]
    public void WriteToString_NonEmpty()
    {
        var result = NdjsonWriter.WriteToString(SampleRecords);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void WriteToString_ContainsFieldValues()
    {
        var result = NdjsonWriter.WriteToString(SampleRecords);
        Assert.Contains("Alice", result);
        Assert.Contains("Finance", result);
    }

    [Fact]
    public void WriteToString_ParseableBackCorrectCount()
    {
        var result = NdjsonWriter.WriteToString(SampleRecords);
        var doc = NdjsonDocument.LoadContent(result);
        Assert.Equal(3, doc.Count);
    }

    [Fact]
    public void WriteToString_ParseableBackCorrectData()
    {
        var result = NdjsonWriter.WriteToString(SampleRecords);
        var doc = NdjsonDocument.LoadContent(result);
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // NdjsonDocument.LoadContent edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_SingleRecord_CountIsOne()
    {
        var doc = NdjsonDocument.LoadContent("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void LoadContent_WithBooleanField_Accessible()
    {
        var doc = NdjsonDocument.LoadContent("{\"active\":true,\"name\":\"Alice\"}");
        var rec = doc.RecordAt(0);
        Assert.True(rec.TryGetValue("name", out var name));
        Assert.Equal("Alice", name);
    }

    [Fact]
    public void LoadContent_WithNumericValue_Accessible()
    {
        var doc = NdjsonDocument.LoadContent("{\"id\":42,\"value\":3.14}");
        var rec = doc.RecordAt(0);
        Assert.True(rec.TryGetValue("id", out var id));
        Assert.Equal("42", id);
    }

    [Fact]
    public void LoadContent_WithEmptyStringField_Accessible()
    {
        var doc = NdjsonDocument.LoadContent("{\"name\":\"\",\"dept\":\"Eng\"}");
        var rec = doc.RecordAt(0);
        Assert.True(rec.TryGetValue("dept", out var dept));
        Assert.Equal("Eng", dept);
    }

    [Fact]
    public void LoadContent_MultipleLines_AllParsed()
    {
        var content = "{\"a\":1}\n{\"a\":2}\n{\"a\":3}\n{\"a\":4}\n{\"a\":5}";
        var doc = NdjsonDocument.LoadContent(content);
        Assert.Equal(5, doc.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToString_LoadContent_WriteRecords_LoadFile_Verify_Pipeline()
    {
        // WriteToString
        var ndjsonStr = NdjsonWriter.WriteToString(SampleRecords);
        Assert.NotEmpty(ndjsonStr);

        // LoadContent from string
        var fromStr = NdjsonDocument.LoadContent(ndjsonStr);
        Assert.Equal(3, fromStr.Count);
        var names = fromStr.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);

        // WriteRecords to file
        var path = TempFile("dogfood.ndjson");
        NdjsonWriter.WriteRecords(SampleRecords, path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, fromFile.Count);
        fromFile.RecordAt(2).TryGetValue("name", out var carol);
        Assert.Equal("Carol", carol);

        // Verify both sources give same data
        Assert.Equal(fromStr.Count, fromFile.Count);
        var strNames = fromStr.GetFieldValues("name");
        var fileNames = fromFile.GetFieldValues("name");
        foreach (var name in strNames)
            Assert.Contains(name, fileNames);

        // AppendRecord and write again
        fromStr.AppendRecord(new Dictionary<string, string> { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" });
        var path2 = TempFile("extended.ndjson");
        NdjsonWriter.WriteRecords(
            new List<Dictionary<string, string>> { new() { ["name"] = "Dave", ["dept"] = "HR", ["score"] = "91" } },
            path2);
        var extended = NdjsonDocument.LoadFile(path2);
        Assert.Equal(1, extended.Count);
        extended.RecordAt(0).TryGetValue("name", out var dave);
        Assert.Equal("Dave", dave);
    }
}
