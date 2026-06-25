// Tests for NdjsonDocument.ToNdjson() — in-memory serialization to NDJSON string.
// Sprint: FORMAT-FACTORY-NDJSON-R124-20260627
// Ledger: R124-GOVERNED-DOTNET-NDJSON-TONDJSON-001

using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R124: Tests for NdjsonDocument.ToNdjson() serialization.
/// Verifies: output is non-empty, line count matches record count, each line is valid JSON,
/// round-trip Load→ToNdjson→Load preserves record count and field values.
/// NDJSON basis: each line is a complete JSON object, separated by newlines.
/// </summary>
public class NdjsonR124ToNdjsonSerializationTests
{
    private static NdjsonDocument ThreeRecordDoc()
    {
        const string ndjson = """
{"name":"Alice","score":95,"active":true}
{"name":"Bob","score":72,"active":false}
{"name":"Carol","score":88,"active":true}
""";
        return NdjsonDocument.Load(ndjson);
    }

    // -------------------------------------------------------------------------
    // ToNdjson output format
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonEmptyDocument_ReturnsNonEmptyString()
    {
        var doc = ThreeRecordDoc();
        var result = doc.ToNdjson();
        Assert.NotNull(result);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void ToNdjson_ThreeRecords_OutputHasThreeLines()
    {
        var doc = ThreeRecordDoc();
        var result = doc.ToNdjson();
        var lines = result.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);
    }

    [Fact]
    public void ToNdjson_EachLine_IsValidJson()
    {
        var doc = ThreeRecordDoc();
        var result = doc.ToNdjson();
        var lines = result.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            // Should not throw
            using var parsed = JsonDocument.Parse(line);
            Assert.Equal(JsonValueKind.Object, parsed.RootElement.ValueKind);
        }
    }

    [Fact]
    public void ToNdjson_FirstLine_ContainsAlice()
    {
        var doc = ThreeRecordDoc();
        var result = doc.ToNdjson();
        Assert.Contains("Alice", result.Split('\n')[0]);
    }

    // -------------------------------------------------------------------------
    // Round-trip: Load → ToNdjson → Load
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_RoundTrip_RecordCountPreserved()
    {
        var original = ThreeRecordDoc();
        var serialized = original.ToNdjson();
        var reloaded = NdjsonDocument.Load(serialized);
        Assert.Equal(original.Count, reloaded.Count);
    }

    [Fact]
    public void ToNdjson_RoundTrip_FieldValuesPreserved()
    {
        var original = ThreeRecordDoc();
        var serialized = original.ToNdjson();
        var reloaded = NdjsonDocument.Load(serialized);

        var names = reloaded.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob",   names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void ToNdjson_RoundTrip_AllKeysPreserved()
    {
        var original = ThreeRecordDoc();
        var serialized = original.ToNdjson();
        var reloaded = NdjsonDocument.Load(serialized);

        var keys = reloaded.GetAllKeys();
        Assert.Contains("name",   keys);
        Assert.Contains("score",  keys);
        Assert.Contains("active", keys);
    }

    // -------------------------------------------------------------------------
    // Single-record document
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_SingleRecord_ReturnsOneLine()
    {
        var doc = NdjsonDocument.Load("""{"id":1,"status":"ok"}""");
        var result = doc.ToNdjson();
        var lines = result.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Single(lines);
    }

    // -------------------------------------------------------------------------
    // Dogfood: analytics pipeline with serialization + re-filter
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AnalyticsSerializeAndFilter()
    {
        const string source = """
{"region":"North","product":"Widget","units":100,"revenue":9900.0}
{"region":"South","product":"Gadget","units":50,"revenue":12475.0}
{"region":"East","product":"Widget","units":200,"revenue":19800.0}
{"region":"West","product":"Gadget","units":75,"revenue":18712.5}
""";
        var doc = NdjsonDocument.Load(source);

        // Serialize
        var serialized = doc.ToNdjson();
        Assert.True(serialized.Length > 0);

        // Reload and filter
        var reloaded = NdjsonDocument.Load(serialized);
        Assert.Equal(4, reloaded.Count);

        // Filter for Widget
        var widgets = reloaded.Filter(r =>
            r.TryGetProperty("product", out var p) && p.GetString() == "Widget");
        Assert.Equal(2, widgets.Count);

        // Field values round-trip correctly
        var regions = reloaded.GetFieldValues("region");
        Assert.Contains("North", regions);
        Assert.Contains("West",  regions);
    }
}
