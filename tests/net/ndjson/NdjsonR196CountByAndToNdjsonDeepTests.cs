// Tests for NdjsonDocument.CountBy, ToNdjson deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R196

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R196: Tests for NdjsonDocument.CountBy, ToNdjson deeper coverage.
/// CountBy(field): returns a dictionary of value→count for the given field.
/// ToNdjson(): serializes document records to NDJSON format string (one JSON object per line).
/// Covers: CountBy non-null; CountBy correct value count; CountBy all-unique = RecordCount keys;
/// CountBy single-group all-same; CountBy after AppendRecord updates;
/// CountBy after Filter subset; CountBy integer field;
/// ToNdjson non-null; ToNdjson non-empty; ToNdjson has line count = RecordCount;
/// ToNdjson each line is JSON object; ToNdjson contains field names; ToNdjson contains data values;
/// ToNdjson after AppendRecord larger; ToNdjson after Filter smaller;
/// ToNdjson round-trip via LoadContent;
/// dogfood LoadFile→CountBy→ToNdjson→AppendRecord→Filter→SaveToFile→LoadFile pipeline.
/// </summary>
public class NdjsonR196CountByAndToNdjsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR196CountByAndToNdjsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR196_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"id\":1,\"category\":\"A\",\"status\":\"active\"}\n" +
        "{\"id\":2,\"category\":\"B\",\"status\":\"active\"}\n" +
        "{\"id\":3,\"category\":\"A\",\"status\":\"inactive\"}\n" +
        "{\"id\":4,\"category\":\"C\",\"status\":\"active\"}\n" +
        "{\"id\":5,\"category\":\"B\",\"status\":\"inactive\"}\n" +
        "{\"id\":6,\"category\":\"A\",\"status\":\"active\"}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // CountBy
    // -------------------------------------------------------------------------

    [Fact]
    public void CountBy_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.CountBy("category"));
    }

    [Fact]
    public void CountBy_CorrectValueCount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("category");
        Assert.Equal(3, counts.Count); // A, B, C
    }

    [Fact]
    public void CountBy_CategoryACount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("category");
        Assert.True(counts.ContainsKey("A"));
        Assert.Equal(3, counts["A"]);
    }

    [Fact]
    public void CountBy_CategoryBCount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("category");
        Assert.True(counts.ContainsKey("B"));
        Assert.Equal(2, counts["B"]);
    }

    [Fact]
    public void CountBy_CategoryCCount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("category");
        Assert.True(counts.ContainsKey("C"));
        Assert.Equal(1, counts["C"]);
    }

    [Fact]
    public void CountBy_Status_ActiveInactive()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("status");
        Assert.Equal(2, counts.Count); // active, inactive
        Assert.True(counts.ContainsKey("active"));
        Assert.True(counts.ContainsKey("inactive"));
        Assert.Equal(4, counts["active"]);
        Assert.Equal(2, counts["inactive"]);
    }

    [Fact]
    public void CountBy_AllUnique_KeyCountEqualsRecordCount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("id");
        Assert.Equal(doc.RecordCount, counts.Count);
        foreach (var v in counts.Values)
            Assert.Equal(1, v);
    }

    [Fact]
    public void CountBy_AfterAppendRecord_Updates()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "id", 7 }, { "category", "D" }, { "status", "active" }
        });
        var counts = doc.CountBy("category");
        Assert.Equal(4, counts.Count);
        Assert.True(counts.ContainsKey("D"));
        Assert.Equal(1, counts["D"]);
    }

    [Fact]
    public void CountBy_AfterFilter_Subset()
    {
        var doc = LoadSample();
        var activeCounts = doc.Filter("status", "active").CountBy("category");
        Assert.True(activeCounts.ContainsKey("A"));
        Assert.Equal(2, activeCounts["A"]); // A active: ids 1,6
    }

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_LineCountEqualsRecordCount()
    {
        var doc = LoadSample();
        var ndjson = doc.ToNdjson();
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(doc.RecordCount, lines.Length);
    }

    [Fact]
    public void ToNdjson_EachLineIsJsonObject()
    {
        var doc = LoadSample();
        var ndjson = doc.ToNdjson();
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            var trimmed = line.Trim();
            Assert.True(trimmed.StartsWith("{") && trimmed.EndsWith("}"));
        }
    }

    [Fact]
    public void ToNdjson_ContainsFieldName()
    {
        var doc = LoadSample();
        var ndjson = doc.ToNdjson();
        Assert.True(ndjson.Contains("category") || ndjson.Contains("status"));
    }

    [Fact]
    public void ToNdjson_ContainsDataValue()
    {
        var doc = LoadSample();
        Assert.True(doc.ToNdjson().Contains("\"A\"") || doc.ToNdjson().Contains("A"));
    }

    [Fact]
    public void ToNdjson_AfterAppendRecord_Larger()
    {
        var doc = LoadSample();
        var before = doc.ToNdjson().Length;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "id", 7 }, { "category", "D" }, { "status", "active" }
        });
        Assert.True(doc.ToNdjson().Length > before);
    }

    [Fact]
    public void ToNdjson_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ToNdjson();
        var filtered = doc.Filter("status", "inactive").ToNdjson();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ToNdjson_RoundTrip_ViaLoadContent()
    {
        var doc = LoadSample();
        var ndjson = doc.ToNdjson();
        var reloaded = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc.RecordCount, reloaded.RecordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_CountBy_ToNdjson_AppendRecord_Filter_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RecordCount);

        // CountBy category
        var catCounts = doc.CountBy("category");
        Assert.Equal(3, catCounts.Count);
        Assert.Equal(3, catCounts["A"]);
        Assert.Equal(2, catCounts["B"]);
        Assert.Equal(1, catCounts["C"]);

        // CountBy status
        var statusCounts = doc.CountBy("status");
        Assert.Equal(2, statusCounts.Count);
        Assert.Equal(4, statusCounts["active"]);
        Assert.Equal(2, statusCounts["inactive"]);

        // ToNdjson
        var ndjson = doc.ToNdjson();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        var lines = ndjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(6, lines.Length);
        foreach (var line in lines)
            Assert.True(line.Trim().StartsWith("{"));

        // Filter active records
        var active = doc.Filter("status", "active");
        Assert.Equal(4, active.RecordCount);
        var activeNdjson = active.ToNdjson();
        Assert.True(activeNdjson.Length < ndjson.Length);
        var activeCountBy = active.CountBy("category");
        Assert.True(activeCountBy.ContainsKey("A"));
        Assert.Equal(2, activeCountBy["A"]);

        // AppendRecord — add D category
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "id", 7 }, { "category", "D" }, { "status", "active" }
        });
        Assert.Equal(7, doc.RecordCount);

        // CountBy updated
        var updatedCatCounts = doc.CountBy("category");
        Assert.Equal(4, updatedCatCounts.Count);
        Assert.True(updatedCatCounts.ContainsKey("D"));
        Assert.Equal(5, doc.CountBy("status")["active"]);

        // ToNdjson updated — 7 lines
        var updatedNdjson = doc.ToNdjson();
        var updatedLines = updatedNdjson.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(7, updatedLines.Length);
        Assert.True(updatedNdjson.Length > ndjson.Length);

        // SaveToFile
        var path = TempFile("dogfood_countby.ndjson");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.RecordCount);
        Assert.Equal(4, loaded.CountBy("category").Count);
        var loadedNdjson = loaded.ToNdjson();
        Assert.Equal(7, loadedNdjson.Split('\n', StringSplitOptions.RemoveEmptyEntries).Length);

        // ToNdjson round-trip
        var rt = NdjsonDocument.LoadContent(loaded.ToNdjson());
        Assert.Equal(7, rt.RecordCount);
    }
}
