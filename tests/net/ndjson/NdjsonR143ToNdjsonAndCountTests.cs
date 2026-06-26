// Tests for NdjsonDocument.ToNdjson and Count.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R143

using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R143: Tests for NdjsonDocument.ToNdjson and Count.
/// ToNdjson() serializes all records to a newline-delimited JSON string;
/// each line is a valid JSON object; lines are separated by newlines.
/// Count returns the number of records (same as Records.Count).
/// Covers: ToNdjson empty doc returns empty string or empty lines; single record roundtrip;
/// multi-record output has correct line count; ToNdjson output is valid NDJSON that can be re-Loaded;
/// round-trip preserves field values; Count empty is 0; Count single record is 1;
/// Count matches Records.Count; Count after Filter changes;
/// dogfood Load->Filter->ToNdjson->Load pipeline.
/// </summary>
public class NdjsonR143ToNdjsonAndCountTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":82}\n" +
        "{\"name\":\"Carol\",\"score\":88}";

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_EmptyDoc_ReturnsEmptyOrBlank()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var ndjson = doc.ToNdjson();
        // Should be empty or only whitespace — no real content
        Assert.True(string.IsNullOrWhiteSpace(ndjson));
    }

    [Fact]
    public void ToNdjson_SingleRecord_IsValidJson()
    {
        var doc = NdjsonDocument.Load("{\"x\":1}");
        var ndjson = doc.ToNdjson();
        // Should parse as a JSON object
        var el = JsonDocument.Parse(ndjson.Trim()).RootElement;
        Assert.Equal(JsonValueKind.Object, el.ValueKind);
    }

    [Fact]
    public void ToNdjson_MultiRecord_LineCountMatchesRecordCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var ndjson = doc.ToNdjson();
        var lines = ndjson.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);
    }

    [Fact]
    public void ToNdjson_RoundTrip_SameRecordCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var ndjson = doc.ToNdjson();
        var doc2 = NdjsonDocument.Load(ndjson);
        Assert.Equal(doc.Count, doc2.Count);
    }

    [Fact]
    public void ToNdjson_RoundTrip_PreservesFieldValues()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var ndjson = doc.ToNdjson();
        var doc2 = NdjsonDocument.Load(ndjson);
        var names = doc2.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void ToNdjson_EachLineIsValidJson()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var ndjson = doc.ToNdjson();
        var lines = ndjson.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            var el = JsonDocument.Parse(line).RootElement;
            Assert.Equal(JsonValueKind.Object, el.ValueKind);
        }
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    [Fact]
    public void Count_EmptyDoc_IsZero()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        Assert.Equal(0, doc.Count);
    }

    [Fact]
    public void Count_SingleRecord_IsOne()
    {
        var doc = NdjsonDocument.Load("{\"a\":1}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void Count_MatchesRecordsCount()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Equal(doc.Records.Count, doc.Count);
    }

    [Fact]
    public void Count_AfterFilter_ChangesCorrectly()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var filtered = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() > 90);
        Assert.Equal(1, filtered.Count); // Only Alice (95)
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToNdjsonLoad_Pipeline()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);

        // Filter high scorers
        var high = doc.Filter(el =>
            el.TryGetProperty("score", out var s) && s.GetInt32() >= 88);
        Assert.Equal(2, high.Count); // Alice(95), Carol(88)

        // Serialize and reload
        var ndjson = high.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjson);
        Assert.Equal(2, reloaded.Count);

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
