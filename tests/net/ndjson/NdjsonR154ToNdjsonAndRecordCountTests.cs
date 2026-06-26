// Tests for NdjsonDocument.ToNdjson serialization and record count operations.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R154

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R154: Tests for NdjsonDocument.ToNdjson serialization, Count, and Records access.
/// ToNdjson(): serializes all records back to NDJSON string.
/// Count: total record count.
/// Records: IList of raw JsonElement records.
/// Covers: ToNdjson is non-empty for non-empty doc; ToNdjson newline-delimited;
/// ToNdjson round-trip via Load count preserved; ToNdjson round-trip values preserved;
/// ToNdjson after Filter excludes filtered records; Count equals Records.Count;
/// Count positive for non-empty doc; Records first element is JsonElement;
/// Records has ValueKind Object; Records last element accessible;
/// Load->Filter->ToNdjson->LoadFile round-trip; Count single record;
/// dogfood Load->Filter->ToNdjson->Save->Load pipeline.
/// </summary>
public class NdjsonR154ToNdjsonAndRecordCountTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR154ToNdjsonAndRecordCountTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR154_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FourRecords =
        "{\"name\":\"Alice\",\"score\":95,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Bob\",\"score\":82,\"dept\":\"Finance\"}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"dept\":\"Eng\"}\n" +
        "{\"name\":\"Dave\",\"score\":91,\"dept\":\"Finance\"}";

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonEmptyDoc_ReturnsNonEmptyString()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        Assert.False(string.IsNullOrEmpty(doc.ToNdjson()));
    }

    [Fact]
    public void ToNdjson_IsNewlineDelimited()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var ndjson = doc.ToNdjson();
        // Should have multiple lines for multiple records
        Assert.Contains("\n", ndjson);
    }

    [Fact]
    public void ToNdjson_RoundTrip_PreservesCount()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjson);
        Assert.Equal(doc.Count, reloaded.Count);
    }

    [Fact]
    public void ToNdjson_RoundTrip_PreservesFieldValues()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjson);
        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void ToNdjson_AfterFilter_ExcludesFilteredRecords()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        var ndjson = eng.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Carol", ndjson);
        Assert.DoesNotContain("Bob", ndjson);
        Assert.DoesNotContain("Dave", ndjson);
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_EqualsRecordsCount()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        Assert.Equal(doc.Count, doc.Records.Count);
    }

    [Fact]
    public void Count_PositiveForNonEmptyDoc()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        Assert.True(doc.Count > 0);
        Assert.Equal(4, doc.Count);
    }

    [Fact]
    public void Count_SingleRecord_IsOne()
    {
        var doc = NdjsonDocument.Load("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void Count_AfterFilter_IsSubset()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var filtered = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetDouble() > 88);
        Assert.True(filtered.Count < doc.Count);
    }

    // -------------------------------------------------------------------------
    // Records
    // -------------------------------------------------------------------------

    [Fact]
    public void Records_FirstElement_IsJsonElement()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var first = doc.Records[0];
        Assert.Equal(JsonValueKind.Object, first.ValueKind);
    }

    [Fact]
    public void Records_LastElement_IsAccessible()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var last = doc.Records[doc.Count - 1];
        Assert.True(last.TryGetProperty("name", out var name));
        Assert.Equal("Dave", name.GetString());
    }

    // -------------------------------------------------------------------------
    // Round-trip via file
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_SaveAndLoadFile_CountPreserved()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        var ndjson = doc.ToNdjson();
        var path = TempFile("rt.ndjson");
        File.WriteAllText(path, ndjson);
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(4, reloaded.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->ToNdjson->Save->Load pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterToNdjsonSaveLoadPipeline()
    {
        var doc = NdjsonDocument.Load(FourRecords);
        Assert.Equal(4, doc.Count);

        // Filter Eng
        var eng = doc.Filter(el =>
            el.TryGetProperty("dept", out var d) && d.GetString() == "Eng");
        Assert.Equal(2, eng.Count);

        // ToNdjson and save
        var ndjson = eng.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.DoesNotContain("Bob", ndjson);

        var path = TempFile("eng.ndjson");
        File.WriteAllText(path, ndjson);

        // Load and verify
        var reloaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(2, reloaded.Count);

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);

        // Schema still uniform
        Assert.True(reloaded.IsUniformSchema());

        // Round-trip count
        var roundTrip = NdjsonDocument.Load(reloaded.ToNdjson());
        Assert.Equal(2, roundTrip.Count);
    }
}
