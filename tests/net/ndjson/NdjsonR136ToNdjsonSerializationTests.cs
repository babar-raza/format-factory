// Tests for NdjsonDocument.ToNdjson() serialization method.
// Sprint: ff-sprint-s133-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R136

using System;
using System.Linq;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R136: Tests for NdjsonDocument.ToNdjson() — serializes the document back to
/// NDJSON string format. Each record occupies exactly one line (LF-terminated).
/// Re-loading the output produces the same record count and field values.
/// Covers: empty doc → empty string; single record → one-line string; multi-record
/// count matches line count; each line is valid JSON; field values preserved;
/// ToNdjson line count matches record count; round-trip through Load(ToNdjson());
/// LF line ending per line; dogfood Filter → ToNdjson → Load roundtrip.
/// </summary>
public class NdjsonR136ToNdjsonSerializationTests
{
    private static NdjsonDocument LoadThreeRecords() =>
        NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"score\":72}\n" +
            "{\"name\":\"Carol\",\"score\":88}");

    // -------------------------------------------------------------------------
    // ToNdjson basic behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonDocument_ToNdjson_EmptyDoc_ReturnsEmptyString()
    {
        var doc = NdjsonDocument.Load(string.Empty);
        var result = doc.ToNdjson();
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void NdjsonDocument_ToNdjson_SingleRecord_ReturnsOneLine()
    {
        var doc = NdjsonDocument.Load("{\"id\":1}");
        var result = doc.ToNdjson();
        var lines = result.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Single(lines);
    }

    [Fact]
    public void NdjsonDocument_ToNdjson_ThreeRecords_ThreeLines()
    {
        var doc = LoadThreeRecords();
        var result = doc.ToNdjson();
        var lines = result.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);
    }

    // -------------------------------------------------------------------------
    // Each line is valid JSON
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonDocument_ToNdjson_EachLine_IsValidJson()
    {
        var doc = LoadThreeRecords();
        var result = doc.ToNdjson();

        foreach (var line in result.Split('\n', StringSplitOptions.RemoveEmptyEntries))
        {
            // Should not throw
            var parsed = JsonDocument.Parse(line);
            Assert.NotNull(parsed);
        }
    }

    // -------------------------------------------------------------------------
    // Field values preserved in round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonDocument_ToNdjson_RoundTrip_SameRecordCount()
    {
        var original = LoadThreeRecords();
        var ndjsonStr = original.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjsonStr);
        Assert.Equal(original.Count, reloaded.Count);
    }

    [Fact]
    public void NdjsonDocument_ToNdjson_RoundTrip_PreservesFieldValues()
    {
        var original = LoadThreeRecords();
        var ndjsonStr = original.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjsonStr);

        Assert.True(reloaded.Records[0].TryGetProperty("name", out var name0));
        Assert.Equal("Alice", name0.GetString());

        Assert.True(reloaded.Records[2].TryGetProperty("name", out var name2));
        Assert.Equal("Carol", name2.GetString());
    }

    // -------------------------------------------------------------------------
    // Line endings
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonDocument_ToNdjson_MultiRecord_ContainsLineFeedSeparator()
    {
        var doc = LoadThreeRecords();
        var result = doc.ToNdjson();
        Assert.Contains("\n", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Filter → ToNdjson → Load roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Filter_ToNdjson_Load_SameCount()
    {
        var doc = LoadThreeRecords();

        // Filter: score >= 88 → Alice(95) and Carol(88)
        var filtered = doc.Filter(rec =>
        {
            if (!rec.TryGetProperty("score", out var score)) return false;
            return score.GetInt32() >= 88;
        });

        var ndjsonStr = filtered.ToNdjson();
        var reloaded = NdjsonDocument.Load(ndjsonStr);

        Assert.Equal(2, reloaded.Count);
        Assert.True(reloaded.Records.Any(r =>
            r.TryGetProperty("name", out var n) && n.GetString() == "Alice"));
        Assert.True(reloaded.Records.Any(r =>
            r.TryGetProperty("name", out var n) && n.GetString() == "Carol"));
    }
}
