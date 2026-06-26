// Tests for NdjsonDocument.SortBy, Aggregate, GetAllKeys deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R199

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R199: Tests for NdjsonDocument.SortBy, Aggregate, GetAllKeys deeper coverage.
/// SortBy(field, ascending): returns new document with records sorted by field value.
/// Aggregate(field, operation): computes aggregate (sum/avg/min/max/count) on a numeric field.
/// GetAllKeys(): returns all distinct field names across all records.
/// Covers: SortBy ascending first-value correct; SortBy descending first-value correct;
/// SortBy preserves record count; SortBy ToNdjson reflects order; SortBy consistent;
/// SortBy after Filter still sorted; SortBy string field;
/// Aggregate sum correct; Aggregate avg correct; Aggregate min correct;
/// Aggregate max correct; Aggregate count correct; Aggregate after AppendRecord updates;
/// Aggregate after Filter subset; Aggregate consistent;
/// GetAllKeys non-null; GetAllKeys count correct; GetAllKeys contains known field;
/// GetAllKeys after AppendRecord consistent; GetAllKeys consistent;
/// dogfood LoadContent→SortBy→Aggregate→GetAllKeys→Filter→verify pipeline.
/// </summary>
public class NdjsonR199SortByAndAggregateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR199SortByAndAggregateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR199_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Charlie\",\"dept\":\"Engineering\",\"score\":85}\n" +
        "{\"name\":\"Alice\",\"dept\":\"Finance\",\"score\":92}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Engineering\",\"score\":78}\n" +
        "{\"name\":\"Bob\",\"dept\":\"HR\",\"score\":95}\n" +
        "{\"name\":\"Diana\",\"dept\":\"Finance\",\"score\":88}\n" +
        "{\"name\":\"Frank\",\"dept\":\"Engineering\",\"score\":83}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SortBy
    // -------------------------------------------------------------------------

    [Fact]
    public void SortBy_Ascending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("name", ascending: true);
        var first = sorted.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.True(first["name"].ToString() == "Alice");
    }

    [Fact]
    public void SortBy_Descending_FirstValueCorrect()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("name", ascending: false);
        var first = sorted.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.True(first["name"].ToString() == "Frank");
    }

    [Fact]
    public void SortBy_PreservesRecordCount()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal(doc.RecordCount, sorted.RecordCount);
    }

    [Fact]
    public void SortBy_ByScore_Ascending_LowestFirst()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("score", ascending: true);
        var first = sorted.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        // Eve has score=78 (lowest)
        Assert.True(first["name"].ToString() == "Eve");
    }

    [Fact]
    public void SortBy_ByScore_Descending_HighestFirst()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("score", ascending: false);
        var first = sorted.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        // Bob has score=95 (highest)
        Assert.True(first["name"].ToString() == "Bob");
    }

    [Fact]
    public void SortBy_ToNdjson_ReflectsOrder()
    {
        var doc = LoadSample();
        var sorted = doc.SortBy("name", ascending: true);
        var ndjson = sorted.ToNdjson();
        var alicePos = ndjson.IndexOf("Alice");
        var frankPos = ndjson.IndexOf("Frank");
        Assert.True(alicePos < frankPos);
    }

    [Fact]
    public void SortBy_AfterFilter_StillSorted()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("dept", "Engineering");
        var sorted = filtered.SortBy("score", ascending: false);
        Assert.Equal(3, sorted.RecordCount);
        var first = sorted.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.True(first["name"].ToString() == "Charlie"); // 85 is highest in Engineering
    }

    [Fact]
    public void SortBy_Consistent()
    {
        var doc = LoadSample();
        var s1 = doc.SortBy("name", ascending: true);
        var s2 = doc.SortBy("name", ascending: true);
        Assert.Equal(s1.RecordCount, s2.RecordCount);
        var f1 = s1.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        var f2 = s2.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.Equal(f1["name"].ToString(), f2["name"].ToString());
    }

    // -------------------------------------------------------------------------
    // Aggregate
    // -------------------------------------------------------------------------

    [Fact]
    public void Aggregate_Sum_Correct()
    {
        var doc = LoadSample();
        var sum = doc.Aggregate("score", "sum");
        // 85+92+78+95+88+83 = 521
        Assert.True(Math.Abs(sum - 521.0) < 0.01);
    }

    [Fact]
    public void Aggregate_Avg_Correct()
    {
        var doc = LoadSample();
        var avg = doc.Aggregate("score", "avg");
        // 521 / 6 ≈ 86.833
        Assert.True(Math.Abs(avg - 86.833) < 0.1);
    }

    [Fact]
    public void Aggregate_Min_Correct()
    {
        var doc = LoadSample();
        var min = doc.Aggregate("score", "min");
        Assert.True(Math.Abs(min - 78.0) < 0.01);
    }

    [Fact]
    public void Aggregate_Max_Correct()
    {
        var doc = LoadSample();
        var max = doc.Aggregate("score", "max");
        Assert.True(Math.Abs(max - 95.0) < 0.01);
    }

    [Fact]
    public void Aggregate_Count_Correct()
    {
        var doc = LoadSample();
        var count = doc.Aggregate("score", "count");
        Assert.Equal(6, (int)count);
    }

    [Fact]
    public void Aggregate_AfterAppendRecord_SumIncreases()
    {
        var doc = LoadSample();
        var before = doc.Aggregate("score", "sum");
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Legal" }, { "score", 90 }
        });
        var after = doc.Aggregate("score", "sum");
        Assert.True(after > before);
        Assert.True(Math.Abs(after - (before + 90)) < 0.01);
    }

    [Fact]
    public void Aggregate_AfterFilter_SubsetSum()
    {
        var doc = LoadSample();
        var allSum = doc.Aggregate("score", "sum");
        var engSum = doc.Filter("dept", "Engineering").Aggregate("score", "sum");
        // Engineering: 85+78+83 = 246
        Assert.True(Math.Abs(engSum - 246.0) < 0.01);
        Assert.True(engSum < allSum);
    }

    [Fact]
    public void Aggregate_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.Aggregate("score", "sum"), doc.Aggregate("score", "sum"));
    }

    // -------------------------------------------------------------------------
    // GetAllKeys
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAllKeys_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetAllKeys());
    }

    [Fact]
    public void GetAllKeys_CountCorrect()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        Assert.Equal(3, keys.Count); // name, dept, score
    }

    [Fact]
    public void GetAllKeys_ContainsKnownField()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        Assert.True(keys.Contains("name") || keys.Contains("dept") || keys.Contains("score"));
    }

    [Fact]
    public void GetAllKeys_ContainsAllThreeFields()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("dept", keys);
        Assert.Contains("score", keys);
    }

    [Fact]
    public void GetAllKeys_Consistent()
    {
        var doc = LoadSample();
        var k1 = doc.GetAllKeys();
        var k2 = doc.GetAllKeys();
        Assert.Equal(k1.Count, k2.Count);
    }

    [Fact]
    public void GetAllKeys_AfterAppendRecord_SameOrMore()
    {
        var doc = LoadSample();
        var before = doc.GetAllKeys().Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Hank" }, { "dept", "Research" }, { "score", 80 }
        });
        var after = doc.GetAllKeys().Count;
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_SortBy_Aggregate_GetAllKeys_Filter_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RecordCount);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.NotNull(keys);
        Assert.Equal(3, keys.Count);
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);

        // Aggregate
        var sum = doc.Aggregate("score", "sum");
        Assert.True(Math.Abs(sum - 521.0) < 0.01);
        var avg = doc.Aggregate("score", "avg");
        Assert.True(avg > 80 && avg < 95);
        var min = doc.Aggregate("score", "min");
        Assert.True(Math.Abs(min - 78.0) < 0.01);
        var max = doc.Aggregate("score", "max");
        Assert.True(Math.Abs(max - 95.0) < 0.01);

        // SortBy name ascending
        var sortedAsc = doc.SortBy("name", ascending: true);
        Assert.Equal(6, sortedAsc.RecordCount);
        var first = sortedAsc.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.Equal("Alice", first["name"].ToString());

        // SortBy score descending
        var sortedDesc = doc.SortBy("score", ascending: false);
        var firstDesc = sortedDesc.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.Equal("Bob", firstDesc["name"].ToString()); // score=95

        // Filter Engineering then SortBy + Aggregate
        var eng = doc.Filter("dept", "Engineering");
        Assert.Equal(3, eng.RecordCount);
        var engSum = eng.Aggregate("score", "sum");
        Assert.True(Math.Abs(engSum - 246.0) < 0.01);
        var sortedEng = eng.SortBy("score", ascending: false);
        var topEng = sortedEng.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.Equal("Charlie", topEng["name"].ToString()); // 85 is highest

        // GetAllKeys on filtered — same structure
        var engKeys = eng.GetAllKeys();
        Assert.Equal(3, engKeys.Count);

        // AppendRecord and verify Aggregate updates
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Engineering" }, { "score", 90 }
        });
        Assert.Equal(7, doc.RecordCount);
        var newSum = doc.Aggregate("score", "sum");
        Assert.True(Math.Abs(newSum - 611.0) < 0.01);
        var newMax = doc.Aggregate("score", "max");
        Assert.True(Math.Abs(newMax - 95.0) < 0.01); // Bob still has highest

        // SortBy after AppendRecord
        var sortedAfter = doc.SortBy("name", ascending: true);
        Assert.Equal(7, sortedAfter.RecordCount);
        var firstAfter = sortedAfter.GetTypedRecord<System.Collections.Generic.Dictionary<string, object>>(0);
        Assert.Equal("Alice", firstAfter["name"].ToString());

        // SaveToFile and reload
        var path = TempFile("dogfood_sort_agg.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, loaded.RecordCount);
        Assert.True(Math.Abs(loaded.Aggregate("score", "sum") - 611.0) < 0.01);
        var loadedKeys = loaded.GetAllKeys();
        Assert.Equal(3, loadedKeys.Count);
    }
}
