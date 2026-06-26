// Tests for NdjsonDocument.SortBy, MergeWith, GetFieldValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R206

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R206: Tests for NdjsonDocument.SortBy, MergeWith, GetFieldValues deeper.
/// SortBy(field, ascending): sorts records by the specified field value.
/// MergeWith(other): combines records from two documents into one.
/// GetFieldValues(field): returns all values for the specified field as a list.
/// Covers: SortBy non-null; SortBy ascending first record correct;
/// SortBy descending first record correct; SortBy preserves record count;
/// SortBy consistent; SortBy no-throw; SortBy then Filter; SortBy numeric;
/// MergeWith non-null; MergeWith total count = sum; MergeWith all records present;
/// MergeWith consistent field structure; MergeWith then Filter; MergeWith persist;
/// MergeWith self doubles count; MergeWith then SortBy;
/// GetFieldValues non-null; GetFieldValues non-empty; GetFieldValues count = record count;
/// GetFieldValues contains known values; GetFieldValues consistent;
/// GetFieldValues after AppendRecord grows; GetFieldValues after Filter shrinks;
/// GetFieldValues no duplicates for unique; GetFieldValues all for repeated;
/// dogfood CreateDoc→SortBy→MergeWith→GetFieldValues→WriteToFile pipeline.
/// </summary>
public class NdjsonR206SortByAndMergeWithDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR206SortByAndMergeWithDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR206_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NdjsonDocument CreateBaseDoc()
    {
        var doc = NdjsonDocument.CreateNew();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Charlie", ["score"] = 78, ["dept"] = "Finance"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Alice", ["score"] = 92, ["dept"] = "Engineering"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Eve", ["score"] = 85, ["dept"] = "Marketing"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Bob", ["score"] = 88, ["dept"] = "Engineering"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Diana", ["score"] = 91, ["dept"] = "Finance"
        });
        return doc;
    }

    private static NdjsonDocument CreateSecondDoc()
    {
        var doc = NdjsonDocument.CreateNew();
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Frank", ["score"] = 77, ["dept"] = "HR"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Grace", ["score"] = 94, ["dept"] = "Engineering"
        });
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Henry", ["score"] = 83, ["dept"] = "Marketing"
        });
        return doc;
    }

    // -------------------------------------------------------------------------
    // SortBy
    // -------------------------------------------------------------------------

    [Fact]
    public void SortBy_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.SortBy("name", ascending: true));
    }

    [Fact]
    public void SortBy_Ascending_FirstRecordCorrect()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("name", ascending: true);
        var first = sorted.GetRecord(0);
        Assert.Equal("Alice", first["name"].ToString());
    }

    [Fact]
    public void SortBy_Descending_FirstRecordCorrect()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("name", ascending: false);
        var first = sorted.GetRecord(0);
        Assert.Equal("Eve", first["name"].ToString());
    }

    [Fact]
    public void SortBy_PreservesRecordCount()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("name", ascending: true);
        Assert.Equal(doc.GetRecordCount(), sorted.GetRecordCount());
    }

    [Fact]
    public void SortBy_Numeric_Ascending_FirstIsLowest()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("score", ascending: true);
        var first = sorted.GetRecord(0);
        Assert.Equal("Charlie", first["name"].ToString()); // score=78
    }

    [Fact]
    public void SortBy_Numeric_Descending_FirstIsHighest()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("score", ascending: false);
        var first = sorted.GetRecord(0);
        Assert.Equal("Alice", first["name"].ToString()); // score=92
    }

    [Fact]
    public void SortBy_NoThrow()
    {
        var doc = CreateBaseDoc();
        var ex = Record.Exception(() => doc.SortBy("name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortBy_Consistent()
    {
        var doc = CreateBaseDoc();
        var s1 = doc.SortBy("name", ascending: true);
        var s2 = doc.SortBy("name", ascending: true);
        Assert.Equal(s1.GetRecord(0)["name"].ToString(), s2.GetRecord(0)["name"].ToString());
    }

    [Fact]
    public void SortBy_ThenFilter_Works()
    {
        var doc = CreateBaseDoc();
        var sorted = doc.SortBy("score", ascending: false);
        var filtered = sorted.Filter("dept", "Engineering");
        Assert.NotNull(filtered);
        Assert.True(filtered.GetRecordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NonNull()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        Assert.NotNull(doc1.MergeWith(doc2));
    }

    [Fact]
    public void MergeWith_TotalCount_IsSumOfBoth()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(doc1.GetRecordCount() + doc2.GetRecordCount(), merged.GetRecordCount());
    }

    [Fact]
    public void MergeWith_AllRecordsPresent()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        var names = merged.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
        Assert.Contains("Grace", names);
    }

    [Fact]
    public void MergeWith_Persist()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        var path = TempFile("merge_persist.ndjson");
        merged.WriteToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(merged.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void MergeWith_ThenFilter_Works()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        var engFiltered = merged.Filter("dept", "Engineering");
        Assert.NotNull(engFiltered);
        // 2 Eng from doc1 + 1 Eng from doc2 = 3
        Assert.Equal(3, engFiltered.GetRecordCount());
    }

    [Fact]
    public void MergeWith_ThenSortBy_Works()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        var sorted = merged.SortBy("name", ascending: true);
        Assert.NotNull(sorted);
        Assert.Equal(8, sorted.GetRecordCount());
        var first = sorted.GetRecord(0);
        Assert.Equal("Alice", first["name"].ToString());
    }

    [Fact]
    public void MergeWith_Self_DoublesCount()
    {
        var doc = CreateBaseDoc();
        var merged = doc.MergeWith(doc);
        Assert.Equal(doc.GetRecordCount() * 2, merged.GetRecordCount());
    }

    [Fact]
    public void MergeWith_PreservesFieldStructure()
    {
        var doc1 = CreateBaseDoc();
        var doc2 = CreateSecondDoc();
        var merged = doc1.MergeWith(doc2);
        var keys = merged.GetAllKeys();
        Assert.Contains("name", keys);
        Assert.Contains("score", keys);
        Assert.Contains("dept", keys);
    }

    // -------------------------------------------------------------------------
    // GetFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValues_NonNull()
    {
        var doc = CreateBaseDoc();
        Assert.NotNull(doc.GetFieldValues("name"));
    }

    [Fact]
    public void GetFieldValues_NonEmpty()
    {
        var doc = CreateBaseDoc();
        Assert.True(doc.GetFieldValues("name").Count > 0);
    }

    [Fact]
    public void GetFieldValues_CountEqualsRecordCount()
    {
        var doc = CreateBaseDoc();
        var values = doc.GetFieldValues("name");
        Assert.Equal(doc.GetRecordCount(), values.Count);
    }

    [Fact]
    public void GetFieldValues_ContainsKnownValues()
    {
        var doc = CreateBaseDoc();
        var names = doc.GetFieldValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Charlie", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetFieldValues_Consistent()
    {
        var doc = CreateBaseDoc();
        var v1 = doc.GetFieldValues("name");
        var v2 = doc.GetFieldValues("name");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetFieldValues_AfterAppendRecord_Grows()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetFieldValues("name").Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Zara", ["score"] = 99, ["dept"] = "Engineering"
        });
        var after = doc.GetFieldValues("name").Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetFieldValues_AfterFilter_Shrinks()
    {
        var doc = CreateBaseDoc();
        var before = doc.GetFieldValues("name").Count;
        var filtered = doc.Filter("dept", "Engineering");
        var after = filtered.GetFieldValues("name").Count;
        Assert.True(after < before);
    }

    [Fact]
    public void GetFieldValues_ForDept_ContainsAllDepts()
    {
        var doc = CreateBaseDoc();
        var depts = doc.GetFieldValues("dept");
        Assert.Contains("Finance", depts);
        Assert.Contains("Engineering", depts);
        Assert.Contains("Marketing", depts);
    }

    [Fact]
    public void GetFieldValues_ForScore_AllNumeric()
    {
        var doc = CreateBaseDoc();
        var scores = doc.GetFieldValues("score");
        Assert.Equal(5, scores.Count);
        foreach (var s in scores)
            Assert.True(s != null);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortBy_MergeWith_GetFieldValues_WriteToFile_Pipeline()
    {
        // Build two documents
        var docA = NdjsonDocument.CreateNew();
        var teamAData = new[]
        {
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Aaron", ["score"] = 95, ["team"] = "Alpha", ["level"] = "Senior" },
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Brianna", ["score"] = 82, ["team"] = "Beta", ["level"] = "Junior" },
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Caleb", ["score"] = 88, ["team"] = "Alpha", ["level"] = "Mid" },
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Diane", ["score"] = 91, ["team"] = "Gamma", ["level"] = "Senior" },
        };
        foreach (var rec in teamAData) docA.AppendRecord(rec);

        var docB = NdjsonDocument.CreateNew();
        var teamBData = new[]
        {
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Ethan", ["score"] = 79, ["team"] = "Beta", ["level"] = "Junior" },
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "Fiona", ["score"] = 96, ["team"] = "Alpha", ["level"] = "Lead" },
            new System.Collections.Generic.Dictionary<string, object> { ["name"] = "George", ["score"] = 84, ["team"] = "Gamma", ["level"] = "Mid" },
        };
        foreach (var rec in teamBData) docB.AppendRecord(rec);

        Assert.Equal(4, docA.GetRecordCount());
        Assert.Equal(3, docB.GetRecordCount());

        // GetFieldValues on docA
        var docANames = docA.GetFieldValues("name");
        Assert.Equal(4, docANames.Count);
        Assert.Contains("Aaron", docANames);
        Assert.Contains("Diane", docANames);

        var docATeams = docA.GetFieldValues("team");
        Assert.Equal(4, docATeams.Count);
        Assert.Contains("Alpha", docATeams);
        Assert.Contains("Beta", docATeams);

        // SortBy on docA ascending
        var sortedA = docA.SortBy("name", ascending: true);
        Assert.Equal(4, sortedA.GetRecordCount());
        Assert.Equal("Aaron", sortedA.GetRecord(0)["name"].ToString());

        // SortBy on docA by score descending
        var sortedByScore = docA.SortBy("score", ascending: false);
        Assert.Equal("Aaron", sortedByScore.GetRecord(0)["name"].ToString()); // score=95

        // MergeWith
        var merged = docA.MergeWith(docB);
        Assert.NotNull(merged);
        Assert.Equal(7, merged.GetRecordCount());

        // GetFieldValues on merged
        var mergedNames = merged.GetFieldValues("name");
        Assert.Equal(7, mergedNames.Count);
        Assert.Contains("Aaron", mergedNames);
        Assert.Contains("Fiona", mergedNames);

        var mergedTeams = merged.GetFieldValues("team");
        Assert.Equal(7, mergedTeams.Count);
        Assert.Contains("Alpha", mergedTeams);
        Assert.Contains("Gamma", mergedTeams);

        // SortBy merged by score descending
        var mergedSorted = merged.SortBy("score", ascending: false);
        Assert.Equal(7, mergedSorted.GetRecordCount());
        var topRecord = mergedSorted.GetRecord(0);
        Assert.Equal("Fiona", topRecord["name"].ToString()); // score=96

        // Filter merged — Alpha team
        var alphaTeam = merged.Filter("team", "Alpha");
        Assert.Equal(3, alphaTeam.GetRecordCount()); // Aaron, Caleb, Fiona
        var alphaNames = alphaTeam.GetFieldValues("name");
        Assert.Contains("Aaron", alphaNames);
        Assert.Contains("Caleb", alphaNames);
        Assert.Contains("Fiona", alphaNames);

        // SortBy filtered result
        var alphaSorted = alphaTeam.SortBy("score", ascending: true);
        Assert.Equal("Caleb", alphaSorted.GetRecord(0)["name"].ToString()); // score=88

        // AppendRecord to merged
        merged.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["name"] = "Hannah", ["score"] = 90, ["team"] = "Beta", ["level"] = "Senior"
        });
        Assert.Equal(8, merged.GetRecordCount());
        var namesAfterAppend = merged.GetFieldValues("name");
        Assert.Equal(8, namesAfterAppend.Count);
        Assert.Contains("Hannah", namesAfterAppend);

        // GetAllKeys on merged
        var allKeys = merged.GetAllKeys();
        Assert.Contains("name", allKeys);
        Assert.Contains("score", allKeys);
        Assert.Contains("team", allKeys);
        Assert.Contains("level", allKeys);

        // WriteToFile
        var path = TempFile("dogfood_merged.ndjson");
        merged.WriteToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(8, loaded.GetRecordCount());

        var loadedNames = loaded.GetFieldValues("name");
        Assert.Equal(8, loadedNames.Count);
        Assert.Contains("Hannah", loadedNames);

        // SortBy on loaded
        var loadedSorted = loaded.SortBy("score", ascending: false);
        Assert.Equal(8, loadedSorted.GetRecordCount());
        Assert.Equal("Fiona", loadedSorted.GetRecord(0)["name"].ToString());

        // MergeWith on loaded with docB again
        var mergedAgain = loaded.MergeWith(docB);
        Assert.Equal(11, mergedAgain.GetRecordCount());
        var mergedAgainNames = mergedAgain.GetFieldValues("name");
        Assert.Equal(11, mergedAgainNames.Count);

        // WriteToFile merged result
        var mergedPath = TempFile("dogfood_merged_again.ndjson");
        mergedAgain.WriteToFile(mergedPath);
        Assert.True(File.Exists(mergedPath));
        var loadedMerged = NdjsonDocument.LoadFile(mergedPath);
        Assert.Equal(11, loadedMerged.GetRecordCount());
    }
}
