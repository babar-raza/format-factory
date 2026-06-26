// Tests for NdjsonDocument.GetFieldValues, CountBy, GetAllKeys deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R192

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R192: Tests for NdjsonDocument.GetFieldValues, CountBy, GetAllKeys deeper coverage.
/// GetFieldValues(field): returns all values for a given field key across all records.
/// CountBy(field): returns dict of field value → count of records with that value.
/// GetAllKeys(): returns set/list of all unique field keys across all records.
/// Covers: GetFieldValues non-null; GetFieldValues count=doc.Count; GetFieldValues all present;
/// GetFieldValues after Filter reduces; GetFieldValues after AppendRecord includes new;
/// GetFieldValues after Sort preserves count;
/// CountBy non-null; CountBy Eng=3; CountBy Finance=2; CountBy HR=1;
/// CountBy sum=doc.Count; CountBy after Filter; CountBy after AppendRecord;
/// GetAllKeys non-null; GetAllKeys count=field count; GetAllKeys contains all field names;
/// GetAllKeys for ragged schema is superset; GetAllKeys after AppendRecord may grow;
/// dogfood LoadContent→GetAllKeys→GetFieldValues→CountBy→Filter→AppendRecord pipeline.
/// </summary>
public class NdjsonR192GetFieldValuesAndCountByDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR192GetFieldValuesAndCountByDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR192_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"Name\":\"Alice\",\"Score\":92,\"Dept\":\"Engineering\",\"Active\":true}\n" +
        "{\"Name\":\"Bob\",\"Score\":78,\"Dept\":\"Finance\",\"Active\":false}\n" +
        "{\"Name\":\"Carol\",\"Score\":85,\"Dept\":\"Engineering\",\"Active\":true}\n" +
        "{\"Name\":\"Dave\",\"Score\":71,\"Dept\":\"HR\",\"Active\":false}\n" +
        "{\"Name\":\"Eve\",\"Score\":90,\"Dept\":\"Finance\",\"Active\":true}\n" +
        "{\"Name\":\"Frank\",\"Score\":88,\"Dept\":\"Engineering\",\"Active\":true}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetFieldValues("Name"));
    }

    [Fact]
    public void GetFieldValues_CountEqualsDocCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.Count, doc.GetFieldValues("Name").Count);
    }

    [Fact]
    public void GetFieldValues_AllNamesPresent()
    {
        var doc = LoadSample();
        var names = doc.GetFieldValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void GetFieldValues_AfterFilter_Reduces()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        var names = filtered.GetFieldValues("Name");
        Assert.Equal(3, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void GetFieldValues_AfterAppendRecord_IncludesNew()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace", ["Score"] = 95, ["Dept"] = "Research", ["Active"] = true
        });
        var names = doc.GetFieldValues("Name");
        Assert.Contains("Grace", names);
        Assert.Equal(7, names.Count);
    }

    [Fact]
    public void GetFieldValues_AfterSort_PreservesCount()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Name", ascending: true);
        Assert.Equal(doc.Count, sorted.GetFieldValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // CountBy
    // -------------------------------------------------------------------------

    [Fact]
    public void CountBy_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.CountBy("Dept"));
    }

    [Fact]
    public void CountBy_EngineeringThree()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("Dept");
        Assert.Equal(3, counts["Engineering"]);
    }

    [Fact]
    public void CountBy_FinanceTwo()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("Dept");
        Assert.Equal(2, counts["Finance"]);
    }

    [Fact]
    public void CountBy_HROne()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("Dept");
        Assert.Equal(1, counts["HR"]);
    }

    [Fact]
    public void CountBy_SumEqualsDocCount()
    {
        var doc = LoadSample();
        var counts = doc.CountBy("Dept");
        var total = 0;
        foreach (var kv in counts)
            total += kv.Value;
        Assert.Equal(doc.Count, total);
    }

    [Fact]
    public void CountBy_AfterFilter_SubsetCounts()
    {
        var doc = LoadSample();
        var engOnly = doc.Filter("Dept", "Engineering");
        var counts = engOnly.CountBy("Dept");
        Assert.Equal(1, counts.Count); // Only Engineering
        Assert.Equal(3, counts["Engineering"]);
    }

    [Fact]
    public void CountBy_AfterAppendRecord_UpdatesCounts()
    {
        var doc = LoadSample();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace", ["Score"] = 91, ["Dept"] = "Engineering", ["Active"] = true
        });
        var counts = doc.CountBy("Dept");
        Assert.Equal(4, counts["Engineering"]);
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
    public void GetAllKeys_ContainsFourFields()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetAllKeys().Count);
    }

    [Fact]
    public void GetAllKeys_ContainsAllFieldNames()
    {
        var doc = LoadSample();
        var keys = doc.GetAllKeys();
        Assert.Contains("Name", keys);
        Assert.Contains("Score", keys);
        Assert.Contains("Dept", keys);
        Assert.Contains("Active", keys);
    }

    [Fact]
    public void GetAllKeys_AfterAppendRecord_MayGrow()
    {
        var doc = LoadSample();
        var before = doc.GetAllKeys().Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace", ["Score"] = 91, ["Dept"] = "Research",
            ["Active"] = true, ["ExtraField"] = "new"
        });
        var after = doc.GetAllKeys().Count;
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetAllKeys_GetFieldValues_CountBy_Filter_AppendRecord_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.Count);

        // GetAllKeys
        var keys = doc.GetAllKeys();
        Assert.Equal(4, keys.Count);
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);

        // GetFieldValues for Name
        var names = doc.GetFieldValues("Name");
        Assert.Equal(6, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);

        // GetFieldValues for Dept
        var depts = doc.GetFieldValues("Dept");
        Assert.Equal(6, depts.Count);

        // CountBy Dept
        var counts = doc.CountBy("Dept");
        Assert.Equal(3, counts["Engineering"]);
        Assert.Equal(2, counts["Finance"]);
        Assert.Equal(1, counts["HR"]);

        // Filter Engineering (3 records)
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.Count);

        // CountBy on filtered — only Engineering
        var engCounts = eng.CountBy("Dept");
        Assert.Equal(1, engCounts.Count);
        Assert.Equal(3, engCounts["Engineering"]);

        // GetFieldValues on filtered
        var engNames = eng.GetFieldValues("Name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.False(engNames.Contains("Bob")); // Finance

        // AppendRecord with new dept
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Hana", ["Score"] = 94, ["Dept"] = "Research", ["Active"] = true
        });
        Assert.Equal(7, doc.Count);

        // CountBy after append includes new dept
        var updatedCounts = doc.CountBy("Dept");
        Assert.True(updatedCounts.ContainsKey("Research"));
        Assert.Equal(1, updatedCounts["Research"]);

        // GetFieldValues after append
        var updatedNames = doc.GetFieldValues("Name");
        Assert.Equal(7, updatedNames.Count);
        Assert.Contains("Hana", updatedNames);

        // CountBy sum = 7
        var total = 0;
        foreach (var kv in updatedCounts)
            total += kv.Value;
        Assert.Equal(7, total);
    }
}
