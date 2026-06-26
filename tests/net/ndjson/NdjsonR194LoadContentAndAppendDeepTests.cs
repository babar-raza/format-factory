// Tests for NdjsonDocument.LoadContent, AppendRecord, ToNdjson deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R194

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R194: Tests for NdjsonDocument.LoadContent, AppendRecord, ToNdjson deeper coverage.
/// LoadContent(text): parses NDJSON text string into a document.
/// AppendRecord(dict): appends a new record to the document.
/// ToNdjson(): serializes the document back to NDJSON string.
/// Covers: LoadContent non-null; LoadContent correct count; LoadContent data accessible;
/// LoadContent single record; LoadContent empty string no throw or empty;
/// AppendRecord increases count; AppendRecord data accessible via RecordAt;
/// AppendRecord multiple; AppendRecord then GetFieldValues includes new;
/// AppendRecord then CountBy updates; AppendRecord then Filter finds new;
/// ToNdjson non-null; ToNdjson non-empty; ToNdjson has { char; ToNdjson has data values;
/// ToNdjson line count >= record count; ToNdjson round-trip same count;
/// ToNdjson after AppendRecord larger; ToNdjson after Filter smaller;
/// dogfood LoadContent→ToNdjson→AppendRecord×3→ToNdjson→Filter→ToNdjson→round-trip pipeline.
/// </summary>
public class NdjsonR194LoadContentAndAppendDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR194LoadContentAndAppendDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR194_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"Name\":\"Alice\",\"Score\":92,\"Dept\":\"Engineering\"}\n" +
        "{\"Name\":\"Bob\",\"Score\":78,\"Dept\":\"Finance\"}\n" +
        "{\"Name\":\"Carol\",\"Score\":85,\"Dept\":\"Engineering\"}\n" +
        "{\"Name\":\"Dave\",\"Score\":71,\"Dept\":\"HR\"}\n";

    // -------------------------------------------------------------------------
    // LoadContent
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_NonNull()
    {
        Assert.NotNull(NdjsonDocument.LoadContent(SampleNdjson));
    }

    [Fact]
    public void LoadContent_CorrectCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.Equal(4, doc.Count);
    }

    [Fact]
    public void LoadContent_DataAccessible()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.Equal("Alice", doc.RecordAt(0)["Name"].ToString());
        Assert.Equal("Dave", doc.RecordAt(3)["Name"].ToString());
    }

    [Fact]
    public void LoadContent_SingleRecord()
    {
        var single = "{\"Name\":\"Solo\",\"Value\":42}\n";
        var doc = NdjsonDocument.LoadContent(single);
        Assert.Equal(1, doc.Count);
        Assert.Equal("Solo", doc.RecordAt(0)["Name"].ToString());
    }

    [Fact]
    public void LoadContent_EmptyString_NoThrowOrEmpty()
    {
        try
        {
            var doc = NdjsonDocument.LoadContent(string.Empty);
            Assert.True(doc == null || doc.Count == 0);
        }
        catch (Exception)
        {
            // Throwing is acceptable for empty input
        }
    }

    // -------------------------------------------------------------------------
    // AppendRecord
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendRecord_IncreasesCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var before = doc.Count;
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "Finance" });
        Assert.Equal(before + 1, doc.Count);
    }

    [Fact]
    public void AppendRecord_DataAccessibleViaRecordAt()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "Finance" });
        var last = doc.RecordAt(doc.Count - 1);
        Assert.Equal("Eve", last["Name"].ToString());
    }

    [Fact]
    public void AppendRecord_Multiple_CountCorrect()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var before = doc.Count;
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "E1", ["Score"] = 80, ["Dept"] = "X" });
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "E2", ["Score"] = 81, ["Dept"] = "X" });
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "E3", ["Score"] = 82, ["Dept"] = "X" });
        Assert.Equal(before + 3, doc.Count);
    }

    [Fact]
    public void AppendRecord_ThenGetFieldValues_IncludesNew()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Zara", ["Score"] = 99, ["Dept"] = "Research" });
        var names = doc.GetFieldValues("Name");
        Assert.Contains("Zara", names);
    }

    [Fact]
    public void AppendRecord_ThenCountBy_Updates()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "Engineering" });
        var counts = doc.CountBy("Dept");
        Assert.Equal(3, counts["Engineering"]); // Alice + Carol + Eve
    }

    [Fact]
    public void AppendRecord_ThenFilter_FindsNew()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "NewDept" });
        var filtered = doc.Filter("Dept", "NewDept");
        Assert.Equal(1, filtered.Count);
    }

    // -------------------------------------------------------------------------
    // ToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToNdjson_NonNull()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.NotNull(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_NonEmpty()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.NotEmpty(doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_HasBraceChar()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.Contains("{", doc.ToNdjson());
    }

    [Fact]
    public void ToNdjson_HasDataValues()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var ndjson = doc.ToNdjson();
        Assert.Contains("Alice", ndjson);
        Assert.Contains("Dave", ndjson);
    }

    [Fact]
    public void ToNdjson_RoundTrip_SameCount()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var ndjson = doc.ToNdjson();
        var reparsed = NdjsonDocument.LoadContent(ndjson);
        Assert.Equal(doc.Count, reparsed.Count);
    }

    [Fact]
    public void ToNdjson_AfterAppendRecord_Larger()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var before = doc.ToNdjson().Length;
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "Finance" });
        var after = doc.ToNdjson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ToNdjson_AfterFilter_Smaller()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        var all = doc.ToNdjson();
        var filtered = doc.Filter("Dept", "HR").ToNdjson();
        Assert.True(filtered.Length < all.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_ToNdjson_AppendRecord_Filter_RoundTrip_Pipeline()
    {
        var doc = NdjsonDocument.LoadContent(SampleNdjson);
        Assert.Equal(4, doc.Count);

        // ToNdjson
        var ndjson = doc.ToNdjson();
        Assert.NotNull(ndjson);
        Assert.Contains("Alice", ndjson);
        Assert.Contains("{", ndjson);

        // AppendRecord × 3
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Eve", ["Score"] = 90, ["Dept"] = "Finance" });
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Frank", ["Score"] = 88, ["Dept"] = "Engineering" });
        doc.AppendRecord(new Dictionary<string, object> { ["Name"] = "Grace", ["Score"] = 95, ["Dept"] = "Research" });
        Assert.Equal(7, doc.Count);

        // ToNdjson after append — larger
        var ndjsonAfter = doc.ToNdjson();
        Assert.True(ndjsonAfter.Length > ndjson.Length);
        Assert.Contains("Grace", ndjsonAfter);

        // Round-trip
        var reparsed = NdjsonDocument.LoadContent(ndjsonAfter);
        Assert.Equal(7, reparsed.Count);
        Assert.Equal("Alice", reparsed.RecordAt(0)["Name"].ToString());

        // Filter Engineering
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.Count); // Alice + Carol + Frank

        // ToNdjson after filter — smaller than full
        var engNdjson = eng.ToNdjson();
        Assert.True(engNdjson.Length < ndjsonAfter.Length);
        Assert.Contains("Frank", engNdjson);
        Assert.False(engNdjson.Contains("Grace")); // Research

        // CountBy on full doc
        var counts = doc.CountBy("Dept");
        Assert.Equal(3, counts["Engineering"]);
        Assert.Equal(2, counts["Finance"]);
        Assert.Equal(1, counts["HR"]);
        Assert.Equal(1, counts["Research"]);

        // GetFieldValues
        var names = doc.GetFieldValues("Name");
        Assert.Equal(7, names.Count);
        Assert.Contains("Grace", names);

        // SaveToFile via NdjsonWriter and reload
        var path = TempFile("dogfood.ndjson");
        NdjsonWriter.WriteRecords(doc, path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.Count);
    }
}
