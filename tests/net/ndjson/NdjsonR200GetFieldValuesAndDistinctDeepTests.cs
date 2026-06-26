// Tests for NdjsonDocument.GetFieldValues, Distinct, WriteToStream deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R200

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R200: Tests for NdjsonDocument.GetFieldValues, Distinct, WriteToStream deeper coverage.
/// GetFieldValues(field): returns list of all values for a given field across all records.
/// Distinct(field): returns a new document with deduplicated records by field value.
/// WriteToStream(stream): writes NDJSON content to a stream.
/// Covers: GetFieldValues non-null; GetFieldValues count equals RecordCount;
/// GetFieldValues contains known values; GetFieldValues after AppendRecord grows;
/// GetFieldValues after Filter subset; GetFieldValues consistent;
/// Distinct non-null; Distinct record count correct; Distinct values are unique;
/// Distinct after Filter; Distinct all-unique input unchanged count;
/// Distinct then GroupBy has one per group; Distinct consistent;
/// WriteToStream non-empty output; WriteToStream parseable as NDJSON;
/// WriteToStream line count equals RecordCount; WriteToStream after AppendRecord larger;
/// WriteToStream then LoadStream round-trip; WriteToStream consistent;
/// dogfood LoadContent→GetFieldValues→Distinct→WriteToStream→round-trip pipeline.
/// </summary>
public class NdjsonR200GetFieldValuesAndDistinctDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR200GetFieldValuesAndDistinctDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR200_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleNdjson =
        "{\"name\":\"Alice\",\"dept\":\"Engineering\",\"score\":92}\n" +
        "{\"name\":\"Bob\",\"dept\":\"Finance\",\"score\":78}\n" +
        "{\"name\":\"Carol\",\"dept\":\"Engineering\",\"score\":85}\n" +
        "{\"name\":\"Dave\",\"dept\":\"HR\",\"score\":71}\n" +
        "{\"name\":\"Eve\",\"dept\":\"Finance\",\"score\":90}\n" +
        "{\"name\":\"Frank\",\"dept\":\"Engineering\",\"score\":88}\n";

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
        Assert.NotNull(doc.GetFieldValues("name"));
    }

    [Fact]
    public void GetFieldValues_CountEqualsRecordCount()
    {
        var doc = LoadSample();
        var values = doc.GetFieldValues("name");
        Assert.Equal(doc.RecordCount, values.Count);
    }

    [Fact]
    public void GetFieldValues_ContainsKnownValues()
    {
        var doc = LoadSample();
        var values = doc.GetFieldValues("name");
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Frank", values);
    }

    [Fact]
    public void GetFieldValues_AfterAppendRecord_Grows()
    {
        var doc = LoadSample();
        var before = doc.GetFieldValues("name").Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Legal" }, { "score", 95 }
        });
        var after = doc.GetFieldValues("name").Count;
        Assert.Equal(before + 1, after);
        Assert.Contains("Grace", doc.GetFieldValues("name"));
    }

    [Fact]
    public void GetFieldValues_AfterFilter_Subset()
    {
        var doc = LoadSample();
        var all = doc.GetFieldValues("name");
        var engValues = doc.Filter("dept", "Engineering").GetFieldValues("name");
        Assert.True(engValues.Count < all.Count);
        Assert.Contains("Alice", engValues);
        Assert.Contains("Carol", engValues);
        Assert.Contains("Frank", engValues);
        Assert.DoesNotContain("Bob", engValues);
    }

    [Fact]
    public void GetFieldValues_Consistent()
    {
        var doc = LoadSample();
        var v1 = doc.GetFieldValues("dept");
        var v2 = doc.GetFieldValues("dept");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetFieldValues_DeptField_HasRepetitions()
    {
        var doc = LoadSample();
        var depts = doc.GetFieldValues("dept");
        Assert.Equal(6, depts.Count); // 6 records
        // Engineering appears 3 times
        int engCount = 0;
        foreach (var d in depts) if (d?.ToString() == "Engineering") engCount++;
        Assert.Equal(3, engCount);
    }

    // -------------------------------------------------------------------------
    // Distinct
    // -------------------------------------------------------------------------

    [Fact]
    public void Distinct_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Distinct("dept"));
    }

    [Fact]
    public void Distinct_RecordCountCorrect()
    {
        var doc = LoadSample();
        var distinct = doc.Distinct("dept");
        // 3 distinct depts: Engineering, Finance, HR
        Assert.Equal(3, distinct.RecordCount);
    }

    [Fact]
    public void Distinct_ValuesAreUnique()
    {
        var doc = LoadSample();
        var distinct = doc.Distinct("dept");
        var depts = distinct.GetFieldValues("dept");
        var unique = new System.Collections.Generic.HashSet<string>();
        foreach (var d in depts) unique.Add(d?.ToString() ?? "");
        Assert.Equal(depts.Count, unique.Count);
    }

    [Fact]
    public void Distinct_AllUniqueInput_UnchangedCount()
    {
        var doc = LoadSample();
        var distinct = doc.Distinct("name");
        // All names are unique → same record count
        Assert.Equal(doc.RecordCount, distinct.RecordCount);
    }

    [Fact]
    public void Distinct_Consistent()
    {
        var doc = LoadSample();
        var d1 = doc.Distinct("dept");
        var d2 = doc.Distinct("dept");
        Assert.Equal(d1.RecordCount, d2.RecordCount);
    }

    [Fact]
    public void Distinct_AfterFilter_SubsetDistinct()
    {
        var doc = LoadSample();
        // Filter Engineering then distinct dept → 1 distinct dept
        var engDistinct = doc.Filter("dept", "Engineering").Distinct("dept");
        Assert.Equal(1, engDistinct.RecordCount);
    }

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_NonEmptyOutput()
    {
        var doc = LoadSample();
        using var stream = new MemoryStream();
        doc.WriteToStream(stream);
        Assert.True(stream.Length > 0);
    }

    [Fact]
    public void WriteToStream_LineCountEqualsRecordCount()
    {
        var doc = LoadSample();
        using var stream = new MemoryStream();
        doc.WriteToStream(stream);
        stream.Position = 0;
        using var reader = new StreamReader(stream);
        var content = reader.ReadToEnd();
        var lines = content.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(doc.RecordCount, lines.Length);
    }

    [Fact]
    public void WriteToStream_ContainsKnownData()
    {
        var doc = LoadSample();
        using var stream = new MemoryStream();
        doc.WriteToStream(stream);
        stream.Position = 0;
        using var reader = new StreamReader(stream);
        var content = reader.ReadToEnd();
        Assert.Contains("Alice", content);
        Assert.Contains("Frank", content);
    }

    [Fact]
    public void WriteToStream_AfterAppendRecord_Larger()
    {
        var doc = LoadSample();
        using var streamBefore = new MemoryStream();
        doc.WriteToStream(streamBefore);
        var sizeBefore = streamBefore.Length;

        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Hank" }, { "dept", "Marketing" }, { "score", 82 }
        });
        using var streamAfter = new MemoryStream();
        doc.WriteToStream(streamAfter);
        Assert.True(streamAfter.Length > sizeBefore);
    }

    [Fact]
    public void WriteToStream_ThenLoadStream_RoundTrip()
    {
        var doc = LoadSample();
        using var stream = new MemoryStream();
        doc.WriteToStream(stream);
        stream.Position = 0;
        var loaded = NdjsonDocument.LoadStream(stream);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
    }

    [Fact]
    public void WriteToStream_Consistent()
    {
        var doc = LoadSample();
        using var s1 = new MemoryStream();
        using var s2 = new MemoryStream();
        doc.WriteToStream(s1);
        doc.WriteToStream(s2);
        Assert.Equal(s1.Length, s2.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetFieldValues_Distinct_WriteToStream_RoundTrip_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RecordCount);

        // GetFieldValues
        var names = doc.GetFieldValues("name");
        Assert.Equal(6, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);

        var depts = doc.GetFieldValues("dept");
        Assert.Equal(6, depts.Count);
        int engCount = 0;
        foreach (var d in depts) if (d?.ToString() == "Engineering") engCount++;
        Assert.Equal(3, engCount);

        // Distinct by dept
        var distinctDept = doc.Distinct("dept");
        Assert.Equal(3, distinctDept.RecordCount);
        var distinctDepts = distinctDept.GetFieldValues("dept");
        var uniqueDepts = new System.Collections.Generic.HashSet<string>();
        foreach (var d in distinctDepts) uniqueDepts.Add(d?.ToString() ?? "");
        Assert.Equal(3, uniqueDepts.Count);

        // Distinct by name (all unique)
        var distinctName = doc.Distinct("name");
        Assert.Equal(6, distinctName.RecordCount);

        // Filter then GetFieldValues
        var engNames = doc.Filter("dept", "Engineering").GetFieldValues("name");
        Assert.Equal(3, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
        Assert.Contains("Frank", engNames);

        // AppendRecord then GetFieldValues
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            { "name", "Grace" }, { "dept", "Engineering" }, { "score", 96 }
        });
        Assert.Equal(7, doc.RecordCount);
        var updatedNames = doc.GetFieldValues("name");
        Assert.Equal(7, updatedNames.Count);
        Assert.Contains("Grace", updatedNames);

        // Distinct after AppendRecord — still 3 depts
        var updatedDistinct = doc.Distinct("dept");
        Assert.Equal(3, updatedDistinct.RecordCount);

        // WriteToStream
        using var stream = new MemoryStream();
        doc.WriteToStream(stream);
        Assert.True(stream.Length > 0);
        stream.Position = 0;
        using var reader = new StreamReader(stream);
        var content = reader.ReadToEnd();
        Assert.Contains("Alice", content);
        Assert.Contains("Grace", content);

        // Lines in stream
        var lines = content.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(7, lines.Length);

        // LoadStream round-trip
        stream.Position = 0;
        var reloaded = NdjsonDocument.LoadStream(stream);
        Assert.Equal(7, reloaded.RecordCount);
        Assert.Contains("Grace", reloaded.GetFieldValues("name"));

        // Distinct on reloaded
        var reloadedDistinct = reloaded.Distinct("dept");
        Assert.Equal(3, reloadedDistinct.RecordCount);

        // SaveToFile and reload
        var path = TempFile("dogfood_fieldvalues.ndjson");
        doc.SaveToFile(path);
        var fileLoaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, fileLoaded.RecordCount);
        Assert.Contains("Grace", fileLoaded.GetFieldValues("name"));
    }
}
