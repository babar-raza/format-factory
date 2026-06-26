// Tests for NdjsonDocument.Sort, Select, RecordAt deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R193

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R193: Tests for NdjsonDocument.Sort, Select, RecordAt deeper coverage.
/// Sort(field, ascending): returns new document sorted by given field.
/// Select(fields): returns new document with only specified fields per record.
/// RecordAt(index): returns a typed record dictionary at the given index.
/// Covers: Sort non-null; Sort preserves count; Sort ascending first=Alice;
/// Sort descending first=Frank; Sort numeric ascending first≤last;
/// Sort numeric descending first≥last; Sort doesn't mutate original;
/// Select non-null; Select preserves count; Select reduces keys;
/// Select single field; Select after Filter; Select GetAllKeys has only selected;
/// RecordAt non-null; RecordAt first correct; RecordAt last correct;
/// RecordAt middle correct; RecordAt GetField returns value; RecordAt all non-null;
/// dogfood LoadContent→Sort ascending→Select 2 fields→RecordAt all→Filter→Sort→Select pipeline.
/// </summary>
public class NdjsonR193SortAndSelectDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR193SortAndSelectDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR193_" + Guid.NewGuid().ToString("N"));
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
        "{\"Name\":\"Dave\",\"Score\":71,\"Dept\":\"HR\"}\n" +
        "{\"Name\":\"Eve\",\"Score\":90,\"Dept\":\"Finance\"}\n" +
        "{\"Name\":\"Frank\",\"Score\":88,\"Dept\":\"Engineering\"}\n";

    private NdjsonDocument LoadSample()
    {
        var path = TempFile("sample.ndjson");
        File.WriteAllText(path, SampleNdjson);
        return NdjsonDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Sort
    // -------------------------------------------------------------------------

    [Fact]
    public void Sort_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Sort("Name", ascending: true));
    }

    [Fact]
    public void Sort_PreservesCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.Count, doc.Sort("Name", ascending: true).Count);
    }

    [Fact]
    public void Sort_Ascending_FirstIsAlice()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Name", ascending: true);
        Assert.Equal("Alice", sorted.RecordAt(0)["Name"].ToString());
    }

    [Fact]
    public void Sort_Ascending_LastIsFrank()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Name", ascending: true);
        Assert.Equal("Frank", sorted.RecordAt(sorted.Count - 1)["Name"].ToString());
    }

    [Fact]
    public void Sort_Descending_FirstIsFrank()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Name", ascending: false);
        Assert.Equal("Frank", sorted.RecordAt(0)["Name"].ToString());
    }

    [Fact]
    public void Sort_NumericAscending_FirstLessOrEqualLast()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Score", ascending: true);
        var first = Convert.ToDouble(sorted.RecordAt(0)["Score"]);
        var last = Convert.ToDouble(sorted.RecordAt(sorted.Count - 1)["Score"]);
        Assert.True(first <= last);
    }

    [Fact]
    public void Sort_NumericDescending_FirstGreaterOrEqualLast()
    {
        var doc = LoadSample();
        var sorted = doc.Sort("Score", ascending: false);
        var first = Convert.ToDouble(sorted.RecordAt(0)["Score"]);
        var last = Convert.ToDouble(sorted.RecordAt(sorted.Count - 1)["Score"]);
        Assert.True(first >= last);
    }

    [Fact]
    public void Sort_DoesNotMutateOriginal()
    {
        var doc = LoadSample();
        var firstOriginal = doc.RecordAt(0)["Name"].ToString();
        doc.Sort("Name", ascending: true);
        Assert.Equal(firstOriginal, doc.RecordAt(0)["Name"].ToString());
    }

    // -------------------------------------------------------------------------
    // Select
    // -------------------------------------------------------------------------

    [Fact]
    public void Select_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.Select(new[] { "Name", "Score" }));
    }

    [Fact]
    public void Select_PreservesCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.Count, doc.Select(new[] { "Name", "Score" }).Count);
    }

    [Fact]
    public void Select_ReducesKeys()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "Name", "Score" });
        Assert.Equal(2, selected.GetAllKeys().Count);
    }

    [Fact]
    public void Select_SingleField()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "Name" });
        Assert.Equal(1, selected.GetAllKeys().Count);
    }

    [Fact]
    public void Select_AfterFilter_SmallerCount()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Dept", "Engineering");
        var selected = filtered.Select(new[] { "Name" });
        Assert.Equal(3, selected.Count);
    }

    [Fact]
    public void Select_GetAllKeys_HasOnlySelected()
    {
        var doc = LoadSample();
        var selected = doc.Select(new[] { "Name", "Dept" });
        var keys = selected.GetAllKeys();
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);
        Assert.False(keys.Contains("Score"));
    }

    // -------------------------------------------------------------------------
    // RecordAt
    // -------------------------------------------------------------------------

    [Fact]
    public void RecordAt_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.RecordAt(0));
    }

    [Fact]
    public void RecordAt_First_CorrectName()
    {
        var doc = LoadSample();
        Assert.Equal("Alice", doc.RecordAt(0)["Name"].ToString());
    }

    [Fact]
    public void RecordAt_Last_CorrectName()
    {
        var doc = LoadSample();
        Assert.Equal("Frank", doc.RecordAt(doc.Count - 1)["Name"].ToString());
    }

    [Fact]
    public void RecordAt_Middle_CorrectName()
    {
        var doc = LoadSample();
        var name = doc.RecordAt(2)["Name"].ToString();
        Assert.Equal("Carol", name);
    }

    [Fact]
    public void RecordAt_GetField_ReturnsValue()
    {
        var doc = LoadSample();
        var record = doc.RecordAt(0);
        Assert.True(record.ContainsKey("Score"));
        Assert.True(Convert.ToDouble(record["Score"]) > 0);
    }

    [Fact]
    public void RecordAt_AllIndices_NonNull()
    {
        var doc = LoadSample();
        for (var i = 0; i < doc.Count; i++)
            Assert.NotNull(doc.RecordAt(i));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Sort_Select_RecordAt_Filter_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.Count);

        // Sort ascending by Name
        var sorted = doc.Sort("Name", ascending: true);
        Assert.Equal(6, sorted.Count);
        Assert.Equal("Alice", sorted.RecordAt(0)["Name"].ToString());
        Assert.Equal("Frank", sorted.RecordAt(5)["Name"].ToString());

        // Sort descending by Score
        var sortedDesc = doc.Sort("Score", ascending: false);
        var firstScore = Convert.ToDouble(sortedDesc.RecordAt(0)["Score"]);
        var lastScore = Convert.ToDouble(sortedDesc.RecordAt(5)["Score"]);
        Assert.True(firstScore >= lastScore); // 92 >= 71

        // Select Name and Dept only
        var selected = doc.Select(new[] { "Name", "Dept" });
        Assert.Equal(6, selected.Count);
        var keys = selected.GetAllKeys();
        Assert.Equal(2, keys.Count);
        Assert.Contains("Name", keys);
        Assert.Contains("Dept", keys);
        Assert.False(keys.Contains("Score"));

        // RecordAt on selected
        var firstSelected = selected.RecordAt(0);
        Assert.True(firstSelected.ContainsKey("Name"));
        Assert.True(firstSelected.ContainsKey("Dept"));
        Assert.False(firstSelected.ContainsKey("Score"));

        // Filter then Sort
        var eng = doc.Filter("Dept", "Engineering");
        Assert.Equal(3, eng.Count);
        var engSorted = eng.Sort("Score", ascending: false);
        Assert.Equal("Alice", engSorted.RecordAt(0)["Name"].ToString()); // 92

        // Filter then Select
        var engSelected = eng.Select(new[] { "Name" });
        Assert.Equal(3, engSelected.Count);
        Assert.Equal(1, engSelected.GetAllKeys().Count);

        // RecordAt all in sorted
        for (var i = 0; i < sorted.Count; i++)
        {
            var record = sorted.RecordAt(i);
            Assert.NotNull(record);
            Assert.True(record.ContainsKey("Name"));
        }

        // AppendRecord and re-sort
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Zara", ["Score"] = 100, ["Dept"] = "Research"
        });
        var newSorted = doc.Sort("Score", ascending: false);
        Assert.Equal("Zara", newSorted.RecordAt(0)["Name"].ToString()); // Score 100
    }
}
